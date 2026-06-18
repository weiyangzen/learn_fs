<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/TopAuditLogger.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/TopAuditLogger.java

## Purpose

`TopAuditLogger` is an `AuditLogger` implementation that feeds NameNode audit events into NNTop metrics so operators can see top users by operation.

## Important APIs and types

- Default constructor builds `HdfsConfiguration`, `TopConf`, and `TopMetrics`, then registers the metrics source if absent.
- Test/injection constructor accepts a `TopMetrics`.
- `initialize(Configuration)` is a no-op.
- `logAuditEvent` forwards audit event fields to `TopMetrics.report` and emits debug logging.

## Control flow

On each audit event, the logger attempts to report to `topMetrics` and catches `Throwable` so audit logging cannot fail the NameNode operation. If debug logging is enabled, it formats the standard audit fields and permission information.

## State and persistence behavior

The logger holds one `TopMetrics` instance. State is accumulated in rolling metrics windows, not in this class. No persistent logging beyond SLF4J is performed here.

## Dependencies and integration points

Implements the NameNode `AuditLogger` SPI. Integrates with `DefaultMetricsSystem`, `TopConf`, `TopMetrics`, `FileStatus`, and NameNode audit configuration.

## Risks and edge cases

The default constructor creates a fresh `HdfsConfiguration`, so configuration source alignment matters when used outside normal audit logger initialization. Catching `Throwable` protects operations but can hide persistent NNTop failures except for logs. The metrics source is registered only if absent, so multiple logger instances share process-global registration behavior.

## Test signals

`TestAuditLogger`, `TestAuditLogs`, `TestTopMetrics`, and NameNode MXBean top-user tests provide signals. Tests should verify disabled top logger behavior, WebHDFS audit integration, and that report failures do not break audited operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/top/TopAuditLogger.java -->
