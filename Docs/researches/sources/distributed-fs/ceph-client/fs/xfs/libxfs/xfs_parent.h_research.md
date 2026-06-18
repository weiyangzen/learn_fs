# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_parent.h

Purpose: Declares the parent pointer interface and small helpers for encoding parent records and allocating update context.

Important APIs and types: validators, hash functions, `xfs_parent_rec_init`, `xfs_inode_to_parent_rec`, `struct xfs_parent_args`, `xfs_parent_start`, `xfs_parent_finish`, transactional add/remove/replace, attr extraction, lookup, repair set, and repair unset.

Control flow: `xfs_parent_start` allocates a zeroed parent args object only when the filesystem has parent pointers; otherwise it returns a null context and success. `xfs_parent_finish` frees the context if present. Inline record helpers encode inode and generation in big-endian on-disk form.

State and persistence: `struct xfs_parent_args` is transient state that carries old/new parent records and a prepared `xfs_da_args` for logged attr operations. Parent records themselves persist inside child xattrs.

Dependencies and integration: used by directory create/remove/rename code, metadir operations, attr recovery, scrub/repair, and parent-pointer validators.

Risks and test signals: callers must honor null contexts on filesystems without parent pointers and must not reuse stale `xfs_da_args`. Tests should cover feature-disabled no-op start/finish, allocation failure, record endian encoding, and rename replacement carrying both old and new records.
