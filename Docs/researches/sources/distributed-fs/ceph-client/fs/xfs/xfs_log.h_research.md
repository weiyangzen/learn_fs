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
