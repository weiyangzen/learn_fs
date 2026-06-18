<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/verify-govet -->
# sources/control-plane/juicefs-csi-driver/hack/verify-govet

## Purpose
Go vet verifier for all non-vendor packages.

## Important APIs, Types, and Resources
Runs `go vet $(go list ./... | grep -v vendor)` and prints progress messages.

## Control Flow
The script asks `go list` for packages, filters vendor, then invokes `go vet` over the resulting package list. Any vet failure stops the script.

## State and Persistence
No intended repository state changes, though Go may populate module/build caches. Exit code is the CI signal.

## Dependencies and Integration Points
Depends on Bash, Go module resolution, package compileability, and network/cache availability for dependencies. Integrated into `verify-all`.

## Risks
Risks include command-line length for very large package lists, filtering only literal `vendor`, and go vet behavior changing across Go versions.

## Test Signals
Run in CI with the project Go version; pair with unit tests for behavior that vet cannot prove.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/verify-govet -->
