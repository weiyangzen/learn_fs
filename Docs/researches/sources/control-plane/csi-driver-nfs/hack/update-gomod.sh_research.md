<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/update-gomod.sh -->
# sources/control-plane/csi-driver-nfs/hack/update-gomod.sh

## Purpose
Updates `replace` directives for Kubernetes staging modules to match a specified Kubernetes release.

## Important APIs, Types, and Functions
The script requires a version argument with optional leading `v`, downloads Kubernetes `go.mod` from GitHub, extracts staging module names with `sed`, resolves module versions using `go mod download -json "${MOD}@kubernetes-${VERSION}"`, and writes replacements with `go mod edit`.

## Control Flow, State, and Persistence
It strips `v` from the argument, fails if empty, builds a shell array of `k8s.io/*` module names from the upstream Kubernetes release, then iterates and rewrites `go.mod` replace directives. It mutates only module metadata directly.

## Dependencies and Integration Points
It depends on network access to GitHub and module proxies, Go modules, `curl`, `sed`, and `go mod edit`. It complements dependency update scripts when aligning CSI dependencies with Kubernetes versions.

## Risks and Test Signals
Risks include network or upstream tag failures, unquoted echo/output, module proxy inconsistencies, and partially updated `go.mod` if a later module fails. Signals are replacement lines matching Kubernetes pseudo-versions and successful follow-up `go mod tidy`/`verify-gomod.sh`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/update-gomod.sh -->
