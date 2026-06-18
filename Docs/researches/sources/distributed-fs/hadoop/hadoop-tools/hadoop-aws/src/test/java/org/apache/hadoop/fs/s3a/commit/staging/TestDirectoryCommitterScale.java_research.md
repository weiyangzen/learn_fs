# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/TestDirectoryCommitterScale.java

## Purpose
Mock scale test for `DirectoryStagingCommitter` job commit/abort behavior with many pending uploads. It stresses loading and committing thousands of pending entries without using real S3.

## Important APIs, Types, and Functions
The class extends `StagingTestBase.JobCommitterTest<DirectoryStagingCommitter>`. Constants define 500 tasks, 10 files per task, 5000 total commits, 1000 blocks per task, and 100 committer threads. It defines a `DirectoryCommitterForTesting` subclass that uses a prebuilt local staging path as the job attempt path and records `ActiveCommit`.

## Control Flow and Behavior
`setupStaging()` creates a local staging directory. `test_010_createTaskFiles()` calls `createTasks()`, which builds template `SinglePendingCommit` objects with many `CompletedPart` entries, writes `.pendingset` files per task, and records active upload IDs. `test_020_loadFilesToAttempt()` verifies `listPendingUploadsToCommit()` finds all task pending-set files. `test_030_commitFiles()` seeds active uploads into mock results, commits the job in append mode, and verifies 5000 complete-MPU requests plus success marker limits. `test_040_abortFiles()` exercises abort handling over the same scale.

## State, Persistence, and Dependencies
State includes local `.pendingset` files, `activeUploads` map, mock S3 results, and recorded `ActiveCommit`. Dependencies include `PendingSet`, `SinglePendingCommit`, `CompletedPart`, `CommitOperations`, `CommitContext`, `JsonSerialization`, and local filesystem staging.

## Integration Points, Risks, and Test Signals
This is a stress signal for staging job commit listing, active commit aggregation, success marker truncation, and high-thread commit execution. Risks are local disk use, static `activeUploads` lifecycle, and mock behavior not fully matching S3 latency/error patterns.
