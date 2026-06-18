# sources/distributed-fs/ceph-client/drivers/net/veth.c

## Purpose

`veth.c` implements the Linux virtual Ethernet pair driver. A veth link creates two peer `net_device` instances; packets transmitted on one endpoint are delivered as received packets on the other endpoint, often across network namespaces. The driver is central to containers, namespaces, bridges, routing tests, XDP redirect targets, and virtual datapaths.

The implementation supports ordinary skb forwarding, software stats, ethtool queue/stat reporting, GRO-over-NAPI mode, XDP program execution, XDP_TX and XDP_REDIRECT, ndo_xdp_xmit frame injection, XDP metadata accessors, configurable channel counts, peer link creation/deletion through rtnetlink, and feature negotiation against peer state.

## Important APIs, Types, and Functions

- `struct veth_priv` stores the RCU-protected peer pointer, drop counter, attached XDP program pointer, receive queue array, and requested headroom.
- `struct veth_rq` represents one receive queue with NAPI state, optional XDP program, XDP memory info, stats, notification mask, ptr_ring, xdp_rxq info, and page pool.
- `struct veth_stats` and `struct veth_rq_stats` hold per-queue XDP/drop counters protected by `u64_stats_sync`.
- Ettool support is implemented by `veth_get_drvinfo()`, `veth_get_strings()`, `veth_get_sset_count()`, `veth_get_ethtool_stats()`, `veth_get_channels()`, `veth_set_channels()`, and `veth_get_link_ksettings()`.
- The normal skb transmit path is `veth_xmit()`, with forwarding through `veth_forward_skb()`.
- XDP and NAPI paths include `veth_xdp_xmit()`, `veth_ndo_xdp_xmit()`, `veth_xdp_rcv_one()`, `veth_xdp_rcv_skb()`, `veth_xdp_rcv()`, `veth_poll()`, `veth_xdp_tx()`, and flush helpers.
- NAPI/XDP resource management is handled by `veth_enable_xdp_range()`, `veth_disable_xdp_range()`, `__veth_napi_enable_range()`, `veth_napi_del_range()`, `veth_enable_xdp()`, `veth_disable_xdp()`, `veth_napi_enable()`, and range-safe variants for channel changes.
- Device lifecycle uses `veth_open()`, `veth_close()`, `veth_dev_init()`, `veth_dev_free()`, `veth_setup()`, and `veth_free_queues()`.
- Netdevice ops include `ndo_start_xmit`, stats, multicast no-op, MAC address change, iflink lookup, feature fix/set, RX headroom, BPF/XDP setup, XDP xmit, and peer lookup.
- Rtnetlink integration is provided by `veth_validate()`, `veth_newlink()`, `veth_dellink()`, `veth_get_link_net()`, and `veth_link_ops`.
- XDP metadata ops expose timestamp, RSS hash, and VLAN tag through `veth_xdp_rx_timestamp()`, `veth_xdp_rx_hash()`, and `veth_xdp_rx_vlan_tag()`.

## Control Flow

Module initialization registers `veth_link_ops` as the `veth` rtnetlink link type. Creating a veth link enters `veth_newlink()`. It parses optional `VETH_INFO_PEER` attributes, creates and registers the peer first in the peer net namespace, assigns random MAC addresses when needed, disables GRO by default for established compatibility, registers the requested endpoint second, turns carrier off initially, connects both `veth_priv.peer` pointers with RCU assignment, initializes real RX/TX queue counts, and calculates XDP feature flags for both sides. Deletion through `veth_dellink()` clears peer pointers and queues both devices for unregister.

`veth_setup()` defines Ethernet defaults and veth-specific properties: no TX skb sharing, live address changes, no queue, phony headroom, disabled netpoll, lockless TX, feature flags, VLAN/MPLS/GSO capabilities, per-CPU tstats, destructor, ops tables, and `ETH_MAX_MTU`.

The ordinary TX path starts in `veth_xmit()`. Under RCU it resolves the peer, verifies the skb can expose an Ethernet header, selects the peer receive queue from the skb queue mapping, decides whether to use NAPI based on `rq->napi` and GRO eligibility, timestamps TX, and calls `veth_forward_skb()`. Without NAPI, the peer receives the skb through `__netif_rx()` and the transmitting device records software TX stats. With NAPI/GRO/XDP, the skb is put into the peer queue's `ptr_ring`; `__veth_xdp_flush()` schedules peer NAPI. If the ring is full and the TX queue can be stopped, the Ethernet header is restored and the queue is stopped until the peer NAPI poll releases backpressure. Drops increment `priv->dropped`.

NAPI polling in `veth_poll()` consumes queued skbs or XDP frames from `rq->xdp_ring` through `veth_xdp_rcv()`. SKBs are converted into XDP buffers when an XDP program is attached by `veth_xdp_rcv_skb()`, possibly copying/COWing data with the page pool to create sufficient headroom. XDP frames from ndo_xdp_xmit are processed by `veth_xdp_rcv_one()`. XDP actions are handled as follows: `XDP_PASS` rebuilds an skb or updates the original skb and sends it to GRO/receive; `XDP_TX` batches frames back toward the peer with `veth_xdp_tx()` and `veth_xdp_flush()`; `XDP_REDIRECT` calls `xdp_do_redirect()` and later `xdp_do_flush()`; `XDP_DROP` and `XDP_ABORTED` update drop/exception stats and free the frame/buffer. After poll completion, the code clears notification masking, reschedules if the ring refilled, and wakes a stopped peer TX queue.

`veth_xdp_xmit()` implements peer injection of XDP frames. It requires valid XDP flags, a live peer, and an initialized peer NAPI pointer, selects a receive queue, validates frame length against MTU/header/VLAN allowance, enqueues tagged XDP-frame pointers into the peer `ptr_ring`, optionally flushes, and updates peer transmit-queue XDP counters for ndo-originated calls. Pointer tagging uses `VETH_XDP_FLAG` to distinguish `struct xdp_frame *` from `struct sk_buff *` in the same ring.

Opening a device requires a peer. It enables full XDP resources if an XDP program is attached, or NAPI resources if GRO was requested; if the peer is up, it turns carrier on for both sides. Closing turns carrier off on both sides and removes XDP/NAPI resources as appropriate. Feature changes toggle NAPI for GRO when the device is up and no XDP program is attached. XDP program setup through `veth_xdp_set()` validates peer presence, peer MTU against XDP headroom and fragment support, RX/TX queue compatibility, enables resources when up, adjusts peer GSO and max MTU limits, manages BPF program references, and updates peer features.

Channel changes through `veth_set_channels()` validate nonzero queues and XDP constraints between local RX and peer TX counts. When running, it temporarily drops carrier, enables newly added RX queue resources before applying queue counts, reverts on errors where possible, disables removed queue resources, restores carrier, and refreshes XDP feature flags on both peers.

## State and Persistence Behavior

The driver has no disk persistence. State exists in paired netdevices, their private `veth_priv` structures, RCU peer pointers, per-queue rings/NAPI/page pools/XDP rxq info, BPF program references, feature bits, real queue counts, per-CPU tstats, per-queue u64 stats, atomic drop counters, carrier state, requested headroom, and MTU/max-MTU constraints. Peer relationships can cross network namespaces; `veth_get_link_net()` reports the peer namespace when available.

Resource lifetime is tied to netdev registration and open/XDP/GRO state. Queue arrays are allocated during `ndo_init` and freed by the private destructor. NAPI/page-pool/ptr-ring/XDP rxq resources are enabled only when needed and explicitly torn down on close, XDP removal, GRO disable, channel shrink, or unregister. RCU and `synchronize_net()` protect peer/ring/NAPI pointer changes from in-flight TX, poll, and stats readers.

## Dependencies and Integration Points

`veth.c` depends on the Linux networking core, rtnetlink link operations, network namespaces, SKB helpers, RCU, per-CPU software stats, ethtool, qdisc/queue APIs, XDP/BPF core, page-pool helpers, ptr_ring, GRO/NAPI, VLAN metadata, and optional page-pool stats. It registers as `MODULE_ALIAS_RTNL_LINK("veth")`, so userspace creates devices with netlink tools such as `ip link add type veth`.

The driver integrates heavily with peer feature negotiation. XDP attachment on one side constrains the peer's GSO and max MTU, sets redirect-target features, and requires local RX queue count to cover peer TX queues. GRO enables NAPI and redirect target behavior even without an XDP program.

## Risks and Edge Cases

- Peer pointer access is RCU-protected; missing RCU discipline would cause use-after-free during namespace teardown or peer deletion.
- The shared ptr_ring stores both skb and XDP frame pointers with low-bit tagging. This assumes pointer alignment keeps the tag bit free.
- Backpressure relies on stopping the correct peer TX queue and waking it from NAPI poll; queue mapping and real queue counts must stay consistent.
- XDP setup must reject incompatible MTU, queue, or detached-peer states; otherwise frames may exceed available headroom or arrive on queues without resources.
- Channel changes while running have partial rollback limits; the code warns if RX queue restoration fails after a TX queue update failure.
- SKB-to-XDP conversion can COW/copy through page_pool and may drop packets on memory pressure.
- Feature changes are asymmetric because local XDP affects peer GSO/max MTU and redirect capabilities.
- GRO is disabled by default for compatibility, so tests expecting GRO must explicitly enable it.
- XDP metadata helpers return `-ENODATA` when processing pure XDP frames without backing skbs.

## Test Signals

Useful tests include rtnetlink creation with and without explicit peer attributes, cross-namespace peer placement, deletion from either endpoint, carrier state when one or both peers are up, ordinary skb forwarding and stats, full rings causing TX queue backpressure and wakeup, GRO enable/disable while up, channel resize with and without attached XDP, XDP attach rejection for too-large peer MTU or insufficient RX queues, XDP_PASS/TX/REDIRECT/DROP behavior, ndo_xdp_xmit bulk injection, XDP metadata reads for skb-backed packets, peer ifindex ethtool stat reporting, page-pool stats when configured, and feature/MTU restoration after XDP program removal.
