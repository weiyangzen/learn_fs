## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephecblockpool.yaml

Purpose: renders erasure-coded block pool support from `.Values.cephECBlockPools`, including data and metadata pools plus optional RBD StorageClass.

Important template behavior: for each entry it creates a data `CephBlockPool` named `<name>` and replicated metadata pool named `<name>-metadata`, rendering `spec.dataPool` and `spec.metadataPool`. When storageClass is enabled, it creates an RBD StorageClass with provisioner from `csiDriverNamePrefix` or `operatorNamespace`, clusterID, metadata pool, dataPool, image settings, fixed RBD CSI secret references, ext4 fstype, expansion, and reclaim policy.

Control flow: range over values; StorageClass conditional. Unlike the normal blockpool template, many CSI parameters are hard-coded instead of arbitrary `tpl` parameters.

State and persistence: creates Ceph pools and cluster-scoped StorageClass. Erasure-coded pools affect durability/performance tradeoffs and require correct metadata pool setup.

Dependencies and integration points: depends on Rook CephBlockPool CRD and RBD CSI driver. Risks: clusterID in values can drift from release namespace; incorrect EC parameters or metadata pool settings can create unusable or unsafe storage; hard-coded secret names assume standard Rook CSI secret generation. Default values keep this disabled/commented, so render coverage may be weaker unless explicitly tested.
