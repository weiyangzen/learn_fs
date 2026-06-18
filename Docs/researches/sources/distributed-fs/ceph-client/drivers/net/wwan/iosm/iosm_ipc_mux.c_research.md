# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_mux.c

Purpose: manages the IP mux object and session lifecycle over the WWAN IPC channel. It creates the mux channel, opens/closes per-session interfaces, handles channel teardown, allocates mux transmit buffers, and restarts/stops network TX based on flow-control state.

Important functions: `ipc_mux_init`, `ipc_mux_deinit`, `ipc_mux_open_session`, `ipc_mux_close_session`, `ipc_mux_get_max_sessions`, `ipc_mux_get_active_protocol`, `ipc_mux_check_n_restart_tx`, plus internal channel/session scheduling helpers.

Control flow: opening the first session allocates and opens the WWAN channel through imem, suspends TD update timer while sending a blocking open-session ACB command, initializes session padding/flow state, and marks the mux active. Closing a session sends close-session, resets queues, and closes the channel when the last session is gone. Initialization preallocates DMA-backed UL ADB/ADGH SKBs and aggregation QLT tables based on MUX Lite vs aggregation.

State/dependencies: `iosm_mux` tracks sessions, channel ID, protocol, UL flow mode, transaction IDs, round-robin scheduling, ADB state, pending byte counters, and flags. Dependencies include imem channel APIs, mux codec command sending, WWAN flow control, PCIe SKB allocation, and protocol constants. Risks include session ID bounds, allocation unwind for aggregation QLTs, blocking command timeouts, mux state transition errors, and `nr_sessions` consistency. Test signals: open/close state machine, device-specific mux protocol allocation sizes, flow-control restart thresholds, deinit with active channel, and invalid session IDs.
