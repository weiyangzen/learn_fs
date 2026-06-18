# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_wwan.h

Purpose: declares the public IOSM WWAN adapter interface used by the IMEM layer and device lifecycle code.

Important APIs/types: `ipc_wwan_init()` registers WWAN operations and returns an opaque `struct iosm_wwan`. `ipc_wwan_deinit()` unregisters WWAN operations and frees the object. `ipc_wwan_receive()` is the downlink entry point from IOSM channel handling, taking an SKB, DSS flag, and interface/session ID. `ipc_wwan_tx_flowctrl()` toggles network queue flow control for a session.

Control flow and state: the header intentionally keeps `struct iosm_wwan` opaque. The implementation owns all per-session netdev state and RCU mapping. Callers only initialize/deinitialize, pass received SKBs, and signal modem TX backpressure.

Dependencies and integration points: depends on IOSM IMEM and Linux SKB types through forward declarations from included compilation context. It bridges low-level IOSM IPC data path and Linux WWAN/netdev users.

Risks and test signals: API misuse risks include passing invalid session IDs, calling receive after deinit, or toggling flow control before link creation. Build tests catch prototype drift; runtime tests should pair IMEM channel lifecycle with WWAN link creation and teardown.
