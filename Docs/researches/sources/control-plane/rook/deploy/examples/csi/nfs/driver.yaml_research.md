<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/driver.yaml -->
# sources/control-plane/rook/deploy/examples/csi/nfs/driver.yaml

Purpose: deploys the Rook-managed Ceph NFS CSI `Driver` custom resource.
Important APIs/types/functions: `csi.ceph.io/v1` `Driver`, name `rook-ceph.nfs.csi.ceph.com`, `fsGroupPolicy: File`, node plugin rolling update strategy, and controller plugin block.
Control flow: the Rook CSI operator reconciles this CR into controller and node plugin workloads for the NFS CSI driver. State is the driver CR and generated CSI Kubernetes resources. Dependencies are Rook CSI operator CRDs, namespace `rook-ceph`, and Ceph NFS support. Risks: the custom Driver API must be installed, driver name must match StorageClasses and snapshot classes, and empty controllerPlugin relies on defaults. Test signals: CSIDriver appears, controller/node pods become ready, and `storageclass.yaml` provisions an NFS PVC.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/driver.yaml -->
