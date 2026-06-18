## sources/control-plane/csi-driver-host-path/release-tools/verify-go-version.sh

Purpose: warns developers when their Go major/minor version differs from the version configured for CSI Prow builds.

Control flow requires a Go binary path, extracts major.minor from `go version` with sed, sources `release-tools/prow.sh` to read `CSI_PROW_GO_VERSION_BUILD`, and prints a large warning if versions differ. It does not fail on mismatch.

State is none beyond sourced shell variables. Dependencies are bash, sed, the Go binary, and release-tools path. Risks include sourcing the very large `prow.sh` for one variable, version parsing drift, and warning-only behavior allowing incompatible local runs. Test signal is console output during update/vendor scripts.
