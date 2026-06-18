# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_main.c lines 1-9669

## Scope

This chunk covers the Intel E800 `ice` PF driver main orchestration file from module metadata through probe/load/remove, service-task/reset handling, netdev open and feature paths, XDP setup, VLAN/RSS/statistics handling, bridge/TC/ADQ support, and `ice_open_internal()`. The assigned range ends at line 9669, just before the later `ice_stop()` body and final `net_device_ops` definitions.

## Purpose

`ice_main.c` is the PF-facing glue layer between the Linux PCI/netdev/TC/XDP/devlink/PM frameworks and lower-level ice hardware libraries. It owns the primary lifetime of `struct ice_pf` and PF `struct ice_vsi`, schedules asynchronous hardware work through the driver service task, routes AdminQ/Mailbox/Sideband events, performs reset preparation and rebuild, configures netdev capabilities, opens and tears down queues, and integrates advanced features such as DDP packages, Flow Director, DCB, PTP, GNSS, DPLL, SR-IOV mailboxes, RDMA auxiliary devices, switchdev, TC flower, ADQ channels, ETF TxTime, and XDP/XSK.

The file is intentionally broad: most lower-level hardware operations live in sibling modules, while this file coordinates sequencing, state bits, locks, Linux callback entry points, and error unwinding.

## Important APIs, Types, and State

- Module/PCI entry points: `ice_module_init()`, `ice_module_exit()`, `ice_probe()`, `ice_remove()`, `ice_shutdown()`, `ice_suspend()`, `ice_resume()`, PCI error handlers, `ice_pci_tbl`, and `ice_driver`.
- Netdev-facing entry points in this chunk: `ice_open()`, `ice_open_internal()`, `ice_set_mac_address()`, `ice_set_rx_mode()`, `ice_set_tx_maxrate()`, `ice_fdb_add()`, `ice_fdb_del()`, `ice_fix_features()`, `ice_set_features()`, `ice_change_mtu()`, `ice_get_stats64()`, `ice_tx_timeout()`, RSS helpers, bridge get/set, TC setup, and XDP setup.
- Main driver objects: `struct ice_pf` owns PCI device, `struct ice_hw`, PF-wide bitmaps, VSI array, interrupt trackers, flags/state bitmaps, service work/timer, wake state, DCB/FDir/PTP/RDMA/devlink/switchdev contexts, and statistics. `struct ice_vsi` owns a virtual station interface, netdev, queues/rings, VLAN ops, TC config, XDP program/rings, channel list, RSS state, and VSI state bits.
- Other important local types: `struct ice_aq_task` for waiting on AdminQ events, `struct ice_dim` for interrupt moderation profiles, local ring stat accumulators `struct ice_vsi_tx_stats` and `struct ice_vsi_rx_stats`, and ADQ `struct ice_channel` relationships.
- State and flag bits are central. PF state bits include `ICE_DOWN`, `ICE_SERVICE_DIS`, `ICE_SERVICE_SCHED`, reset request/receive bits, `ICE_PREPARED_FOR_RESET`, `ICE_RESET_FAILED`, `ICE_NEEDS_RESTART`, AdminQ/Mailbox/Sideband pending bits, `ICE_MDD_EVENT_PENDING`, `ICE_VFLR_EVENT_PENDING`, `ICE_SUSPENDED`, and auxiliary/RDMA error bits. PF flags include feature and policy flags such as `ICE_FLAG_ADV_FEATURES`, `ICE_FLAG_DCB_ENA`, `ICE_FLAG_PTP_SUPPORTED`, `ICE_FLAG_TC_MQPRIO`, `ICE_FLAG_FLTR_SYNC`, `ICE_FLAG_NO_MEDIA`, `ICE_FLAG_LINK_DOWN_ON_CLOSE_ENA`, and `ICE_FLAG_CLS_FLOWER`. VSI state bits include `ICE_VSI_DOWN`, `ICE_CFG_BUSY`, filter-change bits, promiscuous-change bits, rebuild pending, and netdev allocation/registration bits.
- Important locks and synchronization: `pf->sw_mutex`, `tc_mutex`, `adev_mutex`, `lag_mutex`, `avail_q_mutex`, `vfs.table_lock`, `aq_wait_lock`, `reset_wait_queue`, `aq_wait_queue`, per-ring `u64_stats` sequence counters, RCU for ring/XDP pointer cleanup, RTNL locks for some netdev/VSI queue and switchdev operations, device locks for RDMA qdisc exclusion, and service-task scheduling bits.

## Initialization and Load Control Flow

Module init creates the shared `ice_wq` workqueue, ordered `ice_lag_wq`, initializes debugfs, registers the PCI driver, then registers the SF driver. Module exit unregisters in reverse order.

`ice_probe()` rejects VFs, optionally performs FLR for kdump, enables and maps BAR0 with devres, allocates `struct ice_pf`, configures 64-bit DMA, saves PCI state, fills the `ice_hw` identity and MMIO fields, sets control queue lengths, initializes debug masks, and handles firmware recovery mode with `ice_probe_recovery_mode()`. The normal path calls `ice_init_hw()`, `ice_init_dev_hw()` to load DDP and safe-mode capabilities, gets the shared adapter, initializes device interrupt/service state with `ice_init_dev()`, initializes PF software with `ice_init()`, then under devlink lock calls `ice_load()` and `ice_init_devlink()`.

`ice_init_dev_hw()` initializes feature support, requests the DDP package, applies optional Tx topology, loads or validates the package, and populates supported RXDIDs. If DDP fails, advanced features are disabled and safe-mode capabilities are substituted. Safe mode still creates a PF netdev with minimal ops and VLAN settings that allow tagged traffic without advertised offloads.

`ice_init()` layers PF software setup: `ice_init_pf()` initializes locks, wait queues, mailbox overflow/snapshot handling, xarrays, queue bitmaps, UDP tunnel callbacks, and the misc MSI-X vector; `ice_alloc_vsis()` allocates VSI tables; `ice_init_pf_sw()` creates the switch structure and PF VSI; wake reason is recorded and cleared; link events, NVM PHY type, link override, PHY user configuration, and driver version are initialized; then service scheduling is enabled and the timer is armed.

`ice_load()` configures the main PF VSI netdev, DCB netlink, initial MAC and broadcast filters, devlink PF port, netdev registration, indirect TC block registration, NAPI, advanced feature initialization, RDMA initialization/finalization, and restarts the service task. Error paths unwind in the reverse order.

Removal and shutdown are strict reverse-lifetime paths. `ice_remove()` waits for reset completion, handles recovery-mode cleanup, disables SR-IOV/VF resets when needed, removes aRFS outside safe mode, tears down dynamic ports/devlink/netdev/RDMA/features, deinitializes PF software, releases VSIs, configures WoL/magic wake, drops adapter and hardware state, deinitializes interrupts/service, cancels waiting AQ tasks, and marks the PF down. `ice_shutdown()` calls remove and moves to D3hot for poweroff if WoL is enabled.

## Service Task, Interrupts, and AdminQ Events

Interrupt handlers intentionally do little work. `ice_misc_intr()` marks AdminQ, MailboxQ, and SidebandQ as pending, reads OICR, classifies software interrupt, MDD, VFLR, reset warning, PTP timestamp/event, auxiliary critical errors, and unexpected critical conditions. It sets PF state bits, may request a PFR, schedules the service task, and re-enables dynamic interrupts. The threaded handler processes deferred PTP Tx timestamps and re-arms timestamp interrupts if more are pending. `ice_ll_ts_intr()` handles low-latency PTP timestamp completion.

`ice_service_task()` is the main asynchronous control plane. It reports queued Tx hang health information, runs reset handling first, and bails during reset/suspend/restart-needed. It then sends auxiliary error and MTU-change events to RDMA, handles plug/unplug auxiliary-device flags, cleans AdminQ, checks media and PHY config, checks for hung Tx queues, synchronizes MAC/promisc filters, handles MDD events, updates periodic stats, and when not in safe mode processes VFLR, MailboxQ, SidebandQ, aRFS filters, and FDir context flush. It clears `ICE_SERVICE_SCHED` only at completion and immediately re-arms the timer when work remains or work ran longer than the timer period.

`__ice_clean_ctrlq()` is the shared AdminQ/MailboxQ/SidebandQ event drain. It checks queue error bits, allocates an event buffer, drains receive queue elements up to `ICE_DFLT_IRQ_WORK`, wakes any `ice_aq_task` waiters matching the opcode, and dispatches events: link status, VF LAN overflow, VF mailbox messages, firmware logs, LLDP MIB changes, and health status. Mailbox overflow/malicious-VF detection data is prepared differently depending on mailbox-limit feature support.

`ice_aq_prep_for_event()` and `ice_aq_wait_for_event()` provide a wait-list abstraction around asynchronous AdminQ completions. The wait path uses `pf->aq_wait_lock` and `pf->aq_wait_queue`, returns `-ETIMEDOUT`, `-ECANCELED`, or event success, and removes the task entry after wake. `ice_aq_cancel_waiting_tasks()` cancels all waiters during removal.

## Reset and Rebuild Behavior

Reset control is bit-driven. `ice_schedule_reset()` validates no earlier failed/in-progress reset, sets a PFR/CORER/GLOBR request bit, and schedules the service task. `ice_reset_subtask()` either completes a reset indicated by OICR, or initiates a new requested reset. CORER/GLOBR/EMPR are detected from hardware reset warnings and require polling `ice_check_reset()` before rebuild. PFR does not generate the same OICR flow, so `ice_do_reset()` calls `ice_rebuild()` directly after triggering it.

`ice_prepare_for_reset()` is the main quiesce path: synchronize misc IRQ, unplug auxiliary devices, notify VFs and mark them disabled, flush switchdev bridge FDBs, preserve or remove ADQ channel state depending on reset type, detach the main netdev, clear switch/filter tables, mark the main VSI rebuild pending, disable all VSIs and reset aggregation node counters, prepare PTP, exit GNSS, clear scheduler port state, shut down control queues, and set `ICE_PREPARED_FOR_RESET`.

`ice_rebuild()` reinitializes control queues, reloads software filter tables or DDP package depending on reset type, clears PF config, reinitializes NVM/capabilities/MAC frame size/port params/scheduler, recreates misc interrupts, restores FDir allocation, rebuilds DCB/PTP/GNSS, rebuilds PF VSIs, rebuilds ADQ channels for PFR, rebuilds control VSI/FDir/aRFS when enabled, reattaches netdev, restores link state, sends driver version, replays post-reset switch state, clears reset failure, clears health reporters, finalizes RDMA, rebuilds LAG, restores PTP timestamp mode, and starts PTP work. Failure sets `ICE_RESET_FAILED` and `ICE_NEEDS_RESTART`, requiring unload/reload.

## Link, PHY, Media, and WoL

`ice_init_link_events()` programs link-event masks and enables link events. `ice_handle_link_event()` parses AdminQ link events and calls `ice_link_event()`. `ice_link_event()` refreshes link info, checks module power/PHY FW/link config errors, handles no-media transitions by disabling link, updates PTP link state, rebuilds DCB or sends default LLDP MIB when DCB is inactive, updates carrier/queues, logs link details, and notifies VFs.

PHY setup is media-aware. `ice_init_nvm_phy_type()` captures NVM PHY capabilities for link override, `ice_init_link_dflt_override()` enables total port shutdown/link-down-on-close if NVM requests it, `ice_init_phy_user_cfg()` seeds current user speed/FEC/FC configuration from FW default/topology capabilities, and `ice_phy_cfg()` compares active config to desired config before programming speed/FEC/FC/link enable. `ice_check_media_subtask()` polls for inserted media when `ICE_FLAG_NO_MEDIA` is set and re-applies PHY config if appropriate.

WoL state is persisted in `pf->wol_ena` and programmed in `ice_set_wake()`. `ice_setup_mc_magic_wake()` writes the current or permanent MAC to firmware for multicast magic wake and preserves LAA across PFR. Wake reason is recorded from `PFPM_WUS` at init/resume and then cleared.

## Netdev, Queues, XDP, and Statistics

`ice_cfg_netdev()` allocates an Ethernet netdev sized for max Tx/Rx queues, attaches `struct ice_netdev_priv`, sets ops/features, assigns permanent MAC for PF VSI, enables unicast filtering, configures TC layout, and sets max MTU. `ice_register_netdev()` registers and leaves carrier/queues off until open.

`ice_open()` blocks while reset is in progress. `ice_open_internal()` refuses `ICE_NEEDS_RESTART`, refreshes link info, initializes PHY user settings if media is present, enables PHY link or marks no-media, then calls `ice_vsi_open()`. `ice_vsi_open()` allocates Tx/Rx descriptors, configures LAN queues/VLAN/DCB/XDP, requests queue IRQs, sets real queue counts, attaches NAPI queues, and calls `ice_up_complete()`. `ice_up_complete()` programs MSI-X, starts Rx rings, clears `ICE_VSI_DOWN`, enables NAPI/IRQs, starts netdev queues if link is up, initializes stats baseline, and schedules service work for PF VSIs.

`ice_down()` expects `ICE_VSI_DOWN` already set, removes VLAN zero, marks PTP link down, stops carrier and Tx queues, disables queue IRQs, stops LAN and XDP Tx rings, stops Rx rings, disables NAPI and DIM work, cleans Tx/XDP/Rx rings, and reports close failure if ring or VLAN operations fail. `ice_down_up()` wraps a reconnect for feature/MTU changes.

XDP support is PF/SF-only and disabled in safe mode. `ice_xdp()` serializes with `vsi->xdp_state_lock` and handles program setup or XSK pool setup. `ice_xdp_setup_prog()` validates MTU vs linear-frame XDP, handles hot swaps without full down/up, stops the VSI when needed, computes XDP Tx queue resources, allocates and maps XDP rings, updates scheduler queue counts, assigns the BPF program, toggles redirect target features, destroys rings on detach, restarts the VSI, and schedules Rx NAPI. A static key `ice_xdp_locking_key` tracks when fewer XDP Tx rings than CPUs force shared locking.

Statistics combine software ring counters and hardware port counters. Ring counters are read with `u64_stats_fetch_begin/retry` and summed across Tx, Rx, and XDP Tx rings. Netdev packet/byte counters are maintained as deltas from previous ring values once `pf->stat_prev_loaded` is valid, protecting against random post-reset baselines. `ice_update_pf_stats()` reads many GLPRT/PRT registers and DCB stats, while `ice_get_stats64()` returns ring-updated packet/byte fields and cached hardware/error fields.

Interrupt moderation uses local DIM profiles rather than generic hardware packet-count assumptions. `ice_tx_dim_work()` and `ice_rx_dim_work()` translate DIM profile indexes to driver ITR microsecond values; `ice_init_moderation()` initializes DIM work, mode, profile, static or dynamic ITR, and INTRL for each q_vector before NAPI is enabled.

## Filters, VLANs, RSS, Bridge, and Netdev Features

MAC filter synchronization is deferred. `ice_set_rx_mode()` marks unicast and multicast filter changes and schedules service work. `ice_vsi_sync_fltr()` serializes on `ICE_CFG_BUSY`, snapshots changed netdev flags, builds sync/unsync lists under `netif_addr_lock_bh()`, removes and adds hardware MAC filters, forces promisc when AdminQ reports no filter space, updates ALLMULTI/PROMISC default-VSI state, and re-marks change bits for retry on failure.

Promiscuous mode depends on VLAN state. With non-zero VLANs the code uses VLAN-aware promisc calls and includes VLAN RX/TX promisc bits; without VLANs it uses VSI promisc calls. VLAN add/delete callbacks preserve VLAN 0, coordinate all-multicast promisc lookup-type changes between VLAN and non-VLAN variants, and call compatibility VLAN ops to add/delete VLAN rules.

`ice_fix_features()` enforces VLAN offload limitations: CTAG/STAG stripping and insertion are mutually exclusive, DVM filtering must be enabled or disabled for both CTAG and STAG together, SVM rejects STAG filtering, and VLAN stripping is disabled if FCS/CRC stripping is disabled with no VLANs. `ice_set_vlan_features()` applies stripping/insertion/filtering via `ice_vsi_vlan_ops` and updates ring packet-context VLAN protocol. `ice_set_features()` blocks advanced changes in safe mode and during reset, toggles RSS LUT, VLAN settings, FCS/CRC strip via down/up, ntuple/FDir/aRFS, HW TC offload flags, loopback, and E830 GCS-vs-TSO restrictions.

RSS helpers fill default LUT entries and get/set RSS LUT, key, and hash function through AdminQ/VSI update calls. Symmetric Toeplitz changes are replayed across existing RSS configurations.

Bridge mode callbacks expose VEPA/VEB through rtnetlink. `ice_bridge_setlink()` validates bridge mode attributes, updates every VSI switch flag, toggles `hw->evb_veb`, updates switch rules, and rolls back the hardware mode flag if switch rule update fails.

## TC, Flow Director, ADQ Channels, and TxTime

TC flower setup supports ingress and egress block callbacks and indirect tunnel/VLAN block callbacks. Flower rules are delegated to `ice_add_cls_flower()` and `ice_del_cls_flower()`; only chain 0 is accepted. Indirect block registration tracks `struct ice_indr_block_priv` per netdev and supports tunnel devices plus VLAN devices over the PF netdev.

MQPRIO channel mode implements ADQ. `ice_validate_mqprio_qopt()` requires PF VSI, valid offsets/counts, at most one non-power-of-two queue count with ordering constraints, queue ranges within current queues, min/max rates within link speed and multiples of `ICE_MIN_BW_LIMIT`, and sum of min rates within link speed. `ice_setup_tc_mqprio_qdisc()` rejects switchdev, locks out active RDMA auxiliary drivers, serializes with `tc_mutex`, pauses the VSI, removes old channels if disabling, rebuilds the main VSI with requested queue counts, configures TCs, sets TC0 rate limits, creates channel VSIs for nonzero TCs, optionally reconfigures RSS, and resumes the VSI.

ADQ channels are represented by `struct ice_channel` and created as `ICE_VSI_CHNL` VSIs. Channel setup maps base queues, creates a channel VSI, adds it to existing FDir profiles, records switch/VSI/q mapping info, annotates parent rings and q_vectors with channel pointers, configures bandwidth limits, and tracks channels on `vsi->ch_list` and `vsi->tc_map_vsi`. Removal deletes channel TC flower filters, deletes FDir ntuple filters when queue config changes, releases FDir resources, removes scheduler LAN config, deletes channel VSIs, clears ring/q_vector channel pointers, and resets all-TC metadata.

Channel rebuild after PFR reconstructs TC config and all channel VSIs, replays VSI filters, remaps hardware VSI numbers, restores channel resource annotations and bandwidth limits, and restores RSS LUT/key. If replay fails, advanced filters may be preserved or removed depending on failure point.

ETF TxTime offload is gated by `ICE_F_TXTIME`. `ice_offload_txtime()` validates queue ID, toggles the PF `txtime_txqs` bitmap, and if running disables/re-enables the queue through `ice_cfg_txtime()`. Open path skips normal netdev TC queue configuration when TxTime queues are active.

## Dependencies and Integration Points

- Linux subsystems: PCI, devres, DMA mapping, netdev, NAPI, ethtool ops, rtnetlink bridge API, traffic control block/qdisc/flower APIs, XDP/XSK, firmware loader, devlink, PM sleep ops, PCI AER/ERS, PTP clock/timestamping, workqueues/timers, xarrays, RCU, and u64 stats synchronization.
- Hardware/AdminQ libraries: `ice_common`, `ice_lib`, `ice_base`, `ice_fltr`, `ice_switch`, `ice_sched`, `ice_dcb_lib`, `ice_fdir`, `ice_irq`, `ice_ddp`, and register access via `rd32/wr32/ice_flush`.
- Feature modules: DCB netlink/MIB handling, Flow Director and aRFS, PTP/GNSS/DPLL, RDMA auxiliary (`iidc_rdma_event`), SR-IOV VF mailbox/reset/MDD/VFLR logic, LAG, HWMON, devlink regions/params/ports/health, switchdev/eswitch bridge offloads, subfunction driver, VLAN ops compatibility layer, XSK pool setup, and TC flower parser/action offloads.
- Firmware/DDP integration: `request_firmware()` searches optional DSN-specific `intel/ice/ddp/ice-<dsn>.pkg` before default `intel/ice/ddp/ice.pkg`; DDP package state controls safe mode and advanced feature availability. Tx topology may reinitialize hardware after applying DDP topology data.

## State and Persistence Behavior

Most runtime state is in memory and reconstructed on reset or reload. Persistent hardware/firmware state includes DDP package loaded on device, NVM PHY/link default override, WoL control, firmware-managed MAC/LAA WoL settings, hardware switch/filter/scheduler tables, and mailbox/AdminQ state. The driver preserves user-visible runtime configuration across reset where possible: netdev MAC, MTU, features, XDP program pointer, RSS state, DCB/TC config, ADQ channel config, FDir/aRFS filters, PTP timestamp mode, LAG state, WoL enable, and PHY user speed/FEC/FC settings.

Reset paths explicitly distinguish PFR from wider resets. PFR can preserve more local channel state and rebuild directly; CORER/GLOBR/EMPR require package reload/control-queue reinit and may discard ADQ channel rebuild support. Statistics use previous-counter baselines and set `stat_prev_loaded` false during reset to avoid reporting bogus deltas. AQ waiters are canceled on remove.

## Risks and Edge Cases

- Service-task state bits are a high-risk concurrency boundary. Missed clear/set ordering can lose events or cause the service task to stop rescheduling. The code uses `test_and_set_bit`, memory barriers, queue-pending rechecks, and immediate timer re-arm to reduce this risk.
- Reset and rebuild sequencing is fragile because many subsystems depend on order: control queues before AdminQ commands, PTP before VSI rebuild link events, DDP reload before advanced feature replay, FDir control VSI before FDir filter replay, and RDMA/LAG/PTP restoration after VSI rebuild.
- Safe mode changes behavior substantially. Advanced netdev features, XDP, DCB/FDir/PTP/GNSS/DPLL/LAG/HWMON-style setup are limited or bypassed; safe-mode VLAN config must allow tagged packets without normal advertised offloads.
- MAC and VLAN filter sync has retry behavior but can transiently force promiscuous mode on filter-space exhaustion. Incorrect clearing of change bits or `ICE_CFG_BUSY` can leave stale filters or block configuration.
- ADQ channel mode has many resource coupling points: main VSI queue counts, channel VSI lifecycle, FDir profile group membership, TC flower filter destinations, RSS sizing, bandwidth limits, and reset replay. Partial failure can require filter removal to avoid stale destinations.
- XDP ring setup shares PF queue bitmaps with normal queues and can enable a static key for shared XDP Tx rings. Failure paths must clear bitmap allocations, RCU-free rings and stats, unmap rings from q_vectors, and restore scheduler queue counts.
- VLAN feature rules are hardware-specific and mutually exclusive. Misapplied CTAG/STAG stripping/filtering or FCS interactions can produce packet metadata inconsistencies in Rx ring contexts.
- PCI PM and AER paths reuse reset preparation and interrupt reinitialization. Hibernation explicitly frees queue vectors and misc vectors; resume relies on reset/rebuild to restore functionality.
- Tx timeout escalation is stateful. It detects PFC storms as fake hangs, logs queue head/NTC/NTU/interrupt data, stores health report data, and escalates PFR to CORER to GLOBR before marking the device unrecoverable.

## Test Signals

Useful validation should exercise:

- Probe/load with valid DDP, missing/invalid DDP safe mode, firmware recovery mode, and optional DSN-specific package fallback.
- Interface open/close, MTU change, link up/down, media remove/insert, unsupported module/topology conflict, link-down-on-close, and WoL suspend/resume.
- Reset paths: software PFR, CORER/GLOBR/EMPR OICR reset warning, rebuild failure requiring `ICE_NEEDS_RESTART`, PCI AER reset, kdump FLR path, and reset during active VFs/RDMA/PTP/ADQ/XDP.
- AdminQ/Mailbox/Sideband drains with link events, VF mailbox floods, VF LAN overflow, LLDP MIB change, firmware log events, health status events, and AQ wait timeout/cancel behavior.
- Netdev feature toggles: VLAN CTAG/STAG stripping/filtering in SVM and DVM, FCS/RXFCS interactions, RXHASH, NTUPLE/FDir/aRFS, HW TC offload, loopback, E830 GCS/TSO exclusion, RSS LUT/key/hash get/set.
- XDP attach/detach/hot-swap with MTU limits, XSK pool setup, insufficient XDP Tx queues, queue count changes while XDP is enabled, and redirect target feature toggling.
- TC paths: flower ingress/egress add/delete, indirect tunnel/VLAN blocks, MQPRIO channel mode validation, ADQ channel creation/removal/rebuild, bandwidth min/max limits, RDMA-active qdisc rejection, switchdev MQPRIO rejection, and ETF TxTime enable/disable.
- Statistics and watchdog: ring stats consistency under traffic, PF hardware counters across reset, Tx hang detection and PFC storm suppression, health reporter data, MDD event logging/reset behavior, and service timer re-arm under continuous pending events.
