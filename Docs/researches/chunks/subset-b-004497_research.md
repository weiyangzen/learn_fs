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
