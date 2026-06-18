# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_1_enum.h lines 4754-6808

## Scope

This chunk is the second and final slice of the AMD GFX 8.1 generated enum header. It starts inside the tail of `TCC_PERF_SEL`, covering `TCC_PERF_SEL_CLIENT69_REQ` through `TCC_PERF_SEL_CLIENT127_REQ`, then defines the remaining register-field value enums through the closing `#endif /* GFX_8_1_ENUM_H */`.

The file is declarative hardware ABI metadata. It contains `typedef enum` constants and one size macro, `GSTHREADID_SIZE`; it has no functions, structs, runtime variables, allocations, locks, branches, callbacks, or persistence code. Although the source path is under a Ceph client mirror, this header is AMD GPU driver register documentation for GFX 8.1 and has no distributed-filesystem behavior.

## Purpose

`gfx_8_1_enum.h` supplies symbolic names for numeric values programmed into or decoded from GFX 8.1 hardware registers. The companion generated headers in the same directory provide the register addresses and bit layouts: `gfx_8_1_d.h` has register identifiers and offsets, while `gfx_8_1_sh_mask.h` has field shifts and masks. This enum header names the legal or documented values that occupy those fields.

This chunk covers several major hardware domains:

- Texture/cache performance selector values for TCC, TCA, TA, TD, and TCP.
- TCP cache policies, watch modes, data-share-monitor controls, and memory request classification values.
- VGT, IA, and WD draw, primitive, event, tessellation, shader-stage, and performance counter selectors.
- Debug block IDs and reduced-width debug block ID encodings.
- Surface, color, depth, stencil, export, buffer, image, numeric, tiling, pipe/bank, cache, memory type, performance monitor, array, and memory-power mode enums.

These constants are effectively part of the hardware-facing ABI for the GFX 8.1 generation. Their numeric values matter more than their C type names because callers ultimately write packed register fields, PM4 packets, or indirect debug/performance selector values.

## Important APIs, Types, And Constants

The chunk completes `TCC_PERF_SEL` with client request selectors `CLIENT69_REQ` through `CLIENT127_REQ`, ending at `0xff`. The preceding chunk owns the beginning of this enum, so any merged per-file report must treat `TCC_PERF_SEL` as split across chunk boundaries.

The texture and cache performance families are:

- `TCA_PERF_SEL`: TCA counters for cycles, busy state, forced holes, per-TCC requests, crossbar double arbitration, and crossbar stalls for TCC0-TCC7.
- `TA_TC_ADDR_MODES`: TA-to-TC address modes, including default, component swizzles `COMP0`-`COMP3`, unaligned, and border-color access modes.
- `TA_PERFCOUNT_SEL`: TA counters for shader FIFO busy states, gradient/LOD/addresser/aligner/write-path activity, wavefront classes, image/buffer/flat operations, stalls, mip/aniso/sample distributions, SCLK-valid and clock-gating signals, and XNACK phase events.
- `TD_PERFCOUNT_SEL`: TD counters for busy states, FIFO fullness, stalls from TC/PC/GDS, gather/sample/load/store/atomic wavefronts, D16 and filter modes, border handling, NACKs, poison signals, start-cycle buckets, null cycles, and packed D16 data.
- `TCP_PERFCOUNT_SELECT`: the largest selector group in this chunk. It covers TA/TCP/TD/TCR stalls, tag conflicts, latency, TCC request classes, global/local read/write/atomic totals, image and buffer format counters, tiling/dimension counters, invalidates, tag RAM requests, clock/power gates, cache hit/miss policy buckets, PRT/microtiling, MTYPE and volatility classes, XNACK/ATCL1/GATCL1 behavior, and ETC2 or widened image read/write format events.

The TCP control enums are small field-value domains:

- `TCP_CACHE_POLICIES`: miss/hit LRU or evict policies.
- `TCP_CACHE_STORE_POLICIES`: write-through LRU or evict store policy.
- `TCP_WATCH_MODES`: read, non-read, atomic, or all-access watch selection.
- `TCP_DSM_DATA_SEL` and `TCP_DSM_SINGLE_WRITE`: data-share-monitor selection and single-write enable.

The VGT, IA, and WD draw pipeline enums define front-end command and primitive semantics:

- `VGT_OUT_PRIM_TYPE`, `VGT_DI_PRIM_TYPE`, `VGT_GRP_PRIM_TYPE`, and `VGT_GRP_PRIM_ORDER` encode point/line/triangle/patch/rect/quad/list/strip/fan/loop/polygon primitive forms, including adjacency and 2D copy/fill variants.
- `VGT_DI_SOURCE_SELECT`, `VGT_DI_MAJOR_MODE_SELECT`, `VGT_DI_INDEX_SIZE`, `VGT_INDEX_TYPE_MODE`, `VGT_DMA_SWAP_MODE`, and `VGT_DMA_BUF_TYPE` describe draw-index input source, index width, DMA byte swapping, and DMA buffer source/update behavior.
- `VGT_EVENT_TYPE` names event IDs such as cache flushes, partial flushes, streamout sync/reset/sample, timestamp events, performance counter start/stop/sample, pipeline stats, shader-output flushes, context done, thread trace start/stop/marker/flush/finish, and pixel pipe stats controls.
- `VGT_OUTPATH_SELECT`, `VGT_GROUP_CONV_SEL`, `VGT_GS_MODE_TYPE`, `VGT_GS_CUT_MODE`, `VGT_GS_OUTPRIM_TYPE`, `VGT_CACHE_INVALID_MODE`, `VGT_TESS_TYPE`, `VGT_TESS_PARTITION`, `VGT_TESS_TOPOLOGY`, `VGT_RDREQ_POLICY`, and `VGT_DIST_MODE` encode vertex reuse, tessellation, geometry shader, cache invalidation, read policy, and distribution modes.
- `VGT_STAGES_LS_EN`, `VGT_STAGES_HS_EN`, `VGT_STAGES_ES_EN`, `VGT_STAGES_GS_EN`, and `VGT_STAGES_VS_EN` represent shader-stage enable/remap modes for LS, HS, ES, GS, and VS.
- `VGT_PERFCOUNT_SELECT`, `IA_PERFCOUNT_SELECT`, and `WD_PERFCOUNT_SELECT` provide front-end performance selectors for SPI/VGT/PA handshakes, stalls, starves, cache hits, shader-stage done latency, thread groups, ring/table high-water marks, input assembler latency, DMA FIFO state, work distributor busy/stall state, tessellation frequency bins, and HS done status by shader engine.
- `WD_IA_DRAW_TYPE` and `WD_IA_DRAW_SOURCE` encode draw metadata channels and DMA/immediate/auto/opaque draw sources.

Debug and observability constants include:

- `GSTHREADID_SIZE`, defined as `0x2`.
- `DebugBlockId`: full debug block selector IDs for global blocks and per-instance units such as VMC, PDMA, CG, SRBM, GRBM, RLC, IH, SQ, SDMA, GDS, VC, PA, CP, VGT, IA, SX, TCA, TCC, MCC, SQA/SQB/SQ, CB, TCP, DB, SPS, TA, TD, and LDS instances.
- `DebugBlockId_BY2`, `DebugBlockId_BY4`, `DebugBlockId_BY8`, and `DebugBlockId_BY16`: reduced encodings that group or stride the full debug block namespace by 2, 4, 8, or 16. These are not interchangeable with the full IDs; they correspond to narrower selector fields or grouped debug routes.

The render, image, and memory format enums include:

- `SurfaceEndian`, `SurfaceTiling`, `SurfaceArray`, `ColorArray`, and `DepthArray` for endian, linear/tiled, 1D/2D/3D, color array, and depth array mode fields.
- `ArrayMode`, `PipeTiling`, `BankTiling`, `GroupInterleave`, `RowTiling`, `BankSwapBytes`, `SampleSplitBytes`, `NumPipes`, `PipeInterleaveSize`, `BankInterleaveSize`, `NumShaderEngines`, `ShaderEngineTileSize`, `NumGPUs`, `MultiGPUTileSize`, `RowSize`, and `NumLowerPipes` for GFX8 surface addressing and tiling configuration.
- `TileType`, `NonDispTilingOrder`, `MicroTileMode`, `TileSplit`, `SampleSplit`, `PipeConfig`, `NumBanks`, `BankWidth`, `BankHeight`, `BankWidthHeight`, and `MacroTileAspect` for address-library-compatible tile layout fields.
- `ColorTransform`, `CompareRef`, `ReadSize`, `DepthFormat`, `ZFormat`, `StencilFormat`, and `CmaskMode` for color transform, depth/stencil comparison, read size, depth/stencil formats, and CMASK compression/clear modes.
- `QuadExportFormat` and `QuadExportFormatOld` for shader export packing formats.
- `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, `IMG_DATA_FORMAT`, `BUF_NUM_FORMAT`, and `IMG_NUM_FORMAT` for color/surface/buffer/image data layouts and numeric interpretation. Notable image formats include ETC2, BCn compression, FMASK encodings, packed depth/stencil formats, `GB_GR`/`BG_RG`, 1-bit formats, and `32_AS_*` reinterpretation formats.

The cache, memory, performance monitor, and power enums are:

- `GATCL1RequestType`: normal, shootdown, or bypass request type.
- `TCC_CACHE_POLICIES`: LRU or stream policy.
- `MTYPE`: memory type values `NC_NV`, `NC`, `CC`, and `UC`.
- `PERFMON_COUNTER_MODE`: accumulation, active cycles, max, dirty, sample, cycles since first/last event, high-threshold comparisons, inactive cycles, and reserved mode.
- `PERFMON_SPM_MODE`: off, 16-bit or 32-bit streaming performance monitor modes with clamp/no-clamp, reserved values, and test modes.
- `ENUM_NUM_SIMD_PER_CU`: documents `NUM_SIMD_PER_CU` as `0x4`.
- `MEM_PWR_FORCE_CTRL`, `MEM_PWR_FORCE_CTRL2`, `MEM_PWR_DIS_CTRL`, `MEM_PWR_SEL_CTRL`, and `MEM_PWR_SEL_CTRL2`: memory power force, disable, and dynamic shutdown/deep-sleep/light-sleep selection fields.

## Control Flow

There is no control flow in this header. Runtime behavior appears only in consumers that use these enum values with register or packet programming helpers:

1. Generation-specific code selects a register from `gfx_8_1_d.h` and a field mask/shift from `gfx_8_1_sh_mask.h`.
2. The caller chooses one of the enum values from this header or a matching literal value from firmware/table data.
3. The value is shifted and masked into a register word, PM4 packet field, performance-counter selector, debug selector, or surface/resource descriptor field.
4. AMDGPU MMIO, indirect register, command submission, or firmware-mediated paths deliver the encoded value to hardware.
5. For status, debug, and performance paths, hardware returns numeric selector/data values that diagnostics can decode using these same symbolic domains.

No direct `#include "gfx_8_1_enum.h"` reference was found under the mirrored AMD driver tree during this research pass. That does not make the file dead by itself: generated enum headers are often consumed by generated register tooling, conditional build paths, out-of-tree diagnostics, or code that keeps numeric values in packet/register tables rather than naming the enum symbols directly.

## State And Persistence Behavior

The header persists no software state. All constants are compile-time values.

The hardware fields represented by these constants have stateful effects once programmed:

- Performance selector values configure which hardware events TA, TD, TCP, TCA, TCC, VGT, IA, and WD counters observe. Counter values persist in hardware counter registers until reset, reprogramming, sampling, context switch handling, or power/reset events according to the performance monitor sequence.
- Cache policy, MTYPE, volatility, ATCL1/GATCL1, XNACK, and invalidate-related values influence cache/memory request routing and observability. Incorrect values can alter coherency, eviction, bypass, translation, or replay behavior.
- Draw, primitive, index, DMA, tessellation, geometry, and shader-stage enums affect command processor/front-end interpretation of submitted draws. Their effects persist for the relevant packet/register state until overwritten by later command streams or context state.
- `VGT_EVENT_TYPE` values trigger or request synchronization, flushing, timestamps, performance sampling, thread tracing, and context/shader events. Many event side effects are immediate and ordering-sensitive rather than persistent configuration.
- Debug block IDs select live hardware blocks or grouped block ranges for debug/performance routes. The selected debug path can expose volatile state that changes as waves, queues, caches, and front-end blocks execute.
- Surface, format, tiling, array, pipe, bank, and numeric-format values become part of color/depth/resource descriptor interpretation. They persist as register or descriptor state until command submission or driver setup replaces them.
- Memory power mode values force or permit light sleep, deep sleep, shutdown, or disable memory power control. Their effective lifetime depends on clock/power-gating registers, firmware policy, suspend/resume, reset, and ASIC power transitions.

Reserved enum entries are still numeric field values but should not be treated as safe programming choices unless the hardware specification or existing driver sequence requires them.

## Dependencies And Integration Points

This chunk depends on the generated GFX 8.1 register database staying synchronized across:

- `gfx_8_1_enum.h`, which provides the symbolic values researched here.
- `gfx_8_1_d.h`, which provides the matching register addresses and indirect indices.
- `gfx_8_1_sh_mask.h`, which provides the matching field masks and shifts.
- AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, direct MMIO helpers, SOC15-era register helpers, indirect-register accessors, and PM4 packet builders used by the GFX, CP, KFD, debug, and performance code.
- Surface/addressing code that must map DRM/AMDGPU surface, buffer, color, depth, FMASK, compression, tiling, pipe, and bank choices onto GFX8 hardware descriptor fields.
- Performance monitoring paths that program block selectors and counter modes, including normal counter reads and SPM modes.
- Debug and hang-dump paths that select GFX debug block IDs, route block-specific state, or decode live wave/front-end/cache activity.
- Power-management and clock-gating code that programs memory power controls and interprets block-level busy, stall, and SCLK-valid performance signals.

These enums are generation-specific. Names that look similar in `gfx_8_0_enum.h`, `gfx_7_2_enum.h`, OSS enum headers, or later `navi10_enum.h` may have different value sets, added formats, renamed reserved holes, or different field widths.

## Risks And Edge Cases

- The chunk starts mid-enum. `TCC_PERF_SEL` must be reconciled with chunk `subset-b-002719`; this document only covers the `CLIENT69_REQ`-`CLIENT127_REQ` tail.
- Header/field mismatch is the main integration risk. Pairing GFX 8.1 enum values with another generation's offset or mask header can compile but program semantically wrong values.
- Many enum names are broad hardware terms rather than type-safe APIs. C will not prevent a `SurfaceFormat` value from being assigned to an unrelated integer field if a caller bypasses local validation.
- Reserved values appear throughout the chunk. They may read back from hardware, but writing them can trigger undefined behavior, dropped draws, incorrect tiling, invalid descriptors, or broken performance/debug collection.
- Format enums are easy to confuse: `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, and `IMG_DATA_FORMAT` overlap partially but are not identical. ETC2, FMASK, `32_AS_*`, depth/stencil, and buffer-only/image-only cases need field-specific validation.
- `DebugBlockId` and the `_BY2`/`_BY4`/`_BY8`/`_BY16` variants encode different selector spaces. Using a grouped selector in a full-width debug field, or vice versa, can route diagnostics to the wrong block.
- VGT event values are ordering-sensitive. Flush, timestamp, thread trace, and context-done events need the correct packet sequence and cache/domain waits; the enum itself does not encode those ordering rules.
- Primitive and shader-stage enums interact with command stream state. Invalid combinations of tessellation, GS mode, out path, index source, and primitive topology can hang, drop primitives, or produce undefined rendering.
- Tiling and pipe/bank enums represent hardware address swizzles. Incorrect values can corrupt memory interpretation without failing at compile time.
- Memory power force/disable modes can create hard-to-debug hangs or performance regressions if used outside the intended power-management sequence.

## Test And Validation Signals

Useful validation is mostly compile-time, generated-header consistency, and hardware-runtime testing:

- Build AMDGPU and KFD configurations that include GFX8 support. Direct references to enum names should fail quickly if a generated name is misspelled or removed.
- Verify generated-header consistency between `gfx_8_1_enum.h`, `gfx_8_1_d.h`, and `gfx_8_1_sh_mask.h`: enum domains should fit the target field widths, reserved holes should remain intentional, and selector values should not exceed documented masks.
- Run static checks or scripts that detect duplicated enum values where aliases are not expected, enum values larger than their register field, and accidental cross-generation include mixing.
- Exercise draw paths with indexed and non-indexed draws, 8/16/32-bit indices, immediate/auto index sources, adjacency, patches, tessellation, GS paths, and the listed primitive types.
- Exercise cache flush, partial flush, timestamp, performance counter, pipeline-stat, thread-trace, and context events using known command stream sequences and confirm expected ordering and completion.
- Validate TA/TD/TCP/TCA/TCC/VGT/IA/WD performance counter programming by selecting representative events, reading counters, and checking that idle, busy, stall, and format-specific workloads move plausible counters.
- Test representative color/depth/buffer/image descriptors across uncompressed, compressed BCn/ETC2, FMASK, depth/stencil, sRGB, integer, float, and `*_AS_*` formats.
- Validate tiling/addressing choices with linear, 1D/2D/3D, macro/micro-tiled, pipe/bank, sample split, and multi-GPU-related surface layouts using render/copy/checksum tests.
- Exercise debug block routing on real GFX 8.1 hardware, including full `DebugBlockId` selectors and grouped `_BY*` selector fields if exposed by diagnostics.
- Run suspend/resume, GPU reset, power-gating, clock-gating, and memory power-control tests to catch incorrect memory power enum usage or stale performance/debug selector state.
