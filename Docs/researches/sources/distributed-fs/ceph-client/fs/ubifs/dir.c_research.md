# sources/distributed-fs/ceph-client/fs/ubifs/dir.c

## Purpose
`dir.c` implements UBIFS VFS directory and namespace operations: inode creation, lookup, readdir, link/unlink, mkdir/rmdir, mknod, symlink, tmpfile, rename/exchange/whiteout, directory open/seek/release, and stat attribute reporting. It also enforces UBIFS budgeting and journaling rules for metadata changes.

## Important APIs, Types, and Functions
- `inherit_flags()` and `ubifs_new_inode()` initialize UBIFS inode state, compression defaults, fscrypt context, orphan protection, and VFS operations.
- Lookup/create helpers: `dbg_check_name()`, `ubifs_lookup()`, `ubifs_prepare_create()`, and `ubifs_create()`.
- Directory iteration state: `struct ubifs_dir_data`, `ubifs_dir_open()`, `ubifs_dir_llseek()`, `ubifs_readdir()`, and `ubifs_dir_release()`.
- Namespace mutators: `ubifs_link()`, `ubifs_unlink()`, `ubifs_check_dir_empty()`, `ubifs_rmdir()`, `ubifs_mkdir()`, `ubifs_mknod()`, `ubifs_symlink()`, `ubifs_tmpfile()`, `do_rename()`, `ubifs_xrename()`, and `ubifs_rename()`.
- Exported operation tables: `ubifs_dir_inode_operations` and `ubifs_dir_operations`.
- `ubifs_getattr()` maps UBIFS inode flags and size/block accounting into `kstat`.

## Control Flow
Creation paths first budget space, prepare fscrypt names, allocate a new inode, initialize security/xattrs, update link counts and parent directory size under UBIFS inode mutexes, then journal the combined directory/inode update through `ubifs_jnl_update()`. New non-xattr inodes start with zero nlink and an orphan record so a power cut before dentry journaling does not leave an unreachable live inode.

Lookup prepares fscrypt lookup state, handles no-key encrypted names via hash lookup, reads dent nodes from the TNC, validates debug names when enabled, instantiates the target inode, and verifies encrypted child context compatibility for directories and symlinks.

`ubifs_readdir()` maps directory offsets to UBIFS name hashes. Because key hash collisions prevent full Unix seekdir/telldir semantics, it stores the last full dent node in `file->private_data` and uses a cookie to detect seeks. It emits dots, then iterates with `ubifs_tnc_next_ent()`, decrypting names for encrypted directories.

Deletion paths attempt to budget but continue on `-ENOSPC` for unlink/rmdir because UBIFS reserves deletion space. They purge xattrs, update nlink and directory size, journal deletion, and clear no-space flags when deletion succeeded without a normal budget.

Rename is the most complex path. It budgets dent deletion/creation, dirty inode updates, optional whiteout creation, and dirty old-inode writeback separately. It locks involved UBIFS inodes through `lock_4_inodes()`, adjusts directory sizes and link counts, journals the atomic rename or exchange, then marks the moved inode dirty for ctime persistence.

## State and Persistence Behavior
All namespace mutations journal affected inodes and dent nodes immediately rather than relying on delayed dirty inode writeback, simplifying recovery. Directory `i_size`/`ui_size`, link counts, orphan list state, fscrypt contexts, xattrs, special-device encoded data, symlink inline data, and dent nodes are persistent effects. Rename may leave the moved inode dirty for later ctime writeback, but the namespace operation itself is journaled atomically.

## Dependencies and Integration Points
This file integrates with VFS inode/file operation tables, TNC dent lookup/iteration, journal update/rename/xrename functions, budgeting, orphan handling, fscrypt, security initialization, xattr purge/listing, ioctl/fileattr helpers, and file operations from `file.c`. `crypto.c` depends on `ubifs_check_dir_empty()` for fscrypt policy behavior.

## Risks and Edge Cases
- Directory offsets are hash based, so NFS-style stable arbitrary seekdir/telldir is explicitly unsupported.
- Error paths must reverse size and nlink updates exactly; rename/whiteout paths have many separate budget and inode-state rollback cases.
- New inode orphan handling is essential for power-cut safety; creation callers must set nlink and journal linking in the expected sequence.
- Encrypted no-key lookups use hashes and minor hashes, so name preparation and validation are critical.
- Unlink/rmdir continuing after `-ENOSPC` depends on reserved deletion space and correct clearing of no-space flags.

## Test Signals
High-value tests include encrypted and unencrypted lookup/readdir, hash-collision directory entries, create/unlink/rmdir under low-space conditions, power cuts between inode creation and dentry journaling, rename over files/directories, `RENAME_EXCHANGE`, `RENAME_WHITEOUT`, tmpfile creation, symlink encryption, and stat attributes for UBIFS flags.
