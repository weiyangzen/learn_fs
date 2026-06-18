# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/metrics/DataNodeMetrics.java

## Purpose

`DataNodeMetrics` is the main Hadoop metrics2 source for DataNode activity. It owns counters, gauges, rates, quantiles, and usage-report helpers for block IO, client locality, RPCs to NameNodes, RAM disk activity, erasure coding, xceiver counts, packet latency, dataset lock timing, and local dataset operations.

## Important APIs, Control Flow, and State

The constructor tags the registry with the session id, creates `DataNodeUsageReportUtil`, and creates interval-specific quantile arrays for packet ACK RTT, flush/fsync, network blocking, packet transfer, RAM_DISK eviction/lazy-persist windows, and read transfer rate. `create(Configuration, String)` registers an instance with the default metrics system and creates JVM metrics. The many `incr...`, `decr...`, `set...`, and `add...` methods update the annotated `MutableCounterLong`, `MutableGauge*`, `MutableRate`, `MutableRatesWithAggregation`, and quantile fields.

State is in metrics objects registered with `DefaultMetricsSystem`; it is not persisted by this class. `getDNUsageReport` snapshots cumulative bytes/time/block counters into a `DataNodeUsageReport`. `shutdown` shuts down the default metrics system. RPC-latency helpers add both generic operation rates and per-NameNode suffix rates when a suffix is supplied.

## Dependencies, Integration, Risks, and Tests

Dependencies include Hadoop metrics2 annotations/libs, `JvmMetrics`, `DFSConfigKeys`, `DataNodeUsageReportUtil`, and `ThreadLocalRandom`. Integration spans nearly every DataNode subsystem: block sender/receiver, BP service actors, cache manager, RAM_DISK lazy persist, EC reconstruction worker, FsDataset local operations, and network/xceiver tracking.

Risks include metric-name compatibility, counters that can diverge from subsystem state if callers miss increments/decrements, global `DefaultMetricsSystem.shutdown()` affecting other registered sources, quantile overhead when many intervals are configured, and using `int` deltas for byte counters in some APIs. Tests should validate registration names, quantile creation, usage report values, gauge increment/decrement balance, per-RPC suffix metrics, and representative subsystem update methods.
