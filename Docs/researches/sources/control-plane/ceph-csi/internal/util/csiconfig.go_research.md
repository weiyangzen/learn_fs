<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/csiconfig.go -->
## sources/control-plane/ceph-csi/internal/util/csiconfig.go

**Purpose:** Reads `/etc/ceph-csi-config/config.json` and exposes typed helper accessors for monitors, namespaces, read affinity, network namespaces, mirror daemon counts, mount options, cluster IDs, and secret references.

**Important APIs and functions:** `readClusterInfo` loads JSON into `api/deploy/kubernetes.ClusterInfo` and finds a cluster ID. Accessors include `Mons`, `GetRBDRadosNamespace`, `GetCephFSRadosNamespace`, `GetRBDMirrorDaemonCount`, `CephFSSubvolumeGroup`, `GetMonsAndClusterID`, `GetClusterID`, network namespace getters, `GetCrushLocationLabels`, `GetCephFSMountOptions`, `GetRBDControllerPublishSecretRef`, `GetCephFSControllerPublishSecretRef`, and `GetRBDNodePublishSecretRef`.

**Control flow, state, and persistence:** The file is read on each call; no cache is kept. `readClusterInfo` returns `ErrConfigNotFound` when a cluster ID is absent. Some accessors provide backward-compatible defaults: CephFS subvolume group `csi`, CephFS RADOS namespace `csi`, and RBD mirror daemon count `1`. `GetMonsAndClusterID` optionally routes through cluster mapping before monitor lookup.

**Dependencies and integration points:** Depends on filesystem JSON, deployment API schema, and cluster mapping. It is a central integration point for controller/node configuration, multi-cluster support, read affinity, CephFS/RBD/NFS net namespaces, and secret reference lookup.

**Risks and test signals:** Re-reading config keeps behavior fresh but repeats IO and parsing. Error messages include raw malformed JSON buffers. Monitor lists must be non-empty. Tests cover malformed configs, monitor extraction, net namespace accessors, read-affinity labels, mount options, mirror daemon defaults/type errors, and controller publish secret references.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/csiconfig.go -->
