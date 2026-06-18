# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_sh_mask.h lines 17185-19585

## Scope

This chunk covers a generated section of the AMD GC 9.2.1 shader/register mask header. It starts in the `SPI_PS_INPUT_CNTL_18`/`SPI_PS_INPUT_CNTL_19` area and ends at the `CB_COLOR2_BASE` comment, before the field definitions for color target 2 continue in the next chunk.

The range defines preprocessor constants only. There are no C functions, structs, variables, memory allocations, or runtime branches in this chunk. Every meaningful item is a register-field pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for a field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or compose that field.

## Purpose

The purpose of this header slice is to encode the GC 9.2.1 graphics pipeline register ABI for shader input interpolation, shader exports, blend and render-target state, depth/stencil state, primitive assembly, tessellation/geometry state, streamout, rasterization, and the first color-buffer target descriptors. AMDGPU code uses these definitions with the matching register-address header and helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, `RREG32_SOC15`, and packet-building paths that write context registers.

This chunk is therefore compile-time metadata for MMIO/packet register programming. The behavior belongs to the hardware blocks and to the AMDGPU code that consumes these masks.

## Important Macro Families

### SPI Pixel Shader Inputs and Exports

The chunk begins in the repeated `SPI_PS_INPUT_CNTL_n` family, covering `SPI_PS_INPUT_CNTL_19` through `SPI_PS_INPUT_CNTL_31` after the tail of input control 18. These registers map pixel-shader parameters and interpolation behavior. Fields include `OFFSET`, `DEFAULT_VAL`, `FLAT_SHADE`, `CYL_WRAP` where present, point-sprite texture controls, duplicate/FP16 interpolation controls, default-attribute controls, and attribute-valid bits.

The later SPI registers describe shader-stage export and pixel-shader input requirements:

- `SPI_VS_OUT_CONFIG` exposes vertex-shader export count and half-pack behavior.
- `SPI_PS_INPUT_ENA` and `SPI_PS_INPUT_ADDR` describe which perspective, linear, position, front-face, ancillary, sample coverage, and fixed-point inputs are enabled and addressable.
- `SPI_INTERP_CONTROL_0`, `SPI_PS_IN_CONTROL`, and `SPI_BARYC_CNTL` configure flat shading, point-sprite override, interpolation count, off-chip parameter behavior, barycentric center/centroid policy, position-float location, and front-face bit export.
- `SPI_TMPRING_SIZE`, `SPI_SHADER_POS_FORMAT`, `SPI_SHADER_Z_FORMAT`, and `SPI_SHADER_COL_FORMAT` define temporary-ring sizing and position/Z/color export formats.

### SX and CB Blend State

The SX block controls color export conversion and blend optimization:

- `SX_PS_DOWNCONVERT` packs downconvert modes for MRT0 through MRT7.
- `SX_BLEND_OPT_EPSILON` packs per-MRT epsilon selections.
- `SX_BLEND_OPT_CONTROL` has per-MRT color/alpha optimization disable bits plus `PIXEN_ZERO_OPT_DISABLE`.
- `SX_MRT0_BLEND_OPT` through `SX_MRT7_BLEND_OPT` expose color and alpha source/destination optimization choices and combine functions.

The CB blend-control family then provides per-render-target blend equations:

- `CB_BLEND0_CONTROL` through `CB_BLEND7_CONTROL` share the same layout: color source blend, color combine function, color destination blend, alpha source blend, alpha combine function, alpha destination blend, separate-alpha enable, blend enable, and ROP3 disable.
- `CB_MRT0_EPITCH` through `CB_MRT7_EPITCH` expose per-MRT `EPITCH`.
- `CB_COLOR_CONTROL` later in the chunk controls color-buffer mode, ROP3, degamma, and dual-quad behavior.

### Copy State, Draw Initiation, and Index DMA

`CS_COPY_STATE` and `GFX_COPY_STATE` define small source-state IDs for copying pipeline state. The VGT draw/index path includes:

- `VGT_DMA_BASE_HI`, `VGT_DMA_BASE`, `VGT_DMA_SIZE`, `VGT_DMA_MAX_SIZE`, `VGT_DMA_INDEX_TYPE`, and `VGT_DMA_NUM_INSTANCES`, which describe indexed-draw buffer base, size, maximum size, index type, swap/buffer type, request policy, primitive-generation enable, not-EOP behavior, request path, and instance count.
- `VGT_DRAW_INITIATOR`, with source select, major mode, sprite enable, not-EOP, opaque draw, unrolled instance, GRBM skew behavior, and render-target index fields.
- `VGT_IMMED_DATA`, `VGT_EVENT_ADDRESS_REG`, `VGT_EVENT_INITIATOR`, and `VGT_DMA_EVENT_INITIATOR`, which pack immediate draw/event payloads and event address high/low fields.

### Depth, Stencil, EQAA, and Shader DB Controls

Depth-buffer state in this chunk includes:

- `DB_DEPTH_CONTROL`, covering stencil enable, Z enable/write enable, depth bounds, Z compare function, backface enable, front/back stencil functions, and color-write behavior on depth pass/fail.
- `DB_EQAA`, with anchor sample, pixel-shader iteration sample, mask export sample, alpha-to-mask sample, intersection, interpolation, static association, overrasterization, and post-Z overrasterization controls.
- `DB_SHADER_CONTROL`, with Z/stencil export enables, Z order, kill, coverage-to-mask, mask export, hierarchical fail/no-op execution, alpha-to-mask disable, depth-before-shader, conservative-Z export, dual-quad disable, primitive ordered pixel shader, overlap execution, and overlap sample count fields.
- `DB_HTILE_SURFACE`, `DB_SRESULTS_COMPARE_STATE0`, `DB_SRESULTS_COMPARE_STATE1`, and `DB_PRELOAD_CONTROL`, which define HTILE preload/cache/alignment behavior, shader-results compare tests, and preload window coordinates.
- `DB_ALPHA_TO_MASK`, defining alpha-to-mask enable, four offsets, and offset rounding.

### PA Clip, Setup, Rasterization, and AA State

The PA register families define viewport transform, clipping, culling, primitive setup, rasterizer, antialiasing, centroid, and conservative-raster state:

- `PA_CL_CLIP_CNTL`, `PA_CL_VTE_CNTL`, `PA_CL_VS_OUT_CNTL`, and `PA_CL_NANINF_CNTL` cover user clip planes, clip/cull distance exports, viewport scale/offset enables, clip-space policy, rasterization kill, Z clip disable/programmed near, vertex-output side-band enables, and NaN/Inf handling.
- `PA_SU_SC_MODE_CNTL`, `PA_SU_LINE_STIPPLE_CNTL`, `PA_SU_LINE_STIPPLE_SCALE`, `PA_SU_PRIM_FILTER_CNTL`, `PA_SU_SMALL_PRIM_FILTER_CNTL`, `PA_SU_OVER_RASTERIZATION_CNTL`, `PA_SU_POINT_SIZE`, `PA_SU_POINT_MINMAX`, `PA_SU_LINE_CNTL`, `PA_SU_VTX_CNTL`, and polygon-offset registers define culling, face selection, polygon mode, polygon offset, line/point dimensions, line stipple, primitive filtering/expansion, small-primitive filtering, overrasterization, and vertex control.
- `PA_SC_MODE_CNTL_0`, `PA_SC_MODE_CNTL_1`, `PA_SC_LINE_STIPPLE`, `PA_SC_CENTROID_PRIORITY_0/1`, `PA_SC_LINE_CNTL`, `PA_SC_AA_CONFIG`, the `PA_SC_AA_SAMPLE_LOCS_PIXEL_*` families, `PA_SC_AA_MASK_*`, `PA_SC_SHADER_CONTROL`, `PA_SC_BINNER_CNTL_0/1`, `PA_SC_CONSERVATIVE_RASTERIZATION_CNTL`, and `PA_SC_NGG_MODE_CNTL` describe scan-converter MSAA, viewport scissor, tile/supertile walk, out-of-order primitive handling, centroid priorities, AA sample locations and masks, binning, conservative rasterization, shader quad realignment/collision diagnostics, and NGG deallocation limits.

### VGT Tessellation, Geometry, Primitive ID, and Streamout

The VGT definitions cover vertex/geometry/tessellation topology and streamout:

- `VGT_OUTPUT_PATH_CNTL`, `VGT_HOS_CNTL`, `VGT_HOS_MAX_TESS_LEVEL`, `VGT_HOS_MIN_TESS_LEVEL`, `VGT_HOS_REUSE_DEPTH`, `VGT_TESS_DISTRIBUTION`, `VGT_LS_HS_CONFIG`, and `VGT_TF_PARAM` configure tessellation mode, levels, reuse depth, distribution, patch/control-point counts, partitioning, topology, donut-disable, request policy, and distribution mode.
- `VGT_GROUP_PRIM_TYPE`, `VGT_GROUP_FIRST_DECR`, `VGT_GROUP_DECR`, `VGT_GROUP_VECT_0/1_CNTL`, and `VGT_GROUP_VECT_0/1_FMT_CNTL` describe grouped primitive/component packing, retained ordering/quads, component enables, stride/shift, conversion, and offsets.
- `VGT_GS_MODE`, `VGT_GS_ONCHIP_CNTL`, `VGT_GS_PER_ES`, `VGT_ES_PER_GS`, `VGT_GS_PER_VS`, `VGT_GSVS_RING_OFFSET_1/2/3`, `VGT_GS_OUT_PRIM_TYPE`, `VGT_ESGS_RING_ITEMSIZE`, `VGT_GSVS_RING_ITEMSIZE`, `VGT_GS_MAX_PRIMS_PER_SUBGROUP`, `VGT_GS_MAX_VERT_OUT`, `VGT_GS_VERT_ITEMSIZE*`, and `VGT_GS_INSTANCE_CNT` configure geometry-shader mode, cut behavior, on-chip mode, ring sizing/offsets, output primitive type per stream, subgroup sizing, vertex item sizes, and GS instancing.
- `VGT_SHADER_STAGES_EN` enables LS/HS/ES/GS/VS stage combinations, dispatch draw, deallocation accumulators, VS wave IDs, primitive generation, ordered ID mode, maximum primitive groups per wave, and GS fast launch.
- `VGT_PRIMITIVEID_EN`, `VGT_PRIMITIVEID_RESET`, `VGT_DRAW_PAYLOAD_CNTL`, `VGT_DISPATCH_DRAW_INDEX`, `VGT_INSTANCE_STEP_RATE_0/1`, `VGT_REUSE_OFF`, `VGT_VTX_CNT_EN`, `VGT_VERTEX_REUSE_BLOCK_CNTL`, and `VGT_OUT_DEALLOC_CNTL` control primitive-ID generation/reset, draw payload fields, dispatch index matching, instance stepping, vertex reuse, vertex count enable, reuse depth, and output deallocation distance.
- `VGT_STRMOUT_BUFFER_SIZE_0..3`, `VGT_STRMOUT_VTX_STRIDE_0..3`, `VGT_STRMOUT_BUFFER_OFFSET_0..3`, `VGT_STRMOUT_DRAW_OPAQUE_*`, `VGT_STRMOUT_CONFIG`, and `VGT_STRMOUT_BUFFER_CONFIG` define streamout buffer sizes, strides, offsets, opaque draw counters/stride, stream enables, raster stream, primitives-needed count, and per-stream buffer enables.

### Color Target Descriptor State

The chunk ends in the color target descriptor families:

- `CB_COLOR0_BASE`, `CB_COLOR0_BASE_EXT`, `CB_COLOR0_ATTRIB2`, `CB_COLOR0_VIEW`, `CB_COLOR0_INFO`, `CB_COLOR0_ATTRIB`, `CB_COLOR0_DCC_CONTROL`, `CB_COLOR0_CMASK`, `CB_COLOR0_CMASK_BASE_EXT`, `CB_COLOR0_FMASK`, `CB_COLOR0_FMASK_BASE_EXT`, `CB_COLOR0_CLEAR_WORD0/1`, `CB_COLOR0_DCC_BASE`, and `CB_COLOR0_DCC_BASE_EXT`.
- The same family for color target 1: `CB_COLOR1_*`.
- The range reaches the `CB_COLOR2_BASE` comment but not its field definitions.

These registers encode base addresses, address extensions, mip dimensions, slice view, format/number type/component swap, fast clear, compression, blend options, FMASK/DCC enablement, CMASK address type, resource type, sample/fragment counts, swizzle modes, alignment flags, DCC block sizing, lossy precision, constant encode controls, metadata bases, and clear words.

## Control Flow and State Behavior

There is no control flow in this header chunk. Its effect is indirect: C code includes the macros and uses them to compose 32-bit values for hardware context registers, command packets, or MMIO writes.

The state represented here is persistent hardware pipeline state until overwritten by command submission, context restore, reset, suspend/resume reinitialization, or firmware-managed sequencing. Important persistent state includes PS input interpolation mappings, shader export formats, blend equations and optimization choices, depth/stencil/alpha-to-mask behavior, clip/raster/MSAA state, tessellation and geometry-shader topology, streamout buffer configuration, draw/index DMA controls, and CB color target descriptors including DCC/CMASK/FMASK metadata addresses.

Some fields are action/event payloads rather than long-lived mode state. Examples include `VGT_EVENT_INITIATOR`, `VGT_DMA_EVENT_INITIATOR`, `VGT_DRAW_INITIATOR`, `VGT_IMMED_DATA`, and `VGT_PRIMITIVEID_RESET`. Consumers must follow the sequencing and packet rules in the caller and hardware specification; the mask header only supplies field positions.

## Dependencies and Integration Points

This file depends on the generated AMD register-header convention:

- `gc_9_2_1_offset.h` supplies the register addresses and base indices corresponding to these field names.
- `gc_9_2_1_default.h` supplies reset/default values where generated.
- AMDGPU helper macros and PM4 packet-building paths consume the `__SHIFT` and `_MASK` values.

Integration points are broad because these are core graphics context registers:

- RadeonSI/AMDGPU user-mode command streams and kernel validation paths ultimately program these graphics context registers through PM4 packets.
- Kernel GFX initialization and resume/reset paths include GC-family headers to restore safe defaults and ring state.
- KFD/GFX compute and dispatch paths may interact with shared draw/dispatch, shader-stage, scratch, and export state where graphics and compute register programming overlap.
- Display and render tests exercise CB/DB/SX/SPI/PA/VGT behavior indirectly through real rendering workloads.
- The merge lane should connect this chunk with preceding `SPI_PS_INPUT_CNTL_*` definitions and following `CB_COLOR2_*` through later color-target families for a complete per-file view.

## Risks

- A wrong shift or mask can silently program the wrong bit field in hardware. In this chunk that can produce incorrect interpolation, broken shader exports, bad blend/depth results, rendering corruption, GPU hangs, or lost streamout data.
- Repeated families are vulnerable to mechanical drift. `SPI_PS_INPUT_CNTL_n`, `SX_MRTn_BLEND_OPT`, `CB_BLENDn_CONTROL`, streamout buffer `0..3`, AA sample-location registers, and `CB_COLORn_*` families are similar but not always globally complete within this chunk.
- Color target fields are address- and compression-sensitive. Incorrect base, base extension, DCC/CMASK/FMASK, swizzle, alignment, sample count, fragment count, or clear-word masks can corrupt render-target memory or metadata.
- DB and PA state affects API-visible correctness. Incorrect depth/stencil compare, alpha-to-mask, conservative rasterization, sample locations, centroid priority, polygon offset, clip, or NaN/Inf handling can create subtle conformance failures.
- VGT stage and geometry/tessellation fields are topology-sensitive. Incorrect ring item sizes, subgroup limits, shader-stage enables, primitive-ID behavior, or streamout strides can break specific pipeline combinations while simpler draws still pass.
- The chunk begins and ends mid-family. Any final per-file report must avoid treating this chunk as the complete source of `SPI_PS_INPUT_CNTL_*` or `CB_COLOR*` state.

## Test and Validation Signals

Useful validation is mostly build and hardware/integration coverage:

- Compile AMDGPU and KFD code that includes `gc/gc_9_2_1_sh_mask.h`; this catches missing or renamed macros and malformed preprocessor definitions.
- Run graphics conformance or piglit/deqp-style rendering tests that cover interpolation qualifiers, point sprites, flat shading, FP16 interpolation, shader position/Z/color export formats, and clip/cull distance outputs.
- Exercise blend, ROP, alpha-to-coverage, MRT, DCC, CMASK/FMASK, fast-clear, and render-target format tests to validate SX/CB field usage.
- Run depth/stencil, EQAA/MSAA, conservative rasterization, polygon offset, small-primitive filtering, line stipple, sample-location, and centroid tests to validate DB/PA/SC programming.
- Exercise tessellation, geometry shader, NGG-adjacent, primitive ID, instancing, indirect/indexed draw, and streamout workloads to validate VGT field composition.
- Reset, suspend/resume, and GPU recovery tests should verify that saved/restored context registers using these masks return the device to a valid graphics state.
