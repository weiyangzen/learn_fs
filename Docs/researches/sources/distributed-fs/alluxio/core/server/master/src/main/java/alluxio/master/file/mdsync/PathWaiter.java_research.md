# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/PathWaiter.java

Purpose: interface for task implementations that can block until a path is synchronized and receive progress notifications.

Important APIs and types: `waitForSync(AlluxioURI path)` returns whether the requested path became synced successfully. `nextCompleted(SyncProcessResult completed)` informs the waiter about a processed load result.

Control flow: `BaseTask` implements this interface through concrete subclasses. Traversal or sync-check code can call `waitForSync`; `MetadataSyncHandler.onEachResult` calls `nextCompleted` after each processed load.

State and persistence behavior: no state or persistence in the interface. Implementations maintain in-memory progress and coordinate with persistent metadata sync operations.

Dependencies and integration points: depends on `AlluxioURI` and `SyncProcessResult`. Implemented by `BatchPathWaiter` and `DirectoryPathWaiter`.

Risks: interface semantics require implementations to handle task completion, failure, and interruption consistently. Inconsistent coverage semantics between implementations could affect user-visible traversal.

Test signals: conformance tests should verify both implementations unblock on progress, unblock on task completion, and return false on failure/interruption.
