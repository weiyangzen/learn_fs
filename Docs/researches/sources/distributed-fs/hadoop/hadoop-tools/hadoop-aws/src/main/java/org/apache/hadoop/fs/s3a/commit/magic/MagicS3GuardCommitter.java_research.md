# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/magic/MagicS3GuardCommitter.java

## Purpose
MapReduce committer for S3A magic paths. Tasks write directly to final S3 keys as incomplete MPUs while metadata is recorded under magic paths or in memory; job commit completes the MPUs after all tasks succeed.

## Important APIs, Types, And Functions
`NAME` is `magic`. Constructor sets the task work path and verifies magic output support. `requiresDelayedCommitOutputInFileSystem()` returns true. `setupJob()` creates the magic job path. `listPendingUploadsToCommit()` lists `.pendingset` files in the job attempt directory. `commitTask()` calls `innerCommitTask()`, deletes task attempt paths, and updates statistics. `loadPendingCommits()` selects S3-backed or in-memory metadata loading.

## Control Flow
Task commit loads all pending single commits, patches job/task IDs, aggregates IO stats, saves a single task `PendingSet` under the job attempt path, and aborts loaded pending uploads if saving fails. Job commit uses the superclass flow with `listPendingUploadsToCommit()`. Abort loads pending metadata from memory or S3 and aborts all MPUs, then deletes the attempt path.

## State And Persistence
Persistent state consists of magic directories, task `.pending` files or in-memory maps, job-attempt `.pendingset` files, and optional cleanup of magic/temp directories. Runtime state is mostly inherited from `AbstractS3ACommitter`.

## Dependencies And Integration Points
Uses `CommitOperations`, `CommitContext`, `PendingSet`, `SinglePendingCommit`, `CommitUtilsWithMR`, magic tracker utils, S3A delete/list helpers, and MapReduce contexts.

## Risks
Correctness depends on all task metadata being loadable before job commit. In-memory tracking is process-local. Cleanup is configurable and must not delete unrelated outputs. Failure while saving the task `PendingSet` must abort known MPUs to avoid leaked uploads.

## Test Signals
Exercise S3-backed and in-memory modes, task commit with multiple files, metadata load failure rollback, abortTask from same and different contexts, job pending listing, cleanup enabled/disabled, and verification that final objects appear only after job commit.
