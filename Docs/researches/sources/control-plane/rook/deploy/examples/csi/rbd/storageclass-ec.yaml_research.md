<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/storageclass-ec.yaml -->
# sources/control-plane/rook/deploy/examples/csi/rbd/storageclass-ec.yaml

Purpose: production-style RBD StorageClass using an erasure-coded data pool with a replicated metadata pool.
Important APIs/types/functions: `CephBlockPool` `replicated-metadata-pool`, `CephBlockPool` `ec-data-pool`, `StorageClass` `rook-ceph-block`, RBD provisioner, `dataPool`, `pool`, image format/features, CSI secret parameters, filesystem type, expansion, and delete reclaim.
Control flow: Rook creates the pools; PVC provisioning creates RBD images whose metadata resides in the replicated pool and data in the EC pool. State persists in Ceph pools, RBD image metadata/data, and PV/PVC objects. Dependencies are at least three OSD failure domains, RBD CSI, and Rook secrets. Risks: EC pool requirements, metadata pool replica size 2 may be less durable than default production patterns, image features are conservative `layering`, and same StorageClass name conflicts with non-EC examples. Test signals: pools Ready, PVC Bound, data objects land in EC pool, snapshots/clones still work.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/storageclass-ec.yaml -->
