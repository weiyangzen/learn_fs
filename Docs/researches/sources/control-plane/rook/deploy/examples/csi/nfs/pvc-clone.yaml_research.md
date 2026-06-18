<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/pvc-clone.yaml -->
# sources/control-plane/rook/deploy/examples/csi/nfs/pvc-clone.yaml

Purpose: demonstrates cloning an NFS CSI PVC.
Important APIs/types/functions: `PersistentVolumeClaim` `nfs-pvc-clone`, `dataSource.kind: PersistentVolumeClaim`, source `nfs-pvc`, StorageClass `rook-nfs`, and RWX access mode.
Control flow: Kubernetes invokes CSI clone support through the NFS driver to create a new exported volume initialized from `nfs-pvc`. State persists as a new PV/PVC and underlying CephFS/NFS export resources. Dependencies are a bound source PVC, CSI clone support in the NFS driver path, and compatible requested size/access mode. Risks: clone support depends on backend CephFS behavior, source namespace must match, and access mode differs from the base example. Test signals: cloned PVC Bound, data copied from source, and source/clone mutations are independent.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/pvc-clone.yaml -->
