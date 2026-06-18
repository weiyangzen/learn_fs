<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/update-dependencies.sh -->
# sources/control-plane/csi-driver-nfs/hack/update-dependencies.sh

## Purpose
Regenerates Go module dependency pins and vendor contents in a deterministic, Kubernetes-style way.

## Important APIs, Types, and Functions
The script sets `GO111MODULE=on`, clears `GOPATH` and `GOFLAGS`, moves to the git root, and defines `prune-vendor()`, `ensure_require_replace_directives_for_all_dependencies()`, and `group_replace_directives()`. It uses `go mod edit -json`, `jq`, `go list -m -json all`, `go mod tidy`, and `go mod vendor`.

## Control Flow, State, and Persistence
It captures current `require` and `replace` directives, adds replace directives pinning versions, makes indirect dependencies explicit, repeats after `go mod tidy`, groups replace directives into a block, and regenerates `vendor`. It mutates `go.mod`, `go.sum`, and `vendor` content.

## Dependencies and Integration Points
It depends on Go modules, `jq`, `awk`, `xargs`, git root detection, and write access to module/vendor files. `verify-gomod.sh` and `verify-update.sh` detect whether running update scripts leaves uncommitted diffs.

## Risks and Test Signals
Risks include destructive vendor churn, dependency resolver changes across Go versions, `jq` absence, disabled `prune-vendor()` leaving extra files, and temporary directory cleanup not being automatic. Signals are `SUCCESS`, stable `go mod tidy/vendor`, grouped replace directives, and no git diff after expected updates are committed.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/update-dependencies.sh -->
