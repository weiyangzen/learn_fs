# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/PartitionedStagingCommitterFactory.java

## Purpose
Factory for the partitioned staging committer.

## Important APIs, Types, And Functions
`CLASSNAME` is the factory FQCN. `createTaskCommitter()` constructs `PartitionedStagingCommitter`.

## Control Flow
Selected by `S3ACommitterFactory` when the configured committer name is `partitioned`.

## State And Persistence
Stateless factory.

## Dependencies And Integration Points
Extends `AbstractS3ACommitterFactory`; connects MapReduce task committer creation to partition-aware staging logic.

## Risks
No factory-level validation of partition configuration or destination path; errors occur in committer setup/commit.

## Test Signals
Factory class name, returned committer type, propagation of constructor failures, and top-level selection.
