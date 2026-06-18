# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h lines 7440-9943

## Purpose

This chunk is part of the generated AMD GC 10.1.0 register-offset map used by the amdgpu and amdkfd drivers. It contains preprocessor constants for memory-mapped graphics-core registers and their paired `_BASE_IDX` selectors. Driver code combines these constants with the SOC15 register-base table, for example through `SOC15_REG_OFFSET(GC, inst, mmRLC_CNTL)`, `RREG32_SOC15()`, and `WREG32_SOC15()`, to compute the final MMIO address for Navi/GC 10.1 hardware.

The range covers 1,214 register offset macros and 1,214 matching `_BASE_IDX` macros. It starts mid-block at the graphics pipeline/uconfig area with `mmVGT_INDEX_TYPE = 0x2243` and ends in the beginning of `gc_pwrdec` at `mmCGTS_SA0_WGP00_CU1_SIMD0_CTRL_REG = 0x5014`. All macros in this requested line range use base index `1`, meaning they are resolved against `adev->reg_offset[GC_HWIP][instance][1]` in SOC15-style accessors.

## Register Families In This Chunk

The opening pre-`gc_cprs64dec` portion continues an existing GC register block and includes:

- Draw/index/geometry setup: `mmVGT_INDEX_TYPE`, streamout filled-size registers, vertex index bounds, instance count/base ID, index buffer bases, primitive type state, and GE/VGT ring/offchip parameters.
- Rasterization and screen/trap controls: PA/SC line-stipple, screen extent, trap screen, and HP3D/P3D trap registers.
- Shader and cache debug/control: `mmSQ_THREAD_TRACE_USERDATA_*`, `mmSQC_CACHES`, `mmSQC_WRITEBACK`.
- Depth buffer and query counters: `mmDB_OCCLUSION_COUNT*_LOW/HI`, `mmDB_ZPASS_COUNT_LOW/HI`.
- GDS direct read/write/atomic windows and related atomics/completion registers.
- SPI and wave-limit remap registers, including `mmSPI_WAVE_LIMIT_CNTL_REMAP`.

Named address blocks beginning inside this chunk are:

- `gc_cprs64dec` at base `0x32000`: CP/MES program counter, instruction pointer, MQD base, header dump, queue ownership, VMID, scheduler/debug registers, MES performance counters, and RLC/CP-visible event/state registers.
- `gc_gusdec` at base `0x33000`: GUS command, credit, FIFO, retry, cache, read/write path, and XCD/EA/GC interface controls.
- `gc_gl1dec`, `gc_chdec`, and `gc_gl2dec` at bases `0x33400`, `0x33600`, and `0x33800`: GL1/GL2 arbitration, cache disable, bank selection, pipe steering, channel arbitration, and cache status/control registers.
- `gc_perfddec` at base `0x34000`: low/high result registers for CPG, CPF, CPC, CP, SPI, SQ, SX, TA, TD, TCP, TCC/GL2, CB, DB, PA, CH, GCEA, GCR, GUS, and GCMC/VM L2 performance counters.
- `gc_gcatcl2pfcntrdec`, `gc_gcvml2prdec`, `gc_gcvml2perfddec`, and `gc_gcatcl2perfddec`: small result-register blocks for GC ATC L2 and GCMC VM L2 counters.
- `gc_perfsdec` at base `0x36000`: select/control/mode registers that program the performance counters whose result registers appear in the preceding performance-data blocks.
- `gc_gcatcl2pfcntldec`, `gc_gcvml2pldec`, `gc_gcvml2perfsdec`, and `gc_gcatcl2perfsdec`: ATC/VM L2 performance-counter configuration, select, and mode registers.
- `gc_rlcdec` at base `0x3b000`: the main RLC block, including `mmRLC_CNTL`, firmware/program-counter state, save/restore control, GPU idle/status, safe-mode, performance monitors, SPM, SRM, SMU messaging, power-gating, CP table/DMA/AXI integration, scratch, and debug/capture registers.
- `gc_rlcrdec` at base `0x3b800`: RLC SPP CAM and PACE scratch address/data windows.
- `gc_rlcsdec` at base `0x3b980`: RLC sequence-controller decode registers, exception/general state, clock-gating/deep-sleep controls, IOV status, GRBM soft reset, interrupt handoff, WGP read/status, bootload status, and auxiliary registers.
- `gc_pwrdec` at base `0x3c000`: the first CGTS power/clock-gating and clock-monitor registers for shader-array/quadrant and early WGP/CU controls.

## Important APIs, Types, And Generated Constants

There are no C functions, structs, or runtime control-flow constructs in this chunk. The important API is the macro namespace:

- `mm<REGISTER>` constants hold register offsets such as `mmRLC_CNTL = 0x4c00`, `mmCP_MES_PRGRM_CNTR_START = 0x2800`, and `mmCGTS_STATUS_REG = 0x500c`.
- `mm<REGISTER>_BASE_IDX` constants select which per-IP base slot to add to the offset. Every paired macro in this range is `1`.
- The file-level include guard `_gc_10_1_0_OFFSET_HEADER` makes the generated map safe to include from multiple driver compilation units.

The macros are paired with sibling generated files in the same directory:

- `gc_10_1_0_sh_mask.h` supplies field shifts and masks for these registers.
- `gc_10_1_0_default.h` supplies reset/default values for many of the same register names.
- Other GC generations, such as `gc_10_3_0_offset.h`, carry similar names but sometimes different offsets; callers must include the header matching the IP version.

## Control Flow And Runtime Use

This header contributes only compile-time constants. Runtime control flow appears in its consumers. The standard path is:

1. A GC 10.1.0 driver source includes `gc/gc_10_1_0_offset.h`.
2. The source passes an `mm...` name to an accessor such as `RREG32_SOC15(GC, 0, mmRLC_CNTL)`.
3. `SOC15_REG_OFFSET` computes `adev->reg_offset[GC_HWIP][0][mmRLC_CNTL_BASE_IDX] + mmRLC_CNTL`.
4. The low-level MMIO read/write helper accesses the computed register address.

Direct consumers found in this tree include `amdgpu/gfx_v10_0.c`, KFD queue/MQD management for GFX10, gfxhub/mmhub/sdma/Navi glue, and virtualization-related Navi code. `gfx_v10_0.c` uses registers from this line range for debug/register dumps (`mmCP_MES_*`, `mmRLC_RLCS_*`), RLC enable/disable and status handling (`mmRLC_CNTL`), and RLC bootload polling (`mmRLC_RLCS_BOOTLOAD_STATUS`).

Command processor packet emission can also use these offsets indirectly. For registers that are programmed through packetized UCONFIG/context paths, callers often subtract packet start constants after `SOC15_REG_OFFSET` resolves the MMIO offset; that makes the exact `mm...` value observable in ring command streams, not only in direct MMIO.

## State And Persistence Behavior

The header itself stores no mutable state and performs no persistence. It names hardware state that persists in GPU registers until reset, power transition, firmware action, or explicit driver writes change it. The relevant state domains include:

- Draw/geometry command state, query counters, streamout counters, GDS windows, and SPI/SQ trace state.
- CP/MES scheduling and queue state, including MQD, VMID, program counter, scheduler, and debug state.
- GL1/GL2/GUS/cache configuration and performance-counter selection/result state.
- RLC firmware, save/restore, power-gating, clock-gating, scratch, interrupt, and bootload state.
- CGTS clock-gating and shader-array/WGP/CU clock-monitor state at the start of `gc_pwrdec`.

Because these names map to live MMIO registers, persistence is owned by the hardware and by the surrounding driver sequences. The same offset constant may be read-only, write-only, read/write, destructive-on-read, counter-like, or firmware-owned depending on the hardware register semantics documented outside this header.

## Dependencies And Integration Points

This chunk depends on the AMD-generated register database being internally consistent. Each register must have a matching `_BASE_IDX` macro and must align with the same register name in the mask/default headers when those files expose fields or defaults.

The main integration point is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc15_common.h`, where `SOC15_REG_OFFSET` adds `reg##_BASE_IDX` and `reg` to `adev->reg_offset`. That means a bad offset or bad base index silently redirects all `RREG32_SOC15/WREG32_SOC15` operations for that register. The base-index value is not decorative; it selects the correct aperture within the GC IP block.

Other integration points include:

- GFX10 bring-up, suspend/resume, reset, RLC firmware boot, and power-management paths in `gfx_v10_0.c`.
- KFD queue and MQD programming paths that include the same GC 10.1.0 offsets.
- Performance-monitor programming, where select/mode registers in `gc_perfsdec` must correspond to result registers in `gc_perfddec`.
- Register dump and debug tables, where `SOC15_REG_ENTRY_STR` stores these symbolic names for diagnostics.
- ASIC generation selection in Navi/GC IP discovery code; including a neighboring generation's offset file can compile but target the wrong hardware address.

## Risks And Maintenance Notes

- Generated headers are easy to treat as inert, but an incorrect value changes real MMIO behavior. A single wrong `mmRLC_CNTL`, `mmRLC_RLCS_BOOTLOAD_STATUS`, or `mmCGTS_*` offset can break firmware boot, reset, power gating, or diagnostics.
- The chunk begins at line 7440 with `mmVGT_PRIMITIVE_TYPE_BASE_IDX`; the corresponding `mmVGT_PRIMITIVE_TYPE` macro is just before the chunk. Merge tooling should not infer that the logical register family starts at the chunk boundary.
- All macros in this line range use `_BASE_IDX 1`. If a future regeneration changes an offset into another SOC15 base segment, accessors will compile unchanged but compute different physical addresses.
- Many register names exist across GC 9, GC 10.1, GC 10.3, and later headers. Cross-generation copy/paste can produce values that look plausible while targeting the wrong IP version.
- Performance-counter families are split across result, select, mode, and configuration blocks. Mismatched counter-numbering between these blocks can produce misleading metrics rather than obvious driver failures.
- RLC and RLC_RLCS registers are firmware-sensitive. Writes outside the expected sequencing can race firmware, reset flows, power-gating transitions, or SR-IOV scheduling state.
- Several macros name windows or indirect address/data pairs, such as GDS windows, SPP CAM, PACE scratch, and RLC data windows. Correct usage requires ordering and polling behavior that is not represented in the offset header.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-facing checks:

- Build coverage for all GC 10.1.0 consumers, especially `gfx_v10_0.c`, KFD GFX10 queue/MQD code, and SOC15 register dump paths.
- Static checks that every non-`_BASE_IDX` macro in the chunk has a paired `_BASE_IDX` macro and that all pairs in this range remain base index `1` unless the SOC15 base table is intentionally updated.
- Header consistency checks that fields in `gc_10_1_0_sh_mask.h` and defaults in `gc_10_1_0_default.h` reference register names present in the offset header.
- Boot and reset tests on GC 10.1 hardware that exercise RLC enable/disable, RLC bootload status polling, GRBM idle checks, and safe-mode transitions.
- KFD queue creation/destruction tests that touch CP/MES and MQD-related registers from `gc_cprs64dec`.
- Perf-counter smoke tests that program select/mode registers and verify matching low/high result registers increment for CP/SPI/SQ/TCP/GL2/DB/PA/GUS/VM-L2 counter families.
- Suspend/resume and runtime power-management tests that exercise RLC, CGTS, clock-gating, and power-gating register paths.
- SR-IOV or virtualization tests for the RLC IOV, VM busy, scheduler block, and doorbell-monitor registers when that mode is supported.
