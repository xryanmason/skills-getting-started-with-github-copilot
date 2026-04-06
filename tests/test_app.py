import copy
import pytest
from starlette.testclient import TestClient
import src.app as app_module
from src.app import app

INITIAL_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset shared activity state before each test to prevent pollution."""
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


client = TestClient(app)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities():
    # Arrange
    # (no additional setup needed — initial state has 9 activities)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 9
    assert "Chess Club" in data
    assert "Programming Class" in data


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success():
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}
    assert new_email in app_module.activities[activity_name]["participants"]


def test_signup_activity_not_found():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_student():
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"  # already enrolled in initial data

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/unregister
# ---------------------------------------------------------------------------

def test_unregister_success():
    # Arrange
    activity_name = "Chess Club"
    enrolled_email = "michael@mergington.edu"  # already enrolled in initial data

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": enrolled_email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {enrolled_email} from {activity_name}"}
    assert enrolled_email not in app_module.activities[activity_name]["participants"]


def test_unregister_activity_not_found():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_student_not_signed_up():
    # Arrange
    activity_name = "Chess Club"
    unenrolled_email = "notamember@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": unenrolled_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"
