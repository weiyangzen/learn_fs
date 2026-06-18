# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_7_2_enum.h lines 4780-6280

## Scope

This chunk is the final portion of the generated AMD GFX 7.2 enum header. It starts in the tail of `VGT_EVENT_TYPE` and continues through draw-initiator, vertex-geometry-tessellation, performance-counter, surface-format, debug-block, tiling, cache-policy, memory-type, and performance-monitor enums. It ends with the file's closing `#endif`.

The range contains enum constants and one generated size macro only. There are no functions, structs with storage, global variables, allocations, locks, callbacks, loops, branches, or runtime side effects in this chunk.

## Purpose

The purpose of this section is to provide generation-specific numeric constants for programming and decoding AMD GCN/GFX 7.2 hardware registers and PM4 packet fields. The constants are part of the kernel driver's hardware ABI for CIK-era graphics, memory, display, KFD, and debug paths.

The enum values are not arbitrary software choices. They encode register field values consumed by GPU blocks such as VGT, IA, WD, CB, DB, TA/TCP/TCC, GRBM/debug, and perfmon/SPM. Callers include this header to avoid open-coded numeric literals when composing packets, selecting surface formats, configuring tile modes, selecting debug blocks, or choosing performance counter modes.

Although this repository path is under `sources/distributed-fs/ceph-client`, this file is AMD GPU metadata and has no Ceph filesystem behavior.

## Important APIs, Types, And Constants

The API surface is the generated enum namespace. Important groups in this chunk are:

- `VGT_EVENT_TYPE` tail values at lines 4780-4834, including cache flush, partial flush, streamout sync/reset, end-of-pipe, ZPASS, perfcounter, pipeline-stat, context, thread-trace, pixel-pipe-stat, and `CONTEXT_SUSPEND` events. These values are used in PM4 event packets and release-memory/cache-flush sequences.
- Draw and VGT setup enums: `VGT_DMA_SWAP_MODE`, `VGT_INDEX_TYPE_MODE`, `VGT_DMA_BUF_TYPE`, `VGT_OUTPATH_SELECT`, `VGT_GRP_PRIM_TYPE`, `VGT_GRP_PRIM_ORDER`, `VGT_GROUP_CONV_SEL`, `VGT_GS_MODE_TYPE`, `VGT_GS_CUT_MODE`, `VGT_GS_OUTPRIM_TYPE`, `VGT_CACHE_INVALID_MODE`, `VGT_TESS_TYPE`, `VGT_TESS_PARTITION`, `VGT_TESS_TOPOLOGY`, `VGT_RDREQ_POLICY`, and shader-stage enable enums for LS/HS/ES/GS/VS. These map API draw, tessellation, geometry-shader, cache, and stage-routing choices to VGT register encodings.
- `VGT_PERFCOUNT_SELECT` at lines 4968-5109, a large selector table for VGT/SPI/PA/clipper, tessellation, streamout, cache-reuse, busy, stall, flush, done-latency, and high-watermark events. It is the selector domain for VGT performance counters.
- `IA_PERFCOUNT_SELECT` and `WD_PERFCOUNT_SELECT`, which cover input assembler and work distributor performance events such as memory-controller latency bins, FIFO starvation/stall, clock-valid events, busy, DMA return, and draw/input stalls.
- `WD_IA_DRAW_TYPE` and `GSTHREADID_SIZE`, which describe WD/IA draw command fields and the generated GS thread-id field size.
- Surface and address layout enums: `SurfaceEndian`, `ArrayMode`, `PipeTiling`, `BankTiling`, `GroupInterleave`, `RowTiling`, `BankSwapBytes`, `SampleSplitBytes`, `NumPipes`, `PipeInterleaveSize`, `BankInterleaveSize`, `NumShaderEngines`, `ShaderEngineTileSize`, `NumGPUs`, `MultiGPUTileSize`, `RowSize`, and `NumLowerPipes`. These define the values used in GPU tiling/address-configuration registers and tile-mode tables.
- Debug block enums: `DebugBlockId`, `DebugBlockId_OLD`, `DebugBlockId_BY2`, `DebugBlockId_BY4`, `DebugBlockId_BY8`, and `DebugBlockId_BY16`. These enumerate GRBM/debug client block IDs and stride-compressed variants for selecting repeated hardware blocks such as CB, DB, TCP, TA, TD, TCC, MCD/MCC, VGT, PC, SDMA, UVD, VCE, SMU, and shader-engine components.
- Render/depth/format enums: `CompareRef`, `ReadSize`, `DepthFormat`, `ZFormat`, `StencilFormat`, `CmaskMode`, `QuadExportFormat`, `QuadExportFormatOld`, `ColorFormat`, and `SurfaceFormat`. These represent depth/stencil comparison, DB/CB formats, CMASK compression states, and color/export surface encodings.
- Texture and buffer format enums: `BUF_DATA_FORMAT`, `IMG_DATA_FORMAT`, `BUF_NUM_FORMAT`, and `IMG_NUM_FORMAT`. They cover scalar/vector component layouts, packed color/depth formats, BC compression formats, FMASK formats, normalized/scaled/integer/float interpretation, sRGB, and OpenGL-specific SNORM/UBNORM encodings.
- Additional surface/cache/perf enums: `TileType`, `NonDispTilingOrder`, `MicroTileMode`, `TileSplit`, `SampleSplit`, `PipeConfig`, `NumBanks`, `BankWidth`, `BankHeight`, `BankWidthHeight`, `MacroTileAspect`, `TCC_CACHE_POLICIES`, `MTYPE`, `PERFMON_COUNTER_MODE`, `PERFMON_SPM_MODE`, `SurfaceTiling`, `SurfaceArray`, `ColorArray`, and `DepthArray`.

There are no local helper functions. The effective "types" are C enum names that compile to integer constants used in register bitfields and packet words.

## Control Flow

This header has no direct runtime control flow. The runtime pattern is:

1. A GFX6/GFX7/CIK driver file includes `gca/gfx_7_2_enum.h`.
2. Driver code chooses an enum value based on ASIC family, requested draw operation, surface layout, cache operation, debug target, or perf counter being configured.
3. The value is shifted into a register field or packet field by a companion macro/helper such as `EVENT_TYPE(...)`, `EVENT_INDEX(...)`, tile-mode `PIPE_CONFIG(...)`, or register field composition helpers.
4. The command processor, register block, or indirect debug/perf interface interprets the encoded value.

Examples from nearby consumers include `gfx_v6_0.c` and `gfx_v7_0.c`, which include this header and use values such as `CACHE_FLUSH_AND_INV_TS_EVENT` in ring/cache-flush event packets and `ADDR_SURF_P*` pipe configuration values in tile-mode setup tables. `amdgpu_amdkfd_gfx_v7.c`, `cik.c`, `cik_sdma.c`, `dce_v6_0.c`, and `dce_v8_0.c` also include this enum header, so these constants bridge graphics, KFD, SDMA, common CIK initialization, and display code.

## State And Persistence Behavior

The constants themselves are compile-time metadata and persist no state. The hardware registers and command streams that consume them are stateful:

- VGT event constants trigger synchronization, cache flush/invalidate, streamout, context, perf-counter, pipeline-stat, thread-trace, and pixel-pipe-stat behavior when written into event packet fields. Some events only signal or sample hardware state; others can flush caches, invalidate metadata, increment counters, or produce timestamps.
- Draw, primitive, index, geometry, tessellation, and shader-stage values persist in context or config registers until changed by context switching, command stream programming, reset, or power-management reinitialization.
- Performance selector and perfmon mode enums select what counters accumulate and how SPM/counter data is sampled. Counter values are live hardware state; selector/mode registers are configuration state.
- Tiling, array, bank, pipe, macro-tile, split, and endian values describe memory layout. Once used to allocate or program a surface, the same layout interpretation must be used consistently by CPU-side address libraries, kernel driver programming, firmware-visible tables, and hardware consumers.
- Format enums define how bytes in memory are interpreted by CB/DB/texture/buffer units. Changing a format changes interpretation, not storage; stale or mismatched metadata can make valid memory render incorrectly.
- Debug block IDs are selectors for hardware debug interfaces. They do not store debug data but determine which physical block subsequent reads or writes address.
- Cache policy and `MTYPE` values influence coherence, eviction, and memory transaction behavior for programmed resources.

The header does not express which enum values are legal for a specific register field. That legality is imposed by the ASIC register spec and by the code path using the constants.

## Dependencies

This chunk depends on synchronized AMD GFX 7.2 generated headers and driver helper conventions:

- Companion GFX 7.2 offset and shift/mask headers define the registers and bit positions into which these enum values are placed.
- PM4 packet macros in GFX/KFD code rely on event enum values matching the command processor's `EVENT_TYPE` encoding.
- GFX6/GFX7 tile-mode setup uses these address-layout constants with macros such as `PIPE_CONFIG`, `ARRAY_MODE`, bank/pipe/row/interleave fields, and ASIC-specific tile mode arrays.
- Display and memory code include the same format and tiling enums for shared surface metadata, scanout, and buffer/image programming.
- KFD packet managers and GFX7 KFD integration depend on common event, format, trap/debug, and performance encodings when programming queues or interpreting GPU-visible state.
- Debug and profiling paths depend on `DebugBlockId*`, `VGT_PERFCOUNT_SELECT`, `IA_PERFCOUNT_SELECT`, `WD_PERFCOUNT_SELECT`, `PERFMON_COUNTER_MODE`, and `PERFMON_SPM_MODE` staying aligned with hardware.
- The enum names are reused in several generation headers, including DCE/GMC/SMU and later `*_enum.h` files. Shared names can mask generation-specific value or availability differences, so include ordering and selected ASIC header matter.

## Integration Points

Primary integration points are:

- `drivers/gpu/drm/amd/amdgpu/gfx_v6_0.c` and `gfx_v7_0.c`: graphics initialization, tile-mode tables, ring emission, cache flush/event waits, and generation-specific GFX programming.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v7.c`: KFD integration for GFX7 queues, events, and GPU debug/runtime interactions.
- `drivers/gpu/drm/amd/amdgpu/cik.c`: common CIK initialization and ASIC support paths.
- `drivers/gpu/drm/amd/amdgpu/cik_sdma.c`: SDMA-era CIK code that shares generated enum definitions.
- `drivers/gpu/drm/amd/amdgpu/dce_v6_0.c` and `dce_v8_0.c`: display code that needs shared surface/format/layout constants.
- PM4 packet definitions in KFD headers for VI/GFX-era event values, where constants such as `CACHE_FLUSH_AND_INV_TS_EVENT` must match the event encoding in this header.
- Address/tile calculation and memory-management logic that must agree with the hardware's `ArrayMode`, `PipeConfig`, bank, split, tile type, and macro-tile encodings.
- Profiling/debug tools exposed through kernel paths, where perf counter selections and debug block IDs define what hardware signal or block is observed.

## Risks And Edge Cases

- The chunk starts mid-enum at line 4780. The prior chunk contains the beginning of `VGT_EVENT_TYPE`, so the merge lane must combine both chunks to describe that enum completely.
- Enum name reuse across generations is a correctness risk. A value that is valid for GFX 7.2 may be absent, reserved, or have different semantics in later GFX/GC/DCE/GMC/SMU enum headers.
- Reserved enum values are preserved because hardware fields have fixed encodings. Software should not treat `Reserved_*`, `*_RESERVED_*`, or old debug IDs as safe feature values without an ASIC-specific programming sequence.
- Event constants can have side effects. Misusing cache flush/invalidate, end-of-pipe timestamp, thread-trace, context, or perf-counter events can break synchronization, leak stale data, or produce misleading fence/timestamp behavior.
- Format aliases are easy to confuse. `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, and `IMG_DATA_FORMAT` contain similar-looking values but apply to different hardware blocks and descriptor fields.
- Depth/stencil and FMASK/CMASK formats must match allocation metadata. Incorrect combinations can corrupt depth tests, compression metadata, resolve behavior, or scanout/rendering interpretation.
- Tiling values are ABI-sensitive. Incorrect pipe/bank/row/interleave/split settings can cause address swizzling mismatches, GPU page faults, bad display output, or silent rendering corruption.
- Debug block ID variants (`OLD`, `BY2`, `BY4`, `BY8`, `BY16`) compress or remap block selector spaces. Using the wrong variant can select a neighboring hardware block while still producing plausible debug output.
- Performance selector enums expose many internal events. Some selectors may be invalid on fused-off units, disabled shader engines, or ASIC variants even when the enum value exists in the generated header.
- `GSTHREADID_SIZE` is a bare generated macro in the enum stream. Consumers should treat it as a field-size constant, not as a count of live GS waves or threads.

## Test And Validation Signals

Useful validation is mostly build, static, and hardware coverage:

- Build AMDGPU and KFD configurations that include `gfx_7_2_enum.h`, especially CIK/GFX6/GFX7, DCE6/DCE8, SDMA, and GFX7 KFD paths.
- Static checks that generated enum values remain synchronized with companion GFX 7.2 offset and shift/mask headers and with PM4 packet field definitions.
- Ring/fence tests that exercise `CACHE_FLUSH_AND_INV_TS_EVENT`, partial flushes, end-of-pipe timestamps, context events, and event-index handling on GFX6/GFX7 hardware or emulation.
- Graphics API draw tests covering indexed/non-indexed draws, immediate/auto-index source selection, primitive types, tessellation, geometry-shader output, streamout, and cache invalidation.
- Tile-mode and memory-layout tests for scanout, render targets, depth buffers, compressed textures, FMASK/CMASK, 1D/2D/3D arrays, thick/thin micro-tiling, and bank/pipe variants.
- Format conformance tests that render/sample/copy representative `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, and `IMG_DATA_FORMAT` values, including sRGB, BCn, depth/stencil, and FMASK cases.
- Perf counter tests that select VGT/IA/WD events and verify plausible changes under idle, draw, tessellation, geometry-shader, streamout, and cache-heavy workloads.
- SPM/perfmon tests for each supported counter mode, checking accumulation, active/inactive cycle modes, max/dirty/sample behavior, and clamp/no-clamp SPM encoding.
- Debugfs or hang-dump validation that selects representative `DebugBlockId*` values and confirms the selected block identity matches physical ASIC topology.
- Suspend/resume, GPU reset, and power-transition tests, because event, perf, tile, cache, and memory-type register state may need reprogramming after hardware reset or power gating.
