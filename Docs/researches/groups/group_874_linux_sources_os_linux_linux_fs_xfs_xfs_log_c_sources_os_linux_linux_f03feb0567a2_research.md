# Group Research: XFS log manager and CIL checkpointing

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux`; this grouped report covers exactly the four requested XFS log files. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_log.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_log.c

## Purpose

`xfs_log.c` is the central XFS log manager implementation. It owns log allocation and teardown, log-space reservation grant heads, in-core log buffer (`iclog`) state transitions, physical log writes, log forcing, clean unmount record writing, log covering, shutdown propagation, and LSN validation.

This file bridges transaction/CIL code and the block layer: callers reserve or regrant tickets, `xlog_write()` copies formatted log vectors into iclogs, iclog state transitions eventually submit bios to the log device, and completion callbacks move committed CIL contexts into the AIL.

## Major Responsibilities

- Mount-time log setup in `xfs_log_mount()`: allocate `struct xlog`, validate minimum log size, initialize AIL, perform recovery unless `norecovery`, create sysfs state, clear active recovery, and initialize CIL post-recovery.
- Recovery finish/cancel paths in `xfs_log_mount_finish()` and `xfs_log_mount_cancel()`.
- Unmount/quiesce paths: `xfs_log_quiesce()`, `xfs_log_clean()`, `xfs_log_unmount()`, and unmount-record writing through `xfs_log_unmount_write()` / `xlog_unmount_write()`.
- Reservation grant accounting: `xfs_log_reserve()`, `xfs_log_regrant()`, `xfs_log_ticket_regrant()`, `xfs_log_ticket_ungrant()`, and helpers around reserve/write grant heads.
- In-core log buffer ring management: allocation, state changes, space acquisition, sync submission, completion, activation, callback running, and shutdown cleanup.
- Log writing: `xlog_write()`, `xlog_write_one_vec()`, full/partial log-vector copying, continuation opheaders, record counts, ticket accounting, and split-region handling across iclogs.
- Physical IO: cycle stamping, log checksum calculation, optional split writes across physical log wrap, block-layer bio submission, preflush/FUA handling, external-log data-device flush ordering, and async IO-end workqueue callback.
- Log force APIs: `xfs_log_force()` and `xfs_log_force_seq()` force current iclogs or CIL checkpoint sequences to stable storage.
- Forced shutdown: `xlog_force_shutdown()` serializes shutdown, optionally forces the log first, marks log/mount shutdown, wakes grant/CIL/iclog waiters, processes callbacks, and wakes zoned RT waiters.
- LSN validity: `xfs_log_check_lsn()` warns when metadata LSNs are ahead of the current log head.

## Key Data Flow

1. Transaction code obtains a `struct xlog_ticket` via `xfs_log_reserve()`.
2. CIL or direct log code passes a chain of `struct xfs_log_vec` to `xlog_write()`.
3. `xlog_state_get_iclog_space()` chooses the current active iclog, stamps a header LSN on first use, reserves space, and may switch full iclogs to `WANT_SYNC`.
4. `xlog_write_full()` or `xlog_write_partial()` copies log iovecs into the iclog data area, adding continuation opheaders when a region spans iclogs.
5. `xlog_state_release_iclog()` drops the writer reference. If this was the last reference and the iclog wants sync, it transitions to `SYNCING` and calls `xlog_sync()`.
6. `xlog_sync()` rounds the record size, cycle-stamps 512-byte blocks, records the tail LSN, computes CRC, and submits the write with `xlog_write_iclog()`.
7. IO completion queues `xlog_ioend_work()`, which calls `xlog_state_done_syncing()`.
8. Completion state processing runs CIL callbacks via `xlog_cil_process_committed()`, cleans dirty iclogs back to active order, wakes waiters, and advances covering state.

## Important Functions and Mechanics

- `xlog_grant_space_left()` calculates available grant space as log size minus tail-pinned bytes minus grant-head usage. It has an explicit read barrier paired with CIL AIL insertion so grant head and tail updates are observed in the right order.
- `xlog_grant_head_check()` implements the fast path for log-space reservations without taking the grant-head lock unless waiters exist or free space is insufficient.
- `xlog_grant_head_wait()` sleeps uninterruptibly, pushes the AIL to free log space, and exits with `-EIO` on shutdown.
- `xfs_log_writable()` rejects writes for norecovery mounts, read-only data/log devices, or shutdown logs, while allowing readonly mounts to perform internal recovery/unmount operations.
- `xlog_force_iclog()` marks an iclog for preflush and FUA, switches active iclogs when needed, and releases it for syncing.
- `xlog_wait_on_iclog()` waits on `ic_force_wait` unless the iclog is already active/dirty or the log is shut down.
- `xlog_state_switch_iclogs()` marks the current iclog `WANT_SYNC`, stamps previous-block linkage, advances the log head block/cycle with wrap handling, and moves the ring head to the next iclog.
- `xlog_force_and_check_iclog()` handles synchronous or very fast async devices by detecting if the iclog completed and was reused before the force caller starts waiting.
- `xlog_calc_unit_res()` computes transaction reservation overhead for opheaders, transaction headers, iclog headers, split records, commit record headers, and roundoff padding.
- `xlog_ticket_alloc()` allocates ticket state from `xfs_log_ticket_cache`, initializes reservation counts, random transaction id, and permanent-reservation flag.
- Debug-only `xlog_verify_tail_lsn()` and `xlog_verify_iclog()` check log-space safety, iclog ring integrity, magic numbers, client ids, and operation lengths before IO.

## State Machines and Invariants

- Iclog states flow through `ACTIVE -> WANT_SYNC -> SYNCING -> DONE_SYNC -> CALLBACK -> DIRTY -> ACTIVE`, with `DIRTY` iclogs reactivated only in ring order to preserve log ordering.
- `ic_refcnt` prevents an iclog from being synced while writers are still copying data. Last release of a `WANT_SYNC` iclog submits IO.
- `XLOG_ICL_NEED_FLUSH` and `XLOG_ICL_NEED_FUA` enforce stable-storage ordering for forced log records and CIL checkpoint commits.
- Log covering uses `XLOG_STATE_COVER_IDLE/NEED/DONE/NEED2/DONE2`. Two dummy superblock transactions are used to move the on-disk tail past potentially replayable allocation transactions when the filesystem becomes idle.
- `xlog_state_release_iclog()` records the current log tail into the iclog header when the iclog first needs FUA or wants sync, and avoids later changes to preserve checkpoint ordering.
- Log head updates on wrap write `l_curr_block` before incrementing `l_curr_cycle`; this ordering supports lockless validation in `xlog_valid_lsn()`.
- Shutdown state is protected by `XLOG_SHUTDOWN_STARTED` and `XLOG_IO_ERROR`, and much of the iclog state machine assumes shutdown cannot change while `l_icloglock` is held.

## Error and Shutdown Behavior

- IO errors, injected IO errors, failed external-log data-device flushes, or injected CRC failures force shutdown with `SHUTDOWN_LOG_IO_ERROR`.
- Reservation failures after shutdown return `-EIO`; tickets are zeroed so cancel/ungrant paths do not return bogus reservation space.
- `xlog_state_shutdown_callbacks()` processes callbacks only for unreferenced iclogs, wakes force/write/flush waiters, and is re-run by last iclog release if a referenced iclog delayed callback processing.
- `xlog_force_shutdown()` avoids log force for recovery or log IO error shutdowns, wakes grant queues and CIL wait queues, runs pending callbacks, and marks the mount shutdown if needed.
- `xfs_log_mount_finish()` asserts that a failed recovery finish leaves the log shut down.

## Dependencies and Coupling

- Uses CIL interfaces from `xfs_log_cil.c` for checkpoint flushing, commit callback processing, and empty checks.
- Uses AIL functions to push pinned metadata, insert committed items indirectly via callbacks, and update log tail/free space.
- Uses block-layer `bio`, `REQ_PREFLUSH`, `REQ_FUA`, `REQ_META`, and optional bio splitting for physical log wrap.
- Uses mount/superblock helpers for log geometry, lazysb counters, log incompat feature clearing, read-only checks, health flags, and sysfs registration.
- Uses tracepoints and XFS stats extensively around grant, force, iclog, and unmount paths.

## Notable Edge Cases

- External log devices require flushing the data device before log IO if the iclog has `NEED_FLUSH`, because metadata writeback covered by the LSN must be stable before the external log record.
- Log writes that straddle the physical end of the log are split into two bios and have cycle numbers adjusted for the wrapped portion.
- Partial region writes must never create an empty first continuation segment, because recovery would skip it and mis-associate continuation data.
- `xfs_log_unmount_write()` deliberately skips clean unmount records if summary counters are sick or an error tag requests summary recalculation, forcing next-mount recovery.
- `xfs_log_check_lsn()` treats norecovery and NULL LSNs as valid, but warns when metadata appears ahead of the current log head.

## Research Notes

This file is the durability-critical path for XFS metadata journaling. Correctness depends on three ordering layers working together: grant-head accounting vs. AIL tail updates, CIL checkpoint ordering vs. iclog callback order, and block-device cache ordering via preflush/FUA. The implementation prefers global ordering through the iclog ring rather than out-of-order reuse of free iclogs, simplifying recovery assumptions at the cost of potential sleeps when all iclogs are in flight.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_log.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_log.h

## Purpose

`xfs_log.h` is the public-ish XFS log manager header used by transaction, recovery, and filesystem code outside the private log implementation. It defines log region type constants, small formatting helpers, LSN comparison, log force flags, and declarations for log lifecycle, reservation, forcing, CIL callback, and shutdown APIs.

## Region Type Definitions

The file defines `XLOG_REG_TYPE_*` constants used in `struct xfs_log_iovec.i_type` to identify log payload regions. Types cover buffers, inode formats and forks, quota records, transaction/log-record headers, unmount and commit records, inode create records, reverse-mapping intent/done records, refcount intent/done records, block mapping intent/done records, attribute intent/done/name/value records, and exchange-range intent/done records.

`XLOG_REG_TYPE_MAX` is `34`, matching the highest region constant in this header. `XFS_LOG_VEC_ORDERED` is `-1`, used by item sizing code to mean an ordered item that must be tracked for ordering/unpinning but has no data regions to write.

## Formatting Helpers

- `xlog_calc_iovec_len(int len)` rounds arbitrary payload sizes to `uint32_t` alignment for log iovec storage.
- `xlog_format_start()` and `xlog_format_commit()` are declared here and implemented in `xfs_log_cil.c`; together they reserve and finalize one formatted log-vector region.
- `xlog_format_copy()` wraps start/copy/commit for callers that already have a contiguous structure to copy into a formatted log vector.

These helpers hide the opheader and alignment details from individual log item formatters.

## LSN Comparison

`_lsn_cmp()` compares two `xfs_lsn_t` values by cycle first and block second. The `XFS_LSN_CMP(x, y)` macro maps to this helper. Return values are negative, positive, or zero, but use sentinel magnitudes `-999` and `999` rather than strict `-1`/`1`; callers use sign semantics.

The function avoids treating the LSN as a single host-endian 64-bit integer, which matters because LSN components are encoded as cycle and block fields.

## Public API Declarations

Lifecycle and recovery-facing declarations:

- `xfs_log_mount()`
- `xfs_log_mount_finish()`
- `xfs_log_mount_cancel()`
- `xfs_log_unmount()`
- `xfs_log_quiesce()`
- `xfs_log_clean()`
- `xfs_log_work_queue()`

Reservation and ticket declarations:

- `xfs_log_reserve()`
- `xfs_log_regrant()`
- `xfs_log_ticket_get()`
- `xfs_log_ticket_put()`

Force, tail, and validation declarations:

- `xfs_log_force()`
- `xfs_log_force_seq()`
- `xlog_assign_tail_lsn()`
- `xlog_assign_tail_lsn_locked()`
- `xfs_log_space_wake()`
- `xfs_log_check_lsn()`
- `xfs_log_writable()`

CIL/shutdown related declarations:

- `xlog_cil_process_committed()`
- `xfs_log_item_in_current_chkpt()`
- `xlog_force_shutdown()`

## Constants

`XFS_LOG_SYNC` is the single public force flag and requests synchronous forcing of in-core log state to disk. Calls without this flag may initiate writeout without waiting for stable completion.

## Research Notes

This header deliberately keeps only the stable cross-module surface. Most log internals, including iclog states, CIL structures, tickets, grant heads, and helper implementations, live in `xfs_log_priv.h` and the C files. The region type list is a useful map of every logical payload family the XFS journal can carry.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_log.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_log_cil.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_log_cil.c

## Purpose

`xfs_log_cil.c` implements the XFS Committed Item List (CIL), the delayed logging subsystem that aggregates committed transaction items into checkpoint contexts before writing them to the physical log. It handles per-transaction log item formatting, shadow log vector buffering, per-CPU accumulation, checkpoint context switching, background and forced pushes, strict checkpoint write ordering, commit-record stable-storage semantics, post-commit AIL insertion, busy extent cleanup, and CIL initialization/destruction.

## Major Responsibilities

- Allocate checkpoint tickets that steal reservation space from committing transactions instead of independently reserving log space.
- Track whether log items are already in the current checkpoint sequence.
- Allocate and maintain shadow log-vector buffers to avoid memory allocation while the CIL context lock is held.
- Format dirty transaction items into flat log vectors with aligned opheader-prefixed regions.
- Insert items into the active CIL context, pinning newly added items and accounting only the delta when relogging existing items.
- Aggregate per-CPU CIL space, busy extents, and item lists into the checkpoint context during a push.
- Switch from the current active context to a new empty context while the old one is written out.
- Build checkpoint transaction headers, write checkpoint data, then write ordered commit records.
- Attach checkpoint callbacks to commit iclogs so completion processing can move items into the AIL and unpin them.
- Force CIL sequences for `fsync`/log-force callers and return the commit LSN that the log manager must force.
- Process intent/done pairs within the same checkpoint by whiteing out redundant intent logging.

## CIL Context Lifecycle

1. `xlog_cil_init()` allocates `struct xfs_cil`, a bounded push workqueue, per-CPU tracking areas, locks/wait queues, and the first context.
2. `xlog_cil_init_post_recovery()` allocates the initial checkpoint ticket after recovery establishes log head/tail state.
3. Transaction commits call `xlog_cil_commit()` under a read lock on `xc_ctx_lock`.
4. Items are formatted, inserted into the active context, and the transaction ticket donates reservation space to the checkpoint ticket.
5. `xlog_cil_push_background()` queues push work when soft/hard CIL space limits are reached.
6. `xlog_cil_push_work()` takes the write lock, aggregates per-CPU state, links the old context on `xc_committing`, switches to a new context, and writes the old context to the log.
7. The commit iclog callback eventually calls `xlog_cil_process_committed()`, which invokes `xlog_cil_committed()` and frees the old context after AIL/busy-extent cleanup.
8. `xlog_cil_destroy()` frees the active empty context, per-CPU storage, workqueue, and CIL structure.

## Log Vector Formatting

- `xlog_cil_alloc_shadow_bufs()` runs before taking the CIL context lock. It asks each dirty item for `iop_size()`, allocates or reuses `li_lv_shadow`, accounts alignment, and handles ordered items by setting `lv_buf_used` to `XFS_LOG_VEC_ORDERED`.
- `xlog_format_start()` initializes a region iovec and embedded `xlog_op_header`, aligning payload start to 8 bytes.
- `xlog_format_commit()` rounds payload length, zeroes padding, records opheader length, advances `lv_buf_used`, increments `lv_bytes`, and advances the formatter index.
- `xlog_cil_insert_format_items()` either reuses the existing log vector when the shadow fits, swaps to the shadow buffer, or handles ordered items without data regions. It then calls each item’s `iop_format()`.
- `xfs_cil_prepare_item()` accounts new vs. replaced log-vector bytes, pins first-time CIL items, swaps old vectors into `li_lv_shadow`, attaches the new vector to the item, and records the first checkpoint sequence in `li_seq`.

## Space Accounting and Limits

The CIL uses dynamic reservation stealing. `xlog_cil_insert_items()` subtracts consumed item bytes and checkpoint overhead from the committing transaction ticket and adds reserved space to the checkpoint context ticket through per-CPU accounting.

Important mechanisms:

- `XLOG_CIL_SPACE_LIMIT(log)` is the smaller of one-eighth of log space and 16 times the iclog window, limiting memory pinned by delayed logging while preserving relogging efficiency.
- `XLOG_CIL_BLOCKING_SPACE_LIMIT(log)` is twice the background limit and triggers commit throttling.
- `XLOG_CIL_PCP_SPACE` enables low-contention per-CPU space accounting below the soft limit; once the soft limit is crossed, `xlog_cil_insert_pcp_aggregate()` folds per-CPU counts into the atomic global counter.
- `xc_iclog_hdrs` tracks remaining expected iclog header reservations; commits steal more header/split reservation space when needed or when over the hard limit.
- `xlog_cil_over_hard_limit()` also treats active push waiters as a hard-limit condition, so once throttling begins it remains enforced until the context switch wakes waiters.

## Checkpoint Push Flow

`xlog_cil_push_work()` is the main push worker:

- Runs under `memalloc_nofs_save()` to avoid filesystem reclaim recursion.
- Allocates a new context and ticket before taking `xc_ctx_lock` exclusively.
- Aggregates per-CPU state into the old context with `xlog_cil_push_pcp_aggregate()`.
- Skips if the CIL is empty or the requested sequence was already pushed.
- Adds the old context to `xc_committing` before emptying/switching it so waiters can distinguish "push in progress" from "nothing to do".
- Builds the log-vector chain from CIL items via `xlog_cil_build_lv_chain()`, moving whiteout items aside.
- Switches to the new active context with `xlog_cil_ctx_switch()`.
- Sorts log vectors by transaction order id using `xlog_cil_order_cmp()`.
- Builds and prepends a checkpoint transaction header via `xlog_cil_build_trans_hdr()`.
- Writes checkpoint data through `xlog_cil_write_chain()`, then writes the commit record through `xlog_cil_write_commit_record()`.
- Waits for prior iclogs if the checkpoint spans multiple iclogs, sets preflush/FUA as needed, releases the commit iclog, cleans whiteouts, and ungrants the checkpoint ticket.

## Ordering Rules

The file enforces ordering at several layers:

- Start records and commit records are strictly ordered by checkpoint sequence using `xlog_cil_order_write()`, `xc_start_wait`, and `xc_commit_wait`.
- `xlog_cil_set_ctx_write_state()` records the start LSN on the first write and the commit LSN on the commit-record write. It attaches the checkpoint callback to the commit iclog before publishing `commit_lsn`.
- Checkpoint callbacks are attached to iclogs in commit-record order so completion processing sees checkpoints in correct order.
- If a checkpoint spans multiple iclogs, push work waits on the previous iclog and marks the commit iclog with `NEED_FLUSH` so stable-storage ordering is preserved.
- Commit iclogs always get `NEED_FUA`; asynchronous flush requests can force the active commit iclog to `WANT_SYNC` so the commit record reaches stable storage without a later force.

## AIL and Completion Processing

`xlog_cil_process_committed()` drains a list of completed CIL contexts from iclog callbacks. `xlog_cil_committed()` then:

- Detects abort state from log shutdown and wakes push waiters early.
- Calls `xlog_cil_ail_insert()` to run item committed callbacks and insert items into the AIL in batches.
- Sorts and clears busy extents, optionally issuing discard if enabled and not aborting.
- Removes the context from `xc_committing`.
- Frees log vectors.
- Either schedules discard ownership by keeping the context alive or frees the context immediately.

`xlog_cil_ail_insert()` updates the AIL head LSN to the checkpoint commit LSN before returning grant space. It uses a write memory barrier paired with grant-space reads to avoid transiently overestimating available log space. Items with `XFS_ITEM_RELEASE_WHEN_COMMITTED` are released immediately; unusual item LSNs bypass bulk insertion; abort paths set `XFS_LI_ABORTED` and unpin without AIL insertion.

## Intent Whiteouts

`xlog_cil_process_intents()` optimizes transactions that contain intent-done items whose related intent was first committed in the current checkpoint. In that case both records are unnecessary for recovery because the operation is atomic within the checkpoint:

- The related intent item is marked `XFS_LI_WHITEOUT`.
- Its log vector bytes are counted as released space.
- The intent-done item is removed from the transaction and released.
- `xlog_cil_build_lv_chain()` later skips whiteout items, and `xlog_cil_cleanup_whiteouts()` unpins them as aborted/skipped work.

## Force APIs

- `xlog_cil_flush()` triggers an asynchronous push of the current sequence with stable-commit semantics and forces the log if the CIL is already empty but a previous checkpoint might still sit in an active iclog.
- `xlog_cil_force_seq()` queues a push for the requested sequence, waits for prior or matching committing contexts to publish a commit LSN, retries races where the current context has not started pushing yet, and returns the commit LSN for the log-force layer. During shutdown it returns zero rather than `NULLCOMMITLSN` so the caller still exercises iclog error handling.
- `xlog_cil_push_now()` coordinates push sequence state and optionally flushes the push workqueue for synchronous callers to reduce later wait time.

## Concurrency and Locking

- `xc_ctx_lock` protects active context mutation vs. context switching. Transaction commits hold it read-locked; push work holds it write-locked.
- `xc_push_lock` protects `xc_push_seq`, `xc_push_commit_stable`, `xc_committing`, and push/commit/start wait queues.
- Per-CPU `xlog_cil_pcp` storage reduces contention for space counts, busy extents, and log item lists until push aggregation.
- CPU preemption is disabled around per-CPU insertion accounting with `get_cpu()` / `put_cpu()`.
- Lockless `waitqueue_active()` checks are only used when serialized by `xc_push_lock` or `xc_ctx_lock`, as documented in comments.

## Error Handling

- Ticket allocation for CIL checkpoints is no-fail because failing during checkpointing would make recovery difficult.
- Reservation overrun in `xlog_cil_insert_items()` dumps transaction details and forces log shutdown.
- Errors writing the checkpoint chain or commit record lead to shutdown/abort paths. If the commit iclog was not attached yet, the context is manually committed in abort mode so items are unpinned.
- CIL destroy asserts the active context is empty.

## Research Notes

The CIL is the performance and batching layer of XFS logging. Its design avoids reserving a separate checkpoint transaction up front; instead it safely transfers unused reservation from ordinary transactions into the checkpoint ticket. The implementation is heavily optimized for high-concurrency metadata workloads: per-CPU insertion, shadow buffers, bulk AIL insertion, sequence-ordered checkpoint pipelines, and bounded push workqueue concurrency all reduce contention while preserving recovery ordering.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_log_cil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_log_priv.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_log_priv.h

## Purpose

`xfs_log_priv.h` defines the private data structures, state constants, helper functions, and internal prototypes shared by XFS log manager, CIL, and recovery code. It is the structural contract for in-core log buffers, checkpoint contexts, CIL state, grant heads, log geometry/state, ticket accounting, LSN helpers, allocation helpers, and log item space calculations.

## Core Structures

### `struct xfs_log_iovec`

Represents one formatted log region with an address, byte length, and region type. Region type values come from `xfs_log.h`.

### `struct xfs_log_vec`

Represents the formatted log-vector state for one log item:

- list linkage for CIL chains
- ordering id
- iovec count and iovec array
- owning log item
- formatted buffer pointer
- accounted bytes, used bytes, and allocation size

The CIL swaps these between active item state and shadow buffers during relogging.

### `struct xlog_ticket`

Tracks reservation ownership:

- grant wait queue node and owning task
- transaction id
- reference count
- current and unit reservations
- original/current reservation counts
- permanent-reservation flag
- number of iclog headers included in the reservation

Tickets are used both by ordinary transactions and by CIL checkpoint contexts.

### `struct xlog_in_core`

Represents one in-core log buffer in the iclog ring:

- force/write wait queues
- ring links
- owning log pointer
- usable size, offset, state, flags, data pointer
- callback list for completed CIL contexts
- cacheline-separated reference count
- log record header pointer
- debug CRC failure bit
- semaphore used to serialize IO completion against teardown
- end-IO work item
- embedded bio and flexible bio_vec array

The comments emphasize cacheline separation for fields contended by independent CPUs.

### `struct xfs_cil_ctx`

Tracks one checkpoint context:

- owning CIL and sequence
- start and commit LSNs
- commit iclog reference
- checkpoint ticket
- aggregate space count
- busy extents
- log items and log-vector chain
- iclog callback entry
- committing-list linkage
- push work
- item ordering counter
- CPU mask identifying per-CPU CIL data touched by this context

### `struct xlog_cil_pcp`

Per-CPU CIL staging area containing space-used/reserved counters plus busy extent and log item lists.

### `struct xfs_cil`

Global CIL state for one log:

- owning log
- flags and iclog-header counter
- push workqueue
- context rwsem and active context
- push lock, push sequence, stable-commit request flag
- committing context list and wait queues
- current sequence and push-throttle wait queue
- per-CPU state pointer

The structure is cacheline aligned because it sits in hot transaction commit paths.

### `struct xlog_grant_head`

Represents either the reservation or write grant head with its own cacheline-aligned lock, waiter list, and atomic grant-space counter.

### `struct xlog`

Main in-core log object containing:

- mount, AIL, CIL, buftarg, and IO completion workqueue pointers
- background work, opstate bits, quotaoff flags, recovery cancel table, recovered deferred ops
- iclog geometry and physical log geometry
- iclog ring state protected by `l_icloglock`
- current/previous log cycle and block
- atomic tail LSN on a separate cacheline
- reservation and write grant heads
- tail-space accounting
- sysfs kobject
- recovery LSN tracking
- iclog roundoff

## State and Flag Definitions

Iclog states:

- `XLOG_STATE_ACTIVE`
- `XLOG_STATE_WANT_SYNC`
- `XLOG_STATE_SYNCING`
- `XLOG_STATE_DONE_SYNC`
- `XLOG_STATE_CALLBACK`
- `XLOG_STATE_DIRTY`

Iclog flags:

- `XLOG_ICL_NEED_FLUSH`
- `XLOG_ICL_NEED_FUA`

Ticket flags:

- `XLOG_TIC_PERM_RESERV`

Cover states:

- `XLOG_STATE_COVER_IDLE`
- `XLOG_STATE_COVER_NEED`
- `XLOG_STATE_COVER_DONE`
- `XLOG_STATE_COVER_NEED2`
- `XLOG_STATE_COVER_DONE2`

Log opstate bits:

- `XLOG_ACTIVE_RECOVERY`
- `XLOG_RECOVERY_NEEDED`
- `XLOG_IO_ERROR`
- `XLOG_TAIL_WARN`
- `XLOG_SHUTDOWN_STARTED`

CIL flags:

- `XLOG_CIL_EMPTY`
- `XLOG_CIL_PCP_SPACE`

## CIL Limit Macros

`XLOG_CIL_SPACE_LIMIT(log)` chooses the smaller of one-eighth of the log and 16 times the total iclog record window. `XLOG_CIL_BLOCKING_SPACE_LIMIT(log)` doubles that value. The long comment explains the tradeoff: keep checkpoints below recovery/log-reservation size constraints while bounding pinned metadata memory and retaining relogging efficiency.

## Internal API Declarations

Recovery:

- `xlog_recover()`
- `xlog_recover_finish()`
- `xlog_recover_cancel()`

Log writing and ticket internals:

- `xlog_cksum()`
- `xlog_ticket_alloc()`
- `xlog_print_tic_res()`
- `xlog_print_trans()`
- `xlog_write()`
- `xlog_write_one_vec()`
- `xfs_log_ticket_ungrant()`
- `xfs_log_ticket_regrant()`
- `xlog_state_switch_iclogs()`
- `xlog_state_release_iclog()`

CIL:

- `xlog_cil_init()`
- `xlog_cil_init_post_recovery()`
- `xlog_cil_destroy()`
- `xlog_cil_empty()`
- `xlog_cil_commit()`
- `xlog_cil_set_ctx_write_state()`
- `xlog_cil_flush()`
- `xlog_cil_force_seq()`
- inline `xlog_cil_force()`

Wait and iclog force support:

- inline `xlog_wait()`
- `xlog_wait_on_iclog()`

Grant/tail support:

- `xlog_lsn_sub()`
- `xlog_grant_return_space()`

## Inline Helpers

- `xlog_get_client_id()` extracts the client id from a packed big-endian opheader word; the comment notes historic endian awkwardness in packed log recovery handling.
- `xlog_recovery_needed()`, `xlog_in_recovery()`, and `xlog_is_shutdown()` test log opstate bits.
- `xlog_shutdown_wait()` waits until shutdown state is visible.
- `xlog_crack_atomic_lsn()` samples an atomic LSN once and splits it into cycle/block.
- `xlog_assign_atomic_lsn()` stores an LSN constructed from cycle/block.
- `xlog_wait()` implements the log code’s spinlock-serialized exclusive wait pattern.
- `xlog_lsn_sub()` computes byte distance between two LSNs, handling single-cycle wrap and allowing shutdown exceptions.
- `xlog_valid_lsn()` performs mostly lockless validation that a metadata LSN is not ahead of the current log head, with a locked recheck for wrap races.
- `xlog_kvmalloc()` open-codes kmalloc-with-vmalloc-fallback using no-direct-reclaim flags, relying on caller NOFS context.
- `xlog_item_space()` computes log space for item payload bytes plus per-iovec opheader/alignment overhead.
- `xlog_cycle_data()` returns the cycle-data slot for a 512-byte block, including v2 extended headers after the original header’s array is exhausted.

## Important Design Notes Captured in Comments

- Log covering requires two dummy transactions to ensure recovery starts beyond the last potentially replayable allocation transaction.
- CIL reservation strategy avoids static checkpoint reservations because regranting during push can deadlock. Instead, transaction commits transfer unused reservation into the checkpoint context.
- CIL size limits balance log-space safety, latency, and pinned-memory footprint.
- `l_tail_lsn`, grant heads, and some iclog fields are cacheline-separated because they are hot under concurrent transaction workloads.
- `xlog_valid_lsn()` depends on write/read memory ordering between current block and current cycle updates during log wrap.
- `xlog_kvmalloc()` avoids expensive direct reclaim in log-vector allocation paths.

## Research Notes

This private header is the best compact map of XFS logging internals. It shows that the implementation is organized around three shared objects: `xlog` for physical log/iclog state, `xfs_cil` for delayed checkpoint aggregation, and `xlog_ticket` for reservation accounting. It also documents many of the hidden constraints that drive the C files: recovery ordering, log cover semantics, checkpoint size thresholds, cacheline contention, and lockless LSN validation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_log_priv.h -->