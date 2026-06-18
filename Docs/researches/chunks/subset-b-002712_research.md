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
