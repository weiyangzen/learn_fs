<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nvmeof/driver.yaml -->
# sources/control-plane/rook/deploy/examples/csi/nvmeof/driver.yaml

Purpose: declares the NVMe-oF CSI driver managed by the Rook CSI operator.
Important APIs/types/functions: `csi.ceph.io/v1` `Driver`, name `rook-ceph.nvmeof.csi.ceph.com`, namespace `rook-ceph`, and `controllerPlugin.hostNetwork: false`.
Control flow: the CSI operator reconciles this CR into NVMe-oF controller and node plugin resources. State is Kubernetes Driver CR plus generated CSI workloads. Dependencies are Rook CSI operator support for NVMe-oF and matching StorageClass provisioner name. Risks: NVMe-oF CSI is more environment-sensitive than filesystem examples, and host networking choice must match gateway reachability. Test signals: CSIDriver and pods are ready, sidecars register the provisioner, and `pvc.yaml` provisions via `storageclass.yaml`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nvmeof/driver.yaml -->
