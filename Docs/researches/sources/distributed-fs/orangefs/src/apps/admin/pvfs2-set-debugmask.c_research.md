<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-set-debugmask.c -->
## sources/distributed-fs/orangefs/src/apps/admin/pvfs2-set-debugmask.c

**Purpose:** `pvfs2-set-debugmask` changes the live gossip/debug mask on all servers for a mount, or on one named server. It is an operational diagnostics tool for increasing or disabling server logging.

**Important APIs, types, and functions:** `struct options` contains mount point, parsed debug mask, and optional server address. `parse_args()` supports `-m/--mount`, `-s/--server`, version/help, and a trailing mask list. `PVFS_debug_eventlog_to_mask` translates keyword lists. `usage()` enumerates available debug keywords through `PVFS_debug_get_next_debug_keyword`. Runtime calls are `PVFS_util_init_defaults`, `PVFS_util_resolve`, `PVFS_util_gen_credential_defaults`, `PVFS_mgmt_setparam_single`, and `PVFS_mgmt_setparam_all` with `PVFS_SERV_PARAM_GOSSIP_MASK`.

**Control flow:** The tool requires a mount and final mask list. It resolves the mount to an fsid, builds credentials, wraps the mask in a `PVFS_MGMT_PARAM_TYPE_UINT64`, then targets either the provided server string or all servers. It prints a human-readable PVFS error string if the setparam fails and returns `PVFS_sys_finalize()` rather than the setparam result.

**State and persistence:** It changes live server debug state. Whether the value persists depends on server management parameter behavior; the program itself does not write configuration files. It allocates option strings but does not free them before exit.

**Dependencies and integration points:** This integrates with the management setparam path and the gossip debug keyword registry. The optional server string must match server addressing accepted by the management API.

**Risks and edge cases:** Returning `PVFS_sys_finalize()` can mask a failed setparam. A typo in the mask can translate to an unintended mask if `PVFS_debug_eventlog_to_mask` tolerates unknown tokens. Server-specific mode does not validate the server against cached config before issuing the call. Tests should assert mask translation, all-server and single-server paths, invalid mount handling, invalid server handling, and that failures propagate correctly if fixed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-set-debugmask.c -->
