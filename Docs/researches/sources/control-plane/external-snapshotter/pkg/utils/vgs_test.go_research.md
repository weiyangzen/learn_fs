# sources/control-plane/external-snapshotter/pkg/utils/vgs_test.go

Purpose: tests group snapshot membership detection, parent index key generation, and ownership-add predicates for `VolumeSnapshot` objects.

Important APIs/functions: `TestIsVolumeSnapshotGroupMember` and `TestNeedToAddVolumeGroupSnapshotOwnership`.

Control flow: table tests cover nil snapshots, snapshots without ownership, unrelated owner references, wrong group API version, correct group owner reference, missing ownership with status group name, and already-owned snapshots.

State and persistence: in-memory snapshot objects only.

Dependencies and integration: validates helper behavior for group snapshot controllers and informer indexes.

Risks and test signals: good signal for owner-reference parsing and missing-owner detection. It does not assert `BuildVolumeGroupSnapshotOwnerReference` directly or key generation from explicit components separately.
