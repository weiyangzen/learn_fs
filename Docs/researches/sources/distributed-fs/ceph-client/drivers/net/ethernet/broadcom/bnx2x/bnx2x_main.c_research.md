# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_main.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004365`: lines 1-9287, `Docs/researches/chunks/subset-b-004365_research.md`
- `subset-b-004366`: lines 9288-15476, `Docs/researches/chunks/subset-b-004366_research.md`

## Chunk Research

### subset-b-004365: lines 1-9287

# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_main.c lines 1-9287

## Purpose

This chunk is the front half of the QLogic/Broadcom `bnx2x` Everest Ethernet driver main implementation. It covers module identity, firmware file declarations, PCI IDs, low-level register/DMAE services, interrupt and slowpath plumbing, link/MCP management, attention and parity handling, NIC hardware initialization, memory allocation, queue setup, and the beginning of unload/reset cleanup. The code is built around `struct bnx2x *bp` as the per-device state anchor and orchestrates PF/VF, CNIC, FCoE, SR-IOV, multi-function, and management-firmware interactions.

## Important APIs, Types, and Data

- Module parameters: `bnx2x_num_queues`, `disable_tpa`, `int_mode`, `dropless_fc`, `mrrs`, and `debug` influence queue count, TPA/LRO, interrupt mode, flow control behavior, PCIe read request size, and debug logging.
- PCI identity is declared through `enum bnx2x_board_type`, `board_info[]`, and `bnx2x_pci_tbl[]`, covering BCM57710/57711/57712/57800/57810/57811/57840 PF/MF/VF variants under Broadcom and QLogic vendor IDs.
- Firmware names are derived from `bnx2x_fw_file_hdr.h` version macros and registered with `MODULE_FIRMWARE()` for E1, E1H, E2, and V15 variants.
- Core register/DMA helpers include `REG_RD/REG_WR` users, indirect config-space accessors `bnx2x_reg_wr_ind()` / `bnx2x_reg_rd_ind()`, DMAE command builders `bnx2x_dmae_opcode*()`, `bnx2x_post_dmae()`, `bnx2x_issue_dmae_with_comp()`, `bnx2x_write_dmae()`, and `bnx2x_read_dmae()`.
- Hardware lock helpers `bnx2x_acquire_hw_lock()`, `bnx2x_release_hw_lock()`, `bnx2x_trylock_hw_lock()`, and leader-lock wrappers coordinate shared register/resource access across functions.
- GPIO/SPIO and PHY/link helpers include `bnx2x_get_gpio()`, `bnx2x_set_gpio()`, `bnx2x_set_mult_gpio()`, `bnx2x_set_gpio_int()`, `bnx2x_set_spio()`, `bnx2x_initial_phy_init()`, `bnx2x_link_set()`, `bnx2x_force_link_reset()`, and `bnx2x_link_test()`.
- Slowpath state and completion flows use `struct bnx2x_queue_sp_obj`, `struct bnx2x_func_sp_obj`, `struct eth_spe`, SPQ/EQ rings, status blocks, and event-ring opcodes. Main entry points include `bnx2x_sp_post()`, `bnx2x_sp_event()`, `bnx2x_eq_int()`, `bnx2x_sp_task()`, and `bnx2x_msix_sp_int()`.
- Init and queue data paths use `struct bnx2x_fastpath`, `struct bnx2x_fp_txdata`, status-block structures, ILT clients/lines, CDU contexts, queue setup parameter structs, and ramrod parameter structs.
- Management firmware communication is centralized in `bnx2x_fw_command()` and shared-memory access macros `SHMEM_RD/WR`, `SHMEM2_RD/WR`, and `MF_CFG_RD`.

## Control Flow

- Load/init begins by setting up DMAE state (`bnx2x_setup_dmae()`), allocating coherent driver memory (`bnx2x_alloc_mem()` and optional `bnx2x_alloc_mem_cnic()`), selecting interrupt mode (`bnx2x_set_int_mode()`), configuring ILT layout (`bnx2x_ilt_set_info()`), and then walking common/port/function hardware phases.
- Common hardware initialization (`bnx2x_init_hw_common()` and `bnx2x_init_hw_common_chip()`) resets blocks, initializes PXP/PXP2/endianity/ILT/DMAE/CM/QM/DORQ/BRB/PRS/storm blocks/CDU/CFC/HC/IGU/NIG, handles E2 timer errata by clearing valid ILT entries via pretend function access, enables parity and attentions, and optionally initializes shared PHY state.
- Port initialization (`bnx2x_init_hw_port()`) configures per-port block phases, BRB/PBF thresholds, parser/NIG multi-function header behavior, AEU masks, LLH mode, pause/LLFC defaults, SPIO5 fan-failure attention, and E3 PTP capability.
- Function initialization (`bnx2x_init_hw_func()`) performs PF FLR cleanup on E2+, initializes per-function blocks, fills CDU ILT context lines, configures NIC mode/searcher, enables IGU/PGLUE/CFC/PBF, clears stale PCIe/PGLUE errors, resets/clears IGU producer memory and status blocks, and probes PHY.
- Pre/post IRQ NIC initialization (`bnx2x_pre_irq_nic_init()` / `bnx2x_post_irq_nic_init()`) initializes fastpath descriptors/status blocks, Rx/Tx rings, default status block, SPQ/EQ rings, internal storm memory, PF function data, statistics, interrupts, and initial attentions.
- Queue setup (`bnx2x_setup_queue()`) drives queue state transitions from RESET to INIT to SETUP, populating HC, CDU context, Rx, Tx, pause, TPA, VLAN, FCoE, RSS/multicast, and optional tx-only CoS parameters before issuing ramrods through `bnx2x_queue_state_change()`.
- Interrupts split into fastpath and slowpath. `bnx2x_interrupt()` acknowledges the interrupt, schedules NAPI for per-queue work, delegates CNIC IRQ handling, and schedules `sp_task` for default status block attentions/events. `bnx2x_msix_sp_int()` handles the MSI-X slowpath vector similarly.
- Slowpath work (`bnx2x_sp_task()`) observes the default status block, handles asserted/deasserted attentions, processes EQ completions, acknowledges status blocks, and completes deferred AFEX MCP acknowledgements.
- Event queue processing (`bnx2x_eq_int()`) drains FW events, handles IOV/VF mailbox events, statistics completions, CFC deletes, DCB traffic stop/start, function start/stop/update, AFEX VIF lists, timesync completions, RSS, MAC/VLAN/mcast classification, and Rx mode completions.
- Link/MCP attention flow runs through `bnx2x_attn_int_*()`. MCP link/general attention reads `drv_status`, dispatches OEM/DCC, MF bandwidth, driver-info, VF-disabled, PMF, DCBX, AFEX, EEE, SVID, and periodic link events, then refreshes link status.
- Early unload/reset flow in this chunk includes queue stopping (`bnx2x_stop_queue()`), function/port reset helpers, unload request/done mailbox commands, and `bnx2x_func_wait_started()` synchronizing a PMF function back to STARTED before cleanup continues beyond this chunk.

## State and Persistence Behavior

- Persistent device state is held in `struct bnx2x`: firmware sequence numbers, flags, queues, status block indices, SPQ/EQ producers/consumers, DMAE readiness, link parameters/vars, MF config, congestion-management data, slowpath DMA memory, ILT lines, CDU contexts, statistics, CNIC data, and recovery state.
- Hardware state is persisted in device registers and storm internal memory: function enable bytes, SPQ base/producers, status block data, event ring data, congestion-management structures, Rx mode filters, LLH/NIG MF state, ILT entries, and IGU producer/consumer memory.
- Management state is exchanged through MCP shared memory mailboxes and shmem2 fields. `bnx2x_fw_command()` serializes mailbox commands with `fw_mb_mutex`, increments `fw_seq`, waits up to about five seconds for matching firmware sequence, and dumps firmware trace on timeout.
- Recovery/load state uses `BNX2X_RECOVERY_GLOB_REG` bitfields for per-engine load marks, reset-in-progress bits, and global reset state. Access is guarded by hardware locks.
- Ring state is maintained with producer/consumer indices in host memory and hardware/storm memory. SPQ and EQ free space are tracked by `atomic_t` counters (`cq_spq_left`, `eq_spq_left`) with memory barriers around producer updates and completion accounting.
- VLAN/MAC filter state is mirrored in driver objects/lists and hardware ramrod state. `bnx2x_clear_vlan_info()` marks VLAN entries as forgotten after deleting all VLANs.
- Timers and workqueues maintain periodic pulse/stats updates, slowpath deferred work, and SR-IOV tasks. `bnx2x_timer()` pulses MCP, detects stale MCP pulse deltas, updates stats, samples VF bulletin board state, and rearms itself.

## Dependencies and Integration Points

- Linux kernel subsystems: PCI/PCIe config and capabilities, netdevice/NAPI, IRQ/MSI/MSI-X, DMA coherent allocation, workqueues/timers, firmware loading, zlib decompression, RCU, mutex/spinlock/atomic/barrier primitives, VLAN and Ethernet helpers.
- Local driver modules: `bnx2x.h`, `bnx2x_init.h`, `bnx2x_init_ops.h`, `bnx2x_cmn.h`, `bnx2x_vfpf.h`, `bnx2x_dcb.h`, `bnx2x_sp.h`, and firmware headers define register maps, chip macros, state machines, ramrod formats, init operations, VFPF protocol, DCBX logic, and queue/function objects.
- Firmware/storm integration: xstorm/cstorm/tstorm/ustorm internal memories receive queue, function, status-block, SPQ, EQ, rx-mode, and congestion-management state; ramrod commands are posted on SPQ and completed via CQ/EQ.
- MCP/MFW integration: link management, load/unload mode negotiation, AFEX, DCC/OEM events, EEE, driver-info reporting, version reporting, on-chip dump metadata, fan failure policy, and shared PHY config all depend on MCP shared-memory contracts.
- CNIC/FCoE/iSCSI integration: CNIC status blocks, T2/SRC memory, CNIC callbacks, FCoE queue/statistics, iSCSI MAC/stat reporting, and L5 driver notifications are wired through `bnx2x_cnic_notify()`/`cnic_ops` and CNIC-specific queue/CID handling.
- SR-IOV/VF integration: VF-only interrupt mode checks, VF/PF mailbox EQ events, VF CID handling, VFPF MAC/queue setup fallbacks, IOV ILT/DMAE/DQ allocation/init, and VF FLR scheduling hooks are present throughout this chunk.

## Risks and Edge Cases

- DMAE commands can timeout or report PCI errors; callers usually log and may panic under `BNX2X_STOP_ON_ERROR`. DMAE also has pre-ready fallback paths with direct/indirect register writes, so init ordering is critical.
- MCP mailbox timeouts degrade to return code `0` after a firmware dump. Callers must treat ambiguous firmware responses carefully.
- Interrupt and slowpath synchronization relies on explicit barriers around `interrupt_occurred`, SPQ producer updates, EQ completion accounting, and status-block reads. Reordering can lose interrupts or desynchronize IGU state.
- Shared hardware locks and MCP access locks can fail or timeout; GPIO/SPIO, attention masks, reset registers, and PHY operations assume successful serialization but often continue after logging limited errors.
- FLR cleanup depends on usage counters reaching zero, final cleanup completion, PBF command/buffer flush, and no pending PCIe transactions. Timeout paths return busy and may dump firmware.
- Parity attentions are fatal or trigger recovery scheduling depending on build flags. `bnx2x_attn_int_deasserted()` intentionally stops normal attention handling after parity so other functions can observe the error.
- Multi-function bandwidth and AFEX flows combine shmem values, storm memory writes, link state, queue ramrods, and MCP acknowledgements. Partial ramrod failure paths often ACK MCP immediately or log, so stale VLAN/rate state is possible if FW/hardware rejects updates.
- E1/E1H/E2/E3 conditional paths are dense. Many register offsets and init actions differ by chip, port mode, interrupt block, MF mode, SR-IOV, CNIC, and FCoE support; regression risk is high when changing shared helpers.
- Allocation cleanup is centralized through `bnx2x_free_mem()`/`bnx2x_free_mem_cnic()`. Failure paths depend on all partially allocated fields being either NULL-safe or initialized before free.
- Queue setup/teardown is ramrod-state-machine driven. The tx-only CoS connections must be stopped/deleted before the primary connection, and completions must be observed to reclaim SPQ capacity.

## Test Signals

- Build coverage with relevant kernel configs: PF-only, `CONFIG_BNX2X_SRIOV`, CNIC/FCoE/iSCSI enabled, MSI-X/MSI/INTx, big-endian if supported, and `BNX2X_STOP_ON_ERROR` diagnostics.
- Probe/load smoke tests should exercise common, port, and function init phases, firmware decompression/loading, MCP `DRV_LOAD`/`UNLOAD` handshakes, status block initialization, interrupt enable, and default link reporting.
- Interrupt tests should verify fastpath NAPI scheduling, slowpath MSI-X vector handling, EQ completions, CNIC handler dispatch, and no lost interrupts under shared INTx.
- Link tests should cover link up/down attentions, PMF changes, DCBX updates, EEE acknowledgement, module-detect interrupts, dropless flow-control state, and no-MCP error paths.
- Queue tests should validate leading queue setup, multi-CoS tx-only setup, FCoE queue setup, Rx mode changes, MAC/VLAN add/delete/delete-all, multicast continuations, RSS update completion, and queue teardown.
- Recovery tests should inject or simulate FLR cleanup, parity attention, MCP assert/trace dump, fan failure/SPIO5, PGLUE/ATC/PXP/CFC/DORQ attentions, and unload with/without WoL.
- SR-IOV tests should verify VF MSI-X requirement, VF/PF mailbox EQ events, VF CID classification, VF-disabled attention handling, IOV ILT/DQ/DMAE init, and VF MAC/queue setup delegation.
- Management tests should verify `DRV_INFO` ETH/FCoE/iSCSI stats buffers, driver version shmem updates, AFEX LISTGET/LISTSET/STATSGET/VIFSET acknowledgements, OEM/DCC bandwidth and enable/disable events, and shmem2 indication release behavior.

### subset-b-004366: lines 9288-15476

# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_main.c lines 9288-15476

## Scope And Purpose

This chunk covers the latter half of `bnx2x_main.c`, including the driver paths that tear down and reset hardware, recover from parity and PCI errors, discover board/firmware/link capabilities during probe, attach the driver to Linux `net_device`/PCI/CNIC/PTP interfaces, and handle MAC/VLAN/multicast receive filtering.

The code is for Broadcom NetXtreme II `bnx2x` Ethernet devices. It is not Ceph-specific despite the mirrored source tree path. The chunk starts at the end of a preceding slow-path state transition helper, so some function bodies and type declarations are defined earlier in the file. The assigned span itself contains the main lifecycle and integration surfaces that make the device visible to Linux networking and storage-offload subsystems.

Major responsibilities in this range:

- Stop PTP and full NIC hardware state during unload.
- Execute parity/process-kill recovery using MCP, hardware locks, reset bits, and workqueue rescheduling.
- Clean up residue from a previous driver/UNDI/PXE boot environment before this driver loads.
- Read chip, shared-memory, NVRAM, PHY, multi-function, CNIC, FCoE, iSCSI, MAC, and link configuration.
- Initialize `struct bnx2x`, netdev features, PCI BAR mappings, firmware blobs, function objects, and MSI/MSI-X queue resources.
- Implement `net_device_ops` for open/close, receive mode, VLAN, MDIO, ioctl, feature validation, hardware timestamping, and SR-IOV hooks.
- Register/remove the PCI driver and handle EEH/AER-style PCI error recovery.
- Provide CNIC callbacks and queues for iSCSI/FCoE offload.
- Configure and expose PTP hardware clock and packet timestamping.

## Important APIs, Types, And Functions

Unload, reset, and recovery:

- `bnx2x_chip_cleanup()` drains Tx queues, removes MAC/VLAN/multicast filters, disables LLH/Rx mode, stops queues, stops function state, unregisters PTP, disables interrupts/NAPI/IRQs, resets hardware when PCI is online, and reports unload completion to MCP.
- `bnx2x_disable_ptp()` and `bnx2x_stop_ptp()` disable timestamp filters/registers and cancel/free pending Tx timestamp work.
- `bnx2x_disable_close_the_gate()`, `bnx2x_set_234_gates()`, `bnx2x_process_kill_chip_reset()`, `bnx2x_process_kill()`, and `bnx2x_leader_reset()` implement low-level recovery reset sequencing around PXP/IGU/HC/MISC reset registers.
- `bnx2x_parity_recover()` is the state machine for recoverable parity attention handling. It coordinates leader election, unload, waiting for other functions to go down, process-kill reset, reload, and failure escalation.
- `bnx2x_recovery_failed()` detaches the netdev, marks reset-in-progress, moves PCI power to D3hot, and records `BNX2X_RECOVERY_FAILED`.
- `bnx2x_sp_rtnl_task()` is the rtnl-protected deferred worker for parity recovery, Tx timeout reset, traffic-class setup, AFEX updates, fan-failure shutdown, VF/PF mailbox work, Rx-mode updates, hypervisor VLAN, DCBX Tx restart, management version update, SVID update, and SR-IOV enablement.

Previous-driver and boot firmware cleanup:

- `bnx2x_prev_unload()` is run during PF initialization to clear state left by a prior driver, UNDI/PXE, or failed unload. It releases stale hardware/NVRAM locks, sends unload requests to MCP, and dispatches common vs uncommon cleanup.
- `bnx2x_prev_unload_common()` closes MAC receive paths, blocks LLH filters, detects and services UNDI producers, drains BRB, resets common hardware, restores MAC registers, marks the path, and completes MCP unload.
- `bnx2x_prev_unload_uncommon()` handles function-level cleanup, including optional FLR when firmware version and bootcode capability allow it.
- `bnx2x_prev_path_*()` functions maintain the global `bnx2x_prev_list` under `bnx2x_prev_sem`, recording bus/slot/path cleanup state, UNDI markers, and EEH/AER marks.
- `bnx2x_do_flr()` sends `DRV_MSG_CODE_INITIATE_FLR` after checking chip generation, bootcode support, and pending PCI transactions.

Hardware discovery and initialization:

- `bnx2x_get_common_hwinfo()` reads chip identity, port mode, flash size, shmem/shmem2 bases, bootcode version, feature flags, boot mode, WoL capability, and part number.
- `bnx2x_init_shmem()` polls `MISC_REG_SHARED_MEM_ADDR` and shmem validity, bailing out on `0xffffffff` PCI-error reads.
- `bnx2x_get_igu_cam_info()` discovers IGU default and fastpath status-block IDs from backward-compatible mode or IGU CAM mapping memory.
- `bnx2x_get_port_hwinfo()`, `bnx2x_link_settings_supported()`, and `bnx2x_link_settings_requested()` translate shmem/NVRAM PHY and link configuration into supported/advertised capabilities, requested line speed, duplex, flow control, EEE mode, and MDIO address.
- `bnx2x_get_hwinfo()` validates register access, chooses HC vs IGU, initializes multi-function mode/submode and outer VLAN state, adjusts status block count, and gathers port/MAC/CNIC information.
- `bnx2x_init_bp()` initializes mutexes, semaphores, list heads, delayed works, hardware info, mode bitmap, per-device memory, previous-unload cleanup, TPA/dropless/DCBX settings, ring sizes, timer interval, CNIC client base, CoS count, and minimum MSI-X vector requirements.
- `bnx2x_init_dev()` enables PCI resources, maps BAR0, identifies PF number, programs netdev features and operations, configures MDIO callbacks, and sets MTU ranges.
- `bnx2x_init_one()` is the PCI probe entry point. It estimates queues/status blocks, allocates `net_device`, initializes `struct bnx2x`, maps doorbells, performs VF acquire or PF SR-IOV setup, configures interrupts, registers netdev, adds storage MAC address, and reports device/link details.

Linux network interface integration:

- `bnx2x_open()` powers the PF to D0, optionally completes pending parity recovery in open, marks recovery done, and calls `bnx2x_nic_load()`.
- `bnx2x_close()` calls `bnx2x_nic_unload()` under rtnl.
- `bnx2x_set_rx_mode()` schedules rtnl slow-path receive-mode work; `bnx2x_set_rx_mode_inner()` computes normal/promisc/allmulti/none modes, updates multicast/unicast filters or VF mailbox state, and sends storm Rx mode commands.
- `bnx2x_set_uc_list()`, `bnx2x_set_mc_list_e1x()`, `bnx2x_set_mc_list()`, `bnx2x_init_mcast_macs_list()`, and `bnx2x_free_mcast_macs_list()` manage unicast and multicast filter ramrods, using page-backed temporary multicast element groups.
- `bnx2x_vlan_rx_add_vid()`, `bnx2x_vlan_rx_kill_vid()`, `bnx2x_vlan_configure()`, `bnx2x_vlan_configure_vid_list()`, and `bnx2x_vlan_reconfigure_vid()` maintain `bp->vlan_reg`, hardware VLAN credits, and fallback `accept_any_vlan` state.
- `bnx2x_features_check()` blocks unsafe GSO packets whose GSO size plus header length can trigger firmware panic, then delegates VLAN and VXLAN feature validation.
- `bnx2x_mdio_read()`, `bnx2x_mdio_write()`, and `bnx2x_ioctl()` provide MII/MDIO access under PHY lock.
- `bnx2x_validate_addr()` verifies MAC address, sampling VF bulletin data first for VFs; `bnx2x_get_phys_port_id()` exposes the physical port ID if shmem provided it.
- `bnx2x_netdev_ops` binds all visible netdev callbacks in this span plus callbacks implemented in earlier chunks such as xmit, MTU/features changes, Tx timeout, SR-IOV VF ops, FCoE WWN, and timestamp ops.

Firmware and function objects:

- `bnx2x_check_firmware()` validates firmware section bounds, init-op offsets, and version bytes before use.
- `bnx2x_init_firmware()` requests chip-specific firmware, falls back to older v15 images, validates it, allocates endian-converted init arrays, and records storm firmware data pointers.
- `bnx2x_release_firmware()` frees converted init arrays and releases the firmware blob.
- `bnx2x_func_sp_drv` wires hardware init/reset/gunzip/firmware callbacks into function slow-path object code.
- `bnx2x__init_func_obj()` initializes DMAE resources and the function object with ramrod DMA addresses and callback table.

PTP and hardware timestamping:

- `bnx2x_register_phc()` registers a Linux PTP Hardware Clock with adjfine/adjtime/gettime/settime/enable operations.
- `bnx2x_ptp_adjfine()` computes drift direction/value/period from scaled ppm and sends `BNX2X_F_CMD_SET_TIMESYNC`.
- `bnx2x_ptp_adjtime()`, `bnx2x_ptp_gettime()`, and `bnx2x_ptp_settime()` operate on `bp->timecounter`.
- `bnx2x_ptp_task()` polls NIG Tx timestamp registers, converts cycles to ns, returns the timestamp through `skb_tstamp_tx()`, and frees `bp->ptp_tx_skb`.
- `bnx2x_set_rx_ts()` reads NIG Rx timestamp registers and writes skb hardware timestamp metadata.
- `bnx2x_cyclecounter_read()`, `bnx2x_init_cyclecounter()`, `bnx2x_send_reset_timesync_ramrod()`, `bnx2x_enable_ptp_packets()`, `bnx2x_configure_ptp_filters()`, `bnx2x_hwtstamp_set()`, `bnx2x_hwtstamp_get()`, `bnx2x_configure_ptp()`, and `bnx2x_init_ptp()` configure PHC reads, drift reset, queue PTP packet delivery, timestamp filter rules, and netdev hwtstamp ioctl state.

PCI lifecycle and error handling:

- `__bnx2x_remove()` removes storage MACs, notifies firmware, closes/unregisters netdev, removes SR-IOV, updates OS-driver state, disables MSI, handles VF release, configures wake-from-D3 on shutdown, unmaps BARs/doorbells, releases firmware, frees memory, releases PCI regions, and disables the device.
- `bnx2x_remove_one()` is the PCI remove entry point.
- `bnx2x_eeh_nic_unload()`, `bnx2x_io_error_detected()`, `bnx2x_io_slot_reset()`, and `bnx2x_io_resume()` implement PCI error recovery: detach, partial unload, mark EEH, disable/re-enable PCI, restore state, unload stale firmware state, re-run previous-unload cleanup, free runtime queues, and reload if the netdev was running.
- `bnx2x_shutdown()` detaches and removes without unregistering netdev to avoid SAN-root shutdown hangs.
- `bnx2x_pci_driver`, `bnx2x_init()`, and `bnx2x_cleanup()` register/unregister the PCI driver and global workqueues, and free `bnx2x_prev_list`.

CNIC/offload integration:

- `bnx2x_set_iscsi_eth_mac_addr()` configures the iSCSI L2 MAC object.
- `bnx2x_cnic_sp_queue()` queues CNIC KWQEs into the driver's slow-path queue; `bnx2x_cnic_sp_post()` moves queued CNIC KWQEs to SPQ as credits allow and validates iSCSI L2 context before setup.
- `bnx2x_cnic_ctl_send()` and `_bh()` call registered CNIC operations under mutex or RCU read side.
- `bnx2x_cnic_notify()` and `bnx2x_cnic_cfc_comp()` notify CNIC about driver control/completion events.
- `bnx2x_set_iscsi_eth_rx_mode()` configures accept flags for the iSCSI L2 client.
- `bnx2x_drv_ctl()` handles CNIC driver control commands for ILT writes, SPQ credits, starting/stopping iSCSI L2, L2 credit returns, ULP register/unregister capability flags, and storage-only OS driver state.
- `bnx2x_get_fc_npiv()` reads and validates the FC-NPIV table from NVRAM.
- `bnx2x_setup_cnic_irq_info()`, `bnx2x_setup_cnic_info()`, `bnx2x_register_cnic()`, `bnx2x_unregister_cnic()`, and `bnx2x_cnic_probe()` expose IRQ/status-block/context/queue callbacks and feature flags to the CNIC upper-layer driver.

## Control Flow

Normal PF probe flow starts in `bnx2x_init_one()`. The driver estimates queue and CoS dimensions from the PCI ID, allocates a multi-queue Ethernet netdev, sets PF/VF flags, stores drvdata, then calls `bnx2x_init_dev()` to enable PCI, request regions, map BAR0, set PCI master/state, identify PF number, clear indirect address registers, program netdev feature flags and operations, and set MDIO callbacks.

For PFs, `bnx2x_init_bp()` then calls `bnx2x_get_hwinfo()` before allocating driver memory. Hardware info discovery reads shmem, chip identity, IGU status-block mappings, multi-function mode, port and PHY configuration, MAC addresses, and CNIC/iSCSI/FCoE capability. After memory allocation and VPD firmware-version read, PFs initialize `bp->fw_seq` and run `bnx2x_prev_unload()` to remove stale state from firmware or a previous driver. The probe path maps doorbells, performs VF acquire if needed, initializes SR-IOV support, calculates QM CID count, chooses queue counts and interrupt mode, registers the netdev, optionally adds a SAN/FCoE MAC, and sets OS driver state disabled for normal L2 interfaces.

Opening the device enters `bnx2x_open()` under rtnl. It powers the device to D0, checks for incomplete parity recovery or pending attentions, and lets the first eligible function on an engine/chip take the leader lock and run `bnx2x_leader_reset()` if recovery can be completed at open time. If recovery is not possible it powers down and returns `-EAGAIN`; otherwise it marks recovery done and calls `bnx2x_nic_load()`.

Closing and unload flow uses `bnx2x_close()` -> `bnx2x_nic_unload()` and, in the chip cleanup portion visible here, `bnx2x_chip_cleanup()`. Cleanup first drains Tx queues, waits briefly for old Tx messages to be discarded, removes ETH/UC MACs, VLANs, multicast configuration, LLH and Rx filters, sends unload request to MCP to obtain reset scope, waits for function started state, stops ETH and CNIC queues, waits for slow-path completions, stops the function, stops/unregisters PTP, disables interrupts/NAPI/IRQs, resets hardware unless the PCI channel is offline, and reports unload done.

Parity recovery is driven by `bnx2x_sp_rtnl_task()`. When `bp->recovery_state` is not done, the worker clears pending slow-path state and calls `bnx2x_parity_recover()`. In `BNX2X_RECOVERY_INIT`, it checks parity attention, tries to become leader, sets reset-in-progress/global flags, unloads the NIC with `UNLOAD_RECOVERY`, and moves to wait. In `BNX2X_RECOVERY_WAIT`, a leader waits until all relevant functions are down, then runs `bnx2x_leader_reset()`. A non-leader waits for reset completion/global attention clearing, then attempts `bnx2x_nic_load()` and updates recoverable/unrecoverable counters.

Process-kill reset has a precise hardware ordering. `bnx2x_process_kill()` waits for PXP read queues/Tetris buffers to idle, closes gates 2/3/4, polls IGU pending writes on newer chips, clears `MISC_REG_UNPREPARED`, waits for host/PCIe queues to drain, optionally prepares MCP reset and CLP magic, prepares PXP, resets chip blocks through reset registers, clears PGLUE errors, reinitializes shmem if MCP was reset, and reopens the gates.

Receive-mode changes are deliberately deferred. `bnx2x_set_rx_mode()` only schedules `BNX2X_SP_RTNL_RX_MODE` when the device is open. `bnx2x_sp_rtnl_task()` later calls `bnx2x_set_rx_mode_inner()` under rtnl. The inner function holds `netif_addr_lock_bh()`, computes promisc/allmulti/normal, configures PF multicast and unicast filters or schedules VF mailbox updates, sets `bp->rx_mode`, honors iSCSI-only storage mode by forcing no Rx, and serializes with `BNX2X_FILTER_RX_MODE_PENDING` slow-path state.

VLAN handling keeps software state in `bp->vlan_reg`. Adding a VID allocates a `bnx2x_vlan_entry` and, if running, tries to program unconfigured entries until `bp->vlan_credit` is exhausted. If hardware programming cannot cover the list, `bp->accept_any_vlan` is raised and Rx mode is refreshed. Removing a VID deprograms hardware if it was installed, decrements `vlan_cnt`, removes the list entry, and recomputes accept-any-VLAN state.

PTP setup is split between load-time and ioctl-time. `bnx2x_init_ptp()` calls `bnx2x_configure_ptp()` to reset detection masks, enable PTP hardware, start the free-running counter, reset drift through a ramrod, reset stale timestamp buffers, initialize work and timecounter once, and leave filters disabled until user configuration. `bnx2x_hwtstamp_set()` validates requested Tx/Rx modes, records them in `bp`, calls `bnx2x_configure_ptp_filters()`, normalizes unsupported broad Rx filters to none, programs NIG LLH/TLLH masks, enables queues to deliver PTP packets, and enables PTP-to-host.

PCI error recovery follows Linux PCI error callbacks. `bnx2x_io_error_detected()` detaches the netdev, partially unloads a running NIC via `bnx2x_eeh_nic_unload()`, marks the path as EEH in the previous-unload list, disables PCI, and requests slot reset. `bnx2x_io_slot_reset()` re-enables PCI, restores config state, reinitializes shmem, clears L2 loaded capability, performs unload request/done, resets slow-path state, runs previous-unload cleanup, squeezes/free objects and memory, and marks the NIC closed. `bnx2x_io_resume()` reloads if the netdev is running and recovery state allows it, then reattaches the netdev.

CNIC control flow begins with `bnx2x_cnic_probe()`, which returns a populated `cnic_eth_dev` only if iSCSI or FCoE is enabled. `bnx2x_register_cnic()` loads CNIC resources if needed, allocates the KWQ page, initializes queue pointers/counters, stores upper-layer data, fills IRQ info, publishes `bp->cnic_ops` with RCU, and schedules management-version update. CNIC queues KWQEs through `bnx2x_cnic_sp_queue()`, and completions/credits drain pending KWQEs into SPQ through `bnx2x_cnic_sp_post()`.

## State And Persistence Behavior

Persistent driver state centers on `struct bnx2x`:

- Lifecycle state includes `bp->state`, `bp->recovery_state`, `bp->nic_stopped`, `bp->is_leader`, `bp->flags`, `bp->sp_state`, `bp->sp_rtnl_state`, `bp->port.pmf`, and OS driver state written to management firmware.
- Hardware identity/configuration includes `bp->common.chip_id`, `chip_port_mode`, `flash_size`, `shmem_base`, `shmem2_base`, `mf_cfg_base`, `bc_ver`, `hw_config`, `boot_mode`, `pf_num`, `pfid`, and `INIT_MODE_FLAGS(bp)`.
- Link/PHY state is persisted in `bp->link_params`, `bp->link_vars`, `bp->port.supported[]`, `bp->port.advertising[]`, `bp->port.link_config[]`, MDIO fields, EEE mode, flow-control requests, and feature-config flags derived from shmem/NVRAM.
- MAC/storage identity is stored in `dev->dev_addr`, `bp->phys_port_id`, `bp->cnic_eth_dev.iscsi_mac`, `bp->fip_mac`, WWN fields, `bp->mf_ext_config`, `NO_ISCSI*`/`NO_FCOE` flags, and CNIC resource limits.
- Queue/interrupt state includes `bp->igu_sb_cnt`, `igu_base_sb`, `igu_dsb_id`, `base_fw_ndsb`, `min_msix_vec_cnt`, `num_queues`, `max_cos`, `qm_cid_count`, `cnic_base_cl_id`, `doorbells`, status blocks, and IRQ arrays exposed to CNIC.
- Filter state includes `bp->rx_mode`, `bp->accept_any_vlan`, `bp->vlan_reg`, `bp->vlan_cnt`, `bp->vlan_credit`, multicast temporary lists during updates, unicast list programming, and slow-path pending bits.
- Firmware state includes `bp->firmware`, converted `init_data`, `init_ops`, `init_ops_offsets`, `iro_arr`, storm firmware data pointers, `fw_major/minor/rev/eng`, `fw_cap`, and `fw_seq`.
- PTP state includes `bp->ptp_clock_info`, `bp->ptp_clock`, `bp->cyclecounter`, `bp->timecounter`, `timecounter_init_done`, `ptp_task`, `ptp_tx_skb`, `tx_type`, `rx_filter`, `hwtstamp_ioctl_called`, and `TX_TIMESTAMPING_EN`.
- CNIC state includes `bp->cnic_eth_dev`, `cnic_enabled`, `cnic_ops`, `cnic_data`, KWQ pointers, `cnic_kwq_pending`, `cnic_spq_pending`, and SPQ credit atomics.

Hardware and firmware state is heavily persistent across ordinary function boundaries. Shared memory flags, MCP mailbox sequence numbers, reset-in-progress/global bits, driver capability flags, OS driver state, NVRAM tables, MAC/PHY reset registers, NIG PTP masks, IGU mode, LLH filters, and doorbell/register mappings remain in hardware/firmware until explicitly changed or reset. Much of this chunk exists to clean or reconcile that durable state after unload, PCI error, previous driver residue, parity attention, or boot firmware.

The global `bnx2x_prev_list` persists per module load, not per device. It records whether a bus/slot/path was already cleaned, whether an AER/EEH event marked it, and whether UNDI was detected on a port. It is protected by `bnx2x_prev_sem` and freed in module cleanup.

Synchronization is mixed by subsystem:

- rtnl protects open/close and `sp_rtnl_task` paths that interact with netdev state.
- `netif_addr_lock_bh()` protects multicast/unicast/Rx-mode list access and serializes against completion-side filter state.
- `spq_lock` protects CNIC KWQ/SPQ counters and queue pointers.
- `cnic_mutex` plus RCU protects `bp->cnic_ops`.
- PHY accesses use `bp->port.phy_mutex`.
- Firmware mailbox and management driver-info paths use mutexes initialized in `bnx2x_init_bp()`.
- Hardware reset paths use management firmware locks, leader lock, reset lock, barriers, and explicit sleeps/polls because ordering is architectural.

## Dependencies And Integration Points

Linux kernel interfaces:

- PCI core: `pci_driver`, probe/remove/shutdown callbacks, PCI error handlers, PCI config reads/writes, BAR mapping, MSI-X capability reads, power management, wake-from-D3, DMA mask setup, VPD reads, and firmware request API.
- netdev core: `alloc_etherdev_mqs()`, `register_netdev()`, `unregister_netdev()`, rtnl, carrier/device attach/detach, `net_device_ops`, feature flags, VLAN callbacks, multicast/unicast address iteration, `dev_addr_add/del()`, physical port ID, and watchdog timeout.
- workqueues/timers: global `bnx2x_wq`, `bnx2x_iov_wq`, delayed slow-path/rtnl/period/iov work, PTP work, and device timer setup/deletion.
- PTP/timecounter APIs: `ptp_clock_register()`, `ptp_clock_info`, `timecounter`, `cyclecounter`, hardware timestamp ioctl config, and skb timestamp delivery.
- CNIC upper layer: `cnic_eth_dev`, `cnic_ops`, `drv_ctl_info`, `cnic_ctl_info`, iSCSI/FCoE ULP capability flags, KWQE/SPQE queueing, status-block and interrupt metadata.
- MDIO/MII: `mdio_mii_ioctl()`, `mii_ioctl_data`, and `mii_bus`-style read/write callbacks through `bp->mdio`.
- SR-IOV/VF support: conditional hooks use `bnx2x_iov_*`, VF/PF acquire/release/update routines, VF bulletin sampling, VF MAC/VLAN/spoof/link operations, and VF mailbox Rx/multicast/VLAN updates.

Internal bnx2x dependencies from other chunks/files:

- Slow-path object APIs: `bnx2x_func_state_change()`, `bnx2x_queue_state_change()`, `bnx2x_set_mac_one()`, `bnx2x_set_vlan_one()`, `bnx2x_config_mcast()`, `bnx2x_set_storm_rx_mode()`, and `bnx2x_wait_sp_comp()`.
- Load/unload helpers: `bnx2x_nic_load()`, `bnx2x_nic_unload()`, `bnx2x_netif_stop()`, `bnx2x_free_irq()`, NAPI creation/removal, queue stop/drain/free routines, stats save/disable, and object squeeze/free routines.
- Hardware access macros: `REG_RD/WR`, `REG_RD_DMAE/WR_DMAE`, `SHMEM_RD/WR`, `SHMEM2_RD/WR`, `MF_CFG_RD/WR`, chip/port/function macros, reset-register constants, NIG/PXP/IGU/HC/GRC/MISC/PGLUE register definitions.
- Link library: `bnx2x_phy_probe()`, `bnx2x_phy_read/write()`, `bnx2x_period_func()`, `bnx2x_set_rx_filter()`, flow-control helpers, DCBX helpers, and PHY lock helpers.
- Firmware/MCP: `bnx2x_fw_command()`, load/unload request/done messages, driver capability flags in shmem2, bootcode version constants, and NVRAM read helpers.

Firmware file layout is a strict dependency. `bnx2x_init_firmware()` assumes `struct bnx2x_fw_file_hdr` section descriptors, raw init-op encoding, IRO encoding, big-endian arrays, and firmware version bytes match the chip family and selected file name.

## Risks And Edge Cases

- Reset ordering is fragile. `bnx2x_process_kill_chip_reset()` intentionally resets register 2 before register 1 to avoid QM/PXP/PGLUE deadlock. Reordering or broadening reset masks can hang DMAE or PCIe-side queues.
- Hardware polls have finite timeouts and often continue with degraded behavior. BRB drain failure in previous unload logs "hope for the best"; PXP/IGU waits return `-EAGAIN`. Tests must cover timeout paths, not only successful hardware.
- `bnx2x_init_shmem()` treats `0xffffffff` as PCI error/offline and sets `NO_MCP_FLAG`. Callers that continue to use shmem after this can crash or read garbage.
- Previous-driver cleanup crosses firmware, hardware locks, MAC Rx gating, BRB draining, and UNDI producer manipulation. Failures return `-EPROBE_DEFER`, so probe may be delayed indefinitely on persistent MF UNDI/firmware residue.
- `bnx2x_prev_list` is global and keyed by bus/slot/path. Incorrect cleanup or missed EEH marking can make later probes skip required previous-unload work or repeat it unnecessarily.
- Many flows depend on being called under rtnl. `bnx2x_parity_recover()`, open/close, PCI error flows, and CNIC start/stop paths assume serialization that is not locally asserted everywhere.
- `bnx2x_set_rx_mode_inner()` temporarily drops `netif_addr_lock_bh()` to program the unicast list because it may sleep. Concurrent address-list changes are supposed to be serialized by netdev/rtnl scheduling, but regressions here can race filter programming.
- VLAN fallback to `accept_any_vlan` is intentionally broad. Hitting `vlan_credit` exhaustion changes receive semantics and should be visible to tests that add many VLANs.
- PTP uses a single `bp->ptp_tx_skb` and asynchronous work. Cleanup must cancel work after Tx queues are drained; otherwise a Tx completion can schedule work against a canceled/unregistered PHC path. The code comments call out this ordering requirement.
- `bnx2x_hwtstamp_set()` records user configuration before programming filters. If filter programming fails, `bp->tx_type`/`rx_filter` may already reflect requested state even though hardware setup failed.
- `bnx2x_ptp_task()` polls with exponential ms sleeps and frees `ptp_tx_skb` unconditionally. Any caller must ensure only one pending timestamp skb is owned at a time.
- Firmware validation checks section bounds and init-op offsets, but converted arrays are allocated exactly as firmware-provided lengths. Malformed but bounds-valid firmware can still encode semantically bad ops.
- `bnx2x_release_firmware()` does not free `bp->iro_arr` in this span even though `bnx2x_init_firmware()` allocates it. This may be handled elsewhere or may be a leak risk to verify in surrounding chunks.
- `bnx2x_init_one()` error paths need careful resource unwinding. Doorbells, BAR mappings, firmware, VF resources, PCI regions, and netdev memory have different ownership depending on PF/VF and exact failure point.
- `__bnx2x_remove()` has different behavior for real remove vs shutdown. Shutdown deliberately avoids unregistering the netdev to avoid SAN-root hangs, so code that assumes full unregister on shutdown can break boot-from-SAN scenarios.
- CNIC KWQ/SPQ credit accounting uses `BUG_ON(bp->cnic_spq_pending < count)` and multiple counters under `spq_lock`. Bad credit returns from CNIC can panic the kernel.
- CNIC operations are RCU-published and freed after `synchronize_rcu()`. Any path that calls without RCU or mutex protection can use stale callbacks.
- Multi-function mode selection depends on shmem/mf_cfg validity, legal MAC upper bytes, legal OVLAN values, and bootcode support. Bad NVRAM can abort probe with `-EPERM`, force single-function constraints, or disable storage features.
- PF/VF conditionals are pervasive. VFs skip PF hardware discovery, use PF mailbox for VLAN/Rx mode, and doorbells come from the VF BAR/regview path. PF-only register access in VF contexts is a high-risk regression class.

## Test Signals

Build and static analysis:

- Compile with PF, VF, SR-IOV, CNIC, DCBNL, MSI-X, FCoE WWN, and PTP timestamp options enabled where available.
- Run sparse/smatch/coccinelle checks for endian conversions in firmware/NVRAM/VPD/NPIV paths, RCU use of `cnic_ops`, lock ordering, and unchecked firmware section arithmetic.
- Verify firmware load succeeds for E1, E1H, E2/E3 paths and fails cleanly for wrong versions or truncated section data.

Probe and remove:

- Probe supported PF and VF PCI IDs and verify netdev registration, BAR/doorbell mapping, queue counts, interrupt mode, link-status print, and clean remove without leaked regions or mapped IO.
- Exercise failure injection at `pci_enable_device`, region request, BAR mapping, firmware allocation, previous unload, doorbell mapping, VF acquire, SR-IOV init, interrupt setup, and `register_netdev()` to validate unwind paths.
- Boot in a kdump kernel and confirm the management-firmware ready delay is honored and TPA/GRO-HW/LRO state is reduced.

Previous unload and reset:

- Load after PXE/UNDI boot and verify `bnx2x_prev_unload()` detects UNDI, drains BRB, advances UNDI producers if needed, marks boot-from-SAN, and completes MCP unload.
- Simulate stale hardware/NVRAM locks and confirm they are released before load continues.
- Force FLR-capable and FLR-incapable uncommon unload paths across bootcode versions.
- Inject PXP/IGU/BRB timeout conditions and assert errors are reported without unsafe register access afterward.

Open, close, and recovery:

- Repeatedly open/close while traffic is active and verify Tx queues drain, filters are removed, PTP stops, interrupts/NAPI/IRQs are freed once, and unload done is sent.
- Trigger Tx timeout and observe `BNX2X_SP_RTNL_TX_TIMEOUT` unload/reload and link-down indication.
- Inject parity attentions in local and global blocks, with other functions loaded/unloaded, to verify leader election, reset-global bit handling, wait rescheduling, successful reload, and recovery counter updates.
- Validate recovery-failed path detaches the netdev, powers to D3hot, and blocks further ifup until reset/power cycle.

Network feature and filter behavior:

- Exercise promisc, allmulti, normal multicast, excessive multicast on E1, and unicast list changes while the device is open; confirm final Rx mode and programmed filters match expected fallback.
- Add VLAN IDs up to and beyond `vlan_credit`; verify hardware entries, `accept_any_vlan`, and remove paths update counts and Rx mode.
- Test GSO packets with large `gso_size` and long headers to confirm `bnx2x_features_check()` strips GSO before firmware sees an unsafe frame.
- Run MDIO read/write/ioctl operations while interface is down and up, checking lock coverage and error returns.

PTP:

- Register PHC on PTP-supported hardware and verify `gettime`, `settime`, `adjtime`, and `adjfine` while up; confirm `-ENETDOWN` while down.
- Configure hwtstamp Tx on/off and supported Rx filters, then trace NIG mask registers and queue update ramrods.
- Send timestamped PTP packets and verify exactly one Tx skb is completed/freed, fallback skip counter increments when timestamp registers never become valid, and Rx timestamps are converted from hardware cycles to ktime.
- Unload while timestamping traffic and confirm work cancellation/free ordering prevents use-after-free.

PCI error recovery:

- Inject EEH/AER recoverable errors and verify `error_detected`, `slot_reset`, and `resume` detach, unload, previous-path marking, PCI disable/enable, shmem reinitialization, runtime memory free, reload, and attach sequence.
- Inject permanent channel failure and verify `PCI_ERS_RESULT_DISCONNECT`.
- Test system shutdown with boot-from-SAN/storage-offload configuration to confirm netdev is not unregistered but hardware is removed/powered down as intended.

CNIC/storage offload:

- Probe CNIC when both iSCSI and FCoE are disabled and confirm NULL is returned.
- Register/unregister CNIC and verify KWQ allocation/free, RCU callback publication/removal, IRQ/status-block metadata, and management-version update scheduling.
- Start/stop iSCSI L2 through `DRV_CTL_START_L2_CMD`/`STOP_L2_CMD`, checking MAC object setup/removal, Rx accept flags, slow-path completion waits, and credit accounting.
- Return L2/L5 SPQ credits and ensure queued KWQEs drain without overrun or `BUG_ON`.
- Read FC-NPIV table from absent, zero-entry, valid, overlength, and NVRAM-read-failure cases.

## Cross-Chunk Notes

This chunk starts immediately after code that builds function state-update parameters, so the preceding chunk should supply the complete context for the helper ending at line 9288 and earlier slow-path object setup.

Many functions called here are implemented earlier in `bnx2x_main.c` or neighboring `bnx2x_*` files, especially load/unload internals, IRQ/NAPI allocation, Tx/Rx fastpath cleanup, DCBX, SR-IOV mailbox handling, slow-path object operations, and firmware/hardware register definitions. The final per-file report should merge this chunk with earlier chunks to present the whole driver lifecycle from module parameters and fastpath setup through this probe/remove/recovery tail.

The module entry/exit and PCI driver registration live in this chunk, but the file continues after `module_exit()` with CNIC and PTP helper functions because those helpers are still part of the same compilation unit. The final report should avoid treating `module_exit()` as the end of file behavior.
