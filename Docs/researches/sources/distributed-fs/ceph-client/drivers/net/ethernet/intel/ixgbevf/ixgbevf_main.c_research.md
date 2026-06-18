# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/ixgbevf_main.c

## Purpose
`ixgbevf_main.c` is the Linux PCI/netdev driver body for Intel 10GbE virtual functions. It binds PCI VF IDs to hardware operation tables, manages net_device lifecycle, configures MSI-X vectors, allocates Tx/Rx/XDP rings, handles NAPI polling, implements transmit and receive datapaths, and coordinates PF/VF mailbox-driven reset, link, VLAN, multicast, MTU, RSS, and feature negotiation.

## Important APIs, Types, and Functions
- Module and PCI integration: `ixgbevf_pci_tbl`, `ixgbevf_driver`, `ixgbevf_init_module()`, `ixgbevf_exit_module()`, `ixgbevf_probe()`, `ixgbevf_remove()`, PM callbacks, and PCI error recovery callbacks.
- Netdev operations: `ixgbevf_open()`, `ixgbevf_close()`, `ixgbevf_xmit_frame()`, `ixgbevf_set_rx_mode()`, `ixgbevf_get_stats()`, `ixgbevf_set_mac()`, `ixgbevf_change_mtu()`, VLAN add/remove, feature checks, and `ndo_bpf` XDP setup.
- Datapath: `ixgbevf_clean_tx_irq()`, `ixgbevf_clean_rx_irq()`, `ixgbevf_poll()`, `ixgbevf_tx_map()`, `ixgbevf_tso()`, `ixgbevf_tx_csum()`, `ixgbevf_xmit_xdp_ring()`, and page-backed Rx buffer helpers.
- Resource management: `ixgbevf_setup_*_resources()`, `ixgbevf_free_*_resources()`, q-vector allocation/free, MSI-X request/free, interrupt enable/disable, and ring configure functions.
- Service path: `ixgbevf_service_timer()`, `ixgbevf_service_task()`, reset, queue-reset, watchdog link update, stats update, and Tx hang detection.

## Control Flow
Probe enables PCI, sets 64-bit DMA, requests BARs, allocates a multi-queue Ethernet device, maps BAR0, installs netdev and ethtool ops, copies MAC and mailbox ops from the board info table, performs software init and VF reset/API negotiation, configures features/MTU bounds, initializes a service timer/work item, allocates MSI-X/q-vector topology, registers the netdev, and initializes optional IPsec offload.

Open allocates Tx and Rx descriptor rings, configures PF-mediated Rx mode/VLAN/IPsec state, configures hardware rings, requests MSI-X IRQs, publishes real queue counts, then calls `ixgbevf_up_complete()` to program IVAR/EITR, set RAR, enable NAPI and interrupts, start Tx queues, snapshot counters, and arm the service timer. Close and suspend reverse this: down the queues, disable interrupts, stop NAPI/timer, reset, clean rings, free IRQs, and release descriptors.

NAPI polling first cleans all Tx rings on a q-vector, then distributes Rx budget over Rx rings. Rx processing refills descriptors in batches, prepares an `xdp_buff`, runs an attached XDP program before SKB construction, handles XDP_TX by posting to a paired XDP Tx ring, builds or constructs SKBs for stack delivery, filters VEPA-reflected multicast/broadcast, applies checksum/hash/VLAN/IPsec metadata, and submits via GRO. Tx maps SKB header and fragments into advanced descriptors, emits context descriptors for TSO/checksum/IPsec/VLAN, handles DMA unwind on map failure, and stops/wakes subqueues based on descriptor pressure.

## State and Persistence Behavior
Persistent driver state is held in `struct ixgbevf_adapter`, `struct ixgbe_hw`, ring arrays, q-vectors, `active_vlans`, RSS key/indirection table, hardware counter baselines, `pf_features`, link state, XDP program pointer, and state bit flags such as `__IXGBEVF_DOWN`, `__IXGBEVF_RESETTING`, `__IXGBEVF_REMOVING`, `__IXGBEVF_SERVICE_SCHED`, and reset request bits. Hardware state persists in VF registers, PF mailbox configuration, descriptor DMA memory, and PF-owned VF policy. Statistics are accumulated across reset by saving base and saved-reset counters. The module has one global workqueue.

## Dependencies and Integration Points
The file depends on Linux PCI, netdev, NAPI, BPF/XDP, DMA mapping, page allocation, VLAN, GRO, xfrm/IPsec conditionals, ethtool hooks, and the `ixgbevf` hardware/mailbox abstractions from local headers. Its core integration boundary is the PF over mailbox operations in `vf.c`/`mbx.c`; most privileged settings are requests to the PF rather than direct VF hardware writes. XDP setup changes queue topology because the hardware requires separate Tx resources for XDP_TX.

## Risks and Edge Cases
- Mailbox failures or PF reset state can leave `adapter_stopped` true and prevent open.
- Queue topology is rebuilt for XDP transitions and DCB changes; failures must not leave stale q-vectors or published queue counts.
- Rx page reuse relies on page reference bias, DMA sync discipline, and page-size-dependent offsets.
- Tx hang detection intentionally requires two checks, but false positives still schedule disruptive resets.
- `ixgbevf_clean_rx_ring()` assumes populated `rx_buffer_info` entries between `next_to_clean` and `next_to_alloc` are valid DMA mappings.
- XDP disallows MTU changes and validates frame size against current ring buffers; missing this would overrun Rx buffers.
- PCI removal is detected via failed MMIO reads and schedules service cleanup; any path touching MMIO after removal must honor `IXGBE_REMOVED`.

## Test Signals
Useful signals include probe/open/close under PF reset and normal PF states, MSI-X allocation failure, mailbox API downgrade, link up/down watchdog, Tx hang reset, MTU and XDP attach/detach transitions, VLAN add/remove restoration, multicast/promisc mode changes, RSS queue count and RETA setup, suspend/resume, PCI error recovery, RX checksum/hash/VLAN metadata, XDP_DROP/PASS/TX behavior, DMA mapping failure injection, and stats continuity across reset.
