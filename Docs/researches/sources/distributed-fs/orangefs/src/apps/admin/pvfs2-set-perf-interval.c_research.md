<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-set-perf-interval.c -->
## sources/distributed-fs/orangefs/src/apps/admin/pvfs2-set-perf-interval.c

**Purpose:** `pvfs2-set-perf-interval` changes the server performance sampling interval, in milliseconds, for one server or all servers behind a mount point.

**Important APIs, types, and functions:** It mirrors `pvfs2-set-perf-history` structurally. `struct options` records mount, interval, and optional server. `main()` sends `PVFS_SERV_PARAM_PERF_INTERVAL` through `PVFS_mgmt_setparam_single` or `PVFS_mgmt_setparam_all`, with optional `PINT_cached_config_check_type` validation.

**Control flow:** The parser requires `-m` and a final integer interval >= 1. `main()` initializes PVFS, resolves the mount, creates credentials, builds a uint64 setparam value, then targets one server or all servers. It finalizes on the shared `out` path.

**State and persistence:** This changes live sampling cadence. Short intervals increase monitoring overhead and history churn; long intervals reduce diagnostic precision. It does not write configuration files.

**Dependencies and integration points:** It integrates with server performance counters, cached config, and administrative monitoring.

**Risks and edge cases:** Non-numeric input becomes zero via `atoi`. The parse error condition prints “greater than 0” under a reversed check in one branch. The all-server path lacks per-server detail reporting. Tests should cover interval parsing, invalid server strings, successful single/all updates, very large intervals, and interaction with history size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-set-perf-interval.c -->
