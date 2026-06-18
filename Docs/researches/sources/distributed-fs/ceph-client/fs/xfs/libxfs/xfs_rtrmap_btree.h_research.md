# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtrmap_btree.h

Purpose: Declares realtime rmap btree entry points and defines address/size helpers for overlapping realtime rmap root layouts.

Important APIs, types, and functions: Defines `XFS_RTRMAP_BLOCK_LEN`; declares cursor, staging, reserve, maxlevel, format/flush, create, rtsb initialization, in-memory btree, and highest-rgbno helpers. Inline helpers include `xfs_rtrmap_rec_addr`, `xfs_rtrmap_key_addr`, `xfs_rtrmap_high_key_addr`, `xfs_rtrmap_ptr_addr`, on-disk root address helpers, and root space calculators for incore and disk formats.

Control flow: Realtime rmap roots are leaf roots with records or internal roots with paired low/high keys and long pointers. One-based index helpers compute offsets into compact root storage and generic incore blocks. Callers use these helpers during cursor operations, inode fork conversion, and userspace repair validation.

State and persistence: The header encodes persistent root layout assumptions for `struct xfs_rtrmap_root`. Because rmap btrees are overlapping, internal roots must allocate twice as many key bytes per record slot as ordinary btrees.

Dependencies and integration points: Used by `xfs_rtrmap_btree.c`, generic btree code, inode format/flush, repair staging, and rtgroup/rtsb setup.

Risks and test signals: Risks are low/high key layout mistakes, pointer offset drift after root resize, incorrect userspace assumptions, and root space calculations that exceed dinode fork size. Test leaf/internal root helpers, staged root replacement, maximum records for several block sizes, and in-memory btree builds.
