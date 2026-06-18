<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/pvc.yaml -->
# sources/control-plane/rook/deploy/examples/csi/cephfs/pvc.yaml

Purpose: baseline CephFS PVC used by pod, snapshot, clone, and group snapshot examples.
Important APIs/types/functions: `PersistentVolumeClaim` `cephfs-pvc`, label `group: snapshot-test`, access mode `ReadWriteOnce`, request `1Gi`, and StorageClass `rook-cephfs`.
Control flow: Kubernetes asks the CephFS CSI provisioner to create a subvolume in the configured filesystem/pool and binds the resulting PV to this claim. State is persisted in Kubernetes PV/PVC objects and CephFS subvolume metadata. Dependencies are the `rook-cephfs` StorageClass and Rook CephFS secrets. Risks: CephFS commonly supports RWX, but this sample uses RWO, so it only validates single-writer semantics; the label controls inclusion in group snapshots. Test signals: PVC transitions to Bound, PV uses `rook-ceph.cephfs.csi.ceph.com`, and snapshot/clone examples can reference it.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/pvc.yaml -->
