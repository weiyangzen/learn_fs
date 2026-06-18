# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/StagingCommitter.java

## Purpose
Base implementation for S3A staging committers. Tasks write to local filesystem work directories, task commit uploads files as incomplete MPUs and writes pending manifests to a cluster filesystem, and job commit completes the MPUs.

## Important APIs, Types, And Functions
Constructor configures multipart size, unique filenames, local work path, wrapped `FileOutputCommitter`, commit manifest directory, S3 key prefix, and conflict mode. Key methods include `setupJob()`, `setupTask()`, `needsTaskCommit()`, `commitTask()`, `commitTaskInternal()`, `abortTask()`, `listPendingUploadsToCommit()`, `listPendingUploadsToAbort()`, `cleanup()`, and `preCommitJob()`.

## Control Flow
Task setup creates local and wrapped-committer attempt paths. `needsTaskCommit()` lists local output. `commitTaskInternal()` lists output files, computes relative paths and final S3 keys, uploads each local file through `CommitOperations.uploadFileToPendingCommit()`, builds a `PendingSet`, optionally aggregates IO statistics, saves the manifest to the wrapped committer task path, aborts successfully staged MPUs on failure, commits the wrapped task, and deletes local output. Job abort lists pending manifests and aborts MPUs.

## State And Persistence
Runtime state includes output path, local work path, upload part size, unique filename flag, conflict mode, S3 key prefix, and wrapped committer. Persistent state includes local task files, cluster `.pendingset` manifests, and S3 incomplete MPUs.

## Dependencies And Integration Points
Extends `AbstractS3ACommitter`; wraps `FileOutputCommitter` algorithm 1; uses `CommitOperations`, `CommitContext`, `PendingSet`, `Paths`, S3A filesystem helpers, and MapReduce contexts.

## Risks
Local files are host-local; abort from a different host may not clean them. Failure after MPU upload but before manifest save must abort staged commits. Unique filename mode affects final key stability. Cleanup deletes destination `__temporary`, which is risky when multiple jobs share output paths.

## Test Signals
Task commit with zero, one, and many files; failed upload and manifest save cleanup; unique filename on/off; local work cleanup; job abort cleanup; wrapped committer behavior; IO stats aggregation; and conflict-mode delegation to subclasses.
