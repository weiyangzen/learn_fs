<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cached_dir.c -->
## sources/distributed-fs/ceph-client/fs/smb/client/cached_dir.c

Purpose: manages cached SMB directory handles and cached directory entries for the CIFS client. Cached fids reduce repeated directory opens when leases allow handle reuse, and are invalidated on lease breaks, reconnects, timeout, or explicit debug/proc actions.

Important APIs: external functions include `init_cached_dirs()`, `free_cached_dirs()`, `open_cached_dir()`, `open_cached_dir_by_dentry()`, `close_cached_dir()`, `drop_cached_dir_by_name()`, `close_all_cached_dirs()`, `invalidate_all_cached_dirs()`, and `cached_dir_lease_break()`. Key internals include `find_or_create_cached_dir()`, `path_to_dentry()`, `path_no_prefix()`, `smb2_close_cached_fid()`, and `cfids_laundromat_worker()`.

Control flow: `open_cached_dir()` converts the path to UTF-16, finds or creates a `cached_fid` under `cfid_list_lock`, resolves a dentry, optionally copies a parent lease key, issues a compounded SMB2 create plus query-info request, validates a lease with read caching, stores `file_all_info`, timestamps the cache entry, and returns a referenced cfid. Lease breaks remove entries from the active list, clear lease state, and queue work to drop dentries and close server handles. The laundromat periodically moves expired or dying entries to a local list and closes them asynchronously.

State and persistence: state is per tree connection in `struct cached_fids`: active and dying lists, entry count, delayed work, and aggregate dirent counters. Each `cached_fid` holds path, dentry, fid, lease state, timestamps, refcount, close/put work, optional file-all-info, and cached dirent list/accounting. Nothing persists beyond mount lifetime.

Dependencies and integration: integrates with SMB2 create/query/close, lease keys, DFS prefix paths, dcache, tcon refcounting, workqueues (`cfid_put_wq`, `serverclose_wq`), debug tracing, and global directory-cache accounting.

Risks: lock ordering and refcount invariants are central. `close_cached_dir_locked()` assumes at least two references when called under the spinlock. Error paths must remove half-constructed entries and close any lease/open references. Prefix-path and dentry reconstruction can fail after DFS failover. Workqueue close paths must hold tcon references long enough to close on the server.

Test signals: cache hit and lookup-only miss, max cached dirs, create/query compound failure, replayable errors, lease break during construction, parent lease key propagation, invalidation on reconnect, laundromat timeout, unmount dentry dropping, directory-cache accounting decrement, encrypted shares, DFS prefix paths, and explicit open_dirs proc cache drop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cached_dir.c -->
