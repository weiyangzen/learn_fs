# sources/control-plane/ceph-csi/examples/cephfs/storageclass.yaml

Purpose: canonical CephFS StorageClass example for dynamic provisioning.

Important fields and flow: StorageClass `csi-cephfs-sc` uses provisioner `cephfs.csi.ceph.com`, placeholder `clusterID` and `fsName`, optional data pool, mount options, mounter, volume name prefix, backing snapshot and encryption settings, KMS ID, secret refs for provisioning/expand/publish/stage, `reclaimPolicy: Delete`, and `allowVolumeExpansion: true`.

State, dependencies, and integration: drives dynamic CephFS subvolume provisioning and expansion. Referenced by all CephFS PVC examples and many e2e helpers that inject real cluster details.

Risks and test signals: invalid cluster/filesystem/secret values prevent provisioning. Optional encryption and KMS settings require matching config. Bound PVCs, expansion success, and pod mounts validate this class.
