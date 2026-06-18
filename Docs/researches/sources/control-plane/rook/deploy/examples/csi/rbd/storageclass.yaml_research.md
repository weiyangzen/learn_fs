<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/storageclass.yaml -->
# sources/control-plane/rook/deploy/examples/csi/rbd/storageclass.yaml

Purpose: primary replicated RBD pool and StorageClass example.
Important APIs/types/functions: `CephBlockPool` `replicapool`, `failureDomain: host`, `replicated.size: 3`, `requireSafeReplicaSize: true`, StorageClass `rook-ceph-block`, RBD provisioner, image format/features, optional map/unmap/encryption/KMS/mounter settings, CSI secrets, `fstype: ext4`, expansion, and delete reclaim.
Control flow: Rook creates the replicated pool; PVC provisioning creates RBD images in `replicapool`; node publish maps and formats images for pods. State persists in Ceph pool/image data and Kubernetes PV/PVCs. Dependencies are a healthy multi-host Ceph cluster, RBD CSI sidecars/node plugin, and Rook-generated secrets. Risks: hard-coded namespace/secret names, older kernels require conservative image features, optional `rbd-nbd` is not recommended for production in comments, and delete reclaim removes images. Test signals: pool Ready, PVC Bound, pod mount works, expansion succeeds, and snapshot/clone examples pass.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/storageclass.yaml -->
