<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/k8s-mod.sh -->
# sources/control-plane/juicefs-csi-driver/k8s-mod.sh

## Purpose
Kubernetes module alignment helper for updating Go module replacements to a selected Kubernetes release.

## Important APIs, Types, and Resources
Accepts a version argument with optional leading `v`, downloads the Kubernetes `go.mod` from GitHub, extracts staging module names, resolves each `k8s.io/*@kubernetes-$VERSION` module version with `go mod download -json`, adds `go mod edit -replace` entries, and finally runs `go get k8s.io/kubernetes@v$VERSION`.

## Control Flow
The script exits if no version is supplied. For a valid version, it discovers all staging modules used by Kubernetes, maps them to published pseudo/module versions, edits the local module file, and updates the Kubernetes dependency.

## State and Persistence
Persists changes to `go.mod` and likely `go.sum`; Go also updates module cache. No other state is intended.

## Dependencies and Integration Points
Depends on Bash arrays, curl access to GitHub, sed patterns matching Kubernetes go.mod replace format, Go modules, and published `kubernetes-$VERSION` module tags. Integrates with dependency upgrade workflows.

## Risks
Risks include no bash shebang despite Bash-specific arrays and `pipefail`, network/API drift, sed pattern breakage if Kubernetes go.mod format changes, partial go.mod edits after a failure, and complex replace churn.

## Test Signals
Run on a branch with a target version, review `go.mod`/`go.sum`, run `go mod tidy`, full build, unit tests, and Kubernetes-client integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/k8s-mod.sh -->
