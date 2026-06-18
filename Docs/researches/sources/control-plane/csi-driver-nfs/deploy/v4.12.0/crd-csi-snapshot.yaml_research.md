<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.0/crd-csi-snapshot.yaml

## Purpose
Installs the Kubernetes CSI snapshot API surface required by the NFS CSI deployment. The file defines three `apiextensions.k8s.io/v1` CRDs in API group `snapshot.storage.k8s.io`: namespaced `VolumeSnapshot`, cluster-scoped `VolumeSnapshotClass`, and cluster-scoped `VolumeSnapshotContent`.

## Important APIs, Types, And Objects
`VolumeSnapshot` models a user's snapshot request. Its `spec.source` is a one-of union of `persistentVolumeClaimName` for dynamic creation or `volumeSnapshotContentName` for binding an existing content object. Status exposes `readyToUse`, `restoreSize`, `creationTime`, `error`, and `boundVolumeSnapshotContentName`.

`VolumeSnapshotClass` stores driver-level snapshot parameters with required `driver` and `deletionPolicy` values. `VolumeSnapshotContent` stores the cluster object that represents the backing CSI snapshot, requiring `deletionPolicy`, `driver`, `source`, and `volumeSnapshotRef`, plus status fields such as CSI `snapshotHandle`.

All three resources serve and store `v1`. Deprecated `v1beta1` schemas are present with warnings but `served: false` and `storage: false`, so beta clients cannot use them after this CRD is applied.

## Control Flow
This file must be applied before `csi-snapshot-controller.yaml`, `rbac-snapshot-controller.yaml`, and any `VolumeSnapshotClass` or `VolumeSnapshot` objects. Once registered, the Kubernetes API server validates snapshot objects against these schemas and stores them in etcd. The snapshot controller watches `VolumeSnapshot` and `VolumeSnapshotContent`; the CSI snapshotter sidecar binds requests to the NFS CSI driver over the controller socket.

## State And Persistence Behavior
The CRDs themselves are durable cluster-level API definitions. Snapshot objects created through them are persisted in Kubernetes etcd, with desired state in `spec` and controller-owned progress in `status` subresources. This manifest has no local filesystem state, but it changes the cluster's API discovery and validation behavior.

## Dependencies And Integration Points
Depends on the Kubernetes apiextensions API and the external-snapshotter API contract. It integrates with the snapshot controller RBAC, snapshot controller deployment, CSI snapshotter sidecar in the NFS controller deployment, and `snapshotclass.yaml` using driver `nfs.csi.k8s.io`.

## Risks And Edge Cases
Applying CRDs is cluster-wide and can affect every snapshot client. Because `v1beta1` is not served, older automation still using beta snapshot APIs will fail. Consumers must validate the bidirectional binding between `VolumeSnapshot` and `VolumeSnapshotContent` before restore. `sourceVolumeMode` is marked alpha in the schema, so compatibility should be checked during Kubernetes upgrades. The empty `status.acceptedNames` and `storedVersions` blocks are harmless in manifests because the apiserver owns CRD status.

## Test Signals
Use server-side dry-run or `kubectl apply --server-side --dry-run=server` to validate the CRDs, then confirm API discovery for `volumesnapshots`, `volumesnapshotclasses`, and `volumesnapshotcontents`. Exercise creation of a class, a PVC-backed `VolumeSnapshot`, status updates by the controller, and rejection of invalid source objects with neither or both source fields.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/crd-csi-snapshot.yaml -->
