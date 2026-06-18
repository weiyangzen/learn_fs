# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/igb_main.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004488`: lines 1-9556, `Docs/researches/chunks/subset-b-004488_research.md`
- `subset-b-004489`: lines 9557-10314, `Docs/researches/chunks/subset-b-004489_research.md`

## Chunk Research

### subset-b-004488: lines 1-9556

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

### subset-b-004489: lines 9557-10314

# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/igb_main.c lines 9557-10314

## Chunk Scope

This chunk covers the tail of the Intel `igb` PCI Ethernet driver's main source file. It begins inside `igb_deliver_wake_packet()` and then defines suspend/resume, runtime PM, shutdown, SR-IOV configuration, PCI AER recovery, VF administrative netdev operations, VMDq/SR-IOV receive-address programming, DMA coalescing setup, I2C byte accessors, queue reinitialization, NFC filter replay helpers, PM operations, and the final `struct pci_driver` registration record.

The immediately preceding context is `__igb_shutdown()`, which tears the device down for suspend/runtime suspend/shutdown: it detaches the netdev, closes a running interface, suspends PTP, clears interrupt resources, programs wake filters, controls PHY power, releases firmware ownership, and disables the PCI function. This chunk supplies the matching resume and registration-side callbacks that make that shutdown path reachable.

## Purpose and Responsibilities

- Deliver a captured wake packet from the controller wake-up packet memory into the network stack after resume.
- Restore a suspended or runtime-suspended NIC to D0, re-enable PCI memory access, rebuild interrupts/queues, reset hardware, reclaim firmware ownership, reopen a running netdev, and reattach the device.
- Provide runtime PM policy: schedule suspend after a link-loss idle interval but return `-EBUSY` so runtime PM only acts when explicitly scheduled.
- Handle final system shutdown and power-off wake state programming.
- Expose PCI SR-IOV sysfs configuration through `igb_enable_sriov()` and `igb_disable_sriov()`.
- Implement PCI error recovery callbacks for AER: detach and stop traffic, request slot reset, reinitialize MMIO state, and resume traffic.
- Back the PF netdev VF controls for setting VF MACs, VF max TX rates, spoof checking, trust state, and reading VF configuration.
- Program receive address registers from the driver's MAC table, including VF queue/pool steering bits and source-address filtering flags.
- Configure VMDq replication, loopback, and anti-spoofing for SR-IOV-capable devices.
- Configure DMA coalescing and related PCIe low-power transition controls on supported MAC generations.
- Provide shared-code I2C byte read/write hooks over the driver's bit-banged I2C adapter with SW/FW synchronization.
- Reinitialize queue and interrupt resources after channel-count changes.
- Remove and restore network flow classification filters around device down/up.
- Bind all of the above into Linux PM, PCI error, shutdown, SR-IOV, and PCI driver registration structures.

## Important APIs, Types, and Functions

- `igb_deliver_wake_packet(struct net_device *netdev)`: reads `E1000_WUPL` and `E1000_WUPM_REG()` memory, builds an aligned `sk_buff`, assigns protocol with `eth_type_trans()`, and submits it with `netif_rx()`.
- `igb_suspend()`, `igb_resume()`, `igb_runtime_suspend()`, `igb_runtime_resume()`, and `igb_runtime_idle()`: PM callbacks assembled into `_DEFINE_DEV_PM_OPS(igb_pm_ops, ...)`.
- `__igb_resume(struct device *dev, bool rpm)`: shared resume implementation for system and runtime PM. The `rpm` flag controls RTNL handling because runtime PM callers are expected to be in a context that does not use the same outer lock path.
- `igb_shutdown(struct pci_dev *pdev)`: final PCI shutdown callback. It calls `__igb_shutdown()` and, on `SYSTEM_POWER_OFF`, arms wake-from-D3 and enters `PCI_D3hot`.
- `igb_pci_sriov_configure(struct pci_dev *dev, int num_vfs)`: PCI core SR-IOV configure hook, compiled around `CONFIG_PCI_IOV`.
- `igb_io_error_detected()`, `igb_io_slot_reset()`, and `igb_io_resume()`: `struct pci_error_handlers` implementation referenced by `igb_err_handler`.
- `igb_rar_set_index(struct igb_adapter *adapter, u32 index)`: synchronizes one software `adapter->mac_table[]` entry into `E1000_RAL()`/`E1000_RAH()` hardware receive address registers.
- `igb_set_vf_mac()` and `igb_ndo_set_vf_mac()`: update VF MAC state in `adapter->vf_data[]`, the software MAC table, and the hardware RAR entry reserved from the top of the RAR table.
- `igb_link_mbps()`, `igb_set_vf_rate_limit()`, `igb_check_vf_rate_limit()`, and `igb_ndo_set_vf_bw()`: translate link speed to Mbps and program per-VF max TX rate limits through `E1000_RTTDQSEL`, `E1000_RTTBCNRM`, and `E1000_RTTBCNRC`.
- `igb_ndo_set_vf_spoofchk()`, `igb_ndo_set_vf_trust()`, and `igb_ndo_get_vf_config()`: netdev SR-IOV administrative callbacks stored in `igb_netdev_ops`.
- `igb_vmm_control(struct igb_adapter *adapter)`: configures VMDq/SR-IOV replication behavior, loopback, and anti-spoofing based on MAC type and VF allocation count.
- `igb_init_dmac(struct igb_adapter *adapter, u32 pba)`: initializes DMA coalescing register thresholds and PCIe low-power decision behavior after reset.
- `igb_read_i2c_byte()` and `igb_write_i2c_byte()`: shared-code hooks that use `adapter->i2c_client` and SMBus byte transfers while holding `E1000_SWFW_PHY0_SM` software/firmware synchronization.
- `igb_reinit_queues(struct igb_adapter *adapter)`: exported within the driver via `igb.h` and used by ethtool channel reconfiguration.
- `igb_nfc_filter_exit()` and `igb_nfc_filter_restore()`: erase and replay NFC filters from `adapter->nfc_filter_list` and `adapter->cls_flower_list`.
- `igb_driver`: the final `struct pci_driver` tying together PCI ID matching, probe/remove, PM ops, shutdown, SR-IOV configure, and PCI error handling.

Key data structures are `struct igb_adapter`, `struct e1000_hw`, `struct vf_data_storage`, `struct igb_mac_addr`, `struct igb_nfc_filter`, `struct ifla_vf_info`, `struct net_device`, and `struct pci_dev`. The relevant persistent fields include `adapter->state`, `adapter->flags`, `adapter->wol`, `adapter->en_mng_pt`, `adapter->io_addr`, `adapter->vfs_allocated_count`, `adapter->vf_data[]`, `adapter->vf_rate_link_speed`, `adapter->link_speed`, `adapter->mac_table[]`, `adapter->i2c_client`, `adapter->nfc_filter_list`, `adapter->cls_flower_list`, and `adapter->nfc_lock`.

## Control Flow and State Machines

### Wake Packet Delivery

After `__igb_resume()` resets hardware and reclaims driver ownership, it reads `E1000_WUS`. If `WAKE_PKT_WUS` is set, it calls `igb_deliver_wake_packet()`. The helper reads the hardware wake packet length from `E1000_WUPL`, rejects zero or larger-than-buffer lengths because WUPM stores only the first `E1000_WUPM_BYTES`, allocates an skb sized to the WUPM buffer, advances the skb length by the real packet length, rounds the MMIO copy length up to a 32-bit boundary, copies from wake packet memory, derives the protocol, and injects the packet through `netif_rx()`. This makes a wake-triggering packet visible to the host networking stack after resume when the device captured a complete packet.

### System and Runtime Resume

`__igb_resume()` is the central resume state machine. It moves the PCI function to `PCI_D0`, restores PCI config state, verifies presence, enables memory BAR decoding, sets bus mastership, disables PCI wake from D3 states, allocates interrupt/queue resources with `igb_init_interrupt_scheme(adapter, true)`, and calls `igb_reset(adapter)`. It then calls `igb_get_hw_control()` so firmware knows the OS driver owns the hardware again.

Wake status is handled before reopening the interface: a wake packet is delivered if present, and then `E1000_WUS` is cleared with all ones. For normal system resume, the function takes RTNL before checking `netif_running()` and calling `__igb_open(netdev, true)`. For runtime resume, it skips this explicit RTNL lock because runtime PM call paths already differ from full system PM locking expectations. If reopen succeeds, `netif_device_attach()` marks the netdev usable again.

Important failure exits are early and leave the device detached or not reopened: missing PCI device returns `-ENODEV`; failed `pci_enable_device_mem()` returns that error; failed interrupt-scheme allocation returns `-ENOMEM`. The interrupt allocation failure path occurs after the PCI device has been enabled, so caller-side PM/error recovery cleanup must account for partial resume.

### Runtime PM and Shutdown

`igb_runtime_idle()` checks link state with `igb_has_link()`. If no link is present, it schedules runtime suspend five seconds later using `pm_schedule_suspend(dev, MSEC_PER_SEC * 5)`, but always returns `-EBUSY`. That pattern keeps the PM core from immediately suspending during idle notification while still allowing the delayed suspend request to run.

`igb_runtime_suspend()` reuses `__igb_shutdown()` with `runtime=true`, which narrows wake filtering to link-change wake (`E1000_WUFC_LNKC`) instead of the full user-configured WoL mask. `igb_suspend()` and `igb_shutdown()` use the non-runtime path. During final power-off, `igb_shutdown()` also calls `pci_wake_from_d3(pdev, wake)` and sets `PCI_D3hot` if the system is powering off.

### PCI Error Recovery

`igb_io_error_detected()` is the first PCI AER callback. A `pci_channel_io_normal` event is treated as a recoverable non-fatal report without device teardown. For frozen or reset-needed channels, the netdev is detached, permanent failure returns `PCI_ERS_RESULT_DISCONNECT`, and otherwise RTNL protects `igb_down(adapter)` for a running interface before the PCI function is disabled and `PCI_ERS_RESULT_NEED_RESET` requests slot reset.

`igb_io_slot_reset()` re-enables memory BAR access, restores PCI state, disables D3 wake, reassigns `hw->hw_addr = adapter->io_addr` because PCI reset may invalidate the hardware address pointer used by register accessors, resets hardware, clears wake status, and reports `PCI_ERS_RESULT_RECOVERED`. If `pci_enable_device_mem()` fails, recovery reports disconnect.

`igb_io_resume()` is the second half of recovery. Under RTNL, it checks whether the netdev is running. If the adapter is not marked `__IGB_DOWN`, recovery is from a non-fatal error and no queue restart is needed. Otherwise it calls `igb_up(adapter)` to configure hardware, enable NAPI/interrupts, start queues, notify VFs of PF reset completion, and reschedule the watchdog. On success it attaches the netdev and calls `igb_get_hw_control()`.

### SR-IOV and VF Administration

`igb_pci_sriov_configure()` handles PCI sysfs VF count changes. With `CONFIG_PCI_IOV`, a request for zero VFs disables SR-IOV with `igb_disable_sriov(dev, true)`, while a positive count tries `igb_enable_sriov(dev, num_vfs, true)` and returns either the requested VF count or the error. Without PCI IOV support it returns zero.

The VF netdev callbacks rely on `adapter->vfs_allocated_count` bounds checks and `adapter->vf_data[]` persistence. `igb_ndo_set_vf_mac()` accepts either a zero MAC to clear `IGB_VF_FLAG_PF_SET_MAC` or a valid unicast MAC to set that flag and log that the VF driver must reload. It also warns when the PF is down. In both accepted cases it calls `igb_set_vf_mac()`, which stores the address in VF state, mirrors it to the RAR entry at `hw->mac.rar_entry_count - (vf + 1)`, associates the entry with the VF queue, marks it in use, and writes the hardware RAR registers.

`igb_ndo_set_vf_bw()` supports max TX rate limiting only on `e1000_82576` and rejects nonzero min rates. It requires the VF index to be valid, link to be up, and `max_tx_rate` to be between zero and the current link speed in Mbps. Successful calls set `adapter->vf_rate_link_speed`, store `vf_data[vf].tx_rate`, and program the hardware rate factor. `igb_check_vf_rate_limit()` is called when link comes up in the watchdog path; if the actual link speed changed from the speed used when limits were set, it clears all VF TX rate state and disables hardware limits.

`igb_ndo_set_vf_spoofchk()` writes MAC/VLAN spoofing bits in `E1000_DTXSWC` for 82576 or `E1000_TXSWC` for other supported devices, then persists `vf_data[vf].spoofchk_enabled`. `igb_ndo_set_vf_trust()` updates only the software trusted flag and logs the change; enforcement is consumed by other VF mailbox paths that check `vf_data[vf].trusted`. `igb_ndo_get_vf_config()` reports MAC, TX rate, PF VLAN/QoS, spoof-check, and trust state through `struct ifla_vf_info`.

### Receive Address Register Programming

`igb_rar_set_index()` converts the six-byte MAC address in `adapter->mac_table[index].addr` into little-endian register values, then conditionally adds hardware-valid, source-address, queue-steering, and pool bits based on the entry state. The RAR pool encoding differs by MAC type: `e1000_82575` and `e1000_i210` use multiplication by `E1000_RAH_POOL_1`, while other devices shift `E1000_RAH_POOL_1` by the queue index. The helper writes `E1000_RAL(index)` and `E1000_RAH(index)` with flushes between writes.

This helper is the low-level bridge between software MAC-table intent and hardware unicast filtering. Other parts of the file call similar MAC-table code for the PF default MAC, unicast list sync, MAC steering filters, and VF reset/configuration.

### VMDq, DMA Coalescing, I2C, and Filters

`igb_vmm_control()` is called during RX multi-queue control setup before `E1000_MRQC` is written. Unsupported or non-replicating MACs return early. For 82576 it marks VLAN tags as added by the MAC in `E1000_DTXCTL`; for 82576 and 82580 it enables replicated VLAN stripping in `E1000_RPLOLR`; i350 falls through to the common VMDq controls. With allocated VFs, it enables PF loopback, replication, and anti-spoofing for the VF count. Without VFs, it disables loopback and replication.

`igb_init_dmac()` is invoked from `igb_reset()` after hardware initialization. On MACs newer than 82580 and when `IGB_FLAG_DMAC` is enabled, it programs DMA coalescing thresholds using the packet buffer allocation (`pba`), `adapter->max_frame_size`, and fixed timing/flush constants. It also configures PCIe low-power transition decisions via `E1000_PCIEMISC_LX_DECISION` for i210-or-newer devices or when DMAC is enabled. For 82580 it explicitly clears LX decision and disables `E1000_DMACR`.

`igb_read_i2c_byte()` and `igb_write_i2c_byte()` are global symbols used by the Intel shared-code hardware operation tables. They require `adapter->i2c_client`, acquire the SW/FW PHY semaphore (`E1000_SWFW_PHY0_SM`) through `hw->mac.ops.acquire_swfw_sync()`, issue SMBus byte read/write operations, release the semaphore, and translate Linux I2C failures to `E1000_ERR_I2C` or semaphore failures to `E1000_ERR_SWFW_SYNC`. The `dev_addr` parameter is present for the shared-code API but not used because the Linux `i2c_client` already encodes the target device address.

`igb_reinit_queues()` closes a running netdev, resets interrupt capability, allocates a new interrupt scheme, and reopens the device if it was running. It is used by ethtool channel configuration after `adapter->rss_queues` changes. `igb_nfc_filter_exit()` erases programmed filters from both the ethtool NFC list and the tc flower list under `adapter->nfc_lock`; `igb_nfc_filter_restore()` replays only `nfc_filter_list` under the same lock during `igb_configure()`. Flower filter replay is not done here, which implies cls_flower rules either have a separate restore path or are intentionally removed from hardware on down.

## State and Persistence Behavior

- Hardware wake state lives in `E1000_WUS`, `E1000_WUPL`, WUPM memory, `E1000_WUC`, and `E1000_WUFC`; software wake policy comes from `adapter->wol`, runtime mode, and `adapter->en_mng_pt`.
- Device PM state spans PCI power state/config space, PCI wake flags, driver-owned MMIO register state, interrupt scheme allocations, queue resources, and `netif_device_detach()`/`netif_device_attach()` visibility to the network stack.
- `adapter->state` includes `__IGB_DOWN`, which determines whether PCI error resume must call `igb_up()` and whether VF MAC warnings should tell the operator to bring the PF up.
- VF administrative state persists in `adapter->vf_data[]`: MAC address, PF-set-MAC flag, max TX rate, PF VLAN/QoS, spoof-check enable, and trust. Rate limiting also stores the link speed used for the programmed hardware factors in `adapter->vf_rate_link_speed`.
- `adapter->mac_table[]` is the source of truth for receive address register entries. This chunk writes one entry to hardware but does not allocate or free the table; allocation happens during software init and reset paths clear/rebuild hardware from it.
- NFC filter software lists persist across down/up. The hardware side is erased on `igb_down()` and replayed from `nfc_filter_list` during `igb_configure()`.
- I2C state is persisted in `adapter->i2c_adap`, `adapter->i2c_algo`, and `adapter->i2c_client`, initialized at probe for i350-class hardware and removed during driver remove.
- The final `igb_driver` structure is static module state and is registered/unregistered by the file's module init/exit functions earlier in the file.

## Dependencies and Integration Points

- Linux PCI core: `struct pci_driver`, `pci_set_power_state()`, `pci_restore_state()`, `pci_enable_device_mem()`, `pci_set_master()`, `pci_enable_wake()`, `pci_wake_from_d3()`, `pci_disable_device()`, SR-IOV configure callbacks, and AER `struct pci_error_handlers`.
- Linux PM core: `_DEFINE_DEV_PM_OPS`, system suspend/resume, runtime suspend/resume/idle, `pm_schedule_suspend()`, and wakeup capability configured during probe.
- Linux netdev core: `netif_device_detach()/attach()`, `netif_running()`, `__igb_open()`, `igb_close()/igb_open()`, `igb_up()/igb_down()`, `netif_rx()`, `sk_buff` allocation, `eth_type_trans()`, RTNL locking, and `net_device_ops` VF callbacks.
- Intel shared hardware layer: `struct e1000_hw`, `hw->mac.type`, `hw->mac.rar_entry_count`, `hw->mac.ops.acquire_swfw_sync()`, `hw->mac.ops.release_swfw_sync()`, register access macros `rd32()`, `wr32()`, `wrfl()`, and many `E1000_*` register/bit definitions.
- SR-IOV/VMDq support: `igb_enable_sriov()`, `igb_disable_sriov()`, `adapter->vf_data`, VF mailbox/reset paths, VMDq loopback/replication/anti-spoof helpers, and netlink VF administration.
- Ettool and channel configuration: `igb_reinit_queues()` is declared in `igb.h` and called from `igb_ethtool.c` when the combined channel count changes.
- Flow classification: `igb_add_filter()` and `igb_erase_filter()` live in the ethtool/filter support code and are invoked here for down/up hardware synchronization.
- I2C subsystem: `i2c_smbus_read_byte_data()`, `i2c_smbus_write_byte_data()`, and the i350 bit-banged I2C bus initialized earlier in this file.
- PTP and firmware ownership: resume and error recovery call `igb_get_hw_control()`, while the preceding shutdown path calls `igb_ptp_suspend()` and `igb_release_hw_control()`.

## Risks and Edge Cases

- `igb_deliver_wake_packet()` rounds the copy length up to a 32-bit boundary after setting the skb length to the unrounded packet length. This is intentional for MMIO alignment, but it writes up to three bytes beyond `skb->len` inside the allocated WUPM-sized data area. Any future buffer-size change must preserve that headroom.
- Resume error handling after `igb_init_interrupt_scheme()` failure returns without disabling the PCI function or clearing partial allocations in this function. Correctness depends on caller recovery paths and the interrupt scheme helper's own cleanup behavior.
- `__igb_resume()` uses `u32 err` even though it stores negative Linux errno values such as `-ENOMEM`; returning it as `int` works by conversion but is stylistically risky and can obscure signedness bugs.
- Runtime resume skips RTNL while system resume takes it. Any future changes to `__igb_open()` or attach sequencing need to preserve the locking assumptions for both PM paths.
- `igb_ndo_set_vf_mac()` validates only `vf >= adapter->vfs_allocated_count`, not negative `vf`. Netdev callers normally supply validated VF indices, but the local check alone would not reject negative indexes before indexing `adapter->vf_data[vf]`.
- VF rate limiting divides by `tx_rate` only when nonzero and bounds `max_tx_rate` against current link speed. It also depends on `igb_link_mbps()` returning nonzero; unsupported or stale speeds make otherwise valid requests fail.
- Per-VF rate programming is 82576-only. Link speed changes disable all VF TX rates, so tests should expect user-configured max rates to be lost after speed transition.
- `igb_ndo_set_vf_spoofchk()` chooses `E1000_TXSWC` for every non-82576 MAC once VFs exist. The hardware support matrix must match the earlier SR-IOV enable paths so unsupported MACs cannot reach this register programming.
- `igb_ndo_set_vf_trust()` persists a software flag but does not program hardware directly in this chunk. Enforcement depends on mailbox and filter paths respecting the trusted flag consistently.
- `igb_nfc_filter_exit()` erases both ethtool NFC and cls_flower lists, while `igb_nfc_filter_restore()` re-adds only ethtool NFC filters. This asymmetry deserves review with the tc flower offload path to ensure flower filters are not silently absent after down/up.
- PCI AER recovery manually restores `hw->hw_addr` from `adapter->io_addr`; any future MMIO remap or BAR handling change must keep these pointers coherent before `rd32()`/`wr32()` are used.
- `igb_init_dmac()` computes thresholds from `pba`, `IGB_MIN_TXPBSIZE`, `IGB_TX_BUF_4096`, and `adapter->max_frame_size`. Jumbo MTU or unusual PBA settings should be validated so threshold arithmetic does not underflow or program nonsensical coalescing values.
- I2C read/write ignore `dev_addr`; if the shared code ever expects dynamic target addresses, this wrapper would need to select or instantiate the correct `i2c_client`.

## Test Signals and Validation Ideas

- Suspend/resume: put the interface up, suspend/resume the system, and verify PCI D0 restoration, interrupt allocation, `igb_reset()`, queue reopen, carrier recovery, and absence of leaked/doubled interrupts.
- Wake-on-LAN: enable different WoL modes, suspend, wake by magic/multicast/link where supported, and verify `E1000_WUS` clears and captured wake packets are injected only when `E1000_WUPL` is within `E1000_WUPM_BYTES`.
- Runtime PM: drop link, confirm delayed runtime suspend is scheduled, then restore link and verify runtime resume reopens/reattaches without RTNL warnings or deadlocks.
- Shutdown/poweroff: power off with WoL enabled and disabled and verify D3 wake behavior and PHY power state match `wake = wufc || adapter->en_mng_pt`.
- PCI AER: inject normal, frozen, and permanent-failure channel states. Expected signals are detach/down/disable on frozen errors, slot reset re-enabling MMIO and clearing `E1000_WUS`, and `igb_up()` plus `netif_device_attach()` on resume.
- SR-IOV sysfs: create and remove VFs through PCI sysfs with `CONFIG_PCI_IOV`, verify return counts/errors, and exercise the zero-VF disable path.
- VF MACs: set a valid VF MAC, clear it with all zeros, try invalid addresses, test while PF is down, and confirm RAR entries and `IGB_VF_FLAG_PF_SET_MAC` behavior.
- VF rates: on 82576 with link up, set max TX rates of zero, a valid sub-link rate, and values above link speed; then change link speed and confirm rates are disabled and `vf_data[].tx_rate` clears.
- VF spoof/trust/config: toggle spoof checking and trust through `ip link`, then verify register bits, `ifla_vf_info` output, and behavior of VF MAC/VLAN changes.
- VMDq/SR-IOV receive behavior: test 82576, 82580, and i350-class hardware or emulation for VLAN replication, PF loopback, anti-spoofing, and VF receive path after reset.
- DMA coalescing: test supported MACs with DMAC enabled/disabled, i210-or-newer LX decision behavior, 82580 disable path, jumbo MTUs, and power-latency impact.
- I2C: on i350 hardware with an external I2C target, verify byte reads/writes, semaphore failure handling, missing-client failure, and concurrent PHY/shared-code access.
- Queue reinit: change ethtool channel count while the interface is up and down, ensuring queues/interrupts are rebuilt and traffic resumes; fault-inject interrupt allocation failures.
- NFC filters: add ethtool ntuple and tc flower filters, bring the interface down/up or reset it, and verify which filters are erased, restored, or require replay through a separate path.
