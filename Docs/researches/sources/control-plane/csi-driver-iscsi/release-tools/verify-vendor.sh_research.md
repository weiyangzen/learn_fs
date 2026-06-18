# sources/control-plane/csi-driver-iscsi/release-tools/verify-vendor.sh

Purpose: validates that Go module and vendor metadata are up to date.

Important APIs and types: top-level shell checks `go.mod`, Prow variables `JOB_NAME`, `JOB_TYPE`, and `PULL_BASE_SHA`, and uses `go mod tidy` plus optional `go mod vendor`.

Control flow: if in a Prow presubmit whose diff does not touch dependency-relevant files or imports, skips the check. Otherwise runs tidy, fails if `go.mod` or `go.sum` changed, runs vendor when a vendor directory exists, and fails if vendor changed.

State and persistence: Go commands may modify module and vendor files; the script then reports those diffs as failures.

Dependencies and integration: used from Makefile test targets in importing repos. Depends on Git, Go modules, and Prow env for skip optimization.

Risks: references `${JOB_NAME}` without a default under non-strict shell, so local unset variables evaluate empty but would break under nounset. The skip heuristic can miss dependency effects outside import/go.mod/vendor/release-tools changes.

Test signals: clean git status after tidy/vendor and verifier exit code.
