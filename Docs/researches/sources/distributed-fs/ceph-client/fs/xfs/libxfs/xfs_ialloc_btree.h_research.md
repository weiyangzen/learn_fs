# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ialloc_btree.h

Purpose: `xfs_ialloc_btree.h` declares the inode btree interface and layout helpers for inobt and finobt blocks. It bridges the on-disk record definitions in `xfs_format.h` with the btree implementation in `xfs_ialloc_btree.c` and allocator policy in `xfs_ialloc.c`.

Important APIs and macros: `XFS_INOBT_BLOCK_LEN(mp)` selects the short-form btree header size based on CRC support. `XFS_INOBT_REC_ADDR`, `XFS_INOBT_KEY_ADDR`, and `XFS_INOBT_PTR_ADDR` compute record/key/pointer locations inside a btree block; comments note that these are used by userspace even if not always by kernel code. Public functions include `xfs_inobt_init_cursor`, `xfs_finobt_init_cursor`, `xfs_inobt_maxrecs`, `xfs_inobt_irec_to_allocmask`, debug `xfs_inobt_rec_check_count`, `xfs_finobt_calc_reserves`, `xfs_iallocbt_calc_size`, `xfs_inobt_commit_staged_btree`, `xfs_iallocbt_maxlevels_ondisk`, and cursor cache init/destroy.

Control flow and state behavior: the header itself contains only address arithmetic and declarations. The address macros assume one-based btree slot indexes, a valid block pointer, a caller-supplied `maxrecs` for pointer arrays, and the proper header length for the mounted format. Cursor constructors require perag, optional transaction, and optional AGI buffer; staging cursors pass NULL transaction and AGI buffer.

Persistence behavior: this header does not write metadata directly, but it defines how code locates persistent btree records within on-disk buffers. Header length selection is format-sensitive: CRC-enabled filesystems have larger btree headers with UUID/owner/LSN/CRC fields, and using the wrong size would shift every record. Reserve and size functions affect persistent metadata reservation accounting for finobt.

Dependencies and integration points: it depends on `xfs_format.h` types such as `xfs_inobt_rec_t`, `xfs_inobt_key_t`, pointer types, and btree header lengths. It is consumed by inode allocator code, repair/staging code, userspace tools, and generic btree code. The reserve API integrates finobt sizing into per-AG metadata reservation setup.

Risks: off-by-one indexing in address macros can corrupt or misread btree blocks. Consumers must pass the same `maxrecs` value used to lay out a node block. CRC feature gating must be consistent with mounted superblock state. Debug-only `xfs_inobt_rec_check_count` compiles away in production, so production code must not rely on it for essential validation.

Test signals: build tests should include kernel and xfsprogs users. Btree layout tests should validate record/key/pointer offsets for CRC and non-CRC filesystems, leaf and node blocks, minimum block sizes, and max record calculations. Repair tests should exercise staged btree commit and finobt reserve calculations.
