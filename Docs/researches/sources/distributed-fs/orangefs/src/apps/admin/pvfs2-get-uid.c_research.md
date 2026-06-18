# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-get-uid.c

Purpose: `pvfs2-get-uid.c` queries OrangeFS management servers for UID activity statistics and prints per-server UID counters and time ranges. It can target explicit BMI server addresses or discover all servers for a filesystem.

Important APIs, types, and functions: `struct options` holds history seconds, a fixed-size `server_list`, `server_count`, and optional `PVFS_fs_id`. The code uses `PVFS_util_init_defaults`, `PVFS_util_gen_credential_defaults`, `PVFS_util_get_default_fsid`, `BMI_addr_lookup`, `PVFS_mgmt_count_servers`, `PVFS_mgmt_get_server_array`, `PVFS_mgmt_get_uid_list`, `PINT_util_get_current_timeval`, and `PINT_util_parse_timeval`. Returned records are `PVFS_uid_info_s` arrays sized by `UID_MGMT_MAX_HISTORY`.

Control flow: after parsing `-s`, `-t`, `-f`, and `-h`, the program defaults missing history to `UID_HISTORY_MAX_SECS`. It initializes OrangeFS defaults and credentials, selects the filesystem id, builds a BMI address array either from repeated `-s` options or by querying all servers, allocates one UID history buffer per server plus count buffers, then calls `PVFS_mgmt_get_uid_list`. The output includes fsid, current time, server URI, and each UID record's uid, count, start timestamp, and last timestamp. `cleanup` frees options, server strings, address arrays, and per-server stats arrays.

State and persistence: no persistent state is written. The tool reads OrangeFS configuration through the util initialization path and samples server-side UID history. Its only durable effect is stdout/stderr output.

Dependencies and integration points: it integrates with BMI for address lookup and with the management API's UID tracking feature. If server addresses are not supplied, it depends on cached config and management server enumeration to map the filesystem to servers. Time formatting comes from internal `PINT_util_*` helpers.

Risks: `server_list` is allocated for `UID_SERV_LIST_SIZE`, but in auto-discovery mode the code stores discovered server strings into `prog_opts->server_list[i]` for `server_count` without capping `server_count` to 64. Several error paths return without `PVFS_sys_finalize` or cleanup. `uid_info_count` allocation failure logs an error but does not immediately return before later use. `atoi` parsing gives weak validation for history and fsid. The server-limit branch checks equality then greater-than in a way that still leaves parsing behavior somewhat unclear.

Test signals: exercise explicit single and repeated `-s` lookups, auto-discovery, invalid BMI address, default fsid lookup, explicit `-f`, invalid negative `-f`, `-t 0`, large server counts above 64, management API failures, and output formatting for empty and populated UID history arrays.
