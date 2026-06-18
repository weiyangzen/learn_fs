# sources/distributed-fs/ceph-client/fs/xfs/xfs_buf_item.h

Purpose: Declares the XFS in-core buffer log item, BLI flags, and helper APIs used by transaction, buffer I/O, quota, and recovery code.

Important APIs, types, and functions: Defines BLI flags for hold, dirty, stale, logged, inode allocation, stale inode, inode buffer, and ordered state. `struct xfs_buf_log_item` embeds `xfs_log_item`, an attached `xfs_buf`, flags, recursion count, refcount, format array, and a single embedded format. Declares init, done, put, log, dirty-format, inode/dquot iodone, buffer iodone, iovec checking, and invalidation log-space helpers.

Control flow: Transaction code attaches, dirties, holds, and releases buffer items through these declarations. I/O completion and recovery code use the same item to clean up AIL state and dependent inode/dquot completions.

State and persistence: Defines in-memory buffer item state; persistent contents are emitted as `xfs_buf_log_format` records by `xfs_buf_item.c`.

Dependencies and integration points: Part of the XFS metadata logging ABI and compiled with a quota iodone stub when `CONFIG_XFS_QUOTA` is disabled.

Risks and test signals: Risks are flag semantic drift and non-quota build gaps. Test quota/non-quota builds and trace decoding for every BLI flag.
