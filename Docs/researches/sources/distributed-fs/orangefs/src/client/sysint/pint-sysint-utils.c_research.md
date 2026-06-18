# sources/distributed-fs/orangefs/src/client/sysint/pint-sysint-utils.c
## sources/distributed-fs/orangefs/src/client/sysint/pint-sysint-utils.c

**Purpose:** Provides shared sysint helpers for server configuration access, parent lookup, client-side OpenSSL/security initialization, and perf-counter timer startup.

**APIs and control flow:** `PINT_get_server_config_struct` and `PINT_put_server_config_struct` wrap the server config manager. `PINT_lookup_parent()` extracts a base directory and calls `PVFS_sys_lookup` to return the parent handle. With OpenSSL, `PINT_client_security_initialize/finalize()` set up/tear down OpenSSL algorithms, error strings, static locks, dynamic locks, and thread ID callbacks under a mutex. Without OpenSSL they return success. `client_perf_start_rollover()` allocates a `PVFS_CLIENT_PERF_COUNT_TIMER` SMCB, fills timer pointers, marks the counter running, and posts it.

**State and dependencies:** Security state includes `security_init_mutex`, `openssl_mutexes`, and `security_init_status`. Perf rollover depends on the client state-machine context. Other dependencies include cached config, path utilities, OpenSSL APIs, generated SM lookup, and gossip.

**Risks and tests:** OpenSSL API compatibility is compile-time conditional and brittle across versions. `PINT_client_security_initialize()` returns `-PVFS_EALREADY` on repeat init, while caller initialization treats negative returns as fatal. `client_perf_start_rollover()` can leak allocated SMCB on post failure. Tests should cover OpenSSL and non-OpenSSL builds, repeat init/finalize, parent lookup edge cases, and perf timer post failures.
