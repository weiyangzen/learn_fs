# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/MetadataSyncHandler.java

Purpose: callback facade connecting task tracking, path loading, result processing, and file-master completion actions. It centralizes interactions among metadata sync components so the orchestration can be changed later.

Important APIs and types: methods route load errors, task failures, processing errors, per-result progress, task errors, task completion, path-load completion, nested-directory loads, load outputs, and process completion. It holds `TaskTracker`, `DefaultFileSystemMaster`, and `InodeTree`.

Control flow: UFS and processing callbacks call into this handler with task ids. It looks up active tasks in `TaskTracker` and invokes the relevant `BaseTask` or `PathLoaderTask` method. Path-load completion calls `BaseTask.onComplete`, which persists direct-children-loaded changes and then reports task completion.

State and persistence behavior: no independent persisted state. It triggers task completion paths that may update inode direct-children-loaded state and sync caches.

Dependencies and integration points: integrates `TaskTracker`, `BaseTask`, `PathLoaderTask`, `DefaultFileSystemMaster`, `InodeTree`, `LoadResult`, `UfsLoadResult`, and `SyncProcessResult`.

Risks: callbacks for missing or already-completed tasks are silently ignored through `Optional.ifPresent`, which is appropriate for races but can hide unexpected callback loss. Correct task id and load id routing is critical.

Test signals: tests should cover every callback route, missing task behavior, nested directory load scheduling, and final completion/error cleanup through `TaskTracker`.
