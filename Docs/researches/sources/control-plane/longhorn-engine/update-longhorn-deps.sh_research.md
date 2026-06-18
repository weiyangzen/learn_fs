## sources/control-plane/longhorn-engine/update-longhorn-deps.sh

### Purpose
`update-longhorn-deps.sh` updates selected Longhorn Go dependencies to their `master` branches and refreshes module/vendor state.

### Important APIs, Types, And Functions
It runs `go get` for `github.com/longhorn/go-iscsi-helper@master`, `github.com/longhorn/sparse-tools@master`, and `github.com/longhorn/backupstore@master`, then runs `go mod tidy` and `go mod vendor`.

### Control Flow
The script is linear and has no `set -e`, so later commands may run after earlier failures depending on shell behavior.

### State, Persistence, And Dependencies
It mutates `go.mod`, `go.sum`, and `vendor/`. It depends on network access and Go modules.

### Integration Points
Maintainers use it to refresh Longhorn-internal dependencies before PRs.

### Risks
Tracking `master` can introduce unreviewed breaking changes. Lack of `set -e` can leave partially updated state. Vendor changes can be large and need validation.

### Test Signals
After running, `go mod tidy`, `go test`, `scripts/validate`, and integration tests should pass.
