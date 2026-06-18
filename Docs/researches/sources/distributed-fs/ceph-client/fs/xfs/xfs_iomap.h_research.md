## sources/distributed-fs/ceph-client/fs/xfs/xfs_iomap.h

Purpose: declares the XFS iomap interface used by file I/O, truncation, zeroing, DAX, reflink, and xattr mapping paths.

Important APIs and types: it forward-declares `struct xfs_inode`, `struct xfs_bmbt_irec`, and `struct xfs_zone_alloc_ctx`. It exposes direct allocation (`xfs_iomap_write_direct`), unwritten conversion (`xfs_iomap_write_unwritten`), EOF alignment (`xfs_iomap_eof_align_last_fsb`), sequence-cookie generation (`xfs_iomap_inode_sequence`), bmbt-to-iomap conversion (`xfs_bmbt_to_iomap`), zero/truncate helpers, and all exported `struct iomap_ops` plus `xfs_iomap_write_ops`.

Control flow: callers select an operation table appropriate to read, seek, buffered write, direct write, DAX write, xattr, zoned direct write, or software atomic CoW write. The inline `xfs_aligned_fsb_count` expands a file-block count to cover an extent-size alignment boundary.

State and persistence behavior: no state is stored in the header. Declared functions can reserve delayed blocks, allocate persistent blocks, convert unwritten extents, and update fork sequence counters indirectly through bmap operations.

Dependencies and integration: includes Linux `iomap.h` and assumes XFS block/offset typedefs are already available. It is a contract between `xfs_iomap.c` and higher-level XFS file, inode, reflink, and truncate code.

Risks and test signals: prototype mismatches can break many I/O modes. Coverage should include all exported operation tables under configs with and without realtime/zoned/DAX/reflink support, plus alignment helper edge cases with zero and non-power-of-two extent hints.
