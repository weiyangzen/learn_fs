# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_wwan.c

Purpose: adapts IOSM IP MUX sessions to Linux WWAN raw network devices. It registers WWAN link operations, opens/closes IOSM WWAN channels per session, transmits SKBs to IMEM, and delivers downlink SKBs to the network stack.

Important APIs/functions: `ipc_wwan_init()` allocates `struct iosm_wwan` and registers `wwan_ops` with default IP MUX session. `ipc_wwan_newlink()` initializes `iosm_netdev_priv`, registers a netdev, and stores it in an RCU session array. `ipc_wwan_link_open()` calls `ipc_imem_sys_wwan_open()` and starts the netdev queue. `ipc_wwan_link_transmit()` calls `ipc_imem_sys_wwan_transmit()` and updates TX stats or drops. `ipc_wwan_receive()` identifies IPv4/IPv6, looks up the session under RCU, updates RX stats, and calls `netif_rx()`. `ipc_wwan_tx_flowctrl()` stops or wakes per-session queues.

Control flow and state: `struct iosm_wwan` owns `sub_netlist[]`, an RCU-indexed table keyed by IP MUX session ID. Per-netdev state records IF ID and IPC channel ID. Netdev deletion clears the RCU slot before queued unregister.

Dependencies and integration points: uses WWAN core, rtnetlink-created links, IOSM IMEM WWAN open/close/transmit APIs, raw-IP netdev conventions (`ARPHRD_NONE`, no header), and Linux netdev stats.

Risks and test signals: session ID bounds, RCU lifetime, TX error handling, queue flow control, and packet protocol sniffing are the main risks. Test with default and additional sessions, open/stop cycles, `-EBUSY` TX backpressure, IPv4/IPv6 RX, and link deletion while RX is active.
