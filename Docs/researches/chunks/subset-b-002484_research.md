# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 19901-22380

## Purpose

This chunk is part of AMD's generated GC 10.3.0 register bitfield header. It defines `__SHIFT` and `__MASK` macros for graphics-context registers in the `gc_gfxdec0` address block, starting in the tail of `DB_COUNT_CONTROL`, covering depth-buffer, rasterizer/scissor, viewport, shader-pixel-input, color/blend state, and ending in the middle of the `CB_BLEND*` control series. The header itself contains no executable code; its purpose is to provide stable symbolic bit positions for users of `REG_SET_FIELD`, `REG_GET_FIELD`, packet builders, clear-state tables, and direct MMIO register programming in the AMDGPU/KFD driver.

The covered area is mostly context/register state used by graphics command submission and GPU initialization/reset paths. It is source-tree-aligned with the AMD DRM driver register stack: offset headers name registers, this `*_sh_mask.h` header names fields, and driver code composes or decodes register values through those macros.

## Important APIs, Types, and Macros

There are no C functions, structs, or runtime APIs in this slice. The exported interface is a large set of preprocessor constants following the pattern:

- `<REGISTER>__<FIELD>__SHIFT`: bit position of a hardware field.
- `<REGISTER>__<FIELD>_MASK`: mask for the field in the register word.

Important register groups in this chunk:

- `DB_*`: depth-buffer and stencil state, including `DB_DEPTH_VIEW`, `DB_RENDER_OVERRIDE`, `DB_RENDER_OVERRIDE2`, `DB_Z_INFO`, `DB_STENCIL_INFO`, depth/stencil read/write bases, HTILE base high/low, clears, bounds, and stencil reference masks. These fields encode depth/stencil formats, mip/slice selection, compression/decompression behavior, expclear support, read-only state, VRS overrides, cache policy, and base addresses.
- `PA_SC_*` and `PA_CL_*`: scan converter, rasterizer, and clip/viewport state. This includes screen/window/generic scissor rectangles, cliprects, 16 viewport scissor pairs, 16 viewport Z min/max pairs, raster configuration, tile steering, viewport scale/offset registers, user clip planes, and near-clip Z programming.
- `CB_*` and `SX_*`: color buffer, shader export, and blend state. This includes target and shader write masks, color blend constants, DCC control, coverage output, render-backend L2/cache control, pixel shader down-convert controls, blend optimization controls, `SX_MRT0..7_BLEND_OPT`, and `CB_BLEND0..3_CONTROL` within the requested range.
- `SPI_*`: shader processor interpolation and pixel shader input state, including `SPI_PS_INPUT_CNTL_0..31`, `SPI_PS_INPUT_ENA`, `SPI_PS_INPUT_ADDR`, interpolation control, PS input control, barycentric control, temporary ring size, and shader index/position/Z/color export formats.
- `CP_*`, `VGT_*`, and context placeholders: `CP_PERFMON_CNTX_CNTL`, `CP_PIPEID`, `CP_RINGID`, `CP_VMID`, `CONTEXT_RESERVED_REG0/1`, and index bound/reset registers for graphics command processor and vertex grouper/tessellator context.

Representative consumer patterns elsewhere in the tree show how this generated interface is intended to be used. For example, `gfx_v10_0_set_user_wgp_inactive_bitmap_per_sh()` builds `GC_USER_SHADER_ARRAY_CONFIG` by shifting a bitmap by the matching `__SHIFT`, masking with the matching `__MASK`, and writing the register. KFD wave-control code writes `SQ_CMD` through the same offset/mask framework. The same convention applies to fields in this chunk when callers need to update `DB_Z_INFO`, `SPI_PS_INPUT_CNTL_*`, or blend/scissor fields without hard-coding bit positions.

## Control Flow

This header has no direct control flow. Its influence is compile-time substitution into driver code that performs these runtime flows:

- Graphics context construction: command stream or kernel driver paths program DB/PA/SPI/SX/CB registers using these masks to encode depth/stencil, viewport, interpolation, export, and blending state.
- Initialization and reset: clear-state tables and default context-state programming include many of these registers, such as `DB_RENDER_OVERRIDE`, `DB_Z_INFO`, viewport scissors, `SPI_PS_INPUT_CNTL_*`, `SX_MRT*_BLEND_OPT`, and `CB_BLEND*_CONTROL`.
- Runtime register updates: direct MMIO paths use `REG_SET_FIELD`/`REG_GET_FIELD` with the register/field names to alter specific fields while preserving unrelated bits.
- Debug and validation: register dumps, hang analysis, and bring-up code rely on the symbolic field names to interpret or compose GC state consistently with the hardware packet/register ABI.

Because the file is generated-style data, the main "flow" is dependency flow: hardware specifications feed the header, the header feeds C macros, and those macros feed the driver register writes emitted during GPU initialization, command submission, context restore, and KFD/GFX management.

## State and Persistence Behavior

The macros describe hardware state, but they do not hold state themselves. Persistence depends on the target register:

- DB/PA/SPI/SX/CB registers are graphics context state. Their values can persist in GPU context images, command streams, or kernel-managed clear/default states until overwritten by later context programming or reset.
- Base address fields such as `DB_Z_READ_BASE`, `DB_Z_WRITE_BASE`, stencil base registers, HTILE base registers, `TA_BC_BASE_ADDR`, and `COHER_DEST_BASE*` represent GPU-address state. Incorrect high/low field composition can redirect depth/stencil, metadata, or coherency operations.
- Cache-control and compression fields (`DB_RMI_L2_CACHE_CONTROL`, `CB_RMI_GL2_CACHE_CONTROL`, `DB_Z_INFO`, `DB_STENCIL_INFO`, `CB_DCC_CONTROL`) affect memory visibility, compression validity, decompression, and export/clear behavior across draws.
- Viewport, scissor, cliprect, and shader-input fields persist as pipeline state for following draws until a new command stream changes them.
- `CP_VMID`, `CP_PIPEID`, and `CP_RINGID` describe command processor context identity and are sensitive to queue/context management.

## Dependencies

This chunk depends on the AMD GPU register ABI for GC 10.3.0 and must remain synchronized with sibling generated headers:

- `gc_10_3_0_offset.h` supplies register offsets for names whose field layout is defined here.
- AMDGPU helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` depend on the exact `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` naming convention.
- SOC15 register accessors such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32`, and `SOC15_REG_OFFSET` combine offset headers with these field definitions.
- Clear-state arrays such as `clearstate_gfx10.h` include default values for several registers in this group and must match the same hardware layout.
- Userspace-visible command submission and shader compilation flows indirectly depend on these layouts because command buffers and kernel state setup must agree on register field semantics.

## Integration Points

Primary integration points are in the AMD DRM GPU driver:

- GFX initialization and context setup in `drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c` and related generation-specific files.
- KFD wave/control and compute dispatch support, which uses the same generated register field convention for GC register programming.
- Clear-state headers and context restore paths that seed DB/PA/SPI/SX/CB defaults.
- Command processor, ring, and VMID management paths that need `CP_*` context fields.
- Render backend and depth/stencil code paths that compose DB/CB cache, compression, format, base-address, and blend fields.
- Shader and pipeline programming paths that populate SPI pixel-input controls, interpolation state, export formats, viewport transforms, and clipping/scissor state.

The file is not standalone; it becomes meaningful when included with the matching offset header and AMDGPU register helper macros.

## Risks and Edge Cases

- Bitfield drift is the highest risk. A wrong mask or shift silently writes the wrong hardware bits and can cause rendering corruption, GPU hangs, invalid memory access, or broken context save/restore.
- This chunk starts after the `DB_COUNT_CONTROL` heading and includes only its trailing masks. Chunk-level readers should reconcile the earlier lines during final merge so that `DB_COUNT_CONTROL` is not documented as beginning here.
- This chunk ends at `CB_BLEND3_CONTROL`; the `CB_BLEND4..7_CONTROL` continuation appears after the requested range. Final per-file reconciliation must merge the repeated blend-control pattern across adjacent chunks.
- Repeated register families create copy/paste or generator risks: viewport scissors/Z ranges, viewport scale/offsets, clip planes, `SPI_PS_INPUT_CNTL_0..31`, `SX_MRT0..7_BLEND_OPT`, and `CB_BLEND*` controls all rely on identical or near-identical layouts with only index changes.
- Address split registers (`*_BASE` plus `*_BASE_HI`) are sensitive to lost high bits and alignment assumptions such as 256-byte base fields.
- Reserved fields (`DB_RESERVED_REG_*`, `CONTEXT_RESERVED_REG*`, and named reserved subfields) must not be repurposed casually; hardware may require preserving reset values.
- Cache/compression fields in DB/CB registers are high-impact because stale compression metadata or wrong cache policy can produce subtle data corruption rather than immediate failures.
- VRS, viewport, scissor, and raster-config fields interact with draw clipping and sample locations. Invalid combinations may only appear under multisample, multi-viewport, or variable-rate shading workloads.

## Test Signals

Useful signals for changes touching this header or consumers of these fields:

- Compile coverage for AMDGPU/KFD with GC 10.x enabled; macro naming errors usually surface as build failures in `REG_SET_FIELD`/`REG_GET_FIELD` users.
- Boot and driver probe on a GC 10.3 ASIC or emulation target, checking register initialization and clear-state loading.
- Graphics smoke tests that exercise depth/stencil clears, HTILE compression, depth bounds, stencil read/write, color blending, DCC, multiple render targets, and MSAA.
- Piglit/dEQP/Vulkan CTS coverage for viewport/scissor arrays, clip planes, barycentric interpolation, PS input locations, MRT blend controls, color export formats, and depth/stencil formats.
- GPU hang and register-dump analysis: `DB_*`, `PA_SC_*`, `SPI_*`, `SX_*`, and `CB_*` values should decode consistently with the expected field masks.
- KFD/compute coexistence tests when command processor context fields or shared register helper conventions are modified.
- Static comparison against AMD-generated register headers for the same ASIC revision to catch accidental mask/shift edits.
