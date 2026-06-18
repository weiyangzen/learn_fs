# sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/drain_test.go

Purpose: verifies mgr PDB reconciliation and deletion.

Important APIs and tests: `createFakeCluster` builds a mgr `Cluster` with controller-runtime fake client, Kubernetes fake clientset, policy/v1 scheme, owner info, and a fake Kubernetes version. `TestReconcileMgrPDB` calls `reconcileMgrPDB`, fetches the PDB, asserts `maxUnavailable=1`, and calls reconcile again to verify idempotent update. `TestDeleteMgrPDB` creates the PDB, calls `deleteMgrPDB`, and expects a later GET to fail.

Control flow: tests operate directly on mgr `Cluster` methods rather than through `Cluster.Start`, so they isolate PDB behavior from deployment creation and mgr count decisions.

State and persistence behavior: fake controller-runtime client stores the PDB. No status or external state is modified.

Dependencies and integration points: uses Rook client scheme, fake controller-runtime client, Rook test clientset, Kubernetes policy/v1 types, and `testify/assert`.

Risks: the test case name says "1 mgr" even though direct reconciliation creates the PDB regardless of count; the caller's count-based decision is not tested here. Delete error logging paths and not-found behavior are not asserted.

Test signals: solid unit signal for PDB object shape and delete behavior, limited signal for integration with mgr replica counts.
