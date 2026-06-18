# sources/distributed-fs/orangefs/src/client/usrint/env-vars.c
## sources/distributed-fs/orangefs/src/client/usrint/env-vars.c

**Purpose:** Implements optional user-interface environment variable capture for OrangeFS layout/distribution/cache configuration.

**APIs and control flow:** When `PVFS_USER_ENV_VARS_ENABLED` is true, defines global `env_vars` and string names for seven variables. `env_vars_struct_initialize()` iterates through names, stores each name, current `getenv()` value, and enum ID. `env_vars_struct_dump()` prints each captured name/value pair.

**State and dependencies:** Global `env_vars` persists captured pointers to process environment strings. Depends on `pvfs2-config.h`, libc `getenv`, and stdio.

**Risks and tests:** Captured values are raw environment pointers, so later environment mutation can affect or invalidate them depending on libc behavior. `printf("%s", NULL)` for unset vars is implementation-sensitive and can crash on some C libraries. Tests should cover disabled builds, unset variables, all variables set, environment changes after initialization, and dump behavior with null values.
