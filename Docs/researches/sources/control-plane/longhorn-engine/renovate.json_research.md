## sources/control-plane/longhorn-engine/renovate.json

### Purpose
`renovate.json` configures Renovate dependency update behavior for the Longhorn engine repository.

### Important APIs, Types, And Functions
The config extends `github>longhorn/release:renovate-default`. A package rule disables updates for `github.com/rancher/go-rancher` on `master`, `main`, and version branches matching `v<major>.<minor>.x`.

### Control Flow
Renovate reads this JSON, inherits the shared Longhorn release defaults, then applies the local rule when package name and base branch match.

### State, Persistence, And Dependencies
The file persists repository automation policy. It depends on Renovate's config schema and the shared Longhorn release preset.

### Integration Points
GitHub Renovate runs use this file to decide whether to open dependency update PRs. It coordinates with `.github/mergify.yml`, which can auto-approve and merge Renovate PRs.

### Risks
The disabled package rule can leave `go-rancher` stale across all active branches. If the shared preset changes, inherited behavior changes without local file edits.

### Test Signals
Validation is mainly Renovate config validation and observing Renovate dry-run logs for expected disabled updates.
