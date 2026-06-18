<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/raw-block-pod.yaml -->
# sources/control-plane/rook/deploy/examples/csi/rbd/raw-block-pod.yaml

Purpose: demonstrates consuming an RBD PVC as a raw block device.
Important APIs/types/functions: `Pod` `csirbd-block-demo-pod`, `volumeDevices`, device path `/dev/xvda`, CentOS sleep container, and PVC `raw-block-rbd-pvc`.
Control flow: kubelet stages/maps the RBD image but passes it as a block device rather than formatting/mounting it; the container sees `/dev/xvda`. State persists in the raw-block PVC and RBD image; filesystem state is left to the workload. Dependencies are `raw-block-pvc.yaml`, RBD CSI block volume support, and privileged-enough container/device handling by kubelet. Risks: the device path can be overwritten by workload commands, no filesystem is created, and data interpretation is application-defined. Test signals: pod Running, `/dev/xvda` exists, block reads/writes work, and no mount is created.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/raw-block-pod.yaml -->
