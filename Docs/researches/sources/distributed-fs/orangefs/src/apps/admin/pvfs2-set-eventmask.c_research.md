<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-set-eventmask.c -->
## sources/distributed-fs/orangefs/src/apps/admin/pvfs2-set-eventmask.c

**Purpose:** `pvfs2-set-eventmask` enables server event monitoring categories for all servers in the filesystem identified by a mount point.

**Important APIs, types, and functions:** `struct options` tracks `mnt_point` and `event_string`. `parse_args()` requires `-m` and `-e`; `main()` calls `PVFS_util_init_defaults`, `PVFS_util_resolve`, `PVFS_util_gen_credential_defaults`, and `PVFS_mgmt_setparam_all` with `PVFS_SERV_PARAM_EVENT_ENABLE` and a string parameter.

**Control flow:** The parser appends `/` to the mount, saves the event string, and rejects missing mount/events. `main()` resolves the mount to an fsid, creates credentials, uses the provided event list or `"none"` as the parameter, and sets it on all servers.

**State and persistence:** The program changes live server event monitoring state. It does not persist edits into config files. It finalizes PVFS only on the success path.

**Dependencies and integration points:** It depends on server-side recognition of event names such as `bmi-send` and `dbpf-write`. It is typically paired with event-monitoring tools that consume the enabled event stream.

**Risks and edge cases:** The `case 'e'` branch checks an old `ret` value rather than validating `strdup`, so allocation failure or malformed event strings are not handled cleanly. Event names are not locally validated. Early errors leak options and may skip finalization. Tests should include required-option validation, empty event lists, server rejection of unknown events, and successful `none`/multi-event updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-set-eventmask.c -->
