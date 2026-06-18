<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_inode.c -->
# sources/distributed-fs/ceph-client/fs/9p/vfs_inode.c

## Purpose
`vfs_inode.c` implements legacy and 9P2000.u inode operations, mode/stat conversion, inode allocation/eviction, create/lookup/remove/rename, getattr/setattr, symlink, hardlink, and special-file handling.

## Important APIs, types, and functions
Exports include `v9fs_alloc_inode`, `v9fs_free_inode`, `v9fs_set_netfs_context`, `v9fs_init_inode`, `v9fs_evict_inode`, `v9fs_inode_from_fid`, `v9fs_uflags2omode`, `v9fs_blank_wstat`, `v9fs_stat2inode`, `v9fs_refresh_inode`, `v9fs_vfs_unlink`, `v9fs_vfs_rmdir`, and `v9fs_vfs_rename`.

## Control flow
Stat data is converted into Linux inode fields and qid-indexed through `iget5_locked`. Lookup walks from the parent fid and instantiates cached or new inodes depending on metadata caching. Create clones a parent fid, issues `fcreate`, walks back to get an unopened fid, and instantiates the dentry. Remove uses dotl unlinkat when available, then path-based remove fallback. Rename prefers dotl operations and otherwise uses legacy wstat within `rename_sem`.

## State and persistence
Runtime state includes qid/inode associations, inode cache-validity flags, nlink adjustments, page-cache/netfs state, and dentry fids. Persistent metadata changes are sent to the server through wstat/fcreate/remove.

## Dependencies and integration points
It depends on VFS inode operations, p9 stat/wstat/walk/create/remove RPCs, fid management, netfs, FS-Cache, xattr/ACL hooks for dotl tables, and session protocol flags.

## Risks and test signals
Risks include stale inode reuse by qid/version, type changes, rename races, legacy protocol feature gaps, size truncation cache sync, and special-device extension parsing. Test signals include lookup/create/atomic open, unlink/rmdir, cross-directory rename, symlink/hardlink/mknod on dotu, getattr/setattr under cache modes, and inode eviction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_inode.c -->
