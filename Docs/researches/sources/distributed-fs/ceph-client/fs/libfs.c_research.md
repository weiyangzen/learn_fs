# sources/distributed-fs/ceph-client/fs/libfs.c

## Purpose

`sources/distributed-fs/ceph-client/fs/libfs.c` is a broad library of VFS helpers for simple, pseudo, in-memory, exportable, casefolded, encrypted, and special-purpose filesystems. It provides directory iteration helpers, offset-stable directory maps, simple inode operations, ramfs-like address-space operations, pseudo filesystem setup, buffer/transaction/attribute helpers, export file-handle helpers, fsync helpers, inode version helpers, direct-I/O fallback handling, stashed anonymous dentries, and simple create helpers. The source was read as a complete 2314-line file.

## Important APIs, Types, and Functions

Important exported families include `simple_getattr`, `simple_statfs`, `simple_lookup`, `simple_dir_operations`, `simple_offset_*`, `simple_recursive_removal`, `init_pseudo`, `simple_open`, `simple_link`, `simple_unlink`, `simple_rmdir`, `simple_rename`, `simple_setattr`, `ram_aops`, `simple_fill_super`, `simple_pin_fs`, `simple_read_from_buffer`, `simple_write_to_buffer`, `simple_transaction_*`, `simple_attr_*`, `generic_encode_ino32_fh`, `generic_fh_to_dentry`, `generic_fh_to_parent`, `simple_fsync`, `noop_fsync`, `alloc_anon_inode`, `simple_symlink_inode_operations`, empty-directory helpers, `generic_ci_*`, `generic_set_sb_d_ops`, `inode_maybe_inc_iversion`, `inode_query_iversion`, `direct_write_fallback`, `simple_inode_init_ts`, `path_from_stashed`, `stashed_dentry_prune`, `simple_start_creating`, and `simple_done_creating`.

## Control Flow

Directory helpers either iterate positive dentries directly with a cursor (`dcache_readdir`) or preserve stable offsets through a maple-tree-backed `offset_ctx`. Simple create/remove/rename helpers update ctime/mtime/link counts and leave actual dentry mutation to the caller or VFS path. `ram_aops` zero-fills missing folios and keeps data in page cache without writeback. Pseudo filesystem setup creates anonymous nodev superblocks and a root inode. Buffer helpers enforce bounds and advance positions after user/kernel copies. Transaction helpers allow one write per open followed by readback from a per-file page. Casefold helpers integrate Unicode and fscrypt-aware name matching. Stashed dentry helpers reuse anonymous dentries for namespace/pid-style files.

## State and Persistence Behavior

Most state is caller-owned. The offset directory API stores long offsets in `dentry->d_fsdata` and the dentry pointer map in a maple tree. Simple transaction state lives in one allocated page at `file->private_data`. Simple attrs allocate per-open buffers and callbacks. Pinned pseudo filesystems share a global spinlock-protected mount pointer and refcount. Inode version helpers mutate the atomic `i_version` queried bit and counter. Stashed dentry helpers atomically publish/reuse dentries through caller-provided storage.

## Dependencies and Integration Points

The file is a core integration point for many filesystems, including kernfs via `ram_aops`, `simple_inode_init_ts`, `simple_statfs`, `noop_fsync`, and `kfree_link`. It depends on VFS dcache/inode/file APIs, maple tree, exportfs, fsnotify, fscrypt, Unicode, writeback, block flush, user access, pidfs/nsfs-style stashed operations, and pseudo fs_context support.

## Risks and Edge Cases

Directory cursor and offset-map helpers are sensitive to dentry locking and removal races. `simple_setattr` is unsuitable for real persistent size changes without filesystem-specific work. `simple_write_end` intentionally does not mark inode dirty for size changes. Transaction files reject multiple writes per open. Direct-write fallback must write back and invalidate buffered pages to preserve O_DIRECT expectations. i_version barriers must pair correctly between query and increment paths. Stashed dentry storage must be cleared on prune or stale dentries can be reused incorrectly.

## Test Signals

Coverage should include libfs selftests through ramfs/debugfs/configfs/sysfs users, directory seek/readdir stability with concurrent create/delete/rename, maple-tree offset rename and exchange tests, simple_attr read/write parse tests, transaction error paths, exportfs handle round trips, fsync/writeback error propagation, Unicode/fscrypt lookup tests, inode i_version concurrency tests, direct-I/O fallback tests, and stashed dentry lifecycle tests with prune and reuse.
