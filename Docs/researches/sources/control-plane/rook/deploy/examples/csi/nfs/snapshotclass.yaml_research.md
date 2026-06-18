<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/snapshotclass.yaml -->
# sources/control-plane/rook/deploy/examples/csi/nfs/snapshotclass.yaml

Purpose: defines the NFS CSI `VolumeSnapshotClass`.
Important APIs/types/functions: `VolumeSnapshotClass`, driver `rook-ceph.nfs.csi.ceph.com`, `clusterID`, snapshotter secret parameters that reuse CephFS provisioner credentials, and `deletionPolicy: Delete`.
Control flow: the external snapshotter uses this class to route NFS snapshot operations and provide credentials to the driver. State is cluster-scoped class configuration plus generated snapshot content. Dependencies are NFS CSI driver, Rook CSI CephFS provisioner secret, and snapshot controller. Risks: secret reuse couples NFS snapshotting to CephFS secret names, driver name mismatch prevents binding, and deletion policy destroys backend snapshots. Test signals: class accepted, snapshot reaches ready, and deletion removes snapshot content cleanly.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/snapshotclass.yaml -->
