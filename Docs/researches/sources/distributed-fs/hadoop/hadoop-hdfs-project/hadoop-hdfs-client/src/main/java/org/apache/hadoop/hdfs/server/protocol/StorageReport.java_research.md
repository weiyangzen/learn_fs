# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/StorageReport.java

Purpose: `StorageReport` is a per-storage utilization report containing a `DatanodeStorage`, failure flag, capacity, DFS/non-DFS usage, remaining bytes, block-pool usage, block-pool usage percentage, and mount path.

Important APIs/types/functions: constructors support optional mount. `EMPTY_ARRAY` provides a no-report sentinel. Getters expose all fields; `getRemaining()` clamps negative values to zero. `blockPoolUsagePercent` is computed at construction as zero for non-positive capacity or `bpUsed * 100 / capacity`.

Control flow: DataNodes create reports for each storage and NameNodes aggregate them in `DatanodeStorageReport` and cluster metrics.

State and persistence behavior: immutable final fields. No local persistence.

Dependencies and integration points: depends on `DatanodeStorage`. Integrates with DataNode storage reporting, capacity accounting, balancer/admin UIs, and storage policy logic.

Risks and test signals: values are accepted as supplied, so inconsistent capacity/used/remaining can propagate. The clamped remaining getter hides negative raw values from consumers. Tests should cover percentage calculation, zero/negative capacity, negative remaining clamp, mount propagation, and failed storage reports.
