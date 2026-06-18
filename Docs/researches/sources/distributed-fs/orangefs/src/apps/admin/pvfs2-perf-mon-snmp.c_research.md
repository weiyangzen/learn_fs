# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-perf-mon-snmp.c

Purpose: `pvfs2-perf-mon-snmp.c` adapts OrangeFS performance counters to a simple stdin/stdout protocol suitable for SNMP pass/persist style polling. It maps fixed OIDs to management performance counters and returns a type plus value.

Important APIs, types, and functions: `struct MGMT_perf_iod` maps OID string, SNMP type (`INTEGER` or `COUNTER`), `PINT_PERF_*` key number, and name. `key_table` defines OIDs under `.1.3.6.1.4.1.7778`. `struct options` stores either mount point or explicit server address. The tool uses `PVFS_util_init_defaults`, `PVFS_util_gen_credential_defaults`, `PVFS_util_get_default_fsid`, `BMI_addr_lookup`, `PVFS_util_resolve`, `PVFS_mgmt_count_servers`, `PVFS_mgmt_get_server_array`, and `PVFS_mgmt_perf_mon_list`.

Control flow: parsing requires either `-m fs_mount_point` or `-s bmi_address_string`. With `-s`, the program uses the default fsid and a single looked-up BMI address. With `-m`, it resolves the mount and samples all I/O servers. It counts keys from `key_table`, allocates a one-sample matrix and tracking arrays, then loops reading commands from stdin. `PING` returns `PONG`. `GET` reads the next line as an OID, looks it up in `key_table`, and returns `NONE` if unknown. For valid OIDs it refreshes the performance snapshot if the cached snapshot is older than 60 seconds, then prints the SNMP type and unsigned value.

State and persistence: no files are written. The process caches one performance snapshot for up to 60 seconds using `snaptime`, `perf_matrix`, `next_id_array`, and `end_time_ms_array`.

Dependencies and integration points: this utility is meant to be driven by an SNMP daemon. The OID table comments say it must match `include/pvfs2-mgmt.h`, so key-number drift is a direct integration risk. It can operate from an OrangeFS mount point or a raw BMI server address.

Risks: `returnValue` is initialized to zero for each command and only assigned inside the snapshot-refresh block; valid GETs within 60 seconds after a refresh can return zero instead of cached matrix data. Only `srv = 0` is returned even when multiple I/O servers are sampled. The program does not refresh credentials inside the loop. Memory and sysint cleanup after the infinite loop are unreachable. The command buffer is fixed at 256 bytes and longer OIDs/commands are not robustly drained. Error output from `PVFS_perror` may interfere with SNMP expectations if written to stdout by dependencies.

Test signals: simulate pass/persist input with `PING`, unknown commands, unknown OIDs, valid OIDs before and after the 60-second cache window, mount-discovered multi-server mode, explicit server mode, invalid BMI address, management failure, and key table alignment with `PINT_PERF_*` values. A regression test should specifically catch repeated valid GET returning zero due to cache logic.
