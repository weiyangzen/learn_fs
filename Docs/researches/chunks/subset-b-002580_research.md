# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 27681-30173

## Scope

This chunk covers a generated AMD GC 12.0.0 shader/register mask header section. It starts at the tail of `DB_SHADER_CONTROL` mask definitions, continues through depth/stencil, rasterizer/scissor, viewport, clip, variable-rate shading, pixel-shader input, scratch-ring, shader-export, SX blend optimization, and color-blend control field definitions, and ends at the `PA_CL_POINT_X_RAD` register marker before that register's fields appear in the next chunk.

The file is a register bitfield map only. It defines C preprocessor constants and has no functions, structs, variables, dynamic storage, or executable control flow. Each register field is represented by the normal AMDGPU generated pair:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

The adjacent `gc_12_0_0_offset.h` header supplies the register addresses. This `*_sh_mask.h` chunk supplies the bit positions and masks used to compose or decode the 32-bit values written to those registers.

## Purpose

The purpose of this range is to encode the ABI between GC 12 graphics hardware and the AMDGPU/KFD driver for render-state programming. The fields here are the low-level layout definitions for state that higher layers normally program through PM4 packets, ring commands, clear-state tables, firmware initialization, or direct MMIO helpers.

The covered state is centered on the graphics pipeline after primitive setup and before/around pixel export:

- Depth-buffer and stencil behavior through `DB_SHADER_CONTROL`, `DB_DEPTH_CONTROL`, `DB_STENCIL_CONTROL`, `DB_EQAA`, alpha-to-mask, stencil ref/op/read/write masks, and memory temporal/speculative-read policy.
- Screen, window, generic, cliprect, and per-viewport scissor rectangles, plus 16 viewport top-left/bottom-right pairs.
- User clip planes, guard-band clip/discard adjustment, per-viewport scale/offset/depth range, and near-clip control.
- Rasterizer routing and steering controls such as `PA_SC_RASTER_CONFIG`, `PA_SC_RASTER_CONFIG_1`, tile steering override, pipe/VMID selection, and screen extent control.
- Variable-rate shading surfaces and overrides through `PA_SC_VRS_*` base, size, info, override, and feedback fields.
- Pixel shader interpolation/input/export formats through `SPI_PS_IN_CONTROL`, `SPI_INTERP_CONTROL_0`, `SPI_SHADER_*_FORMAT`, `SPI_BARYC_*`, `SPI_PS_INPUT_ENA`, `SPI_PS_INPUT_ADDR`, and 32 `SPI_PS_INPUT_CNTL_n` registers.
- Scratch ring base/size through `SPI_TMPRING_SIZE` and `SPI_GFX_SCRATCH_BASE_LO/HI`.
- Shader export and color blend behavior through `SX_PS_DOWNCONVERT*`, `SX_BLEND_OPT_*`, `SX_MRT[0-7]_BLEND_OPT`, and `CB_BLEND[0-7]_CONTROL`.

## Important Macro Families

### Depth, Stencil, and Coverage State

The chunk begins in the middle of `DB_SHADER_CONTROL`, carrying masks for late pixel-shader/depth-buffer behavior such as kill/discard enable, coverage-to-mask, mask export, hierarchical-Z fallback execution, alpha-to-mask disable, depth-before-shader, conservative-Z export, dual-quad disable, ordered pixel shader, pre-shader depth coverage, OREO blend, and intrinsic-rate override. The corresponding shifts are immediately above this chunk, so consumers must see the full generated header rather than treating this line span as a standalone include.

`DB_DEPTH_CONTROL` defines enable bits and compare-function fields for stencil, Z, Z-write, depth bounds, Z function, backface handling, front stencil function, and backface stencil function. In GC 12 this chunk names bits 30 and 31 as reserved fields rather than the older color-write-on-depth-fail/pass names found in some sibling ASIC headers, so cross-generation code must not assume semantic compatibility for those high bits.

`DB_STENCIL_CONTROL` describes front and back stencil fail, Z-pass, and Z-fail operations. `DB_STENCIL_REF`, `DB_STENCIL_OPVAL`, `DB_STENCIL_READ_MASK`, and `DB_STENCIL_WRITE_MASK` provide paired front/back 8-bit values. These values are command-stream state, not kernel-owned persistent policy; the kernel's role is to provide correct masks for command construction and decode.

`DB_EQAA` and `DB_ALPHA_TO_MASK` cover enhanced quality anti-aliasing and alpha-to-coverage details: mask export sample count, alpha-to-mask sample count, high-quality intersections, static anchor associations, overrasterization amount, post-Z overrasterization, alpha-to-mask offsets, and offset rounding.

`SC_MEM_TEMPORAL` and `SC_MEM_SPEC_READ` expose temporal and speculative-read settings for VRS, HiZ, and HiS paths. These fields affect cache/memory behavior around raster/depth surfaces and are sensitive to hardware programming guidance.

### Viewports, Scissors, Clip Rectangles, and Clip Planes

The largest early block is the repeated viewport and scissor geometry layout:

- `PA_SC_VPORT_0_TL` through `PA_SC_VPORT_15_BR` encode 16 viewport top-left and bottom-right integer rectangles with 16-bit X/Y halves.
- `PA_SC_SCREEN_SCISSOR_TL/BR`, `PA_SC_WINDOW_OFFSET`, `PA_SC_WINDOW_SCISSOR_TL/BR`, `PA_SC_GENERIC_SCISSOR_TL/BR`, and `PA_SC_VPORT_SCISSOR_0_TL/BR` through `PA_SC_VPORT_SCISSOR_15_TL/BR` provide screen, window, generic, and per-viewport scissor bounds. Several top-left fields include `WINDOW_OFFSET_DISABLE`, and bottom-right fields include `DX10_DIAMOND_TEST_ENA` depending on the register.
- `PA_SC_CLIPRECT_RULE` and `PA_SC_CLIPRECT_0_TL/BR` through `PA_SC_CLIPRECT_3_TL/BR` define rule bits and four clip rectangles. The corresponding `PA_SC_CLIPRECT_0_EXT` through `PA_SC_CLIPRECT_3_EXT` add extended coordinate bits and discard flags.
- `PA_SC_EDGERULE` provides the table entries used by rasterization edge inclusion rules.
- `PA_SU_HARDWARE_SCREEN_OFFSET` defines signed or packed hardware screen offset fields.

The `PA_CL_UCP_0_X/Y/Z/W` through `PA_CL_UCP_5_X/Y/Z/W` field groups are full 32-bit values for six user clip planes. `PA_CL_PROG_NEAR_CLIP_Z` is another full-width programmed clip value. The later `PA_CL_GB_*_ADJ` and `PA_CL_VPORT_*` groups are also full-width data fields, typically floating-point bit patterns for guard-band and viewport scale/offset state.

### Raster Configuration and Routing

`PA_RATE_CNTL` provides packed sample or shading-rate control fields. `PA_SC_RASTER_CONFIG` contains the detailed tile-pipe, shader-engine, packer, rasterizer, scan converter, and SE map selectors used to route work across graphics pipes and shader engines. `PA_SC_RASTER_CONFIG_1` extends this with extra SE-pair mapping fields. These definitions are tightly coupled to ASIC topology, harvest configuration, and the matching offset/register list.

`PA_SC_SCREEN_EXTENT_CONTROL`, `PA_SC_TILE_STEERING_OVERRIDE`, `CB_CP_PIPEID`, and `CB_CP_VMID` expose additional screen-extent, pipe steering, pipe ID, and VMID fields. Incorrect values here can send raster or color-buffer traffic to the wrong backend resources.

### Variable-Rate Shading and Surface Addresses

The VRS-related groups are:

- `PA_SC_VRS_OVERRIDE_CNTL`, with override mode/rate/combiner fields.
- `PA_SC_VRS_RATE_FEEDBACK_BASE`, `_EXT`, and `_SIZE_XY`, defining feedback surface address and dimensions.
- `PA_SC_VRS_INFO`, exposing or programming rate and mode bits.
- `PA_SC_VRS_RATE_BASE`, `_EXT`, and `_SIZE_XY`, defining the VRS rate image surface address and dimensions.

Address fields are split into low and high/ext registers. Writers must preserve the expected address granularity and combine with the matching offset definitions; these macros only describe bit placement.

### Pixel Shader Input and Export State

`SPI_PS_IN_CONTROL` controls pixel-shader input count, parameter generation, barycentric/POS interpolation details, and related flags. `SPI_INTERP_CONTROL_0` contains point sprite, perspective, sample, center, flat-shade, and custom interpolation control fields. `SPI_SHADER_IDX_FORMAT`, `SPI_SHADER_POS_FORMAT`, `SPI_SHADER_Z_FORMAT`, and `SPI_SHADER_COL_FORMAT` define shader export formats for indices, position exports, Z/stencil/sample-mask style exports, and up to eight color exports.

`SPI_BARYC_CNTL` and `SPI_BARYC_SSAA_CNTL` provide barycentric coordinate policy, including perspective/linear center/centroid/sample control and supersampling controls.

`SPI_PS_INPUT_ENA` and `SPI_PS_INPUT_ADDR` are bitmaps for up to 32 pixel-shader inputs. The 32 `SPI_PS_INPUT_CNTL_n` groups describe each input slot's semantic offset, default value, flat-shade control, cyl-wrap, attractor, primitive-attribute, default flag, and in the first 20 slots additional attribute/per-sample/floating-point control fields. Slots 20-31 have a shorter field set in this generated table. These registers are a key ABI between shader compilation metadata and draw-time command emission.

`SPI_TMPRING_SIZE` and `SPI_GFX_SCRATCH_BASE_LO/HI` describe the temporary/scratch ring configuration used by shader execution. These interact with GPU virtual addresses and per-process or per-queue scratch allocation handled elsewhere in AMDGPU/KFD.

### SX and Color Blend State

`SX_PS_DOWNCONVERT_CONTROL` and `SX_PS_DOWNCONVERT` define per-MRT downconversion controls and formats. `SX_BLEND_OPT_EPSILON` supplies per-MRT epsilon settings, and `SX_BLEND_OPT_CONTROL` supplies per-MRT blend optimization disable/enable and optimization mode fields.

`SX_MRT0_BLEND_OPT` through `SX_MRT7_BLEND_OPT` define repeated source/destination optimization and combiner function fields for color and alpha blend paths. `CB_BLEND0_CONTROL` through `CB_BLEND7_CONTROL` define repeated render-target blend equation state: color source blend, color combiner, color destination blend, alpha source blend, alpha combiner, alpha destination blend, separate-alpha enable, blend enable, and ROP3 disable. These are per-MRT render state fields and are directly tied to color export and color-buffer behavior.

## APIs, Types, and Functions

There are no C APIs, types, or functions in this chunk. The usable interface is the macro naming contract consumed by generic AMDGPU helpers:

- `REG_FIELD_SHIFT(reg, field)` expands to `reg##__##field##__SHIFT`.
- `REG_FIELD_MASK(reg, field)` expands to `reg##__##field##_MASK`.
- `REG_SET_FIELD(orig, reg, field, val)` clears the masked field in a 32-bit word and inserts `val` at the generated shift.
- `REG_GET_FIELD(value, reg, field)` masks and shifts a field out of a 32-bit word.
- SOC15 register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, and field-write helpers combine this field layout with the address macros from the sibling offset header.

Direct include users for the GC 12.0.0 mask header in this source tree include `amdgpu/gfx_v12_0.c`, `amdgpu/soc24.c`, `amdgpu/mes_v12_0.c`, `amdgpu/sdma_v7_0.c`, `amdgpu/gfxhub_v12_0.c`, `amdgpu/imu_v12_0.c`, `amdgpu/amdgpu_amdkfd_gfx_v12.c`, `amdkfd/kfd_mqd_manager_v12.c`, and `amdkfd/kfd_device_queue_manager_v12.c`. The specific render-state macros in this chunk also align with clear-state tables such as `amdgpu/clearstate_gfx12.h`, where many of the same register names appear as initialized context state.

## Control Flow and Data Flow

This header has no runtime control flow. Its compile-time data flow is token concatenation:

1. Higher-level code names a register and field in a helper invocation, for example `REG_SET_FIELD(value, SOME_REGISTER, SOME_FIELD, field_value)`.
2. The helper expands that pair into `SOME_REGISTER__SOME_FIELD__SHIFT` and `SOME_REGISTER__SOME_FIELD_MASK`.
3. The generated constants from this header produce the correct masked 32-bit register value.
4. Separate address macros and MMIO/packet helpers send that value to hardware or decode it from a readback.

For draw/context state, the actual runtime flow is typically userspace or kernel command construction, PM4 packet emission to a ring, GPU command processor consumption, and hardware state update. For initialization state, arrays such as clear-state tables provide default register images. This chunk only supplies the bitfield layout used by those flows.

## State and Persistence Behavior

The macros themselves are compile-time constants and do not persist state. The hardware registers described by the macros hold volatile GPU context and configuration state. Depending on the register class, values may be:

- Draw or pipeline state restored by command streams and context switching.
- Clear-state/default context values loaded when initializing a graphics context.
- Per-queue or per-process shader scratch state.
- Surface-address and size state for VRS feedback/rate images.
- ASIC topology/routing state programmed during graphics initialization.

Persistence is therefore owned by GPU context save/restore, firmware, command processor state, kernel ring setup, and userspace driver command buffers, not by this header. The key persistence risk is that stale or cross-generation masks can silently preserve or corrupt unrelated bits when a field helper reads, clears, and writes a 32-bit register value.

## Dependencies and Integration Points

This chunk depends on the generated register-address headers for GC 12.0.0, especially `gc_12_0_0_offset.h`, and on AMDGPU common helper macros in headers such as `amdgpu.h` and `soc15_common.h`. It also depends semantically on AMD hardware register specifications and on the PM4/register programming model used by graphics, KFD, MES, SDMA, GFXHUB, and IMU code.

Important integration points include:

- Graphics initialization and golden/default register programming in `gfx_v12_0.c` and SOC24 setup code.
- KFD queue and MQD setup where compute/graphics queue state must match the GC 12 field layout.
- Clear-state initialization tables for GC 12 render context defaults.
- Userspace driver command buffers that rely on kernel-shipped register definitions and hardware ABI compatibility.
- Debug, tracing, and register decode paths that use `REG_GET_FIELD` to interpret register dumps.

## Risks and Maintenance Notes

- This range starts after several `DB_SHADER_CONTROL` shift definitions, so chunk-local analysis must remember that the full register definition crosses the chunk boundary.
- Reserved fields in `DB_DEPTH_CONTROL` differ from older sibling headers. Code shared across GC generations should use generation-specific names and avoid writing reserved bits unless hardware documentation explicitly requires it.
- Repeated register families are easy to edit mechanically but dangerous to edit by hand. A one-bit shift error in any `PA_SC_VPORT_*`, `SPI_PS_INPUT_CNTL_n`, `SX_MRTn_BLEND_OPT`, or `CB_BLENDn_CONTROL` entry can affect only one viewport/input/MRT and be hard to diagnose.
- Address high/low split fields for VRS and scratch state must match address alignment and aperture rules outside this header.
- `PA_SC_RASTER_CONFIG` fields are topology-sensitive. Copying values between harvested or differently configured ASICs can misroute raster work.
- `SPI_PS_INPUT_CNTL_n` field availability changes after slot 19 in this chunk; code generators or validators should not assume all 32 slots have identical field sets.
- Because `REG_SET_FIELD` masks the shifted input, out-of-range field values may be truncated rather than rejected at compile time.

## Test Signals

Useful validation signals for this chunk are mostly build-time, register-programming, and GPU-render correctness checks:

- The AMDGPU driver should compile with GC 12.0.0 include users; missing or renamed macros surface as C preprocessor/build failures.
- Static checks can verify each mask is consistent with its shift and field width, repeated families have regular strides, and no masks overlap unexpectedly within one register.
- Register readback tests can program representative fields with `REG_SET_FIELD` and confirm `REG_GET_FIELD` returns the original value for single-bit, multi-bit, and high-bit fields such as blend enable/ROP disable.
- Graphics conformance or piglit/Vulkan/GL tests should cover depth/stencil compare/write behavior, alpha-to-coverage, multisampling/EQAA, viewport/scissor clipping, user clip planes, VRS rate images/feedback, pixel shader interpolation, color export formats, blend equations, MRT enablement, and shader scratch use.
- GPU reset, suspend/resume, and context-switch tests should ensure clear-state and context restore paths reload the volatile registers described by this chunk.
