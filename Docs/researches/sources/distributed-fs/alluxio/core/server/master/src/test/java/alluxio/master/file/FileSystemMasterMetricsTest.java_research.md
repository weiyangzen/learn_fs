<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterMetricsTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterMetricsTest.java

**Purpose:** Verifies filesystem master metric gauges for pinned files, total paths, and root UFS capacity.

**Important APIs/types/functions:** Uses `DefaultFileSystemMaster.Metrics.registerGauges`, `MetricsSystem.METRIC_REGISTRY`, `MetricKey.MASTER_FILES_PINNED`, `MASTER_TOTAL_PATHS`, `CLUSTER_ROOT_UFS_CAPACITY_TOTAL`, `CLUSTER_ROOT_UFS_CAPACITY_USED`, and `CLUSTER_ROOT_UFS_CAPACITY_FREE`.

**Control flow:** `before` clears all metrics, mocks `UfsManager` and `InodeTree`, and registers gauges. Individual tests mock `getPinnedSize`, `getInodeCount`, and root UFS `getSpace` return values, then read gauge values by metric name.

**State and persistence behavior:** Pure metric-registration test with no persistence. It validates gauges are live views into mocked dependencies rather than stored constants.

**Dependencies and integration points:** Integrates MetricsSystem, UFS manager resource acquisition, `CloseableResource<UnderFileSystem>`, and Alluxio configuration for the root UFS path.

**Risks:** Gauge names are exact and global registry state must be cleared to avoid test pollution. It does not cover exception behavior if UFS resource acquisition or space calls fail.

**Test signals:** Gauge values equal mocked inode and UFS values: 100 pinned files, 90 total paths, and 1000/200/800 UFS total/used/free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterMetricsTest.java -->
