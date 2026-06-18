<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/storageclass.yaml -->
# sources/control-plane/rook/deploy/examples/csi/nfs/storageclass.yaml

Purpose: dynamic provisioning StorageClass for Rook Ceph NFS exports.
Important APIs/types/functions: `StorageClass` `rook-nfs`, provisioner `rook-ceph.nfs.csi.ceph.com`, `nfsCluster`, `server`, `clusterID`, `fsName`, `pool`, CSI secret parameters, expansion, and optional debug mount option.
Control flow: PVC provisioning creates CephFS-backed NFS export resources against the named NFS cluster/server, then node publish mounts the NFS export. State persists in PV/PVC objects, CephFS subvolumes, NFS export metadata, and Ceph credentials. Dependencies are a `CephNFS` named `my-nfs`, service `rook-ceph-nfs-my-nfs-a`, filesystem `myfs`, pool `myfs-replicated`, and CephFS CSI secrets. Risks: hard-coded service/name coupling, NFS server availability, and secret namespace drift. Test signals: PVC Bound, export exists on the NFS cluster, pod mount succeeds, and expansion is reflected in PVC capacity.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/storageclass.yaml -->
