## sources/control-plane/longhorn-engine/scripts/test

### Purpose
`scripts/test` runs Go unit tests for all non-vendor Longhorn engine packages and collects coverage.

### Important APIs, Types, And Functions
It discovers package directories by finding `.go` files, excluding `.git`, `.trash-cache`, `vendor`, and `bin`. It enables `-race` only when `ARCH=amd64` and runs `go test` with `-coverprofile=coverage.out` and tags `test qcow`.

### Control Flow
The script prints the package list, computes race options, and exits on any `go test` failure.

### State, Persistence, And Dependencies
It writes `coverage.out` and uses Go tooling. It depends on package discovery through Unix `find`, `xargs`, `dirname`, `sort`, and `grep`.

### Integration Points
`scripts/ci` runs this after validation and generated-code sync.

### Risks
Package discovery can include generated or experimental directories if they contain `.go` files outside excluded paths. Race coverage is architecture-gated by `ARCH`, not by actual `go env GOARCH`.

### Test Signals
Successful `go test` with coverage output is the signal. Race failures on amd64 should be treated as real concurrency issues unless environment-specific.
