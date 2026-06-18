# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-perf-mon-example.c

Purpose: `pvfs2-perf-mon-example.c` is an interactive/example performance monitor that repeatedly samples OrangeFS I/O-server counters and prints bandwidth and operation counters to stdout.

Important APIs, types, and functions: `struct options` stores mount point, history, and key count. Counter access is implemented by matrix macros such as `READ`, `WRITE`, `METADATA_READ`, `REQUESTS`, `CREATES`, `GETATTRS`, and `VALID_FLAG`. The code uses `PVFS_util_init_defaults`, `PVFS_util_resolve`, `PVFS_util_gen_credential_defaults`, `PVFS_mgmt_count_servers`, `PVFS_mgmt_get_server_array`, `PVFS_util_refresh_credential`, `PVFS_mgmt_perf_mon_list`, and `PVFS_mgmt_map_addr`.

Control flow: parsing requires `-m fs_mount_point`, optionally accepts `-h history`, `-k keys`, and `-v` version, and appends a slash to the mount path for later resolution. Main defaults history to 10, initializes OrangeFS, resolves the mount, generates credentials, counts I/O servers, allocates a per-server performance matrix plus `next_id` and end-time arrays, and builds the I/O-server address array. It then loops forever: refresh credential, request up to `MAX_KEY_CNT` counter keys with `PVFS_mgmt_perf_mon_list`, print server headers, compute data read/write MB/s from byte deltas and sample intervals, print other counters across the history window, flush, and sleep five seconds.

State and persistence: no persistent state is written. Runtime state is the rolling `next_id_array`, returned matrix samples, and credential refresh state. The process is intentionally long-running.

Dependencies and integration points: it samples management performance counters defined by `pvfs2-mgmt.h`/`PINT_PERF_*` and is useful for manual diagnostics or as sample code for external monitoring integrations. It depends on a mounted or configured filesystem path to discover I/O servers.

Risks: the code after the infinite loop, including `PVFS_sys_finalize`, is unreachable. Allocations are not freed. The `-k` option is parsed but not actually used because `key_cnt` is reset to `MAX_KEY_CNT`. Bandwidth calculation can divide by zero if timestamps match. Counter matrix layout is encoded in macros and must stay aligned with `PVFS_mgmt_perf_mon_list` key ordering. It prints indefinitely and has no signal cleanup. History values are not bounded before allocation.

Test signals: run against a small test filesystem with one and multiple I/O servers, verify valid/invalid mount handling, history default and explicit values, counter matrix dimensions, credential refresh over long runtime, zero-read/write shortcuts, timestamp edge cases, and management failures. Static tests should check key ordering against `pvfs2-mgmt.h`.
