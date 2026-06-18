<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/verify-go-version.sh -->
# sources/control-plane/csi-driver-smb/release-tools/verify-go-version.sh

Purpose: Warns when the local Go major/minor version differs from the release-tools configured build Go version.

Important behavior: Requires a Go binary path argument, parses `go version`, sources `release-tools/prow.sh` to read `CSI_PROW_GO_VERSION_BUILD`, compares major.minor, and prints a warning block on mismatch.

Control flow: Missing argument or inability to run Go exits nonzero; version mismatch is warning-only and exits zero.

State and persistence behavior: No persistence, but sourcing `prow.sh` runs its top-level config logging.

Dependencies and integration points: Used by `update-vendor.sh` and vendor verification workflows.

Risks: The parser assumes standard `go version` output and exact major.minor match. Warning-only behavior may allow sensitive tidy/vendor changes under a different Go version.

Test signals: Provides advisory signal, not a hard gate.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/verify-go-version.sh -->
