# subset-b-005798 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_log.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_log.c

## Purpose
`xfs_log.c` is the core XFS journal manager. It owns log allocation at mount, log recovery handoff, ticket reservation and grant accounting, in-core log buffer (`iclog`) state transitions, physical log writes, log force and force-by-checkpoint operations, log covering/clean unmount records, shutdown wakeups, and debug validation of log head/tail consistency.

## Important APIs, Types, and Functions
Public entry points include `xfs_log_mount()`, `xfs_log_mount_finish()`, `xfs_log_mount_cancel()`, `xfs_log_reserve()`, `xfs_log_regrant()`, `xfs_log_force()`, `xfs_log_force_seq()`, `xfs_log_quiesce()`, `xfs_log_clean()`, `xfs_log_unmount()`, `xfs_log_writable()`, `xfs_log_space_wake()`, `xfs_log_item_init()`, `xfs_log_ticket_get()`, `xfs_log_ticket_put()`, `xfs_log_check_lsn()`, and `xlog_force_shutdown()`. Key internal types are `struct xlog`, `struct xlog_in_core`, `struct xlog_ticket`, `struct xlog_grant_head`, and the local `struct xlog_write_data`.

Grant accounting is handled by `xlog_grant_head_check()`, `xlog_grant_head_wait()`, `xlog_grant_head_wake()`, `xlog_grant_return_space()`, `xfs_log_ticket_regrant()`, and `xfs_log_ticket_ungrant()`. Iclog write mechanics run through `xlog_state_get_iclog_space()`, `xlog_write()`, `xlog_write_full()`, `xlog_write_partial()`, `xlog_state_switch_iclogs()`, `xlog_state_release_iclog()`, `xlog_sync()`, `xlog_write_iclog()`, `xlog_state_done_syncing()`, and `xlog_state_do_callback()`. Mount/unmount and background paths use `xlog_alloc_log()`, `xlog_dealloc_log()`, `xfs_log_worker()`, `xfs_log_cover()`, `xlog_unmount_write()`, and `xfs_log_unmount_write()`.

## Control Flow
Mount starts in `xfs_log_mount()`: allocate the `xlog`, validate log size, create the AIL, run recovery unless `norecovery` is set, publish the sysfs log object, clear active recovery, and initialize the post-recovery CIL ticket. `xfs_log_mount_finish()` completes phase-two recovery after root/RT inodes are available, forces recovered work to disk, drains buffers, and clears `XLOG_RECOVERY_NEEDED`.

Transaction reservation begins with `xfs_log_reserve()`, which allocates a ticket and advances both reserve and write grant heads. Rolling transactions use `xfs_log_regrant()`, and commit cleanup returns unused space through ticket regrant/ungrant helpers. If reservation space is unavailable, tickets are queued on grant-head wait lists, the AIL is pushed, and waiters sleep until tail movement or shutdown wakes them.

Writing starts when CIL code or direct log records call `xlog_write()`/`xlog_write_one_vec()`. `xlog_state_get_iclog_space()` selects the active iclog, stamps its LSN on first use, accounts the iclog header to the ticket, and either reserves space or switches to the next iclog. `xlog_write_full()` copies whole regions; `xlog_write_partial()` splits large regions across iclogs with `XLOG_CONTINUE_TRANS`, `XLOG_WAS_CONT_TRANS`, and `XLOG_END_TRANS` operation headers. Once copying is done, `xlog_state_release_iclog()` flushes the iclog if the last reference has moved it to `WANT_SYNC`.

Forces first push the CIL, then operate on the iclog containing the requested commit LSN. `xfs_log_force()` flushes all current log data, while `xfs_log_force_seq()` asks the CIL for the commit LSN of a checkpoint sequence and then calls `xlog_force_lsn()`. Synchronous force waits on `ic_force_wait`, which is awakened only after ordered iclog completion callbacks have run.

Unmount/freeze first quiesces the log, cancels background covering work, forces the CIL/iclogs, pushes the AIL, drains metadata I/O, performs log covering, and optionally writes an unmount record. `xlog_force_shutdown()` serializes shutdown, optionally forces non-error pending log data before marking `XLOG_IO_ERROR`, marks the mount shut down, wakes grant waiters, CIL waiters, iclog waiters, and callback paths.

## State and Persistence
Persistent journal state is the circular on-disk log of record headers, operation headers, transaction regions, checkpoint commit records, and unmount records. The in-memory log tracks current cycle/block, previous cycle/block, tail LSN, AIL head, grant heads, CIL pointer, iclog ring state, covering state, and shutdown/recovery flags. Iclog writes stamp cycle values into each 512-byte sector, store overwritten sector words in the record header cycle arrays, calculate CRCs, and split bios when a log record wraps the physical end of the log.

Stable-storage ordering is explicit. `XLOG_ICL_NEED_FLUSH` adds `REQ_PREFLUSH`; `XLOG_ICL_NEED_FUA` adds `REQ_FUA`. For external logs, `xlog_write_iclog()` flushes the data device before writing a flushed log record so metadata writeback covered by the tail LSN is stable before the journal record is considered stable. `xlog_state_release_iclog()` captures the current tail LSN into an iclog the first time it needs FUA or sync so later tail movement cannot invalidate recovery ordering for the commit record in that iclog.

Log covering is a small persistence protocol that writes up to two dummy superblock transactions when the filesystem becomes idle. The `XLOG_STATE_COVER_*` states ensure the on-disk tail advances beyond the last real allocation transaction, reducing unnecessary recovery work and avoiding replay of stale allocation side effects after long idle periods.

## Dependencies and Integration Points
This file depends on CIL routines in `xfs_log_cil.c`, AIL manipulation from transaction code, recovery in `xlog_recover*()`, superblock sync and health state, block-layer bio/flush/FUA APIs, sysfs registration, XFS stats and tracepoints, error injection tags, zone wakeups for zoned realtime devices, and mount feature helpers. It is the shared persistence substrate for all XFS transaction item types.

## Risks and Test Signals
High-risk areas are grant-head arithmetic around tail movement, ticket reservation sizing, split-region continuation headers, LSN wrap ordering, iclog state races, callback ordering after concurrent CIL checkpoints, external-log flush ordering, shutdown paths that run while unmount tears down iclog buffers, and log covering transitions. Useful tests include fsstress with small logs, forced rolling transactions, concurrent log forces, power-fail recovery with split records and wraparound, external log device cache flush failures, bad CRC injection, summary-counter sickness suppressing unmount records, read-only/norecovery mounts, and metadata verifier checks that call `xfs_log_check_lsn()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_log.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_log.h

## Purpose
`xfs_log.h` is the public XFS log interface used by transaction, recovery, mount, and log item code. It defines on-log region type identifiers, small formatting helpers for delayed-logging iovecs, LSN comparison semantics, log force flags, and prototypes for reservation, force, mount, unmount, CIL, shutdown, and validity-check operations.

## Important APIs, Types, and Functions
The region type constants `XLOG_REG_TYPE_*` classify each logged iovec, including buffers, inodes, dquots, quotaoff records, start/commit/transaction headers, intent/done item formats, attribute name/value regions, and unmount records. `XLOG_REG_TYPE_MAX` currently tracks the highest known type, and `XFS_LOG_VEC_ORDERED` marks ordered log vectors that pin and order an item without writing data.

Formatting helpers are `xlog_calc_iovec_len()`, `xlog_format_start()`, `xlog_format_commit()`, and `xlog_format_copy()`. LSN comparison is exposed as `XFS_LSN_CMP()` over `_lsn_cmp()`, comparing cycle and block components instead of relying on raw 64-bit ordering. The main exported functions are `xfs_log_force()`, `xfs_log_force_seq()`, `xfs_log_mount()`, `xfs_log_mount_finish()`, `xfs_log_mount_cancel()`, `xfs_log_reserve()`, `xfs_log_regrant()`, `xfs_log_unmount()`, `xfs_log_writable()`, `xfs_log_quiesce()`, `xfs_log_clean()`, `xfs_log_space_wake()`, `xfs_log_check_lsn()`, `xlog_assign_tail_lsn()`, `xlog_assign_tail_lsn_locked()`, `xlog_cil_process_committed()`, `xfs_log_item_in_current_chkpt()`, and `xlog_force_shutdown()`.

## Control Flow
This header does not implement the log state machine, but it describes the call surface. Mount code allocates and finishes the log with `xfs_log_mount*()`. Transaction code reserves or regrants space with `xfs_log_reserve()`/`xfs_log_regrant()`, formats log item regions through the `xlog_format_*()` helpers, commits through the CIL, and later forces durability through `xfs_log_force()` or `xfs_log_force_seq()`. Unmount and freeze paths call `xfs_log_quiesce()`, `xfs_log_clean()`, and `xfs_log_unmount()`. Shutdown and verifier paths use `xlog_force_shutdown()` and `xfs_log_check_lsn()`.

## State and Persistence
The constants in this header are part of the persistent log format because recovery decodes operation regions by `i_type`. The LSN helper encodes the journal's persistent ordering model: an LSN is a cycle plus block pair, and wraparound must be compared component-wise. `XFS_LOG_SYNC` controls whether a force only starts writeout or also waits until the relevant iclog and its ordered callbacks complete.

## Dependencies and Integration Points
The header forward-declares `struct xfs_mount`, `struct xfs_buftarg`, `struct xlog_ticket`, `struct xfs_log_item`, `struct xfs_trans`, `struct xfs_cil_ctx`, and `struct xlog`. It is included by transaction commit code, log item implementations, recovery, mount/unmount code, and CIL internals. The region type list must stay synchronized with all log item `iop_format()` implementations and log recovery item decoders.

## Risks and Test Signals
The main risk is persistent-format drift: adding or reusing a region type incorrectly can make old or new kernels misinterpret recovery data. Incorrect iovec length alignment or LSN comparison can cause reservation underestimation, recovery ordering bugs, or false metadata corruption reports. Test signals include compile coverage for all log item formatters, xfs_logprint/recovery decoding of every region type, rolling log wraparound tests, and verifier tests for LSN comparison near cycle transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_log_cil.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_log_cil.c

## Purpose
`xfs_log_cil.c` implements the XFS Committed Item List. The CIL aggregates committed transaction items in memory, relogs frequently modified metadata, converts the current aggregate into ordered checkpoint transactions, writes checkpoint start/data/commit records into iclogs, manages checkpoint completion callbacks, transfers items to the AIL, and implements force-by-checkpoint-sequence behavior.

## Important APIs, Types, and Functions
Public entry points are `xlog_cil_init()`, `xlog_cil_init_post_recovery()`, `xlog_cil_destroy()`, `xlog_cil_commit()`, `xlog_cil_flush()`, `xlog_cil_force_seq()`, `xlog_cil_empty()`, `xlog_cil_process_committed()`, `xlog_cil_set_ctx_write_state()`, `xlog_format_start()`, `xlog_format_commit()`, and `xfs_log_item_in_current_chkpt()`.

Core private helpers include `xlog_cil_ticket_alloc()`, `xlog_cil_alloc_shadow_bufs()`, `xfs_cil_prepare_item()`, `xlog_cil_insert_format_items()`, `xlog_cil_insert_items()`, `xlog_cil_process_intents()`, `xlog_cil_push_background()`, `xlog_cil_push_now()`, `xlog_cil_push_work()`, `xlog_cil_build_lv_chain()`, `xlog_cil_build_trans_hdr()`, `xlog_cil_write_chain()`, `xlog_cil_write_commit_record()`, `xlog_cil_order_write()`, `xlog_cil_ail_insert()`, and `xlog_cil_committed()`. Important local structures are `struct xlog_format_buf` and `struct xlog_cil_trans_hdr`; durable and runtime CIL state is defined in `xfs_log_priv.h`.

## Control Flow
Commit flow starts in `xlog_cil_commit()`. It allocates or resizes per-item shadow log vectors outside the CIL context lock to avoid reclaim deadlocks. Under the read side of `xc_ctx_lock`, it optionally cancels same-checkpoint intent/done pairs with whiteouts, formats dirty items into flat log-vector buffers, pins newly inserted items, records first checkpoint sequence numbers, steals unused transaction reservation into the checkpoint ticket, moves busy extents and log items into per-CPU CIL staging lists, regrants or ungrants the transaction ticket, calls item `iop_committing()`, returns the checkpoint sequence, and then lets `xlog_cil_push_background()` decide whether to queue a push.

Background push flow runs in `xlog_cil_push_work()` under NOFS allocation context. It allocates the next CIL context and ticket, exclusively locks `xc_ctx_lock`, aggregates per-CPU CIL state, skips empty or already-pushed sequences, links the old context onto `xc_committing`, builds the checkpoint log-vector chain, switches `xc_ctx` to the new empty context, sorts vectors by transaction order id, prepends a checkpoint transaction header, writes the start/data chain, writes the commit record, marks the commit iclog for flush/FUA, releases it for I/O, cleans up whiteouts, and ungrants the checkpoint ticket.

Completion flow is callback-driven from iclog completion. `xlog_cil_set_ctx_write_state()` records the start LSN on the first write and attaches the context callback to the commit iclog before publishing the commit LSN. `xlog_cil_process_committed()` runs callbacks in iclog order. `xlog_cil_committed()` inserts items into the AIL, unpins them, clears busy extents and optionally discards them, removes the context from `xc_committing`, frees log vectors, and frees the context after asynchronous discard completion is no longer needed.

Force flow uses sequence numbers. `xlog_cil_force_seq()` queues a push for the requested sequence, waits until all earlier relevant checkpoints have commit LSNs, restarts if the current CIL has not yet moved to the committing list, and returns the commit LSN that `xfs_log_force_seq()` must flush. `xlog_cil_flush()` is an async stable-storage request: it sets push state so the commit record is forced out even if the caller does not wait.

## State and Persistence
The CIL keeps a current context (`xc_ctx`) with a sequence, checkpoint ticket, aggregate space used, busy extents, dirty item list, log-vector chain, order counter, per-CPU participation mask, and later start/commit LSNs. The `xfs_cil` wrapper holds the current sequence, push sequence, committing list, push/start/commit wait queues, flags for empty state and per-CPU accounting mode, and per-CPU lists/counters.

Persistent output is a checkpoint transaction in the on-disk log: start operation header, transaction header of type `XFS_TRANS_CHECKPOINT`, formatted item regions, and an ordered commit operation header. The CIL intentionally tracks items by the checkpoint start LSN in the AIL, not the commit LSN, because multiple checkpoints can pipeline and the log tail must not move beyond the start record required to replay the next checkpoint. Commit iclogs receive FUA, and multi-iclog checkpoints add preflush ordering so all data portions are stable before the commit record becomes stable.

Intent whiteouts are a persistence optimization: if an intent and its done item both occur in the same checkpoint, neither needs to be written to the journal because the checkpoint commits atomically. The intent is marked `XFS_LI_WHITEOUT`, its log vector space is released, and the done item is removed from the committing transaction.

## Dependencies and Integration Points
This file depends on log writing primitives in `xfs_log.c`, log item operations (`iop_size`, `iop_format`, `iop_pin`, `iop_unpin`, `iop_committing`, `iop_committed`, `iop_intent`, `iop_release`), AIL bulk insertion, transaction item lists, busy extent sorting/clearing/discard, CIL thresholds from `xfs_log_priv.h`, workqueues, per-CPU state, wait queues, tracepoints, and mount discard feature checks. Transaction commit code enters here after items have been joined and dirtied; log force, unmount, and fsync paths consume the sequence/LSN force API.

## Risks and Test Signals
High-risk areas are CIL context switching races, per-CPU space aggregation, checkpoint ticket reservation stealing, hard-limit throttling, ordered write sequencing across concurrent checkpoints, publishing commit LSNs only after callbacks are attached, whiteout handling for intent/done pairs, preserving same-transaction log item order, and abort handling after log I/O failure. Tests should stress concurrent fsync/log forces, small-log CIL hard-limit throttling, reflink intent ordering, repeated relogging of the same inode/buffer, memory pressure during CIL push, discard busy-extents completion, injected log I/O errors before and after commit iclog assignment, and recovery of pipelined checkpoints with overlapping start/commit records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_log_cil.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_log_priv.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_log_priv.h

## Purpose
`xfs_log_priv.h` defines the private data structures, state flags, helper routines, and internal interfaces shared by the XFS log manager, CIL, and recovery code. It captures the in-memory representation of log vectors, tickets, iclogs, CIL contexts, grant heads, and the global `xlog`.

## Important APIs, Types, and Functions
Important structures are `struct xfs_log_iovec`, `struct xfs_log_vec`, `struct xlog_ticket`, `struct xlog_in_core`, `struct xfs_cil_ctx`, `struct xlog_cil_pcp`, `struct xfs_cil`, `struct xlog_grant_head`, and `struct xlog`. The header defines `enum xlog_iclog_state`, iclog flags `XLOG_ICL_NEED_FLUSH` and `XLOG_ICL_NEED_FUA`, ticket flag `XLOG_TIC_PERM_RESERV`, CIL flags `XLOG_CIL_EMPTY` and `XLOG_CIL_PCP_SPACE`, log covering states `XLOG_STATE_COVER_*`, and operational state bits `XLOG_ACTIVE_RECOVERY`, `XLOG_RECOVERY_NEEDED`, `XLOG_IO_ERROR`, `XLOG_TAIL_WARN`, and `XLOG_SHUTDOWN_STARTED`.

Internal prototypes include recovery (`xlog_recover()`, `xlog_recover_finish()`, `xlog_recover_cancel()`), checksum (`xlog_cksum()`), ticket allocation and debug printing, `xlog_write()`, `xlog_write_one_vec()`, ticket grant/ungrant helpers, iclog switching/release helpers, CIL lifecycle/commit/force helpers, `xlog_wait_on_iclog()`, and `xlog_grant_return_space()`. Inline helpers include `xlog_recovery_needed()`, `xlog_in_recovery()`, `xlog_is_shutdown()`, `xlog_shutdown_wait()`, `xlog_crack_atomic_lsn()`, `xlog_assign_atomic_lsn()`, `xlog_wait()`, `xlog_lsn_sub()`, `xlog_valid_lsn()`, `xlog_kvmalloc()`, `xlog_item_space()`, and `xlog_cycle_data()`.

## Control Flow
The header does not execute top-level behavior, but it wires together the major control planes. Log writers format `xfs_log_vec` chains and call `xlog_write()`, which fills `xlog_in_core` buffers. CIL commits populate `xfs_cil_ctx` and per-CPU `xlog_cil_pcp` state until push work switches contexts and writes a checkpoint. Grant paths use `xlog_grant_head` counters and wait lists to reserve circular log space. Recovery and mount code query or set `xlog` operational bits before normal transactions begin.

Wait and validation helpers encode locking expectations. `xlog_wait()` sleeps on a wait queue serialized by a spinlock and returns with the lock dropped. `xlog_valid_lsn()` samples current cycle/block with memory barriers and retries under `l_icloglock` on apparent future LSNs, matching the write-side ordering in `xlog_state_switch_iclogs()`.

## State and Persistence
`struct xlog` is the central in-memory state for persistent log geometry and progress: mount, AIL, CIL, target device, background work, log flags, sector size, iclog size/count, physical log start/length, current and previous cycle/block, tail LSN, grant heads, tail-space accounting, recovery LSN, and iclog rounding. `struct xlog_in_core` stores each ring buffer's record header, data pointer, offset, callbacks, state, flags, wait queues, reference count, semaphore, work item, and bio storage.

The structures directly support persistence but are not themselves on-disk formats. They track where on-disk log records will be written, what tail LSN will be stamped into record headers, how FUA/flush requirements are carried to the block layer, and which CIL checkpoint callbacks must run after commit records reach stable storage. `xlog_cycle_data()` accesses primary and extended cycle data arrays used to make torn-sector detection work for v1 and v2 log records.

## Dependencies and Integration Points
The header depends on XFS extent busy tracking, log format structures, transaction and log item declarations, Linux atomic/spinlock/rwsem/waitqueue/workqueue/bio primitives, per-CPU allocation, and cacheline layout annotations. It is included by `xfs_log.c`, `xfs_log_cil.c`, recovery code, and transaction internals that need private log state.

## Risks and Test Signals
Risks are mostly concurrency and accounting related: cacheline-separated fields must still be synchronized correctly, atomic LSN sampling must match update barriers, CIL space thresholds must stay below recovery/log reservation limits, `xlog_lsn_sub()` assumes at most one wrap except during shutdown, and `xlog_kvmalloc()` intentionally loops until memory is available under NOFS context. Test signals include lockdep on log wait queues and CIL context locks, KCSAN-style races around current LSN sampling, small-log reservation stress, memory-pressure CIL formatting, recovery of v2 log records using extended cycle data, and shutdown tests that wake `xlog_shutdown_wait()` consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_log_priv.h -->
