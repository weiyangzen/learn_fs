# sources/distributed-fs/ceph-client/tools/lib/subcmd/subcmd-config.c

Purpose: Defines the global `subcmd_config` object shared by libsubcmd modules.

Important APIs/types/functions: `struct subcmd_config subcmd_config` is initialized with sentinel string `SUBCMD_HAS_NOT_BEEN_INITIALIZED` for exec name, prefix, exec path, exec path environment, and pager environment.

Control flow: No functions. Initialization occurs at load time; `exec_cmd_init()` and `pager_init()` later populate fields.

State and persistence: Process-global mutable configuration.

Dependencies/integration: Includes `subcmd-config.h`; used by exec, pager, parse-options, and help modules.

Risks: Consumers can use sentinel values if initialization is skipped, potentially creating invalid environment lookups or paths. No locking for concurrent mutation.

Test signals: Verify default values, initialization through exec/pager APIs, and behavior when uninitialized.
