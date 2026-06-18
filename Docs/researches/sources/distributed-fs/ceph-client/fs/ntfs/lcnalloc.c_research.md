# sources/distributed-fs/ceph-client/fs/ntfs/lcnalloc.c

## Purpose
`lcnalloc.c` implements NTFS logical-cluster allocation and deallocation against the volume `$Bitmap` attribute. It allocates clusters from the MFT or data zones, updates allocation bitmap bits, maintains free/dirty cluster counters and allocator cursors, shrinks the MFT zone when necessary, frees clusters from runlists, and issues discard after successful frees when enabled.

## Important APIs, Types, and Functions
`ntfs_cluster_alloc()` is the main allocator. It takes a target VCN, requested count, optional LCN hint, allocation zone (`MFT_ZONE` or `DATA_ZONE`), extension versus hole-fill mode, contiguity requirement, and deallocation-reservation mode. It returns a newly allocated runlist or an error pointer.

`ntfs_cluster_free_from_rl_nolock()` frees every non-negative LCN run in a supplied runlist while the volume LCN bitmap lock is already held. `__ntfs_cluster_free()` frees a range from an inode runlist, maps unmapped runlist fragments as needed, rolls back on partial failure, updates free counts, and optionally discards freed block-device ranges. `max_empty_bit_range()` is a local scanner that finds the longest zero-bit run in a bitmap buffer when no caller hint is being followed.

## Control Flow and State
Allocation begins by validating arguments, entering NOFS allocation context, waiting until free-cluster accounting is known, taking `vol->lcnbmp_lock`, and checking free space minus dirty reservations. It chooses a starting zone based on caller hint or volume cursors (`mft_zone_pos`, `data1_zone_pos`, `data2_zone_pos`) and then scans `$Bitmap` folios. For each free bit it marks the bit allocated, dirties the folio, decrements free clusters, updates per-page empty-bit hints, and appends or coalesces a runlist element. If a zone is exhausted, the allocator performs a second pass over the skipped prefix, switches zones, or shrinks the MFT zone for data allocation. On success it appends a terminator with `LCN_ENOENT` for extension or `LCN_RL_NOT_MAPPED` for hole fill.

Freeing starts at a VCN, finds the corresponding runlist element, clears bitmap bits for real clusters, skips sparse holes, maps unmapped fragments as needed, and tracks both total VCNs processed and real clusters freed. On error after partial freeing, it recursively calls `__ntfs_cluster_free(..., is_rollback=true)` to restore bits and marks volume errors if rollback fails. After success it increments free cluster count and may issue `blkdev_issue_discard()` for aligned freed ranges.

## State and Persistence Behavior
This file directly mutates persistent allocation state in the `$Bitmap` inode's page cache and marks modified folios dirty. It updates in-memory volume accounting (`free_clusters`, `dirty_clusters`, zone cursors, MFT zone bounds, per-page empty-bit hints) to mirror allocation decisions. Rollback is designed to preserve on-disk bitmap consistency when allocation or free operations fail partway through; failure to roll back sets the volume error flag and instructs chkdsk.

## Dependencies and Integration Points
It depends on Linux block-device APIs plus NTFS `lcnalloc.h`, `bitmap.h`, and `ntfs.h`. It integrates with runlist mapping (`ntfs_attr_find_vcn_nolock()`), bitmap bit setters/clearers, volume flags (`NVolFreeClusterKnown`, `NVolDiscard`, `NVolSetErrors`), allocator accounting helpers (`ntfs_inc_free_clusters`, `ntfs_dec_free_clusters`, dirty-cluster helpers), and write paths that request delayed or real allocation.

## Risks
Allocation correctness depends on bitmap locking, folio dirtying, and runlist rollback. Incorrect zone cursor updates can cause fragmentation or missed free space; incorrect MFT zone shrinking can consume reserved MFT growth space too aggressively. Partial failure paths are high risk because bitmap bits may already be changed. The code also mixes byte, bit, cluster, sector, and page units, so off-by-one errors around `buf_size`, `zone_end`, and VCN/LCN conversions are important. Discard alignment must not discard outside freed extents.

## Test Signals
Useful tests include allocating in data and MFT zones, hinted allocations, contiguous-only allocation, ENOSPC with rollback, MFT-zone shrink behavior, freeing ranges that start/end mid-run, freeing sparse and unmapped runs, discard-enabled frees, dirty-cluster reservation interaction with writeback, and fault injection for bitmap read, memory allocation, and bitmap update failures.
