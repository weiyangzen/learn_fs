<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/pvc.yaml -->
# sources/control-plane/rook/deploy/examples/csi/nfs/pvc.yaml

Purpose: baseline PVC for the Rook NFS CSI examples.
Important APIs/types/functions: `PersistentVolumeClaim` `nfs-pvc`, access mode `ReadWriteOnce`, size `1Gi`, and `storageClassName: rook-nfs`.
Control flow: the NFS CSI provisioner creates or references a Ceph-backed NFS export and binds a PV to this claim. State persists in Kubernetes PV/PVC objects, CephFS backing storage, and NFS export metadata. Dependencies are the `rook-nfs` StorageClass, NFS CSI driver CR, and CephNFS service. Risks: RWO does not exercise multi-writer NFS semantics, backend export server must be reachable by nodes, and delete reclaim removes data. Test signals: PVC Bound, PV provisioner is `rook-ceph.nfs.csi.ceph.com`, and the NFS pod can mount it.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/pvc.yaml -->
