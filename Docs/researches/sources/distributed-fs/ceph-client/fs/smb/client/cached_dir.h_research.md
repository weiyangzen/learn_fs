<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cached_dir.h -->
## sources/distributed-fs/ceph-client/fs/smb/client/cached_dir.h

Purpose: declares cached directory handle and cached dirent data structures plus the public API used by the SMB client directory, inode, reconnect, and debug paths.

Important types: `struct cached_dirent` stores a cached name, position, and attributes. `struct cached_dirents` tracks validity/failure flags, the file instance associated with the cache, mutex, expected position, entry list, and accounting. `struct cached_fid` represents one cached open directory handle with lease/open/list state, path, refcount, SMB fid, tcon, dentry, work items, dirents, and trailing `smb2_file_all_info`. `struct cached_fids` is the per-tcon cache container with spinlock, active/dying lists, laundromat work, and aggregate counters.

Control flow: callers allocate per-tcon caches with `init_cached_dirs()`, use `open_cached_dir()` or `open_cached_dir_by_dentry()` to obtain referenced handles, release with `close_cached_dir()`, and invalidate via name, tcon, superblock, or lease-key APIs. `is_valid_cached_dir()` defines a reusable entry as one with both timestamp and lease.

State and persistence: all structures are in-memory mount/session state. Accounting exists per tcon and module-wide through `cifs_dircache_bytes_used`.

Dependencies and integration: depends on CIFS core types, list heads, workqueues, krefs, dentries, SMB2 fid/file-info types, and cifs superblock/tcon abstractions.

Risks: bitfield lease/open/list state must match implementation invariants in `cached_dir.c`. The flexible-array-containing `file_all_info` must remain last. Consumers must respect that `close_cached_dir()` cannot be called with `cfid_list_lock` held.

Test signals: compile users with and without handle cache, verify structure initialization and accounting, lockdep for API misuse, and lease validity transitions across open, lease break, reconnect, and timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cached_dir.h -->
