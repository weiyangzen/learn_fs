# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 42402-44690

## Scope

This chunk is the final generated shift/mask segment of the AMD GC 11.0.3 graphics register header. It contains C preprocessor constants only: each hardware register field is represented by a `__SHIFT` macro and a matching `__MASK` macro for 32-bit register composition and decoding. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines start in the middle of `GFX_IMU_DPM_CONTROL` with the `BUSY_MASK` shift and the full mask set for that register. They then cover GFX IMU counters, RLC RAM windows, fence/debug/reset/isolation/timer/fuse/RAM/bootloader fields, GC and SE CAC accumulator and transition-table fields, the full `grtavfsind` RTAVFS register block from `RTAVFS_REG0` through `RTAVFS_REG194`, and the `sqind` shader-queue debug and wave-state registers. The chunk ends at the `SQ_WAVE_EXEC_HI` field definitions and the file's closing `#endif`.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata for the GC 11.0.3 graphics IP. It is not Ceph filesystem logic.

## Purpose

`gc_11_0_3_sh_mask.h` supplies bit layouts for GC 11.0.3 registers. Driver code pairs these macros with register addresses from the matching `gc_11_0_3_offset.h` header and uses register helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` to write or decode individual fields without open-coded bit positions.

This chunk focuses on low-level firmware/power/debug register metadata rather than packet parsing or normal filesystem control flow:

- GFX IMU controls for DPM accumulation, RLC RAM indexed access, fence logging, core control/status, power-good/reset/isolation sequencing, timers, fuse overrides, data/instruction RAM windows, interrupt-handler gasket state, and PSP-decoded bootloader address/size fields.
- GC CAC and SE CAC fields for block/signal selection, threshold programming, per-block 32-bit accumulators, stall/release/power-break lookup tables, fixed-pattern counters, and hardware LUT update status.
- RTAVFS fields for adaptive voltage/frequency sensing: zone start/stop counts, zone enable bitmaps, voltage/frequency pairs, guardband zone selection, CPO averaging/divider weights, ripple-counter controls and readouts, target/current frequency count overrides, PI/binary-search voltage code outputs, stop/debug states, and final scaled/count status.
- SQ indexed fields for local shader-queue debug status/control, wave active/idle slots, wave execution mode/status/trap state, VGPR/LDS allocation, instruction-buffer wait counters, program counter, flat scratch base, hardware IDs, POPS packer state, scheduling mode, shader cycle count, trap temporary registers, `M0`, and `EXEC` masks.

## Important APIs, Types, And Macros

There are no callable APIs or C data types in this chunk. The interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register address macros are expected in `gc_11_0_3_offset.h`.
- Consumers normally combine these constants with AMDGPU MMIO/indexed-register helpers, debug dump helpers, power-management code, reset code, firmware load code, and performance/fault instrumentation.

The main macro families are:

- `GFX_IMU_DPM_*`: accumulator control and count fields. `GFX_IMU_DPM_CONTROL` includes `ACC_RESET`, `ACC_START`, and `BUSY_MASK`; `GFX_IMU_DPM_ACC` and `GFX_IMU_DPM_REF_COUNTER` expose 24-bit counts.
- `GFX_IMU_RLC_RAM_*`: indexed RLC RAM access metadata. `GFX_IMU_RLC_RAM_INDEX` carries `INDEX`, `RLC_INDEX`, and `RAM_VALID`, while high/low address and data registers expose address and 32-bit data windows.
- `GFX_IMU_FENCE_*`, `GFX_IMU_PROGRAM_CTR`, and `GFX_IMU_CORE_*`: fence enable/logging fields, fence log initiator/address fields, program counter state, core reset/stall/debug/break controls, and core status/fault reporting.
- `GFX_IMU_PWROK*`, `GFX_IMU_RESETn`, `GFX_IMU_GFX_RESET_CTRL`, `GFX_IMU_AEB_OVERRIDE`, `GFX_IMU_VDCI_RESET_CTRL`, and `GFX_IMU_GFX_ISO_CTRL`: power-good, reset, valid/reset override, VDCI reset, and isolation bits that participate in graphics power and reset sequencing.
- `GFX_IMU_TIMER[0-2]_*`: three timer blocks with start/stop, clear, up/down, pulse, PWM, timestamp mode, saturation, compare auto-increment, compare interrupt enable, compare values, and current value fields. This chunk defines compare slots `CMP0`, `CMP1`, and `CMP3`; no `CMP2` appears in this generated segment.
- `GFX_IMU_FUSE_CTRL`, `GFX_IMU_D_RAM_*`, `GFX_IMU_GFX_IH_GASKET_CTRL`, and PSP-decoded `GFX_IMU_RLC_BOOTLOADER_*`/`GFX_IMU_I_RAM_*`: fuse divider override/done bits, data/instruction RAM address/data fields, IH gasket reset/buffer status, and RLC bootloader address/size fields.
- `GC_CAC_*` and `SE_CAC_*`: CAC ID/threshold selection plus many `GC_CAC_ACC_*` 32-bit accumulator registers for CP, EA, UTCL2 router/VML2/walker/ATCL2, GDS, GE, PMM, GL2C, PH, SDMA, CHC, GUS, and RLC blocks. `SE_CAC_*` provides the shader-engine CAC selector and threshold fields.
- Transition and update tables: `RELEASE_TO_STALL_LUT_*`, `STALL_TO_RELEASE_LUT_*`, `STALL_TO_PWRBRK_LUT_*`, `PWRBRK_STALL_TO_RELEASE_LUT_*`, `PWRBRK_RELEASE_TO_STALL_LUT_*`, `FIXED_PATTERN_PERF_COUNTER_*`, and `HW_LUT_UPDATE_STATUS`.
- `RTAVFS_REG0` through `RTAVFS_REG194`: generated AVFS register fields. Early registers define zone start/stop counts and enables, mid-range registers define per-zone CPO average divider values and 64 CPO ripple counter snapshots, and late registers define override controls, voltage-code status, run/save/restore/debug-stop controls, scaled final counts, FSM state, and ripple-count readback.
- `SQ_DEBUG_STS_LOCAL`, `SQ_DEBUG_CTRL_LOCAL`, and `SQ_WAVE_*`: SQ debug and wave-state fields for active/valid/idle slots, floating-point mode, exception/trap state, scalar and vector condition flags, allocation bases/sizes, wait counters, PC, scratch, HW IDs, scheduling, shader cycle count, temporary registers, and execution masks.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU consumers:

1. Select the GC 11.0.3 register header for the active ASIC generation.
2. Select the matching register address from `gc_11_0_3_offset.h`.
3. Read or construct a 32-bit register value.
4. Use the `__SHIFT`/`__MASK` pair, typically through field helpers, to pack a new field or decode a hardware snapshot.
5. Write the value through MMIO or indexed-register access, or report the decoded value through debug, performance, reset, or power-management paths.

For GFX IMU fields, higher-level code may sequence reset/power/isolation bits, load or inspect IMU/RLC RAM windows, arm fence logging, control the IMU core, program timers, or provide PSP-visible bootloader location metadata. For CAC and RTAVFS fields, runtime paths configure counters, thresholds, transition lookup tables, and AVFS measurement/control registers, then poll completion/status fields. For SQ fields, debug and wave-inspection flows select a shader-queue indexed register and decode wave state for hang analysis, trap handling, debugger integration, or diagnostics.

The header does not encode required ordering, polling intervals, clear-on-read behavior, reset defaults, side effects, or atomic snapshot rules. Those semantics live in the AMDGPU engine code, firmware protocols, and hardware programming guide.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe hardware state owned by the GPU, firmware, and the AMDGPU driver.

GFX IMU state is sensitive because many fields directly affect hardware sequencing. Core reset/stall/debug controls, power-good/reset/isolation bits, VDCI reset bits, fuse overrides, and IH gasket reset fields are not passive status fields. Incorrect writes can hold graphics blocks in reset, isolate the wrong interface, hide power-good transitions, or prevent interrupt delivery. RLC RAM and IMU instruction/data RAM fields are indexed windows into device-owned RAM; their address/index/data values persist as device state until overwritten, reset, or power-gated.

Fence logging, program counter, core status, and fault fields are diagnostic state. Some bits are live and volatile, while others may be sticky until cleared by a documented sequence. The header cannot distinguish live, sticky, write-one-to-clear, or read-only semantics; callers must preserve reserved bits and follow the register spec.

CAC and RTAVFS state is both configuration and measurement. CAC thresholds, block/signal selections, transition LUT entries, fixed-pattern counters, and hardware LUT update status affect or expose power/performance classification. RTAVFS zone boundaries, enable masks, CPO weights, ripple counters, voltage/frequency codes, override selects, run-loop controls, retention-save/restore controls, and stop/debug controls participate in adaptive voltage/frequency behavior. Misprogramming these fields can produce unstable clocks/voltages, bad power telemetry, misleading performance counters, or failed save/restore of retained AVFS data.

SQ wave registers represent live shader execution state. `SQ_WAVE_STATUS`, `SQ_WAVE_TRAPSTS`, wait counters, PC, scratch pointers, HW IDs, temporary trap registers, `M0`, and `EXEC` masks can change while waves execute. Debug code must capture them with the correct wave selection and stabilization procedure; reading them without quiescing or selecting the intended wave can produce inconsistent snapshots.

Reserved fields appear throughout the chunk, especially in RTAVFS registers. Any read-modify-write consumer should preserve reserved bits unless the authoritative programming sequence explicitly requires a full-register write.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.0.3 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h` provides the matching register address symbols.
- AMDGPU common register helpers provide field extraction/composition and MMIO or indexed-register access.
- GFX IMU, RLC, PSP/firmware load, interrupt handling, reset, graphics-off, clock/power management, CAC, AVFS, shader debug, hang-dump, KFD/compute debugging, and trap/debugger paths are the likely consumers.

Important integration points include:

- IMU/RLC bring-up and firmware/bootloader handoff through `GFX_IMU_RLC_BOOTLOADER_ADDR_*`, `GFX_IMU_RLC_BOOTLOADER_SIZE`, `GFX_IMU_I_RAM_*`, and `GFX_IMU_D_RAM_*`.
- Reset and power sequencing through `GFX_IMU_CORE_CTRL`, `GFX_IMU_CORE_STATUS`, `GFX_IMU_PWROK*`, `GFX_IMU_GFX_RESET_CTRL`, `GFX_IMU_VDCI_RESET_CTRL`, and `GFX_IMU_GFX_ISO_CTRL`.
- Debug and fault reporting through IMU fence logs, program counter, core fault fields, IH gasket status, CAC counters, RTAVFS FSM/status fields, and SQ wave/trap state.
- Power/performance management through CAC accumulators, stall/release and power-break LUTs, fixed-pattern counters, hardware LUT update status, and RTAVFS control/readout registers.
- Shader hang analysis and debugging through `SQ_DEBUG_STS_LOCAL`, wave slot bitmaps, `SQ_WAVE_MODE`, `SQ_WAVE_STATUS`, `SQ_WAVE_TRAPSTS`, allocation/wait/PC/scratch/HW-ID registers, trap temporary registers, and `EXEC`/`M0` state.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but writes the wrong hardware bit or decodes misleading diagnostics.
- The chunk starts mid-register at `GFX_IMU_DPM_CONTROL`; the missing `ACC_RESET` and `ACC_START` shift definitions are in the previous adjacent chunk. This document is chunk-scoped and final file-level research must merge adjacent chunks.
- This chunk closes the header at `#endif`; it has no following adjacent chunk for SQ definitions. The final file report should note that `SQ_WAVE_EXEC_HI` is the terminal macro family in this generated header.
- GFX IMU reset, isolation, fuse, core-control, and VDCI fields have direct side effects. Treating them as ordinary debug bits can hang the graphics pipeline, lose interrupt delivery, or break firmware handoff.
- Indexed RAM windows require correct index/address/data sequencing. Reusing `GFX_IMU_RLC_RAM_INDEX`, `GFX_IMU_D_RAM_ADDR`, or `GFX_IMU_I_RAM_ADDR` without respecting alignment and validity bits can read or modify the wrong internal RAM location.
- Timer fields are repeated across timers 0, 1, and 2 and are easy to update asymmetrically. The generated absence of `CMP2` in this slice should not be "filled in" by assumption without checking the register database.
- CAC accumulator families are long and repetitive. Copy/generator mistakes can silently map a counter for one block, such as SDMA, GE, GL2C, UTCL2, or PH, to the wrong mask.
- Transition LUT fields use narrow packed entries with different widths across release/stall and power-break tables. Using the wrong table's field width can corrupt neighboring entries.
- RTAVFS fields are power-management critical and include many reserved masks. Full-register writes that fail to preserve reserved bits can destabilize AVFS behavior or retention/debug state.
- SQ wave state is volatile and selected through indexed register access. Debuggers and hang-dump code must account for wave selection, halted/running state, and potentially inconsistent snapshots across PC/status/trap/EXEC reads.
- Trap and exception fields can affect security and fault triage. Misdecoding `SQ_WAVE_TRAPSTS`, privilege bits, scratch state, or HW IDs can attribute a fault to the wrong queue, VMID, wave, or shader engine.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware/runtime diagnostics:

- Kernel build coverage for AMDGPU files that include `gc_11_0_3_sh_mask.h`, especially GC 11.0.3 GFX IMU, RLC, PSP, power-management, reset, AVFS/CAC, SQ debug, KFD, and hang-dump paths.
- Mechanical comparison against AMD's authoritative GC 11.0.3 register database for every `__SHIFT` and `__MASK` value in lines 42402-44690.
- Cross-check that every register family in this chunk has a matching address macro in `gc_11_0_3_offset.h`.
- Static mask/shift sanity checks: masks should align with shifts, full-width data registers should use `0xFFFFFFFFL`, packed LUT fields should not overlap, repeated timer and RTAVFS patterns should stay structurally consistent, and reserved masks should cover only documented reserved bits.
- IMU bring-up tests that validate RLC bootloader address/size programming, IMU instruction/data RAM access, core reset/stall release, program counter movement, and absence of fatal/core access errors.
- Reset and power tests that exercise `PWROK`, reset, isolation, VDCI, fuse override, fence, IH gasket, and graphics-off/GFX reset sequences with post-reset register restore.
- CAC and AVFS tests that program thresholds/LUTs, trigger hardware LUT updates, validate done/error/error-step fields, read fixed-pattern counters and accumulators, and compare RTAVFS voltage/frequency/ripple-counter outputs against expected telemetry.
- Suspend/resume and runtime power-management tests that cover RTAVFS save/restore and retention reset fields, timer state, and IMU/RLC RAM accessibility across power transitions.
- SQ debug tests that capture wave active/idle slots, mode/status/trap state, allocation metadata, wait counters, PC, scratch pointers, HW IDs, temporary registers, `M0`, and `EXEC` masks under controlled compute workloads.
- Hang/debug dump tests that verify SQ busy bits, fault/trap bits, wave status, and PC/EXEC snapshots are internally coherent and correspond to the selected wave and queue.
- Runtime warning signals include GPU reset loops, failed GFXOFF entry/exit, IMU core fatal errors, PSP access errors, broken interrupt handling, bad AVFS voltage/frequency behavior, CAC update errors, unstable clocks, misleading performance telemetry, and SQ dumps with impossible active/idle/trap combinations.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002543`. It covers lines 42402-44690 of `gc_11_0_3_sh_mask.h`. The final per-file research should merge it with previous chunks to complete the partial `GFX_IMU_DPM_CONTROL` register and place the GFX IMU, CAC, RTAVFS, and SQ terminal definitions in the full generated GC 11.0.3 register map.
