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
