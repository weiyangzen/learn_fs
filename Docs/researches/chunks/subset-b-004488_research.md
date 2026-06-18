# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/igb_main.c lines 1-9556

## Scope

This chunk covers the first 9,556 lines of the Intel `igb` PCI Ethernet driver main implementation. It starts at module metadata, PCI ID matching, global driver registration, interrupt/vector setup, probe/remove, open/close, Tx/Rx resource management, netdev operations, traffic-control/XDP hooks, VLAN/MAC filtering, watchdog/reset recovery, statistics, PTP interrupt dispatch, SR-IOV PF/VF mailbox handling, NAPI Tx/Rx cleanup, receive buffer refill, MII ioctl helpers, and the beginning of shutdown/wake handling. The file continues after this chunk, starting inside `igb_deliver_wake_packet()`.

## Purpose

`igb_main.c` is the primary Linux network driver body for Intel 82575-family gigabit Ethernet controllers, including 82575, 82576, 82580, i350, i354, i210, and i211 devices. It binds PCI devices to `struct net_device`, wires the `net_device_ops`, allocates DMA descriptor rings, configures hardware registers, services interrupts via NAPI, transmits and receives packets, manages link state, exposes SR-IOV PF control, coordinates PTP timestamping, and integrates optional DCA, HWMON/I2C, XDP, AF_XDP, VLAN, RSS, traffic-control offloads, and power-management flows.

The chunk is not a standalone subsystem: many hardware-specific primitives, descriptor definitions, ethtool support, PTP helpers, n-tuple filter helpers, AF_XDP helpers, and register macros are declared in `igb.h` and sibling Intel `e1000_*` files. This file acts as the central coordinator around those lower-level operations.

## Important APIs, Types, and Entry Points

- Module/PCI entry points: `igb_init_module()`, `igb_exit_module()`, `igb_probe()`, `igb_remove()`, `igb_driver`, `igb_pci_tbl`, and `igb_err_handler`.
- Netdev operations: `igb_netdev_ops` maps `ndo_open`, `ndo_stop`, `ndo_start_xmit`, stats, MTU, MAC address, VLAN, VF controls, feature negotiation, FDB add, TC setup, BPF/XDP setup, XDP transmit, AF_XDP wakeup, and hardware timestamp get/set handlers.
- Lifecycle helpers: `igb_sw_init()`, `igb_init_queue_configuration()`, `igb_init_interrupt_scheme()`, `igb_open()`, `__igb_open()`, `igb_up()`, `igb_close()`, `__igb_close()`, `igb_down()`, `igb_reinit_locked()`, `igb_reset()`, and `igb_reset_task()`.
- Interrupt and NAPI helpers: `igb_set_interrupt_capability()`, `igb_alloc_q_vectors()`, `igb_configure_msix()`, `igb_request_irq()`, `igb_free_irq()`, `igb_irq_enable()`, `igb_irq_disable()`, `igb_intr()`, `igb_intr_msi()`, `igb_msix_other()`, `igb_msix_ring()`, `igb_poll()`, and `igb_ring_irq_enable()`.
- Ring/resource helpers: `igb_setup_tx_resources()`, `igb_setup_rx_resources()`, `igb_configure_tx_ring()`, `igb_configure_rx_ring()`, `igb_clean_tx_ring()`, `igb_clean_rx_ring()`, `igb_free_tx_resources()`, `igb_free_rx_resources()`, and all-queue wrappers.
- Tx path: `igb_xmit_frame()`, `igb_tx_queue_mapping()`, `igb_xmit_frame_ring()`, `igb_tso()`, `igb_tx_csum()`, `igb_tx_ctxtdesc()`, `igb_tx_map()`, `igb_clean_tx_irq()`, and `igb_tx_timeout()`.
- XDP path: `igb_xdp_setup()`, `igb_xdp()`, `igb_xdp_xmit()`, `igb_xdp_xmit_back()`, `igb_xmit_xdp_ring()`, `igb_run_xdp()`, and `igb_finalize_xdp()`.
- Rx path: `igb_clean_rx_irq()`, `igb_alloc_rx_buffers()`, `igb_alloc_mapped_page()`, `igb_get_rx_buffer()`, `igb_put_rx_buffer()`, `igb_reuse_rx_page()`, `igb_can_reuse_rx_page()`, `igb_construct_skb()`, `igb_build_skb()`, `igb_process_skb_fields()`, `igb_rx_checksum()`, `igb_rx_hash()`, `igb_is_non_eop()`, and `igb_cleanup_headers()`.
- Filtering and VLAN helpers: `igb_set_rx_mode()`, `igb_write_mc_addr_list()`, `igb_vlan_mode()`, `igb_vlan_rx_add_vid()`, `igb_vlan_rx_kill_vid()`, `igb_restore_vlan()`, `igb_flush_mac_table()`, `igb_add_mac_filter_flags()`, `igb_del_mac_filter_flags()`, `igb_uc_sync()`, and `igb_uc_unsync()`.
- SR-IOV helpers: `igb_probe_vfs()`, `igb_enable_sriov()`, `igb_disable_sriov()`, `igb_sriov_reinit()`, `igb_vf_configure()`, `igb_msg_task()`, `igb_vf_reset_msg()`, `igb_rcv_msg_from_vf()`, `igb_ping_all_vfs()`, VF VLAN/MAC/promisc/multicast helpers, and VF netdev operations.
- Link/watchdog/statistics/PTP: `igb_watchdog_task()`, `igb_has_link()`, `igb_update_phy_info()`, `igb_update_stats()`, `igb_get_stats64()`, `igb_tsync_interrupt()`, `igb_perout()`, and `igb_extts()`.
- Optional integration: DCA notifier/setup functions under `CONFIG_IGB_DCA`, HWMON/I2C setup under `CONFIG_IGB_HWMON`, and PCI IOV logic under `CONFIG_PCI_IOV`.

The dominant internal types are `struct igb_adapter`, `struct e1000_hw`, `struct igb_ring`, `struct igb_q_vector`, `struct igb_tx_buffer`, `struct igb_rx_buffer`, `struct vf_data_storage`, and `struct igb_mac_addr`. The driver also uses Linux core types such as `struct pci_dev`, `struct net_device`, `struct sk_buff`, `struct napi_struct`, `struct xdp_buff`, `struct xdp_frame`, `struct flow_cls_offload`, `struct tc_cbs_qopt_offload`, and `struct ifreq`.

## Control Flow

### Module Load and PCI Probe

`igb_init_module()` registers the DCA notifier when configured and registers `igb_driver` with the PCI core. Probe begins in `igb_probe()`: it rejects unexpected virtual functions, enables PCI memory access, configures DMA masks, claims BAR memory, allocates a multi-queue Ethernet netdev, maps MMIO BAR 0, installs netdev/ethtool operations, initializes `struct e1000_hw` function tables from `igb_info_tbl`, calls hardware invariant detection, and then initializes driver software state through `igb_sw_init()`.

`igb_sw_init()` establishes descriptor counts, ITR defaults, work limits, frame sizes, locks, SR-IOV defaults, MAC filter table storage, shadow VLAN table storage, queue configuration, interrupt capability, q-vector/ring allocation, and initial IRQ disable. `igb_probe()` then validates NVM, reads or accepts the platform MAC address, sets advertised netdev features, applies WoL policy quirks, resets hardware, initializes I2C/HWMON/PTP where applicable, registers the netdev, and logs bus/queue/interrupt information. Error labels unwind in reverse order: hardware control release, I2C state clearing, PHY reset, flash unmap, table frees, interrupt scheme clearing, SR-IOV disable, MMIO unmap, netdev free, PCI region release, and PCI device disable.

### Open, Up, Down, Close, and Remove

`igb_open()` delegates to `__igb_open(netdev, false)`. Open blocks during self-test, obtains runtime PM, allocates all Tx/Rx descriptors, powers up link, configures hardware before requesting IRQs, requests MSI-X/MSI/legacy interrupts, publishes real queue counts, enables NAPI, enables interrupts, starts netdev queues, and schedules the watchdog task. The setup order is intentional: descriptor rings and Rx handlers are ready before interrupts can fire.

`igb_up()` is the post-reset activation path used by reinitialization. It configures hardware, clears `__IGB_DOWN`, enables NAPI, configures vectors, clears pending timestamp/general interrupt causes, enables IRQs, notifies VFs of PF reset completion, starts Tx queues, schedules watchdog work, and refreshes EEE advertisement.

`igb_down()` is the shared deactivation path. It sets `__IGB_DOWN`, disables Rx and Tx in hardware, removes NFC filters, stops carrier and queues, flushes MMIO writes, disables IRQs, disables NAPI, deletes watchdog/PHY timers, records stats, resets hardware unless the PCI channel is offline, clears VLAN promiscuous state, cleans all rings, and reapplies DCA setup after reset when enabled. `__igb_close()` wraps `igb_down()`, frees IRQs, and frees descriptor resources. `igb_remove()` performs permanent teardown: runtime PM get, HWMON/I2C/PTP stop, timer/work cancellation, DCA removal, hardware control release, SR-IOV disable, netdev unregister, interrupt scheme clear, MMIO/flash unmap, table frees, netdev free, and PCI disable.

### Interrupt and NAPI Flow

The driver prefers MSI-X. `igb_set_interrupt_capability()` calculates queue counts and vector counts, tries `pci_enable_msix_range()`, and falls back to MSI or legacy interrupts if MSI-X cannot be enabled. `igb_alloc_q_vectors()` assigns one Tx and/or one Rx ring per q-vector. MSI-X uses one "other" vector for link, reset, mailbox, DMA out-of-sync, and timestamp events plus one vector per queue q-vector. MSI and legacy use one q-vector and one shared interrupt path.

`igb_msix_other()` reads `E1000_ICR`, schedules reset on device reset assertion, records DMA out-of-sync and checks spoof state, processes VF mailbox events, schedules near-term watchdog on link status change, dispatches PTP timestamp interrupts, and unmasks the "other" vector. `igb_msix_ring()` writes any pending ITR value and schedules NAPI. `igb_intr_msi()` and `igb_intr()` combine the same non-queue cause processing with q-vector NAPI scheduling; legacy interrupts first verify `E1000_ICR_INT_ASSERTED`.

`igb_poll()` optionally refreshes DCA CPU tags, cleans Tx, cleans Rx or AF_XDP zero-copy Rx, and either returns `budget` for more polling or completes NAPI and reenables ring interrupts. Interrupt moderation is dynamically adjusted by `igb_update_itr()`, `igb_update_ring_itr()`, `igb_set_itr()`, and `igb_write_itr()` based on observed packet/byte mix and configured conservative/dynamic ITR settings.

### Transmit Flow

`igb_xmit_frame()` pads packets to the controller's minimum with `skb_put_padto()` and selects a Tx ring from `skb->queue_mapping`. `igb_xmit_frame_ring()` computes descriptor demand for the skb head and frags, stops the subqueue when space is insufficient, records the first `igb_tx_buffer`, handles optional hardware Tx timestamp ownership, records VLAN tag flags, prepares TSO context descriptors through `igb_tso()` or checksum/VLAN/launchtime context through `igb_tx_csum()`, then maps and posts data descriptors through `igb_tx_map()`.

`igb_tx_map()` DMA maps skb head/frags, splits large buffers across descriptors, writes descriptor command/status fields, accounts BQL with `netdev_tx_sent_queue()`, timestamps software state for hang detection, uses `dma_wmb()` before publishing `next_to_watch`, advances `next_to_use`, potentially stops the queue, and writes the hardware tail when needed. DMA mapping failures unwind descriptor mappings and free the skb.

Completion happens in `igb_clean_tx_irq()`. It walks from `next_to_clean` while `next_to_watch` is set and DD status is visible, frees skb/XDP/XSK payloads, unmaps DMA, updates BQL and u64 stats, services AF_XDP transmit if needed, checks for hung hardware when the watchdog set `IGB_RING_FLAG_TX_DETECT_HANG`, and wakes stopped subqueues once enough descriptors are available. `igb_tx_timeout()` increments timeout counters, marks global reset on newer hardware, schedules reset work, and pokes queue interrupt causes.

### Receive Flow

`igb_configure_rx_ring()` programs descriptor base, length, head/tail, SRRCTL buffer mode, VMOLR pool modes, descriptor thresholds, XDP memory model, XSK pool state, and receive queue enable. `igb_alloc_rx_buffers()` refills descriptors with page-backed DMA buffers, syncs them for device access, clears the next descriptor length, uses `dma_wmb()`, and writes the tail.

`igb_clean_rx_irq()` loops until NAPI budget is reached or a descriptor with zero length is found. For each descriptor it performs `dma_rmb()`, syncs the page for CPU, handles inline PTP packet timestamps, prepares an `xdp_buff` when no incomplete skb exists, runs XDP if configured, handles XDP_TX and XDP_REDIRECT finalization, builds or extends skb buffers, returns/reuses pages, tracks non-EOP multi-buffer packets, drops bad frames unless `NETIF_F_RXALL` is enabled, fills skb hash/checksum/timestamp/VLAN/protocol fields, and passes packets to GRO. Allocation failures set `IGB_RING_FLAG_RX_ALLOC_FAILED`; the watchdog later triggers a software interrupt to retry refill.

The Rx memory model favors page reuse. `igb_can_reuse_rx_page()` rejects remote, pfmemalloc, over-shared, or exhausted-offset pages and refreshes page-count bias when needed. `igb_put_rx_buffer()` either queues the page for reuse or unmaps and drains references. `igb_build_skb()` is used when ring flags allow build-skb; `igb_construct_skb()` copies a small header and attaches the remaining page fragment otherwise.

### Filtering, VLAN, RSS, TC, and XDP Setup

`igb_set_rx_mode()` updates promiscuous, all-multicast, multicast table array, unicast RAR filters, VLAN filtering, receive length, VMOLR, UTA, and VF multicast restoration. VLAN state is mirrored in `adapter->active_vlans` plus hardware VFTA/VLVF tables. VLAN promiscuous mode either programs all VFTA bits or, when VMDq/VLAN-priority filtering requires filtering to remain enabled, temporarily adds the PF pool to VLVF entries and later scrubs hardware state from `active_vlans` and management VLAN.

`igb_setup_mrqc()` seeds RSS keys, initializes the indirection table when queue count changes, configures Rx checksum/RSS fields, selects RSS, VMDq, or VMDq+RSS mode, sets the PF default pool under virtualization, and calls `igb_vmm_control()`.

Traffic-control integration includes CBS offload, ETF txtime offload, flower classifier offload, and capability query. CBS/txtime are limited to i210 queues 0 and 1. FQTSS/Qav setup programs queue priority/mode, TQAVCTRL, TX/RX packet buffer split, CBS idleslope/hicredit, and launchtime flags. Flower parsing supports only basic/control/eth/vlan keys, full masks for MAC/EtherType/VLAN priority, and action-to-traffic-class steering through n-tuple filters.

XDP setup validates Rx buffer size against MTU, atomically swaps adapter and ring BPF program pointers, resets the device when XDP is enabled or disabled on a running netdev, and updates XDP redirect feature flags. XDP transmit shares normal Tx rings and netdev queue locks; program transitions are handled defensively by dropping/returning errors if no Tx ring is currently configured.

### SR-IOV PF/VF Control Flow

SR-IOV is available only for supported hardware and only when MSI-X is present. `igb_enable_sriov()` allocates VF data and optional extra VF MAC filter slots, initializes each VF with no MAC, spoof check enabled, and trust disabled, disables DMA coalescing, reinitializes queue/vector layout if requested, and enables PCI SR-IOV. `igb_disable_sriov()` refuses to remove assigned VFs, disables SR-IOV, frees VF state, restores queue reuse, and optionally reinitializes.

Mailbox processing is serialized with `adapter->vfs_lock` in `igb_msg_task()`. Each VF can signal reset, message, or ack. VF reset clears transient flags while preserving PF-admin MAC state, restores VLAN and VMOLR policy, clears multicast hashes, resets Rx mode, writes the VF MAC into RAR, enables VF Tx/Rx, marks CTS, and replies with ACK or NACK plus MAC. Normal VF messages support MAC address or MAC filter changes, promiscuous/multicast mode, LPE size, and VLAN add/remove when not administratively overridden by a PF VLAN. CTS and NACK throttling prevent pre-reset VFs from configuring the PF repeatedly.

VF VLAN filtering uses VFTA/VLVF pool bits with special handling for VLAN 0, PF-owned VLANs, VLAN promiscuous state, and PF visibility of active VLANs. VF MAC filters use RAR entries reserved away from the PF/VF default MAC range and deny untrusted VF changes when the PF administratively set the VF MAC.

## State and Persistence Behavior

The driver has no ordinary on-disk persistence in this chunk. Durable configuration comes from PCI/NVM/firmware state, platform MAC address, module parameters (`debug`, `max_vfs`), kernel netdev state, and hardware registers. Runtime state is kept in memory and MMIO:

- `adapter->state` bit flags coordinate down/reset/test/PTP-tx-in-progress states. `__IGB_DOWN` gates interrupts, watchdog rescheduling, NAPI, and Tx cleanup. `__IGB_RESETTING` serializes reinitialization and MTU changes. `__IGB_PTP_TX_IN_PROGRESS` serializes single outstanding hardware Tx timestamp ownership.
- `adapter->flags` captures capability and mode state such as MSI-X/MSI, queue pairing, DCA, DMAC, EEE, FQTSS, MAS, media reset, VLAN promiscuous mode, and link update delay.
- Ring producer/consumer state persists in `next_to_use`, `next_to_clean`, `next_to_alloc`, descriptor DMA memory, hardware head/tail registers, and per-buffer DMA mappings. Correct ownership transfer is guarded by `dma_wmb()`, `dma_rmb()`, `smp_mb()`, `smp_rmb()`, and `smp_wmb()` at descriptor publication and completion points.
- Netdev-visible counters are maintained in `adapter->stats64` plus per-ring u64 stats protected with `u64_stats_sync`; hardware clear-on-read counters accumulate in `adapter->stats`.
- VLAN state lives in `adapter->active_vlans`, `adapter->shadow_vfta`, `adapter->mng_vlan_id`, VFTA/VLVF hardware tables, and VMOLR/VMVIR per-pool registers.
- MAC filtering state lives in `adapter->mac_table`, hardware RAR registers, netdev unicast/multicast lists, VF MAC filter lists, and per-VF state.
- SR-IOV state lives in `adapter->vf_data`, `adapter->vf_mac_list`, mailbox CTS/NACK timestamps, VF VLAN/MAC/promisc/multicast settings, and PCI SR-IOV configuration.
- Link state is tracked in `adapter->link_speed`, `adapter->link_duplex`, `hw->mac.get_link_status`, watchdog/PHY timers, carrier state, EEE flags, MAS media swap counters, and runtime PM suspend scheduling.
- PTP state is shared with PTP helper code through `ptp_tx_skb`, `ptp_tx_start`, `tstamp_config`, `ptp_clock`, `tmreg_lock`, timecounter state, and periodic output/extts arrays.

Hardware reset clears many registers, so `igb_reset()` and `igb_configure()` deliberately rebuild RAR, VLAN, RSS, Tx/Rx, NFC filters, PTP, management VLAN, EEE, DMAC, and FQTSS/Qav state.

## Dependencies and Integration Points

- Linux PCI core: PCI device IDs, BAR mapping, MSI/MSI-X, SR-IOV configuration, PCI error handlers, runtime PM, DMA masks, config-space access, and shutdown/suspend hooks.
- Linux networking core: `net_device`, netdev ops, NAPI, qdisc/BQL, GRO, feature negotiation, VLAN acceleration, FDB, ethtool, rtnl locking, queue mapping, carrier state, and XDP features.
- Linux DMA/page APIs: coherent descriptor allocation, streaming DMA map/unmap/sync, page fragment reuse, XDP memory models, AF_XDP pools, and memory barriers.
- Intel shared hardware layer: register macros and helpers (`rd32`, `wr32`, `array_rd32`, `array_wr32`, `wrfl`), MAC/PHY/NVM operation tables, reset/init/link/flow-control/EEE/PHY functions, VFTA/RAR helpers, and chip-specific constants.
- Optional `CONFIG_PCI_IOV`: PF-side VF configuration, mailbox processing, VMDq/RSS queue partitioning, and VF netdev controls.
- Optional `CONFIG_IGB_DCA`: DCA notifier, requester registration, CPU tag programming, and relaxed-ordering descriptor control.
- Optional `CONFIG_IGB_HWMON`: i350 thermal sensor sysfs and I2C bit-bang setup.
- PTP subsystem: hardware timestamp ioctl ops, timestamp interrupt dispatch, external timestamp events, periodic output, PPS events, and Tx/Rx timestamp helper work.
- Traffic control: CBS/ETF qdisc offload, flower classifier block callbacks, hardware traffic-class steering, and taprio capability reporting.

## Risks and Edge Cases

- Resource unwind is complex. Probe/open/SR-IOV enable paths allocate PCI regions, netdevs, MMIO, rings, DMA descriptors, XDP RXQ state, VF arrays, MAC tables, I2C adapters, DCA state, PTP state, and IRQs. Ordering mistakes can leak DMA mappings, leave NAPI references alive, or free q-vectors while stats readers still hold RCU-visible references.
- Reset and close races are central risks. Many paths schedule `reset_task` from interrupt, watchdog, Tx timeout, or media autosense. `__IGB_RESETTING`, `__IGB_DOWN`, `rtnl_lock()`, timer deletion, and work cancellation must remain consistent to prevent reinitializing while resources are being freed.
- Descriptor ownership depends on memory ordering. Tx publishes `next_to_watch` only after descriptor writes; Rx reads descriptor length before other writeback fields; queue stop/wake uses memory barriers around ring indexes. Weakening barriers can create data corruption or false hangs.
- Hardware register programming is chip-specific. IVAR/MSIXBM layouts differ for 82575, 82576, and newer chips. FQTSS/Qav, CBS, txtime, VLAN loopback byte-swap, SCTP checksum, EEE, RSS, SR-IOV, and DCA all have hardware-family guards.
- SR-IOV has limited RAR/VLVF resources and security-sensitive trust/spoof/MAC/VLAN logic. Incorrect pool-bit or filter cleanup can let VFs retain VLAN access, lose PF VLAN visibility, or exhaust shared MAC/VLAN hardware filters.
- Tx timestamping supports only one outstanding hardware timestamp in this path. Failure or reset cleanup must release `ptp_tx_skb` and clear `__IGB_PTP_TX_IN_PROGRESS`, or future timestamp requests are skipped.
- XDP and AF_XDP transitions require ring reconfiguration. Program swaps while running trigger close/open; paths defensively handle transient missing Tx rings, but MTU/buffer-size checks are required to avoid invalid XDP frames.
- `igb_update_stats()` returns early when `link_speed == 0`, so down-link stats refresh depends on stats captured during down/reset and hardware counter semantics.
- VLAN promiscuous and `NETIF_F_RXALL` alter filtering and bad-frame behavior. Tests should cover interactions with VFs, active VLANs, management VLAN, and n-tuple/VLAN-priority filters.
- The chunk ends at line 9,556 inside shutdown/wake handling. `__igb_shutdown()` is covered, but `igb_deliver_wake_packet()` and later suspend/resume/error-handler tail behavior continue in the next chunk.

## Test Signals

- Probe/remove smoke: supported PCI IDs bind, invalid VF device binding is rejected, invalid NVM or MAC errors unwind cleanly, and module unload unregisters PCI/DCA state.
- Open/close/reinit: interface up/down, MTU changes, feature toggles, XDP attach/detach, and SR-IOV reinit leave no leaked IRQ/NAPI/DMA resources and preserve queue counts.
- Interrupt modes: MSI-X, MSI fallback, and legacy interrupt paths all deliver Rx/Tx traffic, link events, PTP timestamp interrupts, mailbox events, and reset events.
- Tx datapath: checksum offload, TSO/TSO6/UDP-L4 GSO, VLAN insertion, no-FCS packets, hardware Tx timestamp, XDP_TX, XDP redirect transmit, descriptor exhaustion, BQL accounting, and DMA map failure cleanup.
- Rx datapath: checksum/RSS/VLAN/timestamp fields, GRO delivery, multi-buffer frames, jumbo MTUs, build-skb versus construct-skb modes, page reuse boundaries, allocation-failure recovery through watchdog-triggered software interrupts, XDP_PASS/DROP/ABORTED/TX/REDIRECT, and AF_XDP zero-copy ring paths.
- Filtering: unicast overflow falls back to UPE, multicast allocation failure falls back to MPE, VLAN add/remove restores VFTA/VLVF after reset, promiscuous and RXALL modes preserve expected frame acceptance, and management VLAN is not scrubbed.
- SR-IOV: VF reset handshake, CTS gating, PF-admin MAC/VLAN enforcement, trusted versus untrusted MAC filters, spoof event logging, VF multicast restoration, VF VLAN 0 handling, assigned-VF refusal during disable, and resource-limited RAR/VLVF behavior.
- Link/watchdog: carrier transitions, media autosense swaps, EEE half-duplex disable, SmartSpeed downshift reporting, thermal events, Tx hang detection/reset, LVMMC warnings, runtime PM suspend scheduling, and PTP hang checks.
- Power/shutdown boundary for this chunk: `__igb_shutdown()` detaches the netdev, closes if running, suspends PTP, clears interrupt scheme, programs wake filters, powers link according to wake/management pass-through, releases hardware control, and disables PCI. Wake packet delivery and full resume/error handling require the next chunk.
