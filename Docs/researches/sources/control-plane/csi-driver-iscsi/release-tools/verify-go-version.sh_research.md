# sources/control-plane/csi-driver-iscsi/release-tools/verify-go-version.sh

Purpose: warns developers when their local Go major/minor differs from the build version configured in `release-tools/prow.sh`.

Important APIs and types: expects one argument: path to the Go binary. Internal `die` exits on missing binary/version failures.

Control flow: reads `go version`, extracts major.minor with sed, sources `release-tools/prow.sh` to read `CSI_PROW_GO_VERSION_BUILD`, and prints a prominent warning if versions differ.

State and persistence: read-only except stderr output.

Dependencies and integration: called by `update-vendor.sh`; depends on Go, sed, and a repo-root relative `release-tools/prow.sh`.

Risks: it only warns, never fails on mismatch. Sourcing `prow.sh` runs all `configvar` declarations and may emit output that is redirected away, but still evaluates shell code.

Test signals: warning presence/absence during local vendor updates.
