# sources/control-plane/external-snapshotter/client/apis/volumegroupsnapshot/v1beta1/types.go

## Purpose
Defines the first beta version of CSI volume group snapshot CRD types.

## Important APIs, Types, and Functions
- Same main object families as stable `v1`: `VolumeGroupSnapshot`, `VolumeGroupSnapshotClass`, `VolumeGroupSnapshotContent`, specs/statuses/sources/lists.
- `VolumeSnapshotHandlePairList` in `VolumeGroupSnapshotContentStatus`.
- `VolumeSnapshotHandlePair` pairs a source volume handle with a snapshot handle.
- Kubebuilder objects are marked `+kubebuilder:deprecatedversion`.

## Control Flow
The file is declarative. Kubernetes code generators and CRD generation consume struct tags and markers; controllers populate status from CSI operations.

## State and Persistence Behavior
Persists group snapshot desired and observed state in Kubernetes. Compared with later versions, status stores per-snapshot backend data as handle pairs rather than richer `VolumeSnapshotInfo` entries. Many immutability guarantees are documented and partly expressed through CEL markers.

## Dependencies and Integration Points
Uses `core/v1.ObjectReference`, `metav1`, and snapshot `v1` `DeletionPolicy`/`VolumeSnapshotError`. Integrates with conversion logic that migrates `VolumeSnapshotHandlePairList` into newer `VolumeSnapshotInfoList`.

## Risks
Deprecated API version should not be used for new clients. Any conversion bug risks losing per-volume/per-snapshot association data. Its validation is less strict than stable/newer versions for some immutable fields.

## Test Signals
Conversion tests from v1beta1 to v1beta2/v1, CRD schema tests, and controller compatibility tests with old objects are the key signals.
