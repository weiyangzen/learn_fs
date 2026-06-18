# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 22208-24656

## Scope

This chunk covers generated shift and mask macros from the GC 11.0.3 AMD GPU register mask header. The range starts in the viewport-scissor family after earlier `PA_SC_VPORT_SCISSOR_9_TL` definitions, covers a broad group of graphics context-state registers, and ends at the `PA_CL_NGG_CNTL` register comment before its field definitions appear in a later chunk.

The chunk is entirely preprocessor metadata. It defines no C functions, structs, enums, runtime storage, or executable control flow. Its behavior is the field-layout contract used by AMDGPU code and command-stream state programming to compose and decode 32-bit hardware register values for the GC 11.0.3 graphics pipeline.

Major register families in this range are:

- Primitive assembler/scissor/clip viewport state: `PA_SC_VPORT_SCISSOR_9_*` through `PA_SC_VPORT_SCISSOR_15_*`, `PA_SC_VPORT_ZMIN/ZMAX_0..15`, `PA_CL_VPORT_*_0..15`, user clip planes, programmed near clip, `PA_CL_CLIP_CNTL`, `PA_CL_VTE_CNTL`, `PA_CL_VS_OUT_CNTL`, and `PA_CL_NANINF_CNTL`.
- Raster and shader-engine routing state: `PA_SC_RASTER_CONFIG`, `PA_SC_RASTER_CONFIG_1`, `PA_SC_SCREEN_EXTENT_CONTROL`, `PA_SC_TILE_STEERING_OVERRIDE`, variable-rate shading register fields, and CP context identity registers (`CP_PERFMON_CNTX_CNTL`, `CP_PIPEID`, `CP_RINGID`, `CP_VMID`).
- Color/depth/blend state: `CB_RMI_GL2_CACHE_CONTROL`, constant blend color registers, `CB_FDCC_CONTROL`, `CB_COVERAGE_OUT_CONTROL`, `DB_STENCIL_CONTROL`, `DB_STENCILREFMASK`, `DB_STENCILREFMASK_BF`, `DB_DEPTH_CONTROL`, `DB_EQAA`, `CB_COLOR_CONTROL`, and `DB_SHADER_CONTROL`.
- Pixel-shader input and export state: `SPI_PS_INPUT_CNTL_0..31`, `SPI_VS_OUT_CONFIG`, `SPI_PS_INPUT_ENA`, `SPI_PS_INPUT_ADDR`, `SPI_INTERP_CONTROL_0`, `SPI_PS_IN_CONTROL`, `SPI_BARYC_CNTL`, temporary scratch-ring/base registers, and shader export format registers.
- Shader export/blend optimizer state: `SX_PS_DOWNCONVERT_CONTROL`, `SX_PS_DOWNCONVERT`, `SX_BLEND_OPT_EPSILON`, `SX_BLEND_OPT_CONTROL`, `SX_MRT0_BLEND_OPT..SX_MRT7_BLEND_OPT`, and `CB_BLEND0_CONTROL..CB_BLEND7_CONTROL`.
- Draw and primitive setup state: `GFX_COPY_STATE`, `VGT_DMA_BASE*`, `VGT_DRAW_INITIATOR`, `VGT_EVENT_ADDRESS_REG`, `GE_MAX_OUTPUT_PER_SUBGROUP`, `PA_SU_SC_MODE_CNTL`, line stipple controls, and small/expanded primitive filtering controls.

## Purpose

`gc_11_0_3_sh_mask.h` supplies bit offsets and masks for GC 11.0.3 registers. Each field is expressed as:

- `<REGISTER>__<FIELD>__SHIFT`: the field's starting bit.
- `<REGISTER>__<FIELD>_MASK`: the bit mask covering the field in the 32-bit register value.

Consumers combine these constants with helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, SOC15 register access helpers, packet-building code, or precomputed context-state tables. Sibling generated headers provide the complementary register addresses and reset/default values, especially `gc_11_0_3_offset.h` and any matching default header for the same ASIC generation.

The purpose of this chunk is to expose the GC 11.0.3 graphics state ABI for viewport transform, clipping, rasterization, pixel-shader interpolation, color/depth export, blending, and primitive filtering. It is the low-level map that lets higher-level driver code and firmware-facing state tables write fields without embedding numeric bit positions at each use site.

## Important Macro Families

### Viewport, Scissor, and Clip Space

The opening section completes viewport scissor definitions for viewports 9 through 15:

- `PA_SC_VPORT_SCISSOR_N_TL` fields define top-left X/Y and `WINDOW_OFFSET_DISABLE`.
- `PA_SC_VPORT_SCISSOR_N_BR` fields define bottom-right X/Y.

The same range defines depth bounds for all 16 viewports via `PA_SC_VPORT_ZMIN_0..15` and `PA_SC_VPORT_ZMAX_0..15`; each uses a full 32-bit payload field because the encoded value is the register's complete data word.

The clip/viewport transform section later defines `PA_CL_VPORT_XSCALE`, `XOFFSET`, `YSCALE`, `YOFFSET`, `ZSCALE`, and `ZOFFSET` for viewports 0 through 15, again as full-register fields. These are paired with `PA_CL_VTE_CNTL`, whose enable bits select whether the viewport transform applies X/Y/Z scale and offset and which vertex XY/Z/W formats are expected.

User clip planes are represented as `PA_CL_UCP_0_X/Y/Z/W` through `PA_CL_UCP_5_X/Y/Z/W`; all are full-register data fields. `PA_CL_PROG_NEAR_CLIP_Z` supplies the full-register programmed near-clip value. `PA_CL_CLIP_CNTL` then controls which user clip planes are enabled, whether they cull only, DirectX clip-space behavior, clip error detection, rasterization kill, linear attribute clipping, near/far Z clip disable, and programmed near-Z enablement.

`PA_CL_VS_OUT_CNTL` describes which vertex-shader side outputs are consumed by downstream graphics stages: clip/cull distance enables, point size, edge flag, render target index, viewport index, kill flag, line width, VRS rate, FSR select, and rate-combiner bypass controls.

`PA_CL_NANINF_CNTL` is a precision/robustness policy register for NaN and infinity handling through viewport transform and VS output paths. It includes discard/retain/convert behavior for XY/Z/W and clip-distance infinity, plus output negative-zero handling.

### Raster, Tiling, VRS, and Context Identity

`PA_SC_RASTER_CONFIG` and `PA_SC_RASTER_CONFIG_1` encode raster backend, packer, scan converter, shader engine, and shader-engine-pair mapping fields. These fields are topology-sensitive and are normally paired with ASIC-specific discovery or golden-setting values.

`PA_SC_SCREEN_EXTENT_CONTROL` controls even/odd slice enables. `PA_SC_TILE_STEERING_OVERRIDE` exposes a manual override for tile steering, including scan-converter count, render-backend count per scan converter, and packer count per scan converter.

The VRS group includes:

- `PA_SC_VRS_OVERRIDE_CNTL`: override rate-combiner mode, VRS rate, VRS surface enable, rate-hint writeback, and feedback override.
- `PA_SC_VRS_RATE_FEEDBACK_BASE`, `_BASE_EXT`, and `_SIZE_XY`: feedback surface address and dimensions.
- `PA_SC_VRS_RATE_CACHE_CNTL`: cache update/flush and flush-done bits.
- `PA_SC_VRS_RATE_BASE`, `_BASE_EXT`, and `_SIZE_XY`: VRS rate image address and dimensions.

`CP_PERFMON_CNTX_CNTL`, `CP_PIPEID`, `CP_RINGID`, and `CP_VMID` provide small command-processor context fields for perfmon enablement and context identity. `CONTEXT_RESERVED_REG0/1` are full-register data placeholders for reserved context state.

### Color Buffer, Depth Buffer, and Blend Constants

`CB_RMI_GL2_CACHE_CONTROL` defines write/read policies for DCC and color data, L3 bypass bits, and color big-page behavior. These fields affect color-buffer traffic between CB/RMI and GL2 and are performance/coherency sensitive.

`CB_BLEND_RED`, `CB_BLEND_GREEN`, `CB_BLEND_BLUE`, and `CB_BLEND_ALPHA` are full-register constant blend-color components. `CB_FDCC_CONTROL` exposes FDCC/sample-mask tracker and constant-encode/eliminate-FC skip controls. `CB_COVERAGE_OUT_CONTROL` controls coverage output enablement, target MRT/channel selection, and sample count.

The depth/stencil section includes:

- `DB_STENCIL_CONTROL`: front/back stencil fail, zpass, and zfail operation fields.
- `DB_STENCILREFMASK` and `DB_STENCILREFMASK_BF`: front and back-face stencil test value, mask, write mask, and operation value.
- `DB_DEPTH_CONTROL`: stencil enable, depth enable/write enable, depth function, backface enable, stencil read/write controls, z pass/fail controls, and color-write behavior on depth pass/fail.
- `DB_EQAA`: anchor/iteration/mask sample counts, high-quality intersections, incoherent reads, interpolation mode, static anchor associations, alpha-to-mask EQAA disable, overrasterization amount, and post-Z overrasterization.
- `DB_SHADER_CONTROL`: shader depth/stencil export controls, Z order, kill/mask export, depth-before-shader, conservative Z export, primitive ordered pixel shader, pre-shader depth coverage, OREO blend, and intrinsic-rate override fields.
- `CB_COLOR_CONTROL`: dual-quad controls, one-fragment PS invoke, degamma enable, color mode, and ROP3 function.

These macros are central to render-target, depth/stencil, MSAA/EQAA, alpha-to-coverage, and pixel-shader depth-export programming.

### SPI Pixel Shader Inputs and Interpolation

The chunk defines `SPI_PS_INPUT_CNTL_0..31`. Each input-control register has a repeated layout for pixel-shader interpolants:

- `OFFSET` selects the parameter offset.
- `DEFAULT_VAL` and optional `USE_DEFAULT_ATTR1`/`DEFAULT_VAL_ATTR1` select default attribute behavior.
- `FLAT_SHADE`, `ROTATE_PC_PTR`, `PRIM_ATTR`, `PT_SPRITE_TEX`, and `PT_SPRITE_TEX_ATTR1` control interpolation and point-sprite handling.
- `DUP`, `FP16_INTERP_MODE`, `ATTR0_VALID`, and `ATTR1_VALID` control duplicated/half-precision and valid-lane behavior.

Entries 20 through 31 have the same general SPI input-control purpose but fewer point-sprite fields in this generated layout than earlier entries, so consumers must not assume every repeated register has every field by name.

Other SPI registers include:

- `SPI_VS_OUT_CONFIG`: VS export count and primitive-export count.
- `SPI_PS_INPUT_ENA` and `SPI_PS_INPUT_ADDR`: 32-bit enable/address bitmaps for PS inputs.
- `SPI_INTERP_CONTROL_0`: point-sprite override and parameter-shade control.
- `SPI_PS_IN_CONTROL`: number of interpolants, parameter generation, offchip parameter enable, late PC deallocation, primitive interpolants, barycentric optimization disable, and wave32 enable.
- `SPI_BARYC_CNTL`: perspective/linear center and centroid behavior, position float location/ULC, and front-face bit behavior.
- `SPI_TMPRING_SIZE`, `SPI_GFX_SCRATCH_BASE_LO/HI`: scratch/temporary ring sizing and base address fields.
- `SPI_SHADER_IDX_FORMAT`, `SPI_SHADER_POS_FORMAT`, `SPI_SHADER_Z_FORMAT`, and `SPI_SHADER_COL_FORMAT`: index, position, depth, and up to eight color export format fields.

### SX and CB Blend State

The SX export/blend group controls downconversion and blend optimization:

- `SX_PS_DOWNCONVERT_CONTROL` has per-MRT format-mapping disable bits.
- `SX_PS_DOWNCONVERT` has per-MRT downconvert format fields.
- `SX_BLEND_OPT_EPSILON` has per-MRT epsilon fields.
- `SX_BLEND_OPT_CONTROL` has per-MRT color/alpha optimization disable bits plus `PIXEN_ZERO_OPT_DISABLE`.
- `SX_MRT0_BLEND_OPT..SX_MRT7_BLEND_OPT` define color source/destination optimization, color combine function, alpha source/destination optimization, and alpha combine function for each MRT.

`CB_BLEND0_CONTROL..CB_BLEND7_CONTROL` define the actual per-MRT blend equation and enablement: color source blend, color combine function, color destination blend, alpha source blend, alpha combine function, alpha destination blend, separate-alpha enable, blend enable, and ROP3 disable.

### Draw, Primitive Setup, and Filtering

`GFX_COPY_STATE` provides per-stage copy-state fields for vertex, hull, tessellation, geometry, pixel, compute, and mesh-like state paths. `VGT_DMA_BASE_HI`, `VGT_DMA_BASE`, `VGT_DRAW_INITIATOR`, and `VGT_EVENT_ADDRESS_REG` expose draw-initiation and event-address payload fields. `GE_MAX_OUTPUT_PER_SUBGROUP` controls geometry-engine output limits per subgroup.

`PA_SU_SC_MODE_CNTL` provides culling, face orientation, polygon mode, front/back polygon primitive type, polygon offset enablement, vertex window offset, provoking vertex selection, perspective correction disable, multi-primitive index-buffer enablement, right-triangle gradient reference, quad decomposition mode, and keep-together enablement.

Line and primitive filter controls include:

- `PA_SU_LINE_STIPPLE_CNTL` and `PA_SU_LINE_STIPPLE_SCALE`: line stipple reset, full-length expansion, fractional accumulation, and scale.
- `PA_SU_PRIM_FILTER_CNTL`: primitive-type filter disable bits, expansion enables, expansion constant, and right/bottom exclusion bits.
- `PA_SU_SMALL_PRIM_FILTER_CNTL`: small-primitive filter enablement, primitive-type disables, and 1x MSAA compatibility disable.

The range ends with the `PA_CL_NGG_CNTL` comment only; its field masks are outside this chunk.

## Control Flow and State Behavior

There is no local control flow in this header chunk. The macros are compile-time constants. Runtime behavior arises when driver code, command-stream construction, firmware tables, or clear-state packets write the corresponding MMIO/context registers.

The persistent state is hardware context state rather than C memory. Important hardware-visible state affected through these fields includes viewport transforms and depth ranges, scissor bounds, clip-plane coefficients, shader output/input routing, pixel-shader interpolation controls, blend constants, per-MRT blend equations, depth/stencil and EQAA state, VRS image/feedback base and dimensions, raster topology mapping, primitive filtering, line stipple state, and draw-initiation fields.

Several fields are not plain persistent configuration even though they are represented as masks:

- `PA_SC_VRS_RATE_CACHE_CNTL` includes cache update/flush request and flush-done status semantics.
- `VGT_DRAW_INITIATOR` and event-address registers participate in draw/event sequencing.
- `CP_PIPEID`, `CP_RINGID`, and `CP_VMID` describe command/context identity rather than render-state math.
- Many full-register data fields represent IEEE-like floating-point payloads or addresses, so their masks are `0xFFFFFFFFL` but their meaning is not an arbitrary integer.

Correct programming order is external to this file and belongs to the owning graphics-state setup paths, userspace command-stream ABI, firmware initialization tables, and hardware documentation.

## Dependencies and Integration Points

This chunk depends on the AMD generated-register-header convention:

- `gc_11_0_3_offset.h` provides register offsets/base indices for the same register names.
- Matching default/reset headers or clear-state tables provide initial values.
- AMDGPU helper macros consume the `__SHIFT` and `_MASK` constants to pack and unpack fields.

Direct includes of this exact GC 11.0.3 mask header in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0_3.c`

Observed source-tree integration signals include `amdgpu/clearstate_gfx11.h`, which contains clear-state values for many registers covered here: viewport scissors and Z ranges, VRS registers, blend constants, stencil state, SPI pixel-shader input controls, blend controls, `PA_SU_SC_MODE_CNTL`, `PA_CL_VTE_CNTL`, `PA_CL_VS_OUT_CNTL`, `PA_CL_NANINF_CNTL`, and related graphics context registers. This header chunk supplies the field-level metadata for the same hardware state families.

The fields are also part of the broader AMDGPU/KMD interface to userspace graphics drivers. Userspace command buffers may program many of these context registers through packetized state, while kernel-side clear-state and initialization paths ensure known reset values for protected or preloaded state.

## Risks

- Bitfield mistakes have high blast radius. A wrong shift or mask can corrupt adjacent register fields and cause rendering corruption, depth/stencil errors, blend errors, shader input mismatches, hangs, or GPU resets.
- Repeated register families invite copy/paste errors. `PA_CL_VPORT_*_0..15`, `SPI_PS_INPUT_CNTL_0..31`, `SX_MRT*_BLEND_OPT`, and `CB_BLEND*_CONTROL` are mostly regular but not perfectly interchangeable.
- Cross-generation similarity is risky. GC 11.0.0, GC 11.0.3, and later GC 12 headers share many names but can differ in fields or masks. Consumers must pair this file with GC 11.0.3 offsets/defaults and not mix generated generations.
- Full-register masks can hide type-sensitive payloads. Viewport floats, blend constants, clip-plane coefficients, scratch addresses, and VRS surface addresses all use broad masks but require correct value encoding and alignment.
- Topology and cache fields are hardware-configuration sensitive. Raster mapping, tile steering, CB cache policy, and VRS cache controls can affect coherency, performance, or feature correctness if applied without ASIC-specific constraints.
- Some fields have action/status semantics. Treating flush/update/draw/event fields as ordinary retained state can break synchronization or lose status information.

## Test and Validation Signals

Useful validation for this chunk is mostly compile-time and graphics-integration coverage:

- Build AMDGPU with GC 11.0.3 support so direct include users (`gfx_v11_0_3.c`, `gfxhub_v3_0_3.c`, `imu_v11_0_3.c`) continue to compile against the macro names.
- Validate clear-state generation and restore paths against `amdgpu/clearstate_gfx11.h`, especially viewport/scissor/Z defaults, SPI input defaults, blend controls, depth/stencil controls, and primitive setup defaults.
- Run graphics workloads that exercise multiple viewports, scissor rectangles, user clip planes, point sprites, flat/perspective interpolation, wave32 PS inputs, MSAA/EQAA, alpha-to-coverage, color/depth writes, and per-MRT blending.
- Exercise VRS paths that program rate images and feedback surfaces, then verify `PA_SC_VRS_RATE_CACHE_CNTL` update/flush behavior through rendered output and any available debug/status hooks.
- Run suspend/resume, GPU reset, and context-switch tests to ensure persistent graphics context state derived from these fields is reinitialized or restored correctly.
- Use render tests with NaN/Inf vertex values and clipping edge cases to validate `PA_CL_NANINF_CNTL`, `PA_CL_CLIP_CNTL`, `PA_CL_VTE_CNTL`, and `PA_CL_VS_OUT_CNTL` behavior.

## Unresolved Cross-Chunk References

This range begins after the definition of `PA_SC_VPORT_SCISSOR_9_TL` has already started in an earlier chunk, so the top-left X shift and related fields for viewport 9 are described there. It ends immediately after the `PA_CL_NGG_CNTL` register comment, leaving that register's actual field layout for the following chunk. The final per-file reconciliation should connect this chunk with neighboring chunks to describe the complete generated GC 11.0.3 register-mask header and its include guards.
