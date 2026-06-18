<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/pod.yaml -->
# sources/control-plane/rook/deploy/examples/csi/nfs/pod.yaml

Purpose: validates an NFS CSI PVC by mounting it into an nginx pod.
Important APIs/types/functions: `Pod` `csinfs-demo-pod`, `persistentVolumeClaim.claimName: nfs-pvc`, and mount path `/var/lib/www/html`.
Control flow: kubelet stages/publishes the NFS CSI volume from the bound PVC into the container. Persistent state is in the referenced PVC/PV and backend CephFS export managed by the NFS CSI driver. Dependencies are `pvc.yaml`, `storageclass.yaml`, the NFS CSI node plugin, and an active CephNFS server. Risks: sample PVC requests RWO although NFS can support shared access, and no readiness probe verifies filesystem writes. Test signals: pod Ready, mount is NFS-backed, writes under the mount persist across pod recreation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/pod.yaml -->
