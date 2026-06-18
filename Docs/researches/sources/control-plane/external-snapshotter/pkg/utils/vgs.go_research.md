# sources/control-plane/external-snapshotter/pkg/utils/vgs.go

Purpose: utilities for detecting and indexing `VolumeSnapshot` membership in a `VolumeGroupSnapshot`, and for building owner references from group snapshots.

Important APIs/functions: `VolumeSnapshotParentGroupIndex`, `getVolumeGroupSnapshotParentObjectName`, `IsVolumeGroupSnapshotMember`, `VolumeSnapshotParentGroupKeyFunc`, `VolumeSnapshotParentGroupKeyFuncByComponents`, `NeedToAddVolumeGroupSnapshotOwnership`, and `BuildVolumeGroupSnapshotOwnerReference`.

Control flow: owner-reference scanning looks for `Kind=VolumeGroupSnapshot` with the current group snapshot API version. Key generation returns `namespace^parentName`. Ownership-add detection requires no existing owner reference and a non-empty `Status.VolumeGroupSnapshotName`. Owner-reference construction fills APIVersion, kind, name, and UID.

State and persistence: stateless; callers persist owner references or use keys in informer indexes.

Dependencies and integration: depends on snapshot and group snapshot CRD types, Kubernetes metadata, and namespaced names. It supports group snapshot reconciliation and snapshot indexing.

Risks and test signals: risks include API-version mismatch across beta/stable group snapshot versions, separator collision in keys, and using status as an ownership source before status is fully reconciled. Tests cover nil/no/wrong/correct owner references and ownership-add predicates.
