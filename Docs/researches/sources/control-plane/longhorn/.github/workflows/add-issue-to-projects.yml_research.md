## sources/control-plane/longhorn/.github/workflows/add-issue-to-projects.yml

### Purpose
This workflow adds opened, reopened, or milestoned issues to the correct Longhorn GitHub Projects for Longhorn members, community reporters, and QA/devops items.

### Important APIs, Types, And Functions
It has three jobs: `longhorn`, `community`, and `qa`. Each creates a GitHub App token. Membership checks use `tspascoal/get-user-teams-membership`, issue/project operations use `actions/add-to-project`, `octokit/request-action`, and `titoportas/update-project-fields`.

### Control Flow
The Longhorn job treats `github-actions[bot]` as a member, otherwise checks org teams, then adds member-created non-test issues to project 8. The community job adds non-member issues to project 5 and sets `Status,Sprint` to `New,[0]`. The QA job adds member issues labeled `kind/test` or `area/infra` to project 4.

### State, Persistence, And Dependencies
It mutates GitHub Projects and uses organization membership data. It depends on app secrets, pinned actions, project URLs, labels, and project fields.

### Integration Points
Works with issue templates that apply labels and with update workflows that later move project status.

### Risks
Membership outcome handling differs between jobs. Project number/field changes break updates. App-token permissions are broad but necessary for projects.

### Test Signals
Test by opening issues as member, bot, and non-member with/without QA labels and verifying project placement and fields.
