# File Research: sources/cow-pools/bcachefs-tools/fs/fs/check_extents.c

## Purpose

Implements fsck passes for extent ownership, extent overlap, inode sector counts, stale pointer removal, encoded extent size diagnostics, and indirect reflink extents.

## Main Interfaces

- `bch2_check_extents(struct bch_fs *c)`.
- `bch2_check_indirect_extents(struct bch_fs *c)`.

## Behavior

The extent pass walks `BTREE_ID_extents` across all snapshots, uses `inode_walker` to validate that each extent belongs to a visible regular-file or symlink inode, and accumulates allocated sectors to check `bi_sectors`.

`extent_ends` tracks the latest visible extent ends per snapshot. `check_overlapping_extents()` compares each extent against visible prior ends and, when overlapping extents are found, chooses which extent to overwrite or convert from `extent_whiteout` to `whiteout`. It updates snapshot visibility state so scanning can continue after repairs.

The pass also detects extents past inode size and punches them out, warns about encoded extents larger than the current maximum, and drops stale pointers. After each commit, visible allocation extents contribute to inode sector counts. At inode boundaries, `check_i_sectors()` recomputes and repairs inode sector totals unless marked dirty.

The indirect extent pass walks `BTREE_ID_reflink`, checks encoded size, and drops stale pointers.

## State And Side Effects

Can overwrite/delete extents, punch ranges, update inode `bi_sectors`, drop stale extent pointers, consume disk reservations, and trigger transaction restarts.

## Dependencies

Uses bucket/extent/io helpers, inode walker and snapshot visibility from `check.h`, name/path formatting, progress reporting, disk reservations, and btree extent update APIs.

## Risks And Notes

Overlap repair is snapshot-sensitive and must distinguish same-snapshot overwrite, ancestor/descendant visibility, and extent whiteouts. The code notes older non-nested restart behavior in sector counting, making restart boundaries important.
