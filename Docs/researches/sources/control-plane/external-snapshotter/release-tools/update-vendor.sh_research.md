<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/update-vendor.sh -->
# sources/control-plane/external-snapshotter/release-tools/update-vendor.sh

## Purpose
`update-vendor.sh` regenerates dependency lock/vendor state for repos that either still use `dep` or use Go modules. It is a developer/CI helper for keeping vendored dependencies synchronized.

## Important APIs, Types, and Functions
The script has a simple top-level branch on repository files: if `Gopkg.toml` exists, it runs `dep ensure`; if `go.mod` exists, it runs `release-tools/verify-go-version.sh go`, then `GO111MODULE=on go mod tidy` and `GO111MODULE=on go mod vendor`.

## Control Flow, State, and Persistence
There is no cleanup or temporary state. It mutates dependency files and the `vendor/` tree in place through the selected dependency manager.

## Dependencies and Integration Points
It depends on `dep` for legacy projects, Go modules for modern projects, the repository-local `release-tools/verify-go-version.sh`, and a working `go` binary. It is meant to be invoked from a repository root where `release-tools` is available as a subtree.

## Risks and Test Signals
Risks are broad workspace churn from `go mod tidy/vendor`, environment-sensitive module resolution, and missing Go version compatibility. Test signals are a clean command exit plus subsequent `git diff` review or `verify-vendor.sh` showing no dependency drift.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/update-vendor.sh -->
