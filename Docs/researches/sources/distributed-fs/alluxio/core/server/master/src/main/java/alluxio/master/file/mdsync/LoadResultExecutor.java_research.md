# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/LoadResultExecutor.java

Purpose: fixed-thread-pool executor for processing `LoadResult`s into metadata sync mutations. It separates UFS listing concurrency from metadata-processing concurrency.

Important APIs and types: constructor accepts a `SyncProcess`, executor thread count, and `UfsSyncPathCache`. `processLoadResult` accepts callbacks for before-processing, completion, and error. `close` shuts down the executor.

Control flow: submitted work calls `beforeProcessing`, invokes `mSyncProcess.performSync(result, mSyncPathCache)`, and routes success to `onComplete`. Mount-point-not-found and generic exceptions are caught separately to record appropriate `SyncFailReason`s before calling `onError`.

State and persistence behavior: executor state is in memory, but `performSync` carries out journaled metadata mutations. It increments process-started and process-completed counters through callbacks supplied by `LoadRequestExecutor`.

Dependencies and integration points: depends on `SyncProcess`, `LoadResult`, `SyncProcessResult`, `UfsSyncPathCache`, thread factory utilities, and sync failure reporting.

Risks: `close` uses `shutdown` without awaiting termination, so callers may need external lifecycle guarantees. Exceptions in `beforeProcessing` are not explicitly caught before `performSync`.

Test signals: tests should cover successful processing, mount-point failure classification, generic failure classification, callback ordering, thread pool shutdown, and process counter updates.
