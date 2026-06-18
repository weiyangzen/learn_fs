<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/Status.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/Status.java

## Purpose

`Status` is the run-state enum for startup phases: not started, currently running, or complete.

## Important APIs and types

The enum constants are `PENDING`, `RUNNING`, and `COMPLETE`. There are no methods beyond enum defaults.

## Control flow

`StartupProgress` and `StartupProgressView` derive status from begin/end timestamp sentinels: no begin is pending, begin without end is running, and both begin/end is complete.

## State and persistence behavior

The enum has immutable JVM state only. Its values are externally visible through startup-progress views and may be serialized by UI/metrics code.

## Dependencies and integration points

Referenced by `Phase` documentation, progress view APIs, and tests.

## Risks and edge cases

Status has no failed/cancelled state, so startup instrumentation can only represent progress, not explicit startup errors.

## Test signals

Tests should cover all three states through phase begin/end transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/Status.java -->
