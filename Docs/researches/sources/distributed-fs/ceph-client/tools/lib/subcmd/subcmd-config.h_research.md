# sources/distributed-fs/ceph-client/tools/lib/subcmd/subcmd-config.h

Purpose: Defines the shared libsubcmd configuration structure and extern declaration.

Important APIs/types/functions: `struct subcmd_config` contains `exec_name`, `prefix`, `exec_path`, `exec_path_env`, and `pager_env`. `extern struct subcmd_config subcmd_config` exposes the global instance.

Control flow: Header-only configuration contract.

State and persistence: Describes process-global mutable strings owned by callers or static literals.

Dependencies/integration: Included by libsubcmd implementation files and tools that need direct config access.

Risks: Direct global access makes initialization ordering and thread safety caller responsibilities. The include guard uses `__PERF_SUBCMD_CONFIG_H`, reflecting perf heritage.

Test signals: Compile users and initialization tests through `subcmd-config.c`.
