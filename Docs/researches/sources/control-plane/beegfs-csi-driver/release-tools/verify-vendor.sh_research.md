<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/verify-vendor.sh -->
# sources/control-plane/beegfs-csi-driver/release-tools/verify-vendor.sh

Purpose: dependency/vendor consistency gate supporting older dep-based repos and Go modules.
Important APIs/functions: detects `Gopkg.toml` for `dep check`; detects `go.mod` for `go mod tidy` and, when `vendor/` exists, `go mod vendor`; compares `git status --porcelain` for `go.mod`, `go.sum`, and `vendor`.
Control flow/state: in Prow presubmits, uses `JOB_NAME`, `JOB_TYPE`, `PULL_BASE_SHA`, and git diffs to skip vendor checks when dependency-related files/imports are unchanged. Otherwise it runs module normalization and fails if files are modified.
Dependencies/integration: depends on dep or Go modules, git, and Prow env vars for skip behavior.
Risks/test signals: unquoted env tests can trip under strict shell in unusual envs; generated vendor changes are destructive to working tree until reverted by caller; skip heuristic only looks at imports and selected paths. Pass signal is up-to-date module/vendor status.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/verify-vendor.sh -->
