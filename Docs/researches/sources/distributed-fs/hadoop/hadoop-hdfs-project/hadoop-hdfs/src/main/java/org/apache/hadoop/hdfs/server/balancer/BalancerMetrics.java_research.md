# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/BalancerMetrics.java

## Purpose
`BalancerMetrics` registers per-balancer Hadoop metrics for iteration activity, bytes left, bytes moved, and counts of over/under-utilized nodes.

## Important APIs and types
The class is annotated with `@Metrics(context="dfs")`. It exposes a tag-like metric `getBlockPoolID()`, gauge-backed setters for iterate-running, bytes-left, under-utilized node count, and over-utilized node count, and a computed metric `getBytesMovedInCurrentRun()`.

## Control flow
`create` registers a new metrics source with `DefaultMetricsSystem` under a name derived from the block pool ID. `Balancer` updates the gauges during initialization and `runOneIteration`, and removes the source name during `resetData`.

## State and persistence
Runtime state is the `Balancer` reference and mutable gauge objects supplied by the metrics system. It persists nothing.

## Dependencies and integration points
It integrates with Hadoop metrics2 annotations, `DefaultMetricsSystem`, `MutableGaugeInt`, `MutableGaugeLong`, `Balancer`, and `NameNodeConnector` counters.

## Risks and edge cases
Metrics source names include block pool ID; duplicate registration without cleanup can fail or overwrite depending on metrics system behavior. The bytes moved metric reads from the connector live, so it reflects current run counters rather than a latched gauge.

## Test signals
Tests should cover source registration names, gauge updates, block-pool tag value, bytes-moved computation, and cleanup when balancer iteration resets.
