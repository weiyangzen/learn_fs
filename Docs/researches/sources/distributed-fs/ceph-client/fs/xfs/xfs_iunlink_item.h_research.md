## sources/distributed-fs/ceph-client/fs/xfs/xfs_iunlink_item.h

Purpose: declares the in-memory log item used for transactional unlinked-list pointer updates.

Important APIs and types: `struct xfs_iunlink_item` embeds `struct xfs_log_item` and stores the target inode, held per-AG pointer, new `next_agino`, and expected `old_agino`. It declares the slab cache `xfs_iunlink_cache` and the entry point `xfs_iunlink_log_inode`.

Control flow: no code executes here. Transactions that manipulate unlinked inode lists call `xfs_iunlink_log_inode`, which creates an item whose precommit callback updates the dinode field.

State and persistence behavior: the struct is transient transaction state that drives persistent updates to `di_next_unlinked`. Its old/new AG inode fields are also consistency guards.

Dependencies and integration: depends on transaction, inode, perag, log item, and `xfs_agino_t` definitions supplied by including code. It is consumed by inode unlink/inactivation code and implemented by `xfs_iunlink_item.c`.

Risks and test signals: ABI is internal, but field ordering and lifetime matter for log item operations. Build coverage plus unlink/recovery tests that allocate and free iunlink items validate this header.
