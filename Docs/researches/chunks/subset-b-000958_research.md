# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi2/gaudi2.c lines 7350-12008

## Scope

This chunk covers the late middle and tail of the Gaudi2 ASIC implementation in the Habana Labs accelerator driver. It begins inside the queue-test support path, then covers device idle probing, compute-reset late initialization, MMU/ASID preparation, hardware event decoding, RAZWI and MMU fault reporting, HBM SEI handling, memory scrubbing, context setup/teardown, debugfs DMA reads, command-buffer generation for synchronization waits/signals, block mmap helpers, PTE accessors, and the `hl_asic_funcs` dispatch table that binds these helpers into the common driver core.

The code is not Ceph filesystem logic despite living in the `sources/distributed-fs/ceph-client` snapshot. It is Linux kernel PCI accelerator driver code for Intel/Habana Gaudi2 devices.

## Purpose

The range provides operational glue between the generic Habana Labs driver framework and Gaudi2-specific hardware blocks:

- Validates queue/QMAN execution by sending short message packets to enabled hardware queues and checking SOB completion.
- Reports whether EDMA, PDMA, NIC, MME, TPC, decoder, and rotator engines are idle, including optional per-engine diagnostic dumps and a non-idle engine bitmask.
- Reprograms Gaudi2 MMU, AXUSER, and ASID registers for user contexts after reset or context creation.
- Handles firmware event-queue entries by translating Gaudi2 event IDs into register reads, error-cause strings, notifier masks, engine captures, interrupt unmasking, and reset escalation.
- Decodes RAZWI, page-fault, access-error, ECC, HBM, PCIe, PSOC, QMAN, DMA, MME, TPC, decoder, rotator, sync-manager, and ARC event payloads.
- Scrubs SRAM and HBM using EDMA linear-DMA packets with MMU bypass and SOB completion.
- Initializes per-context internal command-buffer pools, MSI-X doorbell mappings, and user-visible sync/QMAN register state.
- Exposes debug and integration hooks through `gaudi2_funcs`, the ASIC function table consumed by common `habanalabs` code.

## Important APIs, Types, And Functions

Queue test helpers:

- `gaudi2_test_queue_hw_queue_id_to_sob_id()` maps a queue ID to the first available user SOB plus queue offset.
- `gaudi2_test_queue_clear()`, `gaudi2_test_queue_send_msg_short()`, and `gaudi2_test_queue_wait_completion()` reset a SOB, submit a `packet_msg_short`, and poll for the expected SOB value.
- `gaudi2_test_cpu_queue()` gates firmware CPU queue testing on `HW_CAP_CPU_Q`.
- `gaudi2_test_queues()` iterates enabled non-EDMA queues from `GAUDI2_QUEUE_ID_PDMA_0_0` to `GAUDI2_QUEUE_ID_CPU_PQ`, enables QMAN test mode, submits messages, runs the CPU queue test, and verifies completions.

Idle-state helpers:

- `gaudi2_get_edma_idle_status()`, `gaudi2_get_pdma_idle_status()`, `gaudi2_get_nic_idle_status()`, `gaudi2_get_mme_idle_status()`, `gaudi2_get_tpc_idle_status()`, `gaudi2_get_decoder_idle_status()`, and `gaudi2_get_rotator_idle_status()` read block-specific status registers and use macros such as `IS_QM_IDLE`, `IS_DMA_IDLE`, `IS_MME_IDLE`, `IS_TPC_IDLE`, and `IS_DEC_IDLE`.
- `gaudi2_is_tpc_engine_idle()` is the TPC iterator callback. It handles the special DCORE0 TPC6 engine-id mapping.
- `gaudi2_is_device_idle()` aggregates all engine groups and optionally fills an engine-id bitmask plus `struct engines_data` formatted status output.

Reset and MMU preparation:

- `gaudi2_compute_reset_late_init()` reinitializes ARCs, scrubs ARC DCCM, initializes security, and unmasks firmware IRQs after compute reset.
- `gaudi2_mmu_prepare()` validates the ASID, skips work when MMU capability is absent, then calls shared, TPC, and DCORE preparation paths.
- `gaudi2_mmu_shared_prepare()` programs shared PDMA, ROT, shared decoder, ARC-farm duplicate-engine, and ARC MMU state.
- `gaudi2_mmu_dcore_prepare()` programs per-DCORE EDMA, sync manager, MME, MME SBTE/WB, MME QM, and decoder AXUSER/MMU-bypass registers.
- `gaudi2_arc_mmu_prepare_all()` either delegates ASID setup to firmware for boot-CPU firmware components or programs scheduler/engine ARCs directly.
- `gaudi2_mmu_scramble_addr()` and `gaudi2_mmu_descramble_addr()` convert Gaudi2 HBM addresses between non-power-of-two DRAM page layout and 64 MiB DMMU page layout.
- `gaudi2_mmu_get_real_page_size()` chooses the host or DRAM page size accepted by the MMU mapping layer.

Event and interrupt handling:

- `gaudi2_handle_eqe()` is the central event-queue dispatcher. It decodes `event_type`, updates per-event and aggregate counters, switches over Gaudi2 event ranges, calls specialized handlers, sends notifier events, captures engine errors, optionally unmasks interrupts, and may trigger device reset.
- `gaudi2_print_event()` formats event names from `gaudi2_irq_map_table` with optional rate limiting.
- `is_info_event()` suppresses generic error printing for periodic or informational events such as NIC status, clock/power state, and ARC heartbeat.
- `event_id_to_engine_id()` maps event IDs/ranges to Gaudi2 engine IDs for `hl_capture_engine_err()`.
- `gaudi2_get_events_stat()` exposes either aggregate or current event statistics and returns the byte size.

Error decoders:

- ECC: `gaudi2_handle_ecc_event()` decodes firmware ECC payloads, with block-id printing enabled for firmware version 1.12.0 and newer.
- QMAN: `gaudi2_handle_qman_err_generic()`, `handle_lower_qman_data_on_err()`, `_gaudi2_handle_qm_sei_err()`, `gaudi2_handle_qm_sei_err()`, and `gaudi2_handle_qman_err()` decode stream/lower-QM error status, arbiter errors, undefined opcode context, SEI causes, and EDMA-specific RAZWI checks.
- RAZWI: `gaudi2_razwi_rr_hbw_shared_printf_info()`, `gaudi2_razwi_rr_lbw_shared_printf_info()`, `gaudi2_razwi_calc_engine_id()`, `gaudi2_ack_module_razwi_event_handler()`, `gaudi2_check_if_razwi_happened()`, `gaudi2_psoc_razwi_get_engines()`, `gaudi2_handle_psoc_razwi_happened()`, and `gaudi2_ack_psoc_razwi_event_handler()` translate range-register and PSOC RAZWI captures into addresses, initiators, engine IDs, and `hl_handle_razwi()` calls.
- Engine-specific handlers include `gaudi2_handle_rot_err()`, `gaudi2_tpc_ack_interrupts()`, `gaudi2_handle_dec_err()`, `gaudi2_handle_mme_err()`, `gaudi2_handle_mme_sbte_err()`, `gaudi2_handle_mme_wap_err()`, `gaudi2_handle_kdma_core_event()`, and `gaudi2_handle_dma_core_event()`.
- MMU fault handlers include `gaudi2_handle_page_error()`, `gaudi2_handle_access_error()`, `gaudi2_handle_mmu_spi_sei_generic()`, `get_hmmu_base()`, `gaudi2_handle_mmu_spi_sei_err()`, `gaudi2_get_mmu_base()`, `gaudi2_ack_mmu_error()`, and `gaudi2_ack_mmu_page_fault_or_access_error()`.
- HBM and thermal/power handlers include `gaudi2_hbm_sei_handle_read_err()`, `gaudi2_hbm_sei_print_wr_par_info()`, `gaudi2_hbm_sei_print_ca_par_info()`, `gaudi2_handle_hbm_mc_sei_err()`, `gaudi2_handle_hbm_cattrip()`, `gaudi2_handle_hbm_mc_spi()`, and `gaudi2_print_clk_change_info()`.
- PCIe/PSOC/ARC helpers include `gaudi2_print_pcie_mstr_rr_mstr_if_razwi_info()`, `gaudi2_print_pcie_addr_dec_info()`, `gaudi2_handle_pif_fatal()`, `gaudi2_handle_hif_fatal()`, `gaudi2_handle_pcie_p2p_msix()`, `gaudi2_handle_pcie_drain()`, `gaudi2_handle_psoc_drain()`, `gaudi2_print_out_of_sync_info()`, `gaudi2_print_cpu_pkt_failure_info()`, and `hl_arc_event_handle()`.

Memory and context helpers:

- `gaudi2_memset_memory_chunk_using_edma_qm()` builds a `packet_lin_dma` memset command in device memory and submits it to an EDMA queue.
- `gaudi2_memset_device_memory()` distributes up to 2 GiB chunks over enabled EDMA engines, temporarily enables MMU bypass and QMAN test mode, uses a SOB for write-completion counting, then restores EDMA context registers and clears the command-buffer storage area.
- `gaudi2_scrub_device_dram()` and `gaudi2_scrub_device_mem()` scrub HBM and SRAM when `hdev->memory_scrub` is set.
- `gaudi2_restore_user_sm_registers()`, `gaudi2_restore_user_qm_registers()`, and `gaudi2_restore_nic_qm_registers()` clear user sync-manager/QMAN state and fence counters after context or release/reset transitions.
- `gaudi2_debugfs_read_dma()` maps a coherent host buffer into a compute context, uses KDMA to read device memory in 2 MiB chunks, copies data to the debugfs blob, and tears down MMU mappings.
- `gaudi2_internal_cb_pool_init()` and `gaudi2_internal_cb_pool_fini()` allocate, map, and destroy the host-backed internal CB pool used for generated signal/wait command buffers.
- `gaudi2_ctx_init()` prepares ASID/MMU state, restores user or NIC QMAN registers, creates the internal CB pool, and maps virtual MSI-X doorbell memory for non-kernel contexts. `gaudi2_ctx_fini()` reverses the per-context allocations.

Synchronization, mmap, and function-table hooks:

- `gaudi2_pre_schedule_cs()` arms a reserved CQ monitor for command submissions that need completion.
- `gaudi2_gen_signal_cb()`, `gaudi2_add_mon_msg_short()`, `gaudi2_add_arm_monitor_pkt()`, `gaudi2_add_fence_pkt()`, and `gaudi2_gen_wait_cb()` emit Gaudi2 packet sequences for SOB signaling and monitor/fence-based waits.
- `gaudi2_reset_sob()` clears a SOB register and reinitializes the SOB kref; `gaudi2_reset_sob_group()` is a stub.
- `gaudi2_get_device_time()` reads the PSOC timestamp counter high and low registers.
- `gaudi2_get_dec_base_addr()`, `gaudi2_get_hw_block_id()`, and `gaudi2_block_mmap()` provide decoder base lookup and safe mmap of whole user-mapped MMIO blocks.
- `gaudi2_enable_events_from_fw()`, `gaudi2_get_msi_info()`, `gaudi2_map_pll_idx_to_fw_idx()`, `gaudi2_add_device_attr()`, `gaudi2_send_device_activity()`, `gaudi2_read_pte()`, and `gaudi2_write_pte()` connect firmware, sysfs, MMU, and PCI BAR operations to generic code.
- `gaudi2_state_dump_init()` registers mostly stubbed state-dump callbacks in this snapshot: monitor validation, monitor printing, sync-to-engine map generation, fence printing, SOB address lookup, stream-master QID lookup, and monitor dump are not implemented here.
- `gaudi2_funcs` is the central `struct hl_asic_funcs` instance. `gaudi2_set_asic_funcs()` installs it into `hdev->asic_funcs`.

## Control Flow

Queue self-test flow starts in `gaudi2_test_queues()` through the ASIC function table. It walks enabled, non-EDMA hardware queues, enables test mode, clears the mapped SOB, sends a short message packet, runs the CPU queue firmware test if available, polls every queue's SOB for the test value, clears each SOB, and disables test mode. A queue send or completion timeout aborts the loop and returns an error.

Idle query flow starts in `gaudi2_is_device_idle()`. It invokes each block-family checker in sequence. Each checker reads the relevant hardware status registers, combines the local idle result into a global boolean, records non-idle engine IDs in the optional mask, and appends formatted rows to the optional `engines_data` buffer. TPC iteration is abstracted through `gaudi2_iterate_tpcs()`, which lets the helper respect enabled/binned TPC topology.

Context creation flow in `gaudi2_ctx_init()` skips the kernel ASID, prepares MMU/AXUSER state for the user ASID, restores user or NIC-only register state depending on `reset_upon_device_release`, initializes the internal CB pool, and maps a reserved virtual MSI-X doorbell page. Failure after CB pool creation unwinds the pool before returning. Context finalization unmaps/free these per-context resources for user contexts.

Event flow starts when common EQ handling calls `gaudi2_handle_eqe()`. The function extracts `event_type` from the EQ entry header, bounds-checks it, increments statistics, and then switches over dense Gaudi2 event ranges. Handlers return either an error count, zero when no specific cause was found, or `GAUDI2_NA_EVENT_CAUSE` when no cause count applies. The dispatcher sets notifier bits such as `HL_NOTIFIER_EVENT_USER_ENGINE_ERR`, `HL_NOTIFIER_EVENT_GENERAL_HW_ERR`, `HL_NOTIFIER_EVENT_CRITICL_FW_ERR`, `HL_NOTIFIER_EVENT_DEVICE_RESET`, and `HL_NOTIFIER_EVENT_DEVICE_UNAVAILABLE`; captures engine errors for user-engine failures; prints fallback diagnostics when no cause was printed; unmasks non-message interrupts through firmware; sends notifier events; and conditionally requests device reset.

Reset escalation in `gaudi2_handle_eqe()` is driven by the IRQ map table's reset policy, handler-reported criticality, `reset_required`, `hdev->hard_reset_on_fw_events`, and firmware security state. Critical secure-firmware events bypass the firmware reset request and mark the device unavailable; other reset-triggering events use delayed reset. General hardware errors are escalated through `hl_handle_critical_hw_err()` before `hl_device_cond_reset()`.

RAZWI flow has two variants. Module RR RAZWI events compute a router master-interface base from module type, index, sub-index, binning state, and router-id tables, read HBW/LBW read/write happened registers, print captured addresses, call `hl_handle_razwi()`, and clear the happened bits. PSOC RAZWI flow reads PSOC mask/AXUSER data, maps AXUSER coordinates through common or MME RAZWI tables, probes the possible router capture registers, reports the address and likely engines, then clears the PSOC interrupt only in PLDM or non-Linux-firmware handling modes.

MMU fault flow reads valid bits from PMMU/HMMU error registers, reconstructs captured virtual addresses, descrambles HMMU addresses when needed, reports page or access errors, calls `hl_handle_page_fault()` for page faults, and clears valid/cause/interrupt registers. The same page/access helpers are used both from event handling and from explicit `ack_mmu_errors` table hook.

Memory scrub flow uses EDMA instead of CPU writes. It allocates an array of linear-DMA packets, reserves the beginning of user HBM as temporary command-buffer storage when the scrub target overlaps it, temporarily configures enabled EDMAs for MMU bypass and write-completion SOB signaling, submits chunks no larger than 2 GiB across enabled EDMAs, waits for the SOB to equal the number of submitted DMAs, restores EDMA registers and test mode, clears the temporary HBM CB area, resets the SOB, and frees host packet storage.

## State And Persistence Behavior

The chunk mutates hardware and driver runtime state, not filesystem state. Persistent outputs are hardware register values, in-memory driver structures, and kernel logs/notifier events.

Driver-maintained state includes:

- `gaudi2->events_stat` and `gaudi2->events_stat_aggregate`, incremented for every valid EQ event.
- `hdev->captured_err_info.undef_opcode`, filled once when lower-QM undefined opcode capture is enabled.
- `hdev->clk_throttling.current_reason`, `aggregated_reason`, and per-reason timestamps, updated on CPU power/thermal envelope events under `clk_throttling.lock`.
- `hdev->internal_cb_pool_virt_addr`, `internal_cb_pool_dma_addr`, `internal_cb_pool`, and `internal_cb_va_base`, allocated per user context and mapped through the PMMU.
- `hdev->asic_funcs`, assigned to `gaudi2_funcs` by `gaudi2_set_asic_funcs()`.
- User SOB/MON/CQ/QMAN hardware state, cleared during context setup and queue tests.

Hardware state changed by this chunk includes QMAN test mode/protection bits, EDMA MMU-bypass and write-completion registers, SOB values, monitor payload/arm registers, MMU ASID and bypass registers, ARC region configuration registers, interrupt clear/cause registers, event unmasking state, MSI-X doorbell mappings, and PTE contents in device DRAM BAR space.

Most state is transient and reset-sensitive. Several helpers deliberately restore prior state after temporary changes, such as EDMA scrubbing restoring `AXUSER_HB_MMU_BP` and clearing completion registers. Other helpers intentionally leave state configured for a context lifetime, such as ASID programming, virtual MSI-X doorbell mapping, and internal CB pool mapping.

## Dependencies And Integration Points

The code depends on the common Habana Labs driver core types and helpers: `struct hl_device`, `struct hl_ctx`, `struct hl_cs`, `struct hl_eq_entry`, `struct hl_asic_funcs`, `struct asic_fixed_properties`, `hl_hw_queue_send_cb_no_cmpl()`, `hl_poll_timeout()`, `hl_fw_*()` calls, `hl_mmu_*()` mapping/invalidation APIs, `hl_notifier_event_send_all()`, `hl_device_cond_reset()`, `hl_handle_razwi()`, `hl_handle_page_fault()`, `hl_capture_engine_err()`, `hl_check_for_glbl_errors()`, debugfs helpers, DMA allocation helpers, and sysfs attribute registration helpers.

It also depends on Gaudi2-specific generated register addresses, masks, event IDs, queue IDs, engine IDs, topology constants, router tables, RAZWI metadata tables, error-cause string arrays, QMAN base tables, ARC block base tables, and packet formats such as `packet_msg_short`, `packet_fence`, and `packet_lin_dma`. Many of those are declared earlier in `gaudi2.c`, in `gaudi2P.h`, or in generated register headers.

The main integration point is `gaudi2_funcs`. Common driver code reaches the functions in this chunk through table slots including `test_queues`, `scrub_device_mem`, `scrub_device_dram`, `update_eq_ci`, `context_switch`, `restore_phase_topology`, `debugfs_read_dma`, `handle_eqe`, `get_events_stat`, `read_pte`, `write_pte`, `is_device_idle`, `compute_reset_late_init`, `hw_queues_lock`, `hw_queues_unlock`, `get_pci_id`, `get_eeprom_data`, `ctx_init`, `ctx_fini`, `pre_schedule_cs`, `gen_signal_cb`, `gen_wait_cb`, `reset_sob`, `get_device_time`, `get_dec_base_addr`, `scramble_addr`, `descramble_addr`, `get_hw_block_id`, `hw_block_mmap`, `enable_events_from_fw`, `ack_mmu_errors`, `get_msi_info`, `map_pll_idx_to_fw_idx`, `state_dump_init`, `check_if_razwi_happened`, `mmu_get_real_page_size`, `access_dev_mem`, `set_dram_bar_base`, and `send_device_activity`.

Firmware integration is significant. The code reads firmware EQ payloads, compares firmware versions, delegates ARC ASID setup when boot-CPU firmware is present, unmask IRQs through firmware, requests EEPROM and device-activity messages through CPU queues, consumes dynamic-loader communication descriptors for CPU interrupt registration, and treats some interrupts differently depending on whether Linux firmware owns handling.

## Risks And Edge Cases

Event range mapping is high risk because most handlers derive indexes by subtracting event IDs or dividing by the delta between adjacent event constants. Any change to event enum spacing, topology constants, or binned-engine layout can route an event to the wrong register base or engine ID.

RAZWI attribution is table-driven and topology-sensitive. Incorrect router-id tables, AXUSER coordinate tables, TPC/decoder binning remapping, or NIC macro/port interpretation can report the wrong engine or miss the captured address. Some paths intentionally pass a broad set of possible engines when the AXUSER coordinate is ambiguous.

MMU address handling is sensitive to Gaudi2's HBM scrambling. Page-fault reporting descrambles HMMU addresses and masks ranges; mapping code uses a DRAM page size that may be smaller than MMU page size. Bugs here can make fault logs misleading or produce invalid page-table mappings.

`gaudi2_memset_device_memory()` temporarily changes EDMA MMU-bypass state and QMAN test mode across all enabled EDMAs. Early errors jump to cleanup, but failures during cleanup or temporary command-buffer zeroing can leave stale state or stale HBM content. The loop that clears temporary CB storage advances `i` by `sizeof(u64)` while the loop condition is `i < cb_len / sizeof(u64)`, so the number of stores depends on byte-vs-word interpretation and is worth scrutiny in later review.

The queue test path disables test mode only for queues that reached the verification loop. If send or CPU queue testing fails before the second loop completes, `done` returns without a full per-queue cleanup pass. That may be acceptable for a chip considered unusable in failure paths, but it is a behavioral edge for diagnostics.

`gaudi2_debugfs_read_dma()` has several ordered resources: compute context reference, coherent allocation, VA reservation, MMU mapping, cache invalidation, KDMA MMU-bypass/ASID mode, and cache invalidation on teardown. Error paths around MMU lock/unlock and KDMA ASID restoration are critical because a failed debug read must not leave KDMA addressing under a user ASID or leave stale MMU mappings.

Several hooks are stubs returning success, invalid queue, NULL, zero, or `-EOPNOTSUPP`: context switch, phase topology restore, collective wait support, SOB group reset, sync-to-engine map generation, monitor validation/printing, fence state dump, SOB address lookup, stream-master queue lookup, and monitor dump. Callers must tolerate missing support.

Interrupt fallback logging depends on `error_count` semantics. Handlers that return zero trigger "No error cause" messages; handlers returning `GAUDI2_NA_EVENT_CAUSE` avoid that unless the event is informational. Misusing the sentinel could either hide useful diagnostics or create noisy false alarms.

Reset policy combines event map metadata, secure-firmware criticality, firmware version behavior, and runtime `hard_reset_on_fw_events`. Small changes can affect whether an event is only reported, unmasked, escalated to notifier users, or forces a hard/delayed reset.

## Test Signals

Useful positive signals include:

- Driver probe and context creation succeed for user contexts, including MMU ASID programming, internal CB pool mapping, and virtual MSI-X doorbell mapping.
- `test_queues` completes with all enabled non-EDMA QMANs writing the expected SOB value and CPU queue firmware test passing when `HW_CAP_CPU_Q` is present.
- `is_device_idle` reports correct idle/non-idle status and engine masks for EDMA, PDMA, NIC, MME, TPC, decoder, and rotator blocks under idle hardware and under intentionally busy queues.
- Injected or firmware-reported QMAN, MMU, ECC, HBM, PCIe, PSOC, MME, TPC, decoder, rotator, DMA, ARC, sync-manager, thermal, and power events produce the expected log cause strings, notifier masks, interrupt unmask calls, engine captures, and reset behavior.
- RAZWI injection reports the expected HBW/LBW address, read/write direction, and initiator/engine mapping for module RR and PSOC paths.
- Page-fault injection reports PMMU raw addresses and HMMU descrambled ranges correctly and calls the common page-fault handler.
- Memory scrub covers SRAM and DRAM with enabled EDMA engines, observes SOB completion, restores EDMA registers, and leaves no persistent QMAN test mode.
- Debugfs DMA reads return expected bytes across 2 MiB boundaries and cleanly release context, mapping, VA reservation, and coherent memory.
- Generated signal/wait CBs have expected packet sizes, endian-converted fields, monitor payload addresses, arm-monitor parameters, and fence packet layout.

Failure signals to watch for are queue-test SOB timeouts, missing interrupt unmasking after handled events, repeated "No error cause" logs for known events, wrong engine IDs in captured errors, stale QMAN test mode after scrub/test failure, KDMA debugfs reads returning wrong data at chunk boundaries, MMU mapping failures on DRAM page-size mismatch, invalid block mmap size/address errors, and unexpected hard resets for events expected to be non-critical.
