# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeAdminMonitorInterface.java

## Purpose

`DatanodeAdminMonitorInterface` defines the pluggable contract for NameNode datanode decommission and maintenance monitors. `DatanodeAdminManager` instantiates implementations reflectively and schedules them as background `Runnable`s.

## Important APIs and Types

The interface extends `Runnable`. It exposes lifecycle methods `startTrackingNode(DatanodeDescriptor)` and `stopTrackingNode(DatanodeDescriptor)`, metrics/accessors `getPendingNodeCount()`, `getTrackedNodeCount()`, `getNumNodesChecked()`, `getPendingNodes()`, and `getCancelledNodes()`, dependency setters for `BlockManager`, `DatanodeAdminManager`, and `Namesystem`, plus tuning accessors for pending replication limits and blocks-per-lock.

## Control Flow

The manager creates the monitor class, calls the dependency setters, and schedules `run()` repeatedly. Admin operations enqueue nodes through `startTrackingNode()` and cancel through `stopTrackingNode()`. The concrete monitor owns how pending/cancelled queues become active checks and how it reports progress.

## State and Persistence Behavior

The interface itself is stateless. Implementations are expected to keep runtime-only queues and counters. The authoritative admin state remains on `DatanodeDescriptor` and host configuration.

## Dependencies and Integration Points

It couples monitor implementations to `BlockManager`, `DatanodeAdminManager`, and `Namesystem` without requiring a specific class. The default implementation also implements Hadoop `Configurable` through `DatanodeAdminMonitorBase`, but the interface does not require that directly.

## Risks and Edge Cases

Because implementations are configurable, compatibility risk is in semantic expectations rather than type signatures: `stopTrackingNode()` must handle cancellation, `run()` must respect NameNode locking and liveness, and tuning setters should validate or no-op consistently. The default monitor returns zero/no-op for tuning knobs it does not support.

## Test Signals

Coverage comes indirectly from monitor instantiation tests, `DatanodeAdminManager` activation paths, `TestDatanodeAdminMonitorBase`, and decommission/maintenance integration suites that exercise the interface through the default implementation.
