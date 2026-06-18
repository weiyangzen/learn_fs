# Research: subset-b-005802

## Source set

- `sources/distributed-fs/ceph-client/fs/xfs/xfs_trace.h`
- `sources/distributed-fs/ceph-client/fs/xfs/xfs_trans.c`
- `sources/distributed-fs/ceph-client/fs/xfs/xfs_trans.h`

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_trace.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_trace.h

## Purpose

`xfs_trace.h` is the XFS tracepoint catalog for this kernel tree. It defines the `TRACE_SYSTEM xfs` trace events consumed by XFS metadata, transaction, allocation, recovery, realtime, health monitoring, and IO paths. The header is not a stable ABI; it is a diagnostic contract between XFS code and Linux ftrace/perf/BPF tooling. The file is source-tree-central: many XFS modules include `xfs_trace.h` and call generated `trace_xfs_*` functions, while this header controls event payloads, symbolic formatting, and tracepoint generation through `<trace/define_trace.h>`.

## Important APIs, Types, and Event Families

- Trace macros: `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TRACE_DEFINE_ENUM`, and local wrapper macros such as `DEFINE_BUF_EVENT`, `DEFINE_TRANS_EVENT`, `DEFINE_ALLOC_EVENT`, `DEFINE_DEFER_EVENT`, and `DEFINE_HEALTHMON_EVENT`.
- Forward declarations cover most XFS runtime types observed by tracepoints: `xfs_mount`, `xfs_trans`, `xfs_log_item`, `xfs_buf`, `xfs_inode`, `xfs_btree_cur`, `xfs_perag`, `xfs_group`, `xfs_rtgroup`, deferred intent structures, fsmap records, health monitor records, and log recovery records.
- Transaction and log observability is concentrated in `xfs_trans_resv_class`, `xfs_trans_class`, `xfs_loggrant_class`, `xfs_log_item_class`, `xfs_ail_class`, `xlog_iclog_class`, and log recovery classes.
- Buffer transaction events use `xfs_buf_item_class` and define `xfs_trans_get_buf`, `xfs_trans_get_buf_recur`, `xfs_trans_getsb`, `xfs_trans_getsb_recur`, `xfs_trans_read_buf`, `xfs_trans_read_buf_recur`, `xfs_trans_log_buf`, `xfs_trans_brelse`, `xfs_trans_bdetach`, `xfs_trans_bjoin`, `xfs_trans_bhold`, `xfs_trans_bhold_release`, and `xfs_trans_binval`.
- Filesystem operation coverage includes attribute listing, directory/attribute btrees, inode locks and references, bmap updates, allocation, extent busy tracking, discard, btree cursor activity, rmap/refcount/deferred intents, reflink, fsmap, metadata directory updates, in-memory btrees, exchange-range/exchange-mapping, parent pointers, quota, blockgc/inodegc, realtime zones, free counter reservations, shutdown, health monitor, and media verification.

## Control Flow and Generated Code

The header follows the standard Linux tracepoint pattern: each event class declares a payload schema in `TP_STRUCT__entry`, fills it in `TP_fast_assign`, and formats it in `TP_printk`. `DEFINE_EVENT` instances bind concrete event names to reusable schemas. Inclusion is guarded by `_TRACE_XFS_H` and `TRACE_HEADER_MULTI_READ`; at the end it sets `TRACE_INCLUDE_PATH .`, `TRACE_INCLUDE_FILE xfs_trace`, and includes `<trace/define_trace.h>` to emit tracepoint definitions in the one translation unit that defines tracepoints.

Runtime XFS code does not call these macros directly. It calls generated functions such as `trace_xfs_trans_alloc`, `trace_xfs_trans_commit`, `trace_xfs_trans_free_abort`, `trace_xfs_buf_item_format`, `trace_xfs_log_reserve`, and `trace_xfs_force_shutdown`. The event definitions determine which fields are copied before the event is written, so tracepoints must not dereference invalid objects or sleep. Many event classes intentionally snapshot refcounts, flags, AG numbers, inode numbers, LSNs, and caller IPs so later analysis can reconstruct state transitions.

## State and Persistence Behavior

The file itself persists no filesystem state. Its importance is observational: tracepoint payloads capture transient state from persistent subsystems. For transactions, it records ticket ids, transaction flags, reservation sizes, log grant head/tail positions, log item types, LSNs, AIL moves, and CIL/log force activity. For allocation and metadata btrees, it records block numbers, lengths, owner information, record states, and error call sites. For health monitoring, it records event insertion, merge/drop behavior, corruption/sickness domains, shutdown flags, media addresses, and file IO errors.

Trace payload schemas matter for postmortem test and production diagnostics because they decide which pieces of in-core state survive into trace logs. Several events use symbolic flag tables such as `XFS_LI_FLAGS`, `XFS_BUF_FLAGS`, `XFS_DQTYPE_STRINGS`, `XFS_RMAP_INTENT_STRINGS`, `XFS_REFCOUNT_INTENT_STRINGS`, `XFS_HEALTHMON_TYPE_STRINGS`, and `XFS_FREECOUNTER_STR` to make bitfields readable.

## Dependencies and Integration Points

The header depends on Linux tracepoint infrastructure and many XFS-private data structures and flag string tables defined in surrounding headers. It is included by implementation files across `fs/xfs`, including transaction code that emits `trace_xfs_trans_resv_calc`, `trace_xfs_trans_alloc`, `trace_xfs_trans_cancel`, `trace_xfs_trans_commit`, `trace_xfs_trans_dup`, `trace_xfs_trans_free`, `trace_xfs_trans_roll`, `trace_xfs_trans_add_item`, and `trace_xfs_trans_free_items`.

It integrates with conditional feature blocks: realtime/zoned events under `CONFIG_XFS_RT`, intent draining under `CONFIG_XFS_DRAIN_INTENTS`, memory buffer events under `CONFIG_XFS_MEMORY_BUFS`, in-memory btree events under `CONFIG_XFS_BTREE_IN_MEM`, POSIX ACL and compat ioctl events under their feature guards, and tracepoint reservation dumps under `CONFIG_TRACEPOINTS` in transaction code.

## Risks and Maintenance Notes

- Tracepoint payloads can become unsafe if a caller passes partially initialized or already freed objects; schemas dereference deep fields such as `tp->t_mountp`, `bp->b_target`, `lip->li_log`, `cur->bc_ops`, and inode forks.
- Schema drift is a diagnostic compatibility risk even though the file states tracepoints are not stable ABI. BPF programs, perf scripts, and tests may still rely on field names.
- Format helpers must match units and field widths. This header documents unit conventions up front because XFS exposes many similar block units: fs blocks, allocation-group blocks, realtime extents, device blocks, bytes, file offsets, and owner ids.
- Conditional tracepoint blocks can hide compile coverage; feature-specific build configurations are needed to catch stale struct members or missing enum string tables.
- Some events use `data_race`, raw atomic reads, or unlocked snapshots intentionally. Consumers should treat them as diagnostic samples, not synchronization guarantees.

## Test Signals

Useful validation signals include successful XFS builds with `CONFIG_TRACEPOINTS`, `CONFIG_XFS_RT`, `CONFIG_XFS_MEMORY_BUFS`, `CONFIG_XFS_BTREE_IN_MEM`, and `CONFIG_XFS_DRAIN_INTENTS` combinations; boot/runtime checks that `/sys/kernel/debug/tracing/events/xfs/` exposes expected transaction, buffer, log, allocation, and health events; ftrace/perf smoke tests while creating files, allocating extents, rolling transactions, triggering quota reservations, and forcing sync commits; and compile failures after changes to XFS structs or enum tables. Transaction-specific tests should confirm `xfs_trans_*` events appear around allocation, commit, cancel, roll, and reservation calculation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_trans.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_trans.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_trans.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_trans.h

## Purpose

`xfs_trans.h` declares the kernel-only XFS transaction subsystem interface and its core shared data structures. It defines the generic log item contract, transaction state container, log item operation table, exported transaction/buffer/inode APIs, and small context helpers used by transaction allocation and release. It is the header that lets metadata code join buffers, inodes, quota items, and deferred operation items to a transaction without depending on the implementation details in `xfs_trans.c`.

## Important Types and APIs

- `struct xfs_log_item` is the common base for all loggable XFS items. It carries AIL and transaction list links, last on-disk LSN, owning log and AIL pointers, item type, atomic flag bits, optional real buffer pointer, buffer item list link, item operation table, delayed logging/CIL list links, active and shadow log vectors, commit sequence number, and CIL order id.
- Log item flags include `XFS_LI_IN_AIL`, `XFS_LI_ABORTED`, `XFS_LI_FAILED`, `XFS_LI_DIRTY`, `XFS_LI_WHITEOUT`, and `XFS_LI_FLUSHING`; `XFS_LI_FLAGS` maps them to trace strings.
- `struct xfs_item_ops` defines item-specific behavior: size calculation, log formatting, pin/unpin, stable sort key, precommit, committing, committed, AIL push, release, match, and intent lookup.
- Item operation flags `XFS_ITEM_RELEASE_WHEN_COMMITTED`, `XFS_ITEM_INTENT`, and `XFS_ITEM_INTENT_DONE` describe whether an item is released instead of AIL-tracked and whether it is an intent or intent-done item. `xlog_item_is_intent` and `xlog_item_is_intent_done` are convenience classifiers.
- `struct xfs_trans` stores log and block reservations, used reservation counters, realtime reservations, transaction flags, highest locked AGF, log ticket, mount pointer, dquot accounting pointer, staged superblock deltas, transaction item list, busy extent list, deferred operation list, and saved `memalloc_nofs` process flags.
- Exported APIs cover transaction allocation and reservation (`xfs_trans_alloc`, `xfs_trans_alloc_empty`, `xfs_trans_reserve_more`), superblock mutation (`xfs_trans_mod_sb`), buffer acquisition/read/join/log/release operations, inode joining/logging, commit/roll/cancel, AIL initialization/destruction, buffer type tagging, and transaction-aware allocation helpers for inode create/change/directory operations.

## Control Flow Contract

Callers allocate a transaction with a reservation descriptor, reserve data/realtime blocks and log space, join buffers/inodes/log items, mark items dirty, optionally stage superblock and quota deltas, then commit or cancel. Buffer helper inlines convert a single block range into `struct xfs_buf_map` and dispatch to map-based APIs. Commit and cancel are terminal; the header documents that callers must not reference the transaction afterward through the implementation comments in `xfs_trans.c`.

The log item operations table is the polymorphic control-flow hook used by the transaction and log subsystems. During commit, dirty items can be sorted by `iop_sort`, prepared by `iop_precommit`, formatted into log vectors with `iop_format`, pinned/unpinned around log IO, moved in or out of AIL by commit callbacks, pushed for writeback, and released. Intent and intent-done classification supports deferred operation recovery and matching.

## State and Persistence Behavior

`xfs_trans` separates reserved resources from used resources. `t_blk_res`/`t_blk_res_used` and `t_rtx_res`/`t_rtx_res_used` allow allocation paths to check whether transaction-local use stays within reservation and to return unused space at cancel or commit. Superblock changes are persisted indirectly: fields such as `t_icount_delta`, `t_fdblocks_delta`, `t_res_fdblocks_delta`, `t_frextents_delta`, `t_dblocks_delta`, `t_agcount_delta`, `t_rextsize_delta`, and `t_rgcount_delta` accumulate until commit code applies them to in-core counters and, when required, the logged superblock buffer.

`struct xfs_log_item` bridges in-core dirty state and persistent journal state. `li_lsn` tracks the item's on-disk log location, `li_ail` membership tracks whether writeback/tail pinning is still needed, and `li_cil`/`li_lv` fields support delayed logging in the CIL. Atomic flag updates are explicitly used because item state can race without taking the AIL lock for every flag operation.

## Dependencies and Integration Points

This header forward-declares transaction, log, buffer, mount, quota, inode, btree, and deferred intent types instead of including all definitions. It integrates with Linux list infrastructure, atomic bit operations, `memalloc_nofs_save`/`memalloc_nofs_restore`, XFS log format types, buffer maps, AIL, quota accounting, and trace flag tables. Most XFS metadata subsystems depend on this header to join objects to transactions and log modifications.

The buffer APIs declared here connect transactions with the buffer cache and verifier layer. Inode APIs connect transaction lifetime with inode locks and dirty inode logging. Allocation helpers declared at the end package transaction allocation with quota reservation and locking policies for common VFS-facing operations.

## Risks and Maintenance Notes

- `struct xfs_log_item` is embedded in many item types, so field layout and operation semantics have broad impact on CIL, AIL, recovery, and tracepoint code.
- Any new log item type must supply operations consistent with transaction ordering, pin/unpin lifetime, AIL pushing, and abort release behavior.
- `li_flags` are atomic bit flags; code must use bit helpers rather than unsynchronized plain writes.
- Transaction reservation fields are unsigned and can overflow if replenishment paths do not bound additions; implementation code uses explicit caps for some cases.
- Context helpers save and restore `memalloc_nofs` state; every allocation path that sets the context must clear it exactly once during transaction free.
- Buffer and inode helper ownership semantics are subtle: joined locks are released by commit/cancel, while helper comments define cases where callers remain responsible for unlocks after allocation failures.

## Test Signals

Header-level changes should be validated by full XFS build coverage, sparse/compiler warnings for operation table signature mismatches, runtime tests that exercise each public transaction helper, lockdep tests for inode and buffer join/unlock behavior, tracepoint builds that consume `XFS_LI_FLAGS`, and fault-injection tests around commit/cancel to ensure item release, AIL/CIL state, and reservation fields remain consistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_trans.h -->
