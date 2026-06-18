<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/AbstractTracking.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/AbstractTracking.java

## Purpose

`AbstractTracking` is the shared internal base for startup-progress tracking records. It stores begin and end timestamps with `Long.MIN_VALUE` as the undefined sentinel.

## Important APIs and types

- Package-private abstract class implementing `Cloneable`.
- Fields `beginTime` and `endTime`.
- `copy(AbstractTracking dest)` copies base timestamp fields into subclass clones.

## Control flow

There is no complex flow. Subclasses call `super.copy(clone)` inside their `clone` implementations to preserve common timing state.

## State and persistence behavior

State is in-memory only and uses monotonic timestamps assigned by `StartupProgress`. No persistence or external reporting happens here.

## Dependencies and integration points

`PhaseTracking` and `StepTracking` extend it. `StartupProgressView` interprets its sentinel values to calculate status and elapsed time.

## Risks and edge cases

All consumers must consistently treat `Long.MIN_VALUE` as undefined, not a real timestamp. Direct package-private field access keeps the type lightweight but relies on local discipline.

## Test signals

`TestStartupProgress` and `TestStartupProgressMetrics` indirectly cover begin/end cloning, elapsed time calculations, and sentinel handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/AbstractTracking.java -->
