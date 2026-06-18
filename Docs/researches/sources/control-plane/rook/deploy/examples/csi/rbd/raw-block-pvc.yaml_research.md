<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/raw-block-pvc.yaml -->
# sources/control-plane/rook/deploy/examples/csi/rbd/raw-block-pvc.yaml

Purpose: provisions an RBD volume in Kubernetes raw block mode.
Important APIs/types/functions: `PersistentVolumeClaim` `raw-block-rbd-pvc`, `volumeMode: Block`, RWO access mode, `1Gi` request, and StorageClass `rook-ceph-block`.
Control flow: RBD CSI creates an image and binds it as a block PV; node publish maps it directly into pods via `volumeDevices`. State persists in PV/PVC metadata and the RBD image. Dependencies are RBD CSI support for `volumeMode: Block` and the referenced StorageClass/pool. Risks: workloads must handle partitioning/filesystem/application data safely, and the example does not include a filesystem check. Test signals: PVC Bound with block volume mode, raw-block pod sees a device, and writes persist after pod restart.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/raw-block-pvc.yaml -->
