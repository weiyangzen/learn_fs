<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-set-sync.c -->
## sources/distributed-fs/orangefs/src/apps/admin/pvfs2-set-sync.c

**Purpose:** `pvfs2-set-sync` toggles implicit metadata and data syncing behavior across all servers for a filesystem.

**Important APIs, types, and functions:** `struct options` stores mount, `meta_sync`, and `data_sync` booleans. `parse_args()` requires `-m`, `-M 0|1`, and `-D 0|1`. `main()` sends `PVFS_SERV_PARAM_SYNC_META` and `PVFS_SERV_PARAM_SYNC_DATA` through `PVFS_mgmt_setparam_all`.

**Control flow:** The parser validates both sync flags as 0 or 1. `main()` resolves the mount, creates credentials, sets metadata sync first, then data sync. If the first setparam succeeds but the second fails, the filesystem is left in a mixed requested state.

**State and persistence:** It changes live durability/performance behavior on all servers. Enabling sync can reduce data-loss windows but increases latency; disabling sync does the opposite. No config file is edited.

**Dependencies and integration points:** It depends on server support for sync setparams and normal management credentials. It affects all clients using the filesystem after the live change.

**Risks and edge cases:** There is no rollback if one of the two changes fails. It does not request detailed per-server status, so partial deployment is hard to diagnose. Tests should cover all four flag combinations, invalid values, partial failure injection, and post-change behavior observed through server config or write durability tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-set-sync.c -->
