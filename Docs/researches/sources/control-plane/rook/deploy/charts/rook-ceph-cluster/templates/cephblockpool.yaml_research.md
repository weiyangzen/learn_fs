## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephblockpool.yaml

Purpose: renders CephBlockPool CRs and optional RBD StorageClasses from `.Values.cephBlockPools`.

Important template behavior: iterates each block pool, emits `ceph.rook.io/v1` `CephBlockPool` in the release namespace with raw `.spec`, then emits a `storage.k8s.io/v1` StorageClass when `storageClass.enabled` is true. The StorageClass includes labels/annotations, default-class annotation, RBD CSI provisioner derived from `csiDriverNamePrefix` or `operatorNamespace`, pool and clusterID parameters, user-supplied parameters rendered through `tpl`, reclaim policy, expansion, binding mode, mount options, and allowed topologies.

Control flow: value-driven range with conditionals for optional StorageClass and nested fields.

State and persistence: creates Ceph pools through Rook operator reconciliation and creates cluster-scoped StorageClasses. StorageClass defaults can affect all future PVCs.

Dependencies and integration points: depends on Rook CephBlockPool CRD, CSI RBD driver naming, secrets configured in values parameters, and operator namespace convention. Risks: `tpl` allows values to reference Helm context, useful but capable of rendering invalid/surprising parameters; setting `isDefault` can change cluster-wide storage behavior; mismatched driver names break provisioning. Helm render tests should cover prefix/operator namespace variants.
