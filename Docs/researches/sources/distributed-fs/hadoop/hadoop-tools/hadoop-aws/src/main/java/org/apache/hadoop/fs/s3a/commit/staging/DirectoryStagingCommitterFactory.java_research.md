# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/DirectoryStagingCommitterFactory.java

## Purpose
Factory for the directory staging committer.

## Important APIs, Types, And Functions
`CLASSNAME` is the factory FQCN. `createTaskCommitter()` returns a new `DirectoryStagingCommitter`.

## Control Flow
Selected by `S3ACommitterFactory` when `fs.s3a.committer.name` is `directory`.

## State And Persistence
Stateless factory.

## Dependencies And Integration Points
Extends `AbstractS3ACommitterFactory` and integrates MapReduce output committer creation with `DirectoryStagingCommitter`.

## Risks
No extra validation here; all conflict and path validation is deferred to the concrete committer.

## Test Signals
Factory class name, returned type, constructor failure propagation, and selection from top-level committer factory.
