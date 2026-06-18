<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/pvc.yaml -->
# sources/control-plane/rook/deploy/examples/csi/rbd/pvc.yaml

Purpose: baseline RBD block-backed filesystem PVC.
Important APIs/types/functions: `PersistentVolumeClaim` `rbd-pvc`, RWO access mode, `1Gi` request, and StorageClass `rook-ceph-block`.
Control flow: RBD CSI creates an image in the configured pool and binds it as a filesystem volume for pods. State persists in Kubernetes PV/PVC objects and Ceph RBD image metadata/data. Dependencies are the RBD StorageClass, Rook CSI secrets, and a healthy CephBlockPool. Risks: delete reclaim policy from the StorageClass removes image data, RWO limits scheduling, and missing image features can break clone/snapshot examples. Test signals: PVC Bound, PV provisioner `rook-ceph.rbd.csi.ceph.com`, and pod mount/write succeeds.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/pvc.yaml -->
