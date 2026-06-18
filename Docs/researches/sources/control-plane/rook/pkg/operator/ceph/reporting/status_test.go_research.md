# sources/control-plane/rook/pkg/operator/ceph/reporting/status_test.go

Purpose: verifies status and condition update helpers against controller-runtime fake clients.

Important APIs/types/functions: `TestUpdateStatus` and `TestUpdateStatusCondition`.

Control flow: `TestUpdateStatus` first covers an object whose status is initially unset, then covers a block pool status phase transition to Ready. `TestUpdateStatusCondition` sets up an object store and block pool, then subtests adding a new deletion-blocked condition, adding two distinct conditions to a block pool, and updating an existing condition to a different status/reason/message.

State and persistence behavior: fake client object tracker persists status mutations, and tests fetch objects after each update to validate persisted data rather than only local object mutation.

Dependencies/integration: uses Ceph API schemes/objects, controller-runtime fake client, Kubernetes condition statuses, and testify.

Risks: the first subtest prints an object copy but does not assert much about it. Conflict retry, status-subresource failure modes, and background-context cancellation behavior are not covered.

Test signals: confirms that condition insertion and replacement flow through `cephv1.SetStatusCondition` and that persisted status phase changes can be observed by a fresh client get.
