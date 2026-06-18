# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_main.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004497`: lines 1-9244, `Docs/researches/chunks/subset-b-004497_research.md`
- `subset-b-004498`: lines 9245-12433, `Docs/researches/chunks/subset-b-004498_research.md`

## Chunk Research

### subset-b-004497: lines 1-9244

# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_main.c lines 1-9244

## Chunk Scope

This chunk covers the first 9,244 lines of Intel's `ixgbe_main.c`, the main Linux PCI/netdev driver body for Intel 10GbE adapters in the ixgbe family. The covered span includes module metadata and PCI IDs, adapter removal-safe register access, debug dumping, interrupt/NAPI paths, Rx and Tx descriptor ring configuration and cleanup, RSS/VLAN/MAC filter programming, SR-IOV/VMDq setup, device open/close/suspend/resume flows, statistics, watchdog/service work, E610 firmware event integration, and the beginning of transmit offload/descriptor mapping. Later netdev operation table definitions, probe/remove, XDP setup, traffic-class helpers, and PCI driver registration are outside this chunk, though several functions here are wired into those later structures.

## Purpose

The code is the operational core for bringing an ixgbe adapter up and down and for moving packets between Linux networking objects and hardware descriptor rings. It translates Linux netdev, NAPI, DMA, PCI, VLAN, RSS, DCB, SR-IOV, XDP, PTP, IPsec, FCoE, and firmware/link-management events into ixgbe hardware register programming and persistent adapter state updates.

Within this chunk, the driver primarily:

- Identifies supported PCI devices and board variants through `ixgbe_pci_tbl` and `ixgbe_info_tbl`.
- Provides MMIO/PCI config access wrappers that detect surprise removal and schedule service handling.
- Allocates, configures, cleans, and frees Tx, Rx, and XDP descriptor rings.
- Runs the interrupt and NAPI receive/transmit completion loop.
- Configures receive classification features such as RSS/RETA/MRQC, VLAN filtering/stripping, multicast/unicast RAR/MTA filters, Flow Director, and VMDq/SR-IOV pools.
- Manages adapter lifecycle: `ixgbe_open()`, `ixgbe_up()`, `ixgbe_down()`, `ixgbe_close()`, suspend/resume, and shutdown/WoL.
- Runs a periodic service task for link state, reset requests, SFP media changes, firmware health/events, overtemperature/fan alerts, Tx hang checks, PTP maintenance, VF spoof/MDD checks, and stats refresh.
- Starts Tx descriptor preparation with TSO/checksum/IPsec context descriptors and DMA mapping.

## Important APIs, Types, and State

Key structures visible or heavily used in this chunk:

- `struct ixgbe_adapter`: central driver-private state. It owns `pdev`, `netdev`, `hw`, queue/ring arrays, q_vectors, feature flags, `state` bits, timers/work items, RSS key/table, MAC table, VF info, stats, Flow Director state, DCB/FCoE/IPsec/PTP state, E610 link/firmware state, and XDP/AF_XDP state.
- `struct ixgbe_hw`: hardware abstraction with MAC/PHY operation tables, PCI identity, bus info, MMIO base, flow-control config, link info, flash/NVM/firmware data, ACI lock for E610, and back-pointer to `ixgbe_adapter`.
- `struct ixgbe_ring`: per Tx/Rx/XDP descriptor queue state, including DMA descriptor memory, software buffer arrays, `next_to_use`, `next_to_clean`, `next_to_alloc`, queue/register indices, per-ring stats, NAPI vector pointer, XDP rxq info, AF_XDP pool pointer, and ring state bits.
- `struct ixgbe_q_vector`: interrupt/NAPI aggregation object holding Tx/Rx ring containers, adaptive interrupt throttle values, NAPI instance, CPU/NUMA affinity, and MSI-X vector identity.
- `struct ixgbe_tx_buffer` and `struct ixgbe_rx_buffer`: software ownership records for skbs, xdp frames, DMA addresses, page references, timestamps, and packet accounting around hardware descriptors.
- `struct ixgbe_hw_stats`: persistent accumulated hardware counters, updated by clear-on-read register reads in `ixgbe_update_stats()`.
- `struct ixgbe_mac_addr`: software RAR table mirror with address, pool, and `IN_USE`/`MODIFIED`/`DEFAULT` state.
- `struct ixgbe_aci_event`: E610 firmware event container whose `msg_buf` is allocated per service event and freed by `__cleanup`.

Important state bits and flags:

- Adapter `state` bits include `__IXGBE_DOWN`, `__IXGBE_REMOVING`, `__IXGBE_RESETTING`, `__IXGBE_SERVICE_SCHED`, `__IXGBE_SERVICE_INITED`, `__IXGBE_DISABLED`, `__IXGBE_IN_SFP_INIT`, `__IXGBE_RESET_REQUESTED`, `__IXGBE_TESTING`, and PTP state. They gate work scheduling, open/reset/down races, removal handling, and service-task behavior.
- `adapter->flags` and `flags2` advertise features and pending work such as MSI-X, DCA, DCB, FCoE, SR-IOV, VMDq, Flow Director, link update/config needs, SFP reset/search, firmware async events, temp sensor events, RSC, RX legacy mode, VLAN promisc, media absence, FW rollback/API mismatch, and PHY interrupts.
- Ring state bits drive per-queue behavior: Tx hang armed/check flags, FDIR init done, XPS init done, Rx RSC enabled, Rx 3K buffer mode, Rx build_skb mode, FCoE Rx, and UDP-zero-checksum erratum handling.
- Persistent software mirrors include `active_vlans`, `rss_key`, `rss_indir_tbl`, `mac_table`, VF stats snapshots, `fdir_filter_list`, `vxlan_port`, `geneve_port`, `link_up`, `link_speed`, and link/FW error flags.

Important entry points and helpers in this chunk:

- Register/PCI helpers: `ixgbe_read_reg()`, `ixgbe_check_remove()`, `ixgbe_check_cfg_remove()`, `ixgbe_read_pci_cfg_word()`, `ixgbe_write_pci_cfg_word()`, `ixgbe_get_parent_bus_info()`.
- Interrupt helpers: `ixgbe_set_ivar()`, `ixgbe_irq_rearm_queues()`, `ixgbe_configure_msix()`, `ixgbe_irq_enable()`, `ixgbe_msix_other()`, `ixgbe_msix_clean_rings()`, `ixgbe_intr()`, `ixgbe_request_irq()`, `ixgbe_free_irq()`, `ixgbe_irq_disable()`.
- NAPI/datapath: `ixgbe_poll()`, `ixgbe_clean_tx_irq()`, `ixgbe_clean_rx_irq()`, `ixgbe_alloc_rx_buffers()`, `ixgbe_process_skb_fields()`, `ixgbe_run_xdp()`, `ixgbe_rx_skb()`.
- Hardware configuration: `ixgbe_configure_tx_ring()`, `ixgbe_configure_tx()`, `ixgbe_configure_rx_ring()`, `ixgbe_configure_rx()`, `ixgbe_setup_mrqc()`, `ixgbe_store_key()`, `ixgbe_store_reta()`, `ixgbe_setup_vfreta()`, `ixgbe_configure_virtualization()`, `ixgbe_set_rx_mode()`, `ixgbe_configure()`.
- Lifecycle: `ixgbe_sw_init()`, `ixgbe_setup_tx_resources()`, `ixgbe_setup_rx_resources()`, `ixgbe_open()`, `ixgbe_up_complete()`, `ixgbe_reinit_locked()`, `ixgbe_up()`, `ixgbe_down()`, `ixgbe_close()`, `ixgbe_suspend()`, `ixgbe_resume()`, `ixgbe_shutdown()`.
- Service work: `ixgbe_service_event_schedule()`, `ixgbe_service_timer()`, `ixgbe_service_task()`, `ixgbe_recovery_service_task()`, `ixgbe_reset_subtask()`, `ixgbe_watchdog_subtask()`, `ixgbe_check_hang_subtask()`, `ixgbe_sfp_detection_subtask()`, `ixgbe_sfp_link_config_subtask()`, `ixgbe_check_media_subtask()`, `ixgbe_handle_fw_event()`.
- Tx preparation: `ixgbe_tso()`, `ixgbe_tx_csum()`, `ixgbe_tx_cmd_type()`, `ixgbe_tx_olinfo_status()`, `ixgbe_maybe_stop_tx()`, `ixgbe_tx_map()`, `ixgbe_atr()`.

## Control Flow

### Module and PCI Identity

The file starts by declaring driver strings, module parameters (`max_vfs`, `allow_unsupported_sfp`, `debug`), supported board info entries, and `ixgbe_pci_tbl`. The table maps Intel PCI device IDs for 82598, 82599, X540, X550, X550EM, and E610 variants to board-type metadata. `netif_is_ixgbe()` later uses the address of `ixgbe_netdev_ops` to distinguish native ixgbe netdevs from upper macvlan/L2 forwarding netdevs.

### Safe Register Access and Removal

MMIO reads go through `ixgbe_read_reg()`, which first checks whether `hw->hw_addr` has been cleared by surprise removal. If a register read returns all ones, `ixgbe_check_remove()` retries status-register reads before declaring the adapter removed. Removal clears `hw->hw_addr`, logs an error, and schedules the service task if initialized. PCI config reads follow the same pattern using vendor-ID rereads. This path is central because many later functions call `IXGBE_READ_REG()` and must not fault after hot unplug or PCI error.

For SGMII-managed interfaces, `ixgbe_read_reg()` also waits for `IXGBE_MAC_SGMII_BUSY` to clear before reading, warning if previous register writes remain incomplete. Parent-bus PCIe link info helpers are used for devices where bandwidth should be reported from the upstream switch rather than the endpoint.

### Interrupts and NAPI

Interrupt setup uses either MSI-X or MSI/legacy. `ixgbe_configure_msix()` writes IVAR mappings for Rx, Tx, and miscellaneous causes and configures EITR interrupt moderation. `ixgbe_request_msix_irqs()` requests one IRQ per active q_vector plus one "other" vector. Legacy/MSI mode uses `ixgbe_intr()` on the PCI IRQ and a single q_vector.

`ixgbe_msix_other()` handles non-queue causes: link status change, VF mailbox, E610 firmware events, PHY interrupt, ECC reset requests, Flow Director table-full reinit, SFP insertion/removal, overtemperature, fan failure, and PTP PPS. Queue vectors use `ixgbe_msix_clean_rings()` to schedule NAPI. Legacy `ixgbe_intr()` masks, reads EICR, performs similar non-queue checks, schedules q_vector 0 NAPI, then leaves queue interrupts disabled until polling completes.

`ixgbe_poll()` is the NAPI loop. It optionally refreshes DCA tags, cleans each Tx ring with `ixgbe_clean_tx_irq()` or AF_XDP-specific Tx cleanup, divides the Rx budget across rings, and cleans Rx with `ixgbe_clean_rx_irq()` or zero-copy AF_XDP cleanup. If all work completes, it calls `napi_complete_done()`, updates adaptive ITR when enabled, and rearms the q_vector interrupt.

### Tx Completion and Hang Handling

`ixgbe_clean_tx_irq()` walks completed Tx descriptors from `next_to_clean` until `next_to_watch` is unset, the EOP descriptor lacks DD, or the work limit is exhausted. It frees skbs or XDP frames, unmaps DMA, updates ring and q_vector stats, and wakes the netdev queue through BQL when descriptors are available.

Tx hang detection is deliberately two-stage. `ixgbe_check_hang_subtask()` periodically marks queues for hang checks, and `ixgbe_check_tx_hang()` requires pending descriptors and no completed-packet progress across two checks. Pause/PFC XOFF reception disarms false positives in `ixgbe_update_xoff_received()`. On hang, the PF logs TDH/TDT and queue state, stops the subqueue, and schedules a reset. On E610, MDD handling inspects VF or illegal Tx descriptor state and can disable a repeatedly malicious VF.

### Rx Buffering, XDP, and SKB Construction

Rx buffers are page-based and try to avoid repeated DMA map/unmap work. `ixgbe_alloc_rx_buffers()` allocates mapped pages, writes DMA addresses into descriptors, clears the next descriptor length, updates `next_to_use`/`next_to_alloc`, enforces a write barrier, and rings the hardware tail.

`ixgbe_clean_rx_irq()` processes descriptors with nonzero writeback length. It synchronizes DMA, runs XDP if no skb chain is in progress, handles XDP_TX/XDP_REDIRECT/XDP_DROP, constructs an skb via `napi_build_skb()` or `napi_alloc_skb()` paths, or appends fragments to an existing non-EOP skb. It handles page reuse through page-count biasing and page-offset flipping, validates/pads Ethernet headers, handles RSC append counts, hardware checksum/RSS/VLAN/PTP/IPsec metadata, optional FCoE DDP, and finally submits packets through GRO.

The Rx path is sensitive to memory ordering and ownership transitions: `dma_rmb()` protects descriptor writeback reads, DMA syncs hand buffer contents to CPU, `IXGBE_CB(skb)->dma` tracks delayed unmap for chained frames, and page reuse is rejected for pfmemalloc/remote/unshared cases.

### Hardware Configuration

`ixgbe_configure()` is the main post-reset programming sequence. It configures packet buffers and flow-control thresholds, optionally DCB, virtualization/VMDq before VLAN restoration, Rx mode and VLAN filters, IPsec, Flow Director, DCA, FCoE, Tx rings, Rx rings, and L2 forwarding/macvlan offload.

Tx configuration writes descriptor base/length/head/tail registers, programs TXDCTL thresholds, initializes XPS, resets Tx buffer software state, enables queues, and enables the DMA Tx engine on 82599+ devices. `ixgbe_setup_mtqc()` selects Tx pool/traffic-class layout based on SR-IOV, VMDq mask, DCB traffic classes, and XDP queue counts.

Rx configuration disables receive DMA, programs PSRTYPE/RDRXCTL/RFCTL, RSS/MRQC/RETA, frame size and per-ring buffer mode, descriptor registers, SRRCTL/RSCCTL, RXDCTL, and finally enables receive DMA. XSK pools change RXDCTL/SRRCTL buffer sizing and xdp_rxq memory model registration.

RSS state is stored in `adapter->rss_key` and `adapter->rss_indir_tbl`; setup writes RSSRK, RETA/ERETA, PFVF RSS registers in SR-IOV mode, and MRQC fields for IPv4/IPv6 TCP plus optional UDP hashing.

### Address, VLAN, and Virtualization Filters

VLAN add/kill callbacks maintain `adapter->active_vlans` and program VFTA/VLVF unless VLAN promiscuous mode changes the model. VLAN strip enable/disable differs by 82598 global VLNCTRL versus newer per-queue RXDCTL VME. VLAN promiscuous mode is special under VMDq/SR-IOV: VLAN filtering must remain enabled, the PF pool is added to VLVF entries, and VFTA is temporarily set broadly; disable scrubs VFTA blocks from active VLANs plus VLVF state.

MAC address management keeps a software `mac_table` mirror. `ixgbe_add_mac_filter()` and `ixgbe_del_mac_filter()` mark entries modified and synchronize only changed RAR entries. `ixgbe_set_rx_mode()` combines promiscuous/allmulti/RXALL flags, unicast sync, multicast table programming, VMOLR pool modes, VLAN strip/filter feature state, and fallback to promiscuous if filters cannot fit.

SR-IOV/VMDq setup enables VT_CTL, PF pool receive/transmit, VMOLR defaults, VF queue mode in GCR_EXT/GPIE/MTQC/MRQC, PF MAC pool mapping, spoof checking, VF RSS query enable, and VF stats reset snapshots. Service work later checks spoof packet counters and VF PCI status for master aborts, optionally FLRing or disabling malicious VFs.

### Lifecycle

`ixgbe_sw_init()` initializes adapter fields after PCI identity is known: hardware invariants, queue feature limits, feature flags, jump tables, MAC table, RSS key, AF_XDP bitmap, capability differences by MAC type, semaphores/locks, DCB/IPsec/FCoE state, flow-control defaults, ring sizes/work limits, EEPROM parameters, initial down state, and XDP locking static key.

`ixgbe_open()` refuses opens during tests, allocates all Tx and Rx resources, configures hardware, requests interrupts, sets real queue counts, initializes PTP, completes up, resets UDP tunnel offload notifications, and for E610 refreshes link info and configures link. Error unwinding frees IRQs/resources, powers PHY down if needed, and resets hardware.

`ixgbe_up()` assumes resources already exist, reconfigures hardware after reset, and calls `ixgbe_up_complete()`. Up completion claims hardware control from firmware, configures GPIE/interrupt vectors, enables optics/PHY power, clears `__IXGBE_DOWN`, enables NAPI, configures SFP/non-SFP link, clears and enables interrupts, starts the service timer, clears VF stats, sets PF reset-done, and updates VF Rx/Tx settings.

`ixgbe_down()` is idempotent through `__IXGBE_DOWN`. It stops netdev queues/carrier, disables Rx, waits for XDP RCU drainage if needed, disables IRQs and NAPI, clears reset/link flags, deletes the service timer, marks VFs inactive, disables Tx, resets hardware unless the PCI channel is offline, disables optics, cleans all Tx/Rx rings, and disables E610 link status events.

`ixgbe_close()` stops PTP, calls close/suspend if the device is present, releases Flow Director filters, and releases hardware control. Suspend/shutdown detach the netdev, close if running, clear the interrupt scheme, program WoL registers and PCI wake state, power PHY down if not wake-enabled, release hardware control, and disable the PCI device. Resume reverses this by enabling PCI memory, clearing disabled state, resetting, rebuilding interrupt scheme, reopening if running, and attaching the netdev.

### Service Work and Firmware/Link Events

`ixgbe_service_timer()` fires every 2 seconds normally, or every 100 ms while waiting for link update, then schedules `service_task` through the shared workqueue. `ixgbe_service_event_schedule()` serializes scheduling with `__IXGBE_SERVICE_SCHED`; completion clears the bit after a memory barrier.

`ixgbe_service_task()` first handles removal, then firmware fatal/error conditions. If firmware recovery or API mismatch requires limiting functionality, the task unregisters the netdev. E610-specific service work consumes async ACI events and checks media insertion. It then runs reset, PHY interrupt, SFP detection/link setup, overtemperature, watchdog, Flow Director reinit, Tx hang interrupt strobe, and PTP maintenance.

E610 ACI events are handled by `ixgbe_handle_fw_event()`: link status events update link info and call watchdog link up/down handling, temperature events log and bring the adapter down, firmware log events feed `libie_get_fwlog_data()`, and unknown opcodes warn. E610 link configuration also subscribes to link-status events with a mask and tracks media absence/module power/PHY firmware load errors.

## State and Persistence Behavior

Driver state is persistent in memory for the lifetime of the PCI device, not on disk. Key persistent hardware-facing mirrors are kept in adapter fields and replayed after resets:

- `active_vlans`, `mac_table`, RSS key/indirection table, Flow Director filters, IPsec state, DCB configuration, and VF settings are restored during `ixgbe_configure()`/reset.
- Hardware stats are accumulated in `adapter->stats` because many registers are clear-on-read. VF stats use last-value snapshots and saved reset totals because VF counters do not clear uniformly and are skipped during reset.
- Link state is held in `adapter->link_up`, `adapter->link_speed`, `link_check_timeout`, `lse_mask`, `flags/flags2`, and netdev carrier state.
- Ring queue indices and DMA mappings persist while the interface is open and are reset/freed on down/close.
- Service state is persisted in `adapter->state` bits and pending flags; `__IXGBE_SERVICE_SCHED` prevents duplicate workqueue enqueues.
- Hardware ownership is communicated to firmware via `IXGBE_CTRL_EXT_DRV_LOAD`; up claims it, close/shutdown releases it.

Memory ordering is explicit in high-risk state transitions: barriers protect service scheduling, descriptor write ownership, Tx completion status visibility, queue tail writes, and macvlan ring reassignment before filter installation.

## Dependencies and Integration Points

Kernel subsystems integrated in this chunk:

- PCI: device IDs, config space, PCIe link status, D3/WoL, FLR, suspend/resume/shutdown, completion timeout.
- netdev core: open/stop/start_xmit-related helpers, carrier/queue state, BQL, NAPI/GRO, RX/TX stats, MTU changes, unicast/multicast sync, VLAN offload callbacks, UDP tunnel offload notifications, macvlan upper-device walking.
- DMA/page APIs: coherent descriptor allocation, page DMA mapping/sync/unmapping, page ref biasing, NUMA-aware allocation.
- Interrupt APIs: request/free IRQ, MSI-X entries, affinity hints, synchronize_irq, NAPI scheduling.
- XDP/AF_XDP: `bpf_prog_run_xdp`, XDP_TX, XDP_REDIRECT, xdp_rxq_info, xsk pools, XDP frame return/transmit.
- SR-IOV/VF management: VF pool registers, VF mailbox task, VF stats, spoof/MDD handling, VF link and RSS query settings.
- DCB/PFC/FCoE when configured: DCB credit programming, PFC pause behavior, FCoE DDP and MTU handling.
- PTP/time stamping: RX/TX timestamp paths, PPS event, overflow/hang checks, reset/suspend/start cyclecounter calls.
- IPsec: RX metadata and TX offload descriptor context.
- Firmware/NVM/devlink-adjacent E610 support: ACI events, firmware API mismatch, rollback/recovery checks, FW logs via imported `LIBIE_FWLOG` namespace.
- Hardware-specific ixgbe modules: `ixgbe_common`, `ixgbe_e610`, `ixgbe_dcb_82599`, `ixgbe_mbx`, `ixgbe_phy`, `ixgbe_sriov`, `ixgbe_model`, `ixgbe_txrx_common`, and devlink support.

Functions in this chunk are exposed to or called by later parts of the same source file and sibling modules. Examples include `ixgbe_open()`, `ixgbe_close()`, `ixgbe_change_mtu()`, VLAN callbacks, `ixgbe_set_rx_mode()`, resource setup/free functions, `ixgbe_poll()`, `ixgbe_read_reg()`, `ixgbe_configure_rx_ring()`, `ixgbe_configure_tx_ring()`, `ixgbe_update_stats()`, and XDP tail update helpers outside this chunk.

## Risks and Edge Cases

- Surprise removal safety depends on all register accesses using `IXGBE_READ_REG()`/safe wrappers. Direct reads/writes around removal or PCI error paths can still race with hardware disappearance.
- Descriptor ownership has strict ordering requirements. Missing `dma_rmb()`, `wmb()`, DMA sync, or `next_to_watch` ordering can corrupt packets, leak DMA mappings, or create false Tx hangs.
- Tx hang detection must distinguish real hangs from pause/PFC-induced stalls. The two-check armed bit and XOFF clearing are important; regressions can cause unnecessary resets under congestion.
- Rx page reuse relies on correct page-count bias and offset management. Errors can cause use-after-free, DMA to stale pages, memory leaks, or corruption, especially with jumbo/RSC/XDP/AF_XDP variants.
- E610 adds ACI firmware events and API/rollback/recovery modes into an older driver architecture. Link state can arrive through firmware events as well as legacy EICR paths, and fatal FW states can unregister the netdev.
- SR-IOV/VMDq VLAN promiscuous handling is subtle because PF/VF pools share VLVF/VFTA state. Incorrect clearing can break VF VLAN delivery or leak traffic to the PF.
- VF malicious-driver detection paths can disable VF link after repeated events. False positives are high-impact for tenants; insufficient detection leaves PF resets or PCIe errors unresolved.
- Open/close/reset/suspend paths have many partially-initialized unwind states. Resource allocation failure must free only populated rings, disable IRQs only if requested, and preserve PHY/WoL state.
- `ixgbe_down()` relies on disabling Rx before freeing mapped pages and synchronizing RCU when XDP rings exist. Reordering can leave hardware or XDP users referencing freed buffers.
- Stats collection reads many clear-on-read registers and skips during down/reset. Calling it from unexpected contexts can lose counter deltas or report inconsistent netdev stats.
- Flow Director reinit and ATR sampling share per-ring flags/counters with Tx. Queue counts, VF ring mapping, and tunnel parsing must remain consistent with RSS/VMDq topology.
- Feature interactions are dense: XDP limits MTU, FCoE changes frame size and Tx data length, DCB/PFC changes drop enable and flow control, IPsec adds descriptor context fields, and VLAN offload changes receive metadata.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage under relevant kernel configs: `CONFIG_IXGBE_DCA`, `CONFIG_IXGBE_DCB`, `CONFIG_PCI_IOV`, `IXGBE_FCOE`, XDP/AF_XDP, PTP, IPsec, and E610 support.
- Interface lifecycle tests: repeated `ip link set up/down`, MTU changes while running, suspend/resume, shutdown/WoL programming, PCI error/removal simulation, and reset via Tx timeout or service flag.
- Packet-path tests: TCP/UDP/SCTP checksum offloads, TSO/GSO including encapsulated traffic, VLAN strip/filter add/kill, RSS distribution/reta changes, RSC behavior, XDP_PASS/DROP/TX/REDIRECT, AF_XDP zero-copy rings, and jumbo frame boundaries.
- Interrupt tests: MSI-X and legacy/MSI modes, adaptive ITR updates, queue interrupt rearming, non-queue EICR events, PTP PPS, ECC reset scheduling, and Flow Director full threshold reinit.
- SR-IOV tests: VF enable/disable, VF queue mapping, VF VLAN/MAC filtering, spoof checking, malicious driver detection, VF FLR after master abort, VF stats across PF reset, and PF/VF link-change notifications.
- Link/media tests: SFP insert/remove, unsupported SFP unregister path, non-SFP autoneg setup, E610 ACI link event processing, media absent/present transitions, module power and external PHY firmware load errors.
- Fault-injection tests: DMA mapping failures in Tx/Rx, descriptor allocation failures, IRQ request failures, EEPROM init failure, firmware API mismatch/recovery/rollback modes, overtemperature/fan events, and removed-device all-ones reads.
- Observability checks: `ethtool -S` counters, netdev stats, dmesg messages for link up/down/reset/FW errors, `ethtool -i` firmware version refresh on E610 reset, and BQL queue wake/restart counters.

### subset-b-004498: lines 9245-12433

# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_main.c lines 9245-12433

Chunk ID: `subset-b-004498`

## Scope and Purpose

This chunk is the tail of the Intel `ixgbe` PCI Ethernet driver main file. It covers the driver-facing netdev transmit and control entry points, traffic-class and classifier offload plumbing, XDP setup and XDP TX, per-ring disable/enable helpers, PCI probe/remove, PCI error recovery, and module registration. Earlier chunks define many helper routines and data structures used here; this chunk wires those lower-level routines into Linux networking, PCI, devlink, SR-IOV, DCB, XDP, ethtool/Flow Director, and power/error-management interfaces.

The code is mostly orchestration: it validates Linux subsystem requests, updates `struct ixgbe_adapter` state, programs hardware via `struct ixgbe_hw` operation tables and register macros, and performs ordered teardown on errors and module/device removal.

## Important APIs, Types, and Functions

- `ixgbe_select_queue()` is compiled with FCoE support and implements FCoE/FIP queue selection. It uses subordinate-device traffic class mapping when `sb_dev` is present, otherwise uses the adapter FCoE ring feature offset and indices.
- `ixgbe_xmit_xdp_ring()`, `ixgbe_xdp_ring_update_tail()`, `ixgbe_xdp_ring_update_tail_locked()`, and `ixgbe_xdp_xmit()` implement XDP frame TX into ixgbe TX descriptors, DMA mapping, descriptor ordering, optional ring locking, and tail doorbell updates.
- `ixgbe_xmit_frame_ring()`, `__ixgbe_xmit_frame()`, and `ixgbe_xmit_frame()` are the normal skb TX path exposed as `.ndo_start_xmit`. They handle descriptor budgeting, VLAN metadata, PTP timestamp ownership, DCB priority rewriting, FCoE offload, IPsec TX offload, TSO/checksum offloads, Flow Director ATR, and final DMA descriptor mapping.
- `ixgbe_set_mac()`, `ixgbe_mdio_read()`, `ixgbe_mdio_write()`, `ixgbe_ioctl()`, `ixgbe_add_sanmac_netdev()`, and `ixgbe_del_sanmac_netdev()` provide netdev address, MDIO, MII ioctl, and SAN MAC integration.
- `ixgbe_get_stats64()` and `ixgbe_ndo_get_vf_stats()` export PF ring counters and VF stats. Ring counters are read with `u64_stats_fetch_begin/retry()` under RCU-safe ring pointer access.
- `ixgbe_setup_tc()`, `ixgbe_set_prio_tc_map()`, and `ixgbe_validate_rtr()` manage traffic classes and DCB state. Reconfiguration closes/resets the device, rebuilds interrupt/ring allocation, defragments macvlan pools, and reopens the interface if it was running.
- `ixgbe_setup_tc_cls_u32()` and helpers (`ixgbe_configure_clsu32*`, `ixgbe_delete_clsu32()`, `ixgbe_clsu32_build_input()`, `parse_tc_actions()`) translate `tc u32` classifier offload requests into Flow Director perfect filters and optional jump-table state.
- `ixgbe_setup_tc_block_cb()`, `ixgbe_setup_tc_mqprio()`, and `__ixgbe_setup_tc()` are the netdev TC setup entry points for block classifier and mqprio offload.
- `ixgbe_fix_features()` and `ixgbe_set_features()` reconcile requested netdev features with hardware state, XDP restrictions, RSC/LRO state, Flow Director modes, VLAN filter mode, and L2 forwarding offload.
- `ixgbe_fwd_add()` and `ixgbe_fwd_del()` implement accelerated macvlan/L2 forwarding station support through VMDq pools and subordinate channels.
- `ixgbe_features_check()` strips unsupported per-skb offload features when header lengths exceed context descriptor encoding limits or tunnel TSO cannot safely mangle inner IP ID fields.
- `ixgbe_xdp_setup()` and `ixgbe_xdp()` expose `.ndo_bpf` for XDP program and AF_XDP pool setup.
- `ixgbe_netdev_ops` is the central `struct net_device_ops` table tying this chunk's callbacks to the kernel networking stack.
- `ixgbe_txrx_ring_disable()` and `ixgbe_txrx_ring_enable()` quiesce and restart one RX/TX/XDP queue group, including IRQ synchronization, NAPI disable/enable, hardware descriptor-control polling, ring cleanup, and stat reset.
- `ixgbe_enumerate_functions()`, `ixgbe_wol_supported()`, `ixgbe_set_fw_version*()`, and `ixgbe_recovery_probe()` support probe-time capability reporting, WoL selection, firmware version strings, and E610 firmware recovery mode.
- `ixgbe_probe()` and `ixgbe_remove()` are the PCI lifecycle core. They allocate devlink/netdev/adapter resources, initialize hardware operation tables, set feature bits, register netdev/devlink, and unwind resources in reverse order on failure/removal.
- `ixgbe_io_error_detected()`, `ixgbe_io_slot_reset()`, and `ixgbe_io_resume()` implement PCI AER error recovery, including SR-IOV VF error detection and FLR for offending VFs when possible.
- `ixgbe_driver`, `ixgbe_init_module()`, and `ixgbe_exit_module()` register and unregister the PCI driver and global driver workqueue/debug/DCA hooks.

## Control Flow

Normal packet TX enters through `ixgbe_netdev_ops.ndo_start_xmit -> ixgbe_xmit_frame() -> __ixgbe_xmit_frame() -> ixgbe_xmit_frame_ring()`. The path pads short packets for hardware payload requirements, rejects disabled rings with `NETDEV_TX_BUSY`, reserves descriptors, sets `first` buffer metadata, chooses VLAN tagging mode, optionally claims PTP TX timestamp state, applies DCB priority handling, runs FCoE/IPsec/TSO/checksum offload setup, optionally programs ATR metadata, and finally calls `ixgbe_tx_map()`. Drop/error paths free the skb and release timestamp ownership if it was acquired.

XDP TX enters through either internal driver paths calling `ixgbe_xmit_xdp_ring()` or external `.ndo_xdp_xmit -> ixgbe_xdp_xmit()`. The ndo path verifies device state, carrier/running status, flags, configured XDP ring, and disabled TX state. It then optionally locks the ring, maps each `xdp_frame` fragment into one descriptor chain, updates `ring->next_to_use`, and flushes the tail when requested. Memory barriers protect descriptor visibility before cleanup/hardware consumption.

Traffic-class setup enters through `.ndo_setup_tc`. For `TC_SETUP_QDISC_MQPRIO`, `ixgbe_setup_tc_mqprio()` delegates to `ixgbe_setup_tc()`. For `TC_SETUP_BLOCK`, `flow_block_cb_setup_simple()` registers `ixgbe_setup_tc_block_cb()`, which accepts only chain 0 offloadable classifier requests and supports `TC_SETUP_CLSU32`. `ixgbe_setup_tc()` is disruptive: it closes or resets the device, clears interrupt allocation, toggles DCB flags and netdev TC maps, revalidates hardware priority mapping, rebuilds interrupts, reassigns macvlan pools, then reopens if needed.

The `tc u32` offload flow is split by command. Hnode add/delete manages `adapter->tables` bitmap. Knode add/replace builds a Flow Director input/mask from the currently valid parse graph, validates link-table use, parses actions as either drop or redirect-to-VF/macvlan, enforces a single global mask for all perfect filters, writes the hardware perfect filter, and records it through the ethtool Flow Director entry list. Delete removes either one hardware filter or, if the deleted handle is a jump link, all child filters and the associated jump table.

Probe is a long staged initialization pipeline: enable PCI memory device, set DMA mask, reserve BARs, allocate devlink-backed adapter and multi-queue netdev, map BAR0, install MAC/EEPROM/PHY ops from `ixgbe_info_tbl`, initialize MDIO hooks and netdev/ethtool ops, run `ixgbe_sw_init()`, handle E610 recovery mode if firmware error is detected, fetch E610 capabilities/flash data, configure feature flags, reset hardware, enable SR-IOV when compiled and requested, initialize netdev feature sets, validate EEPROM/MAC address, set timers/work, initialize rings/interrupts/stats, configure WoL/version/bus reporting, register netdev/devlink, initialize optional DCA/HWMON/debug/MII/FW logging, and return. Each labeled error block unwinds only resources allocated up to that stage.

Remove follows the reverse lifecycle: unregister devlink, destroy regions/fwlog/debug, mark removing, cancel service work, unregister MDIO, remove DCA/HWMON/SAN MAC/SR-IOV/netdev, unregister devlink port, stop IPsec, clear interrupts, release hardware control, free DCB/jump-table/mac/RSS/AF_XDP resources, unmap BARs, release PCI regions, free netdev/devlink, destroy E610 ACI mutex, and disable the PCI device once.

PCI error recovery first tries SR-IOV-specific bad-VF detection by reading root-port AER header logs and decoding requestor ID. If an offending VF is found, it logs the TLP and issues a function-level reset, increments `vferr_refcount`, and reports recovered. Otherwise it detaches the netdev, closes it if running, disables the PCI function, and requests slot reset unless the channel failure is permanent. Slot reset reenables the device and calls `ixgbe_reset()`. Resume reopens and reattaches unless it is merely consuming a deferred VF error reference.

## State and Persistence Behavior

Primary persistent runtime state is in `struct ixgbe_adapter`: feature flags (`flags`, `flags2`), state bits (`__IXGBE_DOWN`, `__IXGBE_DISABLED`, `__IXGBE_SERVICE_INITED`, `__IXGBE_REMOVING`, `__IXGBE_PTP_TX_IN_PROGRESS`), queue/ring arrays, ring feature limits/offsets, DCB config, Flow Director filter mask/list/jump tables, SR-IOV VF info, macvlan forwarding pool bitmap, XDP program pointer, devlink state, WoL setting, firmware/EEPROM version string, and optional subsystem resources.

Hardware-visible state is programmed through MMIO register writes and operation tables: descriptor rings and tails, TXDCTL/RXDCTL enable bits, interrupt masks, VMDq/bridge registers, source address pruning, Flow Director masks/perfect filters, WUS WoL status, DCA control, SR-IOV mailbox/total VFs, and hardware reset/start hooks.

Reference and lifetime state is important. PTP TX timestamping stores a held skb in `adapter->ptp_tx_skb` and marks `__IXGBE_PTP_TX_IN_PROGRESS`; the error path must cancel work, free the skb, and clear the bit. XDP setup atomically swaps `adapter->xdp_prog`, puts the old BPF program after ring update/reset, and uses RCU synchronization when removing XDP so wakeup paths stop seeing stale state. Ring stats use `u64_stats_sync`; ring arrays are read under RCU in `ixgbe_get_stats64()`. Device disable is guarded by `test_and_set_bit(__IXGBE_DISABLED)` so PCI disable happens once across probe errors, remove, and AER.

This chunk also persists user-visible configuration into kernel objects: `netdev->features`, `hw_features`, `vlan_features`, `hw_enc_features`, `mpls_features`, `xdp_features`, `min_mtu/max_mtu`, `dcbnl_ops`, `devlink_port`, `udp_tunnel_nic_info`, bridge mode, subordinate-channel assignments, and SAN MAC address entries.

## Dependencies and Integration Points

The chunk depends on Linux networking core APIs (`net_device_ops`, skb helpers, VLAN helpers, MDIO/MII ioctl, TC setup, `flow_block_cb_setup_simple`, macvlan acceleration, bridge link netlink, rtnl locks, NAPI, RCU, XDP/AF_XDP, u64 stats), PCI APIs (`pci_driver`, BAR reservation, DMA masks, AER handlers, SR-IOV, FLR, wake from D3), devlink APIs, DCB, DCA, HWMON, IPsec/XFRM offload, FCoE, PTP hardware timestamping, and ethtool Flow Director infrastructure.

Internal ixgbe dependencies include hardware operation tables from `ixgbe_info_tbl`, register macros (`IXGBE_READ_REG`, `IXGBE_WRITE_REG`, `IXGBE_TXDCTL`, `IXGBE_RXDCTL`, `IXGBE_VMD_CTL`, etc.), ring helpers (`ixgbe_configure_*_ring`, `ixgbe_clean_*_ring`, `ixgbe_maybe_stop_tx`, `ixgbe_tx_map`), reset/open/close helpers, SR-IOV helpers, devlink helpers, debug/fwlog helpers, Flow Director helpers, XSK pool/wakeup helpers, and hardware model data such as `ixgbe_ipv4_jumps`.

Compile-time gates substantially change behavior: `IXGBE_FCOE`, `CONFIG_IXGBE_IPSEC`, `CONFIG_IXGBE_DCB`, `CONFIG_NET_CLS_ACT`, `CONFIG_PCI_IOV`, `CONFIG_IXGBE_DCA`, and `CONFIG_IXGBE_HWMON` each add or remove callbacks, state transitions, features, or teardown duties.

## Risks and Edge Cases

- TX descriptor accounting must match actual fragmentation. Underestimating descriptors can corrupt ring state; overconservative budgeting can cause unnecessary `NETDEV_TX_BUSY`.
- The XDP DMA error unwind walks backward from the current descriptor index and uses `dma_unmap_page()` even though mapping used `dma_map_single()`. This matches the local code pattern only if the DMA unmap metadata abstraction intentionally tolerates it; it is a point to verify against surrounding ixgbe cleanup helpers.
- `ixgbe_configure_clsu32()` returns `0` after attempting to build a jump link even when no `nexthdr` entry matched and temporary allocations may have been freed inside the loop. The behavior may be intentional "unsupported link ignored" semantics, but it is a fragile area for offload correctness.
- `ixgbe_configure_clsu32()` uses `loc - 1` for child location maps when `uhtid != 0x800`; a `loc` of zero in child tables would underflow the bitmap index unless rejected by tc handle constraints elsewhere.
- Flow Director perfect filters require one global mask while filters exist. Users can see `-EINVAL` for valid-looking tc rules if their masks differ from the first installed rule.
- XDP is mutually exclusive with SR-IOV, DCB, RSC/LRO, and some L2 forwarding paths in this chunk. Feature toggles can force disruptive `ixgbe_setup_tc()` resets.
- L2 forwarding offload allocation has a potential leak path: `ixgbe_fwd_add()` allocates `accel`, sets pool/subordinate state, and if `ixgbe_fwd_ring_up()` fails returns `ERR_PTR(err)` without freeing `accel` or clearing the bit in this local chunk.
- Probe error unwind is order-sensitive. Any new resource added after `register_netdev()` or `devl_lock()` must be released in the right label and lock state; otherwise remove/probe failure paths diverge.
- E610 recovery probe intentionally registers devlink with limited initialization and returns success without full netdev registration. Callers and removal paths must tolerate partially initialized adapters.
- PCI AER VF detection assumes root-port AER log availability and decodes requestor ID fields differently for old devices. If detection succeeds, normal PF detach/reset is skipped and `vferr_refcount` gates resume.
- `ixgbe_disable_rxr_hw()` skips RXDCTL polling on 82598 with link down because hardware may not clear the bit; this is a hardware-specific quiesce exception that tests should cover.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage across the compile-time matrix, especially with and without `CONFIG_PCI_IOV`, `CONFIG_IXGBE_DCB`, `CONFIG_NET_CLS_ACT`, `CONFIG_IXGBE_IPSEC`, `IXGBE_FCOE`, `CONFIG_IXGBE_DCA`, and `CONFIG_IXGBE_HWMON`.
- Netdev TX smoke tests with VLAN hardware tags, software VLAN headers, DCB priority mappings, TSO/checksum offload, SCTP CRC, UDP GSO, IPsec offload, FCoE offload, and PTP TX timestamp requests.
- XDP attach/detach tests that verify rejection under SR-IOV/DCB/RSC, AF_XDP pool setup and wakeup, `.ndo_xdp_xmit` with and without `XDP_XMIT_FLUSH`, invalid flag rejection, and ring disabled/down-device returns.
- TC tests for mqprio traffic classes, `tc u32` add/replace/delete hnode/knode, unsupported non-IPv4 protocols, mismatched masks, drop actions, redirect to VF, redirect to offloaded macvlan, chain rejection, and duplicate child locations.
- Feature-toggle tests via ethtool/netlink for LRO/RSC, RXCSUM, NTUPLE, HW_TC, RXALL, VLAN RX/filtering, and HW_L2FW_DOFFLOAD, watching whether reset or rx-mode update paths are triggered.
- SR-IOV and bridge-mode tests for VEPA/VEB programming, VF stats, VF configuration during probe, and bad-VF AER recovery if hardware or fault injection permits.
- Probe/remove fault injection at allocation, BAR map, `ixgbe_sw_init`, firmware recovery, EEPROM validation, interrupt init, netdev registration, MII bus init, devlink registration, and fwlog init boundaries.
- Suspend/resume and PCI AER tests that confirm `__IXGBE_DISABLED` transitions, netdev detach/attach, close/open pairing, and no double PCI disable.
- Runtime leak checks around macvlan `ndo_dfwd_add_station` failure after `ixgbe_fwd_ring_up()` and around tc jump-table allocation failures.
