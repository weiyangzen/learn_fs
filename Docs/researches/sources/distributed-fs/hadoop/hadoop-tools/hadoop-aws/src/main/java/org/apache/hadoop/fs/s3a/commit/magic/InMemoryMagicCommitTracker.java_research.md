# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/magic/InMemoryMagicCommitTracker.java

## Purpose
Magic commit tracker variant that stores pending commit metadata in process memory rather than writing `.pending` metadata objects to S3.

## Important APIs, Types, And Functions
Static concurrent maps store task-attempt ID to `SinglePendingCommit` list, path to bytes written, and task-attempt ID to written paths. `aboutToComplete()` validates MPU inputs, builds a `SinglePendingCommit`, snapshots IO statistics, extracts the task attempt ID from the magic path, and stores metadata in those maps. Static getters expose the maps for task commit/abort cleanup.

## Control Flow
The output stream calls `aboutToComplete()` near close. The method records metadata and returns false, preventing immediate MPU completion. `MagicS3GuardCommitter.loadPendingCommitsFromMemory()` later removes and consumes the entries.

## State And Persistence
All state is static and process-local. Nothing is persisted to S3 until the task committer writes a `PendingSet`; data is removed when a task commits or aborts.

## Dependencies And Integration Points
Extends `MagicCommitTracker`, uses `SinglePendingCommit`, `IOStatisticsSnapshot`, and `MagicCommitTrackerUtils.extractTaskAttemptIdFromPath()`. Enabled by `fs.s3a.committer.magic.track.commits.in.memory`.

## Risks
Because metadata is in-memory, it is unsuitable across process loss or task commit in a different JVM. Static maps can leak if abort/commit cleanup is missed. Task-attempt extraction is path-shape sensitive.

## Test Signals
Test close-time metadata creation, map cleanup on commit and abort, zero/missing parts rejection, process-local failure assumptions, and concurrent writes from multiple files in one task.
