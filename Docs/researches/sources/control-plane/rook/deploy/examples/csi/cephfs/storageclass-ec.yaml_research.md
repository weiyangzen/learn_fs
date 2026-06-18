<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/storageclass-ec.yaml -->
# sources/control-plane/rook/deploy/examples/csi/cephfs/storageclass-ec.yaml

Purpose: example CephFS StorageClass targeting an erasure-coded CephFS data pool.
Important APIs/types/functions: `StorageClass` `rook-cephfs`, provisioner `rook-ceph.cephfs.csi.ceph.com`, `clusterID`, `fsName: myfs-ec`, `pool: myfs-ec-erasurecoded`, CSI secret parameters, expansion, reclaim policy, and optional mount debug flag.
Control flow: dynamic provisioning creates CephFS subvolumes in the named filesystem and pool; expansion requests route through controller expand secrets. Persistent state is CephFS subvolumes and Kubernetes PV/PVC objects. Dependencies are a `CephFilesystem` like `filesystem-ec.yaml`, Rook-generated CephFS CSI secrets, and an EC data pool with a replicated default pool. Risks: EC pools need enough OSDs, filesystem name must match the deployed CR, and using the same `rook-cephfs` name as the replicated class means only one can be installed at a time. Test signals: PVC binds, writes succeed, expansion works, and Ceph reports subvolume data in the EC pool.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/storageclass-ec.yaml -->
