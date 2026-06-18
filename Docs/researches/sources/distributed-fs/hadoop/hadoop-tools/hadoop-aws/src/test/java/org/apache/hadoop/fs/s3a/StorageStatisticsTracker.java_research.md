# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/StorageStatisticsTracker.java

## Purpose

Small helper that snapshots a filesystem's `StorageStatistics` long counters and reports differences against later snapshots.

## Important APIs, Types, and Functions

The public API is `mark()`, `compare(Map<String, Long>)`, `compareToCurrent()`, `toString(Map)`, `snapshot()`, and `latestValues()`. `StatsIterator` adapts `StorageStatistics.getLongStatistics()` to an `Iterable`.

## Control Flow

Construction stores the filesystem and immediately captures a baseline snapshot. `mark()` refreshes the baseline. `snapshot()` iterates current long statistics into a map. `compare()` walks baseline entries and records keys whose current values differ.

## State, Dependencies, and Integration Points

State is the tracked `FileSystem` and the current baseline map. It depends on Hadoop `StorageStatistics` and shaded Guava `Joiner`. It is useful in tests that want operation-count deltas without directly reading S3A instrumentation.

## Risks and Test Signals

The diff direction is baseline minus current, which can surprise readers expecting current minus baseline. New counters that appear after the baseline are ignored. Test signal is strongest when the caller knows exact counter names and understands this signed-difference convention.
