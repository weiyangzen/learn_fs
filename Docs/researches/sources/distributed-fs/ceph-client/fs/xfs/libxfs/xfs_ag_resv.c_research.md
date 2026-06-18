# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ag_resv.c

## Purpose
This file implements per-AG block reservations that keep space available for metadata btree growth, especially refcount and rmap btrees. It uses in-core reservation counters plus global free-block accounting adjustments to virtually withhold blocks rather than writing explicit reservation metadata to disk.

## Important APIs and Functions
- `xfs_ag_resv_critical` reports low-reservation conditions based on remaining availability below 10 percent, below max btree height, or injected error tags.
- `xfs_ag_resv_needed` computes how many reserved blocks must remain unavailable to a given allocation type.
- `xfs_ag_resv_free` and `__xfs_ag_resv_free` return hidden blocks to fdblocks and reset reservation counters.
- `__xfs_ag_resv_init` hides reservation space from fdblocks, adjusts `m_ag_max_usable` for AG 0, and initializes `ar_asked`, `ar_orig_reserved`, and `ar_reserved`.
- `xfs_ag_resv_init` calculates reservation needs for refcountbt, finobt, and rmapbt, falls back if finobt reservation cannot be made, and ensures AGF-derived counters are initialized.
- `xfs_ag_resv_alloc_extent` and `xfs_ag_resv_free_extent` debit or replenish reservation counters and update transaction superblock deltas correctly for reserved versus ordinary blocks.

## Control Flow
Mount/grow/shrink paths call `xfs_ag_resv_init` per AG. Metadata reservation is attempted first from refcountbt and finobt calculations; if the combined reservation fails, the code marks `m_finobt_nores` and retries only the refcountbt requirement. Rmapbt reservation is separate because rmapbt blocks live in free space/AGFL accounting. Allocation and free paths pass a reservation type so the reservation can be consumed or replenished instead of treating all blocks as ordinary fdblocks.

## State and Persistence Behavior
Reservation state is stored in `pag->pag_meta_resv` and `pag->pag_rmapbt_resv`; global free-block accounting is adjusted via `xfs_dec_fdblocks`, `xfs_add_fdblocks`, and `xfs_trans_mod_sb`. There is no on-disk reservation record. After a crash, free-space metadata and normal mount-time accounting rebuild the usable state.

## Dependencies and Integration Points
The file integrates with refcount, rmap, and inode allocation reserve calculators; AGF reads; transaction superblock accounting; error injection; tracepoints; and allocator reservation types (`XFS_AG_RESV_*`). `xfs_alloc.c` uses `xfs_ag_resv_needed`, `alloc_extent`, and `free_extent` to enforce the virtual reservations.

## Risks and Edge Cases
Incorrect hidden-space math can overstate free blocks or starve userspace. Rmapbt differs from other metadata because its used blocks remain counted as free-space-owned, so `ar_orig_reserved` handling matters at unmount. Reservation init can return `-ENOSPC` even after counters were partly initialized; callers must decide whether to continue or recover. Shrink paths must free and reinitialize reservations carefully.

## Test Signals
Relevant tests use reflink/rmapbt/finobt filesystems near ENOSPC, heavy CoW/refcount growth, rmap-heavy metadata updates, mount/unmount accounting comparisons, shrink/grow reservation reinit, error tag injection for reservation failure/critical paths, and xfstests that validate fdblocks stability after metadata btree expansion.
