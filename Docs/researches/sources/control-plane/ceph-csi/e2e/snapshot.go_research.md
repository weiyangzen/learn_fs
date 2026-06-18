# sources/control-plane/ceph-csi/e2e/snapshot.go

Purpose: wraps Kubernetes CSI snapshot APIs for e2e creation, deletion, class setup, content discovery, and restore-size validation.

Important APIs and flow: `getSnapshotClass` and `getSnapshot` unmarshal example YAML. `newSnapshotClient` builds an external-snapshotter v1 client from the e2e kubeconfig. `createSnapshot` creates a `VolumeSnapshot` and polls `Status.ReadyToUse`. `deleteSnapshot` deletes and polls for NotFound. `createRBDSnapshotClass`, `createCephFSSnapshotClass`, and `createNFSSnapshotClass` load example classes, inject cluster ID and secret references, then create them. Delete helpers remove the classes. `getVolumeSnapshotContent` follows `VolumeSnapshot.Status.BoundVolumeSnapshotContentName`. `validateBiggerPVCFromSnapshot` provisions a source PVC/app, snapshots it, restores into a larger PVC, validates filesystem or block size, and for block RBD verifies snapshot metadata keys were not propagated to the restored image.

State and persistence: creates cluster-scoped `VolumeSnapshotClass` objects, namespace-scoped `VolumeSnapshot` and PVC/app objects, and backend snapshots through the CSI snapshotter. Restore validation leaves no intended resources after cleanup.

Dependencies and integration: depends on external-snapshotter client APIs, shared PVC/pod helpers, RBD/CephFS/NFS example paths, cluster ID discovery, RBD metadata helpers, and resize validation from `resize.go`.

Risks and test signals: snapshot readiness depends on CRD/controller availability. `getVolumeSnapshotContent` dereferences snapshot status fields and assumes the snapshot is already bound. `validateBiggerPVCFromSnapshot` assumes an RBD image list ordering when checking restored block metadata. Successful tests signal snapshot class wiring, snapshot controller readiness, restore provisioning, resize-from-snapshot support, and correct cleanup of snapshot metadata on RBD restore.
