# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 22334-24790

## Scope And Purpose

This chunk is a generated AMD GC 10.1.0 register bitfield header segment. It contains C preprocessor constants for register field shifts and masks, not executable code. The constants describe how driver code should pack and unpack fields in GFX10 graphics-context registers for viewport/scissor state, rasterization, command-processor context IDs, color/depth/blend state, shader interpolation/export state, draw initiators, primitive assembly, clipping, setup, tessellation, and geometry-shader mode.

The chunk spans 2,457 lines and contains 294 register comment blocks, 1,085 `__SHIFT` macros, and 1,078 `_MASK` macros. It starts inside the `PA_SC_VPORT_SCISSOR_12_TL` block and ends inside `VGT_GS_MODE`; adjacent chunks are needed for the complete opening and closing register definitions.

## Register Areas Covered

The first section completes viewport scissor register definitions for viewports 12 through 15, then defines `PA_SC_VPORT_ZMIN_0..15` and `PA_SC_VPORT_ZMAX_0..15`. These are full-width 32-bit floating/depth payload fields used with viewport transform and depth range state. `PA_SC_RASTER_CONFIG`, `PA_SC_RASTER_CONFIG_1`, `PA_SC_SCREEN_EXTENT_CONTROL`, and `PA_SC_TILE_STEERING_OVERRIDE` describe shader-engine, shader-array, raster backend, packer, scan converter, tile-walk, and render-backend topology steering fields.

Command-processor and context identity registers include `CP_PERFMON_CNTX_CNTL`, `CP_PIPEID`, `CP_RINGID`, and `CP_VMID`. These expose small context fields and the high-bit `PERFMON_ENABLE` flag used when packet/ring/context code needs to stamp or filter GPU work.

Color-buffer and depth-buffer blocks include `CB_RMI_GL2_CACHE_CONTROL`, `CB_BLEND_RED/GREEN/BLUE/ALPHA`, `CB_DCC_CONTROL`, `CB_COVERAGE_OUT_CONTROL`, `DB_STENCIL_CONTROL`, `DB_STENCILREFMASK`, `DB_STENCILREFMASK_BF`, `DB_DEPTH_CONTROL`, `DB_EQAA`, `CB_COLOR_CONTROL`, and `DB_SHADER_CONTROL`. These macros cover cache policy, blend constants, DCC overwrite and key-clear behavior, coverage export, front/back stencil ops and masks, depth/stencil enable and compare controls, EQAA sample controls, ROP/color mode, and pixel-shader depth/coverage interactions.

Viewport, clipping, and user-clip-plane blocks include `PA_CL_VPORT_*` scale/offset registers for viewports 0 through 15, `PA_CL_UCP_0..5_{X,Y,Z,W}`, `PA_CL_PROG_NEAR_CLIP_Z`, `PA_CL_CLIP_CNTL`, `PA_CL_VTE_CNTL`, `PA_CL_VS_OUT_CNTL`, `PA_CL_NANINF_CNTL`, point radius/size/cull registers, and stereo registers. Most scale, offset, UCP, and point radius definitions are full-width data payloads; control registers expose individual enable and format bits for clip distances, cull distances, viewport transform, near/far clipping, DirectX clip-space behavior, NaN/Inf handling, and stereo render-target/viewport offsets.

Shader processor interface state is heavily represented. `SPI_PS_INPUT_CNTL_0..31` define repeated pixel-shader input mapping fields such as parameter offset, default values, flat shading, cylindrical wrapping, point-sprite texture selection, FP16 interpolation mode, duplicate/valid bits, and secondary-attribute selection. `SPI_PS_INPUT_ENA`, `SPI_PS_INPUT_ADDR`, `SPI_INTERP_CONTROL_0`, `SPI_PS_IN_CONTROL`, and `SPI_BARYC_CNTL` define interpolation modes and barycentric input selection. `SPI_TMPRING_SIZE`, `SPI_SHADER_IDX_FORMAT`, `SPI_SHADER_POS_FORMAT`, `SPI_SHADER_Z_FORMAT`, and `SPI_SHADER_COL_FORMAT` define temporary ring sizing and shader export formats for index, position, depth, and color outputs.

Blend and render-target optimization blocks include `SX_PS_DOWNCONVERT`, `SX_BLEND_OPT_EPSILON`, `SX_BLEND_OPT_CONTROL`, `SX_MRT0_BLEND_OPT..SX_MRT7_BLEND_OPT`, and `CB_BLEND0_CONTROL..CB_BLEND7_CONTROL`. These specify per-MRT downconversion formats, blend epsilon thresholds, independent MRT blend enable state, commutativity/discard optimization, color source/destination factors, color/alpha combine functions, and separate-alpha behavior.

Vertex-grouper/tessellation/geometry blocks include `VGT_DMA_BASE_HI`, `VGT_DMA_BASE`, `VGT_DRAW_INITIATOR`, `VGT_IMMED_DATA`, `VGT_EVENT_ADDRESS_REG`, `GE_MAX_OUTPUT_PER_SUBGROUP`, `VGT_OUTPUT_PATH_CNTL`, `VGT_HOS_CNTL`, `VGT_HOS_MAX_TESS_LEVEL`, `VGT_HOS_MIN_TESS_LEVEL`, `VGT_HOS_REUSE_DEPTH`, `VGT_GROUP_PRIM_TYPE`, `VGT_GROUP_FIRST_DECR`, `VGT_GROUP_DECR`, `VGT_GROUP_VECT_0/1_CNTL`, `VGT_GROUP_VECT_0/1_FMT_CNTL`, and the beginning of `VGT_GS_MODE`. These fields control draw initiation, DMA base addressing, event address writes, tessellation mode and levels, grouped primitive ordering, vector component packing, and GS execution mode flags.

## APIs, Types, And Macro Contract

There are no functions, structs, enums, or runtime control paths in this chunk. Its API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask at its final register position.
- Comment lines of the form `//REGISTER_NAME` group related field constants and serve as the only local structure.

Driver code combines these constants with register address macros from companion GC headers and with register access helpers such as SOC15/MMIO read-modify-write paths. The normal use pattern is to clear a field with the mask and insert a value shifted by the corresponding shift, or to extract a value by masking and shifting down. The constants are part of the kernel C preprocessor contract and must remain stable for code compiled against GC 10.1.0 register layouts.

## Control Flow

This file has no branches or function calls. Runtime control flow appears in consumers: AMDGPU and AMDKFD code include `gc/gc_10_1_0_sh_mask.h`, choose register values based on ASIC configuration, queue setup, graphics state, or golden-register programming, then write packed values to hardware registers. Clear-state tables such as `clearstate_gfx10.h` carry default values for many registers covered here, including viewport Z ranges, raster config, and CP context control, while this header provides the bit positions needed when code builds non-default values.

The ordering in the header follows hardware register ordering rather than software dependency order. Repeated register families, especially viewport and `SPI_PS_INPUT_CNTL_N`, are mechanically expanded. That repetition is important because packet-building or context-state code can address each numbered register independently while using identical field semantics.

## State And Persistence Behavior

The header itself has no mutable state and persists no data. The state it describes is GPU hardware context state. Values assembled with these masks may be stored in command buffers, context images, clear-state tables, queue descriptors, or written directly through MMIO/register programming paths. Once submitted, the fields affect persistent GPU context until overwritten by later context state, reset by clear-state initialization, or invalidated by GPU reset and power-management transitions.

Several blocks influence long-lived rendering behavior. Viewport and clip registers determine coordinate transforms and clipping across draws. DB/CB registers determine depth, stencil, color, coverage, blending, DCC, and compression behavior. SPI registers determine how shader inputs and exports are interpreted. VGT registers affect draw setup, tessellation, primitive grouping, and geometry-shader execution. Incorrect bit packing can therefore survive across many draws within a context and present as rendering corruption, hangs, memory faults, or invalid performance-counter behavior.

## Dependencies And Integration Points

This generated header depends on the GC 10.1.0 hardware register specification. It is paired with offset/address headers in `drivers/gpu/drm/amd/include/asic_reg/gc/`, default-value headers, and AMDGPU/KFD source files that include `gc/gc_10_1_0_sh_mask.h`.

Primary integration points include:

- AMDGPU GFX10 initialization and register programming, including golden settings, context state, clear-state initialization, graphics pipeline setup, and render/depth/blend programming.
- AMDKFD GFX10 queue and packet-management code that shares the GC register masks for compute/graphics queue configuration and context fields.
- Clear-state arrays such as `clearstate_gfx10.h`, where register defaults align with many names in this chunk.
- Mesa/userspace command streams indirectly, because userspace graphics APIs submit state that the kernel validates, schedules, resets, or restores using these hardware definitions.
- Hardware-generation compatibility code, where the same logical register names may differ between GC versions and must use the correct versioned mask header.

## Risks And Edge Cases

- This chunk starts and ends mid-register-block. `PA_SC_VPORT_SCISSOR_12_TL` is partially defined before line 22334, and `VGT_GS_MODE` has additional masks after line 24790. Any reconciliation or regeneration check must include neighboring chunks before judging completeness.
- Manual edits to generated masks are high risk. A single wrong shift or mask silently writes the wrong bitfield and can corrupt rendering, disable depth/stencil/blend behavior, select the wrong shader interpolation, or program invalid primitive/GS state.
- Many fields are full-width `0xFFFFFFFFL` payload masks. Callers must avoid shifting these values unnecessarily and must preserve intended IEEE float or raw register encoding semantics.
- Repeated families can hide copy/paste or generator errors. `SPI_PS_INPUT_CNTL_0..31`, viewport 0..15, MRT 0..7, and blend 0..7 should remain structurally consistent except where the hardware specification intentionally differs.
- Reserved fields appear in `VGT_GS_MODE` and similar registers. Consumers should not infer that reserved bits are safe to set just because masks are present; hardware programming sequences should follow the ASIC specification and golden settings.
- Register state crosses subsystem boundaries. A field used by graphics context restore, KFD queues, or power/reset paths can break only on specific ASICs, queue types, shader stages, or multi-engine configurations.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware-conformance oriented:

- Kernel build coverage for AMDGPU and AMDKFD configurations that include `gc/gc_10_1_0_sh_mask.h`.
- Static checks that every `__SHIFT`/`_MASK` pair is internally consistent, masks do not overlap unintentionally within a register, and repeated register families keep identical layouts where expected.
- Generated-header comparison against the authoritative GC 10.1.0 register database or upstream AMDGPU header.
- Smoke tests on GFX10 hardware for boot, suspend/resume, GPU reset, queue creation, graphics context restore, and clear-state programming.
- Rendering tests that exercise viewport/scissor/depth range, clipping, stencil, depth bounds, EQAA/MSAA, color blending, MRT formats, point/line/stipple state, tessellation, geometry shaders, and pixel-shader interpolation.
- GPU hang and fault monitoring during shader/export/blend/depth stress tests, because incorrect bitfield definitions often surface as command processor faults, VM faults, or ring timeouts rather than direct software errors.
