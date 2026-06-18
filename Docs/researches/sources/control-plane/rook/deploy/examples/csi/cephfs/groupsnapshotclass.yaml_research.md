<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/groupsnapshotclass.yaml -->
# sources/control-plane/rook/deploy/examples/csi/cephfs/groupsnapshotclass.yaml

Purpose: declares the CephFS CSI group snapshot class used by the CephFS group snapshot example.
Important APIs/types/functions: `VolumeGroupSnapshotClass`, driver `rook-ceph.cephfs.csi.ceph.com`, `clusterID`, `fsName`, CSI group-snapshotter secret parameters, and `deletionPolicy: Delete`.
Control flow: the group snapshot controller resolves this class, passes cluster/filesystem identity and provisioner secret references to the CephFS CSI driver, and uses the deletion policy to remove backend group snapshot data when the API object is deleted. State lives in the cluster-scoped snapshot class plus Ceph snapshot metadata. Dependencies are CephFS CSI, Rook-generated `rook-csi-cephfs-provisioner` secret in `rook-ceph`, and filesystem `myfs`. Risks: stale `fsName`, wrong namespace in `clusterID`, missing beta group snapshot support, and destructive delete policy. Test signals: class is accepted, driver name matches installed CSIDriver, and a matching `VolumeGroupSnapshot` becomes ready.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/groupsnapshotclass.yaml -->
