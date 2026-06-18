# sources/control-plane/ceph-csi/examples/nfs/storageclass.yaml

Purpose: canonical NFS CSI StorageClass example backed by CephFS and a Ceph-managed NFS server.

Important fields and flow: StorageClass `csi-nfs-sc` uses provisioner `nfs.csi.ceph.com`, required `nfsCluster`, `server`, `clusterID`, and `fsName`, optional pool, secret refs for provision/expand/publish/modify, volume prefix `nfs-export-`, optional security types and client restrictions, `reclaimPolicy: Delete`, and expansion enabled.

State, dependencies, and integration: provisions CephFS subvolumes and NFS exports. It integrates with Rook CephNFS, CephFS secrets, and VolumeAttributesClass modification.

Risks and test signals: NFS server endpoint, CephFS config, and secrets must be valid. Export validation helpers inspect resulting Ceph NFS exports and client restrictions.
