# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h lines 9800-12226

## Scope

This chunk is a generated AMD GC 9.4.2 shader/header mask slice. It contains 2,168 `#define` constants under 259 register-name comment groups. The range starts immediately after the `SPI_BARYC_CNTL` comment from the previous chunk, so it only contains the `FRONT_FACE_ALL_BITS_MASK` field for that register. It ends inside `CB_COLOR5_INFO`, after the `SIMPLE_FLOAT_MASK` field; the rest of `CB_COLOR5_INFO` and later color-target registers are in the next chunk.

There are no functions, structs, enums, variables, locks, allocation paths, or executable statements here. The file is compile-time hardware metadata: each `__SHIFT` and `_MASK` macro describes a bitfield in a GC 9.4.2 MMIO register.

The covered register families are:

- SPI export and shader-interface fields, including front-face barycentric handling, temporary ring sizing, position/Z/color export formats.
- SX pixel export, downconversion, blend epsilon, blend optimization disable, and per-MRT blend optimization fields.
- CB blend control for MRT0 through MRT7 and CB color buffer state for targets 0 through part of 5.
- DB depth/stencil, EQAA, shader depth interaction, HTILE, alpha-to-mask, and stencil-result compare/preload controls.
- PA clipper, setup, scan converter, rasterization, antialiasing sample locations/masks, binner, conservative rasterization, stereo, line/point, viewport transform, NaN/Inf, primitive filtering, and NGG-facing controls.
- VGT draw initiation, DMA/index draw state, tessellation, geometry shader, streamout, primitive ID, shader-stage enable, ring sizing, and vertex reuse/deallocation controls.
- Small copy-state and command-style payload registers such as `CS_COPY_STATE`, `GFX_COPY_STATE`, `VGT_IMMED_DATA`, and event initiators.

## Purpose

The purpose of this header segment is to expose the bit layout of GC 9.4.2 graphics pipeline registers to AMDGPU driver code. The paired offset header provides register addresses; this mask header provides field offsets and masks used to compose and decode 32-bit register values.

The generated API pattern is consistent:

- `<REGISTER>__<FIELD>__SHIFT` gives the starting bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.

Consumers normally reach these macros through AMDGPU register helpers such as `REG_SET_FIELD()`, `REG_GET_FIELD()`, `WREG32_SOC15()`, `RREG32_SOC15()`, packet-building code, or local read-modify-write helpers. Correctness depends on these symbolic names matching the ASIC register database for GC 9.4.2.

## Important Macro Families

### SPI And SX Export State

The SPI section defines fields for shader output formats and scratch/ring sizing. `SPI_TMPRING_SIZE` packs wave count and wave size. `SPI_SHADER_POS_FORMAT`, `SPI_SHADER_Z_FORMAT`, and `SPI_SHADER_COL_FORMAT` encode position, depth, and up to eight color export formats. The leading `SPI_BARYC_CNTL__FRONT_FACE_ALL_BITS_MASK` is a boundary fragment from the prior register group.

The SX section controls pixel shader export conversion and blend optimization. `SX_PS_DOWNCONVERT` and `SX_BLEND_OPT_EPSILON` have repeated 4-bit fields for MRT0 through MRT7. `SX_BLEND_OPT_CONTROL` disables color/alpha optimizations per MRT and has a global `PIXEN_ZERO_OPT_DISABLE` bit. `SX_MRT0_BLEND_OPT` through `SX_MRT7_BLEND_OPT` each define color and alpha source/destination optimization selectors and combine functions.

### CB Blend And Color Target State

`CB_BLEND0_CONTROL` through `CB_BLEND7_CONTROL` define the per-render-target blend contract: color source blend, color combine function, color destination blend, alpha source blend, alpha combine function, alpha destination blend, separate alpha enable, blend enable, and ROP3 disable. These macros are central to translating API blend state into hardware register values.

The later CB color target section covers complete target descriptors for MRT0 through MRT4 and the beginning of MRT5. Repeated fields include:

- `CB_COLORn_BASE` and `CB_COLORn_BASE_EXT`, which hold 256-byte-aligned base address pieces.
- `CB_COLORn_ATTRIB2`, with mip0 height, mip0 width, and max mip.
- `CB_COLORn_VIEW`, with slice start, slice max, and mip level.
- `CB_COLORn_INFO`, with endian, format, number type, component swap, fast clear, compression, blend clamp/bypass, simple float, round mode, blend optimization hints, FMASK compression flags, DCC enable, and CMASK address type.
- `CB_COLORn_ATTRIB`, with mip0 depth, metadata linear flag, sample/fragment counts, force alpha, color/FMASK swizzle modes, resource type, RB alignment, and pipe alignment.
- `CB_COLORn_DCC_CONTROL`, with overwrite-combiner, compressed/uncompressed block sizing, color transform, independent 64B blocks, lossy precision, and constant encode controls.
- `CB_COLORn_CMASK`, `FMASK`, clear words, and DCC base/base-ext registers.

Because the chunk stops inside `CB_COLOR5_INFO`, later merge work must combine the next chunk before making complete claims about target 5 and targets 6-7.

### DB Depth, Stencil, And Sample State

`DB_DEPTH_CONTROL` exposes stencil enable, Z enable/write, depth-bounds enable, Z compare function, backface enable, front/back stencil functions, and color-write behavior on depth pass/fail. `DB_EQAA` describes sample counts, anchor samples, alpha-to-mask sample count, high-quality intersections, interpolation choices, over-rasterization amount, and post-Z over-rasterization enable. `DB_SHADER_CONTROL` connects pixel shader behavior to depth/stencil processing through Z export, stencil exports, Z ordering, kill/coverage/mask export, hierarchical execution, alpha-to-mask disable, depth-before-shader, conservative Z export, primitive ordered pixel shader, and overlap controls.

`DB_HTILE_SURFACE`, `DB_SRESULTS_COMPARE_STATE0/1`, `DB_PRELOAD_CONTROL`, and `DB_ALPHA_TO_MASK` describe depth metadata, stencil-result compare inputs, preload window coordinates, and alpha-to-mask offsets. These are passive bitfield definitions, but the hardware behavior is stateful once programmed.

### PA Clipper, Setup, Scan Converter, And Rasterizer State

The PA groups are broad pipeline state for clip, setup, scan conversion, rasterization, multisampling, and binning. `PA_CL_CLIP_CNTL`, `PA_CL_VTE_CNTL`, `PA_CL_VS_OUT_CNTL`, `PA_CL_NANINF_CNTL`, and the guard-band adjustment registers define user clip/cull planes, viewport transform behavior, vertex shader output sideband usage, NaN/Inf handling, and guard-band clip/discard parameters.

Setup/raster state includes `PA_SU_SC_MODE_CNTL`, line stipple controls, primitive/small-primitive filtering, object/primitive ID controls, NGG-related clipper state, over-rasterization behavior, stereo routing, point and line sizes, polygon offset scale/offset/clamp, and vertex quantization/rounding. `PA_SC_MODE_CNTL_0/1`, `PA_SC_LINE_CNTL`, `PA_SC_SHADER_CONTROL`, `PA_SC_BINNER_CNTL_0/1`, `PA_SC_CONSERVATIVE_RASTERIZATION_CNTL`, and `PA_SC_NGG_MODE_CNTL` control scan conversion, scissor/MSAA behavior, tile/supertile walk order, multi-GPU or multi-SE discard behavior, EOV forcing, out-of-order primitive handling, shader quad realignment, binning dimensions/state counts, conservative rasterization uncertainty rules, and NGG deallocation limits.

The antialiasing section is highly regular. `PA_SC_AA_CONFIG` defines sample exposure and coverage selection. Sixteen `PA_SC_AA_SAMPLE_LOCS_PIXEL_*_*` registers pack 4-bit X/Y locations for samples 0 through 15 across four pixel positions. `PA_SC_AA_MASK_X0Y0_X1Y0` and `PA_SC_AA_MASK_X0Y1_X1Y1` pack coverage masks for the same pixel quadrants. `PA_SC_CENTROID_PRIORITY_0/1` define centroid priority distances 0 through 15.

### VGT Draw, Tessellation, Geometry, And Streamout State

The VGT groups define draw setup and shader-stage plumbing. `VGT_DMA_BASE`, `VGT_DMA_BASE_HI`, `VGT_DMA_SIZE`, `VGT_DMA_MAX_SIZE`, `VGT_DMA_INDEX_TYPE`, `VGT_DMA_NUM_INSTANCES`, and `VGT_DMA_EVENT_INITIATOR` describe indexed draw DMA base/size/type, instance count, and event signaling. `VGT_DRAW_INITIATOR`, `VGT_IMMED_DATA`, `VGT_EVENT_ADDRESS_REG`, `VGT_EVENT_INITIATOR`, `VGT_DRAW_PAYLOAD_CNTL`, and `VGT_DISPATCH_DRAW_INDEX` describe draw source/mode, immediate payload, event address/type, payload enablement, and dispatch draw matching.

Tessellation and geometry-stage fields include `VGT_OUTPUT_PATH_CNTL`, `VGT_HOS_CNTL`, min/max tessellation level, reuse depth, group primitive/vector controls, GS mode, GS on-chip control, per-ES/GS/VS ratios, GSVS ring offsets/item sizes, GS output primitive types, LS/HS config, GS vertex item sizes, tessellation distribution, shader-stage enablement, and tessellator-factor parameters. These fields are integration points between compiler-selected pipeline state and command submission.

Streamout and primitive state includes `VGT_STRMOUT_BUFFER_SIZE_*`, vertex stride, buffer offset, opaque draw offset/filled-size/stride, `VGT_STRMOUT_CONFIG`, `VGT_STRMOUT_BUFFER_CONFIG`, primitive ID enable/reset, GS instance count, primitive reuse disable, vertex count enable, vertex reuse depth, and output deallocation distance.

## Control Flow

There is no direct control flow in this header. Runtime flow is supplied by driver code that includes this generated file:

1. Code selects the GC 9.4.2 register address from the matching offset header.
2. It builds a register value by shifting field values by `__SHIFT` and constraining them with `_MASK`, usually through helper macros.
3. It writes the value through MMIO or command packets, or reads a register and decodes fields using the matching mask/shift pair.
4. Sequencing, synchronization, cache flushing, command submission, polling, and error handling live outside this header.

Typical higher-level flows include graphics pipeline state emission for draws, render-target setup, blend/depth/stencil programming, MSAA sample programming, tessellation/geometry/NGG setup, streamout setup, and indexed draw DMA/event setup.

## State And Persistence Behavior

The macros themselves hold no software state. They describe hardware register state that persists until overwritten, reset, power-gated/reinitialized, or restored by firmware/driver resume paths.

Most fields in this chunk are context or pipeline state. Once programmed, blend, color target, depth/stencil, rasterizer, sample-location, tessellation, streamout, and draw-control values affect subsequent graphics work submitted to the GPU. Address-bearing CB fields (`BASE`, `BASE_EXT`, `CMASK`, `FMASK`, `DCC_BASE`, and their extension registers) refer to GPU memory in 256-byte units and therefore must match the driver's memory manager, tiling, metadata, compression, and synchronization state.

Some registers are command-like rather than durable configuration, such as draw initiators, event initiators, dispatch draw index matching, copy-state source IDs, and preload/clear controls. These require surrounding driver sequencing to avoid stale state, partial updates, or writes in the wrong pipeline phase.

## Dependencies And Integration Points

This chunk must remain synchronized with the generated GC 9.4.2 register database and the matching address definitions, especially `gc_9_4_2_offset.h`. It is consumed by AMDGPU graphics, display interop, command submission, shader compiler state emission, KFD/compute-adjacent setup where graphics state is shared, render-target compression/metadata code, reset/suspend/resume paths, and debug or register-dump tooling.

The source path is under a `ceph-client` mirror, but this file is AMD GPU driver hardware metadata. It has no Ceph protocol behavior, filesystem data path, distributed consistency, network I/O, or persistent storage semantics beyond the GPU-memory addresses programmed into CB metadata registers.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask compiles cleanly but can corrupt GPU MMIO state.
- The chunk has incomplete boundary register groups: `SPI_BARYC_CNTL` is only represented by one trailing mask, and `CB_COLOR5_INFO` is only partially present.
- Repeated MRT and color-target groups are easy to copy or index incorrectly. Target-specific names must match the register address selected by the caller.
- Address fields are split across low and extension registers and use 256-byte units. Incorrect alignment, truncation, or extension handling can send CB/CMASK/FMASK/DCC traffic to the wrong GPU memory.
- Many fields interact across blocks: color export formats must match CB formats and blend controls; MSAA/EQAA sample counts must match AA sample locations, masks, DB state, and color/depth target attributes; tessellation/GS/NGG settings must match shader-stage enablement and compiler output.
- Some masks cover reserved or legacy-named fields such as `RESERVED_*` in `VGT_GS_MODE` and `SPRITE_EN_R6XX` in `VGT_DRAW_INITIATOR`. Driver code should avoid assuming semantic safety from the names alone.
- Command-like fields and enable/clear/event fields need hardware-specific ordering outside this header. Treating them as ordinary cached state can cause missed events, wrong draws, or inconsistent profiling/debug observations.

## Test Signals

Useful validation is mostly integration-level rather than unit-level:

- Kernel build coverage for all GC 9.4.2 AMDGPU users, catching renamed or missing macros.
- Register helper tests or static checks that `REG_SET_FIELD()` and `REG_GET_FIELD()` round-trip important fields without overlapping unrelated bits.
- GPU graphics CTS/dEQP/Piglit coverage for blending, depth/stencil, alpha-to-mask, MSAA/EQAA sample locations, conservative rasterization, tessellation, geometry shader, NGG, streamout, primitive ID, and indexed draw paths.
- Render-target compression and metadata tests that exercise DCC/CMASK/FMASK base, clear-word, format, sample, fragment, alignment, and swizzle fields.
- Suspend/resume, reset, and context-switch testing to ensure programmed pipeline state is restored or invalidated correctly.
- Register dumps on GC 9.4.2 hardware compared against known-good programming sequences for color/depth/rasterizer/VGT state.
