# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/TestStagingPartitionedFileListing.java

## Purpose
Tests partitioned staging committer task output discovery and partition inference from task output trees.

## Important APIs, Types, and Functions
The class extends `TaskCommitterTest<PartitionedStagingCommitter>` and uses `PartitionedStagingCommitter.getTaskOutput()`, `Paths.getRelativePath()`, `Paths.getPartitions()`, and `S3AUtils.mapLocatedFiles()`.

## Control Flow and Behavior
Task output listing tests create nested partition-like files under the task attempt path and compare discovered relative paths with expected paths. Hidden files such as `_metadata` and dot-prefixed partial files are created but must be filtered out. Partition resolution tests create a local tree, assert empty file lists yield no partitions, verify nested files produce partition strings, and verify root-level files map to `TABLE_ROOT`.

## State, Persistence, and Dependencies
State is local task-attempt output under the test temp directory, cleaned in `@AfterEach`. Dependencies include local/attempt filesystems, partition path utilities, hidden-file filtering, and task committer setup from `StagingTestBase`.

## Integration Points, Risks, and Test Signals
Correct listing and partition extraction drive partitioned commit conflict checks and replace/delete behavior. Risks include accidental inclusion of metadata/temporary files and incorrect table-root handling for non-partitioned outputs.
