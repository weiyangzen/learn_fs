<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/test-go.sh -->
## sources/control-plane/ceph-csi/scripts/test-go.sh

Purpose: runs Go tests across non-vendor, non-e2e packages, with optional exit-first and coverage modes.

Control flow: detects vendor mode, lists packages, and either execs a single `go test` command or loops packages individually. Coverage mode writes a combined `profile.cov`, appends package cover profiles, optionally prints function coverage or writes HTML files under `GO_COVER_DIR`, and exits with failure count.

State and persistence: writes `cover.out`, combined coverfile, and optional HTML coverage artifacts.

Dependencies: Go toolchain, package list, environment variables `GO_COVER_DIR`, `TEST_EXITFIRST`, `TEST_COVERAGE`, `GO_TAGS`.

Integration points: unit-test CI entrypoint.

Risks: `GO_COVER_DIR` must be set for coverage paths. Package loop continues after failures unless exit-first is enabled, which is useful for complete reports but can be slower.

Test signals: this is the test runner itself.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/test-go.sh -->
