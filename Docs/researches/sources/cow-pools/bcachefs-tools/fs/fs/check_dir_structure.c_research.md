# File Research: sources/cow-pools/bcachefs-tools/fs/fs/check_dir_structure.c

## Purpose

Implements fsck passes for subvolume path structure and directory-loop detection.

## Main Interfaces

- `bch2_check_subvolume_structure(struct bch_fs *c)`.
- `bch2_check_directory_structure(struct bch_fs *c)`.

## Behavior

Subvolume checking walks each subvolume’s `fs_path_parent` chain back to `BCACHEFS_ROOT_SUBVOL`, detects missing parents and loops, and repairs by removing the existing backpointer/dirent and reattaching the subvolume root through `bch2_reattach_inode()`.

Directory structure checking walks parent backpointers from each live directory toward a subvolume root. It detects missing parent dirents, parent lookup failures, and loops. On loops, it removes the offending backpointer dirent and reattaches the inode. It also repairs `bi_depth` along the traversed path when parent depths are inconsistent.

## State And Side Effects

Can delete dirents, reattach inodes under `lost+found`, and rewrite inode `bi_depth` values. Uses btree transactions with commit/restart handling.

## Dependencies

Uses `fs/check.h`, `fs/namei.h`, progress reporting, dirent lookup/removal, subvolume lookup, and inode find/write helpers.

## Risks And Notes

This pass assumes previous inode/dirent checks have already repaired basic backpointer validity. It focuses on graph-level correctness: no unreachable subvolumes and no directory cycles.
