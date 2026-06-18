# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_cksum.h

## Purpose
This header provides inline CRC32c checksum helpers for XFS metadata buffers whose checksum field lives inside the covered buffer.  It supports both verification without modifying the buffer and update paths that temporarily zero the checksum field.

## Important APIs And Functions
`XFS_CRC_SEED` is the initial CRC32c seed.  `xfs_start_cksum_safe` computes the intermediate CRC by checksumming bytes before the checksum field, checksumming a local zero value in place of the field, and checksumming the remaining bytes.  `xfs_start_cksum_update` writes zero into the buffer checksum field and computes CRC over the whole buffer.  `xfs_end_cksum` converts the intermediate CRC to the stored little-endian inverted format.  `xfs_update_cksum` writes the final checksum, and `xfs_verify_cksum` compares stored and computed values.

## Control Flow And State
The safe verification flow is non-mutating and fits shared/read-only buffer access.  The update flow mutates the checksum field and therefore requires exclusive buffer access.  The only persistent state affected is the checksum field at `cksum_offset`.

## Dependencies And Integration Points
The helpers depend on `crc32c`, endian conversion, and XFS integer types.  They are used by buffer-level metadata checksum helpers, including btree block CRC functions through `xfs_buf_update_cksum` and `xfs_buf_verify_cksum`.

## Risks And Test Signals
Risks include bad offset/length pairs, using the mutating helper without exclusive access, and confusing host-endian CRC values with on-disk little-endian inverted storage.  Tests should verify update-then-verify cycles, corruption detection, unchanged buffers after safe verification, endian-stable stored values, and boundary offsets.
