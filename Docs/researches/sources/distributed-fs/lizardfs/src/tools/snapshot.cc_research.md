# sources/distributed-fs/lizardfs/src/tools/snapshot.cc

Purpose: Implements `lizardfs makesnapshot`, creating lazy-copy snapshots for one or more sources into a destination.

Important APIs/types/functions: `snapshot_run`; static `snapshot`; static `make_snapshot`; `cltoma::requestTaskId`; `cltoma::snapshot`; `matocl::snapshot`; `signalHandler`; options `-o`, `-f`, `-l` and internal batch/ignore-missing support.

Control flow: The outer `snapshot` function resolves source/destination combinations, validates same device, handles existing/non-existing destinations and directory targets, and calls `make_snapshot`. `make_snapshot` opens destination directory read-write, requests a task id, starts cancellation signal handling, sends the snapshot request with source inode, destination inode/name, uid/gid, overwrite and batching flags, and waits for status.

State and persistence: Mutates namespace and metadata by creating snapshots. Maintains transient task id and signal thread state.

Dependencies and integration: Uses `cltoma`/`matocl`, `ServerConnection`, `MooseFsString`, common path helpers, and master connection logic. Integrates with master async task system.

Risks and test signals: High impact command; path resolution, symlink handling, overwrite semantics, and same-device checks are critical. Cancellation relies on signal masking and thread cleanup. No direct tests in this subset.
