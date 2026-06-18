# sources/distributed-fs/ceph-client/fs/xfs/xfs_trans.c

## Purpose

`xfs_trans.c` implements the core XFS transaction lifecycle: reservation calculation initialization, transaction allocation, resource reservation, superblock delta staging and application, log item attachment and release, commit, cancel, roll, and convenience allocators for inode, inode-create, inode-change, and directory operations. It is the central coordinator between the log, free-space counters, realtime extent counters, quota reservations, deferred operations, buffers/inodes/log items, freeze protection, and transaction tracing.

## Important APIs and Functions

- `xfs_trans_init` computes mount transaction reservations with `xfs_trans_resv_calc` and optionally traces each reservation via `trace_xfs_trans_resv_calc`.
- `__xfs_trans_alloc`, `xfs_trans_alloc`, and `xfs_trans_alloc_empty` allocate `struct xfs_trans` from `xfs_trans_cache`, establish `memalloc_nofs` context, take freeze write protection unless `XFS_TRANS_NO_WRITECOUNT` is set, initialize item/busy/defer lists, and reserve log/blocks/realtime extents when requested.
- `xfs_trans_reserve` reserves data blocks with `xfs_dec_fdblocks`, log space with `xfs_log_reserve`, and realtime extents with `xfs_dec_frextents`, unwinding in reverse order on failure.
- `xfs_trans_mod_sb`, `xfs_trans_apply_sb_deltas`, and `xfs_trans_unreserve_and_mod_sb` stage, log, release, and apply superblock counter and geometry changes.
- `xfs_trans_add_item`, `xfs_trans_del_item`, `xfs_trans_free_items`, `xfs_trans_precommit_sort`, and `xfs_trans_run_precommits` manage transaction log item membership, dirty flags, abort flags, item release callbacks, and deterministic precommit ordering.
- `xfs_trans_commit`, `__xfs_trans_commit`, `xfs_trans_cancel`, and `xfs_trans_roll` implement final commit, low-level commit with optional ticket regrant, abort/cancel, and rolling permanent transactions.
- Higher-level helpers `xfs_trans_alloc_inode`, `xfs_trans_reserve_more`, `xfs_trans_reserve_more_inode`, `xfs_trans_alloc_icreate`, `xfs_trans_alloc_ichange`, and `xfs_trans_alloc_dir` package common lock/quota/retry patterns for inode and directory update callers.

## Control Flow

Allocation starts in `xfs_trans_alloc`: allocate the transaction before freeze accounting to avoid lockdep false positives, reserve blocks/log/realtime extents, retry once after `xfs_blockgc_flush_all` on filesystem ENOSPC, then return the initialized transaction. Empty transactions skip reservation and are intended only for metadata reads that must avoid deadlock against corrupt self-referential structures.

Commit starts in `xfs_trans_commit`, which finishes deferred operations for permanent-log-reservation transactions with `xfs_defer_finish_noroll`. `__xfs_trans_commit` then applies staged superblock and quota deltas, sorts and runs dirty item precommit callbacks, exits early for clean transactions, refuses dirty commits after log shutdown, commits dirty transactions through `xlog_cil_commit`, frees the transaction, and optionally forces the log for `XFS_TRANS_SYNC`. Clean/error paths unreserve counters and dquots, regrant or ungrant the log ticket depending on roll state, release items, free the transaction, and count an empty transaction.

Cancel handles dirty state more aggressively. Deferred operations attached to a cancelled transaction are treated as dirty and cancelled. If a dirty transaction is cancelled before the mount is already shut down, `xfs_force_shutdown(..., SHUTDOWN_CORRUPT_INCORE)` is triggered because dirty in-core metadata cannot be restored safely. It then unreserves superblock and quota state, ungrants the ticket, marks items aborted on dirty cancel, releases items, and frees the transaction.

Rolling a permanent transaction duplicates the reservation state with `xfs_trans_dup`, moves unused block/realtime reservation and deferred ops to the new transaction, commits the old transaction with regrant semantics, restores `memalloc_nofs` context, and calls `xfs_log_regrant` on the copied ticket. This lets long deferred operation chains commit chunks without dropping the logical reservation.

## State and Persistence Behavior

The transaction object accumulates transient deltas for superblock counters and geometry fields. `xfs_trans_mod_sb` marks transactions dirty and, except for lazy superblock counter cases, superblock-dirty. Negative free-block deltas consume reserved blocks and are checked against `t_blk_res`; overconsumption forces shutdown. Positive free-block deltas can replenish the transaction reservation when `XFS_TRANS_RES_FDBLKS` is set. Realtime extent deltas behave similarly, with `xfs_has_rtgroups` changing whether frextents are treated as lazy.

On commit, `xfs_trans_apply_sb_deltas` logs the superblock buffer when persistent superblock fields must change. It logs either the contiguous counter range or the full superblock for noncontiguous geometry updates. It also updates incore device target sector counts for growfs-like `dblocks` and `rblocks` changes and recomputes realtime group block-log fields when realtime extent size changes. `xfs_trans_unreserve_and_mod_sb` releases unused reserved blocks/extents and updates in-core counters under the proper per-cpu counter or superblock spinlock paths.

Log item state is tracked with `li_trans` list membership and `XFS_LI_DIRTY`/`XFS_LI_ABORTED` flags. The commit path hands dirty items to the CIL; the clean/error paths call item release methods directly. Dirty cancellation marks items aborted before release so item-specific cleanup can avoid writing inconsistent metadata.

## Dependencies and Integration Points

The file depends on log management (`xfs_log_reserve`, `xfs_log_ticket_ungrant`, `xfs_log_ticket_regrant`, `xfs_log_regrant`, `xlog_cil_commit`, `xlog_is_shutdown`, `xfs_log_force_seq`), free-space counters (`xfs_dec_fdblocks`, `xfs_add_fdblocks`, `xfs_dec_frextents`, `xfs_add_frextents`), quota accounting (`xfs_trans_apply_dquot_deltas`, `xfs_trans_unreserve_and_mod_dquots`, quota reservation helpers), deferred ops (`xfs_defer_finish_noroll`, `xfs_defer_move`, `xfs_defer_cancel`), extent busy cleanup, inode locks, blockgc flushing, realtime helpers, superblock helpers, and tracepoints from `xfs_trace.h`.

Higher-level XFS operations integrate through helper allocators. Inode update paths use `xfs_trans_alloc_inode` to allocate, lock, join, attach dquots, reserve quota, and retry after quota blockgc. Inode creation reserves against supplied dquots. Ownership changes reserve quota for target dquots, including delayed allocation and realtime accounting. Directory updates can fall back to reservationless operation, communicating the space error through `nospace_error` and setting `*dblocks` to zero.

## Risks and Edge Cases

- Reservation unwind must stay exact. Any failure path that forgets to ungrant log space, return fdblocks/frextents, or undo quota reservations can leak global resources or corrupt accounting.
- Dirty transaction cancellation is intentionally fatal. Callers using `xfs_trans_reserve_more` must only do so while they can still cancel cleanly on ENOSPC.
- Precommit callbacks run after metadata is dirty; errors force shutdown because recovery is not possible at that point.
- `xfs_trans_dup` transfers writer-count responsibility by setting `XFS_TRANS_NO_WRITECOUNT` on the old transaction and carrying it on the new transaction. Mistakes here can break freeze synchronization.
- Lazy superblock counters and realtime group feature gates create different persistence behavior; tests need both old and new filesystem formats.
- Directory and quota retry paths drop and reacquire locks; callers must honor documented lock ownership and not assume inode dquots are unchanged across retries.

## Test Signals

Relevant tests include transaction allocation/commit/cancel/roll coverage under log pressure, ENOSPC, EDQUOT, freeze, and shutdown; xfstests for quota reservation retries, directory fallback without block reservation, realtime allocations, growfs superblock updates, deferred operation chains, and dirty-cancel shutdown behavior; tracing checks for `xfs_trans_alloc`, `xfs_trans_commit`, `xfs_trans_cancel`, `xfs_trans_roll`, `xfs_trans_free`, and log grant events; and accounting assertions that fdblocks, frextents, quota reservations, and superblock counters match before and after forced failures.
