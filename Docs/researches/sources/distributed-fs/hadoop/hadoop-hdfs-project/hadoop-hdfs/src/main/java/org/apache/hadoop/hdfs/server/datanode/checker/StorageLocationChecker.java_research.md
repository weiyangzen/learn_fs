<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/checker/StorageLocationChecker.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/checker/StorageLocationChecker.java

## Purpose

`StorageLocationChecker` validates configured DataNode storage directories during startup and returns the healthy locations in input order. It enforces disk-check timeouts and tolerated-failure policy before the DataNode opens storage.

## Important APIs, Types, And Functions

- Constructor reads disk-check timeout, expected data-dir permission, tolerated volume failures, and creates a `ThrottledAsyncChecker`.
- `check(Configuration, Collection<StorageLocation>)` schedules checks for all locations, waits within a cumulative timeout, classifies failures, and returns healthy locations.
- `shutdownAndWait` shuts down the delegate checker.

## Control Flow

The checker initializes all locations as good, schedules async `StorageLocation.check` calls, then iterates futures and waits only for remaining timeout budget. `FAILED`, execution errors, and timeouts remove locations from the good map. Failure counts are compared against configured tolerance; zero good locations always fail.

## State And Persistence

State includes the delegate checker, timer, max check time, expected permission, and failure tolerance. Concrete `StorageLocation.check` may create or validate local directories depending on filesystem behavior.

## Dependencies And Integration Points

It integrates DataNode startup config, `StorageLocation`, local filesystem permissions, `VolumeCheckResult`, `DiskErrorException`, and `ThrottledAsyncChecker`. It preserves input order through `LinkedHashMap`.

## Risks And Edge Cases

Tolerating a number of failures greater than or equal to configured volumes is invalid. Cumulative timeout means later futures may get little or no wait time. `DEGRADED` is logged but retained as good. Provided storage check returns healthy without disk probing.

## Test Signals

Tests should cover order preservation, all-good, degraded, failed, exception, timeout, all-failed, tolerated-failure thresholds, invalid tolerance, permissions, and shutdown interruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/checker/StorageLocationChecker.java -->
