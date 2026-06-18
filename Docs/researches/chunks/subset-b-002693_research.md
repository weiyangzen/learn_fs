# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_sh_mask.h lines 19507-21915

## Scope

This chunk covers a generated shift/mask section of the GC 9.4.3 AMD GPU register bitfield header. It starts in the middle of the `SPI_PS_INPUT_CNTL_19` definition, covers full definitions for `SPI_PS_INPUT_CNTL_20` through `SPI_PS_INPUT_CNTL_31`, then spans shader interpolation/output controls, color blend state, VGT draw and geometry/tessellation state, depth/stencil and rasterizer state, streamout state, multisample sample-location state, primitive binning/conservative rasterization state, and the beginning of the per-render-target color-buffer descriptor families through `CB_COLOR3_DCC_CONTROL`.

The file is generated hardware ABI data. This chunk contains only C preprocessor constants in the standard AMDGPU form:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

There are no functions, structs, variables, dynamic allocations, or executable control flow in this chunk.

## Purpose

The purpose of this chunk is to describe how GC 9.4.3 graphics pipeline state is packed into 32-bit hardware registers. AMDGPU and KFD code include the matching `gc_9_4_3_offset.h` and `gc_9_4_3_sh_mask.h` pair so register helper macros can address a register and compose or decode its fields without hard-coded bit positions.

The fields here are largely context/draw state: pixel shader input interpolation, render-target blend and color-buffer layout, draw initiator and index-buffer parameters, primitive assembly, clipping, rasterization, depth/stencil, MSAA/EQAA sample layout, streamout, tessellation, geometry shader ring sizing, NGG-related controls, and CB metadata/compression addresses for MRTs 0 through the start of MRT 3.

## Important Macro Families

### Pixel Shader Input and SPI State

`SPI_PS_INPUT_CNTL_20` through `SPI_PS_INPUT_CNTL_31` continue the per-attribute pixel shader input map. Each register defines fields such as `OFFSET`, `DEFAULT_VAL`, `FLAT_SHADE`, `DUP`, `FP16_INTERP_MODE`, `USE_DEFAULT_ATTR1`, `DEFAULT_VAL_ATTR1`, and validity bits for attribute lanes. These fields control how interpolated vertex outputs are routed into pixel shader inputs and how missing/default attributes are supplied.

`SPI_VS_OUT_CONFIG`, `SPI_PS_INPUT_ENA`, and `SPI_PS_INPUT_ADDR` describe shader output/input export masks. `SPI_PS_INPUT_ENA` and `SPI_PS_INPUT_ADDR` each expose 32 single-bit fields, one for every pixel shader input slot, and are paired with the `SPI_PS_INPUT_CNTL_*` attribute descriptors.

`SPI_INTERP_CONTROL_0`, `SPI_PS_IN_CONTROL`, and `SPI_BARYC_CNTL` define interpolation/barycentric behavior, pixel parameter generation, front-face and ancillary slot locations, position/parameter offset controls, and perspective/linear centroid or sample barycentric enables. `SPI_TMPRING_SIZE`, `SPI_SHADER_POS_FORMAT`, `SPI_SHADER_Z_FORMAT`, and `SPI_SHADER_COL_FORMAT` describe scratch/temp ring sizing and shader export format selection for position, depth, stencil/sample mask, and color targets.

### Color Blend and Render Target State

`CB_BLEND0_CONTROL` through `CB_BLEND7_CONTROL` define independent MRT blend state. Each target has source/destination blend factors and combine functions for color and alpha, plus `SEPARATE_ALPHA_BLEND`, `ENABLE`, and `DISABLE_ROP3` bits.

`CB_COLOR_CONTROL` defines global color-buffer mode controls including dual-quad disable, degamma enable, color mode, and ROP3 operation. `CB_MRT0_EPITCH` through `CB_MRT7_EPITCH` define extended pitch for each MRT.

The end of the chunk begins full per-MRT color descriptors:

- `CB_COLOR0_BASE/BASE_EXT`, `CB_COLOR1_*`, `CB_COLOR2_*`, and the start of `CB_COLOR3_*` carry 256-byte aligned base addresses.
- `CB_COLORn_ATTRIB2` carries mip0 height, mip0 width, and max mip.
- `CB_COLORn_VIEW` carries slice start/max and mip level.
- `CB_COLORn_INFO` carries endian, format, number type, component swap, fast clear, compression, blend behavior, DCC enable, FMASK controls, and CMASK address type.
- `CB_COLORn_ATTRIB` carries mip0 depth, metadata linearity, sample/fragment counts, swizzle modes, resource type, and RB/pipe alignment.
- `CB_COLORn_DCC_CONTROL` carries DCC overwrite/key-clear/block-size/color-transform/independent-block/lossy precision/constant-encode controls.
- `CB_COLORn_CMASK`, `FMASK`, clear words, and DCC base/base-ext registers carry color metadata, FMASK, clear color, and DCC metadata addresses.

This chunk ends partway through `CB_COLOR3_DCC_CONTROL`; the remaining masks for that register and later MRTs belong to the next chunk.

### Draw, VGT, Tessellation, Geometry, and Streamout State

`VGT_DMA_BASE`, `VGT_DMA_BASE_HI`, `VGT_DMA_SIZE`, `VGT_DMA_MAX_SIZE`, `VGT_DMA_INDEX_TYPE`, and `VGT_DMA_NUM_INSTANCES` encode index-buffer addressing, index count, index type/swap mode, request policy, primitive generator enablement, and instancing count.

`VGT_DRAW_INITIATOR`, `VGT_IMMED_DATA`, `VGT_EVENT_ADDRESS_REG`, `VGT_EVENT_INITIATOR`, `VGT_DRAW_PAYLOAD_CNTL`, `VGT_DISPATCH_DRAW_INDEX`, and `VGT_DMA_EVENT_INITIATOR` describe draw/event packet payload fields: draw source and major mode, not-EOP behavior, register render-target index, immediate data, event type/address, object/primitive ID payload enables, and dispatch draw index.

The geometry/tessellation block includes `VGT_OUTPUT_PATH_CNTL`, `VGT_HOS_CNTL`, tessellation min/max levels and distribution, `VGT_GROUP_*` primitive/vector controls, `VGT_GS_MODE`, `VGT_GS_ONCHIP_CNTL`, GS/ES/VS ring item sizes and offsets, `VGT_GS_OUT_PRIM_TYPE`, `VGT_GS_MAX_PRIMS_PER_SUBGROUP`, `VGT_GS_MAX_VERT_OUT`, `VGT_SHADER_STAGES_EN`, `VGT_LS_HS_CONFIG`, `VGT_TF_PARAM`, `VGT_GS_INSTANCE_CNT`, and `VGT_PRIMITIVEID_*`. These fields configure which hardware shader stages are active, how many vertices/primitives are grouped, how GS/ES/LS/HS rings are sized, what primitive topology is emitted, and how primitive IDs reset or propagate.

`VGT_STRMOUT_*` registers define streamout buffer size, vertex stride, buffer offset for four streamout buffers, opaque draw offset/filled size/stride, streamout rasterization disable, primitive-needed/count-needed enables, and per-buffer streamout enable state.

### Depth, Stencil, HTILE, and Shader Depth Interaction

`DB_DEPTH_CONTROL` controls stencil enable, Z enable, Z writes, depth bounds, depth compare function, backface stencil, and color-write behavior on depth pass/fail. `DB_SHADER_CONTROL` controls shader depth/stencil/mask exports, Z ordering, kill/coverage-to-mask behavior, execution on hierarchical depth outcomes, depth-before-shader, conservative Z export, POPS, and overlap execution.

`DB_EQAA`, `DB_HTILE_SURFACE`, `DB_SRESULTS_COMPARE_STATE0/1`, `DB_PRELOAD_CONTROL`, and `DB_ALPHA_TO_MASK` define EQAA sample counts, HTILE preload/cache/alignment behavior, shader-result compare tests, preload windows, and alpha-to-mask behavior. These fields are central to depth/stencil correctness and multisample coverage semantics.

### PA/SC Rasterization, Clipping, Viewport, and Multisample State

The PA/SC blocks describe front-end rasterization state:

- `PA_CL_CLIP_CNTL`, `PA_CL_VTE_CNTL`, `PA_CL_VS_OUT_CNTL`, `PA_CL_NANINF_CNTL`, and guard-band adjustment registers control clipping, viewport transform enables, VS export interpretation, NaN/Inf handling, cull/clip distances, and guard-band clip/discard extents.
- `PA_SU_SC_MODE_CNTL`, point/line/polygon offset controls, `PA_SU_LINE_STIPPLE_*`, `PA_SU_PRIM_FILTER_CNTL`, `PA_SU_SMALL_PRIM_FILTER_CNTL`, `PA_SU_POINT_*`, `PA_SU_LINE_CNTL`, and `PA_SU_VTX_CNTL` define culling, polygon mode, polygon offset, point/line sizes, stipple, primitive filtering, provoking vertex, and pixel-center/rounding behavior.
- `PA_SC_MODE_CNTL_0`, `PA_SC_MODE_CNTL_1`, `PA_SC_LINE_STIPPLE`, `PA_SC_LINE_CNTL`, `PA_SC_AA_CONFIG`, `PA_SC_SHADER_CONTROL`, `PA_SC_BINNER_CNTL_0/1`, `PA_SC_CONSERVATIVE_RASTERIZATION_CNTL`, and `PA_SC_NGG_MODE_CNTL` define scan converter MSAA, tile walk/binning, line stipple, sample count, sample mask, shader collision instrumentation, primitive binning, conservative rasterization, and NGG mode behavior.
- `PA_SC_AA_SAMPLE_LOCS_PIXEL_*` registers encode 16 sample X/Y positions for each 2x2 pixel quadrant, and `PA_SC_AA_MASK_*` encodes per-quadrant AA masks.

These masks are consumed by command submission and clear-state paths to establish the exact fixed-function rasterization contract expected by user-mode graphics drivers.

## Control Flow and State Behavior

This header has no control flow. Its effect is compile-time substitution into code that reads and writes GPU MMIO or packetized context registers. Runtime sequencing is owned by the AMDGPU/KFD callers and firmware-visible command streams.

The state described here is persistent GPU context state until overwritten by another context/state packet, reset by clear-state programming, or changed by firmware/driver initialization. Important persistent state includes shader input interpolation mappings, shader export formats, blend factors and color control, draw/index-buffer descriptors, depth/stencil compare/write policy, rasterizer culling and clipping policy, tessellation/geometry shader ring sizing, streamout buffer setup, multisample sample locations and masks, primitive binning/conservative rasterization settings, and color target/metadata base addresses.

Some fields are command-like or event payload fields rather than long-lived configuration, such as `VGT_DRAW_INITIATOR`, `VGT_EVENT_INITIATOR`, `VGT_DMA_EVENT_INITIATOR`, and `CS_COPY_STATE`/`GFX_COPY_STATE` source-state IDs. Others describe memory-backed render state and must remain synchronized with buffer object addresses, tiling/swizzle metadata, DCC/CMASK/FMASK allocation, and pipe/RB alignment assumptions.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention. The sibling `gc_9_4_3_offset.h` provides register addresses such as the `reg*` names, and this file provides field positions/masks for those addresses. AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, `RREG32_SOC15`, and packet/context-state emission code consume these masks.

Direct source-tree inclusion points for this GC 9.4.3 mask header include:

- `drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.c`
- `drivers/gpu/drm/amd/amdgpu/gfxhub_v1_2.c`
- `drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gc_9_4_3.c`
- `drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v9.c`

The same register names also appear in clear-state tables for nearby generations, which shows how these fields map to context-state programming for graphics pipeline reset/default state. For GC 9.4.3 specifically, the masks are part of the graphics IP support layer and are coupled to KFD queue management, GFX initialization, GPUVM/GFXHUB setup, and user-mode driver command streams that emit the corresponding context registers.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can silently program unrelated graphics state, causing rendering corruption, GPU hangs, incorrect depth/stencil behavior, or invalid memory addresses for color metadata.
- The many repeated families are easy to corrupt mechanically. `SPI_PS_INPUT_CNTL_n`, `CB_BLENDn_CONTROL`, `PA_SC_AA_SAMPLE_LOCS_*`, streamout buffer triplets, and `CB_COLORn_*` families are regular but not interchangeable across all fields.
- Color-buffer address and metadata fields are memory-safety sensitive. Bad `BASE`, `BASE_EXT`, `CMASK`, `FMASK`, or `DCC_BASE` masks can direct hardware to the wrong memory or misinterpret compression metadata.
- DCC/CMASK/FMASK and alignment bits must match surface creation metadata. Mismatched swizzle, sample count, fragment count, resource type, RB alignment, or pipe alignment can produce corruption that is workload-dependent.
- Rasterization and depth/stencil fields interact with API-visible semantics. Errors in clip control, viewport transform, conservative rasterization, sample locations, alpha-to-mask, depth-before-shader, or stencil/Z functions can pass simple smoke tests while failing conformance.
- Draw/VGT fields control packet interpretation and geometry-stage sizing. Invalid index type, draw source, shader-stage enablement, GS/ES ring item size, tessellation factor mode, or streamout stride/offset can break command streams or hang geometry processing.
- The chunk starts and ends mid-family: it starts after most of `SPI_PS_INPUT_CNTL_19` and ends inside `CB_COLOR3_DCC_CONTROL`. The merge lane must reconcile adjacent chunks for complete per-register coverage.

## Test and Validation Signals

Useful validation is mostly build, conformance, and hardware execution coverage:

- Build AMDGPU and KFD paths that include `gc/gc_9_4_3_sh_mask.h`; this catches missing or renamed macro definitions.
- Run graphics clear-state and context-switch tests that exercise default programming for SPI, CB, DB, PA/SC, and VGT context registers.
- Run draw tests covering indexed/non-indexed draws, instancing, primitive restart/primitive ID, tessellation, geometry shader output, NGG mode, streamout, and event packets.
- Run render-target tests across multiple MRTs, blend modes, ROP3, formats, component swaps, DCC enabled/disabled, CMASK/FMASK, fast clear, MSAA/EQAA sample counts, and mipped/sliced render targets.
- Run depth/stencil tests covering depth bounds, front/back stencil, shader depth exports, early/late Z, alpha-to-mask, HTILE preload, and shader-result compare state.
- Run rasterization conformance for clipping, culling, guard bands, viewport transform, line/point/polygon offset, small primitive filtering, conservative rasterization, binning, sample locations, and sample masks.
- For GC 9.4.3 multi-die/accelerator configurations, include KFD queue and compute coexistence workloads to ensure graphics context-state definitions remain compatible with queue management and reset paths.
