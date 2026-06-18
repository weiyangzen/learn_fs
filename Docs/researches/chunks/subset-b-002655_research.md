# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_sh_mask.h lines 14605-17184

## Scope

This chunk covers a generated AMD GC 9.2.1 shader/register mask header range. It starts inside the mask half of `TCP_GATCL1_CNTL`, then covers complete TCP UTCL1/perf-counter, GDS, RAS, depth-buffer, rasterizer, viewport, color-buffer, command-processor context, and pixel-shader-input groups through line 17184. The range ends inside `SPI_PS_INPUT_CNTL_18`; the remaining masks for that register continue in the next source lines and must be reconciled by the later merge lane.

The chunk contains 2,139 `#define` macros and 435 comment anchors. The public surface is entirely preprocessor constants, following the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` pattern. There are no C functions, structs, enums, or executable statements in this range.

## Purpose

`gc_9_2_1_sh_mask.h` provides compile-time bit positions and masks for GC 9.2.1 graphics-core registers used by the AMDGPU driver and related generated register programming tables. This slice describes several important hardware state domains:

- Texture/cache and VM controls for TCP/GATCL1/UTCL1, including invalidate, force-miss, fault/retry/PRT status, cache size/FIFO throttling, clock gating, GPUVM response behavior, and texture performance-counter filtering.
- Global Data Share (GDS), Global Wave Sync (GWS), and Ordered Append (OA) resource partitioning across VMIDs, plus reset, restore, and context-switch counters.
- RAS signature capture masks for multiple graphics blocks.
- Depth buffer (DB), stencil, HTILE, scissor, viewport, raster configuration, color write-mask, DCC, blend constants, coherent destination, and primitive reset state for the graphics pipeline.
- Pixel shader input-control registers `SPI_PS_INPUT_CNTL_0` through the start of `SPI_PS_INPUT_CNTL_18`, which define attribute offset, defaulting, interpolation, point-sprite, fp16 interpolation, duplicate, and attribute-valid fields.

The header does not decide policy. It encodes the hardware contract that other code uses when composing 32-bit register values from higher-level driver state, firmware tables, or command streams.

## Important API Surface

- `TCP_GATCL1_CNTL` trailing masks include invalidation, force miss, in-order behavior, FIFO-depth reduction, and cache-size reduction bits. Because this chunk starts mid-register, the matching shifts and earlier masks are outside this slice.
- `TCP_GATCL1_DSM_CNTL`, `TCP_CNTL2`, `TCP_UTCL1_CNTL1`, `TCP_UTCL1_CNTL2`, and `TCP_UTCL1_STATUS` describe texture cache/debug controls, clock-disable fields, GPUVM page-size/default permission behavior, invalidation VMID selection/toggle, snooping, forced GPUVM invalidation acknowledgements, and fault/retry/PRT status bits.
- `TCP_PERFCOUNTER_FILTER` and `TCP_PERFCOUNTER_FILTER_EN` define filter criteria and enable bits for texture/perf monitoring: buffer, flat, dimension, data format, numeric format, software mode, sample count, opcode type, GLC/SLC, compression, and address mode.
- The `gc_gdspdec` block defines per-VMID GDS base and size registers for VMIDs 0-15, GWS base/size partitions for VMIDs 0-15, OA masks for VMIDs 0-15, 64 individual GWS resource reset bits split across `GDS_GWS_RESET0` and `GDS_GWS_RESET1`, and targeted reset controls in `GDS_GWS_RESOURCE_RESET`, `GDS_OA_RESET_MASK`, and `GDS_OA_RESET`.
- `GDS_ENHANCE` and `GDS_OA_CGPG_RESTORE` expose control bits for GDS enhancement, clock/power-gating restore, queue identity, ME/pipe identity, and VMID restore state.
- `GDS_CS_CTXSW_STATUS`, `GDS_GFX_CTXSW_STATUS`, and the repeated `GDS_*_CTXSW_CNT0..3` groups expose context-switch read/write status and up/down pointer counters for compute, graphics, VS, PS0-PS7, and GS domains.
- The `gc_rasdec` block contains signature control/mask registers and signature result fields for SX, DB, PA, VGT, SQ, SC0-7, IA, SPI, TA, TD, CB, and BCI units.
- The `gc_gfxdec0` block starts with DB state: `DB_RENDER_CONTROL`, `DB_COUNT_CONTROL`, `DB_DEPTH_VIEW`, `DB_RENDER_OVERRIDE`, `DB_RENDER_OVERRIDE2`, HTILE base/high, depth size/bounds, stencil/depth clear values, `DB_Z_INFO`, `DB_STENCIL_INFO`, read/write base-high pairs, `DB_DFSM_CONTROL`, and EPITCH helpers in `DB_Z_INFO2` and `DB_STENCIL_INFO2`.
- Scissor and viewport registers include screen, window, generic, clip-rect, and 16 viewport scissor pairs; each top-left register can include a `WINDOW_OFFSET_DISABLE` bit while coordinates are split across low/high halfwords.
- Viewport depth and clip transform state includes `PA_SC_VPORT_ZMIN_0..15`, `PA_SC_VPORT_ZMAX_0..15`, `PA_CL_VPORT_X/Y/Z{SCALE,OFFSET}` for viewports 0-15, `PA_CL_UCP_0..5_{X,Y,Z,W}`, and `PA_CL_PROG_NEAR_CLIP_Z`.
- Raster and routing controls include `PA_SC_RASTER_CONFIG`, `PA_SC_RASTER_CONFIG_1`, `PA_SC_SCREEN_EXTENT_CONTROL`, `PA_SC_TILE_STEERING_OVERRIDE`, grid registers, `PA_SC_EDGERULE`, and `PA_SU_HARDWARE_SCREEN_OFFSET`.
- Command processor context fields include `CP_PERFMON_CNTX_CNTL`, `CP_PIPEID`, `CP_RINGID`, and `CP_VMID`.
- Color/depth integration fields include `CB_TARGET_MASK`, `CB_SHADER_MASK`, `CB_BLEND_{RED,GREEN,BLUE,ALPHA}`, `CB_DCC_CONTROL`, `DB_STENCIL_CONTROL`, `DB_STENCILREFMASK`, and `DB_STENCILREFMASK_BF`.
- `SPI_PS_INPUT_CNTL_0` through the partial `SPI_PS_INPUT_CNTL_18` expose repeated per-attribute shader input routing fields: `OFFSET`, `DEFAULT_VAL`, `FLAT_SHADE`, `CYL_WRAP`, `PT_SPRITE_TEX`, `DUP`, `FP16_INTERP_MODE`, `USE_DEFAULT_ATTR1`, `DEFAULT_VAL_ATTR1`, `PT_SPRITE_TEX_ATTR1`, and attribute-valid bits. The chunk stops after `SPI_PS_INPUT_CNTL_18__USE_DEFAULT_ATTR1_MASK`.

## Control Flow

There is no direct control flow in this header. Runtime flow is in consumers that include this generated mask file:

1. Pick a register address from the companion GC 9.2.1 address header.
2. Derive a 32-bit value from higher-level driver state.
3. Shift each field using `REGISTER__FIELD__SHIFT`.
4. Mask or replace fields using `REGISTER__FIELD_MASK`.
5. Emit the resulting register value through MMIO writes, PM4 packets, context/clear-state restore, golden-register programming, performance-counter setup, or debug decode paths.

The repeated families strongly suggest table-driven or looped consumers: VMID-indexed GDS/GWS/OA allocation, viewport-indexed scissor and clip transform programming, PS-stage repeated context counters, and pixel-shader input control for up to at least 19 attributes in this chunk.

## State and Persistence

The macros themselves are stateless and are resolved at compile time. The underlying registers they describe are persistent GPU state:

- TCP and UTCL1 fields persist until explicitly reprogrammed or reset. Incorrect invalidation, fault-response, cache-reduction, or snoop fields can affect texture cache behavior, GPUVM fault handling, and performance-counter visibility across subsequent work.
- GDS/GWS/OA allocation registers persist per VMID and resource slot. Context-switch status/counter registers represent live engine state and may be used during save/restore or debug flows.
- RAS signature registers are persistent diagnostic state for error detection, logging, or signature comparison. Consumers must preserve expected mask/control behavior when enabling or reading signatures.
- DB and CB registers persist as graphics context state. Depth/stencil metadata bases, HTILE bases, depth/stencil read/write bases, coherent destination bases, and DCC controls describe GPU memory surfaces and metadata.
- PA scissor, viewport, clip, edge, grid, and raster configuration state persists across draws until the command stream changes it. Bad values can clip all primitives, corrupt viewport transforms, or route screen tiles to the wrong backend.
- `SPI_PS_INPUT_CNTL_*` values are part of the shader ABI between compiler-selected PS inputs and hardware interpolation/routing. They must match the compiled shader's expected attribute layout.

Because this file provides constants only, all validation of field ranges, alignment, register sequencing, and hardware generation compatibility must happen outside the header.

## Dependencies and Integration Points

- Depends on the generated AMD GC 9.2.1 register specification. The masks must remain synchronized with companion address and offset headers in `drivers/gpu/drm/amd/include/asic_reg/gc/`, especially the matching `gc_9_2_1_d.h` style address definitions.
- Integrated by AMDGPU SOC15/GC register programming code, command submission paths, golden-register tables, clear-state/context-state restore paths, perf-counter setup, RAS diagnostics, and debug register decoders.
- Ties directly to GPUVM and memory-management code where base/high fields such as `DB_HTILE_DATA_BASE(_HI)`, `DB_Z_READ_BASE(_HI)`, `DB_STENCIL_READ_BASE(_HI)`, `DB_Z_WRITE_BASE(_HI)`, `DB_STENCIL_WRITE_BASE(_HI)`, `TA_BC_BASE_ADDR(_HI)`, and `COHER_DEST_BASE*` are populated from GPU addresses.
- Bridges graphics API state to hardware: viewport arrays, scissors, clip planes, depth/stencil clears, depth bounds, stencil operations, color write masks, blend constants, primitive restart index, and pixel shader input interpolation all eventually depend on these bit definitions.
- The `CP_*` context identifiers integrate with command processor queue/ring/VMID attribution and performance monitoring.
- The GDS/GWS/OA sections integrate with compute and graphics queue resource management, VMID partitioning, context switching, and reset/restore sequencing.

## Risks

- Bitfield drift is the main risk. If any mask or shift differs from the GC 9.2.1 hardware specification or the companion address header, consumers will silently program wrong bits.
- The chunk has boundary-partial registers. `TCP_GATCL1_CNTL` is only represented by trailing masks here, and `SPI_PS_INPUT_CNTL_18` is missing its final masks in this range. Merge tooling should avoid treating either as fully documented by this chunk alone.
- Repeated indexed families are copy/paste sensitive. Off-by-one use in `GDS_VMIDn_*`, `GDS_GWS_VMIDn`, `GDS_OA_VMIDn`, `PA_SC_VPORT_SCISSOR_n`, `PA_SC_VPORT_ZMIN/ZMAX_n`, `PA_CL_VPORT_*_n`, or `SPI_PS_INPUT_CNTL_n` can alter the wrong VMID, viewport, or shader input.
- Address-bearing DB/TA/coherency fields have high blast radius. Wrong base/high fields or alignment assumptions can cause GPUVM faults, metadata corruption, or writes to the wrong depth/stencil/coherency surface.
- TCP/UTCL1 invalidation and fault-response fields are low-level cache/VM controls. Incorrect programming can hide faults, force excessive misses, create stale translations, or distort performance-counter results.
- GDS/GWS/OA reset and allocation masks can disrupt synchronization or append resources for unrelated queues if VMID/resource identity is wrong.
- DB override and compression bits such as force dirty/valid, preserve compression, decompress-on-flush, clear-disallowed, allow expclear, HTILE, DCC, and stencil/depth compression flags are visually and correctness sensitive.
- Raster configuration and tile steering fields are ASIC-topology sensitive. Incorrect values can send work to invalid shader engines/render backends or cause subtle load-balancing and rendering failures.
- Pixel shader input controls must match compiler/driver ABI expectations. Incorrect `OFFSET`, `DEFAULT_VAL`, `FLAT_SHADE`, `CYL_WRAP`, `PT_SPRITE_TEX`, fp16 interpolation, or validity bits can produce wrong interpolants without an obvious kernel-side failure.

## Test Signals

- Build coverage: compiling AMDGPU with this header included catches malformed macros, duplicate definitions, missing guards, and preprocessing errors.
- Generated-header consistency: compare this range against the GC 9.2.1 source register database and the matching address header to confirm all `__SHIFT` and `_MASK` pairs, field widths, and boundary registers.
- Register decode validation: decode known-good command streams or register dumps using these masks for `TCP_UTCL1_*`, `GDS_*`, `DB_*`, `PA_SC_*`, `PA_CL_*`, `CB_*`, and `SPI_PS_INPUT_CNTL_*` and compare against expected state.
- GPUVM/cache smoke tests: run texture-heavy workloads, page-fault/PRT scenarios, and perf-counter collection while checking for VM faults, stale data, unexpected retries, or counter filter mismatches.
- GDS/GWS/OA stress: run compute and graphics workloads that use GDS, ordered append, wave synchronization, queue context switching, reset paths, and multi-VMID scheduling.
- RAS diagnostics: exercise RAS signature enable/read paths and verify stable signatures or expected error reporting on supported GC 9.2.1 hardware.
- Graphics conformance: Vulkan/OpenGL CTS coverage for depth/stencil clears and tests, depth bounds, HTILE/compression paths, stencil front/back operations, scissor and viewport arrays, clip planes, primitive restart, color write masks, blend constants, DCC behavior, point sprites, flat shading, and shader interpolation should exercise the main register surfaces in this chunk.
- Runtime monitoring: run display plus 3D workloads on GC 9.2.1 hardware and watch for GPU hangs, RAS events, VM faults, rendering corruption, or golden-register mismatches.
