# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/pool.go

Purpose: implements Ceph block pool helper methods and validation for replicated, erasure-coded, hybrid, named, and mirrored pool specs.

Important APIs/types/functions: `PoolSpec.IsReplicated`, `PoolSpec.IsErasureCoded`, `PoolSpec.IsHybridStoragePool`, `ValidateCephBlockPool`, `validatePoolSpec`, `CephBlockPool.ToNamedPoolSpec`, `CephBlockPool.GetStatusConditions`, `CephBlockPoolRadosNamespace.GetStatusConditions`, and `MirroringSpec.SnapshotSchedulesEnabled`.

Control flow: pool kind helpers inspect replicated size, erasure-coded data/coding chunks, and hybrid-storage pointer presence. `ValidateCephBlockPool` rejects erasure coding for Ceph built-in pools `.rgw.root`, `.mgr`, and `.nfs`, then delegates to generic named-pool validation. `validatePoolSpec` requires either erasure-coded or replicated configuration, rejects simultaneous erasure-coded and replicated settings, and enforces minimum data/coding chunks when replication is not selected. `ToNamedPoolSpec` uses `spec.name` when provided or falls back to the Kubernetes CR name. Snapshot scheduling is considered enabled whenever the schedule list is non-empty.

State and persistence: no persistence. Status accessors return condition-slice pointers for status update helpers. Validation reads only CRD fields.

Dependencies/integration: depends on `github.com/pkg/errors`. Reconciler code uses this to reject invalid pool CRs and to produce normalized `NamedPoolSpec` input for Ceph pool creation.

Risks: `SnapshotSchedulesEnabled` ignores `MirroringSpec.Enabled` and mode; schedule presence alone controls the result. Erasure-coded detection includes `Algorithm` during validation conflict checks, but `IsErasureCoded` only checks chunk fields. `ToNamedPoolSpec` allows `Spec.Name` to override resource identity, which consumers must handle carefully.

Test signals: `pool_test.go` covers missing replication/EC configuration, replicated success, EC success, simultaneous EC/replicated rejection, and snapshot-schedule presence behavior.
