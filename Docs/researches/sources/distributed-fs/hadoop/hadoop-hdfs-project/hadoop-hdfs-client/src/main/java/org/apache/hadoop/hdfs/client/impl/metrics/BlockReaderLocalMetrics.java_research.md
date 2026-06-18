# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/metrics/BlockReaderLocalMetrics.java

## Purpose
`BlockReaderLocalMetrics` registers and maintains rolling average latency metrics for short-circuit local reads.

## Important APIs, types, and functions
`create()` obtains the default Hadoop `MetricsSystem`, constructs a metrics instance, and registers it under `HdfsShortCircuitReads`. `addShortCircuitReadLatency(long)` adds a sample to `MutableRollingAverages` with value name `ShortCircuitLocalReads`. `collectThreadLocalStates()` flushes thread-local metric state. `getShortCircuitReadRollingAverages()` exposes the metric for tests.

## Control flow
The class relies on Hadoop metrics annotations to initialize and export `shortCircuitReadRollingAverages`. Callers add samples as reads complete; metrics system collection later publishes rolling averages.

## State and persistence behavior
State is the mutable rolling-average metric object registered with the process metrics system. No files are written.

## Dependencies and integration points
It depends on Hadoop Metrics2 annotations, `DefaultMetricsSystem`, `MetricsSystem`, and `MutableRollingAverages`. `BlockReaderIoProvider` records into this class.

## Risks and test signals
Tests should verify metric registration name, value name, latency sample accumulation, thread-local collection, and behavior if `create()` is called multiple times in the same metrics system. Operationally, metric cardinality is low, but registration conflicts can be a risk in repeated unit-test setup.
