<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nvmeof/pvc.yaml -->
# sources/control-plane/rook/deploy/examples/csi/nvmeof/pvc.yaml

Purpose: baseline PVC for the NVMe-oF CSI StorageClass.
Important APIs/types/functions: `PersistentVolumeClaim` `nvmeof-external-volume`, namespace `default`, StorageClass `ceph-nvmeof`, RWO access mode, and `128Mi` request.
Control flow: the external provisioner allocates an RBD image in the configured pool and exposes it through the NVMe-oF gateway/subsystem. State persists in PVC/PV objects, Ceph RBD image metadata, and gateway namespace/subsystem configuration. Dependencies are `storageclass.yaml`, `nvmeof-pool.yaml`, Rook NVMe-oF gateway, and RBD CSI secrets. Risks: small test size may not cover production alignment, gateway provisioning must succeed, and namespace defaults differ from Rook namespace. Test signals: PVC Bound, PV references NVMe-oF CSI driver, and the test pod can mount it.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nvmeof/pvc.yaml -->
