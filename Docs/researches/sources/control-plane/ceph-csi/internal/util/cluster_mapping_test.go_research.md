<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cluster_mapping_test.go -->
## sources/control-plane/ceph-csi/internal/util/cluster_mapping_test.go

**Purpose:** Validates cluster mapping JSON parsing, bidirectional cluster/pool/filesystem mapping lookup, simple ID mapping, and monitor resolution through mapped cluster IDs.

**Important APIs and functions:** `TestGetClusterMappingInfo` builds two mapping entries and checks file-missing, empty-data, unmatched, and site1/site2/site3 matching behavior. `validateMapping` checks cluster, RBD pool, and CephFS ID mappings. `TestGetMappedID` covers key, value, and no-match cases. `TestFetchMappedClusterIDAndMons` writes CSI and mapping configs and checks mapped/fallback monitor results.

**Control flow, state, and persistence:** Tests write temporary JSON files and also mutate the package-level `clusterMappingConfigFile` for exported `GetClusterMappingInfo`. Many subtests are parallel, while shared package variable mutation happens after the first table loop.

**Dependencies and integration points:** Uses JSON, temp files, string joining, reflection, and `api/deploy/kubernetes.ClusterInfo`. It exercises integration between mapping and `csiconfig.Mons`.

**Risks and test signals:** The tests give good signal for bidirectional mappings and fallback behavior. A residual risk is package-level `clusterMappingConfigFile` mutation in a parallel test process, which can interfere with other tests in the same package if they run concurrently. Random Go map iteration can also make first-success mapped target behavior difficult to assert for ambiguous config.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cluster_mapping_test.go -->
