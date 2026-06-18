## sources/control-plane/longhorn/.github/workflows/create-release-task-issues.yml

### Purpose
This manually dispatched workflow creates standard release task issues for a requested Longhorn release version.

### Important APIs, Types, And Functions
Inputs are `release_version`, `release_captain`, and `qa_captain`. The workflow creates an app token, checks out the repo, parses version metadata, validates `v<major>.<minor>.<patch>`, computes major-minor version, branch name, and feature-release flag, then invokes `rancher/gh-issue-mgr/create-an-issue` with release-related templates.

### Control Flow
Every release creates the main release task and security-fix task. Feature releases ending in `.0` also create regular feature-release tasks and performance benchmark tasks.

### State, Persistence, And Dependencies
It creates GitHub issues from templates and depends on app secrets, issue templates, version naming conventions, and the external issue manager action.

### Integration Points
Generated release issues feed release project tracking and captain assignments.

### Risks
Invalid input exits early. Template environment variable names must match template placeholders. Patch releases intentionally skip feature-release task templates.

### Test Signals
Manual dry runs with feature and patch versions should create the correct set of issues with expected env-substituted content.
