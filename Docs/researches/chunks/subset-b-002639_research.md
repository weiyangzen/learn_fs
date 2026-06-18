# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h lines 17205-19598

## Scope

This chunk covers a generated AMD GC 9.1 shader/register mask header range. It starts inside the mask half of `SPI_PS_INPUT_CNTL_14` and ends inside the shift half of `CB_COLOR1_INFO`, so adjacent chunks are needed for the complete file-level view. The range contains 2,174 `#define` macros and 220 register comment anchors. The macros are almost entirely paired bitfield constants named `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`.

## Purpose

`gc_9_1_sh_mask.h` provides compile-time bit positions and masks for GC 9.1 graphics registers used by the AMDGPU driver. This slice describes late graphics-pipeline state: pixel shader input routing, interpolation controls, shader export formats, blend optimization, render target blend controls, primitive assembly, tessellation and geometry-stage routing, depth/stencil controls, rasterization, MSAA sample locations and masks, streamout, and the beginning of color buffer render-target state.

The file does not implement executable behavior. Its value is as a hardware contract: C code can compose register values without hard-coding bit positions, while companion address headers provide the matching `mm...` register offsets. The constants in this chunk are consumed indirectly by register initialization, command emission, clear-state tables, golden-register programming, and debugging/decode code for GC 9.1 ASICs.

## Important API Surface

- `SPI_PS_INPUT_CNTL_14` through `SPI_PS_INPUT_CNTL_31` describe pixel shader input attribute routing. The chunk begins with remaining `SPI_PS_INPUT_CNTL_14` masks, then complete entries for 15-31. Common fields include `OFFSET`, `DEFAULT_VAL`, `FLAT_SHADE`, `CYL_WRAP`, `PT_SPRITE_TEX`, `DUP`, `FP16_INTERP_MODE`, `USE_DEFAULT_ATTR1`, `DEFAULT_VAL_ATTR1`, and attribute-valid bits.
- `SPI_VS_OUT_CONFIG`, `SPI_PS_INPUT_ENA`, `SPI_PS_INPUT_ADDR`, `SPI_INTERP_CONTROL_0`, `SPI_PS_IN_CONTROL`, and `SPI_BARYC_CNTL` define shader interface state: VS export count, PS input enable/address masks, interpolation mode, barycentric behavior, point/linear center selections, position sample selection, and related PS-side routing.
- `SPI_TMPRING_SIZE`, `SPI_SHADER_POS_FORMAT`, `SPI_SHADER_Z_FORMAT`, and `SPI_SHADER_COL_FORMAT` cover shader temporary-ring sizing and shader export formats for position, depth/stencil/sample-mask, and color MRT outputs.
- `SX_PS_DOWNCONVERT`, `SX_BLEND_OPT_EPSILON`, `SX_BLEND_OPT_CONTROL`, and `SX_MRT0_BLEND_OPT` through `SX_MRT7_BLEND_OPT` define shader export/color downconversion and blend optimization controls for multiple render targets.
- `CB_BLEND0_CONTROL` through `CB_BLEND7_CONTROL`, `CB_MRT0_EPITCH` through `CB_MRT7_EPITCH`, `CB_COLOR_CONTROL`, and the first `CB_COLOR0_*`/`CB_COLOR1_*` groups define color-blend equations, MRT pitch, color-operation mode, render-target base addresses, views, formats, DCC/CMASK/FMASK metadata bases, and clear words.
- `DB_DEPTH_CONTROL`, `DB_EQAA`, `DB_SHADER_CONTROL`, `DB_HTILE_SURFACE`, `DB_SRESULTS_COMPARE_STATE0/1`, `DB_PRELOAD_CONTROL`, and `DB_ALPHA_TO_MASK` define depth/stencil, EQAA, shader depth export, HTILE metadata, sample-result compare, preload, and alpha-to-coverage state.
- `PA_CL_*`, `PA_SU_*`, and `PA_SC_*` groups describe clipping, viewport transform, NaN/Inf handling, point/line setup, primitive filtering, over/conservative rasterization, centroid priority, AA sample locations, AA masks, binner controls, shader control, and scanner/rasterizer modes.
- `VGT_*`, `IA_ENHANCE`, and `WD_ENHANCE` groups cover draw initiation, DMA/index buffers, event initiation, primitive ID handling, tessellation distribution, shader-stage enables, LS/HS/GS/VS routing, streamout, instance stepping, and vertex reuse/deallocation controls.
- `CS_COPY_STATE` and `GFX_COPY_STATE` expose a single copy-state field each for compute/graphics copy-state handling.

There are no C types, structs, or functions in this slice. The public surface is the preprocessor namespace itself, and correctness depends on pairing each `__SHIFT` constant with its corresponding `_MASK` and register address.

## Control Flow

There is no direct control flow. Runtime flow happens in consumers:

1. Select the register offset from the matching GC 9.1 address header.
2. Build a 32-bit register value by shifting field values with `REGISTER__FIELD__SHIFT`.
3. Mask fields with `REGISTER__FIELD_MASK`.
4. Emit the value through MMIO writes, PM4 packets, clear-state restore, or golden-register setup.

The repeated register families in this chunk imply looped or table-driven consumers. MRT state commonly iterates over indices 0-7 for `SX_MRTn_BLEND_OPT`, `CB_BLENDn_CONTROL`, and `CB_MRTn_EPITCH`; streamout iterates over buffer slots 0-3; MSAA sample-location programming expands across pixel quadrants and sample pairs.

## State and Persistence

The macros are stateless build artifacts, but they describe persistent GPU context state. Once programmed, the underlying registers remain active until another command stream, context restore, clear-state packet, mode set, or GPU reset changes them.

Important persistent domains include:

- Pixel shader ABI state in `SPI_PS_INPUT_CNTL_*`, `SPI_PS_INPUT_ENA`, and `SPI_PS_INPUT_ADDR`; wrong offsets or validity bits can misroute interpolants or force default values into shaders.
- Render-target and blend state in `SX_*`, `CB_BLEND*`, `CB_COLOR_CONTROL`, and `CB_COLOR0_*`; incorrect format, blend, compression, base-address, or view fields can produce visible corruption or writes to the wrong surface.
- Primitive/tessellation/geometry routing in `VGT_*`; incorrect ring item sizes, output primitive types, subgroup sizes, or shader-stage enables can break draws or hang the graphics pipe.
- Depth/rasterization state in `DB_*`, `PA_CL_*`, `PA_SU_*`, and `PA_SC_*`; mismatches affect depth/stencil tests, conservative rasterization, AA coverage, point/line rendering, clipping, and binning behavior.
- Streamout state in `VGT_STRMOUT_*`; size, stride, offset, and buffer-filled-size fields persist across draw sequences and must match buffer allocations.

## Dependencies and Integration Points

- Depends on AMD's generated GC 9.1 register specification. This header must stay synchronized with companion GC 9.1 address-definition headers such as `gc_9_1_d.h` and other generated include files in `drivers/gpu/drm/amd/include/asic_reg/gc/`.
- Integrated into AMDGPU graphics code through SOC15 register access helpers, command submission paths, golden-register tables, clear-state data, and debug register dumps.
- Maps higher-level graphics API state from Mesa/Vulkan/OpenGL into hardware fields: shader input interpolation, MRT formats and blend modes, depth/stencil state, MSAA sample positions, streamout, primitive assembly, tessellation, and rasterization all eventually rely on these masks.
- Interacts with memory management through GPU address fields such as `VGT_DMA_BASE`, `VGT_EVENT_ADDRESS_REG`, `CB_COLOR0_BASE`, `CB_COLOR0_BASE_EXT`, `CB_COLOR0_CMASK`, `CB_COLOR0_FMASK`, and `CB_COLOR0_DCC_BASE`; callers must apply hardware alignment and address-splitting rules outside this header.
- Uses plain C preprocessor constants only. There is no type checking, range checking, or validation that a field value fits its mask.

## Risks

- Bitfield drift is the central risk. If these generated masks differ from the GC 9.1 hardware spec or the matching address header, register writes silently target the wrong bits.
- This chunk is boundary-partial: `SPI_PS_INPUT_CNTL_14` lacks the field shifts and early masks in this slice, while `CB_COLOR1_INFO` lacks most masks and later shifts here. Merge tooling must not treat either as fully documented by this chunk alone.
- Indexed render-target and blend families create copy/paste hazards. A wrong `CB_BLENDn_CONTROL`, `SX_MRTn_BLEND_OPT`, `CB_MRTn_EPITCH`, or `CB_COLORn_*` index can alter a different MRT than intended.
- Address and metadata fields have high blast radius. Incorrect `CB_COLOR0_*` base/extension, CMASK/FMASK/DCC base, DCC control, or `DB_HTILE_SURFACE` fields can corrupt render-target/depth metadata or trigger GPU VM faults.
- Shader-stage routing fields in `VGT_SHADER_STAGES_EN`, `VGT_GS_MODE`, `VGT_GS_ONCHIP_CNTL`, and ring item-size registers must match compiled shader ABI assumptions. Mismatches can cause bad geometry output, missing primitives, or hangs.
- Rasterization controls such as `PA_SC_AA_SAMPLE_LOCS_*`, `PA_SC_AA_MASK_*`, `PA_SU_OVER_RASTERIZATION_CNTL`, and `PA_SC_CONSERVATIVE_RASTERIZATION_CNTL` are visually sensitive and can cause subtle conformance failures without obvious kernel errors.

## Test Signals

- Build coverage: compiling AMDGPU with this header catches syntax errors, duplicate macros, and missing include dependencies.
- Generation consistency: compare this range against the GC 9.1 register source/spec and companion address header to verify each register has the expected field widths, masks, and shifts.
- Graphics conformance: Vulkan/OpenGL CTS cases for shader interpolation, point sprites, flat shading, MRT blending, color write masks, depth/stencil, tessellation, geometry shaders, streamout, MSAA sample locations, alpha-to-coverage, conservative rasterization, and primitive clipping exercise this register surface.
- Runtime smoke tests: boot a GC 9.1 device, run display plus 3D workloads, and monitor for GPU hangs, VM faults, bad render output, or golden-register warnings.
- Register-dump validation: decode known-good state emission using these masks, especially `SPI_PS_INPUT_CNTL_*`, `CB_BLEND*`, `DB_DEPTH_CONTROL`, `DB_SHADER_CONTROL`, `VGT_SHADER_STAGES_EN`, `PA_SC_AA_*`, `PA_SC_BINNER_*`, and `CB_COLOR0_*`.
