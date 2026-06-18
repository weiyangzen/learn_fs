# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_log_format.h

Purpose: Defines the on-disk log ABI for XFS. It covers physical log record headers, operation headers, transaction headers, log item type codes, and every serialized log item structure interpreted by recovery.

Important APIs and types: physical constants and helpers such as `xlog_assign_lsn`, `xlog_get_cycle`, `CYCLE_LSN`, and record-size macros; `struct xlog_op_header`, `struct xlog_rec_header`, `struct xfs_trans_header`; item type constants `XFS_LI_*`; inode log formats and `XFS_ILOG_*` flags; buffer log format and buffer type encodings; intent/done structures for EFI/EFD, RUI/RUD, CUI/CUD, BUI/BUD, XMI/XMD, ATTRI/ATTRD, quotaoff, dquot, and icreate.

Control flow: this header does not execute recovery but encodes how recovery parses records. Variable-length intent structures place arrays immediately after a fixed 16-byte header and provide size helpers. Buffer item flags encode dirty bitmap chunks and buffer type in upper bits. Inode log flags distinguish core, local data, extents, btree roots, device numbers, fork owner updates, and in-memory-only timestamp/version triggers.

State and persistence: all structures are persistent journal state. Some are host-endian historical formats, so the header preserves 32-bit and 64-bit structure variants and architecture-dependent checksum compatibility. Quota flags are shared with superblock/mount state.

Dependencies and integration: consumed by log item formatters, transaction code, recovery, ondisk layout checks, inode flush, buffer replay, deferred operation recovery, and quota code.

Risks and test signals: this is ABI-critical. Changing sizes, offsets, endian assumptions, item ids, or flag masks can make logs unrecoverable. Tests include xfs/122 layout assertions, dirty-log recovery across architectures, intent/done replay matrices for data and realtime operations, inode log replay with all fork formats, and quota flag compatibility tests.
