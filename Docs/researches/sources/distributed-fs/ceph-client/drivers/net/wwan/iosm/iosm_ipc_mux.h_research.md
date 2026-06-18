# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_mux.h

Purpose: declares the IOSM IP mux protocol model, command IDs, session state, aggregation data structures, and mux lifecycle APIs.

Important types/APIs: `mux_event`, `mux_state`, `ipc_mux_protocol`, `ipc_mux_ul_flow`, command parameter structs, `mux_session`, `mux_adb`, `mux_acb`, `iosm_mux`, `ipc_mux_config`, and exported APIs `ipc_mux_init/deinit`, `ipc_mux_open_session`, `ipc_mux_close_session`, `ipc_mux_get_max_sessions`, `ipc_mux_get_active_protocol`, and `ipc_mux_check_n_restart_tx`.

Control flow role: upper WWAN open/close calls map to mux session events; imem DL processing sends IP SKBs to mux decode; imem UL processing calls mux encode and completion recycling. The header encodes limits such as 8 sessions, ADB sizes, Lite/aggregation TD counts, and command numbers.

State/dependencies: state is in-memory and per-device; packet data is carried in SKB queues and DMA-backed ADB buffers. Dependencies include protocol/imem/WWAN/PCIe types and mux codec structs. Risks include `__packed` on the large `iosm_mux` object, array sizing for per-session datagram tables, command ABI drift, and flow-control counters going stale. Test signals: struct size/layout build checks, max-session boundary tests, command ID compatibility, and queue/flow-control behavior across MUX Lite and aggregation.
