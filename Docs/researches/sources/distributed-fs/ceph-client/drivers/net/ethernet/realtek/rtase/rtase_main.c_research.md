# sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/rtase/rtase_main.c

## Purpose
This file is the complete PCI and netdev implementation for the Realtek RTASE automotive Ethernet switch endpoint driver. It binds PCI device `10ec:906a`, maps the BAR2 MMIO register space, allocates DMA descriptor rings, exposes a multiqueue Ethernet netdev, drives Tx/Rx through NAPI, handles MSI-X or MSI interrupts, reports software and hardware tally statistics, supports VLAN/checksum/TSO/RXFCS/RXALL features, exposes ethtool link/pause/MAC stats, implements CBS traffic-control offload, and handles reset, shutdown, suspend, and resume.

## Important APIs, Types, And Functions
- PCI/module surface: `rtase_pci_tbl`, `rtase_pci_driver`, `rtase_init_one()`, `rtase_remove_one()`, `rtase_shutdown()`, `rtase_suspend()`, and `rtase_resume()`.
- Netdev surface: `rtase_netdev_ops` wires `rtase_open()`, `rtase_close()`, `rtase_start_xmit()`, `rtase_set_rx_mode()`, `rtase_set_mac_address()`, `rtase_change_mtu()`, `rtase_tx_timeout()`, `rtase_get_stats64()`, `rtase_setup_tc()`, `rtase_fix_features()`, and `rtase_set_features()`.
- Queue/ring lifecycle: `rtase_alloc_desc()`, `rtase_free_desc()`, `rtase_init_ring()`, `rtase_tx_desc_init()`, `rtase_rx_desc_init()`, `rtase_tx_clear()`, `rtase_rx_clear()`, and `rtase_rx_ring_fill()` allocate coherent descriptor memory and page-pool Rx buffers.
- Data path: `rtase_start_xmit()` maps skb linear and fragment data into Tx descriptors; `tx_handler()` retires completed Tx descriptors; `rx_handler()` builds recycled skbs from page-pool buffers, handles checksum/VLAN metadata, and feeds GRO.
- Hardware programming: `rtase_hw_config()`, `rtase_nic_enable()`, `rtase_hw_start()`, `rtase_hw_reset()`, `rtase_desc_addr_fill()`, `rtase_interrupt_mitigation()`, and `rtase_hw_set_features()` program DMA, queue, filter, offload, interrupt, and tally-counter registers.
- Interrupt setup: `rtase_alloc_interrupt()`, `rtase_alloc_msix()`, `rtase_init_int_vector()`, `rtase_init_napi()`, `rtase_interrupt()`, `rtase_q_interrupt()`, and `rtase_poll()` connect hardware vectors to per-vector NAPI ring lists.

## Control Flow
Probe rejects virtual functions, allocates an `alloc_etherdev_mq()` netdev, enables PCI, validates BAR2, requests regions, sets a 64-bit DMA mask, maps MMIO, identifies the MAC version from `RTASE_TX_CONFIG_0`, initializes queue counts and interrupt-vector metadata, clears VLAN filter entries, allocates MSI-X with MSI fallback, registers NAPI and netdev/ethtool ops, enables offload feature flags, reads or randomizes the MAC address, allocates a coherent tally counter block, clears hardware counters, and registers the netdev.

Open allocates coherent Tx/Rx descriptors, creates a DMA-mapped page pool, formats Tx and Rx rings, fills all Rx descriptors, configures hardware in reset/config order, requests one IRQ per MSI-X vector or a shared MSI-style IRQ, enables hardware, enables NAPI, marks carrier on, and wakes the netdev queue. Interrupt handlers mask their vector, acknowledge status, and schedule NAPI. `rtase_poll()` runs every ring attached to the vector, retires Tx completions, receives packets up to budget, then re-enables the vector mask after `napi_complete_done()`.

Transmit chooses the queue from `skb_get_queue_mapping()`, prepares VLAN and checksum/TSO bits, maps fragments first, maps the linear head, writes descriptors with DMA barriers, sets `RTASE_DESC_OWN`, records skb ownership on the final descriptor, advances `cur_idx`, stops the subqueue if low on descriptors, and rings `RTASE_TPPOLL` when needed. Receive waits for hardware ownership to clear, checks error bits, rejects fragmented frames as oversized/unsupported, syncs the page-pool buffer for CPU access, builds an skb, applies checksum and VLAN metadata, hands it to GRO, clears the consumed buffer slot, and refills descriptors back to ASIC ownership.

Close disables NAPI, detaches ring list entries from vectors, stops Tx queues and carrier, resets the NIC, clears Tx/Rx software state and page-pool buffers, frees IRQs, and frees coherent descriptors. Tx timeout dumps descriptor, PCI, MMIO, and tally state, then performs a software reset that quiesces IRQ/NAPI, reinitializes rings, restarts hardware, and restores carrier. Suspend detaches and resets a running interface without freeing all PCI resources; resume restores the MAC address, reinitializes rings and hardware if running, and reattaches the netdev.

## State And Persistence
Driver state lives in `struct rtase_private`, the per-vector `struct rtase_int_vector` array, `struct rtase_ring` arrays, page-pool buffers, coherent descriptor memory, a coherent `struct rtase_counters` tally block, MMIO registers, and PCI MSI/MSI-X state. Ring cursors are `cur_idx` and `dirty_idx`; Tx ownership is tracked through `ring->skbuff[]` and `ring->mis.len[]`; Rx ownership is tracked through `ring->data_buf[]` and `ring->mis.data_phy_addr[]`. No disk persistence exists. Hardware-visible state includes descriptor base registers, interrupt masks/status, MAC address registers, queue mode, DMA burst settings, flow-control bits, packet filters, CBS idleslope registers, tally counter DMA address, and feature offload bits.

## Dependencies And Integration Points
The file depends on Linux PCI, netdevice multiqueue APIs, NAPI, DMA mapping, page pool, ethtool, traffic-control CBS offload, VLAN helpers, checksum/TSO helpers, runtime/system PM, and register/descriptor definitions from `rtase.h`. It integrates with the network stack through netdev ops, ethtool ops, per-CPU `tstats`, NAPI GRO, `netif_queue_set_napi()`, `netif_subqueue_completed_wake()`, `netdev_tx_sent_queue()`, and PM callbacks registered through the PCI driver.

## Risks And Edge Cases
- Several descriptor pointer calculations cast `ring->desc` to typed pointers and then add byte-sized products; because `ring->desc` is not visible here, this relies on the header's pointer type matching the intended arithmetic.
- `rtase_rx_ring_clear()` calls `virt_to_head_page(ring->data_buf[i])` before checking whether `data_buf[i]` is non-NULL, which is sensitive to `virt_to_head_page(NULL)` behavior if cleanup runs on partially filled rings.
- `rtase_open()` enables NAPI after `rtase_hw_start()` and IRQ request; an early interrupt before NAPI is enabled would rely on normal IRQ scheduling assumptions and masking.
- DMA mapping failures in transmit drop the skb and return `NETDEV_TX_OK`, so upper layers will not retry.
- Hardware reset, software reset, close, suspend, and resume share ring/page-pool teardown paths; ordering is critical to avoid DMA into freed pages or NAPI touching removed ring list entries.
- The driver reports carrier on unconditionally after open because the PCI endpoint is treated as always linked to the switch GMAC, which differs from PHY-backed drivers.

## Test Signals
Useful validation signals include successful probe and `register_netdev()`, MSI-X allocation with fallback to MSI, queue count and NAPI mapping sanity, Tx/Rx traffic across all queues, VLAN tag insertion/extraction, RXCSUM/IP checksum/TSO/TSO6 toggles, jumbo MTU disabling TSO through `ndo_fix_features`, CBS qdisc offload writes, ethtool pause get/set and MAC stats, rx-all/rxfcs behavior, Tx timeout reset recovery, suspend/resume with a running interface, remove/unload without DMA or NAPI lifetime warnings, and hardware tally counters matching software packet counts.
