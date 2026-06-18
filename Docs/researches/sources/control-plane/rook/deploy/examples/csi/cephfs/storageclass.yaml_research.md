<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/storageclass.yaml -->
# sources/control-plane/rook/deploy/examples/csi/cephfs/storageclass.yaml

Purpose: primary CephFS dynamic provisioning StorageClass for replicated filesystem examples.
Important APIs/types/functions: `StorageClass` `rook-cephfs`, `clusterID: rook-ceph`, `fsName: myfs`, `pool: myfs-replicated`, provisioner/controller-publish/node-stage secrets, optional encryption and mounter parameters, `allowVolumeExpansion`, and `mountOptions`.
Control flow: PVC creation calls the CephFS CSI provisioner to create a subvolume in `myfs`; node staging mounts it with kernel client or ceph-fuse; expansion uses controller expand credentials. State persists in Kubernetes PV/PVCs, CephFS subvolumes, and optional KMS if encryption is enabled. Dependencies are `filesystem.yaml`, Rook CSI secrets, CephFS CSI sidecars, and Kubernetes StorageClass support. Risks: secret namespace coupling, optional encrypted volumes require KMS config, mounter choice affects node prerequisites, and delete reclaim policy removes backend data. Test signals: sample PVC binds, pod can mount/write, expansion changes capacity, and CSI logs show expected filesystem/pool.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/storageclass.yaml -->
