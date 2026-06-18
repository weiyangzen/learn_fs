# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtrefcount_btree.c

Purpose: Adapts the generic XFS btree engine to realtime refcount btrees rooted in realtime metadata inodes, providing cursor operations, verifiers, record/key conversion, root resizing, reserve sizing, and inode fork format/flush support.

Important APIs, types, and functions: Defines `xfs_rtrefcountbt_ops`, `xfs_rtrefcountbt_buf_ops`, `xfs_rtrefcountbt_init_cursor`, `xfs_rtrefcountbt_commit_staged_btree`, `xfs_rtrefcountbt_maxrecs`, `xfs_rtrefcountbt_maxlevels_ondisk`, cursor cache init/destroy, `xfs_rtrefcountbt_compute_maxlevels`, `xfs_rtrefcountbt_calc_size`, `xfs_rtrefcountbt_calc_reserves`, `xfs_iformat_rtrefcount`, `xfs_rtrefcountbt_to_disk`, `xfs_iflush_rtrefcount`, and `xfs_rtrefcountbt_create`.

Control flow: Cursor creation requires the rt refcount inode to be locked, allocates a cursor from the kmem cache, binds it to the inode data fork and rtgroup, and derives height from the inode root. Btree ops encode refcount record starts with the shared/COW domain, compare ordered startblock keys, verify CRC v5 blocks, and resize the inode-root buffer while moving pointer arrays when internal roots grow or shrink. Inode read converts the compact on-disk root into a generic incore btree block; flush reverses that transformation. Staged btree commit replaces the real fork with a fake-root fork and logs core/root changes.

State and persistence: Persistent state is the rt refcount metafile inode with `XFS_DINODE_FMT_META_BTREE`, an on-disk `xfs_rtrefcount_root`, and child btree blocks with `XFS_RTREFC_CRC_MAGIC`. Incore state includes the fork btree root, cursor cache, mount max/min record geometry, and held rtgroup reference.

Dependencies and integration points: Integrates with refcount update code, realtime group inode management, generic btree staging, metadata block allocation/freeing, xfs health sickness masks, transaction logging, and mount-time geometry calculation.

Risks and test signals: Risks include root size calculation mismatches between disk and incore formats, accepting reflink-disabled metadata, pointer-array movement during resize, maxlevel underestimation, and corrupt domain-encoded startblocks. Test metadir growfs creation before rt volume attach, reflink and rtreflink feature combinations, root split/join, staged repair commit, CRC/magic/level corruption, and maximal rtgroup extent counts.
