# sources/control-plane/csi-driver-nfs/release-tools/verify-go-version.sh

Purpose: warns when the locally used Go toolchain major/minor version differs from the version configured for Prow builds.

Important arguments and commands: requires one argument pointing to a Go binary, runs `<go> version`, extracts major.minor with sed, sources `release-tools/prow.sh` to read `CSI_PROW_GO_VERSION_BUILD`, and prints a warning block on mismatch.

Control flow: exits with usage error when no Go binary is provided; otherwise only warns on mismatch and does not fail.

State and persistence behavior: no mutation. It reads toolchain version and release-tools configuration.

Dependencies and integration points: called by `update-vendor.sh` and local verification workflows. Depends on `prow.sh` being sourceable from the current repo root.

Risks: sourcing `prow.sh` executes its top-level `configvar` calls and prints unless redirected, so future top-level side effects would affect this script. Version extraction ignores patch versions intentionally.

Test signals: warning text is the only signal; downstream commands continue.
