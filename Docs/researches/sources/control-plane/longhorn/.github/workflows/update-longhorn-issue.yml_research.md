## sources/control-plane/longhorn/.github/workflows/update-longhorn-issue.yml

### Purpose
`update-longhorn-issue.yml` manages Longhorn member issue status in the Longhorn Sprint project.

### Important APIs, Types, And Functions
It triggers on issue labeled, milestoned, assigned, and unassigned events with per-issue concurrency. It creates an app token, treats `github-actions[bot]` as a member, checks real membership otherwise, fetches project `Status`, adds issues to Longhorn Sprint project 8, updates new project items to `New`, sets missing milestones to `Backlog` for real members, and conditionally applies `New Issues`.

### Control Flow
Only member-created issues proceed. The workflow avoids changing items already `Closed`. Assigned issues with empty or `New Issues` status stay/set `New Issues`; unassigned issues also set `New Issues`.

### State, Persistence, And Dependencies
It mutates project membership, project status, and milestones. Dependencies include app secrets, project URL, status field names, membership action, `gh`, and pinned project-field actions.

### Integration Points
Works with issue templates and add-issue workflow to keep Longhorn Sprint project populated and consistently staged.

### Risks
The initial `Update Item To New` can set `New` before later logic sets `New Issues`, causing extra project churn. Bot membership bypass affects generated issues. Status name changes break shell conditions.

### Test Signals
Member issue label/assignment/milestone events should add project items, set Backlog when missing, and avoid changing closed status.
