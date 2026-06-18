<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/mergify.yml -->
## sources/control-plane/longhorn-engine/.github/mergify.yml

### Purpose
`mergify.yml` automates Longhorn Engine PR merge, Renovate approval, and conflict notification policies.

### Important APIs, Types, And Functions
Rules include automatic merge for PRs with successful AMD64/ARM64 binary builds, at least two approvals, and maintainer approval; automatic merge for Renovate PRs after the same build checks; automatic approval for Renovate PRs after builds; and conflict comments to the author.

### Control Flow
Mergify evaluates pull request conditions and performs rebase merges, approval reviews, or conflict comments.

### State, Persistence, And Dependencies
State is GitHub PR metadata and Mergify-managed reviews/comments/merges. Dependencies are Mergify, GitHub branch protection/check names, and Longhorn team membership.

### Integration Points
The required check names must match `.github/workflows/build.yml` job names. Renovate automation depends on author identity `renovate[bot]`.

### Risks
If build job names change, auto-merge stops. Renovate PRs can be approved and merged without human approval once builds pass. Rebase merge policy can rewrite PR merge topology. The conflict comment includes a Unicode emoji, which is harmless but non-ASCII.

### Test Signals
Signals include Mergify dry-run/status checks, rule matching for normal and Renovate PRs, branch protection alignment, and conflict comment behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/mergify.yml -->
