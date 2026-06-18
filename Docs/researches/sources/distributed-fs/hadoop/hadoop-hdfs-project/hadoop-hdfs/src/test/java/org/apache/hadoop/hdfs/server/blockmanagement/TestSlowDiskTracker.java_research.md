# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestSlowDiskTracker.java

## Purpose
`TestSlowDiskTracker` validates NameNode aggregation, expiration, ranking, and JSON serialization of DataNode slow disk reports. It also verifies the DataNode heartbeat path from disk metrics to the NameNode tracker.

## Important APIs, types, and functions
The primary type is `SlowDiskTracker`, especially `addSlowDiskReport`, `updateSlowDiskReportAsync`, `getSlowDisksReport`, `getSlowDiskReportAsJsonString`, `setReportValidityMs`, and nested `DiskLatency`. It uses `SlowDiskReports`, `SlowDiskReports.DiskOp`, `FakeTimer`, Jackson `ObjectReader`, `MiniDFSCluster`, `DataNode.getDiskMetrics().addSlowDiskForTesting`, `DatanodeManager.getSlowDiskTracker`, and `GenericTestUtils.waitFor`.

## Control flow
`testDataNodeHeartbeatSlowDiskReport` starts two DataNodes, injects slow disk metrics into each, waits for heartbeat/report propagation, validates four aggregated disk IDs and operation latencies, then deserializes JSON and checks the same contents. Unit-style tests add synthetic reports directly to the tracker, call `updateSlowDiskReportAsync`, and verify empty reports, retrieval, total expiration, partial expiration, and replacement of expired reports. `testGetJson` checks JSON includes all active reports. `testGetJsonSizeIsLimited` adds eight reports and verifies only the top five latencies are serialized. `testEmptyReport` verifies expired-only state yields null JSON. `testRemoveInvalidReport` uses a MiniDFSCluster tracker with short validity and waits until invalid reports are removed.

## State and persistence behavior
State is in-memory per-DataNode/per-disk latency reports with timestamps, async generated report snapshots, JSON cache, and validity windows. `FakeTimer` controls unit tests, while MiniDFSCluster tests use wall-clock sleeps. No persistent storage is involved.

## Dependencies and integration points
This file bridges DataNode disk metrics, heartbeat reporting, DatanodeManager aggregation, and NameNode JSON reporting. It depends on configuration keys for heartbeat interval, DataNode file IO profiling sampling percentage, and outlier report interval.

## Risks and test signals
Signals include exact report map size, disk ID keys in the `dn:disk` form, per-operation floating-point latencies, JSON deserialization size, top-five ranking, and null JSON for empty active state. Risks are async update timing and wall-clock sleeps. The tests catch regressions in report expiry, stale replacement, JSON limits, and heartbeat integration.
