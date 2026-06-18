# sources/distributed-fs/ceph-client/fs/afs/inode.c

Purpose: `inode.c` manages AFS inode creation, status application, callback promises, symlink content, root inode setup, getattr/setattr, cache cookies, and inode eviction.

Important APIs and functions: public functions include `afs_init_new_symlink()`, `afs_get_link()`, `afs_readlink()`, `afs_vnode_commit_status()`, `afs_fetch_status()`, `afs_ilookup5_test_by_fid()`, `afs_iget()`, `afs_root_iget()`, `afs_getattr()`, `afs_drop_inode()`, `afs_evict_inode()`, and `afs_setattr()`. Internals include status initialization/application, callback application, cache acquisition, and setattr completion hooks.

Control flow: new inodes are created with `iget5_locked()` keyed by vnode/unique. `afs_inode_init_from_status()` copies server status, selects file/dir/symlink/mountpoint operations, initializes netfs context, size, i_version, callback state, and permits. Existing inodes use `afs_vnode_commit_status()`, which handles deleted-vnode inline errors, speculative bulk-status suppression, normal status/callback application, unlink nlink drops, and permit caching. Symlink reads lazily validate and read the blob into `vnode->directory`. Setattr serializes under `validate_lock`, waits for conflicting writes around truncation, optimizes local-only shrink above remote size, or issues StoreStatus/StoreData and resizes pagecache/netfs/fscache.

State and persistence: vnode status mirrors fileserver metadata. Inode i_version tracks AFS data version. `invalid_before`, `AFS_VNODE_ZAP_DATA`, `AFS_VNODE_DIR_VALID`, `AFS_VNODE_DELETED`, callback locks, and fscache cookies govern local cache validity. Symlink and directory blobs share the folio queue buffer.

Dependencies and integration points: consumes status replies from `fsclient.c`, uses `fs_operation.c`, netfs/fscache, VFS inode/symlink operations, directory operations, mountpoint handling, callback breaking, permits, and writeback/pagecache helpers.

Risks: speculative bulk status must not regress data versions during local modification. Type changes are protocol errors. Directory data-version jumps must invalidate directory blobs; regular file jumps set zap-data. RCU symlink pathwalk cannot sleep. Setattr truncate ordering must preserve dirty data and cache size consistency.

Test signals: instantiate all vnode types, fetch status new/existing, speculative bulk status during modification, deleted aborts, symlink RCU/non-RCU reads, root inode setup, getattr after silly delete and directory size override, eviction of dirty dir/symlink blobs, and setattr mode/owner/time/size paths.
