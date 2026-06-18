## sources/control-plane/ceph-csi/examples/rbd/pvc-block-restore.yaml

Purpose: Example raw block PVC restored from an RBD `VolumeSnapshot`.

Important API surface: PVC `rbd-block-pvc-restore`, `dataSource` referencing `rbd-pvc-snapshot` in API group `snapshot.storage.k8s.io`, `volumeMode: Block`, `ReadWriteOnce`, and `1Gi` request.

Control flow and state: The external provisioner passes the snapshot source to RBD CSI, which creates a new block-mode RBD image from the snapshot and binds it to the PVC.

Dependencies and risks: Requires `snapshot.yaml`, `snapshotclass.yaml`, a snapshot controller, and a source snapshot compatible with block restore semantics. Requested size must be at least snapshot size. Test by publishing via `pod-block-restore.yaml` and validating block data.
