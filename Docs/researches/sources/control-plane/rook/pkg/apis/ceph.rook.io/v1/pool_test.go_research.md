# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/pool_test.go

Purpose: unit-tests pool validation and mirroring snapshot-schedule helper behavior.

Important APIs/types/functions: tests `validatePoolSpec`, `CephBlockPool.ToNamedPoolSpec`, and `MirroringSpec.SnapshotSchedulesEnabled` using `CephBlockPool`, `PoolSpec`, `ReplicatedSpec`, `ErasureCodedSpec`, and `SnapshotScheduleSpec`.

Control flow: `TestValidatePoolSpec` mutates one `CephBlockPool` through invalid empty configuration, valid replicated size, valid erasure-coded chunks, and invalid simultaneous replicated/erasure-coded configuration, delegating through `ToNamedPoolSpec`. `TestMirroringSpec_SnapshotSchedulesEnabled` table-checks disabled and enabled schedule-list cases.

State and persistence: test-only local CRD structs; no persistence.

Dependencies/integration: uses testify assertions and standard testing. It protects validation used before Ceph pool reconciliation.

Risks: the mirroring test case named `"disabled"` sets `Enabled: true` but an empty schedule list, documenting that helper behavior ignores the enabled flag. Tests do not cover built-in pool erasure-coding rejection, target-size-ratio-only replicated pools, minimum EC data/coding chunk failures, hybrid storage, status condition accessors, or name override fallback.

Test signals: basic positive/negative validation coverage with focused schedule-list behavior.
