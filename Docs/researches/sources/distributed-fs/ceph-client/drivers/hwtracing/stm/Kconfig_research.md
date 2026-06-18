
# sources/distributed-fs/ceph-client/drivers/hwtracing/stm/Kconfig

Purpose: Kconfig menu for the generic System Trace Module framework, framing protocols, dummy test device, and kernel trace sources.

Important APIs/types/functions: `CONFIG_STM` selects `CONFIGFS_FS`. Suboptions include `STM_PROTO_BASIC`, `STM_PROTO_SYS_T`, `STM_DUMMY`, `STM_SOURCE_CONSOLE`, `STM_SOURCE_HEARTBEAT`, and `STM_SOURCE_FTRACE` with `TRACING` dependency for ftrace.

Control flow: enabled symbols control which objects the STM Makefile builds and which modules are available for policy/protocol/source testing.

State and persistence: build configuration only.

Dependencies and integration: integrates STM with configfs, Linux tracing, console, and module selection.

Risks: defaulting protocol drivers to `STM` changes module availability and autoload expectations. Missing `CONFIGFS_FS` would break policy creation, hence selected by core.

Test signals: config/build matrix for each protocol/source, especially `STM_SOURCE_FTRACE` with and without `TRACING`.
