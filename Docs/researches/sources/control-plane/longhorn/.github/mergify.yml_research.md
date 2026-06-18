## sources/control-plane/longhorn/.github/mergify.yml

### Purpose
`mergify.yml` configures automated PR approval, merge, and conflict notification rules for the Longhorn repository.

### Important APIs, Types, And Functions
Rules merge PRs with successful Drone CI, at least two approvals, and approval by `@longhorn/maintainer`; merge bot PRs from Renovate or Mergify after Drone CI; auto-approve Renovate PRs; and comment on conflicting PRs.

### Control Flow
Mergify evaluates rules against PR state and runs `merge`, `review`, or `comment` actions when conditions match.

### State, Persistence, And Dependencies
The file persists merge policy and depends on Mergify, the Drone status name `continuous-integration/drone/pr`, GitHub review data, and team membership.

### Integration Points
It interacts with Renovate config and branch protection. Auto-merge uses rebase strategy.

### Risks
Status check name drift will disable merges. Auto-approving bot PRs relies on Renovate policy being safe. Conflict comments can be noisy.

### Test Signals
Observe Mergify dry-run/dashboard rule matches and successful auto-merge of eligible bot and maintainer-approved PRs.
