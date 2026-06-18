# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_trace.h

Purpose: declares the IOSM trace debugfs/relayfs interface and provides no-op fallbacks when WWAN debugfs support is disabled.

Important APIs/types: `enum trace_ctrl_mode` defines disabled/enabled states. `struct iosm_trace` stores relay channel, debugfs control dentry, IMEM pointer, device pointer, opened IPC channel, trace channel ID, mutex, and mode. When `CONFIG_WWAN_DEBUGFS` is enabled, `ipc_is_trace_channel()` checks whether an incoming channel ID is the trace channel, and the init/deinit/RX functions are exported. When disabled, `ipc_is_trace_channel()` always returns false and `ipc_trace_port_rx()` just frees the SKB.

Control flow and state: the header controls compile-time feature presence and prevents non-debugfs builds from carrying relay/debugfs behavior while keeping callers simple.

Dependencies and integration points: includes debugfs, relayfs, IOSM channel config, and IMEM ops. It is integrated into IOSM receive demultiplexing so trace SKBs are diverted away from normal control or WWAN paths.

Risks and test signals: conditional compilation is the main risk. Build both `CONFIG_WWAN_DEBUGFS=y` and disabled configurations. Runtime signals include successful debugfs file creation, correct channel identification, and safe SKB freeing in the disabled stub.
