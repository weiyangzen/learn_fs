# sources/distributed-fs/ceph-client/fs/nilfs2/namei.c

## Purpose

`namei.c` implements NILFS2 pathname and directory inode operations plus NFS export file-handle support. It adapts conventional ext2-style directory manipulation to NILFS2's transactional, log-structured update model: every mutating namespace operation begins a NILFS transaction, updates directory entries and inode link counts, marks affected inodes dirty, then commits or aborts the transaction.

## Important APIs, Types, and Functions

The directory operation implementations are `nilfs_lookup()`, `nilfs_create()`, `nilfs_mknod()`, `nilfs_symlink()`, `nilfs_link()`, `nilfs_mkdir()`, `nilfs_unlink()`, `nilfs_rmdir()`, and `nilfs_rename()`. `nilfs_add_nondir()` is a helper for new non-directory objects that either instantiates the dentry or unwinds link count and new-inode state.

Export helpers are `nilfs_get_parent()`, `nilfs_get_dentry()`, `nilfs_fh_to_dentry()`, `nilfs_fh_to_parent()`, and `nilfs_encode_fh()`. They preserve both inode number and NILFS checkpoint number (`root->cno`) in `struct nilfs_fid`, which matters because snapshots expose historical trees.

The file exports `nilfs_dir_inode_operations`, `nilfs_special_inode_operations`, `nilfs_symlink_inode_operations`, and `nilfs_export_ops`.

## Control Flow

Lookup rejects names longer than `NILFS_NAME_LEN`, asks `nilfs_inode_by_name()` for an inode number, and loads that inode from the directory's root object via `nilfs_iget()`. A stale deleted inode reference is promoted to a filesystem error signal and returns `-EIO`.

Creation, mknod, symlink, link, mkdir, unlink, rmdir, and rename all wrap their changes in `nilfs_transaction_begin()` and `nilfs_transaction_commit()` or `nilfs_transaction_abort()`. New files set inode operation/file operation/address-space operation tables before insertion. Directory creation increments the parent link count, initializes `.` and `..`, links the child, then commits. Failure paths carefully drop link counts, dirty inodes that had link changes, unlock new inodes, and `iput()` abandoned objects.

Unlink looks up the directory entry, verifies that it points to the expected inode number, deletes the entry, drops the target link count, and marks both directory and target dirty. Rmdir adds an empty-directory check and drops both child and parent directory links. Rename supports only `RENAME_NOREPLACE`; it handles overwrite, cross-directory directory moves by rewriting `..`, ctime changes, and all relevant link-count transitions.

NFS export decoding looks up the checkpoint root with `nilfs_lookup_root()`, loads the inode, checks generation when provided, and returns aliases through the VFS dentry helpers.

## State and Persistence Behavior

Namespace persistence is checkpointed by NILFS log construction after transactions mark directories and inodes dirty. Link counts, ctime, directory entries, symlink page contents, and root/checkpoint file handles are all represented in normal inode and directory metadata and become durable through later segment construction.

`nilfs_encode_fh()` includes `root->cno`, so file handles can refer to snapshot roots rather than only the mutable current tree. This is a NILFS-specific persistence detail for exportability across checkpoints.

## Dependencies and Integration Points

The file depends on directory helpers from `dir.c`, inode allocation/loading from `inode.c`, transaction APIs from `segment.c`, file/address-space operation tables, file attribute and fiemap handlers, and `export.h`'s NILFS file-handle layout. It integrates directly with the VFS inode operation and export operation tables.

## Risks and Edge Cases

Rename is the highest-risk path because it combines old-entry deletion, optional new-entry replacement, directory `..` updates, and link-count corrections. Any missed dirty mark can defer or lose metadata updates in the log. `nilfs_do_unlink()` repairs a zero-link target by resetting it to one before dropping the link, but that also signals prior metadata inconsistency. Snapshot file-handle decoding must reject invalid system inode numbers and stale generations to avoid exposing wrong historical objects.

## Test Signals

Test signals include create/link/unlink/mkdir/rmdir/symlink/mknod under crash-recovery workloads, cross-directory rename of directories, rename over files and empty directories, unsupported rename flags, long names, stale directory entries, and NFS export encode/decode for current and snapshot checkpoints. Transaction abort fault injection should verify link counts and dentries are unwound.
