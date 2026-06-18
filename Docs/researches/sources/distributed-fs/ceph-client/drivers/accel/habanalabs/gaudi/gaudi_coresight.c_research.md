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
