# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt.c lines 9570-17513

## Scope

This chunk covers the second half of the Broadcom NetXtreme `bnxt` Ethernet driver implementation. It starts in the firmware backing-store/crash-dump setup area and runs through firmware capability discovery, resource and VNIC setup, interrupt/NAPI management, link and PHY programming, NIC open/close, feature reconfiguration, stats, RX mode, reset and firmware health recovery, traffic-control and RFS integration, queue-management callbacks, PCI probe/remove, suspend/resume, PCI error recovery, and module registration.

The earlier part of `bnxt.c` defines many lower-level helpers used here, including ring allocation/free routines, HWRM request helpers, TX/RX datapath pieces, device event handling, memory allocation helpers, tunnel-port HWRM functions, filter helpers, XDP handlers, and several firmware registration routines. This chunk is where those primitives are assembled into the driver lifecycle exposed to PCI, netdev, ethtool, devlink, TC, RFS, PM, and AER.

## Purpose

The code in this range is the main control plane for the `bnxt` netdevice. It translates kernel lifecycle callbacks and asynchronous firmware events into HWRM commands and local state transitions. The core responsibilities are:

- Query firmware and hardware capabilities, including resource limits, PTP, debug/crash dump support, error recovery, queue profiles, link/PHY/FEC/EEE state, LED support, WoL, and flow-management capabilities.
- Allocate and configure rings, completion rings, stat contexts, VNICs, RSS contexts, TPA/LRO/GRO settings, filters, interrupts, NAPI instances, XPS mappings, and default ring reservations.
- Bring the NIC up and down through `bnxt_open()`, `bnxt_close()`, `__bnxt_open_nic()`, and `__bnxt_close_nic()`.
- Maintain link state and user-requested link settings through HWRM `PORT_PHY_QCFG` and `PORT_PHY_CFG`.
- Periodically collect stats, monitor firmware health, retry failed PHY/filter work, and run slow-path events in `bnxt_sp_task()`.
- Recover from TX timeout, RX ring faults, firmware fatal/non-fatal resets, PCI AER, suspend/resume, and shutdown.
- Register the driver with the PCI core and bind the netdev operations, queue-management operations, stats operations, XDP metadata operations, and PCI error handlers.

## Important APIs, Types, And Functions

Primary state is carried by `struct bnxt *bp`, especially these fields:

- `bp->dev`, `bp->pdev`, `bp->bar0`, `bp->bar1`, `bp->bar2`: netdevice, PCI device, and mapped device windows.
- `bp->fw_cap`, `bp->fw_dbg_cap`, `bp->flags`, `bp->rss_cap`, `bp->phy_flags`, `bp->mac_flags`: capability and mode bitfields discovered from firmware, PCI IDs, chip family, and link probing.
- `bp->hw_resc`: minimum, maximum, and reserved firmware resources for rings, VNICs, RSS contexts, stat contexts, MSIX/NQ resources, and flow records.
- `bp->link_info`, `bp->eee`, `bp->link_lock`: cached PHY/link settings, requested settings, EEE configuration, and serialized link updates.
- `bp->fw_health`: firmware heartbeat/reset counters, health registers, reset sequence, wait intervals, reliability flags, and recovery counters.
- `bp->state` and `bp->sp_event`: driver state bits and slow-path event bits used to coordinate open/close, reset, stats, link changes, filter retry, and firmware work.
- `bp->bnapi`, `bp->rx_ring`, `bp->tx_ring`, `bp->vnic_info`, `bp->irq_tbl`: runtime datapath resources managed by open/close, queue APIs, IRQ paths, and reset paths.
- `bp->net_stats_prev`, `bp->ring_drv_stats_prev`, port stats memory, and per-ring `bnxt_stats_mem`: accumulated counters preserved across closes and resets.

Firmware capability and initialization functions:

- `bnxt_hwrm_ver_get()` queries HWRM and firmware versions, command timeout limits, chip id/revision, short-command support, Kong mailbox, trusted VF support, advanced CFA flow support, and supported HWRM request lengths.
- `bnxt_hwrm_func_qcaps()` wraps `__bnxt_hwrm_func_qcaps()`, debug qcaps, queue port config, context memory allocation, and resource qcaps. It populates `fw_cap`, `flags`, `hw_resc`, PF/VF FIDs, MAC addresses, VF ranges, WoL/PTP support, and max TSO segments.
- `bnxt_hwrm_func_resc_qcaps()` reads resource min/max limits and PF VF reservation strategy. On P5-plus hardware it maps `max_msix` into NQ resources and treats max ring groups as max RX rings.
- `bnxt_hwrm_queue_qportcfg()` reads traffic-class queue IDs/profiles, filters CNP queues when RoCE is unavailable, and derives `max_tc`, `max_lltc`, `max_q`, `q_ids`, and `tc_to_qidx`.
- `bnxt_fw_init_one_p1()`, `bnxt_fw_init_one_p2()`, `bnxt_fw_init_one_p3()`, and `bnxt_fw_init_one()` are the staged firmware bring-up path used during probe and reset recovery.
- `bnxt_hwrm_error_recovery_qcfg()`, `bnxt_map_fw_health_regs()`, `bnxt_try_map_fw_health_reg()`, and `bnxt_remap_fw_health_regs()` discover and map firmware health registers for later polling and reset.
- `bnxt_alloc_crash_dump_mem()`, `bnxt_hwrm_crash_dump_mem_cfg()`, and `bnxt_free_crash_dump_mem()` allocate host DDR crash-dump backing memory and advertise it to firmware when debug qcaps allow it.

NIC resource and open/close functions:

- `bnxt_init_chip()` allocates stat contexts, rings, ring groups, default VNIC, RSS contexts, RFS VNICs, TPA settings, VF MAC state, default L2 filter, RX mask, coalescing, and Nitro A0 special VNICs.
- `bnxt_shutdown_nic()` and `bnxt_hwrm_resource_free()` unwind VNICs, rings, ring groups, stats contexts, and tunnel ports.
- `bnxt_init_nic()` initializes local ring/VNIC structures and delegates firmware allocation to `bnxt_init_chip()`.
- `bnxt_init_int_mode()`, `bnxt_setup_int_mode()`, `bnxt_change_msix()`, `bnxt_clear_int_mode()`, `bnxt_request_irq()`, and `bnxt_free_irq()` handle MSIX allocation, dynamic MSIX growth/shrink, IRQ names, affinity hints, RFS CPU rmap, TPH Steering Tag setup, and notifier teardown.
- `bnxt_init_napi()`, `bnxt_enable_napi()`, `bnxt_disable_napi()`, and `bnxt_del_napi()` bind NAPI poll functions to completion rings and ensure an RCU grace period before freeing NAPI structures.
- `__bnxt_open_nic()`, `bnxt_open_nic()`, and `bnxt_open()` reserve rings, allocate memory, initialize interrupts and hardware resources, apply link settings, enable interrupts/TX, start timers, restore RSS contexts and filters, and restart VF representors/PTP.
- `__bnxt_close_nic()`, `bnxt_close_nic()`, and `bnxt_close()` stop VF representors, disable TX, wait for slow-path and stats readers, clear RSS contexts, free HWRM resources, save stats, delete NAPI, free IRQs/memory, shut down link when allowed, and send interface-down notification to firmware.

Link, PHY, and module functions:

- `bnxt_update_link()` sends `HWRM_PORT_PHY_QCFG`, copies the full response into `link_info->phy_qcfg_resp`, updates link speed, duplex, pause, autoneg, partner advertisements, EEE, FEC, media, module status, and link-down reason, and reports carrier transitions when requested.
- `bnxt_hwrm_phy_qcaps()` and `bnxt_hwrm_mac_qcaps()` discover PHY/EEE/speed and MAC capabilities, including disabled-link detection for newer firmware.
- `bnxt_hwrm_set_link_common()`, `bnxt_hwrm_set_pause_common()`, `bnxt_hwrm_set_pause()`, `bnxt_hwrm_set_eee()`, and `bnxt_hwrm_set_link_setting()` translate requested autoneg, forced speed, PAM4/speeds2, pause, EEE, and TX LPI settings into `HWRM_PORT_PHY_CFG`.
- `bnxt_update_phy_setting()` compares requested settings against current firmware state and reissues PHY config only when link, pause, or EEE settings need correction.
- `bnxt_hwrm_shutdown_link()` forces link down on last close for single-PF cases where firmware and SR-IOV policy allow it.
- `bnxt_get_port_module_status()` reports unqualified SFP module states such as disabled TX, powerdown, or warning mode.
- `bnxt_hwrm_port_phy_read()` and `bnxt_hwrm_port_phy_write()` implement netdev MII ioctl access via HWRM MDIO read/write, including Clause 45 address decoding.

Feature, filtering, and offload functions:

- `bnxt_fix_features()` enforces driver constraints for NTUPLE/RFS, UDP GSO, LRO/GRO_HW, VLAN RX acceleration, XDP, and VF VLANs.
- `bnxt_set_features()` computes new driver flags, decides whether a full or partial reinit is required, updates TPA state in-place when possible, and clears user filters when NTUPLE is disabled.
- `bnxt_set_rx_mode()` and `bnxt_cfg_rx_mode()` maintain unicast/multicast filter lists and RX mask bits, fall back to all-multicast when multicast filter programming fails, and suppress promiscuous mode for untrusted VFs without a default VLAN.
- `bnxt_rx_flow_steer()`, `bnxt_insert_ntp_filter()`, `bnxt_lookup_ntp_filter_from_idx()`, `bnxt_del_ntp_filter()`, and `bnxt_cfg_ntp_filters()` implement accelerated RFS/ntuple filters using flow dissector keys, L2 filter references, RCU hash tables, bitmap IDs, aging, and deferred HWRM allocation.
- `bnxt_setup_tc()` integrates TC block flower offload and mqprio traffic class setup. `bnxt_setup_mq_tc()` closes and reopens the device as needed to reallocate ring resources for traffic classes.
- `bnxt_udp_tunnel_set_port()` and `bnxt_udp_tunnel_unset_port()` expose VXLAN, Geneve, and P7 VXLAN-GPE tunnel-port offload tables through `udp_tunnel_nic_info`.

Reset, health, and async work functions:

- `bnxt_timer()` is the periodic scheduler for firmware health polling, stats collection, TC flow stats, RFS filter aging/programming, PHY-setting retry, L2 filter retry, and P5 missed-IRQ checks.
- `bnxt_sp_task()` drains `bp->sp_event`: ULP restart, RFS filter work, HWRM forwarded requests, PF unload notice, periodic stats, link change, PHY update retry, module checks, TC flow stats, missed IRQ checks, echo replies, thermal notifications, RX mask retry, reset tasks, RX ring reset, firmware reset notify, and firmware exception handling.
- `bnxt_reset_task()` performs close/open reset for TX timeout or slow-path reset events. `bnxt_rx_ring_reset()` attempts targeted RX ring reset and falls back to global reset on unsupported or failed HWRM reset.
- `bnxt_fw_health_check()`, `bnxt_fw_exception()`, `bnxt_force_fw_reset()`, `bnxt_fw_reset()`, `bnxt_fw_reset_task()`, `bnxt_reset_all()`, and `bnxt_fw_reset_abort()` implement firmware fatal/non-fatal recovery as a state machine covering VF polling, firmware down polling, host/Kong/OP-TEE reset, PCI re-enable, HWRM readiness polling, device reopen, ULP restart, SR-IOV restore, health reporter updates, and abort.
- `bnxt_hwrm_if_change()` notifies firmware when the driver interface goes up/down, recovers from transient firmware errors, handles hot reset done, resource changes, capability changes, context memory freeing, DCB teardown, firmware reinitialization, IRQ mode clearing, and reservation cancellation.

PCI/netdev registration functions:

- `bnxt_init_board()` enables PCI, requests BARs, sets DMA masks, maps BAR0 and BAR4, initializes work items, locks, timers, ring sizes, and tunnel-port IDs.
- `bnxt_init_one()` is the PCI probe routine. It allocates the netdev, initializes firmware and resources in stages, maps the doorbell BAR, sets netdev feature flags, initializes MAC/PHY/rings/interrupts/devlink/TC/aux devices, selects queue management ops, registers the netdev, creates health reporters, and saves PCI state.
- `bnxt_remove_one()` unregisters the netdev, disables SR-IOV and aux devices, cancels work, unregisters devlink, frees filters, HWRM resources, PTP, hwmon, ethtool, DCB, health, PCI mappings, context memory, crash dump memory, RSS tables, stats, and the netdev.
- `bnxt_shutdown()`, `bnxt_suspend()`, and `bnxt_resume()` implement system shutdown and PM sleep transitions with netdev locking, ULP stop/start, driver unregister/register, crash-dump reconfiguration, PTP reinit, WoL state, and optional reopen.
- `bnxt_io_error_detected()`, `bnxt_io_slot_reset()`, and `bnxt_io_resume()` implement PCI error recovery and coordinate firmware reset state, device detach/attach, PCI enable/disable, context memory teardown, HWRM function reset, ring reservation, interrupt reinit, ULP restart, and SR-IOV restore.
- `bnxt_netdev_ops`, `bnxt_stat_ops`, `bnxt_queue_mgmt_ops`, `bnxt_pci_driver`, `bnxt_init()`, and `bnxt_exit()` bind these routines to kernel subsystems.

## Control Flow

Probe begins at `bnxt_init_one()`. It rejects PCI bridges and devices without MSIX, clears stale DMA after kdump, allocates the netdev with enough TX/RX queues for the PCI MSIX table, marks VF devices, and calls `bnxt_init_board()` to enable PCI, request regions, configure DMA, map BARs, and initialize timers/work. Firmware phase 1 then queries HWRM versions and resets the function. Firmware phase 2 queries capabilities, error recovery, driver registration, crash-dump memory, VNIC/LED/ethtool/PTP/DCB/hwmon capabilities, and queue profiles. After the doorbell BAR is mapped, probe sets netdev feature masks, initializes MAC and PHY settings, builds filter tables, ring parameters, aux devices, default ring reservations, coalescing, interrupts, TC/devlink, queue management ops, and finally registers the netdev.

Open begins at `bnxt_open()`. It first recovers from an aborted firmware reset if needed, sends the firmware interface-up notification through `bnxt_hwrm_if_change()`, then calls `__bnxt_open_nic()`. The open path reserves rings, allocates ring/VNIC memory, creates NAPI, requests IRQs, allocates HWRM rings/groups/VNICs/filters, enables NAPI, applies PHY settings, resets tunnel port notifications and XPS mappings, enables interrupts/TX, starts the timer, polls link/module status, restores VF representors, PTP timestamp filters, RSS contexts, and user filters.

Close runs through `bnxt_close()`, which calls `bnxt_close_nic()`, optionally forces link down, and sends interface-down to firmware. `__bnxt_close_nic()` stops VF representors, marks TX rings closing, drops carrier, waits for slow-path/stats readers, clears multi-RSS contexts, frees HWRM resources, exits debug support, disables NAPI, deletes the timer, saves ring stats, frees IRQ/NAPI state, and frees memory. It preserves accumulated stats and enough configuration state to reopen with the same user-facing settings.

Link updates are serialized by `bp->link_lock`. Events enqueue `BNXT_LINK_CHNG_SP_EVENT`, and `bnxt_sp_task()` optionally refreshes speed capabilities, calls `bnxt_update_link()`, and refreshes ethtool link settings after firmware link-config changes. `bnxt_update_link()` is also called during open and module checks. If firmware reports that advertised speeds are no longer supported, it trims the advertisement mask and reissues link settings.

Feature changes enter through `bnxt_set_features()`. The function computes new driver mode flags from netdev features, decides whether TPA can be toggled in-place or the NIC must close/reopen, and performs a full IRQ reinit for NTUPLE changes because those alter VNIC/RSS resources. MTU and MAC address changes also close/reopen when the device is running.

The timer and slow-path workqueue split fast periodic checks from work that may sleep or issue HWRM commands. `bnxt_timer()` only enqueues work when the device is open and interrupts are not administratively disabled. `bnxt_sp_task()` then handles stats HWRM requests, link events, RFS aging, RX mask retry, firmware event replies, and reset requests. Some slow-path handlers temporarily drop `BNXT_STATE_IN_SP_TASK` before taking the netdev instance lock so close can wait safely without deadlock.

Firmware reset has a multi-stage state machine. Health polling or firmware events set fatal/non-fatal condition bits and schedule reset. The reset path stops ULPs, sets `BNXT_STATE_IN_FW_RESET`, closes the NIC, waits for registered VFs when necessary, optionally polls firmware shutdown, triggers a host, Kong, or OP-TEE reset, re-enables PCI, polls HWRM readiness, reopens via `bnxt_open()`, restarts ULPs/SR-IOV/VF representors, reapplies PTP PPS, and updates devlink health state. Abort paths clear reset state, mark abort, close the netdev, and may defer recovery until the next open.

Queue-management callbacks provide live RX queue replacement for the netdev queue API. `bnxt_queue_mem_alloc()` clones and allocates an RX ring with a requested page size. `bnxt_queue_stop()` disables VNIC MRU use of the RX ring, frees the HWRM RX/agg rings, disables direct page-pool recycling, stops shared TX if needed, disables NAPI after ring-free completions, and snapshots ring state into the queue memory. `bnxt_queue_start()` copies the clone into the active ring, reallocates HWRM rings, arms doorbells/NQ, re-enables page pools and NAPI, restarts shared TX, and restores VNIC/RSS-context MRUs.

## State And Persistence Behavior

Driver state persists primarily in `bp` across netdev opens. User-visible feature choices, requested link settings, ring counts, coalescing defaults, WoL state, RSS hash configuration, traffic-class counts, and filter lists are kept in memory and reapplied after close/open or firmware reset. Probe and firmware reinitialization rebuild firmware-facing resources from this cached state.

`bp->state` is the central concurrency guard. `BNXT_STATE_OPEN` gates datapath and timer work. `BNXT_STATE_NAPI_DISABLED`, `BNXT_STATE_HALF_OPEN`, `BNXT_STATE_IN_SP_TASK`, `BNXT_STATE_READ_STATS`, `BNXT_STATE_IN_FW_RESET`, `BNXT_STATE_ABORT_ERR`, `BNXT_STATE_FW_RESET_DET`, `BNXT_STATE_L2_FILTER_RETRY`, `BNXT_STATE_FW_FATAL_COND`, `BNXT_STATE_FW_NON_FATAL_COND`, and PCI channel state bits coordinate asynchronous close, stats reads, NAPI state, resets, and retries. Memory barriers around state transitions ensure close sees in-progress stats or slow-path work before freeing shared structures.

Firmware capabilities and resource limits are reloaded after probe, firmware reset, resume, and PCI error recovery. `bnxt_clear_reservations()` resets reservation counters and sometimes ring counts, while `bnxt_cancel_reservations()` refreshes qcaps and clears reservation state. New resource-manager firmware requires explicit reservation state; older firmware paths often derive availability directly from max limits.

Statistics are accumulated to survive hardware counter wrap and device close. `bnxt_accumulate_all_stats()` folds DMA hardware stats into software counters, with a P5-plus workaround that ignores intermittent zero counter reads. Before shutdown with IRQ reinit, `__bnxt_close_nic()` saves netdev and ring driver stats into `net_stats_prev` and `ring_drv_stats_prev`; later `bnxt_get_stats64()` adds current live stats to the saved base or returns the saved base when closed.

Link state is cached in `bp->link_info` and `bp->eee`. `bnxt_update_link()` rewrites most live fields from firmware. Requested settings such as autoneg, advertised speeds, requested forced speed, requested duplex, requested pause, and EEE settings persist in the cache and are reapplied by `bnxt_update_phy_setting()` or `bnxt_hwrm_set_link_setting()`.

Firmware health state persists in `bp->fw_health`: register locations, mapped offsets, heartbeat/reset counts, wait intervals, primary/master status, reset sequences, and reliability booleans. Register mappings are invalidated when firmware goes down and remapped after interface-up, PCI reset, or health-reg rediscovery.

Hardware state is recreated on open and reset. Rings, VNICs, RSS contexts, L2/ntuple filters, TPA, coalescing, tunnel ports, IRQ affinity hints, TPH entries, page pools, and doorbells are volatile firmware or PCI resources. The driver treats them as disposable and reconstructs them from cached `bp` fields after close/open.

## Dependencies And Integration Points

Internal driver dependencies include helper families defined earlier in `bnxt.c` or companion `bnxt_*` files:

- HWRM request helpers: `hwrm_req_init()`, `hwrm_req_send()`, `hwrm_req_hold()`, `hwrm_req_drop()`, `hwrm_req_timeout()`, `hwrm_req_flags()`, `hwrm_req_dma_slice()`, short request setup, and many generated HWRM request/response structs.
- Ring/resource helpers: `bnxt_alloc_mem()`, `bnxt_free_mem()`, `bnxt_alloc_ring()`, `bnxt_free_ring()`, HWRM ring/stat/VNIC/RSS/context/free helpers, and context memory allocation/free.
- Datapath and XDP helpers: `bnxt_start_xmit`, `bnxt_poll`, `bnxt_poll_p5`, `bnxt_xdp`, `bnxt_xdp_xmit`, RX page-pool and TPA helpers, and TX/RX skb cleanup helpers.
- Filter and TC helpers: L2 filter allocation/free, ntuple HWRM allocation/free, TC flower offload helpers, devlink health helpers, VF representor helpers, SR-IOV helpers, and aux-device/ULP helpers.
- PTP, DCB, hwmon, ethtool, devlink, debug, and firmware reporter subsystems initialized or called from this chunk.

Kernel subsystem integration points:

- `net_device_ops` for open/close, TX, stats, RX mode, MDIO ioctl, MAC/MTU changes, feature negotiation, TX timeout, SR-IOV callbacks, TC setup, RFS steering, XDP, bridge mode, and hardware timestamping.
- `netdev_stat_ops` and `netdev_queue_mgmt_ops` for per-queue stats and live queue replacement/page-size management.
- PCI driver callbacks for probe, remove, shutdown, PM sleep, SR-IOV configuration, and PCI AER.
- Workqueues, timers, NAPI, MSIX, IRQ affinity, RFS CPU rmap, page pool, XDP RXQ info, netdev locks, rtnl locking during shutdown, and RCU for ntuple filter lifetime.
- Firmware/management integration through HWRM commands for resource qcaps, function qcaps/reset/config/registration, interface change, queue qportcfg, PHY qcfg/cfg/MDIO, stats, VNIC/RSS/filter/ring operations, crash dump config, error recovery, FW reset, echo response, LED qcaps, WoL, and tunnel ports.

Hardware dependencies include PCI BAR0/BAR1/BAR4 mappings, MSIX tables and dynamic MSIX allocation, DMA mask support, P5/P7/Nitro chip differences, TPH support, firmware health registers in BAR/config/GRC windows, doorbell BAR sizing, and reset behavior during fatal PCI errors.

## Risks And Edge Cases

- Many paths assume firmware is responsive enough for HWRM. VF paths special-case `-ENODEV` when PF is unavailable, but other errors during open, close, filter programming, or reset can leave deferred retry bits or abort state that only a later open can clear.
- Firmware reset recovery is highly stateful. Incorrect ordering of `BNXT_STATE_IN_FW_RESET`, `fw_reset_state`, netdev locking, PTP seqlock handling, ULP stop/start, and PCI enable/disable can race with stats, close, PTP reads, SR-IOV, or representor operations.
- `bnxt_sp_task()` intentionally releases `BNXT_STATE_IN_SP_TASK` before taking the netdev instance lock in some paths. New slow-path work must follow that pattern when it can block behind close, otherwise close can deadlock waiting for slow-path state to clear.
- Resource reservation math differs across old RM, new RM, P5-plus, Nitro A0, shared rings, XDP rings, traffic classes, RoCE ULP reservations, aggregate RX rings, and dynamic MSIX. Off-by-one or stale reservation state can surface as open failures, broken TC setup, or missing IRQs.
- Link capability changes can silently trim user advertisement masks when firmware reports supported speeds dropped. This protects invalid configs but mutates requested link state.
- `bnxt_hwrm_shutdown_link()` does not always force link down. Multi-PF, SR-IOV, and firmware-managed link-down policy can leave physical link state under firmware or other functions' control.
- RX mode programming can partially succeed. Unicast filter programming failure on VFs may defer retry, multicast filter failure falls back to all-multicast, and promiscuous mode can be cleared for untrusted VFs even when the netdev flag is set.
- Stats reads race with close unless `BNXT_STATE_READ_STATS` and memory barriers are respected. New stats paths must either use the same guard or avoid freed ring/stat memory.
- Queue-management start/stop depends on HWRM ring-free completions being processed by NAPI before NAPI is disabled. Reordering can permit DMA into freed queue memory.
- Firmware health register mappings can be unreliable or invalidated after resets. The code downgrades reliability for GRC mappings on interface-down and remaps later; consumers must check reliability flags.
- RFS/ntuple filters combine RCU hash lookup, bitmap IDs, user-filter lists, and L2 filter references. Failure paths must drop L2 references and avoid freeing filters still reachable by RCU readers.
- TPH affinity notifiers can restart RX queues when IRQ affinity changes. This path assumes the netdev lock and queue-management restart are safe in the current device state.
- PM, shutdown, AER, firmware reset, and normal close share cleanup routines but have different PCI and firmware availability assumptions. HWRM errors in these paths may be expected and should not be handled like normal runtime failures.

## Test Signals

Strong validation signals for this chunk include:

- Probe/remove: load/unload the driver on PF and VF devices, verify BAR mappings, HWRM registration/unregistration, devlink registration, aux device lifecycle, health reporters, and no leaks after `bnxt_remove_one()`.
- Open/close: repeatedly bring the netdev up/down with PF, VF, SR-IOV enabled, XDP attached, RFS enabled, multi-RSS contexts, and TC mqprio settings. Confirm rings, VNICs, IRQs, NAPI, filters, timers, and stats survive cycles.
- Link: exercise autoneg and forced speeds, pause on/off/autoneg, EEE on/off, FEC reporting, module warning states, link down reasons, and speed capability changes. Confirm `netif_carrier_*`, `bnxt_report_link()`, and ethtool settings match HWRM state.
- Resource pressure: test limited MSIX, limited rings, RoCE reservations, dynamic MSIX growth/shrink, Nitro A0, aggregate ring disable fallback, and default ring trimming on multi-port systems.
- Feature toggles: enable/disable GRO_HW, LRO, NTUPLE, VLAN RX acceleration, UDP GSO, XDP, and MTU changes while open. Confirm the code chooses in-place TPA update versus close/open reinit correctly.
- RX mode and filters: overflow UC/MC address limits, untrusted VF promiscuous requests, PF unavailable VF filter retries, all-multicast fallback, RFS insertion/aging/deletion, and user filter restoration after reset.
- Stats: verify counter wrap handling, P5-plus zero-counter ignore behavior, saved stats across close, per-queue stats, and no use-after-free during concurrent close and stats reads.
- Firmware health: simulate heartbeat stalls, reset-counter changes, fatal firmware events, echo requests, OP-TEE reset request, reset abort, firmware readiness timeout, and successful reopen. Confirm devlink health state and ULP/SR-IOV restart behavior.
- PCI/PM: suspend/resume, shutdown with WoL, PCI AER frozen/non-fatal/permanent failure, slot reset, and resume. Confirm PCI state, context memory, reservations, interrupts, ULPs, and carrier are restored.
- Queue-management API: live RX queue stop/start with alternate page sizes on supported chips, shared-ring TX stop/start, TPH enabled, TPA enabled, aggregate rings, and failure injection in HWRM ring allocation.

## Cross-Chunk Notes

- Lower-level TX/RX datapath, memory allocation, ring helper, filter helper, HWRM wrapper, event decode, and many feature-specific helpers are defined before line 9570. This chunk depends on them but primarily covers orchestration and lifecycle.
- The file ends at line 17513, so module registration, PCI driver wiring, and netdev operation tables are complete within this chunk. The final merged per-file report should reconcile this lifecycle view with the earlier chunk's datapath and helper implementations.
