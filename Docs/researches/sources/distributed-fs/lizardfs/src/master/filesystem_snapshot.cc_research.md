# sources/distributed-fs/lizardfs/src/master/filesystem_snapshot.cc

Purpose: provides the public master entry points for creating filesystem snapshots and cloning individual nodes. It validates operation context and delegates actual copy work to `SnapshotTask`.

Important APIs/types/functions: `fs_read_snapshot_config_file()` reads `SNAPSHOT_INITIAL_BATCH_SIZE` and `SNAPSHOT_INITIAL_BATCH_SIZE_LIMIT`; `fs_snapshot()` validates source and destination, prevents recursive directory snapshots into descendants, builds a `SnapshotTask`, computes human-readable source/destination paths, clamps batch size, and submits the task to `gMetadata->task_manager`; `fs_clone_node()` builds a non-queued `SnapshotTask` and calls `cloneNode()`.

Control flow: snapshot requests enter with `FsContext`, session mode validation, destination directory write validation, and source read validation. After validation, the function asserts master personality, builds a task configured with overwrite and missing-source flags, derives paths for the job description, resolves default/clamped batch size, and submits asynchronously with callback and job id. The clone helper skips submission and invokes immediate clone logic for restore/task internals.

State and persistence behavior: uses `ChecksumUpdater` around `fs_snapshot()`, but most persistent metadata changes occur inside `SnapshotTask` and its changelog/task-manager integration. Batch-size globals are process configuration state.

Dependencies/integration: depends on config, `FsContext`, node operation helpers, quota header, `SnapshotTask`, `TaskManager`, and metadata singleton. It integrates with client snapshot requests and background task processing.

Risks and test signals: destination path construction assumes first-parent paths; batch limit reads from a similarly named config key and can silently clamp caller input. Tests should cover source/destination permission failures, directory ancestor rejection, overwrite/missing flags, default and explicit batch sizes, and callback/job-id submission behavior.
