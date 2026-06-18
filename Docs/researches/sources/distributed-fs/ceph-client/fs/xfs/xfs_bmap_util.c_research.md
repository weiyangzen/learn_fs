<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_bmap_util.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_bmap_util.c

Purpose: Provides higher-level block mapping utilities around XFS extent state: file extent reporting, delayed allocation punching, EOF preallocation cleanup, fallocate/punch/collapse/insert operations, zeroing, extent counting, and legacy swapext support.

Important APIs and functions: `xfs_getbmap` reports extents for getbmapx. `xfs_bmap_punch_delalloc_range` removes delalloc mappings without a transaction. `xfs_can_free_eofblocks` and `xfs_free_eofblocks` decide and execute post-EOF cleanup. `xfs_alloc_file_space`, `xfs_free_file_space`, `xfs_collapse_file_space`, `xfs_insert_file_space`, and `xfs_flush_unmap_range` implement file-space manipulation. `xfs_swap_extents` swaps data extents between a target and temporary inode. Utility helpers include `xfs_fsb_to_db`, `xfs_zero_extent`, `xfs_bmap_count_leaves`, and `xfs_bmap_count_blocks`.

Control flow: `xfs_getbmap` validates flags, locks I/O and fork state, optionally flushes data fork delalloc, loads extents, emits holes and extents, and splits records around shared/unshared reflink regions. Space allocation loops with transaction reservations and preallocation flags. Free-space punching flushes/invalidate page cache, unmaps full blocks, and zeroes partial blocks without extending EOF. Collapse/insert prepare by freeing EOF blocks, flushing from an aligned boundary, canceling COW, then shifting extents transactionally with defer rolls. Swapext locks both files and page caches, flushes both, validates format/timestamps/realtime/quota compatibility, then either remaps extents with rmapbt or swaps forks and fixes bmbt owners.

State and persistence: Mutates inode extent maps, delayed block counters, preallocation flags, inode block counts, COW forks, and bmbt block owners through transactions. Flush/invalidate paths synchronize page cache with mapping changes. `xfs_getbmap` is read-only except for required writeback flushing.

Dependencies and integration: Integrates with bmap core, iomap zeroing, reflink, realtime and zoned allocation, quota attachment, transaction reservations, inodegc/page cache, rmapbt, bmbt owner changes, VFS locking, and tracepoints.

Risks: Extent shift operations are race-sensitive with COW writeback and require IOLOCK/MMAPLOCK exclusivity plus aligned cache invalidation. Partial block punch must zero correctly without growing i_size. Swapext is deprecated-style and has many invariants; format, owner, quota, timestamp, rmap, and realtime-group restrictions are critical. EOF cleanup avoids updating on-disk size to prevent NULL-file exposure after crash.

Test signals: getbmap with holes/delalloc/shared/unwritten extents and attr/COW forks; fallocate prealloc loops with ENOSR; punch hole partial-block zeroing; collapse/insert under reflink/COW and realtime units; EOF block cleanup for prealloc/append files; swapext with rmapbt, btree forks, reflink flags, timestamp mismatch, and crash recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_bmap_util.c -->
