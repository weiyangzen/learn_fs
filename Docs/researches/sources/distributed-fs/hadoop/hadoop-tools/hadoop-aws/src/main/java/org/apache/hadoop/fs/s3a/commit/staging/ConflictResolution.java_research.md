# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/ConflictResolution.java

## Purpose
Enum defining destination conflict policies for staging committers.

## Important APIs, Types, And Functions
Values are `FAIL`, `APPEND`, and `REPLACE`. `FAIL` rejects existing data, `APPEND` allows merging new files, and `REPLACE` deletes existing destination data at the appropriate job/partition scope.

## Control Flow
`StagingCommitter.getConflictResolutionMode()` parses config into this enum. Directory and partitioned committers switch on it during setup, task commit, and job pre-commit.

## State And Persistence
No persistent state; selected mode is cached by `StagingCommitter`.

## Dependencies And Integration Points
Used by `DirectoryStagingCommitter` and `PartitionedStagingCommitter` to decide fail/append/replace behavior.

## Risks
Unknown configuration strings fail via `valueOf()`. Semantics differ by committer: directory replace deletes whole output path, partitioned replace deletes touched partitions only.

## Test Signals
Validate config parsing, unknown value failure, and behavior for all three modes in directory and partitioned committers.
