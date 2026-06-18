# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_2_offset.h

## Purpose

`sdma1_4_2_offset.h` is a generated-style AMDGPU ASIC register offset header for the SDMA1 engine in the SDMA 4.2 register layout. It does not implement executable logic; it provides preprocessor constants that name SDMA1 memory-mapped register offsets and their `*_BASE_IDX` selectors.

The file declares the `sdma1_sdma1dec` address block with a documented base address of `0x6180`, then enumerates register offsets from low-level engine control registers through queue-specific GFX, PAGE, and RLC queue windows. Consumers combine these offsets with SoC/IP base tables to form absolute MMIO register addresses.

## Important APIs, Types, and Constants

This header exports macros only. There are no C types, functions, structs, static data objects, or inline APIs.

The exported constants follow two patterns:

- `mmSDMA1_<REGISTER>`: register offset within the SDMA1 address block.
- `mmSDMA1_<REGISTER>_BASE_IDX`: base-index selector for the register, consistently `0` in this file.

Important register groups include:

- Firmware and VM control: `mmSDMA1_UCODE_ADDR`, `mmSDMA1_UCODE_DATA`, `mmSDMA1_UCODE_CHECKSUM`, `mmSDMA1_VM_CNTL`, `mmSDMA1_VM_CTX_LO`, `mmSDMA1_VM_CTX_HI`, `mmSDMA1_VM_CTX_CNTL`, `mmSDMA1_MMHUB_CNTL`.
- Engine control and status: `mmSDMA1_CNTL`, `mmSDMA1_POWER_CNTL`, `mmSDMA1_CLK_CTRL`, `mmSDMA1_FREEZE`, `mmSDMA1_STATUS_REG`, `mmSDMA1_STATUS1_REG`, `mmSDMA1_STATUS2_REG`, `mmSDMA1_STATUS3_REG`, `mmSDMA1_ERROR_LOG`.
- Address translation and cache/TLB-facing controls: `mmSDMA1_GB_ADDR_CONFIG`, `mmSDMA1_GB_ADDR_CONFIG_READ`, `mmSDMA1_UTCL1_CNTL`, `mmSDMA1_UTCL1_WATERMK`, `mmSDMA1_UTCL1_RD_STATUS`, `mmSDMA1_UTCL1_WR_STATUS`, invalidation and XNACK registers, and `mmSDMA1_UTCL1_TIMEOUT`.
- Ring and indirect-buffer queues for the graphics SDMA queue: `mmSDMA1_GFX_RB_CNTL`, ring base/read/write pointer registers, write-pointer polling registers, `mmSDMA1_GFX_IB_*`, `mmSDMA1_GFX_DOORBELL`, `mmSDMA1_GFX_CONTEXT_STATUS`, `mmSDMA1_GFX_PREEMPT`, and mid-command save registers.
- The page queue mirrors the GFX queue structure under `mmSDMA1_PAGE_*`.
- Eight RLC queues mirror the queue register pattern under `mmSDMA1_RLC0_*` through `mmSDMA1_RLC7_*`. The queue windows are regularly spaced by `0x60` offsets, with `RLC0_RB_CNTL` at `0x0140` and `RLC7_RB_CNTL` at `0x03e0`.
- Diagnostics, reliability, and performance counters: `mmSDMA1_EDC_CONFIG`, `mmSDMA1_EDC_COUNTER`, `mmSDMA1_EDC_COUNTER_CLEAR`, `mmSDMA1_PERFMON_CNTL`, `mmSDMA1_PERFCOUNTER0_RESULT`, `mmSDMA1_PERFCOUNTER1_RESULT`, `mmSDMA1_GPU_IOV_VIOLATION_LOG`.

The include guard is `_sdma1_4_2_0_OFFSET_HEADER`.

## Control Flow

The header has no runtime control flow. Its effect occurs at compile time when source files include it and use the macros in register access expressions.

The principal local consumer is `drivers/gpu/drm/amd/amdgpu/sdma_v4_0.c`, which includes this header together with the matching SDMA1 shift/mask header. That source file defines `WREG32_SDMA(instance, offset, value)` and `RREG32_SDMA(instance, offset)` wrappers. Those wrappers call `sdma_v4_0_get_reg_offset(adev, instance, offset)`, which adds the supplied offset to `adev->reg_offset[SDMA*_HWIP][...]` for the selected SDMA engine instance. For SDMA instance `1`, offsets from this file are intended to be added to `adev->reg_offset[SDMA1_HWIP][0][0]`.

This means the practical flow is:

1. IP discovery/setup populates `adev->reg_offset` from ASIC IP base tables.
2. SDMA v4.0 code passes a named `mmSDMA1_*` offset, either directly through SOC15 register macros or indirectly through instance-aware SDMA helpers.
3. The register base plus offset becomes the final MMIO address.
4. Driver code reads or writes that address to initialize, start, stop, reset, debug, or monitor the SDMA engine and its queues.

## State and Persistence Behavior

The file itself has no mutable state and no persistence behavior. It is a compile-time register map.

The constants identify hardware state in the SDMA1 MMIO aperture. Runtime state controlled through these addresses includes SDMA microcode upload address/data ports, engine enable/control bits, clock and power-management state, ring buffer base/read/write pointers, doorbell enable/offset state, indirect-buffer state, queue context/preemption state, EDC counters, performance counters, and error logs.

Any persistence is therefore hardware- and driver-lifecycle dependent. Values written to these registers generally live in device MMIO state until reset, power transition, firmware reinitialization, GPU reset, suspend/resume handling, or driver teardown changes them. The header does not serialize, cache, restore, or validate those values.

## Dependencies

Direct dependencies are minimal:

- Standard C preprocessing, because all exports are `#define` constants.
- The matching register mask/shift header, `sdma1_4_2_sh_mask.h`, for code that needs field-level manipulation of registers named here.
- SOC15/IP base infrastructure, including `SOC15_REG_OFFSET`, `SOC15_REG_ENTRY`, `SOC15_REG_GOLDEN_VALUE`, and `adev->reg_offset`, to translate offsets into actual register addresses.
- ASIC-specific IP offset headers that define SDMA hardware-instance base addresses.

The header must stay numerically consistent with sibling generated headers:

- `sdma0/sdma0_4_2_offset.h` for the SDMA0 engine.
- `sdma2` through `sdma7` SDMA 4.2.2 offset headers used by multi-SDMA ASICs.
- SDMA default and shift/mask headers that encode reset values and bit fields for the same register names.

## Integration Points

`amdgpu/sdma_v4_0.c` is the central integration point. It uses `mmSDMA1_*` constants in golden-setting tables such as `golden_settings_sdma1_4_2`, including `mmSDMA1_CHICKEN_BITS`, `mmSDMA1_CLK_CTRL`, `mmSDMA1_GB_ADDR_CONFIG`, ring write-pointer polling controls, RLC queue pointer-address controls, and UTCL1 timeout/page controls. These tables are applied during hardware initialization for supported ASICs.

The same driver area uses SDMA register offsets for:

- SDMA engine setup and teardown.
- Firmware loading through SDMA ucode address/data registers.
- Ring setup for GFX and PAGE queues.
- Doorbell programming for write-pointer updates.
- Polling and status reads for hang detection, idleness, and reset handling.
- EDC/RAS monitoring paths.

KFD integration code also relies on SDMA RLC queue offset regularity. For example, `amdgpu_amdkfd_arcturus.c` computes an engine register base with `SOC15_REG_OFFSET(SDMA1, 0, mmSDMA1_RLC0_RB_CNTL) - mmSDMA1_RLC0_RB_CNTL`, then adds queue spacing derived from consecutive RLC queue offsets. Similar KFD code in gfx v9/v10 paths computes SDMA RLC queue register offsets for MQD programming and queue management.

## Risks

The primary risk is silent register-address drift. If any offset in this header does not match the target ASIC's hardware specification, driver code can read or write the wrong MMIO register. Because the macros are compile-time constants, the compiler will not detect semantic mismatches.

Important risk areas:

- The header is version-specific. SDMA 4.2 and 4.2.2 layouts differ in places, such as PAGE and RLC queue offsets in sibling headers. Using the wrong header for an ASIC can misprogram queue registers.
- Queue-window spacing is assumed by KFD and SDMA code. Incorrect `RLCn` offsets can break per-queue MQD programming, doorbells, preemption, or status reads.
- `*_BASE_IDX` values are all `0`; if a future register moves to a different base segment and the generated value is not updated, SOC15 helper macros may address the wrong segment.
- Register names overlap with older OSS and GC headers that define absolute or differently based `mmSDMA1_*` values. Include ordering and architecture selection must avoid mixing incompatible namespaces.
- Since writes through these offsets can affect power, firmware, MMHUB/VM, RAS, and queue-control state, a bad constant can produce hangs, GPU resets, data corruption, or hard-to-debug initialization failures.

## Test Signals

Useful validation signals are mostly integration and hardware-facing:

- The tree builds without macro redefinition conflicts or missing `mmSDMA1_*` symbols in SDMA and KFD consumers.
- SDMA v4.0 initialization applies `golden_settings_sdma1_4_2` without MMIO access faults or timeout messages.
- SDMA firmware upload succeeds and `mmSDMA1_UCODE_CHECKSUM`/status reads behave as expected for the target ASIC.
- GFX, PAGE, and RLC SDMA queues initialize, ring read/write pointers advance, and doorbell writes wake the expected queue.
- KFD SDMA queue tests exercise `RLC0` through `RLC7` offset arithmetic without invalid queue addressing.
- Suspend/resume, GPU reset, and ring recovery paths can stop and restart SDMA1 cleanly.
- RAS/EDC paths can read and clear `mmSDMA1_EDC_COUNTER` and related registers without spurious errors.
- Register dumps or debugfs register reads show SDMA1 status, UTCL1, ring, and RLC register values at expected addresses for SDMA 4.2 hardware.
