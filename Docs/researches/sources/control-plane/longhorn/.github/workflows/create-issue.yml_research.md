## sources/control-plane/longhorn/.github/workflows/create-issue.yml

### Purpose
`create-issue.yml` creates derived tracking issues when source issues receive labels for backports, automation tests, or UI work.

### Important APIs, Types, And Functions
The workflow has `backport`, `automation`, and `ui` jobs. It uses GitHub App tokens, team membership checks, `actions/github-script`, milestone lookup, label filtering shell snippets, `dacbd/create-issue-action`, Longhorn bot project actions, and `titoportas`/project field updates.

### Control Flow
For `backport/<version>` labels, member actions trigger lookup of existing `[BACKPORT][v<version>]` issues, milestone resolution, label filtering, assignee filtering to org members, issue creation or reopening, and project addition. For `require/auto-e2e-test`, it creates a `[TEST]` issue assigned to QA project. For `require/ui`, it creates a `[UI]` issue with `area/ui`, copied labels minus trigger labels, and the source milestone.

### State, Persistence, And Dependencies
It creates and reopens issues, sets labels/milestones/assignees, and adds project items. It depends on label names, issue title conventions, milestone names, app secrets, and project URLs.

### Integration Points
It is paired with `close-issue.yml` and issue templates that apply requirement labels by default.

### Risks
Title-based duplicate detection can fail after title edits. Milestone lookup for backports assumes `v<version>` exists. UI issue creation uses `github.event.issue.milestone.number`, which can be null if no milestone is present.

### Test Signals
Apply each trigger label to a member-created issue and verify generated issue metadata, duplicate prevention, reopening, project addition, and label filtering.
