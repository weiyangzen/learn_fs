# File Research: sources/cow-pools/bcachefs-tools/fs/fs/check.c

## Purpose

Implements the core bcachefs fsck metadata passes for root, inodes, dirents, xattrs, unreachable inodes, reflink padding migration, and online/offline fsck ioctls. It also provides shared snapshot-visibility and inode-walking helpers used by specialized check files.

## Main Interfaces

- Repair/message helpers: `bch2_dirent_inode_mismatch_msg()`, `bch2_reattach_inode()`, `bch2_fsck_update_backpointers()`.
- Snapshot helpers: `bch2_snapshots_seen_update()`, `bch2_key_visible_in_snapshot()`, `bch2_ref_visible()`, `bch2_ref_visible2()`.
- Inode walker: `bch2_walk_inode()`.
- Passes: `bch2_check_inodes()`, `bch2_check_unreachable_inodes()`, `bch2_check_dirents()`, `bch2_check_xattrs()`, `bch2_check_root()`, `bch2_fix_reflink_p()`.
- Fsck status/ioctl helpers: `bch2_fs_fsck_errcode()`, `bch2_ioctl_fsck_offline()`, `bch2_ioctl_fsck_online()`.

## Behavior

The file reconstructs or repairs filesystem namespace relationships. It can create `lost+found`, find or reconstruct subvolumes, reconstruct missing inodes from extents/dirents/xattrs, repair inode hash info, clear or update bad dirent backpointers, correct child-snapshot flags, handle unlinked inode/deleted-inode state, repair subvolume parent links, and remove bad dirents.

Snapshot visibility is tracked with `struct snapshots_seen`; this determines whether an older key remains visible after newer overwrites. `struct inode_walker` gathers all inode versions or visible inode versions for a given inode number, plus whiteouts/deletes, so dirent/xattr/extent passes can validate keys against the right snapshot-visible inode.

`bch2_check_inodes()` validates inode self-consistency, parent dirents, unlink state, directory sizes, child snapshot flags, subvolume references, and journal sequence bounds. `bch2_check_unreachable_inodes()` reattaches non-unlinked inodes without valid backpointers to `lost+found`. `bch2_check_dirents()` validates directory keys against directory inodes, hash correctness, target inodes/subvolumes, overwritten inode snapshots, and subdirectory nlink counts; it may require a second pass after hash repairs. `bch2_check_xattrs()` validates xattr ownership and hash placement. `bch2_check_root()` creates missing root subvolume/inode. `bch2_fix_reflink_p()` clears old reflink padding fields before the metadata-version fix.

## State And Side Effects

Fsck passes modify btrees transactionally: create inodes and subvolumes, insert/delete dirents, write inode updates, add whiteouts, update subvolume trees, and schedule transaction restarts after structural changes. Online fsck temporarily adjusts fsck options, stdio routing, and `BCH_FS_in_fsck`.

## Dependencies

Depends on btree transactions/updates/cache, dirent/namei/xattr/inode helpers, init recovery/progress/pass machinery, snapshots/subvolumes, VFS declarations, darrays, thread-with-stdio, ioctl structs, and user-copy/capability checks when chardev support is enabled.

## Risks And Notes

This file is deeply snapshot-aware. Most repairs must choose whether to update the current snapshot, an ancestor, a descendant, or insert whiteouts. Several repair paths return transaction restart errors intentionally after committing changes. Online fsck is constrained to passes marked online-capable; offline fsck opens devices read-only through a stdio thread.
