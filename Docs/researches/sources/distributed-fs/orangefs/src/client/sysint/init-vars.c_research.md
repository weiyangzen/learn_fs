# sources/distributed-fs/orangefs/src/client/sysint/init-vars.c
## sources/distributed-fs/orangefs/src/client/sysint/init-vars.c

**Purpose:** Defines sysint global initialization variables shared across the client, currently `relatime_timeout`.

**APIs and control flow:** The file includes `init-vars.h` and defines `int relatime_timeout;`. The value is assigned during `PVFS_sys_initialize()` based on `PVFS2_RELATIME_TIMEOUT` or the default one-day timeout.

**State and dependencies:** Provides one process-global integer used by sysint/user-interface code that needs relatime policy.

**Risks and tests:** Global mutable state depends on initialization order and has no locking around reads after initialization. Tests should verify default value, environment override, negative/zero semantics, and that code using it does not read before `PVFS_sys_initialize()`.
