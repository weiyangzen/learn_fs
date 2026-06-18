<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/ExternalSPSFaultInjector.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/ExternalSPSFaultInjector.java

## Purpose

`ExternalSPSFaultInjector` is a test hook for injecting failures into external SPS block movement retry paths.

## Important APIs and types

It keeps a static singleton `instance`, with visible-for-testing `getInstance()` and `setInstance(...)`. `mockAnException(int retry)` is a no-op by default and may be overridden to throw `IOException`.

## Control flow

`ExternalSPSBlockMoveTaskHandler.BlockMovingTask.moveBlock()` calls `mockAnException(retry)` before obtaining a block token and moving the block. Tests can replace the singleton to force failures on specific retry attempts.

## State and persistence behavior

State is only the static singleton reference. There is no persistence.

## Dependencies and integration points

It integrates with external SPS move retry tests and depends on `VisibleForTesting` and `IOException`.

## Risks and test signals

Because the singleton is static and mutable, tests must reset it to avoid cross-test leakage. Tests should verify injected failures produce expected retry counts and that the default injector has no behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/ExternalSPSFaultInjector.java -->
