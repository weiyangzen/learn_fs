# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 22800-25181

## Scope

This chunk is a generated AMD GC 12.1.0 shift/mask register-header segment. It contains C preprocessor constants only: hardware register fields are represented as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros for packing and decoding 32-bit register values. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines begin with the trailing `GFX_IMU_SCRATCH_5__DATA_MASK` from a register whose marker and shift are in the previous chunk, then cover GFX IMU scratch, timestamp, interrupt-controller, clock/reset/isolation, RAM, fence, timer, fuse, and bootloader fields. The range then crosses GRBMH, PA/GE, SQ/SQC/SQG, and the start of SX debug-busy fields. It ends inside `SX_DEBUG_BUSY_9`, after the first visible mask for `IDX_BANK7VAL2_BUSY`, so the complete SX busy diagnostic family continues in the next chunk.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM graphics-core hardware metadata and is unrelated to Ceph or distributed filesystem logic.

## Purpose

`gc_12_1_0_sh_mask.h` supplies bit layouts for GC 12.1.0 graphics hardware. Driver code pairs these macros with the matching register addresses from `gc_12_1_0_offset.h` and uses them through helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` instead of hard-coding bit positions.

This chunk focuses on low-level graphics management, shader, cache/TLB, and diagnostics surfaces:

- GFX IMU state, including scratch registers, global timestamp offsets, PIC interrupt mask/level/edge/priority/status registers, interrupt-handler gasket state, clock and doorbell controls, RLC throttle/reset/override controls, DPM counters, RLC RAM access windows, fence logging, core control/status, reset and isolation controls, timers, fuse control, D-RAM/I-RAM access, and RLC bootloader address/size fields.
- GRBMH control and status, including read timeout, path disable controls, graphics block busy/clean indicators, fine-grain clock-gating target bits, soft reset bits, read-error capture, clock enables, invalid-pipe reporting, and sync state.
- PA/GE front-end controls for rate limiting, shader-array configuration, interface-safe registers, primitive assembler/setup/clip debug and FIFO controls, and scan-converter debug control.
- SQ/SQC/SQG shader control registers, including shader execution configuration, SQC cache behavior, random wave priority, FIFO sizing, deterministic stress/error injection controls, PIT weights, thread-trace selection, shader cycle counters, host trap status, GL1X status/control, performance snapshot control, watchpoint address/control registers, UTCL0 fault/retry/control registers, VMID fault/error status, indirect SQ register access, timeout status, and miscellaneous SQC controls.
- SX shader-export debug state, including busy bitmaps for exp FIFOs, export buffers, scoreboards, column request paths, blend queues, position/index banks, and related reserved fields.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the raw mask for that field inside the 32-bit register value.
- Matching register addresses and base indices are supplied by `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h`.
- Consumers normally combine these symbols with AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32*`, `WREG32*`, SOC15 register-offset helpers, indexed-register helpers, debugfs/register-dump code, and firmware or command-stream programming paths.

Important register groups in this range include:

- `GFX_IMU_SCRATCH_6` through `GFX_IMU_SCRATCH_15`: full-width scratch data registers used as firmware/driver-visible IMU scratch state. The chunk starts with only the final mask for `GFX_IMU_SCRATCH_5`.
- `GFX_IMU_FW_GTS_*`, `GFX_IMU_GTS_OFFSET_*`, and `GFX_IMU_RLC_GTS_OFFSET_*`: low/high timestamp and timestamp-offset fields, with 32-bit low halves and 24-bit high halves.
- `GFX_IMU_CORE_INT_STATUS`, `GFX_IMU_PIC_INT_MASK`, `GFX_IMU_PIC_INT_LVL`, `GFX_IMU_PIC_INT_EDGE`, `GFX_IMU_PIC_INT_PRI_0` through `GFX_IMU_PIC_INT_PRI_7`, `GFX_IMU_PIC_INT_STATUS`, `GFX_IMU_PIC_INTR`, and `GFX_IMU_PIC_INTR_ID`: IMU interrupt state, masking, trigger mode, priority, active interrupt reporting, and interrupt ID decode.
- `GFX_IMU_IH_CTRL_*`, `GFX_IMU_IH_STATUS`, and `GFX_IMU_GFX_IH_GASKET_CTRL`: interrupt-handler gasket controls and buffer status/overflow visibility.
- `GFX_IMU_GFXCLK_BYPASS_CTRL`, `GFX_IMU_CLK_CTRL`, `GFX_IMU_RLC_CG_CTRL`, `GFX_IMU_RLC_THROTTLE_GFX`, `GFX_IMU_GFX_RESET_CTRL`, `GFX_IMU_VDCI_RESET_CTRL`, and `GFX_IMU_GFX_ISO_CTRL`: clock bypass/gating, throttling, reset, VDCI reset, and isolation controls.
- `GFX_IMU_RLC_RAM_INDEX`, `GFX_IMU_RLC_RAM_ADDR_HIGH`, `GFX_IMU_RLC_RAM_ADDR_LOW`, `GFX_IMU_RLC_RAM_DATA`, `GFX_IMU_D_RAM_ADDR`, `GFX_IMU_D_RAM_DATA`, `GFX_IMU_I_RAM_ADDR`, and `GFX_IMU_I_RAM_DATA`: indexed RAM access windows for RLC, data RAM, and instruction RAM.
- `GFX_IMU_RLC_BOOTLOADER_ADDR_HI`, `GFX_IMU_RLC_BOOTLOADER_ADDR_LO`, and `GFX_IMU_RLC_BOOTLOADER_SIZE`: bootloader location and size fields in the `gfx_imu_pspdec` address block.
- `GRBMH_STATUS`, `GRBMH_SOFT_RESET`, `GRBMH_READ_ERROR`, `GRBMH_GFX_CLKEN_CNTL`, `GRBMH_NOWHERE`, `GRBMH_INVALID_PIPE`, and `GRBMH_SYNC`: GRBMH status, reset, error, clock, invalid access, and synchronization field definitions.
- `GE_RATE_CNTL_*`, `CC_GC_SHADER_ARRAY_CONFIG`, `GE_SE_CNTL_STATUS`, `GE_SPI_IF_SAFE_REG`, `GE_PA_IF_SAFE_REG`, `PA_SU_DEBUG_CNTL`, `PA_CL_CNTL_STATUS`, `PA_CL_ENHANCE`, `PA_CL_RESET_DEBUG`, `PA_SU_CNTL_STATUS`, `PA_SC_FIFO_DEPTH_CNTL`, `PA_PH_DEBUG_CNTL`, and `PA_SC_DEBUG_CNTL`: geometry, primitive assembly, clipping, setup, and scan-converter debug/configuration knobs.
- `SQ_CONFIG`, `SQC_CONFIG`, `SP_CONFIG`, `SQ_ARB_CONFIG`, `SQ_DYN_VGPR`, `SQ_FIFO_SIZES`, `SQ_DSM_CNTL`, `SQ_DSM_CNTL2`, and `SQ_PIT_WEIGHT`: shader execution, arbitration, cache, FIFO, dynamic VGPR, and stress/error-injection layout.
- `SQ_SHADER_CYCLES_LO/HI`, `SQ_PERF_SNAPSHOT_CTRL`, `SQ_INTERRUPT_AUTO_MASK`, `SQ_INTERRUPT_MSG_CTRL`, and `SQ_DEBUG_HOST_TRAP_STATUS`: shader cycle/performance snapshot, interrupt, and trap debug fields.
- `SQ_WATCH0_*` through `SQ_WATCH3_*`: four shader watchpoint address/control sets with address high/low fragments, VMID fields, masks, and valid bits.
- `SQG_UTCL0_*`, `SQC_UTCL0_*`, `SQG_VMID_FED_*`, `SQG_SE_PIT_CONTROL`, `SQC_PIT_CONTROL*`, `SQC_MISC_CONFIG`, `SQ_TIMEOUT_CONFIG`, and `SQ_TIMEOUT_STATUS_SIMD*`: shader TLB/cache fault, retry, PIT, timeout, and miscellaneous control/status fields.
- `SQ_IND_INDEX`, `SQ_IND_DATA`, and `SQ_CMD`: indirect SQ register access and command fields.
- `SX_DEBUG_BUSY`, `SX_DEBUG_BUSY_2` through `SX_DEBUG_BUSY_9`, and `SX_DEBUG_1`: shader-export diagnostic busy/status bitmaps.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Select the GC 12.1.0 generated register headers for the active ASIC.
2. Select a register address from `gc_12_1_0_offset.h`.
3. Use this file's shift/mask macros, usually through field helpers, to compose or decode a register value.
4. Read or write the register through MMIO, indexed access, RLC-safe accessors, firmware-mediated paths, command packets, register dump tools, profiling tools, or debugfs paths.

For IMU and GRBMH controls, higher-level code sequences reset, boot, clock, isolation, interrupt, and RAM-window operations around GPU initialization, firmware loading, reset, suspend/resume, or diagnostics. For SQ/SQC/SQG controls, runtime code and tooling program shader/cache/TLB controls, watchpoints, timeout behavior, performance snapshots, and trap/interrupt behavior. For SX debug registers, diagnostic code reads transient busy bitmaps to understand whether export, blend, position, or index paths are still active. This file does not encode ordering constraints, waits, privilege checks, clear-on-read/write-one-to-clear behavior, or side effects.

## State And Persistence Behavior

The macros themselves hold no state and persist nothing. They describe hardware-visible state:

- GFX IMU scratch registers, timestamp offsets, interrupt-controller configuration, clock/reset/isolation settings, timer compare values, RAM-window indices, and bootloader address/size fields persist in the relevant hardware register file until reset, power-gating loss, firmware reinitialization, or driver reprogramming.
- IMU status, interrupt status, IH gasket status, DPM counters, timer values, core status, power-good, and overflow fields can change asynchronously as firmware and hardware run.
- GRBMH status and busy/clean fields are live hardware state for graphics blocks such as SC, DB, CB, UTCL1, TCP, GL1, GE, RLC, WGS, EA, GL2, SQG, PA, TA, SX, and SPI. Reset and clock-enable fields are persistent controls until cleared or reset.
- PA/GE debug/configuration fields are graphics front-end state. Some are passive configuration, while reset/debug fields can have side effects when written.
- SQ/SQC/SQG configuration, watchpoint, timeout, PIT, performance snapshot, and UTCL0 controls persist until overwritten, context-switched, reset, or power-managed. Status and retry/fault fields can be sticky, transient, or clear-sensitive depending on hardware semantics outside this header.
- SX debug-busy registers are observation surfaces for live pipeline state. They should be treated as snapshots, not persistent configuration.

Reserved fields appear throughout the chunk. Callers should preserve reserved bits during read-modify-write unless emitting a documented full-register value from the hardware programming guide.

## Dependencies And Integration Points

The primary dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h`, which supplies matching register offsets and base-index metadata. The generated shift/mask header must remain synchronized with that offset header and AMD's GC 12.1.0 register database.

Likely integration points in AMDGPU include:

- GFX IMU firmware/bootstrap, RLC interaction, doorbell, fence, interrupt, DPM, timer, reset, isolation, and RAM-access code paths that need the `GFX_IMU_*` fields.
- PSP/RLC firmware loading or validation paths that program `GFX_IMU_RLC_BOOTLOADER_*` fields.
- Graphics reset, hang diagnosis, and idle-wait paths that read `GRBMH_STATUS`, use `GRBMH_SOFT_RESET`, or inspect GRBMH read-error/invalid-pipe state.
- Power-management and clock-gating code that programs IMU/GRBMH/SQ/SQC/SX clock and fine-grain clock-gating override fields.
- Shader debug, trap, watchpoint, and timeout handling paths using `SQ_WATCH*`, `SQ_DEBUG_HOST_TRAP_STATUS`, `SQ_INTERRUPT_*`, and `SQ_TIMEOUT_*`.
- GPUVM fault/retry diagnostics and cache/TLB setup using `SQG_UTCL0_*`, `SQC_UTCL0_*`, and VMID fault/error status fields.
- Profiling and register-dump tooling that decodes shader cycle counters, performance snapshots, PIT controls, SQ/SQC/SQG status, and SX busy maps.

Because this is generated hardware metadata, most concrete behavior is expressed in consumers through AMDGPU helper macros and register-access wrappers rather than in this file.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask can compile cleanly while programming or decoding the wrong hardware bit.
- The chunk starts and ends mid-register family. It starts with only the mask for `GFX_IMU_SCRATCH_5__DATA`, while the associated marker/shift are in the previous chunk, and it ends inside `SX_DEBUG_BUSY_9`. The final file-level research must reconcile these artificial boundaries.
- IMU reset, isolation, clock, bootloader, RAM-window, and fence controls are low-level management surfaces. Misprogramming them can break firmware boot, RLC interaction, interrupts, reset recovery, or power transitions.
- PIC interrupt masks, levels, edges, priorities, status, and ID fields are dense and repetitive. Off-by-one shifts can route, mask, or prioritize the wrong interrupt and may only appear under specific firmware or fault conditions.
- Timestamp high fields use 24-bit masks while low fields are 32-bit. Consumers must not assume every low/high pair is two full 32-bit halves.
- Indexed RAM and indirect SQ access registers require correct sequencing outside this header. A valid mask does not guarantee that arbitrary reads/writes are safe at runtime.
- Reset, soft-reset, timeout, trap, fault, and error-injection fields may be write-one-to-clear, pulse-style, sticky, or side-effecting. The generated macros do not describe access semantics.
- Watchpoint address fields are split and aligned, with low address fields beginning at bit 6 and high address fields using 25 bits. Ad hoc address packing can silently produce watchpoints on the wrong address range.
- UTCL0 fault/retry and VMID fault/error status fields can be transient or sticky. Poor clear/sampling order can hide faults or report stale VMID state.
- SX debug-busy bitmaps are broad and highly repetitive. A mask mismatch can make diagnostics claim the wrong sub-pipeline is stuck, which is especially risky during hang triage.

## Test Signals

Useful validation should combine generated-data checks, build coverage, and hardware/runtime diagnostics:

- Build AMDGPU code paths that include `gc_12_1_0_sh_mask.h` and `gc_12_1_0_offset.h`; missing or renamed macros should surface at compile time.
- Mechanically compare this line range against AMD's authoritative GC 12.1.0 register database. Every complete field should have matching `__SHIFT` and `_MASK` entries, and masks should align with their shifts.
- Cross-check the registers named in this chunk against `gc_12_1_0_offset.h` for matching address definitions and base indices.
- Run static sanity checks for repeated structures: PIC mask/level/edge bitmaps, eight interrupt-priority registers, timer0/timer1 layouts, watchpoint0-3 layouts, SQG/SQC UTCL0 controls, and SX debug-busy register families should remain structurally consistent where hardware expects repetition.
- Exercise GPU init, firmware boot, suspend/resume, GPU reset, and RLC/IMU bring-up on GC 12.1.0 hardware. Signals include successful IMU/RLC boot, stable doorbell/interrupt delivery, no unexpected fence-log or IH overflow, and clean reset recovery.
- Validate GRBMH idle/hang diagnostics by comparing decoded `GRBMH_STATUS`, read-error, invalid-pipe, and sync fields against known-good register dumps or simulator traces.
- Run shader debug and trap/watchpoint tests that program `SQ_WATCH*`, generate controlled traps or memory accesses, and verify that decoded status/VMID/address fields match the workload.
- Run GPUVM fault/retry tests that exercise SQG/SQC UTCL0 status and retry controls, with expected signals in VMID fault/error fields and no stale or missing fault reporting.
- Run profiling or performance snapshot tests using shader cycle counters and `SQ_PERF_SNAPSHOT_CTRL`, checking that controlled workloads move expected counters.
- During hang or stress tests, sample SX debug-busy registers and compare decoded busy bits with hardware traces or known pipeline activity.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002601`. The previous chunk owns the beginning of the `GFX_IMU_SCRATCH_5` definition. This chunk then covers most of the visible IMU management block, GRBMH, PA/GE debug/configuration, SQ/SQC/SQG shader and TLB/cache controls, and the beginning of SX debug-busy state. The next chunk should complete `SX_DEBUG_BUSY_9` and continue the remaining generated GC 12.1.0 shift/mask definitions. The final per-file research should merge these boundaries before describing the complete `gc_12_1_0_sh_mask.h` register map.
