# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_types.c

Purpose: Implements core verifier helpers for XFS block, extent, inode, realtime block, inode count, directory/attribute block, and file offset types.

Important APIs, types, and functions: Exports `xfs_verify_fsbno`, `xfs_verify_fsbext`, `xfs_verify_ino`, `xfs_is_sb_inum`, `xfs_verify_dir_ino`, `xfs_verify_rtbno`, `xfs_verify_rtbext`, `xfs_icount_range`, `xfs_verify_icount`, `xfs_verify_dablk`, `xfs_verify_fileoff`, and `xfs_verify_fileext`. Internal helpers validate AG block and AG inode ranges.

Control flow: Data block verifiers reject blocks outside AG count, outside the AG tail, or inside static AG metadata. Extent verifiers reject wraparound and cross-AG ranges. Inode verifiers reject impossible AG/AGINO conversions and values outside per-AG inode ranges; directory inode verification additionally rejects internal quota/realtime metadata inodes. Realtime verifiers handle rtgroups by checking group number, per-group extent count, rtsb exclusion, and cross-group extents; legacy realtime falls back to `sb_rblocks`.

State and persistence: No state is persisted. The functions validate persistent metadata pointers against mount geometry and per-AG inode range state.

Dependencies and integration points: Used throughout metadata verifiers, bmap/rmap/refcount code, directory checking, repair/scrub, and superblock write validation. Depends on per-AG iteration, rtgroup helpers, quota inode checks, and realtime bitmap conversions.

Risks and test signals: Risks include allowing static metadata references, wraparound misses, rtgroup tail extent mistakes, rtsb block allocation, and inode count range errors during grow/shrink/recovery. Test boundary blocks in first/last AG, AGFL/static metadata addresses, cross-AG and cross-RTG extents, rtgroup zero rtsb, internal inode directory entries, sparse inode ranges, and max file offsets.
