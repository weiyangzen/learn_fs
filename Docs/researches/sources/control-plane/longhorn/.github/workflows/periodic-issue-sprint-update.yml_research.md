## sources/control-plane/longhorn/.github/workflows/periodic-issue-sprint-update.yml

### Purpose
This workflow performs weekly sprint rollover updates for Longhorn GitHub Projects.

### Important APIs, Types, And Functions
It runs on Sunday 20:00 UTC and manual dispatch. It creates an app token, checks out the repository, runs `check-sprint-last-day.py`, and if that script succeeds, invokes `rancher/gh-issue-mgr/move-to-next-iteration` for Longhorn Sprint project 8, QA Sprint project 4, and Community Sprint project 5.

### Control Flow
The workflow gates all updates on being the last day of the current sprint. It clears current sprint values for items not in excluded statuses, moves `Review` items to next sprint, moves `Ready For Testing` items with no sprint into current sprint, and moves community `New` items to next sprint.

### State, Persistence, And Dependencies
It mutates GitHub Project iteration fields. Dependencies are app secrets, project numbers, field names `Sprint` and `Status`, status names, and the Python sprint checker.

### Integration Points
It coordinates with issue update workflows that add items and set statuses throughout the sprint.

### Risks
Incorrect sprint-date detection can skip or prematurely run rollover. Status name drift will leave items unchanged. Project-wide mutations are broad and should be monitored.

### Test Signals
Use workflow dispatch near a mocked or real sprint end and verify field updates on representative project items.
