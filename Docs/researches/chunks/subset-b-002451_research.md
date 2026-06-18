# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 5196-7635

## Purpose

This chunk is part of AMD's generated GFX/GC 10.1.0 register shift/mask header. It provides C preprocessor constants for bit-field extraction and insertion in Navi/GFX10-era AMDGPU graphics, command processor, SDMA, and primitive/rasterizer registers. It has no executable logic; its value is that in-tree drivers can use symbolic field names with `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and generated `mm*` offsets instead of hard-coded bit positions.

Although the file is stored under a local `ceph-client` source mirror, the content is AMDGPU hardware metadata, not Ceph or distributed filesystem code.

The requested range contains 2,440 lines, 2,169 `#define` statements, 1,086 `__SHIFT` macros, 1,083 `_MASK` macros, 3 address-block markers, and 262 generated register comments. It starts inside `SDMA1_RLC6_IB_CNTL` at the `SWITCH_INSIDE_IB` shift and finishes inside `PA_SC_TILE_STEERING_CREST_OVERRIDE` at the `FORCE_TILE_STEERING_OVERRIDE_USE` shift. The fully covered domains are:

- `gc_sdma1_*` tail definitions for SDMA1 RLC queues 6 and 7.
- `gc_grbmdec` global graphics register bus manager status, reset, trap, scratch, IOV, and error fields.
- `gc_cpdec` command processor CPC/CPF/ME/MEC/CE/PFP busy, stalled, status, queue, ring, and threshold fields.
- `gc_padec` primitive assembly, VGT/WD/GE, PA_CL, PA_SC, and binning/rasterizer control/status fields.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocations, locks, or direct MMIO operations in this chunk. The public interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the field in the register word.
- `// addressBlock: ...`: generated boundary mapping subsequent register comments to a hardware register block.
- `//<REGISTER>` comments: generated register group boundaries that correspond to register offsets in `gc_10_1_0_offset.h`.

Major macro families in this range:

- `SDMA1_RLC6_*` and `SDMA1_RLC7_*`: queue/ring buffer and indirect-buffer controls for SDMA1 RLC contexts. The fields cover ring enable/size/swap/VMID/privilege, read/write pointers, read-pointer writeback, write-pointer polling, IB enable/base/size/offset/read pointer, context status, doorbells and doorbell offsets, watermarking, context-save-area addresses, preemption, AQL packet controls, minor pointer update, and mid-command data/control.
- `GRBM_*`: global graphics status and management fields. These include graphics/CP busy status, per-shader-engine status (`GRBM_STATUS_SE0` through `SE3`), status2/status3 flags, power controls, soft-reset bits, clock gating controls, wait-idle timing, read/write/IOV error reporting, interrupt control, trap registers, DSM bypass, chip revision, GFX instance selection, IH credit, UTCL2 invalidation range, fence ranges, `GRBM_NOWHERE`, and scratch registers.
- `CP_CPC_*`, `CP_CPF_*`, and `CP_*`: command processor status, busy, stalled, queue, threshold, scratch, instruction-pointer, header-dump, halt/reset/cache-invalidate, preemption, ring-pointer, command-index/data, ROQ/STQ/MEQ/CEQ availability and statistics, and GRBM free-count fields. The chunk covers CPC, CPF, MEC, ME, PFP, and CE-facing state.
- `VGT_*`, `WD_*`, `GE_*`, `IA_UTCL1_*`, `CC_GC_*`, and `GC_USER_*`: vertex/geometry/tessellation and draw-dispatch front-end configuration fields, including FIFO depths, cache invalidation, shader-array configuration, DMA primitive controls, off-chip/ring sizes, UTCL1 status/control, geometry-engine status, fast clocks, and primitive configuration.
- `PA_CL_*`, `PA_SU_*`, `PA_PH_*`, and `PA_SC_*`: primitive/raster pipeline fields for clipper and setup status/enhance controls, binning event/performance controls, force-EOV counters, FIFO sizing, sideband delays, packed binning/PBB overrides, rasterizer enhancement flags, DSM force controls, and the start of tile-steering override selection.

Common field names encode hardware semantics: `ENABLE`, `IDLE`, `BUSY`, `STALL`, `HALT`, `RESET`, `STATUS`, `ERROR`, `VMID`, `ADDR`, `OFFSET`, `SIZE`, `WPTR`, `RPTR`, `POLL`, `DOORBELL`, `PREEMPT`, `CONTEXT`, `AQL`, `WATERMARK`, `SCRATCH`, `TRAP`, `INT`, `THRESHOLD`, `FREE_COUNT`, `FIFO`, `CACHE_INVALIDATION`, `FLUSH`, `BINNER`, `PBB`, `CLOCK_GATE`, `POWER`, and `RESERVED`.

## Control Flow

This header has no runtime control flow. Runtime behavior emerges only when compiled consumers combine these constants with register offsets and AMDGPU register helper macros:

1. A driver selects a register offset from `gc_10_1_0_offset.h`, such as `mmGRBM_STATUS`, `mmGRBM_SOFT_RESET`, an SDMA RLC queue register, or a CP/PA/VGT register.
2. The driver uses a field mask directly or uses `REG_SET_FIELD`/`REG_GET_FIELD`, which token-pastes the register and field names to the `__SHIFT` and `_MASK` macros in this file.
3. The driver reads, writes, modifies, polls, or dumps the hardware register with SOC15 MMIO helpers.
4. Hardware command processors, SDMA engines, GRBM reset/idle logic, and rasterization front-end state machines act on the programmed values or report status through the same fields.

In-tree examples include `gfx_v10_0.c`, which includes this header and uses `GRBM_STATUS__GUI_ACTIVE_MASK`, `GRBM_STATUS__PA_BUSY_MASK`, `GRBM_STATUS__SC_BUSY_MASK`, `GRBM_STATUS__CP_BUSY_MASK`, and `GRBM_SOFT_RESET` fields to wait for idle and decide which blocks to reset. `sdma_v5_0.c` includes this header next to `gc_10_1_0_offset.h` and uses the same register database for SDMA ring setup, diagnostics, queue stop/restore, and golden register programming. KFD queue, MQD, packet manager, gfxhub, `nv.c`, and virtualization support also include this header.

## State And Persistence Behavior

The macros are stateless compile-time constants. They describe volatile hardware register state, but do not store state themselves and do not define reset values, access permissions, read side effects, write-one-to-clear behavior, ordering constraints, or persistence across GPU resets and power states.

Hardware state represented in this chunk includes:

- SDMA1 RLC6/RLC7 ring, IB, doorbell, polling, VMID, AQL, preemption, context status, context-save, and mid-command state. These values are part of SDMA queue execution and may be initialized by AMDGPU/KFD, changed during queue scheduling, and lost or restored across SDMA stop/start, GPU reset, or suspend/resume.
- GRBM status, per-SE busy state, soft-reset request bits, trap/error/IOV reporting, clock/power controls, scratch registers, fence ranges, and graphics-instance selection. Some fields are status-only snapshots; others are control or debug registers that influence global graphics behavior.
- CP engine state for CPC/CPF/MEC/ME/PFP/CE pipelines, including busy/stalled flags, queue availability, ring pointer status, instruction pointers, command-index/data access, halt/step/reset/cache-invalidate controls, and preemption state.
- VGT/WD/GE/IA state for front-end DMA, primitive, geometry, tessellation, UTCL1, FIFO, and shader-array configuration.
- PA/SC/CL/PH state for clipping, primitive assembly, setup/rasterizer enhancements, binning/PBB behavior, binner event routing, FIFO depths, EOV counters, sideband delays, and tile steering.

Persistence is determined by the underlying hardware block and driver sequencing. Queue pointers, doorbells, scratch registers, and context-save addresses can be meaningful across normal scheduling windows, while reset, power-gate, suspend/resume, and firmware-managed reinitialization paths may clear or rewrite them. Busy/status/error fields are generally live observations and should be treated as volatile.

## Dependencies And Integration Points

This chunk must stay synchronized with the GC 10.1.0 register database and companion generated headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h` supplies the matching `mm*` register offsets.
- `gc_10_1_0_default.h` provides default values for the same generation where emitted.
- Neighbor generation headers such as `gc_10_3_0_sh_mask.h`, `gc_11_0_0_sh_mask.h`, `gc_9_4_3_sh_mask.h`, and SDMA-specific headers expose similar field families with generation-specific differences.
- AMDGPU GFX10 code (`amdgpu/gfx_v10_0.c`) uses GRBM and CP fields for idle polling, soft reset, ring management, and debug.
- AMDGPU SDMA v5 code (`amdgpu/sdma_v5_0.c`) includes this header for SDMA queue/ring and diagnostic register handling.
- KFD GFX10 queue and MQD code includes this header for compute queue metadata and packet programming.
- `gfxhub_v2_0.c`, `mxgpu_nv.c`, `nv.c`, and `amdgpu_amdkfd_gfx_v10.c` also integrate the generated GC 10.1.0 field definitions.

The file depends on AMDGPU's register helper conventions rather than C type checking. A macro pair is usually consumed by token pasting from register and field names, so spelling, casing, and register prefix must exactly match the generated offset/default headers and the consumers' `REG_*_FIELD` invocations.

## Risks And Edge Cases

- The range begins mid-register: lines 5194-5195 contain the first two `SDMA1_RLC6_IB_CNTL` shifts, while this work item starts at line 5196. A merged report needs the previous lines for the complete start-of-register context.
- The range ends mid-register: line 7635 contains the last `PA_SC_TILE_STEERING_CREST_OVERRIDE` shift, while the corresponding masks start at line 7636. The next chunk must complete that register.
- The constants are untyped preprocessor values. An incorrect mask or shift can compile cleanly but program or decode the wrong hardware bit.
- This is generated hardware metadata. Manual edits risk divergence from AMD's authoritative register database, companion offset/default headers, firmware expectations, and silicon documentation.
- SDMA ring/IB/doorbell fields are sequencing-sensitive. Wrong pointer, base, swap, VMID, AQL, preemption, or writeback fields can break queue progress, corrupt command streams, lose completions, or produce hangs that only appear under KFD or multi-queue workloads.
- GRBM status and reset fields are used in recovery paths. Incorrect busy masks can cause false idle detection, skipped resets, excessive resets, or timeout loops during GPU reset and suspend/resume.
- CP busy/stalled, halt/step/reset, queue threshold, and ring pointer fields are tightly coupled with firmware and microcode. Misdecoding them can hide command processor hangs or force a pipeline into an unrecoverable state.
- Error, IOV, trap, and interrupt-related fields may be write-clear or latch hardware faults. Consumers need to preserve documented semantics rather than blindly read/modify/write every field.
- PA/VGT/WD/GE fields affect draw front-end, primitive assembly, binning, rasterization, and cache invalidation. Regressions may show as rendering corruption, hangs, performance cliffs, or failures only with specific primitive types, NGG/tessellation paths, MSAA/binning modes, or multi-SE/RB configurations.
- `RESERVED` fields appear throughout the chunk. Driver code should preserve them unless AMD generation-specific programming guidance says otherwise.
- Similar macro names exist across GC generations and SDMA standalone headers. Mixing a GC 10.1.0 mask with another generation's offset, or with a similarly named SDMA-specific header, may compile but target incompatible field layouts.

## Test Signals

Useful validation for this chunk and its consumers includes:

- Build AMDGPU/KFD configurations that include Navi/GFX10 and SDMA v5 support; missing or renamed macros should fail compilation in `gfx_v10_0.c`, `sdma_v5_0.c`, KFD queue/MQD code, gfxhub, and NV virtualization paths.
- Mechanically compare this range against AMD's GC 10.1.0 register database and `gc_10_1_0_offset.h` to confirm each register has the expected field layout and width.
- Diff repeated SDMA1 RLC6/RLC7 groups against neighboring RLC contexts and SDMA generation headers to catch copy or generator drift while allowing intentional per-generation differences.
- Run boot, modeset, suspend/resume, GPU reset, compute queue creation/destruction, SDMA copy/fill, KFD queue scheduling, and mixed graphics/compute workloads on hardware using this register generation.
- Exercise reset and hang-recovery paths and watch for `GRBM_STATUS` idle timeouts, incorrect `GRBM_SOFT_RESET` selection, repeated CP busy/stalled states, and failed SDMA queue stop/restore.
- Inspect debugfs or register dumps for decoded GRBM, CP, SDMA, VGT, WD, GE, PA, and SC fields. Known-good dumps should decode queue pointers, busy flags, thresholds, FIFO sizes, binning controls, and tile steering consistently with hardware documentation.
- Stress workloads involving doorbells, AQL queues, preemption, indirect buffers, write-pointer polling, VMID switching, cache invalidation, streamout events, binning/PBB, MSAA/rasterizer enhancements, tessellation, and multi-shader-engine routing.
- Monitor for rendering corruption, command processor hangs, SDMA timeouts, missing interrupts, KFD queue failures, false idle detection, reset failures, and performance regressions after any generator or header update.

## Cross-Chunk Notes

The previous chunk owns the beginning of `SDMA1_RLC6_IB_CNTL`, including the register comment and the `IB_ENABLE`/`IB_SWAP_ENABLE` shift lines. This chunk resumes with `SWITCH_INSIDE_IB` and completes most subsequent SDMA1 RLC6/RLC7 queue definitions.

This chunk stops at `PA_SC_TILE_STEERING_CREST_OVERRIDE__FORCE_TILE_STEERING_OVERRIDE_USE__SHIFT`. The next chunk owns the masks for `PA_SC_TILE_STEERING_CREST_OVERRIDE` and then enters the `gc_sqdec` shader-queue address block.
