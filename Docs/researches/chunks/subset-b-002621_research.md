# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_sh_mask.h lines 14706-17177

## Scope

This chunk is a generated AMD GC 9.0 shift/mask register-header segment. It contains C preprocessor constants only: each register field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro for composing or decoding 32-bit GPU register values. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines begin in the tail of `CB_TARGET_MASK` mask definitions, then cover a large graphics-pipeline state block: color-buffer target and shader masks, scissor and viewport state, raster/tile steering, command-processor context IDs, color/depth/stencil/blend controls, viewport transforms, user clip planes, pixel shader interpolation inputs, SPI shader export formats, SX blend optimizations, draw initiator fields, depth/color shader controls, clipping/setup controls, and the beginning of VGT tessellation state. Although the path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata, not Ceph filesystem logic.

## Purpose

`gc_9_0_sh_mask.h` supplies bit layouts for the GC 9.0 graphics IP. Driver code pairs these masks with register addresses from the matching `gc_9_0_offset.h` header and uses AMDGPU register helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` to pack fields before MMIO writes, command-packet programming, or firmware setup, and to decode status/debug reads.

This chunk describes the late fixed-function and shader-interface state used by draw setup:

- CB target/shader output enable masks and per-MRT blend constants, blend equations, color control, DCC overwrite-combiner behavior, down-conversion, blend optimization epsilon/control, MRT blend optimization, and expanded pitch.
- PA/SC scissor, viewport Z bounds, raster mapping, screen extents, tile steering, grid quantization, line stipple, point/line sizing, primitive filtering, small-primitive filtering, over-rasterization, and setup/clipping modes.
- CP pipe/ring/VMID and performance-monitor context fields that associate packet execution with hardware context state.
- DB stencil, stencil reference/masks, depth test/write control, EQAA/sample control, and pixel-shader depth/stencil/coverage export policy.
- PA/CL viewport scale/offset registers for 16 viewports, six user clip-plane vectors, clip control, viewport transform enablement, vertex output control, NaN/Inf policy, object/primitive ID control, NGG control, and early tessellation path fields.
- SPI pixel-shader input control for up to 32 parameters, VS output export count, pixel shader input enable/address masks, interpolation control, barycentric control, temporary ring size, and shader export formats.
- VGT draw state such as multi-primitive reset index, DMA base, draw initiator, immediate data, event address, output path selection, and beginning hull/tessellation state.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit index of a field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit field mask.
- Register-address symbols are provided by the companion GC 9.0 offset header and are consumed by AMDGPU MMIO helpers, packet builders, golden-register programming, command submission, and debug paths.

Notable macro families in this slice are:

- `CB_TARGET_MASK` tail and `CB_SHADER_MASK`: per-render-target write enables and per-shader-output enables for MRT color export routing.
- `PA_SC_GENERIC_SCISSOR_*` and `PA_SC_VPORT_SCISSOR_{0..15}_*`: top-left/bottom-right scissor windows with `WINDOW_OFFSET_DISABLE` on the top-left registers.
- `COHER_DEST_BASE_{0,1}`: full-width destination base fields used by coherency/copy paths.
- `PA_SC_VPORT_ZMIN_{0..15}` and `PA_SC_VPORT_ZMAX_{0..15}`: full-width viewport depth bounds.
- `PA_SC_RASTER_CONFIG`, `PA_SC_RASTER_CONFIG_1`, `PA_SC_SCREEN_EXTENT_CONTROL`, and `PA_SC_TILE_STEERING_OVERRIDE`: render-backend, packer, shader-engine, screen-slice, and tile-steering mapping fields.
- `CP_PERFMON_CNTX_CNTL`, `CP_PIPEID`, `CP_RINGID`, and `CP_VMID`: command processor context/performance and queue identity fields.
- `PA_SC_RIGHT_VERT_GRID`, `PA_SC_LEFT_VERT_GRID`, and `PA_SC_HORIZ_GRID`: grid-quarter/half fields used by rasterization quantization.
- `VGT_MULTI_PRIM_IB_RESET_INDX`, `VGT_DMA_BASE_HI`, `VGT_DMA_BASE`, `VGT_DRAW_INITIATOR`, `VGT_IMMED_DATA`, `VGT_EVENT_ADDRESS_REG`, `VGT_OUTPUT_PATH_CNTL`, `VGT_HOS_CNTL`, `VGT_HOS_MAX_TESS_LEVEL`, `VGT_HOS_MIN_TESS_LEVEL`, and the start of `VGT_HOS_REUSE_DEPTH`: draw setup, event, path, and tessellation fields.
- `CB_BLEND_RED/GREEN/BLUE/ALPHA`, `CB_BLEND{0..7}_CONTROL`, `CB_COLOR_CONTROL`, `CB_DCC_CONTROL`, `CB_MRT{0..7}_EPITCH`, `SX_PS_DOWNCONVERT`, `SX_BLEND_OPT_EPSILON`, `SX_BLEND_OPT_CONTROL`, and `SX_MRT{0..7}_BLEND_OPT`: color output, blending, ROP, DCC, pitch, format conversion, and blend optimization fields.
- `DB_STENCIL_CONTROL`, `DB_STENCILREFMASK`, `DB_STENCILREFMASK_BF`, `DB_DEPTH_CONTROL`, `DB_EQAA`, and `DB_SHADER_CONTROL`: stencil operations/references, depth/stencil testing, sample/anchor configuration, depth export, kill/coverage/mask export, POPS, and early/late Z policy.
- `PA_CL_VPORT_{X,Y,Z}{SCALE,OFFSET}_{0..15}` and `PA_CL_UCP_{0..5}_{X,Y,Z,W}`: full-width viewport transform and user clip-plane coefficients.
- `SPI_PS_INPUT_CNTL_{0..31}`: pixel shader parameter interpolation metadata. Inputs 0-19 include offset/default/flat-shade/cylindrical-wrap/point-sprite/duplicate/FP16/default-attr1/valid fields, while inputs 20-31 omit the cylindrical-wrap and point-sprite texture fields in this slice.
- `SPI_VS_OUT_CONFIG`, `SPI_PS_INPUT_ENA`, `SPI_PS_INPUT_ADDR`, `SPI_INTERP_CONTROL_0`, `SPI_PS_IN_CONTROL`, `SPI_BARYC_CNTL`, `SPI_TMPRING_SIZE`, `SPI_SHADER_POS_FORMAT`, `SPI_SHADER_Z_FORMAT`, and `SPI_SHADER_COL_FORMAT`: shader export counts, pixel input component enable/address bits, interpolation mode, barycentric behavior, temporary ring sizing, and position/depth/color export formats.
- `PA_CL_CLIP_CNTL`, `PA_SU_SC_MODE_CNTL`, `PA_CL_VTE_CNTL`, `PA_CL_VS_OUT_CNTL`, `PA_CL_NANINF_CNTL`, `PA_SU_LINE_STIPPLE_CNTL`, `PA_SU_PRIM_FILTER_CNTL`, `PA_SU_SMALL_PRIM_FILTER_CNTL`, `PA_CL_OBJPRIM_ID_CNTL`, `PA_CL_NGG_CNTL`, `PA_SU_OVER_RASTERIZATION_CNTL`, `PA_SU_POINT_SIZE`, `PA_SU_POINT_MINMAX`, and `PA_SU_LINE_CNTL`: clip/cull/setup, vertex transform, vertex-output sideband use, NaN/Inf policy, primitive filtering, NGG vertex reuse, over-rasterization, point size, and line size/state.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Select the GC 9.0 generated register headers for the detected ASIC.
2. Choose a register address from the matching offset header.
3. Read the current register value, construct a draw-state packet value, or prepare a direct MMIO write.
4. Use these `__SHIFT` and `__MASK` constants, typically through `REG_SET_FIELD` or `REG_GET_FIELD`, to pack or extract field values.
5. Apply the value during graphics pipeline setup, golden-register programming, command submission, context switching, reset/recovery, debugfs, hang analysis, or performance telemetry.

For viewport and scissor state, runtime command streams program up to 16 independent viewport rectangles and depth ranges. Clip/setup state then uses the viewport transform, clip-plane, scissor, culling, primitive-filter, and over-rasterization fields while PA/SC routes primitives to shader engines, packers, and render backends.

For pixel-shader input and export state, compiler and command-buffer setup cooperate: VS/GS output counts and formats, PS input enable/address masks, `SPI_PS_INPUT_CNTL_*`, interpolation and barycentric controls, shader color/Z/position export formats, and CB/DB shader-control bits must agree with the compiled shader's parameter exports and pixel shader inputs.

For DB/CB/SX state, the graphics path programs depth/stencil tests, sample/EQAA policy, coverage/mask/depth export policy, color write masks, DCC overwrite-combiner settings, ROP/color control, per-MRT blend functions, blend constants, down-conversion, and blend optimization before drawing. These macros do not express the packet ordering, cache flushes, synchronization, or hardware-specific validation that higher-level AMDGPU and Mesa/UMD command generation must provide.

For VGT draw and tessellation state, the command processor and graphics ring write index-buffer reset values, DMA base fields, draw initiator bits, immediate data, event addresses, output path, and hull/tessellation settings as part of draw launch. This chunk ends immediately after the `VGT_HOS_REUSE_DEPTH__REUSE_DEPTH__SHIFT` definition; the matching mask is outside the chunk.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe stateful GPU registers whose values are owned by hardware, firmware, kernel command submission, user-mode graphics drivers, and AMDGPU initialization/recovery code.

Most registers in this slice are persistent draw or context state. Scissor rectangles, viewport transforms, user clip planes, raster config, setup control, SPI interpolation state, CB/DB/SX color/depth/blend controls, and VGT draw/tessellation controls persist until a later command stream, context switch, reset, or init path overwrites them. Incorrect read-modify-write handling can preserve stale bits across draws or lose reserved bits that the hardware expects to remain unchanged.

Some fields represent live or context-identifying state. `CP_PIPEID`, `CP_RINGID`, `CP_VMID`, performance-monitor enablement, event addresses, and draw initiator fields connect register programming to queue identity, VM context, event signaling, and command processor execution. Stale or mismatched values can make debug data misleading or direct operations to the wrong context.

Color/depth state has strong cross-register persistence. For example, CB target masks, shader masks, shader export formats, blend controls, CB color control, DB shader control, depth/stencil control, and EQAA fields all describe one coherent pixel-output contract. A value may be individually well-formed but still wrong if it does not match the current shader, render target formats, sample count, or depth/stencil surface state.

Viewport, clipping, and setup fields also form a coupled persistent contract. `PA_CL_VPORT_*`, `PA_SC_VPORT_SCISSOR_*`, `PA_CL_CLIP_CNTL`, `PA_CL_VTE_CNTL`, `PA_CL_VS_OUT_CNTL`, `PA_SU_SC_MODE_CNTL`, point/line size registers, and primitive filters determine where primitives rasterize and which vertex sideband values are consumed. Bad field packing can silently cull geometry, choose the wrong viewport/render target index, or change DirectX/OpenGL clip-space behavior.

## Dependencies And Integration Points

This chunk depends on the generated GC 9.0 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h` provides matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_default.h`, where present, provides reset/default values for related registers.
- Common AMDGPU helpers, including `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32*`, `WREG32*`, `SOC15_REG_OFFSET`, packet-building helpers, and golden-register programming helpers, consume these field definitions.
- GC 9.0 AMDGPU code that includes this header includes graphics initialization, rings, command processor setup, reset/recovery, debug/hang dump paths, power-management golden settings, and KFD/graphics interop paths.

Integration points include graphics pipeline state emission from user-mode drivers, AMDGPU kernel validation and context management, render-backend and depth-buffer programming, shader compiler export/input metadata, graphics ring command packet generation, perf/debug register reads, GPU reset recovery, suspend/resume reinitialization, and golden-register tables for Vega-era GC 9.0 ASICs.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but writes the wrong hardware bits or decodes misleading diagnostics.
- The chunk starts and ends mid-family. It begins with only the final `CB_TARGET_MASK` target masks and ends after the `VGT_HOS_REUSE_DEPTH` shift without its mask. Adjacent chunks are required for complete per-file context.
- Repeated register families are easy to misindex. Viewport 0-15, scissor 0-15, pixel inputs 0-31, MRTs 0-7, blend controls 0-7, and clip planes 0-5 have similar layouts but not always identical fields.
- `SPI_PS_INPUT_CNTL_20` through `SPI_PS_INPUT_CNTL_31` have fewer fields than inputs 0-19 in this chunk. Code that assumes all 32 input-control registers accept cylindrical-wrap or point-sprite texture fields can set nonexistent bits.
- Full-width masks such as blend constants, viewport scale/offset, user clip-plane coefficients, immediate data, and tessellation levels do not imply unconstrained semantics. Values still need correct floating-point encoding, address units, alignment, shader ABI expectations, or packet sequencing.
- CB/DB/SX state must match render target and shader metadata. Mismatched color export formats, write masks, DCC settings, blend functions, ROP mode, depth/stencil exports, or EQAA sample fields can produce rendering corruption, disabled writes, incorrect alpha-to-coverage, or depth/stencil misbehavior.
- Raster and viewport state can cause silent data loss. Bad scissor bounds, viewport Z min/max, clip disable bits, cull modes, primitive filters, small-primitive filters, over-rasterization, point/line sizes, or NaN/Inf policy can make valid draws disappear or render outside expected regions.
- `CP_*` and event-address fields are context-sensitive. Incorrect VMID, ring/pipe identity, or event-address packing can corrupt debugging/perf attribution or signal the wrong memory address.
- Reserved and absent bits should be preserved unless a hardware programming sequence explicitly requires a full-register value. This generated mask header does not encode write-one-to-clear, read-only, sticky, or reserved-bit behavior.
- NGG, object/primitive ID, viewport/render-target index, GS cut flag, and line-width sideband bits depend on shader output conventions. Incorrect `PA_CL_VS_OUT_CNTL` or `PA_CL_OBJPRIM_ID_CNTL` programming can misroute primitives only on pipelines that use those sideband outputs.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, and hardware runtime behavior:

- Kernel build coverage for AMDGPU files that include `gc_9_0_sh_mask.h`, especially GC 9.0 graphics initialization, command processor, rings, reset, debug, KFD interop, and power-management paths.
- Mechanical comparison against AMD's authoritative GC 9.0 register database to confirm every `__SHIFT` and `__MASK` value in this slice.
- Cross-checks that registers in this chunk have matching address macros in `gc_9_0_offset.h` and expected reset/default entries where generated.
- Static mask/shift sanity checks: masks align with shifts, repeated viewport/MRT/input families stay consistent, adjacent fields do not overlap unexpectedly, full-width fields use `0xFFFFFFFFL`, and sparse/reserved bits are intentional.
- Graphics bring-up and suspend/resume tests that verify golden-register writes for PA/SC, PA/CL, SPI, DB, CB, SX, and VGT state do not leave the GPU hung or produce unexpected busy/debug status.
- Render tests covering multiple render targets, color write masks, blend constants, per-MRT blending, ROP3, DCC, down-conversion, depth/stencil operations, stencil front/back masks, depth bounds, EQAA/MSAA, alpha-to-coverage, mask exports, and conservative/depth-before-shader behavior.
- Viewport/scissor tests for all 16 viewports, window-offset disable, viewport Z ranges, multi-viewport/render-target-index sideband outputs, clip/cull distances, user clip planes, DX clip-space definitions, rasterization kill, point size, line width, and line stipple.
- Shader interface tests that exercise PS input parameters 0-31, default attributes, flat shade, duplicate, FP16 interpolation, point sprites, barycentric control, input enable/address masks, VS export counts, position/Z/color export formats, and temporary ring sizing.
- Draw path tests for multi-primitive index-buffer reset, indirect/DMA base programming, immediate data, event address signaling, output path selection, tessellation min/max levels, and HOS reuse depth once the adjacent chunk supplies the full register.
- Runtime warning signals include missing color writes, incorrect blending, depth/stencil regressions, sample-count artifacts, geometry unexpectedly clipped or culled, viewport-index/render-target-index errors, shader interpolation corruption, point/line rasterization differences, event signaling faults, and GPU reset loops after graphics-state programming.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002621`. It covers lines 14706-17177 of `gc_9_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the `CB_TARGET_MASK` context before line 14706 and the `VGT_HOS_REUSE_DEPTH` mask and following VGT state after line 17177.
