# sources/distributed-fs/ceph-client/fs/xfs/xfs_buf_item_recover.c

Purpose: Replays buffer log items during XFS recovery, including freed-buffer cancellation, metadata LSN skip logic, verifier attachment, inode-buffer unlinked-list replay, dquot buffer suppression after quotaoff, and primary superblock growfs updates.

Important APIs, types, and functions: Defines cancel table state `struct xfs_buf_cancel`, `xlog_is_buffer_cancelled()`, `xlog_alloc_buf_cancel_table()`, and `xlog_free_buf_cancel_table()`. Recovery item ops are `xlog_buf_item_ops`; core helpers include `xlog_recover_validate_buf_type()`, regular/dquot/inode buffer replay, primary superblock replay, and `xlog_recover_get_buf_lsn()`.

Control flow: Pass 1 records `XFS_BLF_CANCEL` items with refcounts. Pass 2 skips cancelled buffers, reads uncancelled buffers, compares on-disk metadata LSNs to the current transaction, and replays only if needed. Regular replay copies dirty bitmap chunks; inode buffer replay copies only `di_next_unlinked`; dquot replay obeys quotaoff state; primary superblock replay refreshes in-core mount geometry.

State and persistence: Mutates recovered metadata buffers and queues them for delayed writeback with `_XBF_LOGRECOVERY`. Cancel records are transient. CRC filesystems get buffer ops and temporary BLIs to stamp correct LSNs during write verification.

Dependencies and integration points: Uses log recovery reorder lists, buffer cache, metadata verifiers, quotaoff recovery, inode unlinked-list handling, superblock/perag/rtgroup initialization, and AIL cleanup.

Risks and test signals: Key risks are stale metadata replay over reused blocks, wrong LSN/UUID skip decisions, verifier omissions after readahead, inode-buffer over-replay, and growfs replay errors. Test interrupted recovery, buffer reuse after cancellation, quotaoff with pending dquots, CRC/non-CRC filesystems, inode unlinked recovery, and rt metadata.
