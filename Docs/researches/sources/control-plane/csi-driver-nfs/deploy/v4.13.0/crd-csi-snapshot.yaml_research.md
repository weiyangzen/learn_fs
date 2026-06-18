<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.13.0/crd-csi-snapshot.yaml

## Purpose
Installs the CSI snapshot CRDs for the v4.13.0 NFS CSI deployment bundle. The file defines `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` under `snapshot.storage.k8s.io`.

## Important APIs, Types, And Objects
The CRDs expose `v1` as the only served and stored API version. Deprecated `v1beta1` schemas remain in the manifest but are not served or stored. `VolumeSnapshot` is namespaced and selects either a PVC source or existing content source. `VolumeSnapshotClass` is cluster-scoped driver policy. `VolumeSnapshotContent` is cluster-scoped backing snapshot state with required policy, driver, source, and snapshot reference fields.

## Control Flow
The apiserver registers these resources and enforces schema validation. The snapshot controller watches and updates them, while the NFS CSI snapshotter performs driver-specific CSI snapshot calls for classes using `nfs.csi.k8s.io`.

## State And Persistence Behavior
CRDs and custom resources are persisted in etcd. Snapshot status subresources carry controller-observed readiness, restore size, errors, creation time, and CSI snapshot handles.

## Dependencies And Integration Points
Used by v4.13.0 `snapshot-controller:v8.4.0` and `csi-snapshotter:v8.4.0`. Also integrates with RBAC, `snapshotclass.yaml`, and any workloads restoring PVCs from snapshots.

## Risks And Edge Cases
Cluster-wide CRD changes require upgrade care. Clients using `v1beta1` will fail because it is not served. Restore consumers must verify bound snapshot/content references before treating a snapshot as valid. The CRD schema must remain compatible with the sidecar versions in the same bundle.

## Test Signals
Run server-side apply validation, API discovery checks, invalid object rejection tests, dynamic snapshot creation, pre-provisioned content binding, and status update verification with the v8.4.0 controller/sidecar.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/crd-csi-snapshot.yaml -->
