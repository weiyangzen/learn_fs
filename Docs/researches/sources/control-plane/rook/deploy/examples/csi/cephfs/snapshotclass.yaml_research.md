<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/snapshotclass.yaml -->
# sources/control-plane/rook/deploy/examples/csi/cephfs/snapshotclass.yaml

Purpose: defines the standard CephFS CSI `VolumeSnapshotClass`.
Important APIs/types/functions: `VolumeSnapshotClass`, driver `rook-ceph.cephfs.csi.ceph.com`, `clusterID`, snapshotter secret name/namespace, and `deletionPolicy: Delete`.
Control flow: the snapshot controller maps `VolumeSnapshot` requests to this class, supplies secret parameters to the CephFS CSI driver, and deletes backend snapshots when snapshot content is removed. State is a cluster-scoped class plus generated `VolumeSnapshotContent`. Dependencies are CephFS CSI, Rook provisioner secret, and snapshot external controller. Risks: secret namespace must track the Rook namespace, delete policy can remove restore points, and driver name must match the installed CSIDriver. Test signals: class exists, `snapshot.yaml` reaches ready, and deletion cleans up content without orphan errors.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/snapshotclass.yaml -->
