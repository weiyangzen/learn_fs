# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/PartitionedCommitterForTesting.java

## Purpose
Small test subclass of `PartitionedStagingCommitter` that relaxes destination filesystem checking and records the output path after initialization.

## Important APIs, Types, and Functions
It overrides `initOutput(Path)` to call `super.initOutput(out)` and then `setOutputPath(out)`. It also overrides `getDestinationFS(Path, Configuration)` to return `out.getFileSystem(config)` directly.

## Control Flow and Behavior
Construction follows the normal partitioned committer path. During initialization, output metadata is initialized by the superclass, then forced into the committer for tests. Destination filesystem lookup bypasses S3A type enforcement so `MockS3AFileSystem` wrappers can be used.

## State, Persistence, and Dependencies
The subclass does not add persistent state. It depends on `PartitionedStagingCommitter`, `TaskAttemptContext`, `FileSystem`, and test mock filesystem binding.

## Integration Points, Risks, and Test Signals
Used by partitioned job commit tests to exercise partition conflict and replace behavior against mocks. The relaxation of destination FS checks is test-only and should not be interpreted as production behavior.
