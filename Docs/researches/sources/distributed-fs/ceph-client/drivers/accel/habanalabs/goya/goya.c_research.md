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
