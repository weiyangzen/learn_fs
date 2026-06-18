# sources/distributed-fs/ceph-client/fs/xfs/xfs_discard.c

Purpose: Implements XFS online discard and FITRIM for data and realtime devices while avoiding long AGF lock holds by batching free-space scans and marking extents busy during discard.

Important APIs, types, and functions: Defines `xfs_discard_wq`, `xfs_discard_extents()`, `xfs_ioc_trim()`, data-device trim helpers, and realtime trim helpers under `CONFIG_XFS_RT`. Uses `struct xfs_trim_cur`, `struct xfs_trim_rtdev`, `struct xfs_trim_rtgroup`, and `XFS_DISCARD_MAX_EXAMINE`.

Control flow: FITRIM validates privileges, discard support, norecovery state, user range, granularity, and minlen. Data trim walks perags, forces the log, locks AGF, scans bnobt/cntbt in bounded batches, skips too-small or busy extents, inserts selected extents into busy-under-discard lists, drops locks, and submits asynchronous discard bios. Completion clears busy extents via `xfs_discard_wq`. Realtime paths use either synchronous legacy rtbitmap discard or rtgroup busy extent machinery.

State and persistence: Does not change allocation btrees directly; it temporarily records busy extents to block reallocation until discard completion. Successful FITRIM clamps returned range length.

Dependencies and integration points: Uses block discard APIs, log force, allocation btrees, perag/rtgroup iteration, busy extent tracking, realtime bitmap queries, freezer/signal checks, user-copy helpers, and tracepoints.

Risks and test signals: Risks are discarding uncommitted frees, busy extent leaks after bio errors, excessive AGF lock holds, range overflow, and realtime/data boundary mistakes. Test FITRIM ranges, minlen/granularity edges, concurrent allocation/free, signal/freezer interruption, no-discard devices, norecovery mounts, realtime devices, and slow discard latency.
