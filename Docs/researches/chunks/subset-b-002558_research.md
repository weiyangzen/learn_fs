# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 22221-24948

## Purpose

This chunk is part of AMDGPU's generated GC 11.5.0 register field header. It contains C preprocessor constants for register field shifts and masks, not executable code. Driver code combines these `*_SHIFT` and `*_MASK` definitions with the matching register offsets from `gc_11_5_0_offset.h` and helper macros such as `REG_SET_FIELD()` / `REG_GET_FIELD()` in `amdgpu.h` to read, modify, and decode memory-mapped GPU registers.

The span starts in the `gc_pfonly2_spidec` address block with SPI compute-unit reservation fields, covers the large `gc_gfxudec` graphics/user-data command processor and graphics frontend register block, and enters the `gc_cprs64dec` block for RS64/MES/MEC command processor microcontroller state. The chunk ends mid-register at `CP_GFX_RS64_GP0_HI0__M_RET_ADDR__SHIFT`; the following chunk must complete that register's mask and the remaining RS64 GP register definitions.

## Important APIs, Types, And Macro Families

This file defines no functions, structs, or runtime types. Its public interface is macro names of the form:

- `REGISTER__FIELD__SHIFT`: bit offset for `FIELD` inside `REGISTER`.
- `REGISTER__FIELD_MASK`: bitmask for the same field.

The consumer API is outside this file:

- `REG_SET_FIELD(orig_val, reg, field, field_val)` token-pastes `reg##__##field##__SHIFT` and `reg##__##field##_MASK` to insert a field value.
- `REG_GET_FIELD(value, reg, field)` uses the same generated symbols to extract a field.
- `RREG32_SOC15`, `WREG32_SOC15`, and related SOC15 helpers perform the actual MMIO register access using the corresponding `reg...` offset macros.

Major register groups in this chunk:

- `SPI_RESOURCE_RESERVE_CU_2` through `SPI_RESOURCE_RESERVE_CU_15` and `SPI_RESOURCE_RESERVE_EN_CU_0` through `SPI_RESOURCE_RESERVE_EN_CU_15`: per-CU resource reservation controls for VGPR, SGPR, LDS, wave, barrier, enable, type mask, and queue mask fields.
- `CP_EOP_*`, `CP_PIPE_STATS_*`, `CP_VGT_*`, `CP_PA_*`, `CP_SC_*`: command processor event/fence addresses and graphics pipeline statistics/counter registers.
- `SCRATCH_REG*`, `SCRATCH_REG_ATOMIC`, `SCRATCH_REG_CMPSWAP_ATOMIC`: generic CP scratch registers plus atomic/compare-swap fields.
- `CP_APPEND_*`, `CP_*ATOMIC*_PREOP_*`, `CP_ME_MC_*`, `CP_SEM_*`, `CP_WAIT_*`: append buffer, atomic pre-op, memory-controller read/write, semaphore, and wait-register-memory control fields.
- `CP_DMA_PFP_*`, `CP_DMA_ME_*`, `CP_DMA_CNTL`, `CP_DMA_READ_TAGS`: packet/control fields for CP DMA engines, including byte counts, source/destination selection, endian swap, engine and command fields, privilege, discard, and coherency flags.
- `CP_IB*`, `CP_ST_*`, `CP_DB_*`, `CP_DRAW_INDX_INDR_*`, `CP_DISPATCH_INDR_*`, `CP_INDEX_*`, `CP_GDS_BKUP_*`: indirect buffer, state buffer, draw/dispatch indirect, index, and GDS backup address/buffer-size definitions.
- `CP_EOP_DONE_EVENT_CNTL`, `CP_EOP_DONE_DATA_CNTL`, `CP_EOP_DONE_CNTX_ID`: end-of-pipe completion event/data generation controls.
- `CP_ME_COHER_*`: ME coherency control, base, size, and status fields.
- `RLC_GPM_PERF_COUNT_*`, `GRBM_GFX_INDEX`: performance counter and graphics-index selection fields.
- `VGT_*`, `GE_*`, `PA_*`: geometry engine, vertex grouper/tessellator, stereo, VRS, line stipple, screen extent, and trap-screen controls.
- `SQ_THREAD_TRACE_USERDATA_*`, `SQC_CACHES`, `TA_CS_BC_BASE_ADDR*`: shader trace userdata, shader cache controls, and texture/cache backing address fields.
- `DB_OCCLUSION_COUNT*`: depth-buffer occlusion counter fields.
- `GDS_*`: global data share read/write, atomics, global wave sync resources, ordered append controls, stream-out counters, and GS fields.
- `SPI_CONFIG_CNTL*`, `SPI_WAVE_LIMIT_CNTL`, `SPI_GS_THROTTLE_CNTL*`, `SPI_ATTRIBUTE_RING_*`: shader processor interpolator/global shader throttling, wave limits, context-save, power-save, and attribute ring configuration.
- `CP_MES_*`: MES RS64 firmware control, program counter, interrupt routing/status, RISC-V-like machine CSRs (`MSTATUS`, `MEPC`, `MCAUSE`, `MIP`, `MIE`, `MTIME`, etc.), icache/dcache controls, process quanta, doorbell controls, GP registers, local apertures, scratch base, perfcount, interrupt data, and sixteen data-cache apertures.
- `CP_MEC_*`: MEC RS64 firmware control, program counter, interrupt state, dcache controls, GP registers, local/instruction/scratch apertures, perfcount, interrupt data, and sixteen data-cache apertures.
- `CP_CPC_IC_OP_CNTL`, `CP_GFX_CNTL`, `CP_GFX_RS64_*`: command processor instruction-cache operation, graphics engine selection/config, RS64 interrupts, dcache control, local/instruction/scratch apertures, perfcount, timers, interrupt pending bits, and early GP register definitions.

## Control Flow

There is no local control flow. The effective flow is in consumers:

1. Read a 32-bit register with `RREG32_SOC15()` or prepare a zero value.
2. Insert fields with `REG_SET_FIELD()` using symbols from this header.
3. Write the value with `WREG32_SOC15()`.
4. Poll status bits with `REG_GET_FIELD()` when hardware exposes completion flags.

Examples elsewhere in the tree show the same contract: cache setup paths set `CP_CPC_IC_OP_CNTL.INVALIDATE_CACHE` and poll `INVALIDATE_CACHE_COMPLETE`; RS64 data-cache paths set `CP_GFX_RS64_DC_OP_CNTL.INVALIDATE_DCACHE` and poll `INVALIDATE_DCACHE_COMPLETE`; MES setup writes `CP_MES_CNTL` reset/active/halt fields, program-counter registers, scratch addresses, and optional `CP_MES_IC_OP_CNTL` invalidate/prime fields.

## State And Persistence Behavior

The macros themselves are compile-time constants and persist only as preprocessor definitions. The state they describe is hardware state:

- Many `CP_*`, `SPI_*`, `GE_*`, `VGT_*`, `GDS_*`, and `DB_*` registers persist in GPU MMIO/register files until reset, power-gating transitions, firmware reinitialization, or explicit driver writes.
- Address fields such as EOP, pipe stats, append, indirect buffer, data-cache aperture, local scratch, and firmware base registers point hardware blocks at GPU virtual/physical memory managed by AMDGPU.
- Counter/status registers, including pipeline stats, occlusion counters, GDS atomics, cache operation completion bits, and interrupt pending/data registers, are updated by hardware as command streams execute.
- Some fields are per-pipe/per-me/per-queue selected indirectly through GRBM/SRBM selection in consumer code; writes are only meaningful for the currently selected hardware instance.

## Dependencies

This chunk depends on the generated register offset namespace in `gc_11_5_0_offset.h`; mask macros alone do not name an MMIO address. It also depends on AMDGPU helper definitions in `amdgpu.h` for field composition/extraction and on SOC15 register access helpers for addressing GC instances.

The exact header is directly included by `amdgpu/gfxhub_v11_5_0.c` along with `gc_11_5_0_offset.h`. Other AMDGPU GFX/MES/MEC files use the same generated macro naming pattern for nearby ASIC versions and comparable register blocks, so the chunk participates in a broader generated-register ABI even when a specific function includes a sibling `gc_*_sh_mask.h`.

## Integration Points

- GFX hub/MMU code uses this header family to decode protection faults and program VM invalidation or address-translation registers.
- Command processor firmware loading/configuration uses `CP_CPC_IC_OP_CNTL`, `CP_GFX_RS64_DC_*`, `CP_MES_*`, and `CP_MEC_*` field definitions to point instruction/data caches at firmware buffers, invalidate or prime caches, control resets, and activate pipes.
- MES scheduling and KIQ setup use `CP_MES_CNTL`, `CP_MES_PRGRM_CNTR_START*`, `CP_MES_MSCRATCH_*`, `CP_MES_GP*`, doorbell controls, and interrupt fields to initialize and observe MES firmware execution.
- Graphics command submission and counters use `CP_IB*`, `CP_DRAW_INDX_INDR_*`, `CP_DISPATCH_INDR_*`, `CP_EOP_*`, `CP_PIPE_STATS_*`, `VGT_*`, `GE_*`, `DB_OCCLUSION_COUNT*`, and stream-out/GDS counter fields.
- Low-level debugging and fault analysis paths rely on the names staying aligned with hardware documentation because register dumps and decoded fields are interpreted by developers and diagnostic tooling.

## Risks

- A wrong shift or mask silently corrupts register programming. Because `REG_SET_FIELD()` token-pastes these names, build success does not prove that the bit layout matches hardware.
- Cross-generation similarity is a hazard. Registers such as CP/MES/MEC cache and aperture controls appear in GC 11/12 families but not always with identical fields. Copying masks between versions can program reserved or changed bits.
- This chunk ends in the middle of `CP_GFX_RS64_GP0_HI0`; any merge/reconciliation lane must combine adjacent chunks before treating the per-file research as complete.
- Repeated indexed register families (`*_CU_0..15`, `*_APERTURE0..15`, `*_INTERRUPT_DATA_16..31`) are prone to generator or review mistakes where one instance's mask differs accidentally from its siblings.
- Some fields describe security- or isolation-sensitive controls, including VMID, bypass mode, privilege, GDS resource limits, doorbells, scratch/aperture bases, and coherency/cache operations. Incorrect values can cause GPU hangs, memory corruption, cross-VM leakage, or failed firmware startup.
- The macros carry no runtime validation. Tests that only compile the driver may miss field-level regressions unless they exercise real register writes, firmware loading, or hardware polling paths.

## Test Signals

Useful signals for this chunk are mostly integration and hardware-facing:

- Build coverage for AMDGPU GC 11.5.0 paths, ensuring all generated macro names referenced by `REG_SET_FIELD()` and `REG_GET_FIELD()` resolve.
- Driver boot on GC 11.5.0 hardware with successful gfxhub initialization, firmware loading, MES enablement, and queue bring-up.
- No timeout logs from instruction/data cache operations, especially messages around failed CP/MES/MEC icache or RS64 dcache invalidation/priming.
- Successful graphics and compute command submission, indirect draw/dispatch, EOP fence signaling, doorbell handling, and context switching.
- Stable pipeline statistics, occlusion queries, stream-out counters, GDS atomics/global wave sync, and scratch/append-buffer operations under stress.
- Clean GPU reset/resume cycles, because many of these registers are reprogrammed after reset or power transitions.
- Register dump comparison against the GC 11.5.0 hardware specification or AMD-generated headers, especially for indexed aperture/resource families and cache-operation completion bits.
