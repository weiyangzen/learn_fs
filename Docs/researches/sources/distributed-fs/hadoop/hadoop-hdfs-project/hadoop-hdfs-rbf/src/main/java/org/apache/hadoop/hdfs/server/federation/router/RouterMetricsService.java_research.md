<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterMetricsService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterMetricsService.java

## Purpose
`RouterMetricsService` owns the lifecycle of all router metrics and JMX-facing federation metrics. It creates core metrics during service init, creates JMX beans during service start, and closes everything during service stop.

## Important APIs, Types, and Functions
`serviceInit` creates `RouterMetrics` and `RouterClientMetrics`. `serviceStart` constructs `NamenodeBeanMetrics` and `RBFMetrics` wrappers over the router. `serviceStop` closes `RBFMetrics` and `NamenodeBeanMetrics`, then shuts down router and client metrics. Getter methods expose each metrics object and `getJvmMetrics` safely returns null before initialization.

## Control Flow
The service follows Hadoop lifecycle ordering: basic metrics are available after init, JMX beans after start, and all handles are guarded for null on stop. It does not call `super.serviceInit/start/stop` in the shown overrides, so lifecycle behavior relies on `AbstractService` caller semantics around override methods.

## State and Persistence Behavior
All state is process-local metrics/JMX handles. No durable state is written. Shutdown closes MBeans and metrics systems.

## Dependencies and Integration Points
Dependencies include `Router`, `RouterMetrics`, `RouterClientMetrics`, `RBFMetrics`, `NamenodeBeanMetrics`, `JvmMetrics`, and `AbstractService`.

## Risks
Partial initialization can leave some handles null; the stop path handles that. Metrics shutdown order matters because `RouterMetrics.shutdown()` shuts down the default metrics system. Missing `super` calls could be relevant if `AbstractService` changes expectations. JMX wrapper constructors may throw during start, leaving only init metrics active.

## Test Signals
Tests should cover init/start/stop lifecycle, null-safe stop after partial start, getter behavior before and after init/start, JVM metrics delegation, and MBean close calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterMetricsService.java -->
