<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/update-gofmt -->
# sources/control-plane/juicefs-csi-driver/hack/update-gofmt

## Purpose
Developer helper that reformats all non-vendor Go files with `gofmt -s -w`.

## Important APIs, Types, and Resources
Uses `find . -name '*.go'`, filters `/vendor/`, and pipes to `gofmt -s -w` under `set -euo pipefail`.

## Control Flow
When run from the repo root, it enumerates Go files and rewrites them in place using simplified gofmt formatting.

## State and Persistence
Persists formatting changes directly to Go source files. No separate state is stored.

## Dependencies and Integration Points
Depends on Bash, GNU-ish find/grep/xargs behavior, and the Go toolchain. Paired with `hack/verify-gofmt`.

## Risks
Risks include xargs behavior with unusual filenames, running from the wrong directory, and touching generated files if they are not under vendor.

## Test Signals
Run it then `git diff`; `hack/verify-gofmt` should report no issues afterward.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/update-gofmt -->
