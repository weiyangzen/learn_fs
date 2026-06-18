## sources/control-plane/longhorn/.github/workflows/wont-fix.yml

### Purpose
`wont-fix.yml` labels and demilestones issues closed as "not planned".

### Important APIs, Types, And Functions
It triggers on issue closure. `actions/github-script` checks `context.payload.issue.state_reason === "not_planned"`. If true, `actions-ecosystem/action-add-labels` adds `wontfix`, and another `github-script` clears the milestone.

### Control Flow
The second and third steps are conditional on the first step returning true.

### State, Persistence, And Dependencies
It mutates issue labels and milestone. Dependencies are GitHub issue `state_reason`, the `wontfix` label, and pinned actions.

### Integration Points
The label feeds community issue status automation, which treats `wontfix` as closed.

### Risks
Manual closures without not-planned reason are ignored. Clearing milestone may remove useful release context.

### Test Signals
Close a test issue as not planned and verify `wontfix` is added and milestone removed; close as completed and verify no change.
