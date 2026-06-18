<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-set-mode.c -->
## sources/distributed-fs/orangefs/src/apps/admin/pvfs2-set-mode.c

**Purpose:** `pvfs2-set-mode` switches OrangeFS servers between `normal` and `admin` modes, either cluster-wide for a mount or for one server.

**Important APIs, types, and functions:** `struct options` stores mount point, `enum PVFS_server_mode`, and optional server string. `parse_args()` accepts `-m`, optional `-s`, and a final mode token. `main()` resolves the mount, builds credentials, verifies a single-server target with `PINT_cached_config_check_type`, and sends `PVFS_SERV_PARAM_MODE` through `PVFS_mgmt_setparam_single` or `PVFS_mgmt_setparam_all`.

**Control flow:** After parsing, only exact `normal` and `admin` strings are accepted. For a single server the tool validates that the address appears in cached config before issuing setparam. The all-server path directly sends the mode to every server. Both paths finalize PVFS and return the setparam result.

**State and persistence:** This changes live server operating mode, a high-impact cluster state. It does not edit the config file. Depending on server behavior, admin mode may restrict client operations until returned to normal.

**Dependencies and integration points:** It integrates with cached config, management setparam, credentials, and operational workflows such as fsck/validate that may need admin mode.

**Risks and edge cases:** A partial all-server failure can leave mixed modes, and the code does not request detailed per-server errors. It does not free parsed options. Tests should cover mode validation, single-server config validation, all-server partial failure behavior, repeated idempotent mode changes, and operational recovery from admin mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-set-mode.c -->
