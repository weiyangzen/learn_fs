# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_inode_buf.h

Purpose: Declares inode-buffer location and conversion/verifier interfaces shared by libxfs users. It is the public contract for mapping inode numbers to buffers and translating `xfs_dinode` cores.

Important APIs and types: `struct xfs_imap` records inode chunk block, length, and byte offset; declarations cover `xfs_imap_to_bp`, `xfs_dinode_calc_crc`, `xfs_inode_to_disk`, `xfs_inode_from_disk`, `xfs_dinode_verify`, `xfs_dinode_verify_metadir`, `xfs_inode_validate_extsize`, `xfs_inode_validate_cowextsize`, `xfs_inode_from_disk_ts`, `xfs_inode_encode_bigtime`, and `xfs_dinode_good_version`.

Control flow: the header itself has minimal logic. `xfs_inode_encode_bigtime` maps Unix seconds into the XFS bigtime epoch and adds nanoseconds. `xfs_dinode_good_version` defines the feature-dependent acceptable dinode versions: v3 only for v3 inode filesystems, otherwise v1/v2.

State and persistence: exposes structures and functions that operate on persistent dinode buffers and bigtime timestamp encoding. `xfs_imap` is transient in-core mapping metadata but points to persistent inode chunks.

Dependencies and integration: included by inode read/write, recovery, icache, and repair paths needing verifier or conversion functions. It depends on mount feature predicates, timestamp constants, and core XFS type definitions.

Risks and test signals: the header is small but ABI-sensitive because callers rely on exact conversion semantics. Tests should cover bigtime encode/decode round trips, v1/v2/v3 version acceptance, and inode buffer mapping callers that pass `xfs_imap` into transaction reads.
