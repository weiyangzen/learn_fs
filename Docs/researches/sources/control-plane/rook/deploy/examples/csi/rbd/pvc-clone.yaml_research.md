<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/pvc-clone.yaml -->
# sources/control-plane/rook/deploy/examples/csi/rbd/pvc-clone.yaml

Purpose: demonstrates RBD PVC cloning.
Important APIs/types/functions: `PersistentVolumeClaim` `rbd-pvc-clone`, `dataSource.kind: PersistentVolumeClaim`, source `rbd-pvc`, StorageClass `rook-ceph-block`, and RWO access mode.
Control flow: the CSI provisioner creates a new RBD image cloned from the source PVC image, usually through snapshot/clone mechanics provided by RBD. State persists as a new PVC/PV and RBD image. Dependencies are a bound source PVC, RBD CSI clone support, and image features such as `layering`. Risks: source and clone must be in the same namespace, clone support depends on StorageClass features, and clone chains may affect cleanup/performance. Test signals: clone PVC Bound, data equals source at clone time, and deleting source does not break clone.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/pvc-clone.yaml -->
