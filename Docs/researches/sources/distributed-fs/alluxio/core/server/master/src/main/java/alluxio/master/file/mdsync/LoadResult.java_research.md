# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/LoadResult.java

Purpose: packages one completed UFS load batch with the originating `LoadRequest`, base load path, task info, previous last item, raw `UfsLoadResult`, and first-load flag.

Important APIs and types: getters expose first-load state, previous last item, base load path, UFS load result, task info, and original load request. `onProcessComplete` and `onProcessError` route processing outcomes back through `MetadataSyncHandler`. `compareTo` orders by task id then load request ordering.

Control flow: `PathLoaderTask.createLoadResult` creates it after receiving UFS output. `LoadResultExecutor` processes it by calling `SyncProcess.performSync`, then invokes its completion or error callback.

State and persistence behavior: transient result object. Its previous-last, last-item, truncation, and base path information determine the inode range that `DefaultSyncProcess` updates in persistent metadata.

Dependencies and integration points: depends on `UfsLoadResult`, `TaskInfo`, `LoadRequest`, `AlluxioURI`, and metadata sync callback plumbing.

Risks: like `LoadRequest`, `equals` is based on compare ordering while `hashCode` remains identity-based. Correct previous-last propagation is essential for chunked listing reconciliation.

Test signals: tests should cover ordering, callback routing, previous-last behavior, first-load flag, and truncated versus complete UFS result handling through `DefaultSyncProcess`.
