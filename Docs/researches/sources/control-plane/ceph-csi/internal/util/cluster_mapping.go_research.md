<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cluster_mapping.go -->
## sources/control-plane/ceph-csi/internal/util/cluster_mapping.go

**Purpose:** Reads failover/failback cluster mapping configuration and resolves alternate cluster IDs and monitor lists when a CSI object created in one cluster is handled in another.

**Important APIs and types:** `ClusterMappingInfo` holds cluster ID mappings plus RBD pool ID and CephFS filesystem ID mappings. `readClusterMappingInfo` loads JSON. `getClusterMappingInfo` filters mapping entries that mention the requested ID as key or value. `GetMappedID` returns the opposite side of a mapping pair. `fetchMappedClusterIDAndMons` and exported `FetchMappedClusterIDAndMons` combine mapping lookup with CSI config monitor lookup.

**Control flow, state, and persistence:** Mapping is read from `/etc/ceph-csi-config/cluster-mapping.json` or a supplied test path on every call. Missing mapping files are treated as non-errors to preserve non-failover behavior. When mappings exist, the resolver tries mapped IDs first and skips ones whose monitors are not in CSI config, then falls back to the original cluster ID.

**Dependencies and integration points:** Depends on JSON, filesystem reads, internal logging, and `Mons` from CSI config. It integrates with restore/failover paths that parse cluster IDs from CSI handles and need local monitor endpoints.

**Risks and test signals:** Ambiguous mappings are possible because map iteration order is randomized and multiple entries can map a cluster to different targets. Raw invalid JSON content is included in errors, which helps debugging but can be noisy. Tests cover missing files, no mapping, bidirectional mapping counts, mapped ID helper, mapped monitor resolution, and fallback/error behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cluster_mapping.go -->
