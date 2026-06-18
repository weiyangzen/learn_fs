# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_trace.c

Purpose: provides IOSM modem trace capture through debugfs and relayfs. It opens a dedicated IOSM control channel on demand and writes incoming trace SKBs to a relay channel.

Important APIs/functions: `ipc_trace_init()` initializes IPC control channel 3, allocates `struct iosm_trace`, creates `trace_ctrl` debugfs control file, and opens the relay channel named `trace`. `ipc_trace_ctrl_file_write()` parses `0`/`1` user input and opens or closes the system port with `ipc_imem_sys_port_open()`/`ipc_imem_sys_port_close()`. `ipc_trace_ctrl_file_read()` exposes current mode. `ipc_trace_port_rx()` writes trace payloads to relayfs and frees SKBs. Relay callbacks create/remove buffer files and drop data when relay buffers are full. `ipc_trace_deinit()` removes debugfs, closes relay, destroys mutex, and frees state.

Control flow and state: `mode`, `channel`, and relay state are protected by `trc_mutex` for user control operations. RX path is simple and assumes `ipc_imem->trace` is valid when trace channel traffic is routed here.

Dependencies and integration points: depends on `CONFIG_WWAN_DEBUGFS`, debugfs, relayfs, IOSM channel config, and IMEM system port operations. It integrates with IOSM RX dispatch through `ipc_is_trace_channel()` in the header.

Risks and test signals: trace enable/disable races, relay full drops, channel-open failure, and deinit while userspace has debugfs files open are key risks. Tests should cover repeated toggles, reading mode, receiving trace traffic while disabled/enabled, and module/device teardown.
