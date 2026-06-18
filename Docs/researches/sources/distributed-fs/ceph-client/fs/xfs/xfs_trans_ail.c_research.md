# sources/distributed-fs/ceph-client/fs/xfs/xfs_trans_ail.c

## Purpose
`xfs_trans_ail.c` implements the XFS Active Item List, the ordered list of dirty log items whose on-disk metadata writeback controls log tail advancement. It also runs `xfsaild`, the background thread that pushes dirty metadata buffers toward disk so log space can be reclaimed.

## Important APIs, types, and functions
The file operates on `struct xfs_ail`, `struct xfs_log_item`, and `struct xfs_ail_cursor` from `xfs_trans_priv.h`. Public entry points include `xfs_trans_ail_init`, `xfs_trans_ail_destroy`, `xfs_ail_min_lsn`, `xfs_trans_ail_update_bulk`, `xfs_trans_ail_insert`, `xfs_ail_delete_one`, `xfs_trans_ail_delete`, `xfs_ail_update_finish`, `xfs_ail_push_all_sync`, and AIL cursor helpers. The daemon path centers on `xfsaild`, `xfsaild_push`, `xfsaild_process_logitem`, `xfsaild_push_item`, and `xfs_ail_calc_push_target`.

## Control flow
Mount setup allocates an AIL, initializes lists, locks, wait queues, delayed-write buffer list, and starts `xfsaild`. Committed log items are inserted or repositioned by `xfs_trans_ail_update_bulk` under `ail_lock` in LSN order. Deletion clears `XFS_LI_IN_AIL`, invalidates active cursors, recalculates the log tail if the minimum LSN changed, and wakes log-space waiters. `xfsaild` sleeps when no work exists, computes a push target based on log occupancy or explicit push-all requests, walks the AIL with cursor invalidation protection, calls item `iop_push` methods, submits delayed write buffers, and backs off according to lock contention, pinned items, or flushing pressure.

## State and persistence
AIL state is in-memory but represents committed log items whose metadata has not reached stable storage. Persistent consequences appear through log tail updates, buffer writeback, and recovery ordering. `ail_target`, `ail_last_pushed_lsn`, `ail_log_flush`, cursor invalidation bits, and `ail_buf_list` are runtime control state. `atomic64_set(&log->l_tail_lsn)` and `l_tail_space` update log accounting after AIL changes.

## Dependencies and integration points
The file integrates with the xlog/CIL layer, item operation vectors, buffer delayed writeback, kthreads/freezer, XFS stats and tracepoints, error tags, shutdown handling, and log-space wakeups. Items without push callbacks are treated as pinned so the CIL can be forced.

## Risks and test signals
Risk concentrates in list ordering, cursor invalidation under item removal, lock dropping by item push callbacks, use-after-free after `iop_push`, failed buffer resubmission ordering, and tail LSN correctness. Test signals include debug AIL ordering checks, forced pinned-item errortags, shutdown during delayed write submission, push-all sync drain, concurrent insert/delete traversal, log-space exhaustion workloads, and metadata IO error recovery.
