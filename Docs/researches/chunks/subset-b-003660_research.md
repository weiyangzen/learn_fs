# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a6xx.xml lines 1-4706

## Scope

This chunk covers the first 4,706 lines of the Freedreno XML register database for the `A6XX` Adreno register domain. The XML file continues past this range, so this document is intentionally a chunk-level report, not the final per-file report.

The covered range starts with imports and domain metadata, then defines a large set of A6XX/A7XX/A8XX register descriptions for CP, RBBM, DBGC, UCHE, VBIF/GBIF, VSC, GRAS, RB, VPC, PC, VFD, SP, TPL1, and HLSQ-related blocks. It is declarative hardware ABI data: there are no C functions, call sites, allocations, locks, or executable branches in this source range. Runtime behavior is created later by register-code generators and by DRM/MSM/Freedreno driver code that writes or reads the generated register constants.

## Purpose

`a6xx.xml` is a source-of-truth register schema for Qualcomm Adreno 6xx-family GPUs and newer variant ranges included under the same domain. It describes:

- Register names, offsets, widths, and address alignment requirements.
- Packed bitfields and enumerated values used to compose MMIO writes and decode reads.
- Variant-specific offsets and layouts for `A6XX`, `A7XX`, and `A8XX-`.
- Usage metadata indicating where driver command streams are expected to program a register.
- Reusable bitsets for repeated layouts such as CP protection state, bin-size state, viewport/scissor coordinates, shader-stage resource configuration, and buffer pitch descriptors.

The comment near the top is important for integration: `usage="cmd"` marks registers used outside renderpasses and blits, roughly corresponding to Freedreno IB1 command-buffer state; `usage="rp_blit"` marks registers used inside renderpasses or blits, roughly corresponding to IB2 state; `usage="init"` marks initialization-time state. That annotation is part of how generated register helpers and driver state emission can reason about command-buffer placement.

## Important Schema Elements

The file imports shared schema and enum dependencies:

- `freedreno_copyright.xml`.
- `adreno/adreno_common.xml`.
- `adreno/adreno_pm4.xml`.
- `adreno/a6xx_enums.xml`, `a7xx_enums.xml`, and `a8xx_enums.xml`.
- `adreno/a6xx_perfcntrs.xml` and `a7xx_perfcntrs.xml`.
- `adreno/a6xx_descriptors.xml` and `a8xx_descriptors.xml`.

The main XML API surface in this chunk is made from `domain`, `bitset`, `enum`, `reg32`, `reg64`, and `array` nodes. These are consumed by the Freedreno register generation pipeline to produce constants, typed packet helpers, bitfield pack/unpack helpers, and register names used by kernel and userspace command emission code. Important referenced field types include `a5xx_address_mode`, `a6xx_format`, `a6xx_tile_mode`, `a3xx_msaa_samples`, `a3xx_regid`, `adreno_compare_func`, `adreno_rb_blend_factor`, `adreno_stencil_op`, `vgt_event_type`, `waddress`, and `address`.

## Major Register Areas

### CP, Interrupts, Protection, and Debug

The first register block defines command processor state. It includes ringbuffer base, read/write pointers, SQE/AQE instruction bases, CP-to-GMU status, hardware-fault status, interrupt status/mask registers, APRIV controls, ROQ thresholds, protect ranges, context-switch restore addresses, crash-dump script registers, debug address/data windows, IB/SDS/MRB/VSD queue base and size state, aperture controls, BV/LPAC/AQE debug state, and CP performance counter selectors.

Key reusable types include `A6XX_RBBM_INT_0_MASK`, `A6XX_CP_INT`, `A8XX_CP_GLOBAL_INT_MASK`, `A8XX_CP_INTERRUPT_STATUS_MASK_PIPE`, `A8XX_CP_HW_FAULT_STATUS_MASK_PIPE`, `a6xx_cp_protect_status`, `a6xx_cp_apriv_cntl`, `a6xx_cp_protect_cntl`, `a8xx_cp_protect_cntl`, `a6xx_cp_context_switch_cntl`, and `a6xx_roq_status`.

This block is central to GPU submission, fault diagnosis, register access protection, preemption/context-switch restore, crash dumping, and per-pipe status on newer GPUs. A7XX/A8XX variants add BV, LPAC, pipe, global, and slice-specific register windows that must not be confused with the older single-pipe A6XX offsets.

### RBBM, Performance Counters, Security, and Bus Interfaces

The RBBM section defines global status and interrupt registers, busy/status bitfields, clock and reset controls, performance counter banks, pipeline-stat counters, security-video TSB registers, GBIF/VBIF halt and QoS controls, and debug-bus configuration. The chunk also contains large perf-counter selector arrays whose offsets and lengths vary by GPU generation.

The RBBM status fields are the high-level health signals for GPU idle/busy detection and fault triage. The counter arrays are integration points for perf tooling and debugfs/perfetto-style performance capture, while halt/QoS/GBIF/VBIF registers are involved in reset, bus quiesce, and memory-interface behavior.

### DBGC, UCHE, VBIF, and GBIF

DBGC register definitions describe debug-bus select/control, trace buffers, event interfaces, GBIF debug buffers, and A8XX scoped performance-counter capture paths for BR, BV, LPAC, and cluster-local groups.

UCHE definitions cover cache mode, write-through base, trap base, GMEM ranges, cache ways, prefetch/client controls, performance selectors, and A8XX CCHE-specific state. VBIF definitions are A6XX-only, while GBIF definitions cover the later bus fabric, including halt, reinit, performance counter, and power counter registers.

These registers are mostly persistent hardware state and diagnostic state. They are consumed by initialization, reset, memory-fault handling, performance capture, and debug-dump paths.

### VSC and Binning

The VSC block defines bin sizes, VSC pipe configuration, visibility stream base/stride/length registers, visibility bitmaps, and per-pipe data sizes. The comments document the visibility stream format and explain that A6XX hardware adds `pipe_num * VSC_*_STRM_PITCH` from the first stream base.

This block integrates directly with tiled rendering and binning. Misprogramming bin dimensions, pipe mapping, or visibility stream allocation can break GMEM/tiled renderpasses or cause skipped/duplicated draw work.

### GRAS Rasterization, Scissor, LRZ, and 2D Blit

The GRAS section defines clip control, clip/cull distance masks, interpolation controls, guardband adjustment, viewport transforms, z clamps, cull/front-face/multiview state, point size limits, depth/stencil/raster controls, binning controls, MSAA sample positions, scissor rectangles, VRS/foveation/quality-buffer state, LRZ control and buffer state, and A2D blit controls.

Important local types include `a6xx_gras_cl_cntl`, `a6xx_gras_su_cntl`, `a6xx_gras_sc_cntl`, `a6xx_bin_cntl`, `a8xx_bin_cntl`, `a6xx_gras_vrs_config`, `a6xx_gras_lrz_cntl`, `a6xx_a2d_blt_cntl`, and `a6xx_reg_xy`.

The LRZ comments are especially important. `GRAS_LRZ_VIEW_INFO` records depth view identity so LRZ can be reused only when base layer, layer count, and mip level match. The fast-clear buffer is described as one bit per LRZ block, with size derived from depth dimensions and MSAA sample count. This makes LRZ a cross-renderpass state hazard: driver resource tracking must agree with the hardware view identity and clear/modified state.

### RB Render Backend

The RB block defines render mode, MSAA, interpolation, PS input/output controls, sRGB and dither controls, MRT blend and buffer state, blend constants, depth and stencil state, sample counter state, LRZ enable state, viewport z clamps, resolve controls, CCU cache control, UBWC flag buffers, GMEM dimensions, A2D destination/flag state, performance selectors, and context-switch GMEM save/restore state.

The `RB_MRT` array is a dense repeated structure for eight render targets with control, blend control, buffer info, pitch, array pitch, system base, and GMEM base. Depth/stencil and resolve registers separately describe sysmem and GMEM bases, format/tile/flag metadata, pitches, clear colors, and operation type.

These registers are central to renderpass correctness. They encode the relationship between sysmem images, GMEM attachments, UBWC flag buffers, resolves, clears, depth/stencil tests, blending, color masks, and CCU cache reservation. Many fields are marked `rp_blit`, so command-stream emission must keep them synchronized with the currently active framebuffer, renderpass, and blit operation.

### VPC and PC Primitive/Varying State

The VPC and PC blocks describe clip/cull and system-value locations, raster stream selection, primitive restart and provoking vertex controls, geometry/tessellation parameters, stereo/multiview controls, varying interpolation and replacement modes, VPC local-memory transfer masks, streamout mapping ports, streamout buffers and query base, per-stage VPC/PC control, GMEM allocation for VPC/PC attribute and position buffers, draw/event initiators, visibility-stream state, tessellation base, DMA state, and performance counters.

The streamout mapping port is a special write-multiple register with auto-incrementing address semantics. The comments describe a 4-stream by 64-entry program where each entry maps VPC locations to streamout buffers and offsets. This is not a normal persistent scalar register and needs ordered programming.

The VPC/PC blocks are integration points for shader compiler output locations, transform feedback, multiview, tessellation, primitive assembly, binning visibility, and draw initiation.

### VFD Vertex Fetch

The VFD section defines fetch/decode counts, system-value destination registers, vertex/index/instance offsets, 32 vertex-buffer descriptors, 32 fetch instructions, destination controls, power control, debug/init registers, and VFD performance selectors.

Fetch instructions pack buffer index, byte offset, instancing, format, component swap, floating/integer interpretation, and step rate. Destination controls map fetched components into `a3xx_regid` shader registers with write masks. Consumers must keep these registers consistent with the shader's declared vertex inputs and the bound vertex buffers.

### SP Shader Processor, TPL1 Texture, and HLSQ Adjacent State

The SP section covers shader-stage control for VS, HS, DS, GS, PS, and CS. It defines thread mode/size, merged register behavior, register footprints, branch stack size, early-preamble mode, boolean condition masks, shader output maps, VPC destination maps, program counter offsets, shader base addresses, private-memory bases/sizes/stack offsets, resource counts, bindless descriptor bases, sampler and texture descriptor bases, UAV bases, constant configuration, PS outputs, initial texture load/prefetch, compute local/global size state, workgroup register IDs, and shader profiling/performance/debug registers.

Important reusable types include `a6xx_threadsize`, `a6xx_sp_xs_cntl_0`, `a6xx_sp_xs_config`, `a6xx_sp_xs_pvt_mem_param`, `a6xx_sp_xs_pvt_mem_size`, `a6xx_sp_xs_pvt_mem_stack_offset`, `a6xx_sp_blend_cntl`, `a6xx_bindless_descriptor_size`, `a6xx_xs_const_config`, and the SP fragment-program register ID bitsets.

The comments contain several behavioral contracts: early preamble mode restricts usable registers and instruction classes; `MERGEDREGS` on VS controls all geometry stages; private memory has per-wave and per-fiber layouts with different address formulas; some compute thread-size combinations can hang; and A7XX/A8XX work item ordering can tile or reorder dispatches. These notes are important because the XML is not just names and masks; it preserves reverse-engineered semantics that compiler and command emission code rely on.

TPL1 definitions cover texture border-color bases, MSAA/sample-position state, texture mode controls, 2D source texture/plane/flag buffers, UBWC hint behavior, noncoherent mode, bicubic weights, and TP performance selector arrays. The covered HLSQ-adjacent entries include load-state geometry command/source/data registers and several A6XX/A7XX SP register-program ID layouts used for fragment system values.

## Control Flow

There is no executable control flow in this XML chunk. The practical control flow is implied by consumers:

1. Register generators parse the XML imports, domain, enums, bitsets, registers, arrays, variants, and usage tags.
2. Generated headers/helpers expose register offsets and field pack/unpack macros or inline helpers.
3. Driver initialization programs `usage="init"` hardware state such as cache ways, debug ECO controls, noncoherent modes, perf masks, and address-mode controls.
4. Command-buffer emission programs `usage="cmd"` state before renderpass or compute work, including CP, VSC stream bases, LRZ view identity, CCU cache allocation, sample counters, shader descriptor bases, tessellation bases, streamout buffers, and compute shader base/private-memory/resource state.
5. Renderpass/blit emission programs `usage="rp_blit"` state around draws, clears, resolves, and blits, including GRAS, RB, VPC/PC, VFD, SP PS/VS/etc., TPL1, MRT, depth/stencil, and resolve registers.
6. Fault, performance, and debug code reads status/debug/perf registers and decodes bitfields to produce diagnostics.

The XML uses `variants` as declarative branching. A generator or consumer must select the correct offset/layout for the active GPU generation. Many register names are shared across A6XX, A7XX, and A8XX with different offsets or widened fields.

## State and Persistence Behavior

All state described here is hardware register state. The XML file itself persists no runtime data.

State classes include:

- CP scheduler, ringbuffer, instruction, protection, context-switch, fault, interrupt, crash-dump, and debug state.
- RBBM global status, clock/reset, performance-counter, security, and bus-control state.
- Debug trace, scoped performance, and GBIF/VBIF/UCHE cache or bus-fabric state.
- Renderpass state for binning, VSC visibility streams, GRAS clipping/rasterization/scissors/LRZ, RB render targets/depth/stencil/resolves, and CCU/GMEM cache allocation.
- Shader-stage state for executable base addresses, program sizes, resource counts, private memory, constants, UAVs, bindless descriptors, samplers, texture descriptors, outputs, and system-value register IDs.
- Vertex fetch, primitive assembly, tessellation, multiview, varying interpolation, transform feedback, and compute dispatch dimensions.

Persistence depends on GPU reset domains, preemption save/restore, command-buffer sequencing, and driver resource tracking. Registers such as context-switch restore addresses and GMEM save/restore state explicitly participate in persistence across preemption. LRZ and UBWC flag buffers couple register state to memory-backed metadata that can outlive a renderpass, so resource tracking and synchronization must keep those registers and backing buffers coherent.

## Dependencies and Integration Points

This chunk depends on the Freedreno XML schema and imported enum/descriptor files for shared type names, PM4/event definitions, descriptor layouts, address types, and performance counter definitions.

Primary integration points are:

- The Freedreno register generator that turns XML into C/C++ register definitions.
- DRM/MSM kernel code that initializes the GPU, handles faults, manages protected register ranges, reads status, controls ringbuffers, and restores context/preemption state.
- Mesa Freedreno/Turnip command-stream emission that programs IB1/IB2 state for GL/Vulkan draws, renderpasses, blits, compute dispatches, descriptor bases, and shader programs.
- Shader compiler and pipeline layout code that chooses `a3xx_regid` mappings, output locations, register footprints, private-memory sizes, bindless/resource counts, and system-value register IDs.
- Performance tooling and debug/coredump paths that consume RBBM/DBGC/SP/TPL1/RB/VPC perf selectors and status/debug windows.
- Memory management and resource-layout code that supplies aligned `address`/`waddress` values, UBWC flag buffers, GMEM offsets, LRZ buffers, private memory, streamout buffers, and descriptor tables.

## Risks

- Variant drift is the dominant risk. The same register name often has different offsets, lengths, or bit layouts across A6XX, A7XX, and A8XX. Selecting the wrong variant can program unrelated hardware.
- `usage` metadata affects command-buffer placement. Treating `rp_blit` state as stable command-buffer state, or emitting `cmd` state too late, can create hard-to-reproduce renderpass bugs.
- Many fields are reverse-engineered and marked with comments such as unknown, TODO, guessed, blob-observed, or generation-specific. These should not be treated as fully specified hardware contracts without validation.
- Address alignment fields matter. Shader bases, descriptor bases, LRZ/UBWC/resolve buffers, streamout buffers, and sample counters have explicit alignments; violating them can fault or corrupt rendering.
- LRZ state is cross-pass and view-dependent. Incorrect `GRAS_LRZ_VIEW_INFO`, fast-clear buffer sizing, direction tracking, or depth-format state can cause invalid early-z results.
- RB/GRAS duplicate or related fields must stay synchronized. Examples include depth buffer info, MSAA sample positions, sRGB, interpolation, VRS/foveation, binning, and render-mode state.
- Special write-only or write-multiple registers, such as `VPC_SO_MAPPING_PORT`, require ordered programming and cannot be treated like ordinary scalar state.
- Compute thread-size and workgroup-order fields include documented hang hazards. Command emission must respect comments requiring matching thread-size fields and avoiding invalid scalar/thread128 combinations.
- Perf/debug/status registers may have sticky, side-effect, or hardware-specific clear semantics not encoded by the XML. Consumers must rely on driver conventions and hardware docs where available.

## Test Signals

Useful validation for consumers of this chunk includes:

- Regeneration of headers from this XML without schema errors, missing imported types, duplicate-name conflicts, or variant-selection failures.
- Kernel and Mesa builds that include generated A6XX register definitions and compile all referenced enum/bitset types.
- Unit or generator tests that pack and unpack representative fields: CP interrupt masks, CP protect ranges, bin sizes, viewport/scissor coordinates, RB_MRT descriptors, depth/stencil state, blend state, VFD fetch instructions, SP private-memory sizes, bindless descriptor bases, and compute NDRANGE fields.
- Hardware smoke tests across A6XX, A7XX, and A8XX-class devices to catch offset/layout drift, especially where the same register name has generation-specific offsets.
- Render tests covering GMEM and sysmem paths, clears, resolves, UBWC flag buffers, MSAA sample positions, depth/stencil, blending, sRGB, alpha-to-coverage, foveation/VRS, and A2D blits.
- LRZ-specific tests for depth clear, LRZ reuse across renderpasses, layer/mip view changes, wrong-direction handling, fast-clear enable/disable, and sysmem versus GMEM rendering.
- Shader pipeline tests for VS/HS/DS/GS/PS/CS base addresses, output maps, varying interpolation/replacement, system values, private memory, bindless descriptors, UAVs, early preamble, merged registers, and compute workgroup dimensions.
- Transform feedback tests that validate `VPC_SO_MAPPING_WPTR`, repeated `VPC_SO_MAPPING_PORT` writes, stream selection, flush base, and query base behavior.
- Fault and debug tests that verify CP/RBBM interrupt/fault status decoding, protect violation reporting, crash-dump state, DBGC trace capture, and performance counter programming.
- Suspend/resume, GPU reset, and preemption tests that verify context-switch restore addresses, GMEM save/restore state, streamout save state, and reinitialization of `usage="init"` registers.
