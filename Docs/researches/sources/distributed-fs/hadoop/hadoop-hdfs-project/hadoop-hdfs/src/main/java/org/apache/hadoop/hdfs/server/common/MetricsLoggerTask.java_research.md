<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/MetricsLoggerTask.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/MetricsLoggerTask.java

## Purpose

`MetricsLoggerTask` dumps Hadoop JMX metrics to a named logger, typically for periodic operational diagnostics.

## Important APIs and types

The constructor accepts metrics logger name, node name, and maximum log line length. `run` queries platform MBeans matching `Hadoop:*`, filters unsupported complex attribute types, fetches attributes, and logs `mbeanName:attribute=value` lines. Helpers are `trimLine`, `hasAppenders`, and `getFilteredAttributes`.

## Control flow

The task exits early if the metrics logger is not info-enabled, has no appenders, or the object-name pattern failed to initialize. Otherwise it logs begin/end markers, iterates MBeans, retrieves allowed attributes in batch, truncates long values if configured, and logs per-MBean errors without stopping the whole dump.

## State and persistence behavior

State is limited to logger configuration. Metrics are read live from the platform MBean server and persisted only as log output.

## Dependencies and integration points

It integrates with Java Management APIs, Hadoop `MBeans`, SLF4J, and Log4j appender detection.

## Risks and edge cases

Log4j-specific appender detection is called from SLF4J logger names and may not work with all logging backends. Complex OpenMBean values are skipped entirely. Very high attribute counts can produce large logs despite line truncation.

## Test signals

Tests should cover early exits, attribute filtering, truncation boundaries, per-MBean exception handling, begin/end markers, and logger/appender configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/MetricsLoggerTask.java -->
