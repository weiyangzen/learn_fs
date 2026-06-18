# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/magic/MagicS3GuardCommitterFactory.java

## Purpose
Factory for creating `MagicS3GuardCommitter` instances when the S3A committer name is `magic`.

## Important APIs, Types, And Functions
`CLASSNAME` is the factory FQCN. `createTaskCommitter()` constructs and returns a new `MagicS3GuardCommitter`.

## Control Flow
Called by `S3ACommitterFactory` after config selection. The concrete committer constructor performs magic-path capability checks.

## State And Persistence
Stateless factory; no persistent data.

## Dependencies And Integration Points
Extends `AbstractS3ACommitterFactory` and integrates with MapReduce `PathOutputCommitter` creation.

## Risks
No compatibility validation happens here; failures surface during committer construction/setup if magic commit support is disabled.

## Test Signals
Verify factory class name, returned committer type, propagation of constructor failures, and selection through `S3ACommitterFactory`.
