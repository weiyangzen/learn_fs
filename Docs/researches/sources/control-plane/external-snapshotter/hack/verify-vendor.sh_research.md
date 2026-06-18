# sources/control-plane/external-snapshotter/hack/verify-vendor.sh

## Purpose
Verifies vendored dependencies are in sync with module metadata.

Source size: 39 lines, 1459 bytes.

## Important APIs, Types, and Functions
- External commands/helpers: `go`.

## Control Flow
- Runs Go vendoring verification logic from the repository hack tooling.
- Fails when `vendor/` differs from `go.mod`/`go.sum` expectations.

## State and Persistence
- May create temporary files during verification but should not persist changes in a clean run.
- Dependency state is represented by module files and vendor contents.

## Dependencies and Integration Points
- Go toolchain and repository module/vendor layout.

## Risks and Edge Cases
- Vendoring checks can be sensitive to Go version and environment.
- Failure indicates dependency drift that should be regenerated, not ignored.

## Test Signals
- CI can run this script as a presubmit signal.
