# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_1_sh_mask.h lines 4616-9227

## Scope

This chunk is a large middle slice of the generated AMD GFX 8.1 shift/mask register header. It contains C preprocessor constants only: each hardware register field is represented by `<REGISTER>__<FIELD>_MASK` and `<REGISTER>__<FIELD>__SHIFT` macros used to compose or decode 32-bit MMIO register values.

The range starts in the middle of command-processor HQD queue status/control definitions and then covers 713 distinct register macro families across these blocks:

- CP HQD end-of-pipe, context-save, GDS-resource, and queue error/status fields.
- DB depth/stencil surface, render, query, debug, performance counter, watermark, and cache/FIFO fields.
- CC/GC/GB render-backend redundancy, address configuration, tile-mode, macrotile-mode, and EDC/RAS signature fields.
- GRBM status, indexing, traps, read/write errors, soft reset, debug, scratch, and performance counter fields.
- PA_CL, PA_SU, and PA_SC viewport, clipping, point/line, polygon offset, rasterization, scissor, sample-location, trap-screen, debug, and performance counter fields.
- Clipper, SXIFCCG, and setup debug-register fields.
- Compute dispatch, program-resource, thread-management, wave-restore, user-data, CSPRIV connection, and thread-trace fields.
- RLC control, safe mode, memory sleep, clocking, performance monitoring, load-balance, GPM debug/microcode, GPU BIST, and the beginning of `RLC_ROM_CNTL`.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata. It has no Ceph or distributed filesystem behavior.

## Purpose

`gfx_8_1_sh_mask.h` is the bit-layout companion to the GFX 8.1 register-offset headers. Offset headers identify registers such as `DB_DEPTH_CONTROL`, `GRBM_GFX_INDEX`, `PA_SC_RASTER_CONFIG`, `COMPUTE_PGM_RSRC1`, and `RLC_CNTL`; this header identifies the fields inside those registers.

Driver code uses these definitions through common AMDGPU/KFD helper patterns such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, SOC15-era read/write wrappers in newer code, packet emission helpers, register dump code, and performance/debug tooling. The macros are the hardware ABI for GFX 8.1-era blocks: changing a mask or shift changes which hardware bits are read or written.

## Important Macro Families

### CP HQD Queue And EOP State

The opening CP section covers hardware queue descriptor fields for the command processor:

- `CP_HQD_HQ_STATUS1` and `CP_HQD_HQ_CONTROL1` expose full-width HQ status/control words.
- `CP_HQD_EOP_BASE_ADDR`, `CP_HQD_EOP_BASE_ADDR_HI`, `CP_HQD_EOP_CONTROL`, `CP_HQD_EOP_RPTR`, `CP_HQD_EOP_WPTR`, `CP_HQD_EOP_EVENTS`, `CP_HQD_EOP_WPTR_MEM`, and `CP_HQD_EOP_DONES` describe the end-of-pipe ring base, ring sizing, memory type/cache policy, read/write pointers, availability, event counts, and done counts.
- `CP_HQD_CTX_SAVE_*`, `CP_HQD_CNTL_STACK_*`, `CP_HQD_WG_STATE_OFFSET`, and `CP_HQD_CTX_SAVE_SIZE` define context-save backing storage and stack/state offsets.
- `CP_HQD_GDS_RESOURCE_STATE` tracks ordered-append/GWS requirements and allocation state for queues.
- `CP_HQD_ERROR` decodes HQD error status such as EDC and SUA error bits.

These fields integrate with KFD/amdgpu queue management and compute ring execution. The header does not describe the required queue suspend, drain, context-save, or EOP polling sequence; it only provides the bit positions used by that code.

### DB Depth, Stencil, Queries, And Debug

The DB block is the largest early section in the chunk. It defines depth and stencil surface programming:

- `DB_Z_READ_BASE`, `DB_STENCIL_READ_BASE`, `DB_Z_WRITE_BASE`, and `DB_STENCIL_WRITE_BASE` are full-width base-address fields in the hardware's expected alignment units.
- `DB_DEPTH_INFO`, `DB_Z_INFO`, `DB_STENCIL_INFO`, `DB_DEPTH_SIZE`, `DB_DEPTH_SLICE`, and `DB_DEPTH_VIEW` describe array mode, pipe/bank layout, tile split, format, sample count, compression/multisample state, pitch/height, slice range, and mip level.
- `DB_RENDER_CONTROL`, `DB_COUNT_CONTROL`, `DB_RENDER_OVERRIDE`, `DB_RENDER_OVERRIDE2`, `DB_EQAA`, `DB_SHADER_CONTROL`, `DB_DEPTH_CONTROL`, `DB_STENCIL_CONTROL`, and `DB_ALPHA_TO_MASK` define render policy, z/stencil compare behavior, hierarchical Z/stencil controls, EQAA sample/fragment rules, shader export interactions, alpha-to-mask behavior, and override/debug disables.
- `DB_DEPTH_BOUNDS_MIN/MAX`, `DB_STENCIL_CLEAR`, `DB_DEPTH_CLEAR`, `DB_HTILE_DATA_BASE`, `DB_HTILE_SURFACE`, `DB_PRELOAD_CONTROL`, `DB_STENCILREFMASK`, and `DB_STENCILREFMASK_BF` encode clear/reference/mask and HTILE metadata state.
- `DB_OCCLUSION_COUNT*`, `DB_ZPASS_COUNT_*`, and `DB_SRESULTS_COMPARE_STATE*` provide query/comparison counter fields.

The same block includes DB performance counters (`DB_PERFCOUNTER*_SELECT`, `*_SELECT1`, `*_LO`, `*_HI`), deep debug controls (`DB_DEBUG` through `DB_DEBUG4`), credit/watermark/cache controls, FIFO depths, clock-gating delay controls, ring control, and read-debug windows. Many of these are active hardware state or debug override knobs, not passive metadata.

### Render Backend, Addressing, Tile Modes, And RAS

The `CC_*`, `GC_USER_*`, `GB_*`, and `RAS_*` families describe chip-level graphics backend layout:

- `CC_RB_REDUNDANCY`, `CC_RB_BACKEND_DISABLE`, `GC_USER_RB_REDUNDANCY`, and `GC_USER_RB_BACKEND_DISABLE` expose render-backend disable/redundancy maps.
- `GB_ADDR_CONFIG` and `GB_BACKEND_MAP` describe pipe, bank, shader-engine, render-backend, row-size, and backend mapping fields used by surface/tile programming.
- `GB_TILE_MODE0` through `GB_TILE_MODE31` and `GB_MACROTILE_MODE0` through `GB_MACROTILE_MODE15` encode array mode, pipe config, tile split, micro tile mode, sample split, bank dimensions, macro aspect, and bank swizzle.
- `GB_EDC_MODE`, `CC_GC_EDC_CONFIG`, `RAS_SIGNATURE_CONTROL`, `RAS_SIGNATURE_MASK`, and the per-block `RAS_*_SIGNATURE*` registers expose EDC/RAS signature collection for SX, DB, PA/VGT/SC/IA/SPI/TA/TD/CB/BCI-style blocks.

These definitions are consumed by initialization, surface layout, diagnostics, and RAS paths. Incorrect values can corrupt tiling interpretation or hide/trigger backend and error-reporting behavior.

### GRBM Global Graphics Manager

The GRBM section spans status, routing, reset, trap, error, scratch, and profiling fields:

- `GRBM_HYP_CAM_INDEX`, `GRBM_CAM_INDEX`, `GRBM_*_CAM_DATA`, `GRBM_CNTL`, `GRBM_SKEW_CNTL`, and `GRBM_PWR_CNTL` configure low-level graphics-manager indexing, skew, and power controls.
- `GRBM_STATUS`, `GRBM_STATUS2`, and `GRBM_STATUS_SE0..SE3` expose busy/clean/active status across CP, VGT, IA, PA, SC, SPI, SX, DB, CB, GUI_ACTIVE, TAs, and per-shader-engine resources.
- `GRBM_SOFT_RESET`, `GRBM_DEBUG_CNTL`, `GRBM_DEBUG_DATA`, `GRBM_DEBUG`, `GRBM_DEBUG_SNAPSHOT`, `DEBUG_INDEX`, and `DEBUG_DATA` provide reset and debug access.
- `GRBM_GFX_INDEX` selects shader engine, shader array, instance, and broadcast routing for indexed register accesses.
- `GRBM_READ_ERROR`, `GRBM_READ_ERROR2`, `GRBM_WRITE_ERROR`, `GRBM_INT_CNTL`, and `GRBM_TRAP_*` decode MMIO access errors and trap address/data windows.
- `GRBM_PERFCOUNTER*` and `GRBM_SE*_PERFCOUNTER*` configure and read global/per-SE GRBM counters.
- `GRBM_SCRATCH_REG0..7`, `GRBM_NOWHERE`, and related full-width data fields provide scratch and discard/write sink registers.

GRBM fields are sensitive integration points because register routing and reset controls affect all graphics blocks behind GRBM. Callers must preserve broadcast/index state around per-instance register access and must not treat status/error registers as ordinary persistent configuration.

### PA_CL, PA_SU, And PA_SC Graphics Pipeline State

The PA block dominates the middle of the chunk and represents graphics viewport, clipping, setup, and rasterization state:

- `PA_CL_VPORT_*` defines viewport scale/offset for viewport 0 plus indexed viewport 1 through 15 variants.
- `PA_CL_VTE_CNTL`, `PA_CL_VS_OUT_CNTL`, `PA_CL_NANINF_CNTL`, `PA_CL_CLIP_CNTL`, guard-band adjustment registers, and `PA_CL_UCP_*` define viewport transform enable, vertex-shader output interpretation, NaN/Inf handling, clip/discard policy, guard-band clipping, and user clip planes.
- `PA_CL_POINT_*` and `PA_CL_ENHANCE` cover point radius/size and clipper enhancement/debug behavior.
- `PA_SU_VTX_CNTL`, `PA_SU_POINT_*`, `PA_SU_LINE_*`, `PA_SU_PRIM_FILTER_CNTL`, `PA_SU_SC_MODE_CNTL`, `PA_SU_POLY_OFFSET_*`, `PA_SU_HARDWARE_SCREEN_OFFSET`, and `PA_SU_LINE_STIPPLE_VALUE` define setup-unit point/line, primitive filtering, culling/front-face/fill, polygon offset, and line stipple state.
- `PA_SC_AA_CONFIG`, `PA_SC_AA_MASK_*`, `PA_SC_AA_SAMPLE_LOCS_PIXEL_*`, and `PA_SC_CENTROID_PRIORITY_*` describe multisample configuration, sample masks, per-sample locations, and centroid selection.
- `PA_SC_CLIPRECT_*`, `PA_SC_EDGERULE`, `PA_SC_LINE_*`, `PA_SC_MODE_CNTL_*`, `PA_SC_RASTER_CONFIG`, `PA_SC_RASTER_CONFIG_1`, `PA_SC_GENERIC_SCISSOR_*`, `PA_SC_SCREEN_SCISSOR_*`, `PA_SC_WINDOW_*`, `PA_SC_VPORT_SCISSOR_*`, and `PA_SC_VPORT_ZMIN/ZMAX_*` encode rasterizer routing, scissor rectangles, screen/window bounds, viewport scissor rectangles, and depth ranges.
- `PA_SC_ENHANCE`, `PA_SC_ENHANCE_1`, `PA_SC_DSM_CNTL`, FIFO size fields, EOV max counts, line-stipple state, screen extent fields, trap-screen registers, clock controls, and debug controls expose implementation-specific tuning and diagnostics.
- `PA_SU_PERFCOUNTER*` and `PA_SC_PERFCOUNTER*` define PA setup/scanner performance counter selectors and low/high data words.

These macros back user-visible graphics behavior: viewport transforms, clipping, culling, polygon offset, scissor, depth range, AA sample locations, and rasterization can all be affected by wrong field definitions.

### Clipper, SXIFCCG, And Setup Debug

`CLIPPER_DEBUG_REG00` through `CLIPPER_DEBUG_REG19`, `SXIFCCG_DEBUG_REG0` through `SXIFCCG_DEBUG_REG3`, and `SETUP_DEBUG_REG0` through `SETUP_DEBUG_REG5` are dense debug and tuning registers. Their fields include bypass/disables, FIFO and arbitration controls, event/debug selectors, stall controls, primitive and clipper counters, and implementation-specific extra debug payloads.

These definitions are mostly diagnostic or bring-up oriented. They should be used from debug paths or known-good init tables rather than opportunistically changed in normal rendering paths.

### Compute Dispatch And CSPRIV State

The compute section describes command-processor compute-dispatch programming:

- `COMPUTE_DISPATCH_INITIATOR` defines dispatch mode, dimensionality, partial-TG handling, thread-trace, and launch-policy bits.
- `COMPUTE_DIM_*`, `COMPUTE_START_*`, `COMPUTE_NUM_THREAD_*`, and `COMPUTE_RESTART_*` describe grid dimensions, starting coordinates, workgroup thread dimensions, and restart coordinates.
- `COMPUTE_PGM_LO/HI`, `COMPUTE_TBA_LO/HI`, `COMPUTE_TMA_LO/HI`, `COMPUTE_PGM_RSRC1`, and `COMPUTE_PGM_RSRC2` describe shader program addresses, trap/metadata addresses, VGPR/SGPR counts, priority, float mode, DX10 clamp, debug mode, LDS size, scratch enable, user SGPR count, trap handler, and TGID/XNACK-related resources.
- `COMPUTE_VMID`, `COMPUTE_RESOURCE_LIMITS`, `COMPUTE_STATIC_THREAD_MGMT_SE0..SE3`, and `COMPUTE_TMPRING_SIZE` define VMID, CU masks/resource limits, per-SE thread management, and scratch/temp-ring sizing.
- `COMPUTE_THREAD_TRACE_ENABLE`, `COMPUTE_MISC_RESERVED`, `COMPUTE_DISPATCH_ID`, `COMPUTE_THREADGROUP_ID`, `COMPUTE_RELAUNCH`, `COMPUTE_WAVE_RESTORE_*`, and `COMPUTE_USER_DATA_0..15` expose tracing, dispatch identification, wave relaunch/restore, and user SGPR payload state.
- `CSPRIV_CONNECT` maps doorbell offset, queue ID, VMID, and unordered-dispatch behavior; `CSPRIV_THREAD_TRACE_TG*` and `CSPRIV_THREAD_TRACE_EVENT` expose compute thread-trace group/event fields.

These fields integrate with KFD queues, compute rings, shader dispatch packet emission, debugger/trap support, and thread tracing. Program-resource fields are especially ABI-sensitive because they must match compiler-generated shader metadata.

### RLC, Clocking, Load Balance, GPM, And BIST

The final section covers run-list controller state:

- `RLC_CNTL`, `RLC_DEBUG_SELECT`, `RLC_DEBUG`, `RLC_MC_CNTL`, and `RLC_STAT` define enable/step/cache controls, debug selection/data, memory-controller request attributes, and busy status.
- `RLC_SAFE_MODE`, `RLC_RLCV_SAFE_MODE`, `RLC_SMU_SAFE_MODE`, `SMU_RLC_RESPONSE`, and `RLC_RLCV_COMMAND` provide command/response fields for safe-mode or SMU/RLCV coordination.
- `RLC_MEM_SLP_CNTL`, `RLC_CLK_CNTL`, `RLC_PERFMON_CLK_CNTL`, `CGTT_RLC_CLK_CTRL`, `CGTT_PA_CLK_CTRL`, and `CGTT_SC_CLK_CTRL` define memory sleep, clock, on-delay, off-hysteresis, and soft override controls.
- `RLC_PERFMON_CNTL`, `RLC_PERFCOUNTER*_SELECT`, and `RLC_PERFCOUNTER*_LO/HI` define RLC profiling state.
- `RLC_LB_CNTL`, `RLC_LB_CNTR_MAX`, `RLC_LB_CNTR_INIT`, and `RLC_LOAD_BALANCE_CNTR` expose RLC load-balance control/counter fields.
- `RLC_JUMP_TABLE_RESTORE`, `RLC_PG_DELAY_2`, `RLC_GPM_DEBUG_SELECT`, `RLC_GPM_DEBUG`, `RLC_GPM_DEBUG_INST_*`, `RLC_GPM_UCODE_ADDR`, and `RLC_GPM_UCODE_DATA` expose firmware/GPM debug and microcode-address/data paths.
- `GPU_BIST_CONTROL` configures BIST stop-on-fail and loop-count fields.
- The chunk ends at `RLC_ROM_CNTL__SLP_MODE_EN_MASK`; its corresponding shift and later `RLC_ROM_CNTL` fields are outside this chunk.

RLC controls are power-management and firmware-adjacent integration points. Safe-mode, microcode, sleep, and clock fields can affect register accessibility and GPU liveness.

## APIs, Types, And Functions

This chunk defines no C functions, types, structs, enums, storage, callbacks, locks, or exported symbols. Its API surface is the macro namespace itself. The naming convention is consistent:

- `REGISTER__FIELD_MASK` gives the already-shifted bit mask for a field.
- `REGISTER__FIELD__SHIFT` gives the field's least-significant bit position.
- Full-width data/address/counter fields usually use mask `0xffffffff` and shift `0x0`.
- Reserved fields are present for documentation of hardware bit layout, but consumers should generally preserve reserved bits in read-modify-write flows unless writing a trusted full-register init value.

Because the header is generated hardware metadata, consumers depend on exact spelling. A typo is usually a compile-time break for direct users, but a semantically wrong numeric mask may compile cleanly and misprogram hardware.

## Control Flow

There is no runtime control flow in this chunk. It contains only preprocessor definitions. The implied runtime flow is:

1. GFX 8.1 AMDGPU/KFD code includes the appropriate offset and shift/mask headers.
2. A call site selects a register offset and target instance, sometimes through GRBM indexed access.
3. The call site uses these macros through `REG_SET_FIELD`, `REG_GET_FIELD`, or equivalent bit operations.
4. The resulting value is emitted through MMIO reads/writes, packetized command streams, queue programming, debugfs/register-dump paths, profiler paths, or firmware/RLC control flows.

Ordering rules, locking, polling loops, timeout handling, reset sequences, cache flushes, W1C/W1S behavior, and privilege checks are implemented in surrounding driver code and hardware/firmware protocols, not here.

## State And Persistence Behavior

The macros themselves hold no software state and persist nothing. They describe hardware-visible state with different lifetimes:

- DB/PA/compute registers hold context or command state that persists until another context restore, command packet, reset, or explicit write changes it.
- CP HQD and CSPRIV fields describe queue state, doorbell routing, VMID, context-save storage, EOP rings, and completion counters that are shared with hardware execution.
- GB tile/macrotile and backend fields are chip-configuration state used by surface layout and render backend routing.
- GRBM index, reset, trap, and debug fields affect global routing and access to per-instance graphics registers.
- RAS/EDC signature and error/status fields are diagnostic hardware state, potentially latched or sticky depending on the underlying register.
- Performance counters are hardware-updated while enabled; low/high halves may need a coherent sampling sequence outside this header.
- RLC safe-mode, clock, memory sleep, microcode, and BIST fields can alter power/firmware behavior and may need handshakes before and after writes.

Any read-modify-write sequence using these macros should preserve unrelated fields unless the caller intentionally owns the full register value.

## Dependencies And Integration Points

The header depends only on the C preprocessor and the include guard at the top of the file. Practical consumers depend on:

- Sibling GFX 8.1 register offset headers that define the register addresses.
- AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, indexed GRBM access helpers, and command-stream packet builders.
- KFD queue management for CP HQD and compute/CSPRIV programming.
- Graphics command emission for DB/PA/GB/GRBM state and render context setup.
- RAS/debug/performance infrastructure for EDC signatures, status/error decoding, performance counters, thread trace, debug-index/data, and register dumps.
- RLC firmware and power-management code for safe mode, clock gating, memory sleep, GPM debug, microcode address/data, and BIST controls.

The file path is source-tree-aligned under `drivers/gpu/drm/amd/include/asic_reg/gca`, so merged research should stay attached to the AMDGPU generated-register-header area rather than to Ceph storage code.

## Risks And Edge Cases

- The chunk begins and ends on macro boundaries chosen by line range, not by semantic register family. It starts after prior `CP_HQD_HQ_STATUS1` definitions and ends halfway through `RLC_ROM_CNTL`; the next chunk must complete that family.
- These macros are ASIC-specific. Reusing a GFX 8.1 mask with a nearby but different ASIC generation can silently program the wrong bits.
- Full-width-looking fields can be addresses, counters, opaque debug payloads, or command data. Callers must still respect register-specific alignment, latching, side effects, and ordering.
- Debug and override registers such as `DB_DEBUG*`, `CLIPPER_DEBUG_REG*`, `SETUP_DEBUG_REG*`, `SXIFCCG_DEBUG_REG*`, `GRBM_DEBUG*`, and `RLC_GPM_*` can disable optimizations, force misses/stalls, alter clocking, or expose implementation state.
- `GRBM_GFX_INDEX` changes which shader engine/array/instance subsequent indexed register accesses target; failure to restore broadcast/default state can misdirect later writes.
- Performance counters and status registers can change while being read. Split low/high counters need the sampling protocol used by the owning performance code.
- Reserved masks appear in several registers. Treating reserved bits as writable feature flags can cause undefined hardware behavior.
- Surface-layout fields in `DB_*`, `GB_TILE_MODE*`, `GB_MACROTILE_MODE*`, and `GB_ADDR_CONFIG` are high blast-radius: wrong fields can corrupt depth/stencil rendering, compression metadata, or tiling interpretation.
- Compute program resource fields must agree with shader compiler metadata and queue ABI; wrong VGPR/SGPR/LDS/scratch/user-SGPR values can hang waves or produce invalid execution.
- RLC safe-mode, memory sleep, clock, GPM microcode, and BIST controls may require firmware/SMU handshakes that are not represented by masks alone.

## Test Signals

Useful validation signals for changes touching this header or generated-register consumers include:

- Kernel build coverage for AMDGPU/KFD configurations that include GFX 8.1-era ASIC support; macro spelling mistakes should fail compilation at direct call sites.
- Static comparison against AMD's authoritative generated register database or known-good upstream `gfx_8_1_sh_mask.h` to detect numeric mask/shift drift.
- Boot and GPU reset smoke tests on affected GFX 8.1 hardware, watching for GRBM busy bits clearing, RLC safe-mode handshakes completing, and absence of GPU hangs.
- KFD queue tests that create/destroy compute queues, dispatch kernels, exercise doorbells, EOP completion, and context-save/restore behavior.
- Graphics rendering tests that cover depth/stencil, HTILE, EQAA/MSAA, scissor/viewport, polygon offset, line/point rasterization, tile/macrotile modes, and occlusion/Z-pass queries.
- Performance counter and debug tooling tests that select DB/GRBM/PA/RLC counters and verify nonzero, coherent counter updates under workload.
- RAS/debug register dump tests that decode GRBM read/write errors, RAS signatures, and DB/PA/RLC debug data without malformed field extraction.
