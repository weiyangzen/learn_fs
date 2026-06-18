# sources/control-plane/csi-driver-smb/hack/verify-govet.sh

## Purpose
Runs Go vet across repository packages.

## Important APIs, Types, and Functions
Executes `go vet $(go list ./... | grep -v vendor)`.

## Control Flow
Lists Go packages, filters vendor, vets them, and exits on vet failure.

## State and Persistence
Read-only except Go cache.

## Dependencies
Requires Go toolchain and loadable packages.

## Integration Points
Called by `verify-all.sh`.

## Risks and Edge Cases
Command substitution can exceed shell limits in huge repos. Build tags or platform-specific packages may alter coverage.

## Test Signals
"Done" with zero exit status.
