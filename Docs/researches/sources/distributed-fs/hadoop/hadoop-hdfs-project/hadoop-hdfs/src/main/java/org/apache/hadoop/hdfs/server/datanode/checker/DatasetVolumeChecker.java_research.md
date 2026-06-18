<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/checker/DatasetVolumeChecker.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/checker/DatasetVolumeChecker.java

## Purpose

`DatasetVolumeChecker` runs runtime health checks against DataNode dataset volumes and returns or reports failed volumes. It centralizes disk-check throttling, timeouts, callback handling, and counters.

## Important APIs, Types, And Functions

- Constructor reads disk-check timeout, minimum gap, and tolerated failure count, then creates a `ThrottledAsyncChecker`.
- `checkAllVolumes(FsDatasetSpi)` synchronously schedules checks for all referenced volumes and returns volumes not proven healthy before timeout.
- `checkVolume(FsVolumeSpi, Callback)` schedules one asynchronous volume check and invokes callback when complete.
- `ResultHandler` maps `HEALTHY`/`DEGRADED` to healthy and `FAILED` or exceptions to failed, then releases `FsVolumeReference`.
- Counter getters report volume checks, synchronous dataset checks, and skipped checks.

## Control Flow

All-volume checks are skipped when the minimum gap has not elapsed. Otherwise the checker obtains volume references, schedules checks, attaches direct callbacks, and waits up to the configured max time. Volumes that were scheduled but not marked healthy by completion/timeout are treated as failed.

## State And Persistence

State includes the delegate checker, timing configuration, failure tolerance, last all-volume check time, timer, counters, and result-handler executor. No filesystem state is changed directly here; concrete volume checks do that.

## Dependencies And Integration Points

It integrates `FsDatasetSpi`, `FsVolumeSpi`, `FsVolumeReference`, `VolumeCheckResult`, DataNode failure-tolerance config, Guava futures, and DataNode metrics/caller handling for failed volumes.

## Risks And Edge Cases

Timeouts mark unproven volumes failed even if their checks later complete. `DEGRADED` is currently treated as healthy. Reference cleanup must happen for scheduled, skipped, success, and failure paths. Config validation rejects negative time/gap and invalid tolerated failure counts.

## Test Signals

Tests should cover skipped all-volume checks, empty datasets, scheduled versus unscheduled checks, timeout behavior, `HEALTHY`/`DEGRADED`/`FAILED` mapping, exception mapping, reference cleanup, counters, and delegate injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/checker/DatasetVolumeChecker.java -->
