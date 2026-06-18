<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/Phase.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/Phase.java

## Purpose

`Phase` enumerates the coarse NameNode startup phases in expected execution order: loading fsimage, loading edits, saving checkpoint, and safemode.

## Important APIs and types

Each enum constant has a stable metrics/display name and human-readable description. Public accessors are `getName()` and `getDescription()`.

## Control flow

The enum has no dynamic flow. `StartupProgress` initializes tracking for all enum values, and `StartupProgressView` iterates all phases when computing aggregate percent complete.

## State and persistence behavior

Enum state is immutable JVM metadata. Names are used for metrics identity and should be treated as compatibility-sensitive.

## Dependencies and integration points

Used throughout NameNode startup instrumentation, the startup-progress servlet/UI path, and `StartupProgressMetrics`.

## Risks and edge cases

Adding or reordering phases affects aggregate percent-complete math and emitted metric names. The overall progress calculation treats all phases as equal weight, so phase changes can alter operator-visible progress.

## Test signals

Startup progress tests should verify status transitions for each phase, complete detection through `SAFEMODE`, and metric names derived from `getName`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/Phase.java -->
