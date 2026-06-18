# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_alloc_btree.h

## Purpose
This header declares on-disk layout helpers and public operations for XFS free-space allocation btrees. It abstracts record/key/pointer addressing inside bnobt/cntbt blocks and exposes cursor, staged commit, size, level, and cache lifecycle functions.

## Important APIs and Macros
- `XFS_ALLOC_BLOCK_LEN(mp)` selects short btree header size depending on CRC support.
- `XFS_ALLOC_REC_ADDR`, `XFS_ALLOC_KEY_ADDR`, and `XFS_ALLOC_PTR_ADDR` compute typed addresses inside allocation btree blocks.
- `xfs_bnobt_init_cursor` and `xfs_cntbt_init_cursor` create cursors for the by-block and by-count trees.
- `xfs_allocbt_maxrecs`, `xfs_allocbt_calc_size`, and `xfs_allocbt_maxlevels_ondisk` provide sizing/height calculations.
- `xfs_allocbt_commit_staged_btree` installs a staged rebuilt btree root.
- `xfs_allocbt_init_cur_cache` and `xfs_allocbt_destroy_cur_cache` manage cursor slab cache state.

## Control Flow and Integration
Allocator and repair code include this header to navigate btree blocks and construct cursors. The address macros are used by both kernel and userspace libxfs-style code, which is why some macros may appear unused in this kernel subset.

## State and Persistence Behavior
The macros directly address persistent on-disk btree records, keys, and pointers in buffers. The function declarations expose operations that mutate AGF roots and btree blocks through transactions.

## Dependencies and Risks
Correct header-length selection is essential: CRC-enabled and non-CRC formats have different btree headers. Off-by-one index handling in address macros would corrupt btree records. Staged commit callers must invalidate/free old btree blocks separately as documented in the implementation.

## Test Signals
Signals include btree record/key/pointer layout tests for CRC and non-CRC filesystems, cursor construction tests, online repair staged btree commits, max-level sizing checks, and userspace libxfs build coverage for the address macros.
