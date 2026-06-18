## sources/control-plane/csi-driver-nfs/release-tools/verify-vendor.sh

Purpose: verifies Go module metadata and optional `vendor/` content are up to date. It only runs in repositories with `go.mod`, then compares the working tree after `go mod tidy` and, when present, `go mod vendor`.

Important flow: in Prow presubmit jobs it can skip the check when dependency-relevant files and import blocks have not changed. Otherwise it executes `GO111MODULE=on go mod tidy`, fails if `go.mod` or `go.sum` changed, then refreshes `vendor` and fails if vendor status or diff changed.

State and persistence risk are important: the script intentionally mutates module and vendor files during verification and uses git status/diff to detect whether those changes were needed. Dependencies include Go modules, git, and Prow variables such as `JOB_NAME`, `JOB_TYPE`, and `PULL_BASE_SHA`. Risks include unbound environment references in local `nounset`-free shell, shallow diff assumptions, and expensive vendor rewrites. Test signal is exact diff output for stale dependency artifacts.
