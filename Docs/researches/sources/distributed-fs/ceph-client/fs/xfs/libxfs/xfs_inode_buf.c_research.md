# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_inode_buf.c

Purpose: Verifies inode buffers and converts inode cores between on-disk `struct xfs_dinode` and in-core `struct xfs_inode` state. It centralizes dinode integrity checks, timestamp conversion, CRC calculation, extent count encoding, and inode hint validation.

Important APIs: buffer verifier ops `xfs_inode_buf_ops` and `xfs_inode_buf_ra_ops`; `xfs_imap_to_bp`; timestamp helpers `xfs_inode_from_disk_ts` and the private disk encoder; conversion functions `xfs_inode_from_disk` and `xfs_inode_to_disk`; verifiers `xfs_dinode_verify`, `xfs_dinode_verify_metadir`, `xfs_inode_validate_extsize`, `xfs_inode_validate_cowextsize`; CRC writer `xfs_dinode_calc_crc`.

Control flow: read verification scans every inode in a buffer, checking magic, version, and unlinked-list agino. Readahead failures mark the buffer not done instead of producing normal corruption reports. `xfs_inode_from_disk` verifies the dinode, copies permanent VFS/XFS fields, handles v1 inode compatibility, decodes timestamps including bigtime, formats data and attr forks, initializes CoW forks for reflink, and adjusts metadata-inode stats. `xfs_inode_to_disk` writes the reverse representation, selecting v2/v3 fields and large extent counters. `xfs_dinode_verify` performs layered checks: v3 CRC/UUID/ino, mode/size, fork counts, fork offsets and formats, feature-dependent flags, metadata inode constraints, hint alignment, bigtime, reflink/realtime compatibility, and nblocks consistency.

State and persistence: this file is a persistence boundary. It reads and writes dinode core fields, inode buffer CRCs, LSNs, fork counters, timestamps, metadata type, quota/project ids, and unlinked-list pointers. It marks sick AG/inode metadata on verifier failures.

Dependencies and integration: calls fork materialization from `xfs_inode_fork.c`, health marking, transaction buffer reads, directory and metadata feature predicates, and Linux VFS inode helpers.

Risks and test signals: ABI and compatibility risks are high: incorrect endian conversion, v3 CRC range, large extent counters, bigtime ranges, metadir restrictions, and extent hint validation can reject valid filesystems or admit corruption. Signals include xfs/122-style ondisk layout tests, fuzzed inode images, mount tests across feature combinations, realtime/reflink/bigtime/metadir matrices, and log recovery over inode buffers.
