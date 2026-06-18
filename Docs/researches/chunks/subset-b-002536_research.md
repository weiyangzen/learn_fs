# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 24657-27046

## Scope

This chunk is a generated AMD GC 11.0.3 shift/mask header slice. It contains only C preprocessor constants for hardware register bit positions and masks. There are no functions, structs, enums, global variables, allocations, locks, direct MMIO operations, or executable branches in this range.

The requested lines contain 2,177 `#define` statements: 1,089 `__SHIFT` macros and 1,088 `_MASK` macros. The chunk starts inside the `PA_CL_NGG_CNTL` register group, immediately after the `//PA_CL_NGG_CNTL` comment in the previous line, and ends inside the `SQ_DEBUG` group before `SQ_DEBUG__WAIT_DEP_CTR_ZERO_MASK` on the following line.

Although the path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU DRM graphics-core register metadata and is not Ceph filesystem logic.

## Purpose

`gc_11_0_3_sh_mask.h` describes the bit layout of AMD graphics core 11.0.3 registers. Driver code combines these field definitions with register offsets from the matching offset header and helper macros to construct, update, and decode 32-bit register values without open-coded bit numbers.

This slice covers graphics pipeline state across primitive assembly, rasterization, depth/stencil, color-buffer render targets, PF/VF command controls, GRBM queue selection, PA/SC tuning, and early SQ memory/debug state. It is primarily used by graphics setup, clear-state programming, context state packets, virtualization/control paths, KFD memory configuration, and debug or hang-diagnosis code.

The main register surfaces are:

- PA/SC/VGT frontend and rasterization controls for NGG vertex reuse, over-rasterization, stereo rendering, variable-rate shading, point and line state, tessellation distribution, shader-stage enablement, primitive IDs, event initiation, streamout opaque draw state, polygon offset, centroid/sample locations, conservative rasterization, and NGG/binning behavior.
- DB depth/stencil-related controls for HTILE surface metadata, sample-result compare state, preload windows, and alpha-to-mask behavior.
- CB color target state for render targets 0 through 7, including base addresses, views, format/type/component-swap fields, fragment/sample/compression attributes, DCC/FDCC metadata bases, extended address bits, mip dimensions, swizzle mode, resource type, and pipe-alignment flags.
- PF/VF command and GRBM controls for reserved config data, MEC/ME reset/halt/step/cache-invalidate bits, and GRBM selection of pipe, ME, VMID, queue, and context.
- PA/SC and PA/PH maintenance registers for VRS surface control, out-of-order/packer/binning enhancement knobs, FIFO sizing, wave ID controls, ATM/PKR controls, binner event routing, binner performance thresholds, trap-screen write locks, and PA/PH interface clock/performance controls.
- SQ/SPI-adjacent state for runtime configuration, SQ global busy/wave/fifo status, shader memory bases/configuration, and the beginning of SQ single-step/debug controls.

## Important APIs, Types, And Macros

The only API surface in this chunk is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives a field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the in-register mask for that field.
- `//<REGISTER>` comments mark register boundaries.
- `// addressBlock: gc_pfvf_cpdec`, `gc_pfvf_grbmdec`, `gc_pfvf_padec`, and `gc_pfvf_sqdec` mark generated address-block transitions.

There are no callable functions or C types. Runtime consumers normally use these definitions through AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, and packet-building paths that token-paste register and field names.

Important PA/SC/VGT/DB families include:

- `PA_CL_NGG_CNTL`, `GE_NGG_SUBGRP_CNTL`, `PA_SC_NGG_MODE_CNTL`, and `VGT_SHADER_STAGES_EN`, which define NGG/primitive-generator enablement, wave32 flags for shader stages, primitive pass-through controls, sub-group sizing, and vertex reuse behavior.
- `PA_SU_OVER_RASTERIZATION_CNTL`, `PA_SC_CONSERVATIVE_RASTERIZATION_CNTL`, and `PA_SC_SHADER_CONTROL`, which shape zero-area primitive discard, conservative rasterization, out-of-order modes, scissor interaction, kill/stencil/depth behavior, and pixel-shader routing.
- `PA_STEREO_CNTL`, `PA_STATE_STEREO_X`, and `VGT_DRAW_PAYLOAD_CNTL`, which expose stereo, render-target slice, viewport ID, FSR, primitive payload, draw viewport, VRS-rate, and register RT-index payload fields.
- `PA_CL_VRS_CNTL`, `PA_SC_VRS_SURFACE_CNTL`, and `PA_SC_VRS_SURFACE_CNTL_1`, which describe rate combiner modes, exposed VRS pixels, cmask rate hints, VRS feedback/cache behavior, forced fine-rate controls, SSAA normalization overrides, and VRS spare bits.
- `PA_SU_POINT_SIZE`, `PA_SU_POINT_MINMAX`, `PA_SU_LINE_CNTL`, `PA_SC_LINE_CNTL`, `PA_SC_LINE_STIPPLE`, and `PA_SU_VTX_CNTL`, which cover point/line sizing, stipple, vertex quantization, pixel-center mode, and provoking-vertex details.
- `VGT_TESS_DISTRIBUTION`, `VGT_LS_HS_CONFIG`, and `VGT_TF_PARAM`, which describe tessellation accumulation, patch/input/output control point counts, topology, partitioning, distribution mode, memory type, and related request policy fields.
- `VGT_DMA_SIZE`, `VGT_DMA_MAX_SIZE`, `VGT_DMA_INDEX_TYPE`, `VGT_DMA_NUM_INSTANCES`, `VGT_PRIMITIVEID_EN`, `VGT_PRIMITIVEID_RESET`, `VGT_EVENT_INITIATOR`, `VGT_ESGS_RING_ITEMSIZE`, `VGT_GS_INSTANCE_CNT`, `VGT_GS_MAX_VERT_OUT`, and streamout opaque draw registers, which define draw/index/event/primitive-ID state.
- `DB_HTILE_SURFACE`, `DB_SRESULTS_COMPARE_STATE0/1`, `DB_PRELOAD_CONTROL`, `DB_ALPHA_TO_MASK`, and `PA_SU_POLY_OFFSET_*`, which represent depth-buffer metadata, compare-state windows, preload rectangles, alpha-to-mask offsets, and polygon depth bias settings.

Important color-buffer families include:

- `CB_COLOR0_BASE` through `CB_COLOR7_BASE` and `CB_COLOR0_DCC_BASE` through `CB_COLOR7_DCC_BASE`, full-width 256-byte-aligned base-address low fields for color surfaces and DCC metadata.
- `CB_COLOR0_VIEW` through `CB_COLOR7_VIEW`, which split slice start, slice max, and mip level.
- `CB_COLOR0_INFO` through `CB_COLOR7_INFO`, which define render target format, number type, component swap, blend clamp/bypass, simple float, round mode, and blend optimizations.
- `CB_COLOR0_ATTRIB` through `CB_COLOR7_ATTRIB`, `CB_COLOR*_FDCC_CONTROL`, `CB_COLOR*_ATTRIB2`, and `CB_COLOR*_ATTRIB3`, which cover fragment counts, FMASK/no-alloc optimizations, compression block sizes, color transform, constant encode controls, FDCC/DCC enable and disable controls, mip0 dimensions, max mip, metadata linearity, swizzle mode, resource type, and pipe alignment.
- `CB_COLOR*_BASE_EXT` and `CB_COLOR*_DCC_BASE_EXT`, which provide the high address bits for base and DCC base programming.

Important control/debug families include:

- `CONFIG_RESERVED_REG0/1`, full-width PF/VF config data placeholders.
- `CP_MEC_CNTL` and `CP_ME_CNTL`, which expose pipe reset, pipe disable, instruction cache invalidate, halt, and step controls for MEC, CE, PFP, and ME engines.
- `GRBM_GFX_CNTL` and `GRBM_NOWHERE`, which provide graphics-register routing fields for pipe, ME, VMID, queue, context, and a discard-style data register.
- `PA_SC_ENHANCE`, `PA_SC_ENHANCE_1`, `PA_SC_ENHANCE_2`, `PA_SC_ENHANCE_3`, `PA_SC_BINNER_CNTL_*`, `PA_SC_BINNER_EVENT_CNTL_0..3`, and `PA_SC_BINNER_PERF_CNTL_*`, which expose a large set of rasterizer/binning overrides, event-to-binner hooks, thread trace markers, pipeline done controls, statistics dumps/resets, and histogram thresholds.
- `PA_SC_P3D_TRAP_SCREEN_HV_LOCK`, `PA_SC_HP3D_TRAP_SCREEN_HV_LOCK`, and `PA_SC_TRAP_SCREEN_HV_LOCK`, each providing a non-privileged write-lock bit for trap-screen registers.
- `PA_PH_INTERFACE_FIFO_SIZE` and `PA_PH_ENHANCE`, which configure PA/PH interface FIFO sizing, clock-gating disables, perf-counter sampling behavior, and PH/SPI/GE throttling.
- `SQ_RUNTIME_CONFIG`, `SQ_DEBUG_STS_GLOBAL`, `SQ_DEBUG_STS_GLOBAL2`, `SH_MEM_BASES`, `SH_MEM_CONFIG`, and the partial `SQ_DEBUG` group, which describe SQ runtime presence, busy/interrupt busy state, per-shader-array wave levels, register FIFO levels, private/shared memory bases, addressing/alignment/prefetch/cache policy, and debug single-step control fields.

## Control Flow

This header has no runtime control flow. It affects runtime behavior only when C code expands these macros while composing or decoding register values.

The implied driver flow is:

1. Driver code selects a GC 11.0.3 register offset from `gc_11_0_3_offset.h`.
2. It reads, writes, or read-modify-writes the register through AMDGPU SOC15/MMIO helpers or emits the register value into a command stream/state packet.
3. It uses the `__SHIFT` and `_MASK` pair, often through `REG_SET_FIELD` or `REG_GET_FIELD`, to isolate or set the desired field.
4. The hardware PA/SC/VGT/DB/CB/CP/GRBM/SQ blocks perform the actual graphics, command, memory, or debug behavior.

For graphics state, higher-level code programs shader-stage enablement, primitive assembly, tessellation, rasterizer, depth/stencil, sample-location, binner, VRS, and color-target registers in a hardware-defined order. This chunk describes the fields but does not enforce register sequencing, cache flushes, compression transitions, render-target layout rules, or event ordering.

For command/control state, CP and GRBM code can use these fields to halt or step engines, reset pipes, invalidate micro-engine instruction caches, and select a queue/context register aperture. The macros do not encode which bits are write-one, self-clearing, privileged, PF/VF-only, or safe to touch while queues are active.

For SQ state, KFD/AMDGPU paths can program `SH_MEM_CONFIG` and `SH_MEM_BASES` for process memory behavior and read `SQ_DEBUG_STS_GLOBAL*` for hang/debug status. This chunk only names the fields; memory-model, VMID/PASID, trap, and wavefront semantics live in hardware and the surrounding driver.

## State And Persistence Behavior

The macros themselves are stateless compile-time constants. Persistent and volatile state exists only in GPU registers, command-stream state, context state images, firmware-owned queues, render-target memory, metadata surfaces, and debug/status latches.

Graphics state described in this chunk persists until overwritten by a later command stream, clear-state restore, context switch, queue teardown, GPU reset, suspend/resume, power-gating loss, or firmware/hardware context save/restore. That includes shader-stage enablement, tessellation parameters, primitive ID state, event initiators, rasterizer controls, VRS controls, sample locations, polygon offset, binner configuration, and render-target state.

Color-buffer state is especially persistent because it describes memory addresses and layout metadata for active render targets. `CB_COLOR*_BASE`, `CB_COLOR*_BASE_EXT`, `CB_COLOR*_DCC_BASE`, `CB_COLOR*_DCC_BASE_EXT`, `CB_COLOR*_INFO`, and `CB_COLOR*_ATTRIB*` must match the actual backing BO, swizzle mode, format, mip/slice view, compression mode, and synchronization state. Misaligned or stale values can persist across draws until the pipeline state is explicitly changed.

Control/debug state has mixed semantics. CP halt/step/reset/cache-invalidate bits may be command-like or self-clearing, GRBM selection fields route subsequent register accesses, trap-screen lock bits enforce privilege boundaries, and SQ status bits reflect live hardware activity. The generated header does not classify access side effects, so consumers must rely on hardware docs and established driver sequences.

Reserved, spare, and ECO fields occur throughout this range. Consumers should preserve these bits in read-modify-write sequences unless generation-specific documentation or existing driver code explicitly says to write a known value.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.0.3 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h` supplies matching register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_default.h` supplies generated reset/default values where present.
- AMDGPU register helper macros and SOC15 MMIO helpers perform actual field packing, reads, writes, and read-modify-writes.
- Direct include users in this tree include `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.c`, `gfxhub_v3_0_3.c`, and `imu_v11_0_3.c`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_gfx11.h` contains clear-state entries for many registers named in this chunk, including `VGT_SHADER_STAGES_EN`, `PA_SC_BINNER_CNTL_*`, and the repeated `CB_COLOR*` render-target groups.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v11.c` programs `SH_MEM_CONFIG`, integrating the SQ memory configuration fields with KFD process/queue behavior.

Runtime integration points include graphics pipeline state emission, clear-state initialization, render-target and DCC programming, VRS and sample-position setup, depth/stencil state, binner and out-of-order rasterization tuning, command processor reset/debug, GRBM register routing, KFD memory configuration, hang diagnosis, and register-dump decoding.

## Risks And Edge Cases

- Generated-header drift is the main risk. An incorrect shift or mask can compile cleanly while setting the wrong hardware bit.
- This work item starts inside `PA_CL_NGG_CNTL` and ends inside `SQ_DEBUG`. The previous chunk owns the register comment for the first group, and the next line after this chunk completes the `SQ_DEBUG__WAIT_DEP_CTR_ZERO` mask.
- Many register families are repeated for render targets 0 through 7. Mechanical similarity makes copy/paste or generated-data errors hard to spot, especially for `CB_COLOR*_INFO`, `CB_COLOR*_FDCC_CONTROL`, `CB_COLOR*_ATTRIB2`, and `CB_COLOR*_ATTRIB3`.
- Color target address and metadata fields are layout-sensitive. Wrong base, high address, DCC base, swizzle, resource type, mip dimensions, or compression bits can corrupt render targets, break resolves, or cause GPU faults.
- Compression and FDCC/DCC controls interact with cache flushing, metadata transitions, and render backend behavior. The masks alone do not describe required synchronization.
- VRS, conservative rasterization, sample-location, centroid, and alpha-to-mask fields can subtly change image correctness. Errors may appear only in specific MSAA, VRS, stereo, or shader-kill combinations.
- `VGT_SHADER_STAGES_EN`, tessellation, NGG, and primitive payload fields are tightly coupled to shader program state. Mismatched wave32, primitive-generation, LS/HS/GS/VS, or pass-through settings can hang draws or produce invalid geometry.
- `CP_MEC_CNTL` and `CP_ME_CNTL` bits affect engine halt, step, reset, and cache invalidation. Accidental writes while queues are active can stall command submission or disturb firmware-managed engines.
- `GRBM_GFX_CNTL` changes the selected pipe/ME/queue/context aperture for following accesses. Stale selection state can make subsequent debug or RLC/CP accesses observe or modify the wrong queue.
- `SQ_DEBUG_STS_GLOBAL*` are live status surfaces. Decoding errors can mislead hang triage by reporting wrong busy, wave-level, or FIFO occupancy values.
- Reserved, spare, and ECO fields appear in DB, PA_SC, PA_PH, and VRS controls. Full-register writes that ignore reserved-bit preservation may introduce generation-specific instability.

## Test Signals

Useful validation is a mix of generated-data checks, build coverage, and hardware exercise:

- Build AMDGPU configurations that include GC 11.0.3 support. Missing or malformed macros should surface in `gfx_v11_0_3.c`, `gfxhub_v3_0_3.c`, `imu_v11_0_3.c`, KFD GFX11 code, or clear-state-related paths.
- Mechanically compare every `__SHIFT` and `_MASK` in lines 24657-27046 against AMD's authoritative GC 11.0.3 register database.
- Cross-check that each register in this chunk has matching entries in `gc_11_0_3_offset.h` and, where expected, default values in `gc_11_0_3_default.h`.
- Run mask/shift consistency checks: masks should align with shifts, full-width data/address fields should use `0xFFFFFFFFL`, high address extension fields should use the expected low-bit width, and repeated `CB_COLOR0..7` families should remain structurally identical where hardware says they should.
- Boot affected GC 11.0.3 hardware and run graphics tests that exercise MSAA sample locations, VRS, conservative rasterization, tessellation, NGG, primitive ID reset, streamout opaque draws, polygon offset, depth/stencil compare, alpha-to-mask, and stereo/RT-slice state.
- Exercise render-target formats, views, mip/slice ranges, DCC/FDCC compression, extended base addresses, and swizzle/resource-type combinations while checking for corruption, resolve failures, VM faults, or render backend errors.
- Exercise queue halt/reset/debug flows and register-dump tooling that use `CP_MEC_CNTL`, `CP_ME_CNTL`, `GRBM_GFX_CNTL`, and SQ status fields.
- Exercise KFD process/queue creation and memory configuration paths that program `SH_MEM_CONFIG`, including address mode, alignment mode, instruction prefetch, and GL1 icache-use behavior.
- Decode known-good register dumps with these masks and compare against reference tooling, especially for `CB_COLOR*`, PA/SC binner/VRS controls, CP engine controls, GRBM queue selection, and SQ busy/wave/fifo state.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002536`. The final per-file research should merge it with neighboring chunks for complete `gc_11_0_3_sh_mask.h` coverage. The previous chunk should provide the line immediately before this slice, including the `//PA_CL_NGG_CNTL` boundary comment, while the next chunk should complete `SQ_DEBUG` with `SQ_DEBUG__WAIT_DEP_CTR_ZERO_MASK` and continue into SQ trap-memory address registers.
