# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_symlink_remote.c

Purpose: Implements encoding, verification, reading, writing, conversion, and truncation for remote XFS symlink targets stored outside the inode data fork.

Important APIs, types, and functions: Exports `xfs_symlink_blocks`, `xfs_symlink_hdr_set`, `xfs_symlink_hdr_ok`, `xfs_symlink_buf_ops`, `xfs_symlink_local_to_remote`, `xfs_symlink_shortform_verify`, `xfs_symlink_remote_read`, `xfs_symlink_write_target`, and `xfs_symlink_remote_truncate`.

Control flow: `xfs_symlink_write_target` stores short targets inline when they fit in the inode data fork; otherwise it allocates metadata extents, writes one buffer per mapping, stamps CRC headers when enabled, copies target chunks, logs buffers, and updates inode size/core. Read maps symlink extents, reads each buffer with verifier ops, checks header offset/length/owner, copies payload chunks, and NUL-terminates the caller buffer. Truncate reads current mappings, invalidates their buffers in the transaction, then unmaps all remote blocks.

State and persistence: Persistent remote symlink buffers optionally start with `xfs_dsymlink_hdr` containing magic, offset, bytes, UUID, owner inode, block address, LSN, and CRC. Non-CRC filesystems store raw target bytes. Inline symlink state lives in the inode local fork.

Dependencies and integration points: Depends on bmap read/write/unmap, buffer verifiers, inode health marking, transaction buffer logging/binval, log LSN checks, and inode fork initialization.

Risks and test signals: Risks include header/payload length mismatches, stale owner or block address, missing NUL termination for shortform data, multi-extent chunk ordering bugs, and partial truncate corruption. Test CRC and non-CRC filesystems, inline-to-remote conversion, max-length targets, sparse/corrupt symlink mappings, bad header owner/offset/length, and create/unlink recovery.
