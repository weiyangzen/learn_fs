# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/StateStoreMBean.java

Purpose: `StateStoreMBean` is the JMX contract for State Store operation metrics.

Important APIs: it exposes operation counts and average latencies for reads, writes, failures, and removes: `getReadOps`, `getReadAvg`, `getWriteOps`, `getWriteAvg`, `getFailureOps`, `getFailureAvg`, `getRemoveOps`, and `getRemoveAvg`.

Control flow and state: this is a stateless interface. `StateStoreMetrics` implements the methods by reading Metrics2 `MutableRate` snapshots.

Dependencies and integration points: Hadoop private/evolving annotations mark the management contract. State store drivers and monitoring code indirectly depend on these names.

Risks: these methods expose last Metrics2 interval stats rather than lifetime totals, because the implementation calls `lastStat`. Consumers must understand the rolling-window semantics.

Test signals: validate that `StateStoreMetrics` updates operation rates and that JMX getters reflect samples after read/write/remove/failure increments.
