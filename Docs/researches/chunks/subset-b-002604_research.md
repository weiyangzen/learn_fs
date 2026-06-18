# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 30184-32568

## Scope

This chunk covers a generated AMD GC 12.1.0 shader/register mask header range. It starts in the middle of `SPI_PS_INPUT_CNTL_23` and ends in the middle of `PA_SC_ENHANCE_2`, so merge-time reconciliation should join it with adjacent chunks for the complete file-level view. The range contains 2,179 `#define` macros: field shift constants named `...__SHIFT` and bit masks named `..._MASK` for graphics pipeline registers.

## Purpose

The header provides compile-time bitfield metadata for programming GC 12.1.0 registers in the AMDGPU driver. These macros let C code construct, mask, compare, or patch hardware register values without embedding raw bit positions. The covered registers describe late graphics-pipeline state: pixel shader input interpolation, shader export/blend optimization, color blend controls, primitive assembly and clipping/rasterization controls, depth/HiZ/HiS and binning controls, MSAA sample locations and masks, render target color buffer state, and several PA/SC enhancement controls.

The chunk does not implement functions or own runtime logic. Its behavioral importance comes from being included alongside companion address headers such as `gc_12_1_0_d.h`, where `mm...` register offsets are defined, and from being consumed by AMDGPU register programming paths, golden-register initialization, generated clear-state tables, command emission, and debug/register decode helpers.

## Important API Surface

- `SPI_PS_INPUT_CNTL_23` through `SPI_PS_INPUT_CNTL_31` expose per-pixel-shader input fields: `OFFSET`, `DEFAULT_VAL`, `FLAT_SHADE`, `ROTATE_PC_PTR`, `PRIM_ATTR`, `DUP`, `FP16_INTERP_MODE`, `USE_DEFAULT_ATTR1`, `DEFAULT_VAL_ATTR1`, `ATTR0_VALID`, and `ATTR1_VALID`. These shape how SPI routes interpolated or default primitive attributes into the pixel shader.
- `SPI_BARYC_SSAA_CNTL`, `SPI_TMPRING_SIZE`, and `SPI_GFX_SCRATCH_BASE_LO/HI` cover shader interpolation/sample behavior and shader scratch/tmp-ring memory programming. Scratch base fields split GPU addresses across low/high registers.
- `SX_PS_DOWNCONVERT_CONTROL`, `SX_PS_DOWNCONVERT`, `SX_BLEND_OPT_EPSILON`, `SX_BLEND_OPT_CONTROL`, and `SX_MRT0_BLEND_OPT` through `SX_MRT7_BLEND_OPT` describe shader-export color downconversion and per-MRT blend optimization controls.
- `CB_BLEND0_CONTROL` through `CB_BLEND7_CONTROL` define per-render-target blend equation fields: color/alpha source blend, destination blend, combine function, separate alpha blending, enable, and `DISABLE_ROP3`.
- `PA_CL_*`, `PA_SU_*`, `PA_SC_*`, `GE_*`, `VGT_*`, and `DB_*` macros cover primitive setup, clipping, viewport transform enablement, NGG/subgroup control, line/point state, stereo, variable-rate shading, conservative rasterization, AA sample layout, HiZ/HiS metadata surfaces, DB/HTILE behavior, GS output sizing, and draw payload handling.
- `CB_TARGET_MASK`, `CB_SHADER_MASK`, `CB_COLOR_CONTROL`, `CB_COLOR{0..7}_*`, and `CB_MEM{0..7}_INFO` define color buffer render target masks, shader write masks, color-control mode bits, render target base addresses, views, dimensions, swizzle/resource type attributes, FDCC compression controls, extended base-address bits, format/compression metadata, and memory info.
- The tail switches to address block `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_pfvf_padec` and defines `PA_SC_VRS_SURFACE_CNTL`, `PA_SC_ENHANCE`, `PA_SC_ENHANCE_1`, and the first part of `PA_SC_ENHANCE_2`, covering VRS surface/cache controls and many rasterizer/scanner enhancement or workaround bits.

## Control Flow

There is no executable control flow in this range. Control flow is indirect: driver code combines these masks and shifts into register writes that are emitted through AMDGPU MMIO accessors, command processor packets, clear-state arrays, or golden-register setup. A typical use is:

1. Start from a desired 32-bit register value or a read-modify-write value.
2. Clear a field with `~REGISTER__FIELD_MASK`.
3. Insert a value with `(value << REGISTER__FIELD__SHIFT) & REGISTER__FIELD_MASK`.
4. Write the result to the matching `mmREGISTER` offset from the companion register-address header.

Because many registers in this range are replicated by slot, state emission code generally loops or expands over MRT/render-target indices 0 through 7, selecting matching `CB_COLORn_*`, `CB_BLENDn_CONTROL`, or `SX_MRTn_BLEND_OPT` macros.

## State and Persistence

The macros are stateless, but they describe persistent GPU context state. Values programmed into these registers persist in the graphics context until changed by later command streams, clear-state restore, context switch restore, or device reset. Important persistent domains include:

- Pixel shader ABI state in `SPI_PS_INPUT_CNTL_*`, where invalid offsets/default selectors can misroute attributes or feed undefined/default values into shaders.
- Render target and blend state in `CB_*` and `SX_*`, including blend equations, color write masks, base addresses, view ranges, format metadata, swizzle/resource type, FDCC compression, and extended base-address fields.
- Rasterization state in `PA_*`, `GE_*`, and `VGT_*`, including clip/viewport behavior, point and line parameters, primitive filtering, NGG limits, over-rasterization/conservative rasterization, VRS, binning, and MSAA sample positions.
- Depth/metadata state in `DB_HTILE_SURFACE` and `PA_SC_HIZ/HIS_*`, where address/size/control mismatches can corrupt metadata or cause incorrect depth/stencil visibility behavior.

The generated constants themselves are stable build artifacts; persistence risk is in consumers using the wrong field width, wrong generation, or wrong companion address header for the actual ASIC revision.

## Dependencies and Integration Points

- Depends on naming and bit layouts generated from AMD GC 12.1.0 register specifications. This header must remain synchronized with `gc_12_1_0_d.h` register offsets and other GC 12.1.0 generated headers.
- Integrated through AMDGPU graphics code under `drivers/gpu/drm/amd/amdgpu`, which uses SOC15 register helpers, golden-register tables, clear-state arrays, and command submission paths. Repository search shows related legacy/current usage patterns for `SPI_PS_INPUT_CNTL_23` clear-state entries and `PA_SC_ENHANCE_2` golden-register programming in other GFX generations.
- Connected to user-visible graphics APIs through Mesa/KFD/AMDGPU state emission: render target setup, blending, MSAA, VRS, conservative rasterization, shader scratch, and primitive/rasterizer state eventually map to these register fields.
- Uses C preprocessor constants only; no type checking is available. Consumers must pair the correct `REGISTER__FIELD__SHIFT` with the matching `REGISTER__FIELD_MASK`.

## Risks

- Bitfield drift is the primary risk. If generated masks do not match the hardware specification or the corresponding address header, register writes can silently program the wrong field.
- The chunk starts and ends inside register definitions. Documentation or automated processing must not treat this chunk as containing complete definitions for `SPI_PS_INPUT_CNTL_23` context or all of `PA_SC_ENHANCE_2`.
- Repeated indexed registers create copy/paste hazards. `CB_COLORn_*`, `CB_BLENDn_CONTROL`, and `SX_MRTn_BLEND_OPT` fields are mostly parallel; using the wrong target index can bind, blend, or compress the wrong MRT.
- Address-splitting and extended-base fields are sensitive. `SPI_GFX_SCRATCH_BASE_LO/HI`, `CB_COLORn_BASE`, and `CB_COLORn_BASE_EXT` must be composed consistently with GPU address alignment rules.
- Compression and metadata fields such as `CB_COLORn_FDCC_CONTROL`, `CB_COLORn_INFO`, `CB_MEMn_INFO`, `DB_HTILE_SURFACE`, and HiZ/HiS base/size registers have high corruption risk if mismatched with allocation layout or clear/decompress paths.
- Enhancement/workaround bits in `PA_SC_ENHANCE*` often encode hardware-specific behavior. Incorrect defaults can cause rendering hangs, missed synchronization, power regressions, or subtle rasterization differences.

## Test Signals

- Build coverage: compile AMDGPU with this generated header included; syntax errors, duplicate definitions, or missing masks surface immediately.
- Register-generation consistency: compare this header with the matching GC 12.1.0 register XML/spec generation output and with `gc_12_1_0_d.h` names for one-to-one address/mask pairing.
- Graphics conformance: Vulkan/OpenGL CTS coverage for blending, MRT color masks, MSAA sample positions, conservative rasterization, VRS, point/line rendering, clipping, and render-target formats exercises many fields in this chunk.
- Runtime smoke tests: boot a GC 12.1.0 ASIC, run display and 3D workloads, and watch for GPU hangs, VM faults, render corruption, or golden-register programming warnings.
- Debug validation: register dumps after known state emission should decode cleanly using the same masks, especially `CB_COLOR{0..7}_*`, `CB_BLEND{0..7}_CONTROL`, `PA_SC_AA_*`, `PA_SC_BINNER_*`, and `PA_SC_ENHANCE*` fields.
