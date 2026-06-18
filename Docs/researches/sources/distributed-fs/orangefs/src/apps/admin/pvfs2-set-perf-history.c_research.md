<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-set-perf-history.c -->
## sources/distributed-fs/orangefs/src/apps/admin/pvfs2-set-perf-history.c

**Purpose:** `pvfs2-set-perf-history` changes the number of performance history samples retained by OrangeFS servers for a filesystem.

**Important APIs, types, and functions:** `struct options` stores mount, positive integer history, and optional server. `parse_args()` accepts `-m`, optional `-s`, and final history count via `atoi`. `main()` uses `PINT_cached_config_check_type` for single-server validation and sends `PVFS_SERV_PARAM_PERF_HISTORY` as a `PVFS_MGMT_PARAM_TYPE_UINT64`.

**Control flow:** The tool parses and validates mount/history, initializes PVFS, resolves the mount, creates credentials, and applies the history depth to one server or all servers. It prints success/failure messages and finalizes.

**State and persistence:** It changes live server performance instrumentation retention. Larger histories can increase memory use; smaller values reduce observability. The program does not persist the setting to config.

**Dependencies and integration points:** It is used with performance monitoring/stat tools and depends on the management interface and cached server config.

**Risks and edge cases:** `atoi` silently maps invalid strings to zero; the error message for negative/zero has a minor condition bug. No detailed per-server errors are requested. Tests should cover boundary values, non-numeric input, one-server and all-server updates, invalid server strings, and performance history visibility after change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-set-perf-history.c -->
