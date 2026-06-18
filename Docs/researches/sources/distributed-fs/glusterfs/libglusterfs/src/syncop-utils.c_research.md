# sources/distributed-fs/glusterfs/libglusterfs/src/syncop-utils.c

## Purpose

`syncop-utils.c` builds higher-level directory traversal, locality, GFID-to-path, and inode lookup helpers on top of the synchronous FOP wrappers from `syncop.c`. It supports recursive walks, throttled walks, multithreaded directory scans, protocol/client locality checks, and inode resolution by GFID.

## Important APIs, Types, and Functions

Important APIs are `syncop_dirfd()`, `syncop_ftw()`, `syncop_ftw_throttle()`, `syncop_mt_dir_scan()`, `syncop_dir_scan()`, `syncop_is_subvol_local()`, `syncop_gfid_to_path_hard()`, `syncop_gfid_to_path()`, and `syncop_inode_find()`. The internal `struct syncop_dir_scan_data` carries subvolume, parent loc, queue pointers, condition/mutex pointers, callback, running job counts, queue length, and accumulated retval for multithreaded scan workers.

## Control Flow and Data Flow

`syncop_dirfd()` creates an fd for a directory inode, calls `syncop_opendir()`, binds it on success, and on Linux falls back to `fd_anonymous()` for backward compatibility when opendir fails against older bricks. `syncop_ftw()` opens the directory, loops through `syncop_readdirp()` batches, skips `.` and `..`, links inodes from dirents, invokes the callback, and recursively descends into directories. `syncop_ftw_throttle()` adds sleep after a configurable number of entries, falling back to `syncop_ftw()` when throttling is disabled.

`syncop_mt_dir_scan()` uses `syncop_readdir()` and a bounded queue to run file callbacks in separate synctasks up to `max_jobs`, while directories are processed synchronously. Worker synctasks pop queued entries under a pthread mutex, run the callback, free dirents, update `retval`, decrement running counts, and signal queue space or completion. The function refuses to run from inside an existing synctask because its pthread condition waits would block the sync scheduler model.

Locality and lookup helpers use xattrs and inode tables: `syncop_is_subvol_local()` fetches `GF_XATTR_PATHINFO_KEY` from a protocol/client translator and parses pathinfo; `syncop_gfid_to_path_hard()` resolves a GFID through `GFID_TO_PATH_KEY` or `GFID2PATH_VIRT_XATTR_KEY`; `syncop_inode_find()` first checks the inode table, then performs a lookup by GFID and links the inode.

## State and Persistence Behavior

Traversal state is transient: fds, offsets, dirent lists, queue length, running job counts, and callback return aggregation. `syncop_gfid_to_path_hard()` may fetch on-disk virtual xattr path state when `hard_resolve` is true, but it does not persist new state. Inode lookup can populate the in-memory inode table through `inode_link()`.

## Dependencies and Integration Points

The file depends on `syncop.c` wrappers, inode/fd helpers, dirent utilities, pthread primitives, synctask creation, xattr dictionary helpers, pathinfo parsing, and translator cleanup flags. It integrates with self-heal, rebalance, scrub, and management workflows that need synchronous traversal over translator subvolumes.

## Risks and Edge Cases

Linux-only anonymous-fd fallback intentionally violates strict directory offset portability assumptions and is disabled elsewhere. `syncop_ftw_throttle()` continues after callback errors in some paths where `syncop_ftw()` breaks, so callers must understand return aggregation differences. `syncop_mt_dir_scan()` can leave queued entries to cleanup on early exit and relies on waiting for all jobs before freeing shared queues. It returns `ret | retval`, which can combine negative errno-style values with callback bitmasks. Locality checks require a protocol/client translator and a valid pathinfo xattr.

## Test Signals

Tests should cover empty directories, `.`/`..` filtering, recursive directory descent, callback failure behavior, throttling sleep cadence, Linux opendir fallback, multithreaded queue limits and cleanup-starting exits, xdata pass-through, locality true/false parsing, hard and soft GFID path resolution, and inode table cache-hit versus lookup paths.
