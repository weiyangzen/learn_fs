# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/cleanup.go

Purpose: defines cleanup/sanitize constants and small helpers for Ceph cluster data cleanup policy.

Important APIs/types/functions: constants `SanitizeDataSourceZero`, `SanitizeDataSourceRandom`, `SanitizeMethodComplete`, `SanitizeMethodQuick`, `DeleteDataDirOnHostsConfirmation`; methods `CleanupPolicySpec.HasDataDirCleanPolicy`, `SanitizeMethodProperty.String`, and `SanitizeDataSourceProperty.String`.

Control flow: cleanup policy logic checks for exact confirmation string `yes-really-destroy-data` before treating host data dir cleanup as enabled.

State and persistence: no mutable state; values are persisted in `CephCluster.spec.cleanupPolicy`.

Dependencies/integration: depends on API types generated elsewhere in package v1.

Risks: confirmation string is intentionally strict; typos silently disable destructive cleanup.

Test signals: cluster validation/reconcile tests should cover confirmation, sanitize method/source string conversion, and destructive cleanup opt-in.
