<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/log.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/log.c

## Purpose
`log.c` owns GFS2's in-memory journal accounting and log flush machinery. It reserves journal and revoke space, merges committed transactions into the incore system transaction, writes log headers, advances the log head and tail, drains the active item lists, handles ordered-data writeout, and runs the `gfs2_logd` background thread.

## Important APIs, types, and functions
External functions include `gfs2_struct2blk`, `gfs2_log_is_empty`, `gfs2_log_release_revokes`, `gfs2_log_release`, `gfs2_log_try_reserve`, `gfs2_log_reserve`, `gfs2_write_log_header`, `gfs2_remove_from_journal`, `gfs2_log_flush`, `gfs2_log_commit`, `gfs2_ail1_flush`, `log_flush_wait`, `gfs2_add_revoke`, `gfs2_glock_remove_revoke`, `gfs2_flush_revokes`, `gfs2_ail_drain`, and `gfs2_logd`. Key internal helpers are `gfs2_ail1_start_one`, `gfs2_ail1_empty_one`, `log_pull_tail`, `gfs2_ordered_write`, `gfs2_ordered_wait`, `log_write_header`, `__gfs2_log_flush`, `gfs2_merge_trans`, `log_refund`, and threshold predicates for journal and AIL flushing.

## Control Flow
Transactions reserve space through `gfs2_log_try_reserve` or `gfs2_log_reserve`; revoke reservations are accounted separately through `sd_log_revokes_available`, while log block reservations use `sd_log_blks_free` and `sd_log_blks_needed`. `gfs2_log_commit` refunds unused reservation, attaches or merges the transaction into `sd_log_tr`, recalculates reserved blocks with `calc_reserved`, and wakes `gfs2_logd` when pinned or occupied log blocks cross thresholds.

`gfs2_log_flush` takes `sd_log_flush_lock` and runs `__gfs2_log_flush`. The flush snapshots `sd_log_head`, detaches `sd_log_tr`, reserves minimal flush space if necessary, performs ordered-data writeout, calls `lops_before_commit` to write descriptors and payloads, submits pending journal bios, writes a log header if the log moved or the tail needs advancing, and then calls `lops_after_commit` to unpin buffers and put them on the AIL. Non-normal flushes can force AIL drain, write an additional header, and shut down the journal. On error or withdraw, pending bios are errored, pinned transaction buffers are drained, and the transaction is put on AIL1 so `gfs2_ail_drain` can free it.

AIL management is two-stage. AIL1 contains transaction buffers that still need in-place writeback; once clean, they move to AIL2. `log_pull_tail` empties AIL2 entries whose `tr_first` is behind the new tail and releases log blocks. `gfs2_ail1_flush` starts writeback by mapping buffers back to their inode address spaces and calling either journaled-data or normal writepages. `gfs2_ail1_empty` moves completed buffers, optionally turning eligible completed items into revokes. The background `gfs2_logd` wakes on thresholds or timeouts, performs journal flushes and AIL writeback, and exits on withdraw or kthread stop.

## State and Persistence
Persistent state is the journal stream: log descriptors, metadata/data payloads, revoke blocks, and log headers with sequence, tail, flags, physical address, journal inode, local statfs changes, hash, and CRC. In-memory state includes `sd_log_head`, `sd_log_tail`, `sd_log_flush_head`, `sd_log_flush_tail`, `sd_log_sequence`, `sd_log_tr`, `sd_log_blks_reserved`, `sd_log_num_revoke`, `sd_log_revokes`, `sd_log_ordered`, `sd_ail1_list`, `sd_ail2_list`, and atomic counters for free, needed, pinned, in-flight, and revoke-available blocks.

## Dependencies and Integration Points
`log.c` calls the log operation table in `lops.c`, writes pages through `gfs2_log_write`, uses metadata and bmap helpers, touches glock state and revoke counts, drives ordered writeback for data mode, and integrates with transaction lifecycle in `trans.c`. It is called from glock demotion paths, file sync paths, remount/read-only conversion, freeze, kill-superblock, quota sync, statfs, and recovery clean-up.

## Risks
Journal accounting is corruption-sensitive: `used_blocks` must match reserved blocks, revoke slack must align with descriptor capacity, and `GFS2_LOG_FLUSH_MIN_BLOCKS` protects logd from self-deadlock. AIL flushes can loop for a long time if buffers stay dirty or locked; ten-minute diagnostics and withdraw paths guard this. Barrier-disabled mode relies on ordered wait and log write completion instead of flush/FUA. Error handling must drain pinned buffers and pending transactions without double-freeing bufdata. Freeze and read-only recovery paths constrain which transactions and revokes may be flushed.

## Test Signals
Exercise transaction reservation/refund, forced log flush, sync flush, shutdown flush, freeze flush, barrier and nobarrier modes, AIL tail advancement, revoke-heavy block frees, ordered-data write ordering, journal write I/O errors and withdraw, logd threshold wakeups, unmount with nonempty AIL, and tracepoints for log block accounting and flush start/end.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/log.c -->
