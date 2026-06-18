<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/pod.yaml -->
# sources/control-plane/rook/deploy/examples/csi/cephfs/pod.yaml

Purpose: mounts the example CephFS PVC into an nginx pod to validate filesystem-backed workload access.
Important APIs/types/functions: `Pod` `csicephfs-demo-pod`, container `nginx`, `persistentVolumeClaim.claimName: cephfs-pvc`, and mount path `/var/lib/www/html`.
Control flow: the scheduler places the pod, kubelet asks CephFS CSI to stage/publish the already-bound PVC, and nginx sees the mounted directory. Persistent state is the referenced PVC/PV and CephFS subvolume; the pod itself is disposable. Dependencies are `pvc.yaml`, `storageclass.yaml`, CephFS CSI node plugin, and Rook secrets. Risks: pod fails if the PVC is not bound or access mode conflicts with the StorageClass, and the sample has no readiness probe. Test signals: pod Ready, `mount` shows CephFS/fuse or kernel client, writing under the mount survives pod recreation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/pod.yaml -->
