<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.1/crd-csi-snapshot.yaml

## Purpose
Installs the same CSI snapshot API CRDs used by the v4.12.1 NFS CSI deployment. It defines `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` in the `snapshot.storage.k8s.io` API group.

## Important APIs, Types, And Objects
`VolumeSnapshot` is namespaced and supports PVC-backed dynamic snapshots or binding to existing `VolumeSnapshotContent`. `VolumeSnapshotClass` is cluster-scoped and requires `driver` and `deletionPolicy`. `VolumeSnapshotContent` is cluster-scoped and requires `deletionPolicy`, `driver`, `source`, and `volumeSnapshotRef`. The `v1` versions are served/storage; deprecated `v1beta1` versions are declared but not served or stored.

## Control Flow
Apply this before snapshot controller and class manifests. The API server validates snapshot resources, then the external snapshot controller and per-driver CSI snapshotter reconcile those objects and call the NFS CSI driver where appropriate.

## State And Persistence Behavior
CRDs persist API definitions cluster-wide; snapshot resources created under them persist desired and observed state in etcd. Status subresources hold readiness, restore size, creation time, errors, and binding information.

## Dependencies And Integration Points
Depends on Kubernetes apiextensions v1 and external-snapshotter schema compatibility. Integrates with the v4.12.1 `csi-snapshot-controller.yaml`, `rbac-snapshot-controller.yaml`, `snapshotclass.yaml`, and `csi-nfs-controller.yaml`.

## Risks And Edge Cases
The beta API is unavailable despite schema presence, so old clients must use `snapshot.storage.k8s.io/v1`. The CRDs are shared infrastructure for all CSI snapshot-capable drivers. Binding correctness requires both `VolumeSnapshot` and `VolumeSnapshotContent` references to match before consumers restore from a snapshot.

## Test Signals
Validate server-side apply, confirm API discovery for all three resources, create both valid and invalid snapshot requests, and ensure the snapshot controller can update status subresources without schema or RBAC errors.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/crd-csi-snapshot.yaml -->
