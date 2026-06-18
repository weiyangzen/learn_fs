# sources/distributed-fs/ceph-client/fs/xfs/xfs_message.h

Purpose: Declares the XFS diagnostic API and macro layer used throughout the filesystem for severity-specific logging, ratelimited logging, once-only logging, assertions, hex dumps, tagged alerts, buffer alerts, and experimental feature warnings.

Important APIs, types, and functions: Defines `xfs_emerg`, `xfs_alert`, `xfs_crit`, `xfs_err`, `xfs_warn`, `xfs_notice`, `xfs_info`, and conditional `xfs_debug`. `xfs_printk_index_wrap` emits printk index metadata before calling `xfs_printk_level`. `xfs_alert_tag` wraps `_xfs_alert_tag`. Ratelimited and once macros generate per-callsite static state. `enum xfs_experimental_feat` currently covers shrink, logged extended attributes, and zoned realtime devices.

Control flow: Macros forward format strings and arguments to implementation functions while preserving printf checking. DEBUG builds route `xfs_debug` to printk; non-DEBUG builds compile it away. Ratelimited macros call a selected XFS logging macro only when the local ratelimit permits.

State and persistence behavior: Header has no direct storage beyond static ratelimit state emitted at call sites. Experimental warnings rely on mount opstate bits managed by `xfs_message.c`.

Dependencies and integration points: Pulls in `linux/once_lite.h`, forward declares `struct xfs_mount`, and is included by `xfs_platform.h`, making it part of the base include surface for nearly all XFS source files.

Risks: Since most interfaces are macros, side-effecting arguments must be safe under ratelimit/once behavior. The printk-index wrapper must stay consistent with the actual printed format for indexing tools. Adding experimental enum values requires updating the implementation table.

Test signals: Compile with and without DEBUG; run sparse/format checking for printf attributes; confirm ratelimited call sites maintain independent state; add an experimental enum only with matching implementation table coverage.
