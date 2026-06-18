<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/pvc-restore.yaml -->
# sources/control-plane/rook/deploy/examples/csi/rbd/pvc-restore.yaml

Purpose: restores a new RBD PVC from an RBD volume snapshot.
Important APIs/types/functions: `PersistentVolumeClaim`, `dataSource.kind: VolumeSnapshot`, `apiGroup: snapshot.storage.k8s.io`, source `rbd-pvc-snapshot`, and StorageClass `rook-ceph-block`.
Control flow: the external provisioner resolves the snapshot and asks RBD CSI to create a new image from it, then binds the PVC. State persists in the new PV/PVC and cloned/restored RBD image. Dependencies are snapshot CRDs/controller, a ready snapshot from `snapshot.yaml`, `snapshotclass.yaml`, and compatible image features. Risks: restore requires snapshot content to exist, restored size cannot be smaller than source, and deletion policy may remove backend snapshots. Test signals: PVC Bound, pod mount succeeds, and data matches the snapshot point.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/pvc-restore.yaml -->
