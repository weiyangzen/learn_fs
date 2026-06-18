## sources/distributed-fs/ceph-client/drivers/net/ethernet/engleder/tsnep_main.c

## Purpose
Implements the main Engleder TSN endpoint Ethernet MAC platform driver. It owns probe/remove, MMIO resource setup, PHY/MDIO attachment, MAC address programming, queue discovery, IRQ/NAPI wiring, TX/RX descriptor rings, page-pool RX, XDP and AF_XDP zero-copy data paths, statistics, multicast filtering, hardware timestamp handoff, and netdev operations.

## Important APIs, Types, and Functions
Key entry points are `tsnep_probe`, `tsnep_remove`, `tsnep_netdev_open`, `tsnep_netdev_close`, `tsnep_netdev_xmit_frame`, `tsnep_netdev_bpf`, `tsnep_netdev_xdp_xmit`, `tsnep_netdev_xsk_wakeup`, `tsnep_enable_xsk`, `tsnep_disable_xsk`, `tsnep_set_irq_coalesce`, and `tsnep_get_irq_coalesce`. TX helpers include ring creation/cleanup, `tsnep_tx_map`, `tsnep_tx_activate`, `tsnep_tx_poll`, and XDP/XSK transmit helpers. RX helpers include page-pool and XSK allocation, `tsnep_rx_poll`, `tsnep_rx_poll_zc`, `tsnep_build_skb`, and XDP action handling. The file uses `struct tsnep_adapter`, `tsnep_queue`, `tsnep_tx`, `tsnep_rx`, and descriptor structs declared in `tsnep.h`/`tsnep_hw.h`.

## Control Flow and State
Probe allocates a multi-queue netdev, maps registers, reads hardware type/revision/queue count, initializes locks/lists, disables interrupts, configures queues, sets a 64-bit DMA mask, initializes MAC/MDIO/PHY/PTP/TC/RXNFC, sets features, and registers the device. Open allocates TX/RX rings per queue, registers NAPI and IRQs, sets real queue counts, enables link IRQ, starts PHY, then enables queues. Close disables link IRQ and PHY, disables queues, frees IRQ/NAPI, and releases rings. TX maps SKB heads/frags or inlines small segments, marks owner counters and last-fragment bits, rings hardware, and reclaims on NAPI. RX maintains page-pool or XSK buffers, checks owner counters, handles timestamp metadata, runs XDP when installed, builds SKBs for `XDP_PASS`, and refills before re-enabling hardware.

Persistent state is mostly in MMIO registers and descriptor rings. Software state includes queue read/write indices, owner counters, NAPI/IRQ names, per-queue packet/byte/drop counters, XSK pool pointers, page buffers used during XSK transitions, PHY state, MAC address cache, and the installed `xdp_prog`.

## Dependencies and Integration Points
Depends on platform devices, OF MAC/PHY/MDIO properties, PHYLIB, DMA mapping/coherent allocation, page_pool, NAPI, AF_XDP, XDP core helpers, BPF reference handling, netdev feature and queue APIs, ethtool hooks from `tsnep_ethtool.c`, PTP hooks from `tsnep_ptp.c`, taprio offload from `tsnep_tc.c`, and RX flow classification from `tsnep_rxnfc.c`.

## Risks and Test Signals
Risks center on descriptor ownership ordering, owner-counter/user-flag wrap, TX cleanup for mixed SKB/XDP/XSK entries, page-pool lifetime during XSK enable/disable, queue disable waiting for software TX drain, XDP frags handling, missing work between NAPI completion and IRQ re-enable, and ABI assumptions around inline timestamp metadata. Test signals include probe/remove, repeated up/down, multi-queue IRQ assignment, PHY link changes, TX/RX traffic with SG and small frames, `ethtool -S`, interrupt coalescing, XDP_PASS/DROP/TX/REDIRECT, `ndo_xdp_xmit`, AF_XDP zero-copy bind/unbind while running, hardware timestamp RX/TX, and fault injection for DMA/page allocation failure.
