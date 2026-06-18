<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-set-turn-off-timeouts.c -->
## sources/distributed-fs/orangefs/src/apps/admin/pvfs2-set-turn-off-timeouts.c

**Purpose:** `pvfs2-set-turn-off-timeouts` toggles server-side credential/capability timeout checking for all servers in a filesystem, unless key or certificate security is compiled in.

**Important APIs, types, and functions:** `struct options` stores mount and a string value for `TurnOffTimeouts`. `parse_args()` requires `-m` and `-t yes|no`, appends `/` to the mount, and validates the value case-insensitively. `main()` sends `PVFS_SERV_PARAM_TURN_OFF_TIMEOUTS` as `PVFS_MGMT_PARAM_TYPE_STRING` via `PVFS_mgmt_setparam_all`.

**Control flow:** Compile-time security macros cause an immediate message and exit before parsing. Otherwise the tool parses input, initializes PVFS, resolves the mount, generates credentials, sends the string setparam to all servers, prints status, finalizes, and returns the setparam result.

**State and persistence:** This is a security-relevant live server setting. Setting it to `yes` disables timeout checking and can weaken credential/capability expiry enforcement. The program does not edit config.

**Dependencies and integration points:** It depends on compile-time security configuration, management APIs, and server parameter handling. It is operationally tied to authentication and credential timeout behavior.

**Risks and edge cases:** The parser uses `strdup` then `strcat` without reserving room for the appended slash, which can overflow. The required-argument check uses `if (!mflag && !tflag)`, so mixed missing argument paths are handled in later branches but the expression is easy to misread. Tests should cover security-enabled builds, `yes`/`no` variants, missing arguments, mount string length, and server rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-set-turn-off-timeouts.c -->
