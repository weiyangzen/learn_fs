# sources/control-plane/beegfs-csi-driver/release-tools/verify-go-version.sh

Purpose: Warns when the active Go toolchain version does not match the Go version expected by `release-tools/prow.sh`.

Important APIs/types/functions: Takes one argument, the path/name of a Go binary. Extracts major.minor from `$GO version`, sources `release-tools/prow.sh` to read `CSI_PROW_GO_VERSION_BUILD`, and prints a warning block if versions differ.

Control flow: Validates argument, runs Go version command, parses with sed, sources `prow.sh` with output suppressed, compares major.minor strings, and emits warning text. It does not fail on mismatch.

State and persistence: No file writes. Sourcing `prow.sh` evaluates config defaults in the current shell, but output is redirected for the expected-version read.

Dependencies and integration points: Used by `update-vendor.sh` before module tidy/vendor operations. Requires a local `release-tools/prow.sh` path and a working Go binary.

Risks: Sourcing a large script for one variable can run side-effectful top-level config evaluation and depends on relative working directory. It only compares major.minor, not patch. The warning text contains minor grammar issues but is operationally clear.

Test signals: Human-visible warning when Go version differs; no nonzero exit for mismatch.
