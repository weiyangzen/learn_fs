# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi/gaudi.c Research Chunk subset-b-000950

Scope: lines 1-8621 of `sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi/gaudi.c`.

## Purpose

This chunk is the main Gaudi ASIC implementation for the HabanaLabs accelerator driver. It binds the generic `hl_device`/`hl_asic_funcs` layer to Gaudi-specific firmware loading, PCI BAR/iATU mapping, hardware queue setup, command-submission parsing, MMU programming, memory scrubbing, event handling, reset handling, synchronization stream/collective support, and low-level diagnostic helpers.

The file is hardware-facing: most routines write or read Gaudi MMIO registers through `WREG32`, `RREG32`, `WREG32_FIELD`, `RMWREG32`, `readq`, and `writeq`, and many functions are intended to be called only by the core habanalabs driver through function pointers registered later in the file. The top comment describes the security model: host access is protected through range registers and MMU; DDR/HBM and configuration spaces use range/protection bits; MMU is always enabled; PCI DMA channels are handled specially because some driver-owned DMA work must run while the device is idle.

## Static Tables, Constants, And Types

- Firmware names are declared with `MODULE_FIRMWARE`: `gaudi-boot-fit.itb`, `gaudi-fit.itb`, and `gaudi_tpc.bin`.
- Hardware constants define reset, PLDM, queue-test, CPU-message, firmware-loader, TPC-kernel, DMA-pool, CB-pool, and HBM-scrubbing timeouts/sizes.
- `gaudi_stream_master`, `gaudi_dma_assignment`, `gaudi_cq_assignment`, and `gaudi_queue_type` encode the static queue topology. External queues are PCI DMA queues 0/1, the CPU queue is `GAUDI_QUEUE_ID_CPU_PQ`, and the remaining DMA/MME/TPC/NIC queues are internal.
- `gaudi_packet_sizes` plus `validate_packet_id()` define the packet types the command-submission parser understands.
- Interrupt and diagnostic name tables include TPC interrupt causes, QMAN error causes, QMAN arbiter error causes, sync object names, monitor names, and `gaudi_sync_manager_names`.
- `gaudi_queue_id_to_engine_id` maps queue ids to engine ids for error reporting and captured undefined-opcode diagnostics.
- `struct ecc_info_extract_params` carries the ECC block address, memory-wrapper count, and single/double-error selector for local ECC extraction.

## Initialization And Teardown Control Flow

The bring-up path is split into early, software, hardware, and late phases.

- `gaudi_set_fixed_properties()` fills `hdev->asic_prop`: queue count/properties, memory ranges, MMU layout, SRAM/HBM ranges, PCI DBI addresses, event counts, TPC mask, power defaults, CB pool sizing, MSI ids, clock PLL defaults, reset/security flags, and the host DMA mask. It derives sync-stream SOB/monitor allocations and per-queue collective mode from `get_collective_mode()`.
- `gaudi_early_init()` calls fixed-property setup, validates PCI BAR sizes, records the HBM BAR size/start, detects firmware-managed iATU/security constraints, initializes PCI, reads preboot status, and resets dirty hardware if `mmHW_STATE` reports `HL_DEVICE_HW_STATE_DIRTY`.
- `gaudi_early_fini()` frees queue properties and tears down PCI.
- `gaudi_sw_init()` allocates `struct gaudi_device`, builds the event id array from `gaudi_irq_map_table`, creates the small DMA pool, allocates CPU-accessible coherent memory with address-extension constraints, creates the CPU-accessible `gen_pool`, allocates host PQ memory for internal QMANs, initializes the queue lock, and enables driver feature flags such as sync streams, coresight, staged submission, and wait-for-multiple-CS.
- `gaudi_sw_fini()` reverses SW allocation: internal QMAN PQs, CPU-accessible pool, coherent memory, DMA pool, and `gaudi_device`.
- `gaudi_hw_init()` marks hardware dirty, fixes the HBM BAR base, initializes the device CPU, disables clock gating, enables SRAM/HBM scramblers, programs golden registers, initializes MMU/security and all QMAN families, starts the timestamp counter, enables MSI, and initializes CPU queues.
- `gaudi_late_init()` performs CPUCP info/handshake, disables unsupported NIC ports on PCI cards, enables PCI access through firmware, scrubs SRAM/HBM, fetches PSOC frequency, clears MMU page tables, loads/runs the TPC memory initialization firmware, initializes collective SOB groups, prepares ASID 1 in hardware, and sets the PLL profile.
- `gaudi_hw_fini()` only supports hard reset. It halts/asks firmware or hardware to reset depending on loaded firmware, security, and FW reset flags; configures reset registers when the driver owns the reset; waits for BTM FSM idle; clears initialized hardware-capability bits and event stats.
- `gaudi_halt_engines()` stops, stalls, disables QMANs/engines, disables timestamp, and disables MSI unless firmware reset skips engine handling.

## PCI, BAR, Firmware, And CPU Integration

- `gaudi_pci_bars_map()` maps SRAM/CFG/HBM BARs and sets `hdev->rmmio` to the CFG offset.
- `gaudi_set_hbm_bar_base()` moves inbound region 2 for the HBM BAR unless firmware owns iATU; it tracks the current base in `gaudi->hbm_bar_cur_addr`.
- `gaudi_init_iatu()` configures inbound regions for SRAM/CFG/HBM and an outbound host region when firmware has not done so.
- `gaudi_init_firmware_loader()` fills common firmware-loader state, then chooses dynamic or static loader register descriptors. The dynamic path seeds CPU communication registers until firmware descriptors are available; the static path supplies fixed status/error/version/register offsets.
- `gaudi_init_cpu()` writes the CPU PCI MSB extension when security permits, calls `hl_fw_init_cpu()`, and marks `HW_CAP_CPU`.
- `gaudi_init_cpu_queues()` programs CPU PQ, EQ, and CQ base/length registers, raises the PI-update interrupt, polls until firmware reports queue readiness, refreshes FW application security status registers, and marks `HW_CAP_CPU_Q`.
- `gaudi_send_cpu_message()`, `gaudi_send_heartbeat()`, `gaudi_cpucp_info_get()`, `gaudi_get_eeprom_data()`, and `gaudi_get_monitor_dump()` are guarded by `HW_CAP_CPU_Q` and delegate to firmware/common helpers.

## Queue And Engine Programming

The QMAN setup routines program queue base addresses, sizes, PI/CI registers, CP DMA offsets, message-base registers for sync managers, error IRQ routing, stop-on-error behavior, arbiter watchdogs, protection bits, and enable registers.

- PCI DMA: `gaudi_init_pci_dma_qmans()` maps external kernel queues, completion queue ids, MSI vectors, initializes DMA QMANs and cores, then enables PCI DMA QMANs.
- HBM DMA: `gaudi_init_hbm_dma_qmans()` configures internal host-resident PQs and lower CPs for DMA2-DMA7, then enables them.
- MME: `gaudi_init_mme_qmans()` maps logical MME queue ids to physical MME2 and MME0 QMAN blocks, configures upper and lower CPs, and enables the two master MME QMANs.
- TPC: `gaudi_init_tpc_qmans()` configures all eight TPC QMANs, lower CPs, sync-manager high address, and sets per-TPC capability bits.
- NIC: `gaudi_init_nic_qmans()` respects `hdev->nic_ports_mask`, programs each enabled NIC QMAN, handles the two-QMAN-per-macro offset pattern, and marks NIC capability bits.
- Disable/stop/stall helpers (`gaudi_disable_*_qmans`, `gaudi_stop_*_qmans`, `gaudi_*_stall`) write the expected stop, enable, and halt bits for reset/error paths.
- `gaudi_ring_doorbell()` maps every queue id to the correct PI register and writes `pi`; CPU queue doorbells also memory-barrier and trigger the PI-update interrupt.
- `gaudi_pqe_write()` copies two 64-bit words into host-memory QMAN PQEs.

## Command Submission Parsing And Patching

`gaudi_cs_parser()` routes by queue type and MMU capability:

- Internal queues use `gaudi_parse_cb_no_ext_queue()`, which checks NIC capability for NIC queues and verifies that the CB address lies in SRAM, DRAM, or PMMU address ranges.
- External queues with MMU use `gaudi_parse_cb_mmu()`: allocate a patched CB, copy the user CB, validate the copied packets, and reserve room for completion/MSI packets when needed.
- External queues without MMU use `gaudi_parse_cb_no_mmu()`: validate the user CB, pin/map user memory for DMA packets, allocate a patched CB, and rewrite DMA packets to SG-list-backed physical DMA descriptors.

Important validation behavior:

- `gaudi_validate_cb()` rejects user `MSG_PROT`, `CP_DMA`, `STOP`, and `WREG_BULK` packets. It validates packet boundaries from `gaudi_packet_sizes`, handles `LOAD_AND_EXE` with `gaudi_validate_load_and_exe_pkt()`, detects `LIN_DMA`, and computes patched CB size.
- `gaudi_validate_dma_pkt_no_mmu()` allows zero-size DMA packets and otherwise determines host direction from the queue id.
- `gaudi_pin_memory_before_cs()` pins host memory, maps it for DMA, stores it on the job userptr list, and accounts for the number of generated LIN_DMA descriptors after SG coalescing.
- `gaudi_patch_dma_packet()` coalesces adjacent SG entries up to `DMA_MAX_TRANSFER_SIZE`, preserves the user's final write-completion bit only on the last generated packet, and handles host-to-device memset specially.
- `gaudi_add_end_of_cb_packets()` appends NOP padding, a completion `MSG_PROT`, and an MSI `MSG_PROT`.

## Memory, MMU, And Context State

- `gaudi_dma_alloc_coherent()`, `gaudi_dma_free_coherent()`, `gaudi_dma_pool_zalloc()`, and `gaudi_dma_pool_free()` translate Linux DMA addresses to/from the device's host physical base by adding/subtracting `HOST_PHYS_BASE`.
- `gaudi_alloc_cpu_accessible_dma_mem()` retries coherent allocations until a CPU-accessible range has consistent high address bits for Gaudi's 40-bit device CPU addressing.
- `gaudi_alloc_internal_qmans_pq_mem()` allocates coherent PQ buffers for every internal QMAN with family-specific queue sizes.
- `gaudi_scrub_device_mem()` waits for device idle, clears user SRAM through `gaudi_memset_device_memory()`, then scrubs HBM via all DMA cores in parallel with `gaudi_scrub_device_dram()`.
- `gaudi_mmu_init()` programs each ASID's HOP0 table address, cache management page registers, cache invalidation, MMU enable/SPI mask/HOP config, and initializes `gaudi->mmu_cache_inv_pi`.
- `gaudi_mmu_invalidate_cache()` performs whole-STLB invalidation. `gaudi_mmu_invalidate_cache_range()` intentionally degrades range invalidation to full invalidation because Gaudi lacks range invalidation.
- `gaudi_mmu_update_asid_hop0_addr()` writes MMU ASID/HOP registers and polls `MMU_BUSY`.
- `gaudi_mmu_prepare()` writes ASID/MMBP fields into many DMA, TPC, MME, NIC, and trace non-secure/aruser/awuser registers after MMU init.
- `gaudi_read_pte()` and `gaudi_write_pte()` access page tables through the current HBM BAR mapping and avoid access during hard-reset-pending.
- `gaudi_internal_cb_pool_init()` allocates and maps a host internal CB pool into the user context VA space, invalidates MMU cache, and uses a `gen_pool` sized to collective CB needs. `gaudi_internal_cb_pool_fini()` unmaps, unreserves, invalidates, destroys, and frees the pool.
- `gaudi_ctx_init()` skips kernel ASID, otherwise initializes the internal CB pool and restores user registers. `gaudi_ctx_fini()` tears it down.

State persistence is split across:

- `struct gaudi_device`: capability bits, events/stat arrays, current HBM BAR address, internal QMAN backing buffers, collective properties, MMU invalidation PI, and queue lock.
- `hdev->asic_prop`: static hardware properties, firmware security/status fields, memory layout, queue properties, power defaults, and firmware/reset flags.
- `hdev` core state: queues, completion/event queues, CPU-accessible DMA memory, DMA pools, internal CB pool, clock-throttling state, reset state, and captured error info.
- Hardware registers: queue PI/CI, QMAN/core configuration, MMU tables/cache invalidation, CPU queue handshake, sync objects/monitors, timestamp counter, error-capture registers, and reset state.

## Collective And Sync Stream Support

- `get_collective_mode()` classifies external queues as masters and DMA5/TPC7/NIC queues as slaves.
- `gaudi_collective_init()` reserves aligned SOB groups, initializes `kref`s, maps SOBs to slave queues for each stream, initializes next SOB values, and computes master SOB masks from enabled NICs plus the reduction engine.
- `gaudi_collective_wait_create_jobs()` builds one master wait job plus slave jobs for enabled NICs and a DMA5/TPC7 collective engine. It validates the wait queue and engine id.
- `gaudi_collective_wait_init_cs()` links wait CS completion to the signal CS SOB, protects against signal completion races with locks, gets SOB-group refs, emits master/slave wait/signal CB fragments, handles SOB value wraparound by switching SOB groups, and releases the signal fence.
- `gaudi_gen_signal_cb()`, `gaudi_add_mon_msg_short()`, `gaudi_add_arm_monitor_pkt()`, `gaudi_add_fence_pkt()`, and the beginning of `gaudi_get_fence_addr()` generate sync-stream packets against W_S sync-manager SOB/monitor/fence resources.

## Diagnostics, Events, And Reset Decisions

- MSI support in this chunk is single-vector: `gaudi_enable_msi()` allocates one MSI vector and `gaudi_irq_handler_single()` drains all completion queues and the event queue.
- `gaudi_get_event_desc()` resolves event names through `gaudi_irq_map_table`.
- RAZWI/MMU diagnostics use `gaudi_get_razwi_initiator_name()`, DMA-specific disambiguation through DMA core error causes, `gaudi_print_and_get_razwi_info()`, and `gaudi_print_and_get_mmu_error_info()`. RAZWI/address info is forwarded to common handlers.
- ECC diagnostics use firmware-provided data where required or local register extraction through `gaudi_extract_ecc_info()` for TPC/MME blocks.
- QMAN error handling (`gaudi_handle_qman_err_generic()`, `handle_qman_data_on_err()`, `gaudi_handle_last_pqes_on_err()`) reads stream/lower-CP status, prints causes, optionally captures last PQEs and SW config stream data under stop-on-error, and records undefined-opcode context.
- HBM, TPC, NIC SEI, sync-manager SEI, clock-throttling, FW alive, packet out-of-sync, and device reset request events are decoded in `gaudi_handle_eqe()`.
- `gaudi_handle_eqe()` increments per-event and aggregate stats, builds notifier masks, unmasks recoverable interrupts, and conditionally calls `hl_device_cond_reset()`. Fatal ECC, GIC/AXI/L2/PLL, HBM fatal events, FW alive, packet queue out-of-sync, FW/device reset requests, and some RAZWI paths escalate to reset depending on security and `hard_reset_on_fw_events`.
- `gaudi_get_events_stat()` exposes current or aggregate event-stat arrays.
- `gaudi_is_device_idle()` reads DMA/TPC/MME/NIC status registers, fills an engine busy mask, and optionally formats detailed status into `struct engines_data`.

## Dependencies And Integration Points

This chunk depends heavily on:

- Gaudi private headers: `gaudiP.h`, register maps, masks, async id maps, FW interface headers, and MMU v1.1 definitions.
- Core habanalabs helpers: CB/job allocation, debugfs job registration, queue send/CI helpers, firmware messaging/handshake, DMA mapping, userptr pinning, MMU mapping, VA reservation, reset/notifier/error handlers, hwmon release, and state dump.
- Linux kernel APIs: PCI resources/MSI vectors, DMA coherent allocation and DMA pools, firmware loading, genalloc pools, spinlocks, mutexes, krefs, completions/fences, VM mmap flags, polling helpers, and rate-limited logging.
- Firmware/CPUCP protocols: CPU queue initialization, CPUCP card info, PLL info, heartbeat, EEPROM/monitor dumps, PCI access enable/disable, IRQ unmasking, and reset/halt requests.

The functions in this chunk are consumed by the final `hl_asic_funcs gaudi_funcs` table later in the same source file. The chunk also exports `gaudi_mmu_prepare_reg()` as a non-static helper visible outside this translation unit.

## Risks And Edge Cases

- Hardware register programming is order-sensitive. Reset, QMAN, MMU, iATU, security, and firmware-queue sequences rely on flush reads, sleeps, and timeout polling; small ordering changes could hang the device or leave DMA engines active.
- Security mode changes control whether the driver may touch ELBI/MC/register regions. Several paths return early under `fw_security_enabled`; tests must cover both secure and non-secure firmware.
- Address translation is easy to break: coherent DMA handles are deliberately shifted by `HOST_PHYS_BASE`, CPU-accessible memory has 40-bit MSB constraints, and HBM BAR reads/writes depend on `gaudi->hbm_bar_cur_addr`.
- CS parsing rejects privileged packet types and rewrites host DMA packets. Bugs here could allow illegal register writes, unpinned host access, wrong DMA direction, or completion/MSI corruption.
- Collective wait logic relies on SOB group `kref`s, signal-fence lifetime, stream modulo arithmetic, and wraparound handling. Races around already-completed signal CSs or SOB reset would break synchronization.
- Error paths often clear hardware causes conditionally and may trigger resets. Misclassifying an interrupt can either mask a real hardware failure or reset unnecessarily.
- Several helpers are no-ops or placeholders (`gaudi_context_switch()`, `gaudi_restore_phase_topology()`, `gaudi_pre_schedule_cs()`), so behavior may rely on generic-driver assumptions or later chunks.
- PLDM mode uses larger timeouts and smaller SRAM scrub size; timeout-sensitive tests should cover both PLDM and normal paths.
- The assigned chunk ends inside `gaudi_get_fence_addr()`, so the rest of sync wait CB generation, state dump specs, final ASIC function table, sysfs attributes, and activity reporting are outside this chunk.

## Test Signals

Useful validation signals for this chunk include:

- Probe/init tests that exercise early BAR validation, PCI/iATU setup, firmware loader selection, CPU queue handshake, MMU init, QMAN programming, MSI allocation, and late init.
- Reset tests for driver-owned hard reset, firmware-owned reset, secure firmware reset, dirty hardware reset before init, and heartbeat/FW-fatal reset causes.
- Queue tests using `gaudi_test_queues()`/`gaudi_test_queue()` and CPU queue messaging to verify QMAN0 fence completion, CPUCP queue readiness, and CI advancement.
- CS parser tests with valid mixed packets, invalid packet ids, out-of-bound packet sizes, forbidden `MSG_PROT`/`CP_DMA`/`STOP`/`WREG_BULK`, zero-size DMA, host-to-device memset, SG coalescing, and MMU vs no-MMU paths.
- Memory tests for SRAM/HBM scrubbing, MMU page-table clearing, MMU invalidation timeout behavior, PTE read/write BAR mapping, and internal CB pool map/unmap.
- Collective sync tests for master/slave job creation, disabled NIC skipping, DMA5/TPC7 engine selection, encapsulated signals, signal already completed races, SOB value wraparound, and generated wait/signal packet sizes.
- Interrupt injection or simulator tests for ECC, RAZWI, MMU page/access errors, QMAN undefined opcode, HBM SPI, TPC DEC/KRN, NIC SEI, SM SEI, clock throttling, FW alive, and packet queue out-of-sync handling.
- Idle/debugfs tests that validate `gaudi_is_device_idle()` masks/status text and `gaudi_debugfs_read_dma()` behavior when PCI DMA engines are idle vs busy.
