<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/update-gofmt.sh -->
# sources/control-plane/csi-driver-nfs/hack/update-gofmt.sh

## Purpose
Applies canonical Go formatting to all non-vendor Go files in the repository.

## Important APIs, Types, and Functions
The script runs `find . -name "*.go" | grep -v "\/vendor\/" | xargs gofmt -s -w` under `set -euo pipefail`.

## Control Flow, State, and Persistence
It recursively locates Go files, excludes vendor paths, and rewrites files in place using simplified formatting. Persistent effects are source file formatting changes.

## Dependencies and Integration Points
It depends on the Go toolchain and is the fixer counterpart to `hack/verify-gofmt.sh`. It is also part of broader update/verification workflows.

## Risks and Test Signals
Risks include xargs behavior with no files, path handling for unusual file names, and formatting generated or unrelated Go files outside intended scope. Signals are no subsequent diff from `verify-gofmt.sh` and expected gofmt-only changes.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/update-gofmt.sh -->
