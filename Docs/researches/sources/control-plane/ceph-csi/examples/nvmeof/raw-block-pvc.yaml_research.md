# sources/control-plane/ceph-csi/examples/nvmeof/raw-block-pvc.yaml

Purpose: example NVMe-oF raw block PVC.

Important fields and flow: PVC `raw-block-pvc` requests `1Gi`, `ReadWriteOnce`, `volumeMode: Block`, and StorageClass `csi-nvmeof-sc`.

State, dependencies, and integration: provisions a block volume for direct device publishing through NVMe-oF.

Risks and test signals: consumers must use `volumeDevices`, not filesystem mounts. Successful pod device access validates raw block support.
