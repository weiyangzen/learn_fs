# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_main.c lines 9300-16679

## Chunk Scope

This chunk covers the high-level PF lifecycle for the Intel i40e Ethernet driver: reset recovery, AdminQ event handling, Flow Director recovery, link/DCB updates, VSI/VEB allocation and rebuild, RSS/XDP/netdev operations, PCI probe/remove, suspend/resume, PCI error recovery, shutdown, and module registration. It sits after the lower-level queue, interrupt, filter, DCB, channel, and open/close helpers from earlier in the file and wires those helpers into the device lifetime and Linux networking callbacks.

## Purpose and Responsibilities

- Dispatch pending reset requests from `pf->state`, perform PF/core/global resets, and rebuild firmware-visible switch state while preserving software state such as filters, channels, bandwidth limits, promiscuity, PTP time, and VF resources.
- Run the periodic service task that coordinates filter sync, reset recovery, MDD/VFLR handling, watchdog/statistics updates, FDir maintenance, client notifications, and AdminQ event draining.
- Manage firmware switch elements: the main PF VSI, FDir VSI, SR-IOV/VMDq/channel VSIs, and VEB bridge elements, including reconstruction after reset and deletion during remove.
- Initialize the PF during PCI probe: PCI resources, MMIO mapping, AdminQ, NVM/firmware capability discovery, software feature flags, queue/vector budgets, LAN HMC, switch setup, PTP, DCB, SR-IOV, UDP tunnel offload, iWARP client integration, and devlink registration.
- Expose netdev callbacks for feature toggles, FDB/bridge operations, XDP/AF_XDP setup, UDP tunnel ports, physical port IDs, hwtstamp, and VF controls.
- Provide PM and PCI error paths that quiesce IO, preserve wake settings, tear down/restores interrupts, and rebuild the device.

## Important APIs, Types, and Entry Points

- `struct i40e_pf`: central PF state holder. This chunk heavily mutates `pf->state`, `pf->flags`, `pf->hw`, `pf->vsi[]`, `pf->veb[]`, queue/vector lump trackers, FDir counters, cloud filter lists, DCB state, WoL state, timers, work item, and PCI/devlink/client bookkeeping.
- `struct i40e_vsi`: software representation of PF, FDir, SR-IOV, VMDq/channel, or iWARP VSIs. Allocation paths set queue counts, ring arrays, q_vectors, netdevs, MAC filters, RSS settings, XDP pointers, uplinks, and hardware SEIDs.
- `struct i40e_veb`: software representation of hardware VEB bridge elements. This chunk allocates, adds, configures VEPA/VEB mode, queries bandwidth, reconstructs, releases, and recursively deletes VEB branches.
- Reset/rebuild functions: `i40e_do_reset_safe()`, `i40e_prep_for_reset()`, `i40e_reset()`, `i40e_rebuild()`, `i40e_reset_and_rebuild()`, and `i40e_handle_reset_warning()`.
- Service/event functions: `i40e_service_task()`, `i40e_service_timer()`, `i40e_reset_subtask()`, `i40e_watchdog_subtask()`, `i40e_clean_adminq_subtask()`, `i40e_handle_link_event()`, `i40e_handle_lan_overflow_event()`, and, with DCB, `i40e_handle_lldp_event()`.
- FDir helpers: `i40e_get_current_fd_count()`, `i40e_get_global_fd_count()`, `i40e_fdir_check_and_reenable()`, `i40e_fdir_flush_and_replay()`, `i40e_fdir_sb_setup()`, and `i40e_fdir_teardown()`.
- VSI/VEB lifecycle: `i40e_vsi_mem_alloc()`, `i40e_vsi_setup()`, `i40e_vsi_reinit_setup()`, `i40e_add_vsi()`, `i40e_vsi_release()`, `i40e_vsi_clear()`, `i40e_veb_setup()`, `i40e_add_veb()`, `i40e_veb_release()`, `i40e_switch_branch_release()`, and `i40e_setup_pf_switch()`.
- Interrupt/RSS/resource setup: `i40e_init_msix()`, `i40e_init_interrupt_scheme()`, `i40e_restore_interrupt_scheme()`, `i40e_setup_misc_vector()`, `i40e_vsi_alloc_q_vectors()`, `i40e_pf_config_rss()`, `i40e_config_rss()`, `i40e_get_rss()`, and `i40e_reconfig_rss_queues()`.
- Netdev and XDP integration: `i40e_netdev_ops`, `i40e_config_netdev()`, `i40e_set_features()`, `i40e_xdp_setup()`, `i40e_xdp()`, `i40e_queue_pair_disable()`, and `i40e_queue_pair_enable()`.
- PCI/module entry points: `i40e_probe()`, `i40e_remove()`, `i40e_shutdown()`, `i40e_suspend()`, `i40e_resume()`, `i40e_err_handler`, `i40e_driver`, `i40e_init_module()`, and `i40e_exit_module()`.

## Control Flow and State Machines

### Reset and Rebuild

Reset requests are accumulated as bits in `pf->state` and consumed by `i40e_reset_subtask()`. The subtask clears request bits, gives priority to `__I40E_RESET_INTR_RECEIVED` recovery, and avoids reset work while the PF is down or configuration is busy. `i40e_do_reset()` chooses between global, core, PF reset, PF reset plus main VSI reinit, VSI reinit, and VSI down requests. User-facing calls can use `i40e_do_reset_safe()`, which serializes with `rtnl_lock()`.

`i40e_prep_for_reset()` is the reset prologue. It guards with `__I40E_RESET_RECOVERY_PENDING`, notifies VFs if the Admin Send Queue is alive, quiesces all active VSIs, clears XPS state, invalidates VSI SEIDs, shuts down AdminQ and HMC, and saves PTP hardware time. `i40e_reset()` performs the PF reset and records `pfr_count` or `__I40E_RESET_FAILED`. `i40e_rebuild()` then rebuilds AdminQ, capabilities, LAN HMC, DCB state, PF switch, VEBs, VSIs, cloud filters, channels, MSS workaround, autoneg restart, misc IRQ, flow-control drop filter, queues, promiscuous mode, VFs, and driver version reporting. It also has a recovery-mode branch that only restores minimal resources and ethtool operations as needed.

The rebuild path depends on local switch arrays retaining intent while firmware state disappears across reset. If VEB reconstruction fails for the main VEB, it falls back to a simple PF VSI connection to the MAC SEID. Channel VSIs and cloud filters are replayed after the main VSI exists again.

### Service Task

`i40e_service_timer()` periodically reschedules `service_task` via the driver's workqueue. `i40e_service_task()` exits early if reset recovery or suspend is active, serializes with `__I40E_SERVICE_SCHED`, then runs a fixed sequence outside recovery mode: hung recovery detection, filter sync, reset handling, malicious driver detection, VFLR processing, watchdog updates, FDir maintenance, client reset/L2 notifications, and a second filter sync. In recovery mode it only runs reset handling before cleaning AdminQ. After AdminQ drain it clears the schedule bit with a memory barrier and immediately reschedules if work exceeded one timer period or event bits remain.

`i40e_clean_adminq_subtask()` clears AdminQ error bits in ARQ/ASQ length registers, allocates an AQ event buffer, drains up to `I40E_AQ_WORK_LIMIT` events, dispatches link, VF mailbox, LLDP MIB, LAN overflow, peer, and NVM completion opcodes, then re-enables AdminQ interrupt cause. Link and LLDP handlers take RTNL because they update netdev and DCB/VSI state.

### Link, DCB, and Notifier Behavior

`i40e_link_event()` forces a fresh firmware link query, manages temporary link polling on query errors, compares old/new link and speed, updates carrier and TX queues for the main VSI or VEB-connected VSIs, notifies VFs, updates PTP clock increments, and for software DCB falls back to single-TC defaults on link down. `i40e_handle_link_event()` ignores ARQ link payload for state refresh but uses it to report high-temperature or unsupported-module conditions.

Under `CONFIG_I40E_DCB`, `i40e_handle_lldp_event()` handles nearest-bridge local/remote MIB changes. Remote updates refresh `hw->remote_dcbx_config`; local updates fetch the new DCBX config, compare ETS/PFC/app tables with `i40e_dcb_need_reconfig()`, flush DCBNL apps, quiesce VSIs, reconfigure DCB, resume port TX, wait for queues to disable, then unquiesce and notify clients of L2 changes.

### VSI, VEB, Queue, and Interrupt Lifecycles

`i40e_vsi_setup()` is the main VSI constructor. It validates or creates the uplink VEB, allocates the software VSI slot, reserves queue lumps, adds or retrieves the hardware VSI, configures netdev/devlink for main/VMDq VSIs, registers the netdev, sets DCBNL for the main netdev when enabled, allocates vectors, allocates rings, maps rings to q_vectors, resets stats, and configures RSS for VMDq when supported. Error unwinds delete hardware elements, destroy devlink ports, unregister/free netdevs, free vectors/rings, and clear the VSI slot.

`i40e_add_vsi()` builds `struct i40e_vsi_context` differently by type. The main PF VSI is retrieved from firmware rather than added; FDir, VMDq, and SR-IOV VSIs are created through AQ. It applies source pruning changes, MFP queue map updates, TC config, VEB loopback flags, iWARP queue options, SR-IOV VLAN/security settings, and marks existing MAC filters as `I40E_FILTER_NEW` so the filter sync subtask reloads them after resets.

`i40e_vsi_release()` refuses VEB owners and a running PF main VSI, unregisters or closes netdev-backed VSIs, disables IRQs, destroys devlink for the main VSI, marks filters for deletion, syncs filters, deletes the hardware element, frees q_vectors/netdev/rings/software arrays, and may release the uplink VEB if no non-owner VSIs remain. VEB deletion uses `i40e_switch_branch_release()` for recursive branch cleanup.

`i40e_init_msix()` budgets MSI-X vectors among misc, LAN/RSS, FDir sideband, iWARP, and VMDq. It degrades feature counts if the platform grants fewer vectors, disabling FDir, VMDq, or iWARP when none remain. `i40e_init_interrupt_scheme()` falls back from MSI-X to MSI to legacy IRQ and creates an IRQ lump tracker with vector 0 reserved for misc. `i40e_restore_interrupt_scheme()` reacquires vectors after suspend, allocates q_vectors for all VSIs, remaps rings, and reinitializes the misc vector.

Queue-pair hot toggles (`i40e_queue_pair_disable()` and `i40e_queue_pair_enable()`) are protected by `__I40E_CONFIG_BUSY`, disable or enable IRQ/NAPI/rings, clean rings and stats on disable, configure Tx/XDP/Rx rings on enable, and use `i40e_control_wait_tx_q()`, `i40e_control_rx_q()`, and `i40e_pf_rxq_wait()` for hardware synchronization. One risk is that `i40e_queue_pair_disable()` does not call `i40e_exit_busy_conf()` on its path in this chunk; callers must ensure the busy bit is cleared elsewhere or this is a latent lockout bug.

### Probe, Remove, PM, and Error Recovery

`i40e_probe()` performs the full PCI bring-up: enable memory BARs, set DMA mask, request regions, allocate PF, map registers after BAR-size validation, initialize IDs and AQ locks, clear PXE mode on old revisions, clear hardware, determine MAC type, handle repeated resets/recovery, initialize shared code and AdminQ, report firmware/NVM versions, verify EEPROM, discover capabilities, initialize software flags/resource trackers, optionally enter minimal recovery mode, initialize/configure LAN HMC, stop firmware LLDP where supported, resolve MAC address, set PTP pins, initialize DCB, configure service timer/work, read WoL setting, determine queue use, initialize interrupts, configure UDP tunnel offload table, allocate VSI table, set up PF switch, open FDir VSI if present, configure PHY interrupt masks, initialize MDD rate limiting, apply MSS/autoneg workarounds, clear `__I40E_DOWN`, set misc vector, allocate existing VFs, reserve iWARP vectors, initialize debug/client service, start timer, log PCI link capabilities, fetch PHY/FEC capabilities, set MAC frame size, add flow-control drop filter, mark LED/retimer capabilities, print features, and register devlink.

Probe has many labeled unwind paths. The major cleanup sequence tears down VSIs, PTP pins, interrupt capability, timer, LAN HMC, queue pile, AdminQ/MMIO/PF memory, PCI regions, and device enablement. Some labels intentionally share cleanup for multiple failure points.

`i40e_remove()` unregisters devlink/debug/PTP, disables RSS, blocks rebuild by taking `__I40E_RESET_RECOVERY_PENDING` and setting `__I40E_IN_REMOVE`, frees VFs, suspends timers/work, closes clients, tears down FDir/cloud filters, removes VEB branches and VSIs, deletes iWARP client devices, shuts down HMC/AdminQ, destroys AQ locks, clears interrupt scheme and remaining rings/VSIs/VEBs, frees trackers, unmaps MMIO, frees PF, releases PCI regions, and disables the device. Recovery-mode removal has a shorter netdev-only path before common unmap/AdminQ cleanup.

`i40e_io_suspend()` and `i40e_io_resume()` are shared by PM and error handling. Suspend marks down, stops timer/work, closes clients, enables multicast magic WoL if supported, takes RTNL, preps for reset, programs wake registers, and clears interrupts. Resume takes RTNL, restores interrupts, clears down, reset/rebuilds, clears suspended, and restarts the timer. PCI error handlers call these or the reset prologue/rebuild around slot resets and SR-IOV MSI restoration.

## State and Persistence Behavior

- Persistent software intent is held in `pf->flags`, `pf->state`, `pf->vsi[]`, `pf->veb[]`, filter lists, channel lists, bandwidth settings, RSS user key/LUT buffers, XDP program pointers, and VF structures. Reset rebuild relies on these structures remaining valid while hardware/AdminQ/HMC state is destroyed and recreated.
- Hardware state is programmed through AQ commands and MMIO registers. It includes switch element SEIDs, VSI contexts, VEB bandwidth/stats, RSS keys/LUT/HENA, PF/VF MDD registers, interrupt cause registers, queue control registers, NVM-derived OEM/WoL/total-port-shutdown values, FEC flags, wake registers, and flow-control drop filters.
- `pf->state` bits serialize or gate asynchronous paths: down, suspended, reset recovery pending, reset failed, AdminQ pending, service scheduled, config busy, recovery mode, remove-in-progress, FDir auto-disabled/flush requested, MDD print/event pending, temporary link polling, and client notifications.
- `pf->flags` advertise capability/configuration state: MSI/MSI-X, RSS, DCB, SR-IOV, FDir ATR/SB, VMDq, iWARP, MFP, VEB mode, PTP, total-port-shutdown, WoL-related behavior, MDD auto-reset, and feature-specific inactive states.
- Timers/work persist the service loop until suspend/remove/shutdown. Probe and resume arm the timer; remove/shutdown/suspend delete or shutdown it and cancel work.
- User-configured RSS key/LUT buffers persist across most reconfigurations but are discarded when RSS queue count shrinks below the previous VSI RSS size.

## Dependencies and Integration Points

- Linux PCI and PM: `struct pci_driver`, `pci_error_handlers`, BAR mapping, DMA mask setup, MSI/MSI-X APIs, PCI state save/restore, power-state and wake APIs.
- Linux netdev stack: `net_device_ops`, feature negotiation, carrier state, queue start/stop, FDB and bridge netlink operations, UDP tunnel NIC offload, XDP/AF_XDP, NAPI, ethtool setup, hwtstamp hooks, VLAN/macvlan handling, and RTNL locking.
- Intel AdminQ/shared-code APIs: capabilities discovery, switch config queries, VSI/VEB add/delete/update, PHY/link/FEC, LLDP/DCB, RSS key/LUT, UDP tunnel ports, partition bandwidth, NVM reads, MAC writes, and filter control.
- SR-IOV/VF control: VF reset notification, VF mailbox processing, VF MDD detection/reset, VFLR processing, VF allocation/free, VF link notifications, and SR-IOV netdev callbacks.
- DCB and PTP modules: DCBX config comparison/reconfigure, DCBNL app flushing/setup, PTP pin allocation, PTP init/stop, PTP time save, increment update, and TX/RX hang detection.
- Client/iWARP integration: client device add/delete, MSI-X info updates, client close/reset/L2-change notifications, and a neighbor private length requirement for `i40iw_net_event()`.
- Devlink/debugfs: main VSI devlink port creation/destruction and PF debug init/exit.

## Risks and Edge Cases

- Reset/rebuild ordering is fragile: AdminQ, HMC, switch, interrupts, VSIs, VEBs, filters, channels, clients, VFs, and PTP each have dependencies. Missing one replay step can leave software state apparently valid but firmware state absent.
- Locking context matters. Several paths explicitly require RTNL (`i40e_do_reset_safe()`, feature changes, bridge setlink, RSS reconfig, suspend/resume rebuild sections), while service work uses state bits and may schedule itself immediately. Mixing direct reset calls without the expected lock can race netdev registration or queue changes.
- Recovery mode intentionally limits functionality and has separate interrupt/netdev setup. Paths must respect `__I40E_RECOVERY_MODE` and `__I40E_IN_REMOVE` to avoid normal rebuild or queue work against a minimally initialized PF.
- MSI-X vector budgeting dynamically disables features. Test coverage should include partial vector grants, MSI fallback, and legacy IRQ mode because FDir, iWARP, VMDq, SR-IOV, RSS, and DCB assumptions change.
- `i40e_handle_lan_overflow_event()` derives a VF index from hardware fields and indexes `pf->vf[vf_id]`; correctness depends on firmware-provided PF/VF queue metadata being valid for allocated VFs.
- FDir counter maintenance has type-specific decrements. The `SCTP_V6_FLOW` case decrements `fd_udp6_filter_cnt` in this chunk, which looks suspicious because the IPv6 user SCTP path decrements `fd_sctp6_filter_cnt`.
- `i40e_queue_pair_disable()` enters `__I40E_CONFIG_BUSY` but this chunk does not clear it before return, unlike `i40e_queue_pair_enable()`. If no external caller clears it, queue-pair disable can leave future configuration blocked.
- Probe unwind and remove touch many shared resources. Double-free risk is mitigated by flags/nulling, but paths involving recovery mode, failed netdev registration, or partially allocated `pf->vsi` require careful review.
- XDP setup resets rings when XDP state changes and swaps `vsi->xdp_prog` before rebuild. Error paths after `xchg()` can leave program ownership or ring buffer allocation expectations subtle, especially with AF_XDP zero-copy pools.
- DCB handling for X710-T*L 2.5G/5G link speeds changes `I40E_FLAG_DCB_CAPABLE` based on link speed and firmware responses; tests must cover link-speed transitions as well as LLDP local and remote MIB events.

## Test Signals and Validation Ideas

- Probe/remove: successful module load/unload, `i40e_probe()` logs firmware/NVM/MAC/features, devlink registration, no leaks or warnings on repeated bind/unbind, and correct recovery-mode minimal netdev behavior when firmware reports recovery.
- Reset/rebuild: trigger PF reset, core/global reset, EMP reset, TX timeout recovery, RSS queue reconfig, XDP attach/detach, and bridge-mode changes; verify netdev carrier, queues, filters, channels, VFs, PTP, promiscuity, and UDP tunnel ports are restored.
- AdminQ events: inject or exercise link changes, unsupported/high-temperature module reports, VF mailbox messages, LLDP MIB updates, LAN overflow, NVM completion, and unknown opcodes; verify event bits clear and interrupts are re-enabled.
- FDir: fill/flush/replay filter table, check SB/ATR auto-disable and re-enable thresholds, validate invalid filter deletion counters, and specifically test SCTP IPv6 counter accounting.
- Interrupt modes: boot or fault-inject with full MSI-X, limited MSI-X, MSI-only, and legacy IRQ; verify vector distribution logs, feature disabling, q_vector mapping, misc interrupt setup, and suspend/resume restoration.
- VSI/VEB: create/release VMDq/channel/SR-IOV VSIs, bridge VEPA/VEB transitions, floating VEB deletion, recursive branch removal, and reset-time VEB reconstitution with cloud filters and bandwidth limits.
- Netdev features: toggle RXHASH, ntuple, VLAN stripping, HW TC with active cloud filters, loopback, L2 forwarding offload with macvlans, FDB add, bridge get/setlink, UDP tunnel port add/delete, and features_check for encapsulated header limit violations.
- XDP/AF_XDP: attach/detach programs across MTU limits, attach with frags support, zero-copy pool setup, redirect feature toggling, and queue wakeups after reset.
- PM/PCI error: suspend/resume, hibernate-like vector teardown/restore, shutdown with WoL enabled/disabled, PCI AER detected/slot_reset/reset_prepare/reset_done/resume, and SR-IOV VF MSI restoration after PCI reset.
