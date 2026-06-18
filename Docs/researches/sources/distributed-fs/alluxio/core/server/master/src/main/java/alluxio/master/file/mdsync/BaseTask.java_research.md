# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/BaseTask.java

Purpose: abstract base for a metadata sync task. It combines task identity and stats, UFS path loading through `PathLoaderTask`, wait-for-path semantics through `PathWaiter`, task state transitions, cancellation, completion notification, and final direct-children-loaded updates.

Important APIs and types: `State` maps internal states to `SyncMetadataState`; static `create` selects `DirectoryPathWaiter` for recursive BFS/DFS directory loading and `BatchPathWaiter` otherwise. Public APIs include `getState`, `isCompleted`, `succeeded`, `getTaskInfo`, `waitComplete`, `getSyncDuration`, and `toProtoTask`.

Control flow: a task starts with a `PathLoaderTask`. Load and process callbacks eventually call `onComplete`, `onFailed`, or `cancel`. `waitComplete` blocks until completion or timeout, propagating the failure cause. Completion updates direct-children-loaded flags through the file master and inode tree, marks success, notifies the metadata sync handler, and wakes waiters.

State and persistence behavior: task state is in memory. On success, `updateDirectChildrenLoaded` opens a journal context and persists direct-children-loaded updates for directories recorded in `TaskInfo`. Proto conversion includes exception and stats for reporting.

Dependencies and integration points: integrates `TaskInfo`, `PathLoaderTask`, `MetadataSyncHandler`, `DefaultFileSystemMaster`, `InodeTree`, journal contexts, `SyncMetadataTask`, and Alluxio exception types.

Risks: many methods synchronize on the task object, but callbacks arrive from loader and processor threads, so deadlock and notification correctness matter. `getStartTime` requires completion even though its name suggests simple access. Runtime exceptions in direct-children-loaded updates can turn completion into failure-like behavior outside the task result model.

Test signals: tests should cover success, failure, cancellation, timeout, proto conversion, recursive versus batch waiter selection, and direct-children-loaded journal updates.
