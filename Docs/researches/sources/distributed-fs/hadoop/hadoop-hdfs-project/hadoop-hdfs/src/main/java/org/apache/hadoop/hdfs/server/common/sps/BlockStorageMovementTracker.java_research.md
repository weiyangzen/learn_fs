<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlockStorageMovementTracker.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlockStorageMovementTracker.java

Purpose: runnable tracker that drains completed SPS movement futures and forwards successful result objects to a status handler.

Important APIs and functions: constructor takes a `CompletionService<BlockMovementAttemptFinished>` and optional `BlocksMovementsStatusHandler`. `run` loops on `completionService.take()`, calls `future.get()`, logs the result, and invokes `handler.handle(result)` while still running. `stopTracking` flips a volatile `running` flag.

Control flow and state: `running` controls the outer loop and suppresses handler callbacks after stop. `take()` blocks until interrupted or a future completes. Interrupted exceptions are logged only when still running; execution exceptions are logged with a TODO for retry handling.

Persistence and dependencies: no persistence. Depends on Java concurrency, SPS result/handler types, and logging.

Integration points: movement executor services use this as a companion thread to decouple movement task completion from SPS policy state updates.

Risks and test signals: `stopTracking` alone does not unblock `take`; callers must interrupt the tracker thread for prompt shutdown. Failed futures are logged but not converted to failure status objects. Tests should cover handler invocation, null handler, stop plus interrupt, and `ExecutionException` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlockStorageMovementTracker.java -->
