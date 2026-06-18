# sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunvnet_common.c

## Purpose
`sunvnet_common.c` is the shared protocol and data-path library for Sun virtual network ports. It negotiates VIO network attributes, manages exported/imported descriptor rings, handles LDC events through NAPI, receives packets from peer domains, maps and transmits SKBs through LDC cookies, handles ACK/STOPPED flow control, reshapes SKBs for hypervisor copy alignment, maintains multicast control messages, manages TX cleanup timers, and exports these common helpers to vnet/vsw-style drivers.

## Important APIs, Types, And Functions
- Exported handshake and control: `sunvnet_send_attr_common()`, `sunvnet_handle_attr_common()`, `sunvnet_handshake_complete_common()`, and `sunvnet_event_common()`.
- RX path: `vnet_rx_one()`, `get_rx_desc()`, `put_rx_desc()`, `vnet_walk_rx_one()`, `vnet_walk_rx()`, `vnet_rx()`, and `sunvnet_poll_common()`.
- TX ACK and trigger path: `vnet_ack()`, `vnet_nack()`, `vnet_send_ack()`, `__vnet_tx_trigger()`, `idx_is_pending()`, and `maybe_tx_wakeup()`.
- TX data path: `sunvnet_start_xmit_common()`, `vnet_skb_shape()`, `vnet_skb_map()`, `vnet_handle_offloads()`, `vnet_clean_tx_ring()`, `vnet_free_skbs()`, and `sunvnet_clean_timer_expire_common()`.
- Offload/checksum helpers: `vnet_fullcsum_ipv4()` and optional `vnet_fullcsum_ipv6()`.
- Netdev helpers: `sunvnet_open_common()`, `sunvnet_close_common()`, `sunvnet_tx_timeout_common()`, `sunvnet_set_rx_mode_common()`, and `sunvnet_set_mac_addr_common()`.
- Port resource helpers: `sunvnet_port_free_tx_bufs_common()`, `vnet_port_reset()`, `vnet_port_alloc_tx_ring()`, `sunvnet_port_is_up_common()`, `sunvnet_port_add_txq_common()`, and `sunvnet_port_rm_txq_common()`.
- Multicast helpers: `__vnet_mc_find()`, `__update_mc_list()`, `__send_mc_list()`, and `handle_mcast()`.

## Control Flow
During VIO handshake, `sunvnet_send_attr_common()` allocates the TX ring and sends supported transfer mode, MAC address, MTU, VIO_TX_DRING option, and LSO capabilities based on protocol version. `handle_attr_info()` validates peer attributes, negotiates MTU and TSO length, ACKs supported settings, or NACKs/reset on mismatch. Handshake completion initializes RX/TX ring sequence numbers.

LDC events are accumulated in `port->rx_event`, interrupts are disabled, and NAPI is scheduled. `vnet_event_napi()` handles RESET first by resetting VIO state, freeing TX rings, restarting handshake, and waking queues; handles UP by updating link state; otherwise it reads VIO messages, validates session IDs, dispatches data INFO to RX walking, data ACK to TX reclaim/wakeup, control multicast replies, or generic VIO control. RX walking imports peer descriptors with `ldc_get_dring_entry()`, copies packet data with `ldc_copy()`, marks descriptors done, and sends ACTIVE or STOPPED ACKs. If NAPI budget is exhausted, it records resume state and defers the STOPPED ACK.

TX chooses a port via a driver-supplied callback, handles GSO/TSO segmentation if needed, enforces remote MTU with ICMP packet-too-big feedback, shapes the SKB for the LDC alignment contract, computes full checksums when required, cleans old TX descriptors, maps the SKB into LDC cookies, fills a VIO net descriptor, optionally writes descriptor extension offload flags, publishes `VIO_DESC_READY` after `dma_wmb()`, sends exactly one start trigger while the peer is stopped, advances `dr->prod`, stops/wakes the netdev queue based on ring space, and starts the cleanup timer.

## State And Persistence
State is per `struct vnet_port` and per `struct vio_dring_state`: TX cookies/SKBs, negotiated remote MTU, TSO flag and max length, NAPI resume index, STOPPED ACK state, queue index, per-port stats, and cleanup timer. `struct vnet` holds the multicast subscription list and queue usage counters. There is no persistent storage; reset clears negotiated MTU/offload state and frees/reallocates TX rings.

## Dependencies And Integration Points
The file depends on Linux netdev, SKB, GSO, checksum, IPv4/IPv6 ICMP, timers, RCU/list state provided by the front-end driver, tracepoints from `trace/events/sunvnet.h`, and SPARC VIO/LDC primitives. It exports GPL symbols consumed by `sunvnet.c` and related virtual switch code. It integrates with VIO protocol versions 1.0 through 1.8, LDC descriptor ring APIs, hypervisor interrupt control via `vio_set_intr()`, and netdev multi-queue flow control.

## Risks And Edge Cases
- Attribute validation has a suspicious expression `!(xfer_mode | VIO_NEW_DRING_MODE)`, which uses bitwise OR where a capability test may have intended bitwise AND; this should be reviewed before protocol changes.
- `sunvnet_tx_timeout_common()` is a stub despite netdevs installing it.
- RX checksum code compares `skb->protocol == ETH_P_IP` in one branch while most checks use `htons(ETH_P_IP)`, making that path worth auditing.
- TX trigger/ACK state (`start_cons`, `stop_rx`, `dr->cons`, `dr->prod`) is subtle and races with queue locking; missed triggers are explicitly handled in `vnet_ack()`.
- LDC mapping and copying require 8-byte alignment and padded lengths; `vnet_skb_shape()` is critical for correctness.
- GSO handling recursively calls `sunvnet_start_xmit_common()` for each segment and must avoid queue/ring accounting regressions.
- Cleanup timer reclaims SKBs independent of ACK frequency; incorrect descriptor state transitions can leak mappings or free too early.

## Test Signals
High-value tests include VIO version negotiation across 1.0/1.3/1.6/1.7/1.8, MTU and TSO negotiation boundaries, LDC send `-EAGAIN` retry behavior, RX NAPI budget exhaustion/resume, STOPPED ACK flow control, TX ring full and queue wake paths, reset while TX descriptors are pending, SKB alignment and fragmented SKB mapping, GSO segmentation above `tsolen`, IPv4/IPv6 checksum correction, multicast add/delete propagation, and tracepoint-assisted packet flow verification.
