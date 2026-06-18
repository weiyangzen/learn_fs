## sources/control-plane/longhorn/.github/workflows/scan-and-notify-testing-items.py

### Purpose
`scan-and-notify-testing-items.py` scans a GitHub Projects v2 board for issues in testing-related statuses and sends a Slack reminder to QA.

### Important APIs, Types, And Functions
Functions include project lookup (`get_github_project_info`), current sprint detection (`get_current_sprint`, `is_today_is_in_last_day_of_current_sprint`), paginated project item listing (`list_issues_in_project`), Slack block formatting (`flatten_issues`), notification posting (`send_slack_notification`), and main orchestration (`scan_and_notify`).

### Control Flow
The script locates a project by title, determines the current sprint, paginates all project items with `Status` and `Sprint` fields, filters statuses `Ready For Testing` and `Testing`, splits results into current-sprint and non-current-sprint lists by sprint start date, formats assignee Slack mentions from optional JSON mapping, and posts a Slack message if any issues exist.

### State, Persistence, And Dependencies
It persists nothing. Dependencies are GitHub GraphQL API, `requests`, Slack webhook, `GITHUB_TOKEN`, `USER_MAPPING`, and specific project field names.

### Integration Points
`scan-and-notify-testing-items.yml` schedules the script. The commented-out last-day gate shows prior or planned coupling with sprint rollover timing.

### Risks
The code assumes every item has `status.name`; draft/non-issue items or missing fields can raise errors. It prints full project GraphQL responses. The current-sprint label text says "Previous Sprint" for `current_issues`, which may confuse recipients.

### Test Signals
Mock GraphQL pagination and Slack post calls to cover status filtering, sprint split, no-notification path, user mapping, and API error propagation.
