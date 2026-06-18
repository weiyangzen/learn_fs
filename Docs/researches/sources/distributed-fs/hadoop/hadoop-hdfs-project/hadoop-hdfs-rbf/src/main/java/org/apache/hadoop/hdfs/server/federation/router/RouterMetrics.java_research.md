<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterMetrics.java

## Purpose
`RouterMetrics` registers router activity metrics with Hadoop metrics2. It currently exposes router process/session tags, JVM metrics, and a startup safe-mode duration gauge.

## Important APIs, Types, and Functions
`create` obtains the DFS metrics session id, creates `JvmMetrics` for process name `Router`, and registers a `RouterMetrics` instance with `DefaultMetricsSystem`. `setSafeModeTime` updates the annotated `MutableGaugeInt`. `getJvmMetrics` exposes the JVM metrics handle. `shutdown` shuts down the default metrics system.

## Control Flow
Construction tags the internal `MetricsRegistry` with process and session. Metrics registration is centralized through the static factory rather than public constructor access.

## State and Persistence Behavior
Metrics are in-memory and exported by the Hadoop metrics system. No durable state is written. The safe-mode time is cast from `long` to `int`, so very large elapsed values would truncate.

## Dependencies and Integration Points
It depends on `DefaultMetricsSystem`, `MetricsSystem`, `MetricsRegistry`, metrics annotations, `MutableGaugeInt`, `JvmMetrics`, and `DFS_METRICS_SESSION_ID_KEY`. `RouterMetricsService` owns lifecycle.

## Risks
Calling `DefaultMetricsSystem.shutdown()` from this component affects the process-wide metrics system, not just router metrics. The `safeModeTime` gauge is annotation-injected by metrics2 registration and must be non-null before use. The int cast is a minor overflow risk.

## Test Signals
Tests should validate metrics registration, process/session tags, JVM metrics creation, safe-mode gauge update after registration, and service shutdown interactions with other metrics components.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterMetrics.java -->
