# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/PartitionedStagingCommitter.java

## Purpose
Staging committer variant that applies conflict resolution at partition-directory granularity. It is designed for partitioned table writes where only touched partitions should be checked or replaced.

## Important APIs, Types, And Functions
`NAME` is `partitioned`. `commitTaskInternal()` computes touched partitions from task output and fails early in `FAIL` mode if corresponding destination partitions already exist. `preCommitJob()` handles job-side policy; `replacePartitions()` reloads all pending sets to identify destination parents and delete them in parallel.

## Control Flow
Task commit identifies partitions relative to the local attempt path before staging uploads. In `FAIL` mode it probes each destination partition before delegating to base upload/pending-set creation. In job pre-commit, `REPLACE` scans pending manifests, builds a concurrent set of partition paths, deletes those partitions, and skips the normal pending-file precheck because manifests were already loaded.

## State And Persistence
No new persistent fields. It consumes `PendingSet` and `SinglePendingCommit.destinationPath()` to discover partition parents.

## Dependencies And Integration Points
Extends `StagingCommitter`; uses `Paths.getPartitions()`, `PersistentCommitData.load()`, `TaskPool`, and destination/source filesystems.

## Risks
Partition replacement requires rereading all pending files and can be expensive. Root-table files map to a special partition token. Destination existence checks during task commit can race with other writers.

## Test Signals
Task outputs in root and nested partitions, FAIL/APPEND/REPLACE modes, partition deletion set correctness, parallel load/delete failures, and preservation of untouched partitions.
