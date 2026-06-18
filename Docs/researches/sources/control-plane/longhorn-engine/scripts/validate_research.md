## sources/control-plane/longhorn-engine/scripts/validate

### Purpose
`scripts/validate` runs static validation for Longhorn engine Go packages.

### Important APIs, Types, And Functions
It discovers top-level Go package roots, expands them to `./<root>/...`, then runs `go vet`, `golangci-lint run --timeout=5m`, and `go fmt`, failing if formatting changes would be produced.

### Control Flow
`set -e` stops at the first failure. The formatting check pipes `go fmt` output to stderr and requires it to be empty.

### State, Persistence, And Dependencies
It should not persist changes; `go fmt` can rewrite files if they are unformatted, but the script expects no output. Dependencies are Go, golangci-lint, and Unix discovery commands.

### Integration Points
`scripts/ci` runs validation before generated Python sync and tests.

### Risks
The package discovery compresses paths to first-level directories, so unusual nested module layouts may not be represented precisely. Running `go fmt` as a validator can modify files before failing.

### Test Signals
Success means vet, golangci-lint, and formatting are clean.
