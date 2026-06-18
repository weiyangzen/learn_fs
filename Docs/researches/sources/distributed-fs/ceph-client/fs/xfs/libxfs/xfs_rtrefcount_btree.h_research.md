# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtrefcount_btree.h

Purpose: Declares the realtime refcount btree interface and provides layout helpers for incore and on-disk realtime refcount roots.

Important APIs, types, and functions: Defines `XFS_RTREFCOUNT_BLOCK_LEN`; declares cursor, staging, max-record, max-level, reserve, format, flush, conversion, and create functions. Inline helpers compute record/key/pointer addresses in incore `xfs_btree_block` roots and on-disk `xfs_rtrefcount_root` blocks, plus `xfs_rtrefcount_broot_space_calc`, `xfs_rtrefcount_broot_space`, `xfs_rtrefcount_droot_space_calc`, and `xfs_rtrefcount_droot_space`.

Control flow: Btree code and inode format/flush paths use these helpers to locate variable-length root contents. Leaf roots store `xfs_refcount_rec` records; internal roots store keys followed by long pointers. Disk-root helpers start after the compact `xfs_rtrefcount_root`, while incore helpers reserve the full CRC btree block header area.

State and persistence: The header defines no state itself, but its layout math is the contract between on-disk inode fork bytes and incore btree root buffers. Persistent correctness depends on exact sizes and endian-aware callers.

Dependencies and integration points: Used by realtime refcount btree implementation, inode fork formatting, userspace libxfs consumers, repair/staging code, and generic btree code.

Risks and test signals: Risks are ABI/layout drift, off-by-one one-based index handling, using a leaf layout for internal roots, and inconsistent incore-vs-disk root sizing. Test root address helpers with zero, one, and many records; max dinode fork sizes; internal roots with pointer movement; and userspace repair builds.
