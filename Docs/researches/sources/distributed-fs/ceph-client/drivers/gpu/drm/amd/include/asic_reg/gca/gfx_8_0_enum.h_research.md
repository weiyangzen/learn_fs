# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_0_enum.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002711`: lines 1-4749, `Docs/researches/chunks/subset-b-002711_research.md`
- `subset-b-002712`: lines 4750-6858, `Docs/researches/chunks/subset-b-002712_research.md`

## Chunk Research

### subset-b-002711: lines 1-4749

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_0_enum.h lines 1-4749

## Scope

This chunk is the first 4,749 lines of the generated-style AMD GFX 8.0 enum/value header. It starts with the AMD license block and include guard, then defines C `typedef enum` groups and raw `#define` constants for register-field values, performance-counter select values, shader instruction encodings, resource descriptor encodings, texture/vertex fetch formats, and texture-cache operation/performance selectors.

There are no functions, structs, global variables, includes, allocations, locks, loops, callbacks, or runtime branches in this range. The selected range ends inside `TCC_PERF_SEL` after `TCC_PERF_SEL_CLIENT119_REQ`; that enum continues in the next chunk and should be reconciled there for full-file research.

Although the source path sits under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for AMD GFX 8.0 graphics IP. It is not Ceph filesystem logic.

## Purpose

`gfx_8_0_enum.h` gives AMDGPU code symbolic names for numeric values programmed into or decoded from GFX 8.0 registers and command/shader encodings. Companion offset and shift/mask headers identify register addresses and bit positions; this file supplies the value domains that go into those fields.

The chunk covers these main domains:

- Color-buffer and blend state: surface number formats, channel swaps, CB operating modes, blend factors, combine functions, blend optimizations, CMASK codes/addressing, and a large `CBPerfSel` selector set for CB/cache/DCC/blend events.
- Command processor and perfmon controls: ring, pipe, ME identifiers, stream/CP perfmon states, CP perfmon enable modes, CPG/CPF/CPC perf selectors, CP alpha tag RAM selection, semaphore/IQ interrupt constants, and register-space range constants.
- Depth/stencil and DB instrumentation: Z ordering/force modes, compare and stencil operations, conservative-Z export, DB PSL control, DB `PerfCounter_Vals`, pixel-pipe counter IDs, strides, and GB EDC/tiling constants.
- Graphics/rasterization blocks: GRBM and per-shader-engine perf selectors, SU and SC performance selector tables, raster configuration map selectors for shader engines, scan converters, packers, and render backends.
- SPI and SQ descriptors/debug/performance: SPI sampling/fog/point-sprite values, SPI performance selectors, shader export formats, clock-gating modes, texture resource and sampler values, wave/thread-trace token values, SQ performance selectors, indirect SQ commands, EDC source selection, rounding and interrupt encodings, export/RAT instruction values, wave-buffer status values, shader memory modes, and thread-trace start prefix.
- Shader ISA encoding constants: instruction encoding masks/fields, counts/offsets for VOP/SOP/SMEM/DS/MUBUF/MTBUF/MIMG/EXP/FLAT encodings, register IDs, literal/source selectors, waitcnt fields, instruction opcodes, data-share operations, image operations, flat operations, scalar/vector compare and arithmetic opcodes, DPP/SDWA controls, system messages, hardware register IDs, and trap-related IDs.
- Texture and vertex fetch domains: texture border/chroma/clamp/coordinate/depth/dimension/format/filter/request/sampler values; vertex clamp/fetch/type/memory request values; TVX data format, destination/source selectors, endian swap, fetch instructions, numeric format, surface mode, and data type.
- Texture cache and TCC domains: `TC_OP_MASKS`, `TC_OP` cache/atomic/invalidation operations, credit constants, `TC_NACKS`, and the beginning of `TCC_PERF_SEL`.

## Important APIs, Types, And Constants

The exported interface is entirely compile-time symbols:

- `typedef enum <Name> { ... } <Name>;` gives typed numeric value domains. The large selector enums include `CBPerfSel` with 396 entries, `PerfCounter_Vals` with 257 entries, `SU_PERFCNT_SEL` with 153 entries, `SC_PERFCNT_SEL` with 397 entries, `SPI_PERFCNT_SEL` with 197 entries, and `SQ_PERF_SEL` with 292 entries in this chunk.
- Raw `#define` constants fill gaps where the generator emitted individual numeric constants rather than enums. These include register-space boundaries (`CONFIG_SPACE_*`, `UCONFIG_SPACE_*`, `PERSISTENT_SPACE_*`, `CONTEXT_SPACE_*`), SQ decoder ranges, instruction encoding masks/fields, register names, opcodes, source selectors, and message IDs.
- Small state enums such as `SurfaceNumber`, `SurfaceSwap`, `CBMode`, `CompareFrag`, `StencilOp`, `SQ_TEX_CLAMP`, `SQ_RSRC_IMG_TYPE`, `SQ_WAVE_TYPE`, `TEX_DIM`, and `TVX_DATA_FORMAT` are the likely values packed into specific register fields or descriptors.
- Performance selector enums such as `CBPerfSel`, `CPG_PERFCOUNT_SEL`, `CPF_PERFCOUNT_SEL`, `CPC_PERFCOUNT_SEL`, `PerfCounter_Vals`, `GRBM_PERF_SEL`, `SU_PERFCNT_SEL`, `SC_PERFCNT_SEL`, `SPI_PERFCNT_SEL`, `SQ_PERF_SEL`, and the partial `TCC_PERF_SEL` provide mux values for hardware counters.
- Shader ISA constants are not C-callable APIs, but they are an ABI-like hardware contract for disassembly/debug, packet generation, trap/thread-trace decode, and shader-engine diagnostics.

Representative enum families and their starts in this chunk are:

- Lines 27-120: compact CB/surface/blend/CMASK value domains.
- Lines 125-531: CB perf selectors and CB perf filters.
- Lines 535-679: CP ring/pipe/ME/perf/tag selectors.
- Lines 706-1059: DB/Z/stencil/perf and GB EDC value domains.
- Lines 1066-1822: GRBM, SU, SC, raster-map, and CSDATA domains.
- Lines 1831-2079: SPI value domains and SPI perf selectors.
- Lines 2079-2708: SQ descriptor, thread-trace, performance, command, EDC, export/RAT, and memory-mode enums.
- Lines 2710-4124: SQ ISA-related `#define` constants.
- Lines 4126-4368: texture and vertex fetch enums.
- Lines 4374-4519: TC operation masks, TC operations, credit constants, and NACK values.
- Lines 4520-4749: start of TCC perf selector values.

## Control Flow

This header has no direct runtime control flow. The implied driver flow is:

1. Compile GFX 8.0 AMDGPU code with this enum header and companion register headers.
2. Select a register field or packet/descriptor field from the offset and shift/mask metadata.
3. Choose one of these symbolic values to pack into the field, or decode a hardware readback/performance-counter selector into a symbolic domain.
4. Program MMIO/context state, build command packets, configure performance counters, or decode shader/thread-trace/cache/debug data in the surrounding driver code.

All sequencing, locking, polling, reset ordering, cache invalidation ordering, context-save behavior, and userspace-facing semantics are outside this file. This chunk only supplies literal numeric contracts.

## State And Persistence Behavior

The file itself is stateless. The constants describe values that may become persistent or volatile state after surrounding AMDGPU code writes them to hardware registers, command packets, descriptors, or shader/debug configuration.

CB/DB/SPI/SQ/TC/TCC performance selector values persist in hardware performance-counter mux registers until reprogrammed, while the counters they select are dynamic hardware observations. Selector mistakes can make counters appear valid while measuring the wrong block, event, client, cache state, or pipeline stall.

Surface, blend, Z/stencil, texture, vertex fetch, resource descriptor, shader export, and cache operation values participate in rendering and compute state. Once written into a context register or descriptor, they remain part of the active graphics/compute state until overwritten or context-switched by the driver.

SQ instruction and register constants describe encoded shader instructions, source operands, wait counters, hardware registers, system messages, thread-trace tokens, and trap/debug IDs. These values affect debug decode, trap handling, thread-trace interpretation, and any tool or driver path that reasons about ISA encodings.

Register-space boundary constants (`CONFIG_SPACE_*`, `PERSISTENT_SPACE_*`, `CONTEXT_SPACE_*`, `SQ*DEC_*`) classify MMIO ranges. Incorrect range usage can misclassify context-saved, persistent, user-config, or decoder-owned registers.

The partial `TCC_PERF_SEL` state in this chunk is not complete; any consumer or report must combine it with the following lines before reasoning about the full TCC selector domain.

## Dependencies And Integration Points

This header depends on the generated GFX 8.0 register set staying synchronized:

- Matching GFX 8.0 offset and shift/mask headers define where these enum values are written or read.
- AMDGPU register helper macros and MMIO/PM4 paths pack these values into register fields.
- Graphics initialization, context setup, command submission, debugfs/hang-dump code, shader trap/thread-trace code, RAS/EDC paths, KFD-adjacent compute paths, and performance-monitor code can depend on the values indirectly.
- Userspace graphics and compute stacks depend on these constants through the kernel's programming of CB/DB/SPI/SQ/TC/TCC state, shader ABI expectations, and performance/debug outputs.

Important integration surfaces include CB blending/compression/DCC behavior, DB depth/stencil testing and counters, CP ring/pipe/ME targeting, GRBM/SU/SC/SPI/SQ/TCC performance monitoring, raster configuration, SPI shader export and resource limits, SQ descriptor construction, SQ thread-trace decoding, shader trap/debug handling, texture and vertex fetch descriptors, TC cache invalidation/writeback/atomic operations, and TCC cache/client-event attribution.

## Risks And Edge Cases

- Generated-header drift is the primary risk. Wrong numeric enum values compile cleanly but program incorrect hardware behavior or decode the wrong event.
- The chunk ends mid-`TCC_PERF_SEL`; treating the TCC selector list as complete from this file alone would miss later client and event selectors.
- Large performance-selector enums are dense and index-sensitive. A single off-by-one or duplicated value can silently shift metrics for CB, DB, SC, SPI, SQ, or TCC counters.
- Several constants share generic names such as `SQ_F`, `SQ_LT`, `SQ_EQ`, and are redefined in different opcode/compare contexts. Include order and macro namespace collisions are a maintenance risk because these are preprocessor symbols, not scoped enum members.
- Reserved values are explicitly named in many domains. Their presence does not make them safe to program; callers need hardware documentation for reserved fields.
- Cache/TCC/TC operations include invalidation, writeback, atomic, and NACK values. Misusing these can lead to coherency failures, lost writes, page/protection fault misdiagnosis, or incorrect recovery logic.
- Shader ISA encodings are hardware ABI material. Mistakes can break disassembly, debug traps, thread tracing, wave state decode, or any code that emits or validates instructions.
- Register-space constants separate config, user-config, persistent, and context ranges. Bad classification can corrupt context save/restore or allow state to leak across contexts.
- Texture/vertex format enums directly affect how memory bytes are interpreted. Wrong values can cause rendering corruption without obvious kernel errors.

## Test Signals

Useful validation is mostly build coverage, generated-data checks, and hardware/runtime behavior:

- Kernel build coverage for AMDGPU code paths that include `gfx_8_0_enum.h`.
- Mechanical comparison against AMD's authoritative GFX 8.0 register/ISA database for every enum and `#define` in lines 1-4749.
- Static checks that enum values are unique where the hardware domain expects uniqueness, that intentional aliases/holes are documented, and that the partial `TCC_PERF_SEL` is completed by the next chunk.
- Cross-checks that values in this header are used with matching fields in the GFX 8.0 offset and shift/mask headers.
- Rendering tests covering CB formats, swaps, blending, CMASK/DCC, depth/stencil compares, stencil ops, conservative Z, raster mapping, texture sampling, vertex fetch formats, and shader export formats.
- Compute and shader-debug tests covering SQ resource descriptors, waitcnt fields, trap/thread-trace tokens, shader ISA decode, system messages, hardware-register access, and flat/DS/SMEM/MIMG/MUBUF operation handling.
- Performance-monitor tests that select representative CB, CP, DB, GRBM, SU, SC, SPI, SQ/SQC, TC, and TCC events and verify nonzero/monotonic/plausible counters under targeted workloads.
- Cache and VM tests exercising TC invalidation/writeback operations, atomics, NACK/page/protection fault reporting, and TCC hit/miss/client request attribution.
- Runtime warning signals include GPU hangs after context setup, incorrect color/depth output, texture/vertex corruption, unexpected VM faults or missing faults, broken shader trap/thread-trace decode, impossible performance counters, and metrics attributed to the wrong hardware block.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002711`. It covers lines 1-4749 of `gfx_8_0_enum.h`. The final per-file research should merge this with later chunks, especially to complete `TCC_PERF_SEL` and the remaining GFX 8.0 enum/value domains after line 4749.

### subset-b-002712: lines 4750-6858

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_0_enum.h lines 4750-6858

## Purpose

This chunk is the second and final slice of the generated AMD GFX 8.0 graphics-core enum header. It contains symbolic numeric values for hardware register fields and packet-facing encodings used by the GFX8 AMDGPU and KFD code paths. The range starts with the tail of `TCC_PERF_SEL` client request selectors, then defines texture/cache performance selectors, vertex/geometry/tessellation input and event encodings, surface tiling and format encodings, debug block identifiers, memory/cache policy values, perfmon modes, and memory power-control values. It ends with the file's include guard close.

The file is declarative hardware metadata. It does not implement logic, but the enum constants are part of the source-level contract between GFX8 driver code, generated register mask/offset headers, PM4 packet programming, memory-management setup, performance-counter configuration, and debug tooling. Keeping these values aligned with the GFX8 register database is important because callers often pass them into `REG_SET_FIELD()` or packet-building code where a wrong numeric value compiles cleanly but programs the wrong hardware behavior.

## Important APIs, Types, and Constants

There are no functions, structs, or inline helpers in this chunk. The exported interface is a large set of `typedef enum` definitions whose names and values are included by GFX8 AMDGPU/KFD files such as `gfx_v8_0.c`, `amdgpu_amdkfd_gfx_v8.c`, `sdma_v2_4.c`, `sdma_v3_0.c`, `kfd_device_queue_manager_vi.c`, and `kfd_mqd_manager_vi.c`.

Major enum families in this range are:

- Texture/cache performance selectors: `TCC_PERF_SEL` tail entries `TCC_PERF_SEL_CLIENT120_REQ` through `CLIENT127_REQ`, `TCA_PERF_SEL`, `TA_TC_ADDR_MODES`, `TA_PERFCOUNT_SEL`, `TD_PERFCOUNT_SEL`, and `TCP_PERFCOUNT_SELECT`. These select counters for TCC/TCA/TA/TD/TCP busy cycles, stalls, wavefront classes, format/dimension traffic, cache requests, XNACK phases, clock-gating visibility, and GATCL1/TCP/TC interactions.
- TCP behavior enums: `TCP_CACHE_POLICIES`, `TCP_CACHE_STORE_POLICIES`, `TCP_WATCH_MODES`, `TCP_DSM_DATA_SEL`, and `TCP_DSM_SINGLE_WRITE`, covering cache replacement/store policy, watchpoint mode, and DSM diagnostic-selection encodings.
- Vertex/geometry/tessellation enums: `VGT_OUT_PRIM_TYPE`, `VGT_DI_PRIM_TYPE`, `VGT_DI_SOURCE_SELECT`, `VGT_DI_MAJOR_MODE_SELECT`, `VGT_DI_INDEX_SIZE`, `VGT_EVENT_TYPE`, DMA swap/index/buffer modes, `VGT_OUTPATH_SELECT`, grouped primitive type/order/conversion enums, geometry shader mode/cut/outprim, cache invalidation mode, tessellation type/partition/topology, read-request policy, distribution mode, and per-stage enable enums for LS/HS/ES/GS/VS.
- VGT/IA/WD performance selectors: `VGT_PERFCOUNT_SELECT` has 146 entries, `IA_PERFCOUNT_SELECT` has 24 entries, and `WD_PERFCOUNT_SELECT` has 37 entries. These are used to select pipeline event-window, valid/stall, primitive, vertex, index, offchip, and draw-distribution performance events.
- Draw dispatch metadata: `WD_IA_DRAW_TYPE` and `WD_IA_DRAW_SOURCE` encode draw source classes such as DMA, auto, opaque, immediate, index buffer, and pre-draw-init paths.
- Surface and address-library encodings: `SurfaceEndian`, `ArrayMode`, `PipeTiling`, `BankTiling`, `GroupInterleave`, `RowTiling`, `BankSwapBytes`, `SampleSplitBytes`, `NumPipes`, `PipeInterleaveSize`, `BankInterleaveSize`, `NumShaderEngines`, `ShaderEngineTileSize`, `NumGPUs`, `MultiGPUTileSize`, `RowSize`, `NumLowerPipes`, `TileType`, `NonDispTilingOrder`, `MicroTileMode`, `TileSplit`, `SampleSplit`, `PipeConfig`, `NumBanks`, `BankWidth`, `BankHeight`, `BankWidthHeight`, and `MacroTileAspect`.
- Debug block identifiers: `DebugBlockId`, `DebugBlockId_OLD`, and compressed BY2/BY4/BY8/BY16 variants map graphics blocks such as CPF, CPC, CPG, SPI, SX, TA, TD, TCP, TCC, TCA, DB, CB, VGT, IA, WD, MC, SRBM, SDMA, UVD, VCE, IH, SEM, RLC, and other units into debug/perf infrastructure encodings.
- Render/texture formats: `ColorTransform`, `CompareRef`, `ReadSize`, `DepthFormat`, `ZFormat`, `StencilFormat`, `CmaskMode`, `QuadExportFormat`, `QuadExportFormatOld`, `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, `IMG_DATA_FORMAT`, `BUF_NUM_FORMAT`, and `IMG_NUM_FORMAT`. These include color/depth/stencil formats, block-compressed BC formats, FMASK encodings, numeric interpretation, SRGB, read width, comparison function, CMASK modes, and export format choices.
- Cache, memory, and perfmon control values: `GATCL1RequestType`, `TCC_CACHE_POLICIES`, `MTYPE`, `PERFMON_COUNTER_MODE`, `PERFMON_SPM_MODE`, `SurfaceTiling`, `SurfaceArray`, `ColorArray`, `DepthArray`, `ENUM_NUM_SIMD_PER_CU`, `MEM_PWR_FORCE_CTRL`, `MEM_PWR_FORCE_CTRL2`, `MEM_PWR_DIS_CTRL`, `MEM_PWR_SEL_CTRL`, and `MEM_PWR_SEL_CTRL2`.

Representative integration visible in this tree includes `MTYPE` values being used for GFX8 CP ring/HQD fields and KFD MQD setup. For example, `gfx_v8_0.c` sets `CP_RB0_CNTL.MTYPE` and HQD `IB_CONTROL`, `IQ_TIMER`, and `CTX_SAVE_CONTROL` memory-type fields to numeric value `3`, which corresponds to `MTYPE_UC` in this enum. KFD VI queue management uses `MTYPE_UC` and `MTYPE_NC` in MQD and device-queue-manager setup. GFX/MM hub code also programs `MC_VM_MX_L1_TLB_CNTL.MTYPE` with `MTYPE_UC` through generated register-field helpers.

## Control Flow

This header has no runtime control flow. Its effective flow is compile-time constant use:

1. A GFX8 source file includes `gca/gfx_8_0_enum.h` alongside generated register offset and mask headers.
2. The source chooses an enum constant matching a hardware field, packet opcode payload, tiling mode, format, perf counter, debug block, memory type, or power-control setting.
3. The value is shifted/masked by a generated field helper, copied into an MQD/ring structure, emitted into a PM4 command stream, or passed to lower-level register programming.
4. Hardware interprets the numeric field according to the GFX8 register specification.

The logical flows represented by this chunk are broad. Command submission and KFD queue setup use memory/cache policy values for ring buffers, indirect buffers, queue timers, context-save state, and MQDs. Graphics draw paths use primitive type, source, index-size, outpath, stage-enable, geometry/tessellation, and event enums when programming VGT/IA/WD state or emitting events. Surface allocation and display/render paths use tiling, endian, pipe/bank, array, sample-split, format, CMASK, depth/stencil, and export enums to describe memory layouts and shader-visible resources. Profiling paths use perf counter selector enums to choose signals from TA/TD/TCP/TCA/VGT/IA/WD/TCC blocks. Debug infrastructure uses block IDs to route debug or perf access to the intended graphics unit.

## State and Persistence Behavior

The enums themselves store no state and allocate no memory. The state affected by these constants lives in GPU registers, command streams, queue descriptors, page-table/cache controls, surface descriptors, and performance-monitor configuration programmed elsewhere.

Most values in this chunk are persistent only after a caller writes them into hardware-visible state. Examples include MQD and HQD queue fields that remain active until queue teardown, eviction, restore, or GPU reset; ring and TLB memory-type fields that remain until the next init/reset sequence; surface tiling/format metadata that persists in BO metadata or command descriptors; and perfmon selector/mode values that persist for the duration of a profiling session. Event and primitive encodings may be transient PM4 payloads, while debug block IDs and performance selectors may be used only during diagnostic reads or counter setup.

The header does not encode reset values, access permissions, side effects, read-clear/write-one-to-clear behavior, valid ASIC variants, or firmware sequencing. Callers must rely on companion register headers, AMDGPU/KFD lifecycle code, firmware contracts, and hardware documentation for those rules.

## Dependencies and Integration Points

This generated header depends only on C enum syntax and the include guard around the complete file. In practice it must remain synchronized with:

- Companion GFX8 GCA register offset and mask headers, especially fields whose legal values are defined here.
- AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32`, `RREG32`, SOC15 helpers, and PM4 packet-building macros that place enum values into bitfields.
- GFX8 command processor and ring setup in `amdgpu/gfx_v8_0.c`, including CP ring buffer memory type and HQD memory-type programming.
- KFD VI device queue and MQD management in `amdkfd/kfd_device_queue_manager_vi.c` and `amdkfd/kfd_mqd_manager_vi.c`, where MQDs and queue policies use GFX8 enum values.
- SDMA/GFX8 include users that share the enum namespace with generated register definitions.
- Address-library and tiling consumers that map `ArrayMode`, pipe/bank configuration, tile split, micro-tile mode, and format enums to BO metadata, display scanout, render targets, depth buffers, FMASK/CMASK, and shader image/buffer descriptors.
- Profiling and debugging paths that configure GFX8 performance counters, SPM modes, debug block routing, event selection, and status decoding.

Because C enum members occupy the global identifier namespace, this header is also coupled to other included AMD enum headers. The names are intentionally generation-specific in values but not always uniquely prefixed by generation, so include ordering and duplicate definitions must be controlled by the surrounding driver build.

## Risks and Edge Cases

The highest risk is silent ABI drift between these generated enum values and the GFX8 hardware specification. Incorrect values for `MTYPE`, cache policies, tiling, formats, primitive/event types, or perf selectors would still compile but could produce GPU hangs, corrupted rendering, bad queue memory behavior, wrong TLB/cache policy, broken profiling data, or invalid debug routing.

Large repeated enum families are difficult to review manually. `TCP_PERFCOUNT_SELECT`, `VGT_PERFCOUNT_SELECT`, `DebugBlockId`, `DebugBlockId_OLD`, and BY2/BY4/BY8/BY16 debug ID variants contain many near-regular values with reserved gaps and legacy encodings. A generator mistake or accidental edit can look plausible while changing the meaning of only one hardware block or selector.

Several names are semantically close but not interchangeable. `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, and `IMG_DATA_FORMAT` overlap numerically in places but target different register/descriptor fields. Similarly, `TileSplit` differs from `SampleSplit` and byte-oriented `SampleSplitBytes`; `SurfaceArray`, `ColorArray`, and `DepthArray` are related but not identical; `TCP_CACHE_POLICIES` and `TCC_CACHE_POLICIES` apply to different cache levels. Callers that reuse a value across fields because names or numeric ranges look similar risk programming an invalid encoding.

The chunk starts mid-enum with only the final eight `TCC_PERF_SEL` client selectors; the beginning of `TCC_PERF_SEL` is in the previous chunk. The final merged per-file report should treat this document as partial coverage of that enum but full coverage of all following enum definitions through the end of the file.

Enum constants include reserved values and legacy names. Reserved encodings are useful for exact generated coverage but should not be used as normal driver settings without explicit hardware guidance. Legacy debug block IDs and old quad-export formats may exist for compatibility with older debug hardware or tooling and should not be assumed to match newer ASIC enum headers.

## Test Signals

Useful validation for this chunk is mostly build-time, static, and hardware-integration oriented:

- Build GFX8 AMDGPU and KFD configurations to catch syntax errors, missing enum members, duplicate identifiers, and consumers expecting different names.
- Compare the entire line range against the authoritative GFX8 register database or generated-header source to verify every enum value, reserved gap, alias, and legacy debug ID variant.
- Exercise GFX8 command submission and KFD queue lifecycle tests: ring resume, MQD creation/update, HQD load/unload, context save/restore, eviction/restore, and GPU reset recovery should keep working with the expected `MTYPE` and queue-memory behavior.
- Run graphics draw and tessellation/geometry workloads that cover indexed and non-indexed draws, primitive types, VGT events, stage enable modes, outpath modes, and DMA/index-size encodings.
- Validate surface/display/render paths with linear and tiled BOs, compressed/depth/stencil formats, FMASK/CMASK, endian/tiling metadata, multisample splits, and pipe/bank configurations.
- Use performance-counter or SPM tooling on GFX8 hardware to confirm TA/TD/TCP/TCA/TCC/VGT/IA/WD selector values select the intended signals and that `PERFMON_COUNTER_MODE`/`PERFMON_SPM_MODE` settings produce sane counter behavior.
- Exercise debug/perf block routing, where available, to confirm `DebugBlockId` and legacy/BY* encodings still address the intended hardware units.
