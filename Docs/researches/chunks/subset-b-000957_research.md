# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi2/gaudi2.c lines 1-7349

## Scope

This chunk covers the opening 7,349 lines of the Gaudi2 ASIC implementation in the HabanaLabs accelerator driver. It starts with static hardware metadata, register-base lookup tables, queue/engine/event maps, error-cause catalogs, and helper declarations, then covers the first major lifecycle half of the file: fixed property setup, PCI/iATU mapping, binning/capability setup, firmware/CPU queue bring-up, software allocation, queue-manager stop/init paths, MSI-X registration, reset/halt handling, MMU initialization and invalidation, hardware init/fini, mmap, queue/ARC capability checks, CPU messaging, command-submission validation, heartbeat, and KDMA helper setup. The chunk ends inside `gaudi2_qman_set_test_mode`, so the test-queue helpers and later event/error/context paths belong to following chunks.

## Purpose

The code in this chunk is the hardware-specific backbone that lets the generic `habanalabs` driver operate a Gaudi2 device. It translates generic driver callbacks and concepts (`hl_device`, queues, completion queues, firmware loader, MMU operations, reset, interrupts, user mappings) into Gaudi2 register programming and chip topology.

Core responsibilities in this range are:

- Describe Gaudi2 topology: dcores, TPCs, MMEs, EDMAs/PDMAs/KDMA, rotators, NIC QMAN ARCs, decoder blocks, HMMUs, PMMU, sync manager objects, MSI-X vectors, queue IDs, engine IDs, and special blocks.
- Build `asic_fixed_properties` and queue properties, including SRAM/DRAM/host virtual ranges, page-table shapes, ASID count, reserved SOB/monitor/CQ ranges, interrupt counts, firmware defaults, decoder counts, and DMA masks.
- Configure hardware according to firmware/user binning masks for HBM clusters, EDMA, TPC, decoder, XBAR edge, and HMMU availability.
- Allocate per-device private state and DMA resources, including a small DMA pool, CPU-accessible DMA memory, virtual MSI-X doorbell page, queue-test messages, user-mapped block descriptors, and special-block iterator metadata.
- Bring hardware up: firmware preload parameters, CPU boot, CPU queues, CPUCP information, KDMA, PMMU/HMMU, PDMA/EDMA/TPC/MME/rotator/decoder QMANs, sync manager, timestamp, coresight, and MSI-X.
- Tear hardware down or reset it safely by stopping QMANs, halting ARCs, stalling engines, stopping decoders, disabling queues/timestamp/MSI-X, asking firmware or driver reset paths to run, and clearing capability masks for re-init.

## Important data and static maps

- Includes `gaudi2P.h`, `gaudi2_masks.h`, Gaudi2 special-block descriptions, MMU headers, packet formats, register map, async event map, and ARC packet definitions. It also depends on Linux PCI, IOMMU, hwmon, module, DMA pool, genalloc, interrupt, and VM mapping APIs through included headers.
- Defines timeout and sizing constants for reset, firmware messages, queue tests, CPU-accessible memory retry behavior, MMU cache invalidation, VDEC stop, KDMA, HBM MMU scrambling, and DMA pool block size.
- `struct gaudi2_razwi_info` plus `common_razwi_info` and `mme_razwi_info` map AXUSER/router metadata to engine IDs and names for later RAZWI diagnostics.
- `cluster_hmmu_hif_enabled_mask`, `xbar_edge_to_hbm_cluster`, and `edma_to_hbm_cluster` encode how binning one component disables or constrains HBM/HIF/HMMU clusters.
- Large static arrays map Gaudi2 enum spaces to operational data:
  - `gaudi2_qman_async_event_id` and `gaudi2_dma_core_async_event_id` map QMAN/DMA blocks to firmware async events.
  - `gaudi2_engine_id_str` and `gaudi2_queue_id_str` expose stable names for diagnostics.
  - `gaudi2_queue_id_to_engine_id`, `gaudi2_qm_blocks_bases`, `gaudi2_arc_blocks_bases`, `gaudi2_arc_dccm_bases`, `gaudi2_queue_id_to_arc_id`, `gaudi2_dma_core_blocks_bases`, `gaudi2_mme_acc_blocks_bases`, `gaudi2_tpc_cfg_blocks_bases`, `gaudi2_tpc_eml_cfg_blocks_bases`, `gaudi2_rot_blocks_bases`, and ID-conversion tables drive most queue, ARC, engine, and register selection.
  - Error-cause string tables cover QMAN, lower QMAN, ARC/CPU SEI, decoder, rotator, TPC, MME, DMA core, PMMU/HIF fatal, HBM, MMU SPI/SEI, PSOC AXI drain, and PCIe address decode causes. Most handlers are later in the file, but this chunk defines their shared decode data.
- `gaudi2_special_blocks` and skip config arrays define special-block iteration policy for security/global-error style register traversal.
- Chunk-local helper structs include `gaudi2_cache_invld_params` for MMU invalidation, `gaudi2_tpc_idle_data`, `gaudi2_tpc_mmu_data`, and `gaudi2_tpc_init_cfg_data`.

## Key APIs and functions

- `gaudi2_set_fixed_properties()` allocates and fills `hdev->asic_prop.hw_queues_props`, queue capabilities, SRAM/DRAM/host address ranges, PMMU/DMMU hop parameters, reserved interrupt/SOB/monitor/CQ ranges, firmware defaults, power defaults, and reset/feature flags. It calls `set_dram_properties` early because HMMU page-table addresses are needed before firmware CPUCP info is available.
- `gaudi2_set_dram_properties()` computes DRAM page size, total DRAM size, user/dram/DMMU ranges, HBM firmware/driver carveouts, HMMU page-table location, and EDMA PQ DRAM addresses. It includes a TLB workaround by using a page size scaled by `GAUDI2_COMPENSATE_TLB_PAGE_SIZE_FACTOR`.
- Binning functions (`gaudi2_set_tpc_binning_masks`, `gaudi2_set_dec_binning_masks`, `gaudi2_set_dram_binning_masks`, `gaudi2_set_edma_binning_masks`, `gaudi2_set_xbar_edge_enable_mask`, `gaudi2_set_cluster_binning_masks`, `gaudi2_set_binning_masks`) translate faulty-component masks into enabled masks, queue `binned` flags, replacement TPC/EDMA behavior, faulty DRAM cluster maps, and HMMU/HIF availability.
- `gaudi2_early_init()` validates BAR sizes, sets whether iATU is firmware-owned or driver-owned, initializes PCI, reads preboot status, and performs a reset if the hardware dirty marker is set.
- `gaudi2_sw_init()` allocates `struct gaudi2_device`, builds the valid hardware-event array, seeds MME LFSRs, creates DMA pools, allocates CPU-accessible DMA memory and virtual MSI-X doorbell backing, initializes user-mapped blocks and user interrupt objects, configures feature flags, PCI memory regions, special-block iterator metadata, and queue-test message buffers.
- `gaudi2_late_init()` enables PCI access through CPUCP, fetches PSOC timestamp frequency, clears HMMU page tables using KDMA if needed, builds active ARC masks from enabled queues and NIC/TPC capabilities, scrubs active ARC DCCM memory, and initializes security.
- QMAN control helpers (`gaudi2_stop_qman_common`, `gaudi2_flush_qman_common`, `gaudi2_clear_qm_fence_counters_common`, `gaudi2_qman_manual_flush_common`, `gaudi2_disable_qman_common`) perform common stop/flush/fence/disable register operations. Families such as `gaudi2_stop_dma_qmans`, `gaudi2_stop_mme_qmans`, `gaudi2_stop_tpc_qmans`, `gaudi2_stop_rot_qmans`, `gaudi2_stop_nic_qmans` and matching disable/stall routines fan these actions across enabled engines.
- MSI-X setup is split across `gaudi2_irq_name`, `gaudi2_dec_enable_msix`, `gaudi2_enable_msix`, `gaudi2_sync_irqs`, and `gaudi2_disable_msix`. It allocates the full vector table, installs completion, event queue, decoder normal/abnormal, TPC assert, unexpected error, user CQ, and EQ error handlers, applies user interrupt affinity, and unwinds in reverse on failure.
- Engine control functions (`gaudi2_set_engine_cores`, `gaudi2_set_tpc_engine_mode`, `gaudi2_set_mme_engine_mode`, `gaudi2_set_edma_engine_mode`, `gaudi2_set_engine_modes`, `gaudi2_set_engines`) expose HALT/RUN for ARC cores and STALL/RESUME for TPC/MME/EDMA engines.
- Firmware/CPU functions (`gaudi2_init_firmware_preload_params`, `gaudi2_init_firmware_loader`, `gaudi2_init_cpu`, `gaudi2_init_cpu_queues`, `gaudi2_send_cpu_message`, `gaudi2_send_heartbeat`) set register defaults for boot/preboot protocol, load/init CPU firmware, configure PF PQ/EQ/CQ buffers, signal CPU queue readiness through GIC dynamic registers, and proxy CPU messages/heartbeat through firmware helpers.
- Hardware init functions (`gaudi2_init_kdma`, `gaudi2_init_pdma`, `gaudi2_init_edma`, `gaudi2_init_sm`, `gaudi2_init_tpc`, `gaudi2_init_mme`, `gaudi2_init_rotator`, `gaudi2_init_dec`) program DMA cores, QMAN PQ/CP/PQC blocks, sync manager CQs/SOBs/monitors, MME accelerator interrupt masks/LFSR seeds, TPC config, decoder virtual MSI-X bridge controls, and capability bits.
- MMU functions (`gaudi2_mmu_update_asid_hop0_addr`, `gaudi2_mmu_send_invalidate_cache_cmd`, `gaudi2_mmu_invalidate_cache_status_poll`, `gaudi2_hmmus_invalidate_cache`, `gaudi2_mmu_invalidate_cache`, `gaudi2_mmu_invalidate_cache_range`, `gaudi2_mmu_init_common`, `gaudi2_pci_mmu_init`, `gaudi2_dcore_hmmu_init`, `gaudi2_hbm_mmu_init`, `gaudi2_mmu_init`) program PMMU/HMMU hop configuration, ASID hop0 roots, multi-page-size settings, SEI masks, bypass/enable bits, and cache invalidation commands. Range invalidation uses explicit VA start/end registers and falls back to full invalidation when start VA is zero.
- `gaudi2_hw_init()` is the top-level bring-up sequence for this chunk: mark dirty, set HBM BAR, initialize CPU/KDMA/CPU queues, refresh CPUCP/DRAM/binning info, initialize MMUs and engines, enable timestamp, coresight, and MSI-X, then flush configuration with a read.
- Reset/fini functions (`gaudi2_send_hard_reset_cmd`, `gaudi2_execute_hard_reset`, `gaudi2_execute_soft_reset`, `gaudi2_poll_btm_indication`, `gaudi2_hw_fini`, `gaudi2_halt_engines`) coordinate firmware-vs-driver reset ownership, preboot-only behavior, heartbeat reset fallbacks, RR protection during soft reset, reset polling, and capability-mask cleanup.
- User/kernel integration helpers include `gaudi2_mmap`, `gaudi2_ring_doorbell`, `gaudi2_pqe_write`, DMA allocation/pool wrappers, `gaudi2_validate_cb_address`, `gaudi2_cs_parser`, queue/ARC capability helpers, and KDMA helpers (`gaudi2_kdma_set_mmbp_asid`, `gaudi2_arm_cq_monitor`, `gaudi2_send_job_to_kdma`, `gaudi2_memset_device_lbw`).

## Control flow

Typical initialization through this chunk is:

1. `gaudi2_early_init()` calls fixed-property setup, validates PCI BAR sizes, initializes PCI/iATU assumptions, reads firmware preboot status, and resets dirty hardware if needed.
2. `gaudi2_sw_init()` allocates all driver-side Gaudi2 state and DMA resources, initializes user interrupt objects and user-mapped block metadata, configures special blocks, and prepares queue-test buffers.
3. Firmware loader setup functions seed the common firmware-loader struct with Gaudi2 images, timeouts, BAR IDs, and dynamic register defaults.
4. `gaudi2_hw_init()` marks hardware dirty, maps HBM BAR to DRAM base, initializes CPU firmware and KDMA, configures CPU queues, reads CPUCP information, updates DRAM/binning masks, initializes PMMU/HMMUs, then initializes PDMA/EDMA/SM/TPC/MME/rotator/decoder/timestamp/coresight/MSI-X.
5. `gaudi2_late_init()` enables PCI access, fetches PSOC frequency, clears HMMU page tables, enables active ARC masks according to actual initialized queues and NIC/TPC masks, scrubs DCCM for active ARCs, and applies security setup.

Reset/fini flow is deliberately staged:

1. Higher-level teardown calls `gaudi2_halt_engines()` to stop QMANs, halt ARCs, stall engines, stop decoders, optionally manual-flush NIC QMANs on soft reset, disable QMANs/timestamp, and either disable or synchronize MSI-X.
2. `gaudi2_hw_fini()` clears ARC active masks, chooses hard or soft reset, delegates to firmware or driver reset paths, waits for preboot/BTM indications if driver/hard reset applies, and clears capability masks so subsequent init can reprogram only what is invalid.
3. `gaudi2_sw_fini()` frees queue-test DMA messages, special-block metadata, virtual MSI-X doorbell memory, gen_pool, CPU-accessible coherent memory, DMA pool, and the `gaudi2_device`.

KDMA internal jobs use a local sync-manager completion path: arm a reserved SOB/monitor/CQ, program KDMA source/destination/completion registers, commit copy or memset, poll a CQ entry, clear it, advance CQ CI, and halt KDMA on timeout.

## State and persistence behavior

The persistent runtime state in this chunk is in memory and hardware registers, not files:

- `hdev->asic_prop` holds the authoritative static/derived device properties for queue count, queue descriptors, memory ranges, MMU layouts, interrupt IDs, reserved sync resources, enabled masks, firmware/security fields, and power defaults.
- `hdev->asic_specific` points to `struct gaudi2_device`, allocated in `gaudi2_sw_init`, which tracks initialized hardware capability masks (`hw_cap_initialized`, `tpc_hw_cap_initialized`, `nic_hw_cap_initialized`, `dec_hw_cap_initialized`), active ARC masks, current DRAM BAR base, queue-test message buffers, virtual MSI-X doorbell addresses, scratchpad address, event stats, random seeds, and CPUCP info callback.
- Hardware dirty state is written to `mmHW_STATE` during `gaudi2_hw_init`; early init treats dirty state as requiring reset before normal init.
- Firmware CPUCP info can overwrite user/default binning and DRAM size data. The driver then recomputes DRAM properties and binning masks.
- Capability masks are the main guard against duplicate init and are explicitly cleared on reset according to hard vs soft reset scope.
- DMA resources are lifetime-bound to software init/fini. CPU-accessible memory has a hardware-specific address constraint: all extension bits used by ARC must match across the allocated range, so allocation retries until a suitable coherent block is found.
- The virtual MSI-X doorbell uses CPU-accessible DMA memory and sync-manager monitor chains to let blocks that cannot directly write HBW completion addresses raise interrupts through LBW/SOB indirection.

## Dependencies and integration points

- Integrates with the generic HabanaLabs core through `struct hl_device`, `struct asic_fixed_properties`, `struct hw_queue_properties`, `struct hl_hw_queue`, `struct hl_cq`, `struct hl_eq`, `struct hl_cs_parser`, generic IRQ handlers, queue helpers, MMU helpers, firmware loader helpers, CPUCP helpers, and memory validation helpers.
- Depends on generated Gaudi2 register definitions and masks (`mm...`, `*_MASK`, offsets, queue/engine IDs, event IDs). Most functions are register-programming glue around `RREG32`, `WREG32`, `RMWREG32`, `FIELD_PREP`, and `hl_poll_timeout`.
- Uses Linux PCI APIs (`pci_resource_len`, `pci_resource_start`, `pci_alloc_irq_vectors`, `pci_irq_vector`, `pci_free_irq_vectors`), IRQ APIs (`request_irq`, `request_threaded_irq`, `free_irq`, `synchronize_irq`, `irq_set_affinity_and_hint`), DMA APIs (`dma_alloc_coherent`, `dma_free_coherent`, `dma_pool_create`, `dma_pool_zalloc`, `dma_pool_free`), gen_pool APIs, VM mapping APIs, and IOMMU detection.
- Firmware integration is central: preboot status, CPU init, CPU queue handoff, CPUCP handshake, CPUCP PLL/power/card/binning/DRAM info, PCI access enable/disable, soft/hard reset messages, heartbeat, and dynamic GIC scratchpad register addresses all come from or go through firmware helpers.
- Security and special-block integration is prepared here by configuring special-block metadata, skip policy, active user-mapped blocks, and late `gaudi2_init_security`.
- The chunk exposes user-facing integration through mapped decoder/ARC/ACP/NIC UMR/sync-manager blocks, user interrupts, command-buffer address validation, mmap behavior for coherent DMA buffers, and doorbell writes.

## Risks and edge cases

- Hardware topology is encoded in many parallel static arrays. Any enum reorder or missing entry can silently program the wrong register base, event ID, ARC ID, or engine mapping.
- Binning logic has tight limits: only one faulty cluster-class element is supported for several resources. Invalid masks return `-EINVAL`, but subtle firmware/user mask combinations affect HMMU availability, substitute queues, and enabled masks.
- DRAM/DMMU addressing uses a Gaudi2-specific page-size workaround and HBM address scrambling assumptions. Bugs here can corrupt page-table placement or expose invalid virtual ranges.
- Initialization order is critical. CPU queues and CPUCP info must happen before later firmware-dependent register choices; MMU init must happen before normal engine use; KDMA is needed to scrub ARC DCCM and clear HMMU page tables.
- MSI-X registration has many unwind paths. A mismatch between vector numbers, decoder relative indexes, and user interrupt indexes can leak IRQs or free with the wrong cookie.
- Reset paths differ by hard vs soft reset, firmware-vs-driver reset ownership, preboot-only firmware, PLDM, security-enabled firmware, heartbeat cause, and CPLD shutdown. Missing one condition can leave the device inaccessible or reset out of sync with firmware.
- `gaudi2_mmu_invalidate_cache_range()` subtracts one from start VA for range invalidation because hardware excludes the start register value; zero start must fall back to full invalidation to avoid underflow semantics.
- `gaudi2_send_job_to_kdma()` polls memory for completion and halts KDMA on timeout. Incorrect CQ/SOB monitor setup or stale CQ entries can create false completion or timeout behavior.
- `gaudi2_validate_cb_address()` permits host physical addresses without PMMU only when no IOMMU mapping is active. Incorrect mode detection can accept unsafe command buffers or reject valid ones.
- The chunk ends before the full test-queue implementation; `gaudi2_qman_set_test_mode()` begins but its restore path is outside this researched range.

## Test signals

Useful verification signals for this code are mostly hardware/driver integration signals:

- Probe/early init logs should show successful BAR-size validation, PCI init, preboot status read, and no unexpected dirty-state reset loop.
- `gaudi2_hw_init()` should complete with CPU init, CPU queue handshake, CPUCP info fetch, MMU init, engine/QMAN init, coresight init, and MSI-X enable without error logs.
- Binning tests should cover no-binning, one faulty HBM/EDMA/TPC/decoder/XBAR, and unsupported multi-fault masks, then verify enabled masks and binned queue flags.
- Reset tests should cover hard reset, soft reset, firmware reset, driver reset, heartbeat reset, preboot-only mode, PLDM timeouts, and dirty-state reset before init.
- MMU tests should exercise PMMU userptr invalidation, HMMU phys-pack invalidation, range invalidation including VA zero fallback, hard-reset-pending no-op, and PLDM timeout scaling.
- IRQ tests should confirm every requested vector is registered/freed with the intended handler cookie, user IRQ affinity is removed on teardown, and `gaudi2_sync_irqs()` waits all active vectors.
- KDMA tests should verify copy/memset completion through reserved SOB/monitor/CQ, CQ CI advance, timeout handling, and KDMA halt on timeout.
- Command submission parser tests should verify disabled queue rejection, SRAM/DRAM/DMMU/PMMU/HPMMU ranges, host physical fallback without IOMMU, and PMMU-required behavior for kernel-allocated CBs.
- Resource lifetime tests should confirm `gaudi2_sw_fini()` frees every allocation from `gaudi2_sw_init()` and failure paths unwind DMA pools, gen_pool, virtual MSI-X doorbell memory, special blocks, and queue-test messages.
