## sources/control-plane/longhorn/.github/workflows/update-community-issue.yml

### Purpose
`update-community-issue.yml` synchronizes community issue status, sprint, and milestone across GitHub Projects when issues or comments change.

### Important APIs, Types, And Functions
It triggers on issue labeled/milestoned/reopened/closed and issue comment created/edited events, with per-issue concurrency. It uses an app token, team membership check, project field lookup via `EndBug/project-fields`, `actions/add-to-project`, shell status decision logic, `titoportas/update-project-fields`, and `gh issue edit`.

### Control Flow
After membership and project-field checks, it adds the issue to community project 5. Member milestone events set `Resolved,[0]`; closed unresolved issues set `Closed`; reopened closed issues set `In Progress,[0]`; non-member comments on non-resolved/non-closed issues set `In Progress,[0]`; invalid/wontfix/duplicated labels set `Closed`. Resolved issues are also added to Longhorn Sprint project 8 and get Backlog milestone if missing.

### State, Persistence, And Dependencies
It mutates project fields, project membership, and milestones. Dependencies are project URLs, fields `Status,Sprint`, status values, app secrets, labels, and GitHub CLI.

### Integration Points
It complements add-issue and longhorn-issue workflows by managing community-reported issue lifecycle.

### Risks
The shell parses JSON-ish teams output by trimming brackets and splitting commas, which is fragile. The environment variable name `field-values` contains a hyphen; GitHub env supports it for expressions but shell variable access would be awkward. Project field lookup failures skip updates.

### Test Signals
Exercise each event branch with member/non-member actors and verify project fields, sprint, Longhorn project addition, and Backlog milestone behavior.
