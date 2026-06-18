<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/snapshotclass.yaml -->
# sources/control-plane/rook/deploy/examples/csi/rbd/snapshotclass.yaml

Purpose: defines the RBD CSI `VolumeSnapshotClass`.
Important APIs/types/functions: `VolumeSnapshotClass`, driver `rook-ceph.rbd.csi.ceph.com`, `clusterID`, RBD snapshotter secret parameters, and `deletionPolicy: Delete`.
Control flow: snapshot requests referencing this class are routed to the RBD CSI driver with Rook provisioner credentials; deletion of snapshot content removes backend RBD snapshots. State is cluster-scoped class configuration and generated snapshot content. Dependencies are RBD CSI sidecars, Rook provisioner secret in `rook-ceph`, and snapshot CRDs/controller. Risks: wrong secret namespace or driver name breaks snapshots; delete policy is destructive. Test signals: class exists, `snapshot.yaml` reaches ready, and deleting the snapshot removes content without stuck finalizers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/snapshotclass.yaml -->
