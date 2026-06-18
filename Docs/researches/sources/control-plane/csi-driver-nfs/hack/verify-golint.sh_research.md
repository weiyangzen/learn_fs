<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-golint.sh -->
# sources/control-plane/csi-driver-nfs/hack/verify-golint.sh

## Purpose
Runs legacy golint checks through golangci-lint.

## Important APIs, Types, and Functions
The script checks for `golangci-lint`, installs v1.31.0 with the upstream install script if missing, appends `$(go env GOPATH)/bin` to `PATH`, and runs `golangci-lint run --no-config --enable=golint --disable=typecheck --deadline=10m`.

## Control Flow, State, and Persistence
It may download and install a linter into the Go bin directory, then runs linting across the repository. The script exits on the first failure due to strict shell settings.

## Dependencies and Integration Points
It depends on network access, Go, `curl`, and golangci-lint. It is not invoked by the shown `verify-all.sh`, but remains available as a separate quality gate.

## Risks and Test Signals
Risks include use of deprecated `golint`, old golangci-lint version compatibility with modern Go, network installation at verify time, and disabled typechecking reducing signal. Signals are successful linter execution and no reported golint issues.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-golint.sh -->
