# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeStatistics.java

## Purpose

`DatanodeStatistics` is the interface exposing aggregate datanode capacity, cache, load, liveness, and storage-tier statistics to NameNode block-management users. `HeartbeatManager` implements it by delegating to `DatanodeStats`.

## Important APIs and Types

The interface provides totals for capacity, DFS used, non-DFS used, remaining space, block-pool used space, cache capacity/usage, xceiver load, in-service xceiver and volume counts, number of in-service datanodes, expired heartbeats, storage-type stats, provided capacity, and a `ClientProtocol#getStats()` compatible `long[]`.

## Control Flow

Consumers obtain an instance through `DatanodeManager.getDatanodeStatistics()`, which returns `HeartbeatManager`. Heartbeat updates mutate `DatanodeStats`; callers read through this interface for reports, metrics, block placement, and client protocol responses.

## State and Persistence Behavior

The interface is stateless. Implementations expose runtime aggregate state derived from live datanode registrations and heartbeats. No values are persisted by the interface.

## Dependencies and Integration Points

It references `StorageType`, `StorageTypeStats`, and `ClientProtocol`. It is the stable boundary between heartbeat/stat aggregation and NameNode consumers such as metrics, reports, and placement policies.

## Risks and Edge Cases

The contract distinguishes total cluster capacity from in-service-only load. Implementations must keep decommissioning, decommissioned, and maintenance states consistent with caller expectations, especially because block placement should not treat out-of-service capacity as writable.

## Test Signals

Capacity and metrics tests such as `TestNamenodeCapacityReport`, `TestBlockStatsMXBean`, `TestNameNodeMetrics`, and `TestHeartbeatHandling` indirectly validate this interface. Tests should confirm percent calculations with zero capacity and correct inclusion/exclusion of decommissioning or maintenance nodes.
