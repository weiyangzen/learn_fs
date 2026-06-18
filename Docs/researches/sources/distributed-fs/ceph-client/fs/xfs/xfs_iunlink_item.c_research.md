## sources/distributed-fs/ceph-client/fs/xfs/xfs_iunlink_item.c

Purpose: implements the transaction log item used to update an inode dinode's `di_next_unlinked` pointer during unlinked-list maintenance while preserving correct inode-cluster buffer logging order.

Important APIs and functions: `xfs_iunlink_log_inode` allocates and attaches an `xfs_iunlink_item` to a transaction. Internal item operations include `xfs_iunlink_item_release`, `xfs_iunlink_item_sort`, `xfs_iunlink_log_dinode`, and `xfs_iunlink_item_precommit`. `xfs_iunlink_cache` is the slab cache for these log items.

Control flow: callers request a next-agino update for an inode. The function verifies old and new AG inode values, rejects non-null self-links, allocates a log item, records the inode, per-AG reference, old pointer, and new pointer, joins it to the transaction, marks it dirty, and returns. During transaction precommit, the item maps the inode cluster buffer, skips stale buffers, verifies the on-disk old pointer still matches the expected value, writes the new pointer, recalculates the dinode CRC, logs only the field range, removes itself from the transaction, and releases resources.

State and persistence: this file updates persistent `di_next_unlinked` fields in inode cluster buffers as part of transaction commit. It holds a passive perag reference until release and intentionally avoids relogging stale inode buffers because doing so could clear stale state during inode cluster freeing.

Dependencies and integration: integrates with XFS transaction log items, inode mapping, per-AG lifetime management, dinode verifiers/CRC, tracepoints, and unlinked-list code that tracks `ip->i_next_unlinked`.

Risks and test signals: list corruption risk is managed by old-pointer verification and self-link rejection. Stale-buffer handling is delicate because relogging a stale cluster can resurrect freed metadata. Tests should cover unlink/inactive transactions, unlinked-list recovery, inode cluster freeing, corrupted old pointer detection, null termination, perag lifetime, and transaction precommit ordering across multiple inode clusters.
