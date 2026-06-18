# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/metrics/NameNodeMetrics.java

## Purpose

`NameNodeMetrics.java` maintains mutable Hadoop metrics for NameNode runtime activity, edit-log latency, block reports, encryption key operations, image transfer servlet calls, and standby edit tailing. The source was read as a complete 484-line file.

## Important APIs, Types, and Functions

The class is annotated `@Metrics(name="NameNodeActivity", context="dfs")` and owns many `@Metric` counters, gauges, rates, stats, and quantile arrays. Important methods include constructor, static `create`, `shutdown`, `totalFileOps`, numerous `incr*` operation counters, block queue setters, transaction/sync metrics, block/cache report latencies, safe mode and image load time setters, get/put image metrics, EDEK/resource-check metrics, and edit-tail metrics.

## Control Flow

`create` obtains the metrics session ID, process name from `NamenodeRole`, registers JVM metrics, reads percentile intervals, and registers a new `NameNodeMetrics` instance with the default metrics system. The constructor tags process/session and creates quantile metrics for each configured interval. Increment/add methods update both aggregate rate/stat and corresponding quantile arrays where present. `totalFileOps` sums the operation counters considered filesystem operations.

## State and Persistence Behavior

All state is in-memory metrics state exported through Hadoop metrics sinks. There is no persistence, though external metrics systems may scrape or store values.

## Dependencies and Integration Points

It integrates with Hadoop metrics2 annotations, `DefaultMetricsSystem`, `MetricsRegistry`, `MutableCounterLong`, `MutableGaugeInt`, `MutableRate`, `MutableStat`, `MutableQuantiles`, `JvmMetrics`, `DFSConfigKeys`, and NameNode subsystems that call increment methods.

## Risks and Edge Cases

Metrics must be updated on all relevant operation paths or operator observability becomes misleading. Casting long elapsed times to int for safe mode and image load time can truncate extreme values. Percentile interval configuration controls quantile allocation; empty intervals mean no quantiles. `shutdown` shuts down the default metrics system, which affects process-wide metrics.

## Test Signals

Tests should verify registration tags, counters included in `totalFileOps`, each increment/add method mutates expected metrics, quantiles are updated for configured intervals, safe mode/image load setters, edit-tail metrics from `EditLogTailer`, image servlet metrics from transfer endpoints, and shutdown behavior.
