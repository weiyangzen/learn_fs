# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/check_extents.c

Implements fsck checks for extent ownership, inode sector accounting, overlapping extents across snapshots, stale pointers, and overlarge encoded extents.

Key entry points:
- `bch2_check_extents()` walks the extents btree and validates extent/inode relationships.
- `bch2_check_indirect_extents()` walks the reflink btree for stale pointer and encoded-size checks.
- `check_extent()` performs per-extent snapshot, inode, overlap, past-EOF, overbig encoded extent, stale pointer, commit, and sector-count accounting work.
- `check_i_sectors()` / `check_i_sectors_notnested()` reconcile inode `bi_sectors` against counted allocated extent sectors.
- `check_overlapping_extents()` and `overlapping_extents_found()` detect and repair visible overlapping extents in snapshot-aware order.

Core mechanics:
- `snapshots_seen` records overwrites at a position so visibility of older extents in descendant snapshots can be determined.
- `extent_ends` tracks the latest extent end per snapshot and its snapshot visibility context.
- Overlap repair chooses which visible extent to overwrite, handles extent whiteouts specially, updates compressed-sector reservation accounting, and may force nested transaction restarts.
- Past-EOF extents are punched from the affected snapshot unless they are reservations.
- `bch2_bkey_drop_stale_ptrs()` is called after validation to remove stale physical pointers.
- Sector counts are accumulated only for visible allocated extents and later compared with inode `bi_sectors` unless the inode marks sectors dirty.

Important invariants:
- Extent keys must belong to regular-file or symlink inodes.
- Visible extents for the same inode/snapshot lineage must not overlap.
- Encoded extents should not exceed `encoded_extent_max`.
- Sector accounting must ignore whiteouts and respect snapshot visibility.
- Transaction restarts are handled carefully because post-commit accounting cannot use stale key references.

Filesystem relevance:
- This pass validates the data extent namespace and inode size/sector consistency, central to preventing duplicate logical ownership and stale physical references.
