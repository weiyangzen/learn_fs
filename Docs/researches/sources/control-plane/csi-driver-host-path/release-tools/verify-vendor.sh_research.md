## sources/control-plane/csi-driver-host-path/release-tools/verify-vendor.sh

Purpose: verifies dependency metadata and vendor directories are up to date for dep or Go module repos.

Control flow uses `dep check` for supported dep versions. For Go modules, Prow presubmits can skip the check when diffs do not touch dependency-relevant files/imports. Otherwise it runs `go mod tidy`, fails if go.mod/go.sum change, optionally runs `go mod vendor`, and fails if vendor changes.

State is potentially modified go.mod/go.sum/vendor in the working tree during verification. Dependencies are bash, git, dep or Go modules, and Prow environment variables for skip logic. Risks include `${JOB_NAME}` under unset-variable shells, imperfect import-diff heuristic, and leaving modified files after failure. Test signal is git diff/status output and exit status.
