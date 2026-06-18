# sources/distributed-fs/orangefs/src/client/usrint/env-vars.h
## sources/distributed-fs/orangefs/src/client/usrint/env-vars.h

**Purpose:** Declares the optional environment-variable tracking structures for OrangeFS user-interface configuration.

**APIs and control flow:** Under `PVFS_USER_ENV_VARS_ENABLED`, defines enum IDs for `ORANGEFS_DIST_NAME`, `ORANGEFS_DIST_PARAMS`, `ORANGEFS_NUM_DFILES`, `ORANGEFS_LAYOUT`, `ORANGEFS_LAYOUT_SERVER_LIST`, `ORANGEFS_CACHE_FILE`, and `ORANGEFS_STRIP_SIZE_AS_BLKSIZE`. It defines per-variable and aggregate structs, and declares global `env_vars`, names, initializer, and dumper.

**State and dependencies:** Depends on `pvfs2-config.h` to compile in or out. The `pad[4]` field suggests alignment or future expansion but is unused.

**Risks and tests:** `ENV_VAR_ENUM_COUNT` must stay synchronized with enum entries and string array length. Tests should compile with the feature enabled/disabled and verify every enum maps to the intended string.
