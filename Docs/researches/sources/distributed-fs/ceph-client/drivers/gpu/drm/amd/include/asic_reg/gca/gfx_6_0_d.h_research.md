<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_6_0_d.h -->
# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_6_0_d.h

## Purpose

`gfx_6_0_d.h` is a GFX6/Southern Islands AMDGPU register-address header. It exports 1,758 preprocessor constants that map symbolic graphics-core register names to dword MMIO or indexed-register offsets. The file is included by GFX6-era amdgpu code so driver logic can program command processor rings, graphics/compute shader state, render backends, rasterization, geometry/tessellation, caches, tiling, power gating, microcode engines, debug state, and performance counters without hard-coding numeric addresses in the C implementation.

The header is part of the `gca` ASIC register namespace and pairs with `gfx_6_0_sh_mask.h`, which supplies the bitfield masks and shifts for many of the offsets defined here. Its scope is register naming only: no register semantics are implemented in this file.

## Important APIs, Types, And Macros

This header defines no functions, structs, enums, or storage. Its public API is the macro namespace:

- `ix...` indexed/debug register constants, including `ixCLIPPER_DEBUG_REG*`, `ixGDS_DEBUG_REG*`, `ixIA_DEBUG_REG*`, `ixPA_SC_DEBUG_REG*`, `ixSQ_WAVE_*`, `ixSQ_INTERRUPT_WORD_*`, `ixSXIFCCG_DEBUG_REG*`, and `ixVGT_DEBUG_REG*`. These name indirect or debug-window register indices rather than ordinary C objects.
- `mmCB_*` color-buffer/render-backend constants, including per-target color base, pitch, slice, view, info, CMASK/FMASK, clear words, blend controls, target masks, shader masks, debug buses, and CB performance counters.
- `mmCC_*`, `mmGB_*`, and `mmGC_*` configuration constants for render backend disable/redundancy, shader-array configuration, GPU ID, tile modes `0` through `31`, backend maps, and privileged/user-visible graphics configuration.
- `mmCGTT_*`, `mmCGTS_*`, and `mmRLC_*` clock, clock-gating, power-gating, run-list-controller, microcode, save/restore, SERDES, and GPU clock counter registers.
- `mmCOMPUTE_*`, `mmSPI_SHADER_*`, and `mmSPI_SHADER_USER_DATA_*` compute and shader-program registers for dispatch dimensions, program addresses, resources, trap/TBA/TMA state, temporary rings, and per-stage user data for PS/VS/GS/ES/HS/LS.
- `mmCP_*` command processor registers for CP DMA, indirect buffers, coherency, semaphores, scratch, counters, queues, interrupts, microcode RAM, and ring buffers. The ring families include `mmCP_RB0_*`, `mmCP_RB1_*`, `mmCP_RB2_*`, plus legacy aliases such as `mmCP_RB_BASE`, `mmCP_RB_CNTL`, `mmCP_RB_RPTR`, and `mmCP_RB_WPTR`.
- `mmDB_*`, `mmPA_*`, and `mmVGT_*` depth buffer, primitive assembly, scan converter, setup, clipping, viewport, geometry, tessellation, DMA/index, streamout, and draw-initiation registers.
- `mmGDS_*`, `mmSQ_*`, `mmSQC_*`, `mmSX_*`, `mmTA_*`, `mmTD_*`, `mmTCP_*`, `mmTCI_*`, `mmTCA_*`, and `mmTCC_*` constants for global data share, shader queues, shader core caches, export, texture address/data/cache units, and related performance counters/debug/status registers.
- A manually added trailer from old `sid.h` supplies missing legacy offsets such as `mmCP_DEBUG`, `mmCP_COHER_CNTL2`, `mmRLC_UCODE_ADDR`, `mmRLC_UCODE_DATA`, `mmRLC_RL_BASE`, `mmRLC_RL_SIZE`, `mmRLC_CLEAR_STATE_RESTORE_BASE`, `mmRLC_PG_AO_CU_MASK`, and `mmSPI_STATIC_THREAD_MGMT_1/2/3`.

Because the file is just macro definitions, consumers use the constants through the driver's normal register access helpers (`RREG32`, `WREG32`, `WREG32_P`, packet-building macros, and register-list tables) and through bit masks from the companion shift/mask header.

## Control Flow

The only local control flow is the include guard `GFX_6_0_D_H`. Runtime control flow lives in including modules:

- `amdgpu/gfx_v6_0.c` includes this header and uses the offsets during GFX IP initialization, ring setup, command processor start/stop, RLC microcode load, tile-mode programming, shader/SE selection, clock/power gating, clear-state buffer construction, and GPU clock reads.
- `amdgpu/si.c` uses these constants in Southern Islands golden-register arrays and register-remap logic for tile modes, backend disable, and raster configuration.
- `amdgpu/dce_v6_0.c` includes the header alongside GFX6 masks and enum headers for shared SI/DCE register programming paths.
- `pm/legacy-dpm/si_dpm.c` and `pm/legacy-dpm/si_smc.c` include it for legacy power-management paths that touch GFX/SMU-adjacent SI registers.

A representative flow is CP ring initialization in `gfx_v6_0.c`: the driver computes the ring size, writes `mmCP_RB0_CNTL`, enables read-pointer writeback, clears and writes `mmCP_RB0_WPTR`, programs `mmCP_RB0_RPTR_ADDR`/`HI`, restores `mmCP_RB0_CNTL`, writes `mmCP_RB0_BASE`, starts the CP, and runs `amdgpu_ring_test_helper()`. Every register operand in that sequence is a compile-time address from this header; the bit-level enables come from `gfx_6_0_sh_mask.h`.

## State And Persistence Behavior

The header itself has no mutable state, no allocation, no locking, and no persistence. It defines compile-time constants that persist in the built kernel object.

The hardware registers named by these constants are mutable device state. Writes through `WREG32` persist in the GPU until changed by the driver, firmware, reset, suspend/resume, power gating, or ASIC-specific initialization. Important persistent hardware state exposed by this header includes CP ring base/write/read pointers, RLC save/restore GPU addresses, tile-mode tables, backend masks, raster configuration, shader program addresses, viewport/scissor/depth/color state, performance counters, and clock/power gating controls. Incorrect constants therefore do not fail locally in this header; they redirect later register accesses to the wrong hardware state.

## Dependencies

The file depends on AMD's generated register naming convention and the Southern Islands/GFX6 register map. It is meant to be included with:

- `gca/gfx_6_0_sh_mask.h` for field masks and shifts such as `CP_RB0_CNTL__RB_RPTR_WR_ENA_MASK` and RLC/SPI/GB/PA field definitions.
- GFX6 and SI driver code that provides `RREG32`, `WREG32`, `WREG32_P`, `lower_32_bits()`, `upper_32_bits()`, packet builders, firmware loading, and ASIC-family selection.
- Neighboring ASIC register headers for other blocks used by the same call sites, including `bif_3_0`, `oss_1_0`, `gmc_6_0`, `dce_6_0`, and `smu_6_0`.
- Southern Islands headers such as `sid.h`, `si_enums.h`, and `gfx_7_2_enum.h` where common packet constants, enums, or legacy definitions are shared.

The numeric offsets are not self-describing and are only valid for the GFX6 register layout. Later GFX families have similar names in other headers but different offset schemes and, in newer code, SOC15 base-index handling.

## Integration Points

The strongest integration point is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v6_0.c`, where the constants directly control the GFX6 IP block. Examples include:

- Tile mode programming with `mmGB_TILE_MODE0 + reg_offset`.
- Shader-engine and render-backend selection through `mmGRBM_GFX_INDEX`, `mmCC_RB_BACKEND_DISABLE`, and `mmPA_SC_RASTER_CONFIG`.
- Static thread-management updates via the manually added `mmSPI_STATIC_THREAD_MGMT_3`.
- GFX ring access through `mmCP_RB0_BASE`, `mmCP_RB0_CNTL`, `mmCP_RB0_WPTR`, `mmCP_RB0_RPTR_ADDR`, and `mmCP_RB0_RPTR_ADDR_HI`.
- RLC lifecycle and microcode programming through `mmRLC_CNTL`, `mmRLC_UCODE_ADDR`, `mmRLC_UCODE_DATA`, `mmRLC_SAVE_AND_RESTORE_BASE`, `mmRLC_CLEAR_STATE_RESTORE_BASE`, `mmRLC_PG_CNTL`, and related SERDES busy/control registers.

`sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si.c` integrates the same offsets into ASIC-specific golden-register tables. It also treats `mmGB_TILE_MODE0` through `mmGB_TILE_MODE31`, `mmCC_RB_BACKEND_DISABLE`, and `mmPA_SC_RASTER_CONFIG` as special values when remapping saved register tables.

Legacy SI power and firmware paths in `pm/legacy-dpm/si_dpm.c` and `pm/legacy-dpm/si_smc.c` include this header so power-management and SMC code can share the same GFX6 address vocabulary as the graphics block.

## Risks And Edge Cases

The largest risk is silent address drift. Since all definitions are plain macros, a wrong numeric value compiles cleanly and only appears as bad hardware behavior, GPU hangs, failed ring tests, rendering corruption, broken power gating, or invalid debug/performance readings.

The file intentionally contains aliases and repeated values. For example, `mmCP_RB0_BASE` and `mmCP_RB_BASE` both map to `0x3040`, `mmCP_RB0_CNTL` and `mmCP_RB_CNTL` both map to `0x3041`, several `mmSQ_*` instruction decode names map to `0x237F`, and many thread-trace word aliases map to `0x23B0`/`0x23B1`. Duplicate-value checkers must distinguish intentional hardware aliases from accidental copy errors.

Some critical constants are not from the same generated block: the trailer is explicitly "manually added from old sid.h". These names are operationally important in `gfx_v6_0.c` and `si.c`, especially `mmCP_DEBUG`, `mmRLC_UCODE_ADDR`, `mmRLC_UCODE_DATA`, `mmRLC_CLEAR_STATE_RESTORE_BASE`, and `mmSPI_STATIC_THREAD_MGMT_*`. Regenerating the header without preserving these additions would break current consumers.

Register address families are dense and often indexed by arithmetic, such as `mmGB_TILE_MODE0 + reg_offset` or register ranges for color targets and viewport/scissor slots. Off-by-one values in the base macros or assumptions about contiguity can corrupt adjacent register programming. High-address context registers in the `0xA000` range are also used in packet-building paths, where the offset may be converted relative to packet register starts rather than written directly as MMIO.

## Test Signals

Useful build-time signals are successful compilation of Southern Islands amdgpu code paths that include `gfx_v6_0.c`, `si.c`, `dce_v6_0.c`, `si_dpm.c`, and `si_smc.c` with `gfx_6_0_sh_mask.h`. Static checks should verify the macro count and compare offsets against AMD register metadata, while allowing documented duplicate aliases and preserving the manual `sid.h` trailer.

Runtime or hardware-facing signals include successful GFX6 device probe, firmware loading, `amdgpu_ring_test_helper()` passing for the GFX ring after CP ring setup, clean RLC start/resume and power-gating transitions, stable suspend/resume, correct tiling/render output on SI GPUs, and absence of CP/RLC/GRBM hang reports. Debugfs or driver diagnostics that read GPU clock counters, wave state, performance counters, tile modes, and backend/raster configuration can also expose wrong offsets quickly.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_6_0_d.h -->
