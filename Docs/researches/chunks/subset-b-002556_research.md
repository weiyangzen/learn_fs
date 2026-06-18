# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 17372-19737

## Purpose

This chunk is generated AMD GC 11.5.0 shader/register field metadata. It contains no executable C logic; it publishes preprocessor constants for register-field bit positions and masks in the graphics command/raster/DB/CB pipeline. Consumers combine these `REG__FIELD__SHIFT` and `REG__FIELD_MASK` macros with register offsets from the matching GC 11.5.0 offset header and register access helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, and related AMDGPU macros.

The requested range is a mid-file slice of `gc_11_5_0_sh_mask.h`. It starts at the tail of `SPI_PS_INPUT_CNTL_29`, covers complete shader interpolator, vertex geometry/tessellation, primitive assembly, rasterizer, scan converter, depth buffer, blending, and color-buffer render-target field definitions, and stops after the beginning of the `CB_COLOR7_VIEW` field set. The chunk contains 184 register comment groups and 2,182 `#define` lines: 1,090 `__SHIFT` macros and 1,092 `_MASK` macros.

Although the path is under a local `ceph-client` source mirror, this header is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, allocation paths, or locks in this range. The interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the zero-based bit position used to insert or extract a field value.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for that field after it is shifted into register position.

These macros are consumed by token-pasting helpers. For example, `REG_SET_FIELD(value, VGT_SHADER_STAGES_EN, VS_W32_EN, 1)` expands through `VGT_SHADER_STAGES_EN__VS_W32_EN__SHIFT` and `VGT_SHADER_STAGES_EN__VS_W32_EN_MASK`. The related CGS helpers in `include/cgs_common.h` use the same naming contract through `CGS_REG_FIELD_SHIFT`, `CGS_REG_FIELD_MASK`, `CGS_REG_SET_FIELD`, and `CGS_REG_GET_FIELD`.

Major macro families in this slice:

- `SPI_*`: pixel-shader input controls for parameters 30 and 31, vertex-shader export counts, pixel-shader input enable/address bits, interpolation controls, barycentric controls, temporary ring size, scratch base address, and shader export format fields.
- `SX_*` and `CB_BLEND*_CONTROL`: shader export down-conversion, blend optimization epsilon/control fields, per-MRT source/destination blend optimization, and per-render-target color/alpha blend factors/functions/enables.
- `DB_*`: depth/stencil test control, EQAA sample-count and quality fields, shader depth/export behavior, HTILE surface metadata, stencil-results compare state, preload windows, alpha-to-mask, and depth bias format support.
- `PA_CL_*`, `PA_SU_*`, and `PA_SC_*`: clipping, viewport transform, vertex output semantics, NaN/Inf handling, culling, polygon mode/offset, point and line sizes, primitive filtering, stereo and VRS controls, scan-converter mode, anti-alias sample locations and masks, conservative rasterization, NGG mode, shader-control, and primitive binning fields.
- `VGT_*`, `GE_*`, `IA_*`, and `WD_*`: draw initiation, DMA/index-buffer state, primitive ID, event initiation, draw payload, ESGS ring item size, tessellation distribution, shader-stage enablement, LS/HS and tessellation factor parameters, streamout draw state, GS output limits, and NGG subgroup sizing.
- `CB_COLOR0` through `CB_COLOR6` plus the start of `CB_COLOR7`: render-target base, view, format/number type/component swap/blend optimization, fragment attributes, FDCC/DCC compression controls, and DCC base-address fields.

## Control Flow

This header has no runtime control flow. Runtime sequencing belongs to the graphics driver, firmware, command processor packets, and user-mode graphics stack that program the registers represented here:

1. AMDGPU code includes `gc_11_5_0_offset.h` and `gc_11_5_0_sh_mask.h` for GC 11.5.0 ASIC support.
2. Code forms register values by shifting and masking individual fields, usually through `REG_SET_FIELD` or `REG_GET_FIELD`.
3. Register offsets are supplied by the offset header and passed to direct MMIO helpers such as `RREG32_SOC15`/`WREG32_SOC15`, indirect accessors, or command-buffer packet emission paths.
4. Hardware consumes the resulting state during draw dispatch, tessellation, geometry/NGG processing, rasterization, depth/stencil testing, blending, compression, and render-target writes.

Within this repository snapshot, the exact `gc_11_5_0_sh_mask.h` include is visible in `amdgpu/gfxhub_v11_5_0.c`, where other fields from the same generated header are used for VM/GFXHUB programming and fault decode. Direct C references to the specific 3D pipeline masks in this chunk were not found in the searched AMDGPU/display/PM sources, which is expected for generated register databases: some fields are used by packet builders, shared macro tables, out-of-tree consumers, or retained for ASIC completeness even when not referenced by this kernel slice.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed and command-processor-visible GPU state. The represented state includes:

- Pixel-shader interpolation and barycentric state: which inputs are enabled, where they are addressed, flat-shade behavior, default attributes, FP16 interpolation, and primitive-attribute routing.
- Shader export and blend state: render-target format mapping, down-conversion, blend optimization, per-MRT blend controls, color-control modes, and ROP behavior.
- Depth and stencil state: Z/stencil enablement, comparison functions, write enables, bounds testing, EQAA/coverage behavior, shader Z/stencil/mask export controls, HTILE-related surface fields, preload regions, and alpha-to-mask.
- Rasterization state: clipping/culling rules, viewport transform enablement, point/line/raster mode controls, sample positions and sample masks, centroid priority, primitive filtering, VRS, conservative rasterization, and binning/NGG behavior.
- Vertex geometry/tessellation state: draw source, index-buffer address/type, shader-stage enables, LS/HS and tessellation factor parameters, primitive ID, streamout opaque-draw registers, and GS/NGG subgroup limits.
- Render-target state: color buffer base addresses, array slice/mip views, format/number type/component swap fields, fragment count attributes, DCC/FDCC compression toggles, and DCC base addresses for color slots 0 through 6 in this chunk.

Persistence is hardware-defined. Most context registers retain programmed values until the next context restore, command stream update, modeset-like graphics reset, GPU reset, suspend/resume, or power-gating transition. Status/debug/counter fields, event initiators, and clear/copy/decompress controls may be transient, sticky, write-one-to-clear, or sequencing-sensitive, but this generated mask header does not encode access type or side-effect semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated GC 11.5.0 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h` for the corresponding `reg...` or `mm...` register offsets.
- Other GC 11.5.0 generated headers, including any default-value and enum headers used by the same ASIC support code.
- AMDGPU register helpers that assume the `REG__FIELD__SHIFT` and `REG__FIELD_MASK` naming contract, including `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15*`, `CGS_REG_SET_FIELD`, and `CGS_REG_GET_FIELD`.

Observed direct include site:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.c`

Broader integration points are the GC graphics pipeline and command submission paths. Render state represented by this chunk is normally derived from API pipeline state, shader metadata, framebuffer attachments, MSAA/VRS/depth-stencil configuration, and tiling/compression layout decisions, then emitted as register writes or command packets. The `CB_COLOR*`, `DB_*`, `PA_*`, `SPI_*`, `SX_*`, and `VGT_*` families line up with classic GPU pipeline stages: shader input/export, primitive assembly, tessellation/geometry, clipping/setup, rasterization, depth/stencil, blending, and color output.

## Risks And Edge Cases

- Field drift is the central risk. These macros are untyped constants, so an incorrect shift or mask can compile cleanly while corrupting unrelated bits in a hardware register.
- Generated-header pairing matters. A GC 11.5.0 mask header used with the wrong offset/default/enum header can address the right-looking symbolic register name with incompatible bit layout.
- Repeated render-target and MRT families are copy-sensitive. `CB_BLEND0` through `CB_BLEND7` and `CB_COLOR0` through `CB_COLOR6` are structurally similar but slot-specific; one bad generated value may only fail with multiple render targets, a high-numbered color attachment, or DCC/FDCC enabled.
- Chunk boundaries are artificial. The first line is the tail of `SPI_PS_INPUT_CNTL_29`, while the end stops inside the `CB_COLOR7` register family. Adjacent chunks are required before making complete claims about all pixel-shader input controls or all eight color-buffer slots.
- Compression and render-target fields are high impact. Incorrect `CB_COLOR*_FDCC_CONTROL`, `CB_COLOR*_DCC_BASE`, or format/number-type masks can cause visual corruption, incorrect blending, GPU faults, or data loss in compressed render targets.
- Rasterization fields interact with subtle API behavior. Incorrect sample locations, sample masks, conservative rasterization, VRS, centroid priority, flat shading, clip/cull, or viewport-transform fields can produce failures limited to MSAA, VRS, tessellation, geometry-shader, point/line, or conservative-raster workloads.
- Depth/stencil state is side-effect-sensitive. Misprogrammed DB fields can break early/late Z, stencil export, alpha-to-coverage, HTILE use, depth clears/copies/decompresses, or shader depth export ordering.
- Several fields are architectural or reserved-looking in this generated view. Consumers must rely on ASIC documentation and existing driver sequencing, not infer writability or reset values from the presence of a mask.

## Test Signals

Useful validation is a mix of generated-header consistency, build coverage, and graphics behavior:

- Build AMDGPU with GC 11.5.0 support enabled; missing or renamed macros should fail in code that includes `gc_11_5_0_sh_mask.h` and uses `REG_SET_FIELD`/`REG_GET_FIELD`.
- Mechanically verify that field masks are compatible with shifts for each register and that repeated families such as `CB_BLEND*`, `SX_MRT*_BLEND_OPT`, `PA_SC_AA_SAMPLE_LOCS_*`, and `CB_COLOR*` retain expected slot-to-slot structure.
- Diff this generated chunk against AMD's authoritative GC 11.5.0 register database and against nearby GC 11.x headers where compatibility is expected; intentional ASIC deltas such as new `PRIM_ATTR`, `NUM_PRIM_INTERP`, W32, NGG, VRS, FDCC, and binning fields should be reviewed explicitly.
- Run graphics conformance and stress workloads that cover the represented pipeline state: multi-render-target blending, integer/float render-target formats, alpha-to-coverage, MSAA sample positions/masks, depth/stencil tests and shader depth export, conservative rasterization, VRS, primitive filtering, tessellation, geometry/NGG, streamout opaque draws, and indexed draws.
- Exercise DCC/FDCC paths with color compression enabled and disabled, including clears, resolves, copies, decompression, render-target transitions, and high-numbered color slots.
- Watch kernel logs, GPU fault reports, hangs, visual corruption, CRC mismatches, render-target compare failures, and reset/recovery paths. GFXHUB VM faults from CB/DB clients are especially relevant because incorrect render-target or depth state can surface as memory access faults.

## Cross-Chunk Notes

The previous chunk owns the earlier `SPI_PS_INPUT_CNTL_*` definitions and the beginning of this chunk starts with only the final mask lines for `SPI_PS_INPUT_CNTL_29`. Later chunks continue after `CB_COLOR7_VIEW` and are needed for complete coverage of color slot 7 and the rest of the GC 11.5.0 shader/register mask namespace. The final per-file research document should merge adjacent chunks before making complete claims about all render-target, depth-buffer, shader, or rasterization registers in `gc_11_5_0_sh_mask.h`.
