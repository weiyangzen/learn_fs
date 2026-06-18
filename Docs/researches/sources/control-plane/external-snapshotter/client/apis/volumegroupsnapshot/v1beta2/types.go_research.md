# sources/control-plane/external-snapshotter/client/apis/volumegroupsnapshot/v1beta2/types.go

## Purpose
Defines the second beta version of CSI volume group snapshot CRD types, very close to stable v1.

## Important APIs, Types, and Functions
- Main API families: `VolumeGroupSnapshot`, `VolumeGroupSnapshotClass`, `VolumeGroupSnapshotContent`, and list/spec/status/source helpers.
- `VolumeSnapshotInfo` stores volume handle, snapshot handle, creation time, readiness, and restore size.
- `VolumeGroupSnapshotContentStatus.VolumeSnapshotInfoList` replaces the v1beta1 handle-pair list.
- Storage-version markers are present on root resources.

## Control Flow
Declarative struct fields and kubebuilder markers drive CRD schema, client generation, validation, and printer columns. Controllers reconcile these API objects externally.

## State and Persistence Behavior
Persists namespaced group snapshot requests and cluster-scoped classes/contents. Status captures binding, backend group snapshot handle, creation time, readiness, errors, and detailed per-snapshot information. CEL markers enforce one-of source fields and immutability for key fields.

## Dependencies and Integration Points
Shares `DeletionPolicy` and `VolumeSnapshotError` with `volumesnapshot/v1`, and uses Kubernetes `ObjectReference`, label selectors, and metadata/time types. Conversion from v1beta1 maps old handle pairs into `VolumeSnapshotInfoList`.

## Risks
Because v1beta2 is a migration point, protobuf tag and field-name stability are important. Validation or conversion drift from stable v1 can create surprising API behavior during upgrades.

## Test Signals
Conversion and storage-version tests, CRD schema tests, and controller reconciliation tests using group snapshots provide coverage.
