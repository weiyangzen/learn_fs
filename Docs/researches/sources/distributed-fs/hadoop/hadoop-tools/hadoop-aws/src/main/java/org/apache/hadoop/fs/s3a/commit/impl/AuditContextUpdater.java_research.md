# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/impl/AuditContextUpdater.java

## Purpose
Thread-local audit context helper for commit operations. It attaches MapReduce job and task-attempt identifiers to the current S3A audit context and removes them when work completes.

## Important APIs, Types, And Functions
Constructors accept a `JobContext` or explicit job ID. `updateCurrentAuditContext()` sets or removes job/task keys on `CommonAuditContext.currentAuditContext()`. `resetCurrentAuditContext()` clears both fields.

## Control Flow
`CommitContext` creates an updater, applies it to the caller thread, and wraps worker-thread submissions so each task updates audit context before running and resets it afterward.

## State And Persistence
Stores immutable `jobId` and optional `taskAttemptId`. No persistent state; all effects are thread-local audit attributes.

## Dependencies And Integration Points
Depends on Hadoop audit constants, `CommonAuditContext`, MapReduce job/task contexts, and `CommitConstants.PARAM_TASK_ATTEMPT_ID`.

## Risks
Correct reset is important in thread pools; leaked audit attributes would misattribute later filesystem operations. The class removes task-attempt ID using the committer constant key, so key consistency with audit constants matters.

## Test Signals
Verify job-only, task-attempt, null-job, update, reset, and worker-thread wrapping behavior in `CommitContext`.
