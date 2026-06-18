# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_metafile.c

Purpose: Manages metadata inode identity and space reservations for metadata btree files, especially realtime rmap/refcount btrees under the metadir feature.

Important APIs: `xfs_metafile_type_str`, `xfs_metafile_set_iflag`, `xfs_metafile_clear_iflag`, `xfs_metafile_resv_critical`, `xfs_metafile_resv_alloc_space`, `xfs_metafile_resv_free_space`, `xfs_metafile_resv_free`, and `xfs_metafile_resv_init`.

Control flow: metadata flag setup strips permissions, forces root uid/gid, applies mandatory metadata file or directory flags, clears DAX, sets `XFS_DIFLAG2_METADATA`, records metatype, logs the inode, and moves stats from active to metadata. Reservation initialization frees old reservation state, walks realtime groups to compute used and target reserve for rtrmap/rtrefcount btrees, caps reservation to a quarter of data blocks, hides unused reserved space from fdblocks, and records used/available/target counts. Allocation first consumes reservation availability and updates reserved fdblocks, then falls back to free blocks or transaction reservation for overrun. Freeing decrements inode blocks, refills hidden reservation to target, and returns excess to global fdblocks.

State and persistence: mutates inode core metadata flags and `i_nblocks`, mount reservation counters under `m_metafile_resv_lock`, in-core and on-disk fdblocks, and delayed allocation accounting.

Dependencies and integration: depends on realtime group iteration, rtrmap/rtrefcount reserve calculators, transaction superblock accounting, allocation args, error injection, and feature predicates.

Risks and test signals: space-accounting bugs can hide or leak blocks and cause metadata btree ENOSPC. Tests should cover mount/unmount reservation init/free, growfs or realtime feature changes, reservation critical thresholds, overrun paths, transaction rollback, and stats transitions for metadata inodes.
