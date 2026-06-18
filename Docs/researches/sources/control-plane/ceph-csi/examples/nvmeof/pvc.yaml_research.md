# sources/control-plane/ceph-csi/examples/nvmeof/pvc.yaml

Purpose: baseline NVMe-oF filesystem PVC example.

Important fields and flow: PVC `nvmeof-pvc` requests `64Mi`, `ReadWriteOnce`, and StorageClass `csi-nvmeof-sc`.

State, dependencies, and integration: creates an RBD-backed NVMe-oF volume through the NVMe-oF CSI provisioner.

Risks and test signals: small size is suitable for examples but may not match all filesystem requirements. Bound status and pod mount validate provisioning.
