<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/verify-go-version.sh -->
# sources/control-plane/external-snapshotter/release-tools/verify-go-version.sh

## Purpose
`verify-go-version.sh` warns when a provided Go binary's major.minor version differs from the release-tools configured build version. It is advisory rather than failing.

## Important APIs, Types, and Functions
The script accepts one argument, the Go binary path/name. It defines `die`, parses `$("$GO" version)` with `sed`, and obtains the expected version by sourcing `release-tools/prow.sh` and echoing `CSI_PROW_GO_VERSION_BUILD`.

## Control Flow, State, and Persistence
If no Go binary argument is supplied or `go version` fails, it exits 1. Otherwise it compares `majorminor` against the expected release-tools build version and prints a warning block on mismatch. It does not mutate files or exit nonzero for mismatch.

## Dependencies and Integration Points
It depends on `release-tools/prow.sh` being available relative to the current working directory, a working Go binary, and shell sourcing. `update-vendor.sh` invokes it before module tidy/vendor operations.

## Risks and Test Signals
Risks include path sensitivity because it sources `release-tools/prow.sh` rather than the script's own directory, and parsing failures if `go version` output changes. The signal is a visible warning when local Go differs from CI's configured Go version.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/verify-go-version.sh -->
