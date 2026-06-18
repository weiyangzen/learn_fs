<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/storageclass-test.yaml -->
# sources/control-plane/rook/deploy/examples/csi/rbd/storageclass-test.yaml

Purpose: low-redundancy RBD StorageClass for test clusters with a single OSD.
Important APIs/types/functions: `CephBlockPool` `replicapool`, `failureDomain: osd`, `replicated.size: 1`, `requireSafeReplicaSize: false`, StorageClass `rook-ceph-block`, RBD CSI secret parameters, `imageFeatures: layering`, and expansion.
Control flow: Rook creates a single-replica pool; RBD CSI provisions images there for PVCs. State persists in a deliberately unsafe Ceph pool and Kubernetes PV/PVCs. Dependencies are Rook CephCluster, RBD CSI, and `rook-ceph` secrets. Risks: explicit data-loss risk with replica 1, not production-safe, and same StorageClass name as production examples can overwrite intent. Test signals: pool Ready on one OSD, PVC binds, pod mounts, and tests avoid using it for durable data.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/storageclass-test.yaml -->
