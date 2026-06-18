<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nvmeof/storageclass.yaml -->
# sources/control-plane/rook/deploy/examples/csi/nvmeof/storageclass.yaml

Purpose: StorageClass for provisioning RBD-backed volumes exposed through Ceph NVMe-oF.
Important APIs/types/functions: `StorageClass` `ceph-nvmeof`, provisioner `rook-ceph.nvmeof.csi.ceph.com`, `clusterID`, pool `nvmeof`, `subsystemNQN`, management gateway address/port, JSON `listeners`, RBD CSI secret parameters, image format/features, `Immediate` binding, and expansion.
Control flow: PVC creation allocates an RBD image, configures NVMe-oF gateway namespace/subsystem via the management API, and node staging connects workers to listed gateway listeners. State persists in PV/PVCs, RBD images, and NVMe-oF gateway configuration. Dependencies are gateway service DNS, SPDK/NVMe-oF subsystem naming, RBD provisioner/node secrets, and the `nvmeof` pool. Risks: single listener is not HA despite comments, NQN/address are hard-coded, feature set must be kernel/client compatible, and gateway API port reachability is required. Test signals: PVC Bound, gateway reports namespace, node connects to listener, expansion works.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nvmeof/storageclass.yaml -->
