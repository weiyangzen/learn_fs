<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-gomod.sh -->
# sources/control-plane/csi-driver-nfs/hack/verify-gomod.sh

## Purpose
Verifies that Go module metadata and vendor contents are up to date.

## Important APIs, Types, and Functions
The script sets `GO111MODULE=on`, runs `go mod tidy`, runs `go mod vendor`, checks `git diff`, fails with the diff if non-empty, then runs `go list -mod readonly -m all`.

## Control Flow, State, and Persistence
Unlike a purely read-only verifier, it regenerates module and vendor files before comparing the working tree. If regeneration changes files, it reports the diff and exits non-zero. Persistent effects may remain in the working tree on failure.

## Dependencies and Integration Points
It depends on Go modules, git, and vendor mode. It is the verification partner for dependency update scripts and is included in `verify-all.sh`.

## Risks and Test Signals
Risks include network/module cache differences, Go version churn, mutating the working tree during verification, and broad `git diff` including unrelated local changes. Signals are no diff after tidy/vendor and successful `go list -mod readonly -m all`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-gomod.sh -->
