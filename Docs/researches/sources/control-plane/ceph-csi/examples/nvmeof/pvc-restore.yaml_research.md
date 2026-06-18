# sources/control-plane/ceph-csi/examples/nvmeof/pvc-restore.yaml

Purpose: example NVMe-oF PVC restored from a snapshot.

Important fields and flow: PVC `nvme-pvc-restore` uses StorageClass `csi-nvmeof-sc`, snapshot data source `nvme-pvc-snapshot`, `ReadWriteOnce`, and `1Gi`.

State, dependencies, and integration: provisions a new NVMe-oF volume backed by an RBD snapshot restore.

Risks and test signals: restored size must be compatible with source snapshot and gateway config must be valid. Binding/pod access validate restore.
