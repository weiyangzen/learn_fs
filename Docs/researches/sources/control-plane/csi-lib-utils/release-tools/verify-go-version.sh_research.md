# sources/control-plane/csi-lib-utils/release-tools/verify-go-version.sh

## Purpose

This script warns when a caller's Go binary does not match the Go major/minor version configured for CSI Prow builds.

## Important Behavior

It requires a path to a Go binary, runs `<go> version`, extracts major/minor with `sed`, sources `release-tools/prow.sh` to read `CSI_PROW_GO_VERSION_BUILD`, and prints a large warning if the versions differ. It does not exit nonzero for mismatches.

## State, Dependencies, and Integration

There is no persistence. It depends on bash, Go, `sed`, and the side effects of sourcing `release-tools/prow.sh`. It is used by vendoring/update flows to highlight versions that can affect `gofmt`, `go mod tidy`, and vendor output.

## Risks and Test Signals

Sourcing `prow.sh` executes many `configvar` assignments and can print configuration to stdout, though the script redirects source output to `/dev/null`. Because mismatches are warnings only, callers must decide whether to enforce. The test signal is visible warning text.
