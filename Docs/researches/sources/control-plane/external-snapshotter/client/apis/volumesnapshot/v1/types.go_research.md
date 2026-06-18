# sources/control-plane/external-snapshotter/client/apis/volumesnapshot/v1/types.go

## Purpose
Defines the stable CSI VolumeSnapshot, VolumeSnapshotClass, and VolumeSnapshotContent Kubernetes API types.

## Important APIs, Types, and Functions
- `VolumeSnapshot`, `VolumeSnapshotSpec`, `VolumeSnapshotSource`, and `VolumeSnapshotStatus`.
- Cluster-scoped `VolumeSnapshotClass` with `Driver`, `Parameters`, and `DeletionPolicy`.
- Cluster-scoped `VolumeSnapshotContent`, `VolumeSnapshotContentSpec`, `VolumeSnapshotContentSource`, and `VolumeSnapshotContentStatus`.
- `DeletionPolicy` enum with `Delete` and `Retain`.
- `VolumeSnapshotError` for controller-reported failures.

## Control Flow
This file is declarative. Controllers implement behavior by reconciling specs/statuses; the apiserver and CRD validation enforce shape, one-of source rules, enum values, and immutability markers.

## State and Persistence Behavior
Persists namespaced snapshot requests, cluster-scoped classes, and cluster-scoped content objects. Status mirrors backend CSI data: snapshot handle, creation time, readiness, restore size, errors, source volume mode, and optional group snapshot linkage. Snapshot and content status are eventually consistent copies of some CSI-derived fields.

## Dependencies and Integration Points
Uses Kubernetes `core/v1` object references and volume modes, `resource.Quantity`, and `metav1`. Integrates with snapshot-controller, CSI snapshotter sidecar, CRDs, generated clients, PVC restore workflows, and group snapshot status linkage.

## Risks
Consumers must verify bidirectional binding between `VolumeSnapshot` and `VolumeSnapshotContent` before trust. Restore size must be honored to avoid invalid restores. Error messages must not contain sensitive data. Source fields and backend handles are immutable and require careful migration.

## Test Signals
CRD schema/CEL validation tests, controller reconciliation tests, restore tests, fake-client tests, and CSI sidecar integration tests should cover the API contract.
