# sources/distributed-fs/ceph-client/fs/gfs2/bmap.c

## Purpose
Maps GFS2 logical file blocks to disk blocks, allocates extents through iomap, unstuffs inline files, handles truncation/hole punching/deallocation, computes allocation requirements, and builds journal extent caches.

## Important APIs, Types, And Functions
`struct metapath` records the metadata-tree path and buffers. `gfs2_unstuff_dinode()` moves stuffed inline data into normal blocks. `find_metapath()`, `lookup_metapath()`, `fillup_metapath()`, and `release_metapath()` traverse indirect metadata. `__gfs2_iomap_get()` maps inline, hole, or mapped extents; `gfs2_iomap_begin()`, `gfs2_iomap_end()`, and `gfs2_iomap_ops` integrate with iomap. `__gfs2_iomap_alloc()` allocates indirect/data blocks and grows tree height/depth. `gfs2_block_map()`, `gfs2_get_extent()`, and `gfs2_alloc_extent()` provide buffer-head and extent mapping APIs for other GFS2 code. `trunc_start()`, `punch_hole()`, `trunc_end()`, `do_shrink()`, `do_grow()`, and `gfs2_setattr_size()` implement size changes. `gfs2_map_journal_extents()` caches journal file extents. `__gfs2_punch_hole()` supports fallocate-style punching and zeroing partial blocks. `gfs2_writeback_ops` maps folios for iomap writeback.

## Control Flow
Mapping starts with the dinode buffer, handles stuffed files inline, computes target tree height, walks existing metadata, reports holes or extents, and optionally reserves quota/resource groups to allocate. Allocation is a state machine: grow tree height, fill missing depth, then install data block pointers. Iomap end releases reservations, unlocks quotas, cleans up partially written new blocks by punching the unwritten tail, and marks glocks dirty. Truncation first zeroes partial blocks, marks truncate-in-progress, changes i_size, truncates page cache or journaled ranges, deallocates blocks bottom-up by resource group, updates statfs/quota, and clears truncate-in-progress. Hole punching separately zeroes unaligned edges, waits for page cache writeback, truncates cache/jdata ranges, updates timestamps, and deallocates whole blocks.

## State And Persistence
Persists dinode height, size, disk flags, block pointers, inode block counts, journal revokes, statfs/quota changes, resource-group bitmaps, and journal extent lists. Uses `GFS2_DIF_TRUNC_IN_PROG` to support recovery/resume after interrupted truncation. Page cache is truncated or zeroed to match on-disk deallocation.

## Dependencies And Integration Points
Depends on GFS2 glocks, metadata I/O, resource groups, quota, transactions, directory buffer allocation, iomap, buffer heads, and writeback. Provides core mapping services to aops, dir, file, journal, and inode code.

## Risks
This is one of the highest-risk GFS2 files. Metadata-tree updates must be journaled in recoverable order. Resource-group locking is split to reduce contention but must avoid freeing blocks under the wrong rgrp. Partial write failures must deallocate just-created blocks. Journaled-data truncation must split revoke-heavy work into bounded transactions. Stuffed-to-unstuffed transitions must preserve data and mode-specific journaling. Direct I/O intentionally falls back when a write would hit holes or stuffed data.

## Test Signals
Test block mapping of holes, inline data, single/multi-level extents, allocation across indirect boundaries, partial write failures, direct-I/O fallback, grow and shrink truncate, crash/recovery with truncate-in-progress, fallocate punch hole including unaligned edges, journal extent mapping, quota/statfs updates, and resource-group contention.
