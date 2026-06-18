# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/TaskTracker.java

Purpose: tracks active and recently finished metadata sync tasks, prevents conflicting tasks through trie indexes, launches path loaders, handles completion/error/cancel cleanup, and updates sync/absent caches.

Important APIs and types: active task indexes are split by descendant type into recursive, list, and status tries, with configuration controlling whether non-recursive list/get-status can run concurrently with recursive tasks. Public methods include `getActiveTask`, `getTaskProto`, `cancelTaskById`, `launchTaskAsync`, test-visible `checkTask`, and `close`.

Control flow: `launchTaskAsync` finds an existing covering task or inserts a new trie node, allocates an id, creates `BaseTask`, records sync start time, stores it in maps, and submits its `PathLoaderTask` to `LoadRequestExecutor`. Completion removes active state, optionally caches task proto, increments counters, notifies sync path cache, updates absent cache based on status count, and removes trie entry. Error and cancel paths remove task state and clean load executor state.

State and persistence behavior: in-memory task registry and finished-task cache. It updates `UfsSyncPathCache` and `UfsAbsentPathCache`, which influence future sync decisions, but does not directly journal inode changes.

Dependencies and integration points: integrates `LoadRequestExecutor`, `LoadResultExecutor`, `UfsSyncPathCache`, `UfsAbsentPathCache`, `MetadataSyncHandler`, `TaskInfo`, `BaseTask`, tries, metrics counters/gauges, and UFS client suppliers.

Risks: concurrency correctness depends on synchronized methods around trie and map state. `cancelTasksUnderPath` removes active map entries but does not appear to remove trie nodes or notify load executor, making it a path to inspect carefully. Finished task cache is fixed at 1000 and may evict task status.

Test signals: tests should cover duplicate/covered task reuse, concurrency configuration, completion cleanup, error cleanup, cancellation by id, cache updates for absent versus existing paths, metrics gauges, and executor shutdown.
