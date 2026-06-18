# sources/distributed-fs/openafs/src/afs/afs_stats.h

## Purpose

`afs_stats.h` defines the Cache Manager statistics ABI and the macros used to collect call counts, RPC timings, transfer sizes, authentication/PAG stats, server uptime stats, access stats, and authorship stats. It is intentionally conservative because `struct afs_CMCallStats` is exported as an unversioned binary blob for xstat clients; the header explicitly warns that fields must only be appended, never removed, reordered, or made conditional.

## Important APIs, Types, and Macros

The most widely used macro is `AFS_STATCNT(name)`, which increments the corresponding `C_name` member in `afs_cmstats.callInfo`. `AFS_CM_CALL_STATS` is the master call-counter list spanning many Cache Manager source files. Timing macros include `XSTATS_DECLS`, `XSTATS_START_TIME`, `XSTATS_START_CMTIME`, and `XSTATS_END_TIME`; helper macros include `afs_stats_TimeLessThan`, `afs_stats_TimeGreaterThan`, `afs_stats_GetDiff`, `afs_stats_AddTo`, `afs_stats_TimeAssign`, and `afs_stats_SquareAddTo`.

Key structures are `afs_CMStats`, `afs_CMCallStats`, `afs_stats_SrvUpDownInfo`, `afs_stats_CMPerf`, `afs_stats_opTimingData`, `afs_stats_xferData`, `afs_stats_RPCErrors`, `afs_stats_RPCOpInfo`, `afs_stats_AuthentInfo`, `afs_stats_AccessInfo`, `afs_stats_AuthorInfo`, `afs_stats_CMFullPerf`, and `afs_CTD_stats`. The header also declares `extern struct afs_CMStats afs_cmstats`, with the concrete definitions supplied by `afs_stat.c`.

## Control Flow and State

The timing macros assume a local variable named `code` indicates operation result. `XSTATS_START_TIME` or `XSTATS_START_CMTIME` picks the relevant timing record and captures `opStartTime`; `XSTATS_END_TIME` captures stop time, increments operation count, and, on success, updates success count, elapsed-time sum, square sum, min, and max. Transfer stats are structured similarly but updated elsewhere. Server stats are divided into file-server and VL-server arrays, each with same-cell and different-cell slots; they record current up/down counts, total records, record ages, downtime incidents, duration buckets, and incident-count buckets.

## Dependencies and Integration Points

The header depends on `afs/param.h` and provides a user/kernel-compatible `osi_timeval32_t` definition outside kernel builds. It is included throughout Cache Manager code for lightweight counters and by xstat-related callback interfaces for binary data layout. `afs_server.c` updates `afs_stats_SrvUpDownInfo`; `afs_user.c` updates `afs_stats_AuthentInfo`; RPC wrappers and callback code use the XSTATS macros; `afs_stat.c` initializes the exported global instances.

## Persistence and ABI Behavior

All data is in-memory for a Cache Manager runtime, but the layout is externally consumed by monitoring clients. The call-counter list is therefore persistent as an ABI contract even when individual functions become unused. Spare fields in `afs_stats_CMPerf` exist for future expansion without breaking consumers.

## Risks and Test Signals

The main risks are ABI breakage from reordering/removing fields, adding conditional members, adding call counters anywhere except the end, or using timing macros without a valid `code` variable. Arithmetic macros use integer timeval math and can overflow if very large durations or sums accumulate. Test signals include xstat client compatibility across kernel/user builds, structure-size checks, RPC timing sanity after success and failure paths, and call-counter changes after representative vnode, pioctl, server, and token operations.
