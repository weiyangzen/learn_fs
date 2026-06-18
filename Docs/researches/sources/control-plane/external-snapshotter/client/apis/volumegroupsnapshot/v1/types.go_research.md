# sources/control-plane/external-snapshotter/client/apis/volumegroupsnapshot/v1/types.go

## Purpose
Defines the stable Kubernetes CRD Go types for CSI volume group snapshots, classes, and contents.

## Important APIs, Types, and Functions
- `VolumeGroupSnapshotSpec`, `VolumeGroupSnapshotSource`, and `VolumeGroupSnapshotStatus`.
- Root object `VolumeGroupSnapshot` and `VolumeGroupSnapshotList`.
- Cluster-scoped `VolumeGroupSnapshotClass` and list.
- Cluster-scoped `VolumeGroupSnapshotContent`, `VolumeGroupSnapshotContentSpec`, `VolumeGroupSnapshotContentStatus`, and list.
- `VolumeSnapshotInfo`, `VolumeGroupSnapshotContentSource`, `GroupSnapshotHandles`, and legacy conversion helper `VolumeSnapshotHandlePair`.

## Control Flow
There are no functions. Behavior is declarative through Go fields, JSON/protobuf tags, client-gen markers, kubebuilder resource/subresource/printcolumn markers, and CEL validation markers. Controllers and apiservers enforce the declared object shape.

## State and Persistence Behavior
Objects persist desired state (`spec`) and observed state (`status`) in Kubernetes. `VolumeGroupSnapshot` is namespaced; classes and contents are cluster-scoped. The API records binding names, class names, deletion policy, driver, selected PVC labels, backend volume handles, group snapshot handles, readiness, creation time, restore sizes, and errors. Many fields are immutable once set.

## Dependencies and Integration Points
Uses `k8s.io/api/core/v1` object references, `metav1` metadata/time/label selectors, and `volumesnapshot/v1` deletion policy/error types. Integrates with CSI snapshot-controller, CSI snapshotter sidecars, CRDs, generated clients, and conversion logic from beta versions.

## Risks
Binding is security-sensitive: consumers must verify both sides of the VolumeGroupSnapshot/Content reference before trusting data. Dynamic selection by label freezes after content creation, so late PVC label changes do not update an existing group snapshot. API compatibility depends on protobuf tag stability and conversion from older handle-pair fields to `VolumeSnapshotInfoList`.

## Test Signals
CRD schema generation, CEL validation tests, controller reconciliation tests, conversion tests from beta versions, and client round-trip tests should cover these declarations.
