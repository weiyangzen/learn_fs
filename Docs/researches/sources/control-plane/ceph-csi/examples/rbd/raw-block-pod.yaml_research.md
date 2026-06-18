## sources/control-plane/ceph-csi/examples/rbd/raw-block-pod.yaml

Purpose: Example Pod consuming the standard RBD raw block PVC.

Important API surface: Pod `pod-with-raw-block-volume`, CentOS container, `volumeDevices` device path `/dev/xvda`, and PVC `raw-block-pvc`.

Control flow and state: The RBD node plugin maps the PVC's RBD image and exposes it as a block device. Kubernetes does not mount a filesystem because the PVC uses `volumeMode: Block`.

Dependencies and risks: Requires `raw-block-pvc.yaml` and CSI block mode support. Applications must format or use the block device directly. Test by running block-level commands inside the container and verifying persistence across Pod restarts.
