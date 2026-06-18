# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/PathLoaderTask.java

Purpose: manages all UFS load requests for one metadata sync task. It creates initial, continuation, retry, and nested-directory load requests; tracks running loads and truncated batch sets; emits `LoadResult`s; and determines when path loading is complete.

Important APIs and types: key methods include `createLoadResult`, `loadNestedDirectory`, `onProcessComplete`, `onProcessError`, `onLoadRequestError`, `cancel`, `getNext`, and `runOnPendingLoad`. State includes ready priority queue, running load map, truncated load set, next load id, rate limiter, task info, and UFS client supplier.

Control flow: construction enqueues a first request against the base path. UFS output updates stats, records whether the first load was a file, creates continuation requests when truncated, and returns a `LoadResult`. Processing completion removes the load request, clears batch-set tracking for final batches, notifies per-result progress, and marks the whole task complete when no running or truncated loads remain.

State and persistence behavior: in-memory load orchestration only. Its completion callback triggers `MetadataSyncHandler.onPathLoadComplete`, which eventually persists direct-children-loaded updates and updates sync/absent caches.

Dependencies and integration points: depends on `LoadRequest`, `LoadResult`, `TaskInfo`, `TaskStats`, `RateLimiter`, UFS client, `UfsLoadResult`, `MetadataSyncHandler`, and directory load options.

Risks: `addLoadRequest` mutates `mRunningLoads` and queues but is not always called under this object's synchronized lock, so thread-safety relies on caller discipline and queue concurrency. Truncated batch-set accounting must be exact or tasks may complete too early or never complete. Retry exhaustion fails the entire task.

Test signals: tests should cover first load, continuation, truncated batch completion, nested directory loads, retry success/failure, cancellation, process error, and completion notification.
