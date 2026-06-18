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
