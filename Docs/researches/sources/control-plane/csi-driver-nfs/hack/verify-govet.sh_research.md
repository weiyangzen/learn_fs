<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-govet.sh -->
# sources/control-plane/csi-driver-nfs/hack/verify-govet.sh

## Purpose
Runs `go vet` across repository packages outside vendor.

## Important APIs, Types, and Functions
The script executes `go vet $(go list ./... | grep -v vendor)` with strict shell options.

## Control Flow, State, and Persistence
It lists packages, filters vendor, and runs vet once over the resulting package list. It does not intentionally mutate files.

## Dependencies and Integration Points
It depends on the Go toolchain, module resolution, and compilable packages. `verify-all.sh` includes it after gofmt verification.

## Risks and Test Signals
Risks include shell command length for very large package sets, broad `grep -v vendor` filtering, package list failures when module state is dirty, and Go version-dependent vet diagnostics. Signals are `go vet` exiting zero and the script printing "Done".
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-govet.sh -->
