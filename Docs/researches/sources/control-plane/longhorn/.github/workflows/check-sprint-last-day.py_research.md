## sources/control-plane/longhorn/.github/workflows/check-sprint-last-day.py

### Purpose
`check-sprint-last-day.py` determines whether the current date is the final day of the current iteration in a GitHub Projects v2 project.

### Important APIs, Types, And Functions
Functions are `get_github_project_info`, `get_current_sprint`, and `is_today_is_in_last_day_of_current_sprint`. It queries the GitHub GraphQL API for organization projects and iteration field configuration, treats each sprint as a 14-day interval, and exits 0 only on the last day.

### Control Flow
The script reads `GITHUB_TOKEN` and CLI args `github_org github_repo github_project`, finds the project by title, gets current iteration by comparing dates to `startDate + 13 days`, prints details, and exits 1 when not the last day.

### State, Persistence, And Dependencies
It persists nothing. Dependencies are `requests`, environment token, GraphQL schema for Projects v2, and local timezone/date of the runner.

### Integration Points
`periodic-issue-sprint-update.yml` calls it to gate sprint rollover operations.

### Risks
The `github_repo` argument is unused. It assumes the first iteration field is the sprint field and that sprints are exactly 14 days. Missing JSON fields can raise `AttributeError`.

### Test Signals
Unit tests with mocked GraphQL responses should cover current sprint detection, no sprint found, final day, non-final day, and API failure.
