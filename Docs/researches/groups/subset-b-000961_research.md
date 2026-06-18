# Research: subset-b-000961 Goya HabanaLabs Driver Files

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/goya/goya.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/goya/goya.c

## Purpose

`goya.c` is the main ASIC integration file for the HabanaLabs Goya accelerator. It binds the generic `hl_device` core to Goya-specific PCI BAR layout, firmware loading, MMU setup, DMA/MME/TPC queue programming, MSI-X handling, command-buffer validation and patching, reset/halt behavior, event handling, and ASIC function dispatch. The file is mostly low-level register programming through `RREG32`, `WREG32`, MMU helpers, firmware CPU-CP helpers, and the generic Habanalabs queue/CB/runtime APIs.

## Important APIs, Types, And Data

- `goya_set_fixed_properties()` populates `hdev->asic_prop`: queue counts/types, host/DRAM/SRAM ranges, MMU hop geometry, default DRAM page, CB pool sizing, MSI-X event IDs, firmware/reset flags, PLL defaults, power defaults, and DMA mask.
- `goya_funcs` is the central `struct hl_asic_funcs` vtable. `goya_set_asic_funcs()` installs it on `hdev`.
- Static tables include `goya_packet_sizes[]`, `goya_mmu_regs[]`, `goya_all_events[]`, IRQ names, and state-dump placeholders.
- Queue setup entry points include `goya_init_dma_qmans()`, `goya_init_mme_qmans()`, `goya_init_tpc_qmans()`, `goya_init_cpu_queues()`, `goya_ring_doorbell()`, `goya_pqe_write()`, and `goya_get_int_queue_base()`.
- Firmware/CPU integration includes `goya_init_firmware_loader()`, `goya_init_firmware_preload_params()`, `goya_load_boot_fit_to_device()`, `goya_load_firmware_to_device()`, `goya_init_cpu()`, `goya_send_cpu_message()`, `goya_send_heartbeat()`, and `goya_cpucp_info_get()`.
- MMU and memory APIs include `goya_mmu_init()`, `goya_mmu_prepare()`, `goya_mmu_add_mappings_for_device_cpu()`, `goya_mmu_remove_device_cpu_mappings()`, `goya_mmu_invalidate_cache()`, `goya_read_pte()`, `goya_write_pte()`, `goya_mmap()`, and Goya-specific coherent/DMA pool wrappers that offset host DMA addresses by `HOST_PHYS_BASE`.
- Command-submission validation and transformation lives in `goya_cs_parser()`, `goya_validate_cb()`, `goya_validate_dma_pkt_*()`, `goya_patch_dma_packet()`, `goya_patch_cb()`, and `goya_add_end_of_cb_packets()`.
- Event and interrupt handling is centered on `goya_enable_msix()`, `goya_disable_msix()`, `goya_handle_eqe()`, `goya_unmask_irq()`, `goya_unmask_irq_arr()`, `goya_get_events_stat()`, `goya_print_irq_info()`, and `goya_compute_reset_late_init()`.

## Control Flow

Initialization is staged through the generic ASIC lifecycle. `goya_early_init()` calls `goya_set_fixed_properties()`, validates SRAM/CFG and MSI-X BAR sizes, records the DRAM BAR, determines whether firmware already configured iATU, initializes PCI, reads preboot status, resets dirty hardware if needed, and warns on bad SR-IOV strap state. `goya_sw_init()` allocates `struct goya_device`, creates the small DMA pool, allocates a CPU-accessible coherent region and gen_pool, initializes queue locking, feature flags, PCI memory regions, and the delayed frequency work item.

`goya_hw_init()` performs a device read as a liveness check, marks `mmHW_STATE` dirty, boots the device CPU if configured, applies the TPC MBIST workaround, programs golden registers, remaps the DDR BAR toward MMU page tables, initializes the MMU, applies security programming, initializes external DMA queues plus internal MME/TPC queues, starts the timestamp counter, then enables MSI-X. If MSI-X enable fails, it disables internal and external queues. `goya_late_init()` fetches PSOC frequency, clears MMU page-table/default/cache-management ranges, writes the DRAM default page pattern, maps firmware and CPU-accessible memory into the kernel MMU context, initializes and tests CPU queues, fetches CPU-CP board data, updates DRAM size dependent registers, enables PCI access via firmware, and schedules automatic PLL downshift work.

Finalization mirrors the lifecycle. `goya_halt_engines()` stops queues, stalls DMA/TPC/MME engines, disables queues/timestamp, and either tears down MSI-X/MMU CPU mappings for hard reset or synchronizes IRQs for softer paths. `goya_hw_fini()` tells the CPU to halt for hard reset, sets DDR BAR/base PLL/reset bits, waits for reset deassertion, clears capability bits and event stats, and handles soft-reset capability invalidation. `goya_late_fini()` cancels delayed work and releases hwmon resources; `goya_sw_fini()` destroys pools and frees the ASIC-private object; `goya_early_fini()` frees fixed queue properties and PCI resources.

Command submission flow depends on queue type and MMU state. Internal-queue submissions in non-MMU mode only validate that the CB address is in user SRAM or DRAM. External queues in MMU mode copy the user CB into a kernel CB, validate permitted packet IDs and packet sizes, reject privileged packets, and append space for two protected completion/MSI-X messages. External queues without MMU first validate and pin host userptrs for DMA packets, calculate the patched size from scatter-gather coalescing, then emits a patched CB with one or more `PACKET_LIN_DMA` descriptors per pinned SG run. Both paths reject zero-length DMA because of hardware lockup risk and restrict host-read DMA to queue 1 due to HW-23.

Event flow starts in `goya_handle_eqe()`, which extracts the event type, bounds-checks it against `GOYA_ASYNC_EVENT_ID_SIZE`, updates per-reset and aggregate counters, prints a readable description, and chooses between hard reset, IRQ re-unmasking, MMU/RAZWI detail printing, clock throttling state updates, or firmware IRQ unmasking for out-of-sync CPU queue reports.

## State And Persistence Behavior

Driver state is held in `struct goya_device` under `hdev->asic_specific`: queue spinlock, delayed PLL work, saved MME/TPC/IC clock targets, DDR BAR current base, current and aggregate event counters, initialized hardware capability bitmask, CPU MMU mapping flag, current PLL profile, and PM management mode. Hardware programming state persists in device registers across portions of runtime until reset; `hw_cap_initialized` avoids duplicate programming and is selectively cleared after soft/hard reset. Event counters persist in memory until hard reset clears the non-aggregate counters; aggregate counters survive ordinary resets while the device object is alive.

Memory mappings include reserved DRAM layout for CPU firmware image, MMU page tables, DRAM default page, and MMU cache-management page. The CPU-accessible coherent block is mapped either as one 2 MiB page or a set of 4 KiB pages depending on physical alignment. The DDR BAR base is mutable and cached in `goya->ddr_bar_cur_addr`; PTE reads/writes assume the current BAR window covers the target address. User memory pinning for non-MMU DMA is scoped to the job parser list and is deleted on parse failure.

Power management state is managed by `goya_set_frequency()` and the delayed `goya_set_freq_to_low_job()`. Auto mode drops PLLs to low when no compute context is active; manual mode disables that automatic switching through sysfs controls implemented in `goya_hwmgr.c`.

## Dependencies And Integration Points

This file depends heavily on the common Habanalabs core in `../common/habanalabs.h`, firmware interfaces, Goya register maps and masks, MMU v1.0 definitions, Linux PCI/MSI-X, DMA mapping, gen_pool, hwmon, and kernel workqueues. It integrates with generic `hl_asic_funcs` callbacks consumed by the core driver, `hl_fw_*` CPU-CP and firmware-loader APIs, `hl_mmu_*` mapping/cache helpers, `hl_hw_queue_*` queue submission helpers, `hl_cb_*` command buffer management, debugfs job tracking, and the Linux interrupt subsystem.

`goyaP.h` supplies constants, memory maps, capability flags, `struct goya_device`, and prototypes shared with `goya_hwmgr.c` and `goya_coresight.c`. `goya_hwmgr.c` contributes `goya_set_pll_profile()` and `goya_add_device_attr()`. `goya_coresight.c` contributes `goya_debug_coresight()` and `goya_halt_coresight()`.

## Risks And Edge Cases

- Register programming order is critical: firmware CPU boot, DDR BAR remapping, MMU initialization, security programming, queue enable, and MSI-X enable have strict sequencing.
- `goya_set_ddr_bar_base()` changes a shared BAR window. PTE access and firmware/MMU initialization rely on the cached current base being correct.
- Non-MMU command-buffer parsing pins user memory and patches DMA descriptors; mistakes in SG coalescing, DMA direction, or cleanup would expose DMA corruption or leaks.
- MMU mode trusts device virtual addresses more than non-MMU mode but still blocks zero-size DMA and host reads on the wrong queue.
- `goya_stop_queue()` treats fence-timeout as non-fatal because a stuck fence means later stop checks are unreliable; this is hardware-specific and could hide partial stop failures.
- Many debug/state-dump/collective-wait/SOB/block-mmap hooks are stubs or unsupported, so generic code must tolerate zero sizes, `-EPERM`, `-EINVAL`, or `-EOPNOTSUPP`.
- Event handling can trigger hard resets for fatal firmware events depending on `hdev->hard_reset_on_fw_events`; tests must verify reset paths and IRQ unmask behavior together.
- Reset paths clear different subsets of `hw_cap_initialized`; missed bits can either skip required reinitialization or repeat unsafe register writes.

## Test Signals

Useful test signals include successful PCI BAR size validation, iATU setup, firmware/preboot status read, dirty-state reset recovery, CPU queue init/test, CPU-CP handshake and DRAM size update, MSI-X vector allocation/free, external queue fence tests via `goya_test_queues()`, correct parser rejection of privileged packet types and zero-sized DMA, DMA queue-1 restriction for host reads, MMU map/unmap and cache-invalidate behavior, event counter increments from synthetic EQEs, IRQ unmask CPU messages, hard/soft reset capability-bit transitions, and idle-state reporting for DMA/TPC/MME engines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/goya/goya.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/goya/goyaP.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/goya/goyaP.h

## Purpose

`goyaP.h` is the private header for the Goya ASIC driver implementation. It collects Goya-specific queue counts, timeout constants, memory maps, virtual-address ranges, capability bits, the ASIC-private state structure, and cross-file function prototypes used by `goya.c`, `goya_hwmgr.c`, and `goya_coresight.c`.

## Important APIs, Types, And Data

- Queue topology constants define 5 completion queues, 5 external DMA hardware queues, 1 CPU queue, 9 internal MME/TPC queues, and 6 MSI-X interrupt IDs.
- Timeout constants include QMAN fence/stop waits, CoreSight wait, and CPU communication timeout.
- Default operating constants include enabled TPC mask, high PLL default, max/default DC power, default 4 GiB DRAM size, card name, and max pending command submissions.
- DRAM layout reserves contiguous ranges for CPU firmware image, MMU page tables, the DRAM default page, and MMU cache management, with compile-time validation that driver-reserved DRAM stays below the 512 MiB user base.
- SRAM layout reserves QMAN packet queues for MME and TPC0-7, with compile-time validation against `GOYA_KMD_SRAM_RESERVED_SIZE_FROM_START`.
- Virtual address definitions separate host PMMU space, DDR DMMU space, and a fixed CPU-accessible-memory virtual address.
- `HW_CAP_*` flags track initialized hardware areas such as PLL, DDR, MME, CPU, DMA, MSI-X, CPU queue, MMU, golden registers, TPC MBIST, and TPC.
- `struct goya_work_freq` wraps delayed frequency work with its `hl_device`.
- `struct goya_device` holds the Goya-private runtime state: hardware queue lock, delayed work pointer, saved PLL clock values, DDR BAR cached base, event counters, initialized capability bitmap, CPU-MMU-mapping flag, current PLL profile, and PM management profile.
- Prototypes expose initialization, queue setup, security/error ack, doorbell/PQE/EQ operations, context switch, debugfs I2C/LED hooks, queue tests, CPU messaging, sensors, power, PLL/sysfs, CoreSight, suspend/resume, event handling, CB parser helpers, DMA pool helpers, heartbeat, time, and frequency operations.

## Control Flow

This header does not implement control flow, but it defines the contracts that shape control flow in the other Goya files. `goya.c` owns lifecycle and queue/MMU/firmware paths; `goya_hwmgr.c` implements the PLL and device attribute prototypes; `goya_coresight.c` implements debug and halt prototypes; shared helpers use `struct goya_device` through `hdev->asic_specific`.

## State And Persistence Behavior

The header declares all persistent Goya software state in `struct goya_device`. `hw_cap_initialized` is the main guard against duplicate hardware programming across init/reset phases. `events_stat` and `events_stat_aggregate` preserve per-event accounting. `ddr_bar_cur_addr` persists the current inbound DDR BAR base used by BAR-windowed register/PTE access. Clock and PM profile fields persist user/sysfs power-management choices until reset or driver teardown.

Memory-map constants encode persistent ABI expectations between host driver, device firmware, MMU, and user-visible memory ranges. Compile-time checks protect invalid queue counts, pending-CS sizing, DRAM reservation size, CPU-accessible memory size, and SRAM driver reservation layout.

## Dependencies And Integration Points

The header includes the user ABI (`habanalabs_accel.h`), firmware boot interface, common Habanalabs core header, Goya packet definitions, Goya hardware constants, async event IDs, and firmware interface definitions. It is the coupling point between Goya source files and the generic driver types such as `struct hl_device`, `struct hl_ctx`, `struct hl_cs_parser`, `struct hl_eq_entry`, `struct hl_bd`, `struct hl_debug_params`, and sensor/power enums.

## Risks And Edge Cases

- Constants here are hardware ABI: incorrect queue counts, address ranges, or timeout values can break register programming in `goya.c`.
- The compile-time assertions are important guardrails; changing memory sizes without updating firmware/MMU expectations can overlap user memory or reserved SRAM.
- The shared `struct goya_device` fields are touched from init, IRQ, sysfs, delayed work, reset, and command paths; any future field added here should consider locking and reset semantics.
- `DMA_MAX_TRANSFER_SIZE` is `U32_MAX`, which matches packet transfer-size limits and informs SG coalescing in `goya.c`.

## Test Signals

Header-level validation comes from build-time assertions, successful compilation against all Goya C files, correct struct layout use through `hdev->asic_specific`, and runtime tests that exercise each declared callback through `goya_funcs`. Changes to memory maps should be paired with queue initialization, MMU mapping, and firmware boot tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/goya/goyaP.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/goya/goya_coresight.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/goya/goya_coresight.c

## Purpose

`goya_coresight.c` implements Goya-specific debug/CoreSight programming for STM, ETF, ETR, funnel, bus monitor, and SPMU blocks. It translates generic `struct hl_debug_params` operations from the Habanalabs debug interface into direct register writes against Goya block base addresses, and provides a halt path that disables trace sinks during context/reset cleanup.

## Important APIs, Types, And Data

- Static base-address tables map debug enum indices to Goya register bases: `debug_stm_regs[]`, `debug_etf_regs[]`, `debug_funnel_regs[]`, `debug_bmon_regs[]`, and `debug_spmu_regs[]`.
- `goya_coresight_timeout()` wraps `hl_poll_timeout()` with a longer timeout under PLDM and logs the failing address/bit/direction.
- Config functions include `goya_config_stm()`, `goya_config_etf()`, `goya_config_etr()`, `goya_config_funnel()`, `goya_config_bmon()`, and `goya_config_spmu()`.
- `goya_etr_validate_address()` restricts ETR trace buffers to the device DRAM MMU virtual range.
- `goya_debug_coresight()` is the exported dispatcher used by `goya_funcs.debug_coresight`.
- `goya_halt_coresight()` disables all ETF blocks and ETR for cleanup/reset.

## Control Flow

The dispatcher examines `params->op` and calls the matching config helper. STM configuration unlocks the block, programs masks, IDs, timestamp frequency, and enable bits; disable clears masks, waits for not-busy state, and leaves the block disabled. ETF/ETR flows first unlock and detect no-op enable/disable state, flush/stop existing capture through FFCR-style bits, wait for drain/ready state, then either program sink mode and enable or clear registers and disable. ETR enable validates nonzero buffer size and checks the buffer address/size against DMMU bounds before programming the 40-bit address registers; disable can return the write pointer through `params->output`.

Funnel configuration simply unlocks and writes an enable mask. BMON configuration programs address windows, capture settings, ID routing, and a PCIe-specific workaround offset when enabled; disable restores broad masks/defaults and clears the block. SPMU enable validates 3 to 6 event types, writes event selectors, and enables counters. SPMU disable validates output space, reads event counters, overflow, and cycle count, then clears overflow state.

After every debug operation, `goya_debug_coresight()` performs a PCIe device ID register read to flush posted configuration writes. `goya_halt_coresight()` iterates all ETF indices with a zeroed `params` structure, then disables ETR and logs failures without aborting the whole halt sequence.

## State And Persistence Behavior

CoreSight state is persisted in hardware registers, not in driver-owned memory. Enable operations program capture masks, sink modes, event selectors, trace buffer addresses, IDs, and routing; disable operations clear the same register sets and may sample output counters or ETR write pointer. PLDM mode stretches timeouts by multiplying the base CoreSight timeout. The code assumes `params->input` and `params->output` point to operation-specific structs/buffers managed by the caller.

## Dependencies And Integration Points

This file depends on `goyaP.h`, Goya CoreSight enum definitions, ASIC register and mask headers, the debug UAPI, and generic register access macros. It is wired into the main ASIC vtable by `goya.c` through `.debug_coresight = goya_debug_coresight` and `.halt_coresight = goya_halt_coresight`. It also depends on ASIC properties such as `hdev->pldm`, `hdev->asic_prop.psoc_timestamp_frequency`, `hdev->asic_prop.dmmu`, and `hdev->asic_prop.fw_security_enabled`.

## Risks And Edge Cases

- Register index bounds checks are the primary protection against invalid enum input; mismatched enum/table ordering would program the wrong block.
- ETR address validation only checks DMMU virtual range and overflow; callers must ensure the backing memory is mapped and suitable for trace writes.
- `goya_config_spmu()` computes `events_num = output_arr_len - 2` before validating `output_arr_len >= 3`; because these are unsigned values, too-small buffers underflow locally before the later check. The function returns `-EINVAL`, but this ordering is fragile.
- Posted writes are flushed only once in the dispatcher; direct helper use would miss that flush.
- Disable paths often reset registers to magic constants. These values are hardware-specific and need regression coverage when registers or masks change.

## Test Signals

Tests should cover each debug op with valid and invalid `reg_idx`, missing input on enable, missing/too-small output on disable, ETR zero-size and out-of-range buffers, PLDM timeout scaling, SPMU event count bounds, ETF/ETR timeout errors, halt behavior across all ETF entries, and the final register-read flush after successful or failed configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/goya/goya_coresight.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/goya/goya_hwmgr.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/goya/goya_hwmgr.c

## Purpose

`goya_hwmgr.c` implements Goya power/clock management sysfs attributes and PLL profile programming. It exposes current and target MME/TPC/IC clocks, high PLL setting, automatic/manual PM mode, and Infineon VRM firmware version attributes through device attribute groups.

## Important APIs, Types, And Data

- `goya_set_pll_profile()` programs MME, TPC, and IC PLLs to `PLL_HIGH`, `PLL_LOW`, or saved `PLL_LAST` values through `hl_fw_set_frequency()`.
- Per-clock sysfs show/store handlers exist for `mme_clk`, `tpc_clk`, and `ic_clk`; current-frequency read-only handlers use `hl_fw_get_frequency(..., true)`.
- `pm_mng_profile_show()` and `pm_mng_profile_store()` expose `auto` and `manual` PM modes.
- `high_pll_show()` and `high_pll_store()` expose `hdev->high_pll`.
- `infineon_ver_show()` reports the CPU-CP-provided `cpucp_info.infineon_version`.
- `goya_add_device_attr()` assigns Goya clock and VRM attribute arrays into caller-provided `attribute_group` objects.

## Control Flow

Clock show handlers first call `hl_device_operational()` and then read firmware PLL frequency; negative firmware return values are forwarded as errors. Clock store handlers require an operational device, reject changes while `goya->pm_mng_profile == PM_AUTO`, parse the input with `kstrtoul()`, call `hl_fw_set_frequency()`, and cache the requested value in `goya->mme_clk`, `goya->tpc_clk`, or `goya->ic_clk`.

PM mode switching is guarded by `hdev->fpriv_list_lock`. The store path rejects profile changes while a compute context is active. Switching from manual to auto forces low PLL by setting `curr_pll_profile` to high, setting PM mode to auto, and calling `goya_set_frequency(PLL_LOW)`. Switching from auto to manual sets PM mode under the lock, releases the lock, flushes the delayed frequency work if it exists, and returns so the caller knows auto work is no longer racing frequency changes. Unknown values return `-EINVAL`.

`goya_set_pll_profile()` itself is a direct firmware-programming helper and intentionally returns early if `hdev->pdev` is missing. `PLL_LAST` restores saved per-domain clock values from `struct goya_device`.

## State And Persistence Behavior

Stored target clock values persist in `struct goya_device` fields and are used by `PLL_LAST`. `hdev->high_pll` is mutable through sysfs and used by high-profile programming. `goya->pm_mng_profile` controls whether users may directly write clock attributes, and `goya->curr_pll_profile` tracks the last auto profile to avoid redundant changes in `goya_set_frequency()`. The PM mode transition explicitly synchronizes with delayed PLL work to avoid background auto downshift after entering manual mode.

## Dependencies And Integration Points

This file depends on `goyaP.h`, the common firmware frequency helpers `hl_fw_set_frequency()` and `hl_fw_get_frequency()`, operational-state checks, `dev_get_drvdata()`, sysfs `DEVICE_ATTR_*` macros, `kstrtoul()`, `hdev->fpriv_list_lock`, `hdev->is_compute_ctx_active`, and CPU-CP info populated by `goya_cpucp_info_get()`. The attribute groups are installed by the generic driver through `goya_funcs.add_device_attr`.

## Risks And Edge Cases

- Store handlers ignore return status from `hl_fw_set_frequency()`, so firmware programming failures can still update cached clock values and return the original byte count.
- `kstrtoul()` writes into a `long value` variable despite expecting an `unsigned long *`-style destination; this relies on compatible representation and should be treated carefully in type-cleanup work.
- `strncmp("auto", buf, strlen("auto"))` and equivalent manual parsing accept prefixed values such as `automatic`; this may be intentional sysfs leniency but is not strict.
- PM mode switching must avoid deadlock with the delayed work item, hence the manual-mode path releases `fpriv_list_lock` before flushing delayed work.
- The clock write path is blocked in auto mode but not otherwise range-checked; firmware must reject unsupported PLL values.

## Test Signals

Tests should exercise operational and non-operational sysfs reads/writes, invalid numeric input, manual-vs-auto write permission, PM mode changes with and without active compute context, delayed work flushing on auto-to-manual transition, `PLL_HIGH`/`PLL_LOW`/`PLL_LAST` programming calls, high PLL mutation, and Infineon version formatting after CPU-CP info is fetched.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/goya/goya_hwmgr.c -->
