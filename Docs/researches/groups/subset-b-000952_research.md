# Research: subset-b-000952

Grouped research for Gaudi private ASIC definitions and Gaudi CoreSight debug support under `sources/distributed-fs/ceph-client`. Each section preserves the source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi/gaudiP.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi/gaudiP.h

## Purpose
`gaudiP.h` is the private Gaudi ASIC contract used by the HabanaLabs accelerator driver implementation. It centralizes Gaudi-specific queue counts, DMA/MME/TPC/NIC topology constants, memory-map reservations, address-space limits, register-offset arithmetic, hardware capability bits, masks for enabled engines, collective synchronization bookkeeping types, internal QMAN persistent-queue allocation metadata, and the private `struct gaudi_device` hung off `hdev->asic_specific`. It also declares a few Gaudi-private entry points used across implementation files, including the CoreSight debug hooks implemented in `gaudi_coresight.c`.

## Important APIs, types, and functions
- Queue topology macros define the hardware queue model: `NUMBER_OF_EXT_HW_QUEUES`, `NUMBER_OF_CMPLT_QUEUES`, `NUMBER_OF_CPU_HW_QUEUES`, `NUMBER_OF_INT_HW_QUEUES`, `NUMBER_OF_HW_QUEUES`, `QMAN_STREAMS`, `NUMBER_OF_COLLECTIVE_QUEUES`, and `GAUDI_STREAM_MASTER_ARR_SIZE`.
- Engine and queue resource macros define DMA, MME, TPC, NIC, SOB, monitor, and internal QMAN sizing, including `DMA_NUMBER_OF_CHNLS`, `MME_NUMBER_OF_ENGINES`, `MME_NUMBER_OF_QMANS`, `NUM_OF_SOB_IN_BLOCK`, `NUM_OF_MONITORS_IN_BLOCK`, `MONITOR_MAX_SOBS`, and queue persistent-queue sizes such as `HBM_DMA_QMAN_SIZE_IN_BYTES`.
- Memory-map macros reserve device DRAM regions for firmware and driver-owned MMU support: `CPU_FW_IMAGE_ADDR`, `MMU_PAGE_TABLES_ADDR`, `MMU_CACHE_MNG_ADDR`, `DRAM_DRIVER_END_ADDR`, and `DRAM_BASE_ADDR_USER`. The compile-time assertion prevents driver reservations from exceeding the 512 MB boundary.
- Virtual-address macros define host VA space exposed through the device MMU: `VA_HOST_SPACE_START`, `VA_HOST_SPACE_END`, `VA_HOST_SPACE_SIZE`, and `HOST_SPACE_INTERNAL_CB_SZ`.
- Hardware capability bits such as `HW_CAP_PLL`, `HW_CAP_HBM`, `HW_CAP_MMU`, `HW_CAP_MME`, `HW_CAP_CPU`, DMA bits, MSI, scramblers, `HW_CAP_NIC_MASK`, and `HW_CAP_TPC_MASK` are the shared readiness map used by init, reset, validation, and debug paths.
- Address conversion helpers `GAUDI_CPU_PCI_MSB_ADDR()`, `GAUDI_PCI_TO_CPU_ADDR()`, and `GAUDI_CPU_TO_PCI_ADDR()` encode/decode the Gaudi 50-bit PCI/CPU address extension convention.
- `enum gaudi_dma_channels`, `enum gaudi_tpc_mask`, and `enum gaudi_nic_mask` provide stable channel and engine-bit names for DMA/TPC/NIC handling.
- `struct gaudi_hw_sob_group` tracks one reserved hardware SOB group, its owning device, refcount, base SOB id, and waiting queue.
- `struct gaudi_collective_properties` stores all collective SOB groups plus per-stream next/current group state and precomputed master monitor SOB masks.
- `struct gaudi_internal_qman_info` records a kernel virtual address, DMA address, and size for an internal QMAN persistent queue allocated in host coherent memory.
- `struct gaudi_device` is the private per-device object containing the CPU-CP info callback, a legacy hardware queue spinlock, `internal_qmans[]`, collective properties, current HBM BAR address, event id/stat arrays, the hardware capability initialized bitmap, and MMU cache invalidation producer index.
- Declared cross-file functions include `gaudi_init_security()`, `gaudi_ack_protection_bits_errors()`, `gaudi_debug_coresight()`, `gaudi_halt_coresight()`, and `gaudi_mmu_prepare_reg()`.

## Control flow
This header does not execute control flow itself, but it shapes most Gaudi driver control paths. During software initialization, `gaudi_sw_init()` allocates `struct gaudi_device`, assigns it to `hdev->asic_specific`, sets `cpucp_info_get`, allocates internal QMAN persistent-queue memory into `internal_qmans[]`, initializes `hw_queues_lock`, and advertises capabilities such as CoreSight support. Hardware initialization code sets and clears `hw_cap_initialized` bits as PLL, memory, MMU, DMA, MME, TPC, NIC, MSI, CPU, and CPU queue components become available or are reset.

Collective command-submission paths use `struct gaudi_collective_properties` to map reserved SOB groups onto NIC queues plus the single collective engine resource shared by DMA5/TPC7. The kref in each `gaudi_hw_sob_group` lets queue users release a group and trigger hardware SOB reset when the reference count drops to zero. Internal QMAN initialization paths consult the queue sizing macros in this header when allocating host PQ buffers and programming queue bases. Debug ioctl control reaches the prototypes in this header via `gaudi_debug_coresight()` and `gaudi_halt_coresight()` after the common driver has entered debug mode.

## State and persistence
The primary persistent state introduced here is `struct gaudi_device`, which lives for the lifetime of the `hl_device` software initialization and is freed during Gaudi software teardown. Its `events[]` array is initialized from the Gaudi IRQ map; `events_stat[]` is resettable event histogram state; `events_stat_aggregate[]` survives normal resets as an aggregate histogram. `hw_cap_initialized` is persistent but intentionally reset-sensitive: each engine bit is set only after a hardware block is initialized and is cleared when that block is reset or torn down. `mmu_cache_inv_pi` is an 8-bit producer index because the hardware MMU cache invalidation queue expects that width.

The internal QMAN PQ pointers are persistent coherent-DMA allocations owned by the driver, freed in `gaudi_sw_fini()`. Collective SOB group state persists across submissions and is reset through kref release callbacks and collective init. The header's memory-map constants also encode persistent layout contracts with firmware, MMU page tables, and user-visible DRAM base addresses; changing them can alter ABI-like expectations between the driver, firmware, and hardware.

## Dependencies and integration points
The header depends on common HabanaLabs driver types from `../common/habanalabs.h`, the DRM uAPI header `uapi/drm/habanalabs_accel.h`, boot interface definitions, Gaudi packet and firmware interfaces, Gaudi register-derived base macros, and Linux kernel helpers such as `BIT`, `GENMASK`, `dma_addr_t`, `spinlock_t`, and `kref`. Many constants are expressed in terms of generated register map symbols such as `mmDMA1_QM_BASE`, `mmTPC1_QM_BASE`, `mmSYNC_MNGR_*`, `mmHBM*_BASE`, and `CFG_BASE`, so generated ASIC register headers are part of the contract.

Important consumers are `gaudi.c` for initialization, reset, queue setup, collective sync, MMU, events, and hardware capability handling; `gaudi_coresight.c` for CoreSight timeout and MMU capability checks; MMU code for `gaudi_mmu_prepare_reg()`; and common ioctl/device paths through the `hdev->asic_funcs` callbacks. Userspace sees these internals indirectly via queue behavior, debug mode/CoreSight ioctls, memory mapping limits, and event reporting.

## Risks and edge cases
- Hardware capability bits are tightly packed in a 32-bit field. NIC bits occupy 14-23 and TPC bits occupy 24-31, leaving no room for additional high-numbered capabilities without widening or reorganizing the bitmap.
- Register-offset macros assume generated register bases are correct and monotonically laid out per block. A bad generated base or a mismatched ASIC revision can make queue, DMA, TPC, SIF/NIF, MME, or SRAM offset arithmetic silently program the wrong block.
- DRAM reservation constants are guarded only by a compile-time size check. Firmware, MMU table, or cache-management growth can collide with user DRAM if the layout is changed without updating all parties.
- `GAUDI_PCI_TO_CPU_ADDR()` and `GAUDI_CPU_TO_PCI_ADDR()` rewrite bits 49:39 in place. Callers must pass mutable 64-bit address variables and must preserve the correct extension value, especially when security mode changes address interpretation.
- Collective SOB refcount handling must match command-submission ownership. Premature release can reset hardware SOBs still observed by queues; missing release can pin collective groups and stall future reuse.
- Internal QMAN arrays are sized by `GAUDI_QUEUE_ID_SIZE` even though only a sparse subset is used. Queue-id drift between generated ids and driver allocation/programming code can index valid memory with semantically wrong queue data.
- The private header is included broadly, so changes to topology macros or `struct gaudi_device` layout have a large rebuild and behavior surface.

## Test signals
Useful validation includes Gaudi driver probe/remove and reset tests, successful initialization logs through PLL/HBM/MMU/DMA/MME/TPC/NIC/CPU/MSI stages, command submission on external and internal queues, collective operations using NIC queues plus DMA5/TPC7, MMU map/unmap and cache invalidation flows, and debug-mode CoreSight operations. Strong failure signals include event-array overflow during `gaudi_sw_init()`, DMA coherent allocation failures for internal QMAN PQs, queue initialization errors tied to `internal_qmans[]`, collective SOB overflow/underflow or stuck collective waits, invalid MMU/DRAM/SRAM address rejection, and logs indicating a hardware capability bit was not initialized when a path attempted to use that engine.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi/gaudiP.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi/gaudi_coresight.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi/gaudi_coresight.c

## Purpose
`gaudi_coresight.c` implements the Gaudi ASIC-specific CoreSight debug backend behind the common HabanaLabs `HL_DEBUG` ioctl. It maps userspace-visible Gaudi CoreSight register indices to ASIC register bases and programs STM trace sources, ETF trace buffers, the PSOC ETR sink, funnels, bus monitors, and SPMU performance counters. It also provides the halt path used when leaving debug mode so trace sinks are stopped before the device returns to normal operation.

## Important APIs, types, and functions
- Static base-register maps `debug_stm_regs[]`, `debug_etf_regs[]`, `debug_funnel_regs[]`, `debug_bmon_regs[]`, and `debug_spmu_regs[]` translate enum indices from `include/gaudi/gaudi_coresight.h` into generated Gaudi register base addresses.
- `SPMU_SECTION_SIZE`, `SPMU_EVENT_TYPES_OFFSET`, and `SPMU_MAX_COUNTERS` define local SPMU programming limits. In this file `SPMU_MAX_COUNTERS` is six.
- `gaudi_coresight_timeout()` wraps `hl_poll_timeout()` for CoreSight ready/stop bits with `CORESIGHT_TIMEOUT_USEC` from `gaudiP.h`. It logs address, bit position, and expected direction and returns `-EFAULT` on timeout.
- `gaudi_config_stm()` unlocks and enables/disables a selected STM block using `struct hl_debug_params_stm` masks, id, and frequency. It uses the device PSOC timestamp frequency when available and contains a DMA-channel STM workaround for hardware bug SW-2176.
- `gaudi_config_etf()` enables/disables a selected ETF buffer using `struct hl_debug_params_etf`, flushes/stops the formatter, waits for completion/status bits, then programs watermark, sink mode, formatter control, prescaler, and control registers.
- `gaudi_etr_validate_address()` validates an ETR output buffer against Gaudi address width and against host PMMU, device DRAM, or SRAM ranges. It also reports whether the address is host-backed so ETR AXI write burst programming can be adjusted.
- `gaudi_config_etr()` programs or disables the PSOC ETR sink. On enable it validates `struct hl_debug_params_etr`, writes the 50-bit trace address split across global MSB and ETR DBA registers, configures buffer size/mode/watermark/AXI attributes, and starts capture. On disable it clears ETR registers and, when an output buffer is provided, returns the current write pointer.
- `gaudi_config_funnel()` unlocks a selected funnel and writes either all relevant input enables (`0x33F`) or zero.
- `gaudi_config_bmon()` configures a selected bus monitor with two address windows, masks, bandwidth window, capture mode, and event id, or restores disabled defaults.
- `gaudi_config_spmu()` programs SPMU event type registers and counter enable state, or on disable copies counter values, overflow status, and 64-bit cycle count into the caller's output array and clears overflow status.
- `gaudi_debug_coresight()` is the public ASIC callback. It dispatches on `params->op` for `HL_DEBUG_OP_STM`, `ETF`, `ETR`, `FUNNEL`, `BMON`, `SPMU`, and deprecated `TIMESTAMP`, then reads `mmHW_STATE` to flush posted register writes.
- `gaudi_halt_coresight()` is the public halt callback. It disables all ETF blocks and then disables ETR, logging failures but continuing through the halt sequence.

## Control flow
Userspace first uses `HL_DEBUG_OP_SET_MODE` to place the device in debug mode. The common ioctl path rejects CoreSight operations unless `hdev->in_debug` is set and the device is operational. It copies the operation-specific input buffer into a kernel allocation, fills `struct hl_debug_params` with `op`, `reg_idx`, `enable`, input, and output pointers, and calls `hdev->asic_funcs->debug_coresight()`, which is wired to `gaudi_debug_coresight()` in Gaudi's ASIC function table.

`gaudi_debug_coresight()` performs a simple switch dispatch. Per-block handlers first validate `reg_idx` against the corresponding base-register array when the operation targets indexed blocks. Most indexed blocks subtract `CFG_BASE` before using `WREG32()` because the generated base constants are absolute config addresses while the register accessors expect config offsets. Blocks with CoreSight lock access registers write `CORESIGHT_UNLOCK` before programming. ETF and ETR disable/enable paths first request formatter flush/stop, wait for stop/status bits via `gaudi_coresight_timeout()`, clear control, and then either program enable registers or restore disabled defaults.

The ETR path has extra validation and address translation. It rejects addresses above 50 bits and size overflow, accepts host PMMU ranges only when `HW_CAP_MMU` is initialized, and accepts device DRAM/SRAM user ranges regardless of host MMU state. When security firmware is not enabled, it programs `mmPSOC_ETR_AXICTL` to use non-privileged, non-secure writes and selects a smaller write burst for host buffers as a workaround for hardware bug H3 HW-2075.

Leaving debug mode calls `hl_device_set_debug_mode(..., false)`, which invokes `hdev->asic_funcs->halt_coresight()` unless a hard reset is pending. `gaudi_halt_coresight()` builds a zeroed `hl_debug_params`, iterates every ETF index with `enable == false`, then disables ETR. It does not explicitly disable STM, funnels, BMON, or SPMU.

## State and persistence
The file mostly mutates hardware register state rather than maintaining software-owned long-lived state. The static register-base arrays are immutable lookup tables. Runtime state persists in the device's CoreSight blocks: STM masks and ids, ETF/ETR control and write pointers, funnel enable masks, BMON windows and counters, and SPMU event selections/counters. `gaudi_config_etr()` also writes the trace buffer MSB into a PSOC global configuration register used together with ETR RWP/RWPHI to reconstruct a 50-bit write pointer on disable.

Software state dependencies are read from `hdev->asic_prop` and `struct gaudi_device`. `psoc_timestamp_frequency` can override the STM input frequency. `fw_security_enabled` changes whether ETR AXI attributes are programmed. `pmmu`, DRAM, and SRAM range fields define valid ETR target memory. `gaudi->hw_cap_initialized & HW_CAP_MMU` determines whether host PMMU addresses are accepted and controls the diagnostic when an invalid ETR address is not in device SRAM/DRAM.

SPMU disable writes results to the caller-provided output array. The expected layout is event counters first, then overflow status, then cycle count. ETR disable optionally writes the current trace write pointer to a caller-provided 64-bit output location. These outputs are copied back to userspace by the common ioctl layer.

## Dependencies and integration points
This file depends on `gaudiP.h` for `CORESIGHT_TIMEOUT_USEC`, `struct gaudi_device`, `HW_CAP_MMU`, and declarations; `include/gaudi/gaudi_coresight.h` for the userspace-facing register-index enums; generated register definitions in `asic_reg/gaudi_regs.h`; field masks from `gaudi_masks.h`; address map constants from `gaudi_reg_map.h`; and common HabanaLabs debug data structures such as `struct hl_debug_params` and `struct hl_debug_params_*`.

The public callbacks are installed in Gaudi's `asic_funcs` table as `.debug_coresight = gaudi_debug_coresight` and `.halt_coresight = gaudi_halt_coresight`. The common `hl_debug_ioctl()` path handles userspace copy, operation filtering, and debug-mode enforcement. The common device debug-mode path calls `halt_coresight()` when disabling debug mode. The register index arrays must stay synchronized with the enum order in `gaudi_coresight.h`; userspace tools choose `reg_idx` values based on that ABI.

The implementation also integrates with the memory-management model: ETR host buffers are accepted only in PMMU ranges when MMU is initialized, while SRAM and DRAM device buffers are checked against fixed ASIC property ranges. All hardware accesses use HabanaLabs register accessor macros `WREG32()` and `RREG32()`, with a final read from `mmHW_STATE` to flush configuration writes.

## Risks and edge cases
- Register array and enum drift is the highest structural risk. A missing, reordered, or wrong base address in any `debug_*_regs[]` array makes a valid userspace `reg_idx` program the wrong block.
- Many register offsets and magic values are hardware-specific and undocumented in the code. Changes require ASIC documentation or proven hardware validation, especially STM/ETF formatter control, BMON event encodings, and SPMU control values.
- `gaudi_coresight_timeout()` returns `-EFAULT` after a 100 ms poll. A slow or wedged CoreSight block can make debug ioctl disable/enable fail and leave partially programmed capture state.
- `gaudi_config_spmu()` initializes `input = params->input` before checking enable, but only dereferences it after the enable-side null check. The disable path relies instead on a valid output pointer and output size.
- SPMU disable computes `events_num = output_arr_len - 2` before validating `output_arr_len >= 3`. Because these are unsigned values, too-small output sizes underflow `events_num`, though the later size check returns before the value is used in the loop. This is safe as written but fragile under refactoring.
- The common ioctl truncates `args->input_size` to the expected struct size, but `debug_coresight()` allocates the full expected size and copies only the user-provided number of bytes. Operation handlers should continue treating omitted fields as zero-initialized data.
- ETR address validation only checks address ranges; it does not prove that userspace has pinned host pages for the duration of capture. That responsibility is outside this file and must be satisfied by the memory-management/debug tooling contract.
- ETR buffer size is written to a 32-bit register from `input->buffer_size`; oversized values that passed range checks could be truncated if the uAPI type is wider than the hardware register.
- Halting debug mode disables ETF and ETR only. If STM, funnels, BMON, or SPMU blocks were enabled, their state may persist until reset or explicit disable.
- Security mode changes ETR AXI programming. In secure firmware mode this file skips non-secure/non-privileged AXI attribute writes, so behavior depends on firmware-provided defaults.

## Test signals
Positive test signals include successful `HL_DEBUG_OP_SET_MODE` enable, successful enable/disable cycles for STM, ETF, ETR, FUNNEL, BMON, and SPMU on representative indices, trace data reaching an SRAM/DRAM or host PMMU ETR buffer, ETR disable returning a plausible monotonically advancing write pointer, SPMU disable returning event counters plus overflow and cycle count, and debug-mode disable logging no ETF/ETR halt failures. The `mmHW_STATE` flush read should make subsequent debug reads observe the programmed state.

Negative signals include kernel logs such as `Invalid register index in STM/ETF/FUNNEL/BMON/SPMU`, `Timeout while waiting for coresight`, `Failed to enable/disable ETF/ETR on timeout`, `ETR buffer address shouldn't exceed 50 bits`, `ETR buffer size ... overflow`, `ETR buffer address is invalid`, `not enough event types values for SPMU enable`, `too many event types values for SPMU enable/disable`, `not enough values for SPMU disable`, and `Unknown coresight id`. Regression tests should cover invalid `reg_idx`, null or undersized input/output buffers, ETR address overflow, buffer size zero, invalid host address when MMU is not initialized, valid SRAM/DRAM addresses without MMU, and repeated disable calls where the target block is already stopped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi/gaudi_coresight.c -->
