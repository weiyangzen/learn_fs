# Group Research: group_1116_linux_stable_sources_os_linux_linux_stable_fs_xfs_xfs_log_c_sources_19659a6af40c

Scope confirmed against `Docs/research_subset_a.md`: `sources/os/linux/linux-stable` is included in subset A. All four listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_log.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_log.c

## Purpose

`xfs_log.c` implements the core XFS journal/log manager. It handles log mount setup, recovery integration, log reservation and regrant accounting, in-core log buffer state transitions, physical log writes, log forcing, unmount records, idle log covering, ticket lifecycle, forced shutdown, and metadata LSN validation.

It is the main coordinator between transaction reservation accounting, the CIL layer, iclog buffers, the AIL, recovery, block I/O, and mount shutdown state.

## Main Responsibilities

- Allocate and initialize `struct xlog` and the circular ring of `struct xlog_in_core` buffers.
- Maintain reserve and write grant heads for transaction log-space accounting.
- Reserve, regrant, ungrant, and free log tickets.
- Serialize writers into active iclogs and flush iclogs to the on-disk log.
- Handle log record cycle stamping, v2 extended headers, checksums, split writes at log wrap, flush/FUA ordering, and I/O completion.
- Force all log data or a requested checkpoint sequence to stable storage.
- Write clean unmount records and cover idle logs with dummy/superblock transactions.
- Process iclog completion callbacks in LSN order.
- Shut down the log safely and wake all waiters.
- Validate metadata LSNs against the current log head.

## Important Control Flow

`xfs_log_mount` allocates the log, validates minimum log size, initializes the AIL, runs recovery unless mounted with norecovery, initializes sysfs state, clears active recovery, and initializes the post-recovery CIL ticket. `xfs_log_mount_finish` completes phase-two recovery, forces recovered work to disk, drains buffers, and clears recovery-needed state.

`xfs_log_reserve` allocates a ticket, checks grant-space availability, and advances both reserve and write grant heads. `xfs_log_regrant`, `xfs_log_ticket_regrant`, and `xfs_log_ticket_ungrant` handle rolling and completed transaction accounting.

`xlog_state_get_iclog_space` grants writers space in the active iclog. If the current iclog cannot fit more useful records, it switches that iclog to `XLOG_STATE_WANT_SYNC`, advances the ring, and arranges for flushing when references drain.

`xlog_write` copies CIL or direct log vectors into iclogs. It uses `xlog_write_full` for vectors that fit and `xlog_write_partial` for regions that must span iclogs with continuation opheaders.

`xlog_sync` prepares an iclog for disk by rounding the size, stamping cycle numbers into basic blocks, filling record length and checksum, handling physical log wrap, and submitting the write through `xlog_write_iclog`.

## State Machines and Ordering

The iclog state machine flows through active, want-sync, syncing, done-sync, callback, dirty, and back to active. `xlog_state_done_syncing`, `xlog_state_do_callback`, and `xlog_state_clean_iclog` preserve callback order so CIL checkpoint completion and AIL insertion happen in log order.

The log covering state machine tracks idle cover progress through `XLOG_STATE_COVER_IDLE`, `NEED`, `DONE`, `NEED2`, and `DONE2`. Covering only proceeds when the CIL, AIL, and iclogs are empty.

Log forcing combines CIL pushing and iclog flushing. `xfs_log_force` forces the current state of the log, while `xfs_log_force_seq` first asks the CIL to expose a checkpoint commit LSN and then forces the corresponding iclog.

## Concurrency and Error Handling

`l_icloglock` protects iclog ring state, current head position, and iclog state transitions. Grant-head locks protect waiter lists, while the fast path avoids taking them when no waiters exist. Memory barriers pair grant-space visibility with AIL tail-space updates.

I/O completion runs through `xlog_ioend_work`, which converts bio status to errors, triggers shutdown on log I/O failure, completes the iclog state transition, and releases teardown serialization.

`xlog_force_shutdown` is the global log shutdown path. It optionally forces the log first, atomically marks log I/O error state, marks the mount shut down, wakes reservation waiters, wakes CIL force waiters, runs pending callbacks, and wakes zoned realtime waiters when applicable.

## Research Notes

This file is both performance-sensitive and correctness-sensitive. The key invariants are: grant accounting must not overrun tail space, iclog callbacks must run in LSN order, commit records that require persistence must set flush/FUA requirements, and log wrap must update block before cycle so lockless LSN validation cannot observe a transient future LSN.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_log.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_log.h

## Purpose

`xfs_log.h` is the public XFS log manager header used by the rest of XFS. It defines log region type constants, formatting helpers, LSN comparison helpers, log force flags, and prototypes for the main log and CIL-facing APIs.

## Key Contents

The `XLOG_REG_TYPE_*` constants classify log iovec regions for buffers, inodes, quotas, transaction headers, commit records, unmount records, deferred operation intents/dones, attribute intents, exchange mapping intents, and related payloads. `XLOG_REG_TYPE_MAX` is currently `34`.

`xlog_calc_iovec_len` rounds arbitrary payload lengths to 32-bit alignment so item sizing matches later formatting.

`xlog_format_start`, `xlog_format_commit`, and `xlog_format_copy` are the public helpers for CIL log vector formatting. The implementations of start/commit live in `xfs_log_cil.c`.

`_lsn_cmp` compares XFS log sequence numbers by cycle and block components instead of treating them as raw 64-bit values. `XFS_LSN_CMP` aliases this helper.

## Exported Interfaces

The header declares mount lifecycle functions, log forcing functions, tail assignment and log-space wakeups, reservation lifecycle functions, ticket refcount helpers, CIL committed-item processing, current-checkpoint testing, log work scheduling, quiesce/clean operations, LSN validation, and forced shutdown.

Important declarations include:

- `xfs_log_mount`, `xfs_log_mount_finish`, `xfs_log_mount_cancel`, `xfs_log_unmount`
- `xfs_log_force`, `xfs_log_force_seq`
- `xlog_assign_tail_lsn`, `xfs_log_space_wake`
- `xfs_log_reserve`, `xfs_log_regrant`
- `xfs_log_ticket_get`, `xfs_log_ticket_put`
- `xlog_cil_process_committed`, `xfs_log_item_in_current_chkpt`
- `xfs_log_quiesce`, `xfs_log_clean`, `xfs_log_check_lsn`
- `xlog_force_shutdown`

## Research Notes

This header is a compact contract boundary. The region type values and LSN comparison helper must remain consistent with transaction formatters and recovery code. Most implementation details are hidden in `xfs_log_priv.h`, `xfs_log.c`, and `xfs_log_cil.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_log.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_log_cil.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_log_cil.c

## Purpose

`xfs_log_cil.c` implements the XFS Committed Item List. The CIL aggregates committed transaction items in memory into checkpoint contexts, supports relogging of frequently modified metadata, asynchronously pushes checkpoints to the core log, and completes checkpoints by moving committed items to the AIL and unpinning them.

It sits between transaction commit and the lower-level iclog writer in `xfs_log.c`.

## Core Model

The active `struct xfs_cil_ctx` collects formatted log vectors, busy extents, per-CPU accounting, and log items for one checkpoint sequence. Transaction commit formats dirty log items into reusable or shadow log vector buffers, inserts them into the active CIL, steals unused reservation into the checkpoint ticket, and may trigger a background push.

A push switches to a fresh CIL context, builds an ordered log vector chain from the old context, writes a checkpoint start/header and item payloads, writes an ordered commit record, and attaches completion callbacks to the commit iclog.

## Formatting and Insertion

`xlog_cil_alloc_shadow_bufs` preallocates or resizes per-item shadow log vectors before taking the CIL context lock. This avoids memory reclaim deadlocks while a push needs to make progress.

`xlog_format_start` and `xlog_format_commit` build aligned log iovec regions with embedded `xlog_op_header` records. They handle payload alignment, zero padding, region type assignment, op header length, and byte accounting.

`xlog_cil_insert_format_items` formats dirty transaction items into reusable or shadow log vectors. `xfs_cil_prepare_item` pins newly inserted items, swaps old vectors into shadow storage when relogging, adjusts space accounting, and records the first CIL sequence on the item.

`xlog_cil_insert_items` performs per-CPU accounting, busy extent aggregation, reservation stealing, CIL item ordering, and transaction ticket reservation checks. It uses per-CPU counters below the soft threshold and switches to atomic accounting near or above the CIL limit.

## Push Path

`xlog_cil_push_work` is the main checkpoint push worker. It allocates a new context and ticket, aggregates per-CPU state, skips empty or already-pushed contexts, adds the old context to the committing list, switches to a new context, sorts the log vector chain, builds a checkpoint transaction header, writes the item chain, writes the commit record, handles multi-iclog ordering, marks the commit iclog for stable storage, releases the commit iclog, and ungrants the checkpoint ticket.

Whiteout handling lets paired intent/done items from the same checkpoint avoid unnecessary journal writes. `xlog_cil_process_intents` marks the intent item as whiteout and releases the done item when both are atomic within the current checkpoint.

## Completion Path

`xlog_cil_set_ctx_write_state` records checkpoint `start_lsn` on the first write and `commit_lsn` on the commit write. It attaches the context callback before publishing the commit LSN so callback order matches commit record order.

`xlog_cil_process_committed` drains completed contexts from iclog callback lists. `xlog_cil_committed` inserts items into the AIL, clears busy extents, handles discard, removes the context from the committing list, frees log vectors, and releases the context.

`xlog_cil_ail_insert` updates the AIL head LSN to the commit record LSN, returns grant space in the correct order, runs `iop_committed`, bulk-inserts normal items at the checkpoint start LSN, handles special item LSNs individually, and unpins items. Abort mode skips AIL insertion and unpins with abort semantics.

## Forcing and Throttling

`xlog_cil_push_background` queues background pushes when the soft CIL space limit is exceeded and throttles transaction commits above the hard blocking limit.

`xlog_cil_push_now` queues immediate pushes for log force and flush operations. Synchronous callers flush prior work to reduce wait time. Async flush requests set `xc_push_commit_stable` so the push worker forces the commit record to stable storage.

`xlog_cil_force_seq` ensures a requested checkpoint sequence has been pushed far enough to expose a commit LSN. It waits for lower or equal sequence commits as needed and returns the commit LSN used by `xfs_log_force_seq`.

## Initialization and Teardown

`xlog_cil_init` allocates `struct xfs_cil`, creates a bounded push workqueue, allocates per-CPU CIL state, initializes locks and waitqueues, installs the first context, and attaches the CIL to the log.

`xlog_cil_init_post_recovery` allocates the first checkpoint ticket after recovery has established log geometry. `xlog_cil_destroy` frees the active context, ticket, per-CPU state, workqueue, and CIL.

## Research Notes

The central correctness requirements are strict checkpoint ordering, accurate reservation stealing, avoiding memory reclaim deadlocks, preserving stable-storage ordering with flush/FUA flags, and completing callbacks in the same order as commit records. The CIL is optimized for repeated relogging while bounding pinned memory and checkpoint size.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_log_cil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_log_priv.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_log_priv.h

## Purpose

`xfs_log_priv.h` defines private structures, state constants, helper functions, and internal prototypes shared by XFS log implementation files. It is the internal contract for `xfs_log.c`, `xfs_log_cil.c`, recovery code, and related transaction/log components.

## Core Structures

`struct xfs_log_iovec` describes a typed log region: address, byte length, and region type.

`struct xfs_log_vec` groups iovecs for one log item in the CIL. It tracks list linkage, ordering id, iovec array, owning item, formatted buffer, used bytes, and allocation size.

`struct xlog_ticket` tracks a transaction reservation: queue linkage, owner task, transaction id, refcount, current and unit reservations, permanent reservation counts, flags, and iclog header accounting.

`struct xlog_in_core` is an in-core log buffer. It contains waitqueues, ring pointers, owning log pointer, size/offset/state/flags, data and header pointers, callback list, refcount, semaphore, completion work, bio, and bio vectors. The layout separates hot fields onto cachelines to reduce contention.

`struct xfs_cil_ctx` is a CIL checkpoint context. It records sequence, start and commit LSNs, commit iclog, checkpoint ticket, aggregate space, busy extents, log item/vector lists, callback linkage, push work, ordering counter, and CPU mask for per-CPU contributors.

`struct xlog_cil_pcp` holds per-CPU CIL accumulation: space used, reservation space, busy extents, and log items.

`struct xfs_cil` owns active CIL state: current context, push workqueue, locks, push sequence, committing list, waitqueues, current sequence, and per-CPU storage.

`struct xlog` is the main log object. It ties together mount, AIL, CIL, target device, workqueues, operational state, recovered intents, iclog geometry, physical log geometry, iclog ring state, atomic tail LSN, grant heads, sysfs object, recovery LSN, and iclog roundoff.

## State and Flags

The iclog state enum covers active, want-sync, syncing, done-sync, callback, and dirty states. Iclog flags include `XLOG_ICL_NEED_FLUSH` and `XLOG_ICL_NEED_FUA`.

Ticket flags include `XLOG_TIC_PERM_RESERV`.

Covering states model idle log cover progression: idle, need, done, need2, done2. These support the two-dummy-transaction scheme used to make allocation transactions safe after idle periods.

Operational state bits include active recovery, recovery needed, log I/O error, tail warning issued, and shutdown-started exclusion.

CIL flags include `XLOG_CIL_EMPTY` and `XLOG_CIL_PCP_SPACE`.

## Thresholds and Helpers

`XLOG_CIL_SPACE_LIMIT` computes the background CIL push threshold as the smaller of one-eighth of log size and sixteen times the iclog buffer window. `XLOG_CIL_BLOCKING_SPACE_LIMIT` doubles that threshold for throttling.

`struct xlog_grant_head` contains the grant lock, waiter list, and atomic grant byte count for reservation and write heads.

Important helpers include:

- `xlog_get_client_id` for extracting packed op header client ids.
- `xlog_recovery_needed`, `xlog_in_recovery`, and `xlog_is_shutdown`.
- `xlog_shutdown_wait`.
- `xlog_crack_atomic_lsn` and `xlog_assign_atomic_lsn`.
- `xlog_wait` for serialized waitqueue sleeps.
- `xlog_lsn_sub` for byte distance between LSNs with wrap handling.
- `xlog_valid_lsn` for lockless metadata LSN validation with locked recheck.
- `xlog_kvmalloc` for fast kmalloc/vmalloc fallback in NOFS contexts.
- `xlog_item_space` for log space calculation including op headers.
- `xlog_cycle_data` for main or extended log record cycle storage.

## Internal Prototypes

The header declares recovery entry points, checksum support, ticket allocation, transaction/ticket debug printing, log write functions, ticket grant helpers, iclog state functions, CIL initialization/destruction/commit/force routines, and grant-space return.

## Research Notes

This header captures the log subsystem’s design constraints: hot-path cacheline placement, waitqueue serialization, atomic LSN sampling, dynamic CIL reservation stealing, bounded CIL memory pressure, and careful log wrap handling. It is essential context for understanding both `xfs_log.c` and `xfs_log_cil.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_log_priv.h -->