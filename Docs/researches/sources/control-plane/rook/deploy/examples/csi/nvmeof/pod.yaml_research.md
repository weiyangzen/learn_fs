<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nvmeof/pod.yaml -->
# sources/control-plane/rook/deploy/examples/csi/nvmeof/pod.yaml

Purpose: test pod for mounting an NVMe-oF CSI PVC and periodically reporting filesystem usage.
Important APIs/types/functions: `Pod` `nvmeof-test-pod`, `busybox`, shell loop, `df -h /mnt/nvmeof`, PVC `nvmeof-external-volume`, and `restartPolicy: Never`.
Control flow: kubelet stages the NVMe-oF volume, mounts it at `/mnt/nvmeof`, and the container loops every 45 seconds printing mount status. Persistent state is the referenced PVC/PV and RBD/NVMe-oF backend image; pod state is transient. Dependencies are a bound `nvmeof-external-volume`, NVMe-oF node connectivity, and the StorageClass gateway configuration. Risks: `restartPolicy: Never` does not self-heal, busybox command only checks mount visibility, and gateway/listener DNS must be reachable. Test signals: pod Running, `df` output includes the mounted volume, and pod logs continue without I/O errors.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nvmeof/pod.yaml -->
