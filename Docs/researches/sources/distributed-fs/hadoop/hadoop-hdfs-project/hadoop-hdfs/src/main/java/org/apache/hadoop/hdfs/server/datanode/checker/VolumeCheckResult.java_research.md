<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/checker/VolumeCheckResult.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/checker/VolumeCheckResult.java

## Purpose

`VolumeCheckResult` is the health result enum shared by storage-location and dataset-volume checks.

## Important APIs, Types, And Functions

- `HEALTHY` means the volume passed checks.
- `DEGRADED` means checks completed with a nonfatal degradation.
- `FAILED` means the volume should be treated as unhealthy.

## Control Flow

Consumers switch on the enum. `DatasetVolumeChecker` treats `HEALTHY` and `DEGRADED` as usable and `FAILED` as failed. `StorageLocationChecker` logs degradation but keeps the location, while removing failed locations.

## State And Persistence

The enum has no mutable state or persistence. It is returned by `Checkable` implementations and carried through futures.

## Dependencies And Integration Points

It is used by `StorageLocation`, `FsVolumeSpi` checks, `ThrottledAsyncChecker`, `DatasetVolumeChecker`, and `StorageLocationChecker`.

## Risks And Edge Cases

The current consumers treat `DEGRADED` as healthy enough to continue, so implementations must use `FAILED` for conditions requiring removal. Adding enum values would require updating all switch statements.

## Test Signals

Tests should verify consumer mapping for all enum values and default/error handling for unexpected future behavior such as null results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/checker/VolumeCheckResult.java -->
