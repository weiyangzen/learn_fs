# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtrmap_btree.c

Purpose: Implements the realtime reverse-mapping btree adapter for XFS, rooted in realtime metadata inodes and optionally available as an in-memory btree for repair/scrub workflows.

Important APIs, types, and functions: Defines `xfs_rtrmapbt_ops`, optional `xfs_rtrmapbt_mem_ops`, `xfs_rtrmapbt_buf_ops`, `xfs_rtrmapbt_init_cursor`, `xfs_rtrmapbt_mem_cursor`, `xfs_rtrmapbt_mem_init`, `xfs_rtrmapbt_commit_staged_btree`, `xfs_rtrmapbt_maxrecs`, `xfs_rtrmapbt_maxlevels_ondisk`, cursor cache init/destroy, `xfs_rtrmapbt_compute_maxlevels`, `xfs_rtrmapbt_calc_size`, `xfs_rtrmapbt_calc_reserves`, `xfs_iformat_rtrmap`, `xfs_rtrmapbt_to_disk`, `xfs_iflush_rtrmap`, `xfs_rtrmapbt_create`, `xfs_rtrmapbt_init_rtsb`, and `xfs_rtrmap_highest_rgbno`.

Control flow: Btree ops order records by physical rtgroup block, owner, and offset key flags while masking unwritten status for key comparisons. The overlapping btree stores low/high keys, uses metadata inode block allocation, verifies CRC/magic/feature/maxlevel constraints, and resizes inode roots by moving pointer arrays. Disk format load and flush convert between compact `xfs_rtrmap_root` and incore generic btree blocks. The rtsb initializer maps the first realtime extent to `XFS_RMAP_OWN_FS` in rtgroup zero, and `xfs_rtrmap_highest_rgbno` reads the root high key.

State and persistence: Persistent state is the rtrmap metafile inode, its on-disk root, and child blocks with `XFS_RTRMAP_CRC_MAGIC`. Incore state includes cursor cache, mount btree geometry, optional `xfbtree` memory tree, and rtgroup references.

Dependencies and integration points: Integrates with rmap update/deferred-item code, metadir rtgroup inode management, btree staging, scrub/repair in-memory btrees, realtime superblock ownership, health masks, and transaction logging.

Risks and test signals: Risks include incorrect offset flag masking, high-key generation for inode vs non-inode owners, maxlevel calculation under extreme reflink sharing, mem-btree verifier divergence, root conversion errors, and stale rtsb ownership maps. Test rmap insert/delete/update on realtime extents, unwritten extent transitions, non-inode owners, staged repair commit, in-memory scrub btrees, rtsb initialization, and corrupted magic/CRC/level blocks.
