<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/pod.yaml -->
# sources/control-plane/rook/deploy/examples/csi/rbd/pod.yaml

Purpose: validates the standard RBD PVC by mounting it into nginx.
Important APIs/types/functions: `Pod` `csirbd-demo-pod`, PVC `rbd-pvc`, and mount path `/var/lib/www/html`.
Control flow: kubelet stages/maps the RBD image, formats if needed, mounts it, and publishes it to the container path. State persists in the referenced PVC/PV and RBD image. Dependencies are `pvc.yaml`, `storageclass.yaml`, RBD CSI node plugin, and Ceph credentials. Risks: RBD RWO volumes cannot be mounted read-write by multiple nodes, sample lacks probes, and node kernel/nbd mapping failures surface as pod mount errors. Test signals: pod Ready, mount writable, data persists after pod recreation, and RBD image appears in the configured pool.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/pod.yaml -->
