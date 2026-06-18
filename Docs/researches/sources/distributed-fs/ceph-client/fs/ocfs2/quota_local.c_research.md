# sources/distributed-fs/ceph-client/fs/ocfs2/quota_local.c

## Purpose
`quota_local.c` manages per-slot OCFS2 local quota files. Local files record this node's quota usage deltas and dquot references so ordinary filesystem operations can update quota state cheaply, then synchronize or recover those deltas into the clustered global quota files.

## Important APIs, types, and functions
The public entry points are `ocfs2_begin_quota_recovery`, `ocfs2_finish_quota_recovery`, `ocfs2_free_quota_recovery`, `ocfs2_local_write_dquot`, `ocfs2_create_local_dquot`, `ocfs2_local_release_dquot`, and `ocfs2_quota_format`. Internal helpers define the local-file layout (`ol_quota_entries_per_block`, `ol_chunk_blocks`, `ol_quota_chunk_block`, `ol_dqblk_off`), modify quota blocks transactionally (`ocfs2_modify_bh`), validate both local and global headers, load chunk bitmaps, extend the local quota file, and recover dirty chunks from crashed slots.

## Control flow
Quota activation calls `ocfs2_local_read_info`: it allocates `ocfs2_mem_dqinfo`, reads global info, locks the local quota inode, reads the local header, loads chunk headers into memory, captures recovery data if the local file was not marked clean, and marks the file dirty for active use. Creating a dquot tries to reserve a free bitmap entry, extends the last chunk or creates a new chunk if necessary, records physical block location, writes the local dquot delta entry, then marks the bitmap bit. Local writes update `dqb_spacemod` and `dqb_inodemod` from current usage minus the globally synchronized origins. Release clears the chunk bitmap bit within the caller's transaction. Recovery first snapshots dirty chunk bitmaps for a failed slot, then later locks the local quota file, replays each recorded local delta into the matching global dquot, releases the crashed node's global dquot reference, clears local bits, and marks the recovered file clean.

## State and persistence
Local quota files persist an info block, per-chunk bitmap headers, and `ocfs2_local_disk_dqblk` delta records. In memory, `ocfs2_mem_dqinfo` owns loaded chunk headers, local info buffers, dirty/clean flags, block and chunk counts, and optional recovery lists. `OLQF_CLEAN` is the key persistence signal for whether local deltas require replay after a crash.

## Dependencies and integration points
The file integrates with the Linux quota format layer through `quota_format_ops`, with `quota_global.c` for global reads/writes and dquot release, with OCFS2 system-file lookup for per-slot quota inodes, and with journaling, inode locks, metadata validation, and extent mapping. Recovery is tied into OCFS2 journal replay and slot recovery.

## Risks and test signals
Risks include bitmap/header divergence, partial local-file extension, unclean shutdown with stale chunk snapshots, holding or missing `ip_alloc_sem` around quota-file growth, incorrect signedness when replaying deltas, and marking a live local file clean. Test signals include quota enable/disable cycles, exhaustion of local chunk entries, extending local files across chunks, crash recovery of dirty local quota files, concurrent dquot create/release, corrupt header detection, and recovery races where another node already holds the local quota lock.
