# sources/control-plane/ceph-csi/examples/nvmeof/storageclass.yaml

Purpose: canonical NVMe-oF StorageClass example for Ceph-CSI.

Important fields and flow: StorageClass `csi-nvmeof-sc` enables expansion, uses `Immediate` binding, provisioner `nvmeof.csi.ceph.com`, secret refs for expand/stage/publish/provision, RBD parameters (`clusterID`, `fstype`, `imageFeatures`, `pool`), subsystem NQN, gateway management address/port, and JSON listener definitions for NVMe data path.

State, dependencies, and integration: provisions RBD images and exposes them through an NVMe-oF gateway/subsystem. PVC and snapshot examples depend on this configuration.

Risks and test signals: gateway IP, listener JSON, pool, NQN, and secrets must match the environment. Successful PVC binding and pod mount/device access validate gateway and CSI integration.
