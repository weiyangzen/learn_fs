<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-gofmt.sh -->
# sources/control-plane/csi-driver-nfs/hack/verify-gofmt.sh

## Purpose
Checks that all non-vendor Go files are formatted with `gofmt -s`.

## Important APIs, Types, and Functions
The script captures `diff=$(find . -name "*.go" | grep -v "\/vendor\/" | xargs gofmt -s -d 2>&1)` and fails if the diff is non-empty, instructing developers to run `hack/update-gofmt.sh`.

## Control Flow, State, and Persistence
It is read-only: gofmt emits diffs to stdout instead of rewriting. With strict shell options, command failures stop the script. Successful completion prints "No issue found".

## Dependencies and Integration Points
It depends on the Go toolchain and pairs with `update-gofmt.sh`. `verify-all.sh` runs it before vet and other gates.

## Risks and Test Signals
Risks include path handling for unusual names, xargs behavior on empty input, and excluding only paths containing `/vendor/`. Signals are an empty gofmt diff and zero exit status.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-gofmt.sh -->
