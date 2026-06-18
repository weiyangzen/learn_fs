# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h lines 7290-9799

## Scope

This chunk covers generated shift and mask macros from the AMD GC 9.4.2 shader/mask register header. The covered range starts in the `GDS_OA_VMID9`/`GDS_OA_VMID10` area and continues through most of `SPI_BARYC_CNTL`, stopping at `SPI_BARYC_CNTL__POS_FLOAT_ULC_MASK`. The next line in the source file defines `SPI_BARYC_CNTL__FRONT_FACE_ALL_BITS_MASK`, so this chunk ends one line before the `SPI_BARYC_CNTL` family is fully complete.

The major register groups in this range are:

- GDS ordered-append VMID masks, GWS reset bits, ordered-append reset masks, GDS enhancement flags, and GDS context-switch counters.
- The start of `addressBlock: gc_gfxdec0`, including depth-buffer, stencil-buffer, HTILE, depth bounds, depth clear, and depth/stencil read/write base fields.
- Screen, window, generic, clip-rect, and viewport scissor fields, plus viewport depth range registers.
- Color-buffer target/shader masks and blend constant channels.
- Primitive assembler and scan-converter state such as raster config, tile steering, edge rules, hardware screen offsets, and grid fields.
- Command processor context selectors for perfmon context, pipe id, ring id, and VMID.
- Viewport transform registers, user clip-plane registers, programmable near clip Z, and pixel-shader input interpolation control.

The file is a generated hardware register bitfield map. This chunk defines C preprocessor constants only: there are no functions, structs, variables, persistence objects, or executable branches in the header itself.

## Purpose

The purpose of this header range is to provide the bit-level ABI between GC 9.4.2 hardware registers and AMDGPU/KFD code that composes or decodes register values. Each field is represented in the usual generated form:

- `<REGISTER>__<FIELD>__SHIFT`, giving the field's bit offset.
- `<REGISTER>__<FIELD>_MASK`, giving the 32-bit field mask.

The paired `gc_9_4_2_offset.h` file supplies register addresses such as `regGDS_GWS_RESET0`, `regDB_RENDER_CONTROL`, `regDB_Z_INFO`, `regPA_SC_VPORT_SCISSOR_0_TL`, and `regSPI_PS_INPUT_CNTL_0`; this header supplies the corresponding field layouts. Consumers combine these constants through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and packet-building code that writes context registers through command processor packets.

## Important Macro Families

### GDS VMID, Reset, and Context-Switch State

The chunk begins with ordered-append VMID masks for `GDS_OA_VMID9` through `GDS_OA_VMID15`, where the low 16 bits are a VMID-specific mask and the high 16 bits are marked unused. It then defines two 32-bit GWS reset banks:

- `GDS_GWS_RESET0__RESOURCE0_RESET` through `RESOURCE31_RESET`.
- `GDS_GWS_RESET1__RESOURCE32_RESET` through `RESOURCE63_RESET`.

`GDS_GWS_RESOURCE_RESET` provides a single-resource reset command style field with `RESET` plus an 8-bit `RESOURCE_ID`. `GDS_OA_RESET_MASK` and `GDS_OA_RESET` define reset selection for ordered-append resources by ME/pipe, including ME0 graphics/pixel/vertex/compute/geometry reset bits and ME1/ME2 pipe reset bits.

`GDS_ENHANCE` contains miscellaneous and control flags for GDS behavior, including auto-increment index, CGPG restore, read-buffer tag miss handling, GDSA/GDSO clock-gating disables, WD GDS CSB override, GDS clock enhance disable, DS memory clock gate disable, and unused high bits. `GDS_OA_CGPG_RESTORE` exposes ordered-append backup counters and `GDS_CS_CTXSW_STATUS` / `GDS_GFX_CTXSW_STATUS` expose context-save state such as `BUSY`, `GFX_OPCODE`, and `OA_STATE`.

The numerous `GDS_*_CTXSW_CNT*` registers share a simple layout: `UPDN` in bits 0-15 and `PTR` in bits 16-31. Covered variants exist for CS, VS, PS0 through PS7, and GS, with four counters per stage. These fields support GDS context-save/restore bookkeeping around graphics or compute context switches.

### Depth, Stencil, HTILE, and Render Override

The `gc_gfxdec0` section starts with DB register fields:

- `DB_RENDER_CONTROL` controls depth/stencil copy, resolve, decompress, resummarize, and tile-surface enable modes.
- `DB_COUNT_CONTROL` selects sample/rate behavior, Z-pass increment mode, perfect-Z-pass counting, and disabled sample detection.
- `DB_DEPTH_VIEW` defines slice start/max.
- `DB_RENDER_OVERRIDE` and `DB_RENDER_OVERRIDE2` carry force/disable/override controls for Z, stencil, HiZ, HiS, compression, sample counts, quad export, centroids, conservative Z export, decompression, and late-Z behavior.
- `DB_HTILE_DATA_BASE` and `_HI`, `DB_Z_READ_BASE`, `DB_Z_WRITE_BASE`, `DB_STENCIL_READ_BASE`, and `DB_STENCIL_WRITE_BASE` define low/high address fragments for depth/stencil and HTILE surfaces.
- `DB_Z_INFO`, `DB_STENCIL_INFO`, `DB_Z_INFO2`, and `DB_STENCIL_INFO2` define format, tiling, swizzle, compression, clear, metadata, TC compatibility, and related surface interpretation bits.
- `DB_DEPTH_SIZE`, `DB_DEPTH_BOUNDS_MIN`, `DB_DEPTH_BOUNDS_MAX`, `DB_STENCIL_CLEAR`, `DB_DEPTH_CLEAR`, and `DB_DFSM_CONTROL` define size, clear values, bounds, and depth/stencil state-machine control.

These fields are render-context state. They are normally programmed by command submissions or clear-state initialization, not by ordinary CPU-side persistent storage.

### Scissor, Clip, Raster, and Viewport State

The PA/SC portion defines many coordinate-packed registers:

- `PA_SC_SCREEN_SCISSOR_TL/BR`, `PA_SC_WINDOW_SCISSOR_TL/BR`, `PA_SC_GENERIC_SCISSOR_TL/BR`, and `PA_SC_VPORT_SCISSOR_0..15_TL/BR` use `TL_X`, `TL_Y`, `BR_X`, and `BR_Y` fields, with top-left registers also carrying a `WINDOW_OFFSET_DISABLE` bit where applicable.
- `PA_SC_WINDOW_OFFSET` and `PA_SU_HARDWARE_SCREEN_OFFSET` define signed or packed X/Y offsets.
- `PA_SC_CLIPRECT_0..3_TL/BR` and `PA_SC_CLIPRECT_RULE` define four clip rectangles and a 16-bit rule mask.
- `PA_SC_EDGERULE` packs `ER_TRI`, `ER_POINT`, `ER_RECT`, and four line edge-rule fields.
- `PA_SC_VPORT_ZMIN_0..15` and `PA_SC_VPORT_ZMAX_0..15` provide full 32-bit min/max depth values for each viewport.
- `PA_SC_RASTER_CONFIG`, `PA_SC_RASTER_CONFIG_1`, `PA_SC_SCREEN_EXTENT_CONTROL`, and `PA_SC_TILE_STEERING_OVERRIDE` describe raster pipe/bank mappings, shader-engine pairing, screen extent control, and tile steering override.
- `PA_SC_RIGHT_VERT_GRID`, `PA_SC_LEFT_VERT_GRID`, and `PA_SC_HORIZ_GRID` provide grid-offset and grid-count fields used by scan-converter setup.

These fields determine clipping, viewport extent, rasterization placement, and tile-to-pipe routing. The clearstate tables in this tree contain reset-like values for many of these names, for example `PA_SC_VPORT_SCISSOR_0_TL` through `PA_SC_VPORT_SCISSOR_15_BR` and default viewport Z min/max values in `clearstate_gfx10.h` and neighboring generation clearstate headers.

### Color Buffer Masks, Blend Constants, and CP Context Selectors

`CB_TARGET_MASK` and `CB_SHADER_MASK` expose four-bit channel write masks for up to eight MRTs. `CB_BLEND_RED`, `CB_BLEND_GREEN`, `CB_BLEND_BLUE`, and `CB_BLEND_ALPHA` define full-register blend constant values. `CB_DCC_CONTROL` controls DCC overwrite-combiner, independent block size, max compressed block size, max uncompressed block size, and related compatibility/control flags.

`CP_PERFMON_CNTX_CNTL`, `CP_PIPEID`, `CP_RINGID`, and `CP_VMID` define context selector fields used by CP-visible state. They are narrow registers, but wrong values can associate render or perfmon state with the wrong pipe, ring, or VMID.

### Viewport Transform and User Clip Planes

The `PA_CL_VPORT_*` families define viewport transform scale and offset registers for X, Y, and Z over viewport indices 0 through 15. Each is represented as a full 32-bit `DATA` field. The chunk also defines six user clip planes, `PA_CL_UCP_0_*` through `PA_CL_UCP_5_*`, with X/Y/Z/W components as full 32-bit fields, plus `PA_CL_PROG_NEAR_CLIP_Z`.

These are shader/raster interface state registers. Their bitfields are intentionally simple because they transport float or raw 32-bit payloads rather than sub-bit control fields.

### SPI Pixel-Shader Input and Interpolation State

`SPI_PS_INPUT_CNTL_0` through `SPI_PS_INPUT_CNTL_31` define pixel-shader input mapping and interpolation behavior. Inputs 0-19 include fields for `OFFSET`, `DEFAULT_VAL`, `FLAT_SHADE`, `ROTATE_PC_PTR`, `PT_SPRITE_TEX`, `FP16_INTERP_MODE`, default attribute-1 behavior, and attribute validity. Inputs 20-31 have a related but slightly smaller layout that omits `ROTATE_PC_PTR` and `PT_SPRITE_TEX`, retaining offset/default/flat/dup/FP16/default-attr/valid bits. This split is easy to miss because the names are mechanically similar.

`SPI_VS_OUT_CONFIG` provides vertex-shader export count and half-pack control. `SPI_PS_INPUT_ENA` and `SPI_PS_INPUT_ADDR` share fields for perspective, linear, pull-model, line stipple, position, front-face, ancillary, sample coverage, and fixed-point position inputs. `SPI_INTERP_CONTROL_0` controls flat shading, point-sprite enable, X/Y/Z/W point-sprite override selectors, and top-origin selection. `SPI_PS_IN_CONTROL` provides the number of interpolators, offchip parameter enable, late parameter-cache deallocation, and barycentric optimization disable. `SPI_BARYC_CNTL` starts at the end of the chunk and covers perspective/linear center and centroid controls, position float location, position upper-left-corner handling, and the shift for `FRONT_FACE_ALL_BITS`; its final mask line is outside this chunk.

## Control Flow and State Behavior

There is no runtime control flow in this header chunk. It affects compiled driver behavior by determining how code and packet builders pack or unpack 32-bit MMIO/context-register values.

The state represented here lives in GPU hardware context registers and command-stream state, not in the header. Some fields are ordinary persistent context state, such as scissor rectangles, viewport transforms, depth/stencil formats, blend constants, and PS interpolation controls. Others are command-like or reset/control fields, especially GDS/GWS reset bits, `GDS_GWS_RESOURCE_RESET__RESET`, and `GDS_OA_RESET__RESET`.

The DB, PA/SC, PA/CL, CB, and SPI fields are generally part of graphics context state that can be saved/restored by CP/RLC mechanisms or reset through clearstate programming. GDS context-switch counters and status fields are hardware bookkeeping for context save/restore. The macros do not describe sequencing, hazards, polling, or write-one-to-clear behavior; those rules have to come from the hardware specification and the driver paths that program the registers.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention:

- `gc_9_4_2_offset.h` supplies the register numbers and base indices for the names in this mask header.
- `gc_9_4_2_default.h` supplies reset/default values where generated defaults exist.
- AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_RLC`, and CP packet builders consume the `__SHIFT` and `_MASK` names.

Observed integration in this tree includes:

- `amdgpu/gfx_v9_4_2.c`, which includes `gc/gc_9_4_2_offset.h` and `gc/gc_9_4_2_sh_mask.h` for Aldebaran/GC 9.4.2 graphics support, golden settings, compute initialization, RAS/error paths, and register access.
- `amdgpu/amdgpu_amdkfd_aldebaran.c`, which also includes the GC 9.4.2 offset and mask headers for KFD-to-KGD debug, trap, watchpoint, queue, VMID, and wave-control integration.
- Clearstate tables such as `amdgpu/clearstate_gfx10.h` and nearby generation tables, which show the same class of DB, PA/SC, viewport, and SPI context registers being reset to known render-state values.
- Userspace graphics drivers and kernel command submission paths, which program many DB/CB/PA/SPI context registers through PM4 packets rather than direct CPU MMIO.

The register names are cross-generation familiar, but the exact field layout is generation-specific. In particular, the SPI input control layout differs across GC generations and even within this chunk between inputs 0-19 and 20-31.

## Risks

- Bitfield drift is high impact. A wrong mask or shift in DB, PA/SC, CB, or SPI state can cause incorrect depth/stencil tests, invalid clears, broken compression metadata, wrong scissor/viewport clipping, missing color channels, or bad pixel-shader interpolation.
- GDS reset fields are dense and mechanically repetitive. Off-by-one resource reset masks in `GDS_GWS_RESET0/1` could reset the wrong GWS resource, while wrong ordered-append pipe reset bits could disturb another ME or pipe.
- Context-switch counters all share `UPDN` and `PTR` layouts; incorrectly treating them as independent semantic counters rather than context-save bookkeeping can mislead diagnostics.
- DB surface address and metadata fields must match memory layout, tiling, swizzle, compression, and HTILE/DCC state. Bad values can produce GPU faults, corrupted depth/stencil data, or hangs.
- Scissor and viewport fields are signed/packed coordinate state. Mispacking top-left, bottom-right, or offset-disable bits can silently clip all rendering or allow rendering outside intended bounds.
- `PA_SC_RASTER_CONFIG` and tile steering fields encode topology-sensitive routing. Incorrect values can misroute work across raster pipes or shader engines.
- `SPI_PS_INPUT_CNTL_*` is split into two layouts. Applying the input 0-19 masks to input 20-31, or assuming `ROTATE_PC_PTR`/`PT_SPRITE_TEX` exist everywhere, can corrupt interpolation setup.
- This chunk ends before `SPI_BARYC_CNTL__FRONT_FACE_ALL_BITS_MASK`; the merge/reconciliation lane should join it with the next chunk so the final per-file report does not imply the `SPI_BARYC_CNTL` family is complete here.

## Test and Validation Signals

Useful validation is mostly build, bring-up, and graphics conformance coverage:

- Build AMDGPU and KFD code with GC 9.4.2 support enabled; this catches missing or renamed generated macros included by `gfx_v9_4_2.c` and `amdgpu_amdkfd_aldebaran.c`.
- Run graphics render tests that exercise depth/stencil formats, depth bounds, clears, resolves, HTILE metadata, compression/decompression, and stencil front/back reference/mask behavior.
- Run scissor, viewport, clip rectangle, user clip plane, programmable near clip, and viewport-depth-range tests across all 16 viewport slots.
- Run MRT color-mask and blend-constant tests to validate `CB_TARGET_MASK`, `CB_SHADER_MASK`, and `CB_BLEND_*` packing.
- Run pixel-shader interpolation tests covering flat shade, perspective/linear center/sample/centroid, pull model, point sprites, FP16 interpolation, default attributes, front-face, sample coverage, and position inputs.
- Exercise suspend/resume, GPU reset, preemption, and queue context-switch workloads to validate GDS context-switch status/counter behavior and GWS/OA reset sequencing.
- Compare generated `gc_9_4_2_*` headers against AMD's source register database or upstream-generated headers when refreshing this file; repeated families should be checked with scripts because visual review is error-prone.
