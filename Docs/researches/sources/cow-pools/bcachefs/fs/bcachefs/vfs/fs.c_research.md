# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/fs.c

Implements the main bcachefs VFS bridge: inode cache lifecycle, inode btree synchronization, namespace operations, file/directory/symlink operation tables, export/NFS handles, mount/reconfigure plumbing, superblock operations, and per-filesystem VFS resource initialization.

Key entry points:
- `bch2_vfs_inode_get()` / `bch2_vfs_inode_get_trans()` locate or instantiate VFS inodes from `(subvol, inum)` btree inode records.
- `__bch2_create()` creates regular files, directories, device nodes, tmpfiles, subvolumes, and snapshots through common inode/dirent transaction logic.
- `bch2_lookup()`, `bch2_link()`, `__bch2_unlink()`, `bch2_symlink()`, `bch2_rename2()`, `bch2_tmpfile()`, and `bch2_vfs_readdir()` implement core inode and directory operations.
- `bch2_setattr()`, `bch2_setattr_nonsize()`, `bch2_getattr()`, `bch2_fileattr_get()`, and `bch2_fileattr_set()` translate VFS stat/attribute requests into bcachefs inode updates.
- `bch2_encode_fh()`, `bch2_fh_to_dentry()`, `bch2_fh_to_parent()`, `bch2_get_parent()`, and `bch2_get_name()` provide export operations for NFS/file handles.
- `bch2_fs_get_tree()`, `bch2_fs_parse_param()`, `bch2_fs_reconfigure()`, and `bch2_kill_sb()` implement the Linux filesystem type mount lifecycle.
- `bch2_fs_vfs_init()`, `bch2_fs_vfs_init_rw()`, `bch2_fs_vfs_exit()`, `bch2_vfs_init()`, and `bch2_vfs_exit()` allocate and release VFS-wide tables, biosets, mempools, workqueues, inode cache, and filesystem registration.

Core mechanics:
- `bch2_inode_update_after_write()` is the central synchronization point from `struct bch_inode_unpacked` to `struct inode` and `struct bch_inode_info`, updating nlink, uid/gid, mode, size, times, cached inode copy, and VFS flags.
- `bch2_write_inode()` wraps inode btree mutation in a transaction, detects reconcile option changes, writes the inode key, commits, updates the VFS inode while the btree node lock still protects `ei_inode`, and wakes reconcile work if needed.
- VFS inodes are tracked in both a full `(subvol, inum)` `rhashtable` and an inum-only `rhltable`; the latter supports snapshot/open-inode checks.
- `bch2_inode_hash_find()` handles races with `I_FREEING`/`I_WILL_FREE` by waiting on the inode bit waitqueue, dropping btree locks when called from a transaction.
- `bch2_inode_hash_insert()` handles duplicate-cache races by discarding the newly allocated inode and returning the already-cached inode.
- Namespace mutations update btree metadata first, then refresh affected VFS inodes and dentry state. Casefolded negative dentries are intentionally not cached.
- Project quota changes are pre-transferred before updates and rolled back when the btree commit fails.
- Mount setup parses device lists, deduplicates already-mounted device sets, opens/starts the filesystem, configures the superblock, initializes root inode/dentry, and maps read-only recovery cases to user-visible errors carefully.

Important invariants:
- `ei_update_lock` serializes in-memory inode updates with btree inode writes; multi-inode operations use sorted locking via `bch2_lock_inodes()` to avoid deadlocks.
- VFS inode cache insertion occurs before transaction exit for newly created inodes to prevent another thread from importing and modifying the same on-disk inode first.
- Inodes in snapshot subvolumes are flagged with `EI_INODE_SNAPSHOT` and excluded from normal quota accounting paths.
- `bch2_evict_inode()` removes non-deleted inodes from VFS hashes before final pagecache teardown, but keeps deleting inodes visible until fsck/open-inode checks can observe them.
- Mount reconfiguration uses `state_lock` and filesystem read-only/read-write transitions, and synchronous conversion to read-only flushes the filesystem first.
- Address-space operations are installed for all VFS inodes; regular files receive bcachefs file ops, directories directory ops, symlinks page-backed link ops, and special files `init_special_inode()`.

Filesystem relevance:
- This file is the Linux VFS personality of bcachefs. It turns bcachefs transactional inode, dirent, quota, subvolume, snapshot, xattr, and journal machinery into normal Linux filesystem semantics.

Notable risks:
- Inode-cache races are delicate because bcachefs does not use `I_NEW` for normal lookup insertion; compatibility with VFS discard paths is handled explicitly.
- Several comments call out deadlock hazards around eviction-time btree reads and lookup/check repair commits.
- Freeze support relies on internal write references instead of full VFS internal-write freeze integration.
