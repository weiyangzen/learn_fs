# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/SyncProcess.java

Purpose: interface for the component that applies one loaded UFS batch to Alluxio metadata.

Important APIs and types: single method `performSync(LoadResult loadResult, UfsSyncPathCache syncPathCache)` returns a `SyncProcessResult` and can throw any `Throwable`.

Control flow: `LoadResultExecutor` calls this interface for each `LoadResult`, allowing execution and error classification to be separated from the sync implementation. `DefaultSyncProcess` is the production implementation.

State and persistence behavior: interface has no state. Implementations are expected to perform journaled metadata changes and update sync path cache as needed.

Dependencies and integration points: depends on `LoadResult`, `SyncProcessResult`, and `UfsSyncPathCache`. Integrates with `LoadResultExecutor` and `DefaultSyncProcess`.

Risks: broad `throws Throwable` gives implementations and callers flexibility but requires careful error classification. Implementations must define transactional boundaries and cache updates clearly.

Test signals: executor tests can use fake `SyncProcess` implementations for success and failure; production behavior is covered through `DefaultSyncProcess` tests.
