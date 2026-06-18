<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/verify-vendor.sh -->
# sources/control-plane/csi-driver-smb/release-tools/verify-vendor.sh

Purpose: Verifies Go module and vendor content are up to date, with Prow-aware skip logic for presubmits that do not affect dependencies.

Important behavior: If `go.mod` exists, it may skip in Prow when a presubmit did not touch dependency-sensitive files/imports. Otherwise it runs `go mod tidy`, checks `go.mod`/`go.sum` cleanliness, runs `go mod vendor` when `vendor/` exists, and checks vendor cleanliness.

Control flow: Shell condition combines job type and git diff checks to decide skipping. Failures print diffs/status and exit nonzero.

State and persistence behavior: Runs tidy/vendor, which can mutate `go.mod`, `go.sum`, and `vendor`; it then fails if mutations occurred.

Dependencies and integration points: Used by CI verify targets to enforce dependency reproducibility.

Risks: The skip heuristic may miss dependency impacts outside its diff/import patterns. It references `${JOB_NAME}` with no default under non-strict shell, which is okay here but would be unsafe under nounset. Running it on a dirty worktree can conflate preexisting changes with generated drift.

Test signals: Strong dependency reproducibility signal for module-based repos.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/verify-vendor.sh -->
