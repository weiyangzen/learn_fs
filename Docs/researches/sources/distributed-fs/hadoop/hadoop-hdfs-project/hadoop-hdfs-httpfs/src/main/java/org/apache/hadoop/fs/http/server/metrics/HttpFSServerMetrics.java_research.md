<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/metrics/HttpFSServerMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/metrics/HttpFSServerMetrics.java

## Purpose
`HttpFSServerMetrics` is the metrics2 source for HttpFS server activity. It exposes counters for bytes and selected read/write operations and attaches JVM metrics for the server.

## Important APIs, Types, And Functions
The class is annotated `@Metrics(context="httpfs")`. Mutable counters include `bytesWritten`, `bytesRead`, create/append/truncate/delete/rename/mkdir, open/listing/stat/checkAccess/status/allECPolicies/ECCodecs/trashRoots. `create(Configuration, String)` registers a named source in `DefaultMetricsSystem`, creates `JvmMetrics`, and derives a sanitized source name. Increment methods update counters; getters expose a few values for tests; `shutdown` shuts the default metrics system.

## Control Flow
`HttpFSServerWebApp.setMetrics` calls `create`, then `FSOperations` executors increment counters during request execution. JVM pause monitor integration is completed by the webapp via `getJvmMetrics()`.

## State And Persistence
Metrics counters are in memory and exported through Hadoop metrics/JMX. The registry tags `SessionId`. Shutdown affects the process-wide default metrics system.

## Dependencies And Integration Points
It depends on Hadoop metrics2 annotations, `DefaultMetricsSystem`, `MutableCounterLong`, DFS metrics session id config, `JvmMetrics`, and `FSOperations`/`HttpFSServerWebApp` callers.

## Risks
Only some operations are counted; ACL/xattr/storage-policy/snapshot mutations have little direct metric coverage. Calling `shutdown` on the default metrics system may affect other metrics sources in the same JVM. Counter fields are injected by metrics2 registration and should not be used before registration.

## Test Signals
Tests should confirm registration names, session tags, counter increments from representative operations, JVM metrics attachment, and shutdown behavior in isolated metrics systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/metrics/HttpFSServerMetrics.java -->
