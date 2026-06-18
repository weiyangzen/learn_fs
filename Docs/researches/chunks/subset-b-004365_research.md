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
