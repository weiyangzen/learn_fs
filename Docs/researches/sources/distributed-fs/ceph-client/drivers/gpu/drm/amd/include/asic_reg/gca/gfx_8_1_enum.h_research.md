# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_1_enum.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002719`: lines 1-4753, `Docs/researches/chunks/subset-b-002719_research.md`
- `subset-b-002720`: lines 4754-6808, `Docs/researches/chunks/subset-b-002720_research.md`

## Chunk Research

### subset-b-002719: lines 1-4753

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_1_enum.h lines 1-4753

## Scope

This chunk is the first 4,753 lines of the generated-style AMD GFX 8.1 enum header. The full file is 6,808 lines, but this research covers only the requested range. The chunk starts at the file license/header guard and ends inside `typedef enum TCC_PERF_SEL`, at `TCC_PERF_SEL_CLIENT68_REQ = 0xc4`; the remaining `TCC_PERF_SEL` client events and later enum definitions are outside this chunk.

Although the path is under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

`gfx_8_1_enum.h` names the numeric values programmed into, or decoded from, GFX 8.1 hardware register fields, command fields, performance counter selectors, shader instruction encodings, texture/resource descriptors, and cache/memory operation selectors. It complements the sibling GFX 8.1 register offset and shift/mask headers:

- `gca/gfx_8_1_d.h` supplies register offsets.
- `gca/gfx_8_1_sh_mask.h` supplies field shifts and masks.
- This enum header supplies meaningful values for those fields.

The values are a hardware ABI. Consumers write the numeric constants into register fields via AMDGPU register helpers, command streams, debug/profiling setup, or low-level shader/packet metadata. They are also used when decoding register dumps or performance counter selections into named hardware events.

## Important APIs, Types, And Constants

This header defines preprocessor constants and many named C enum types. It has no functions, structs, callbacks, allocations, or exported symbols.

### Color Buffer And Render Target Values

The opening enum families describe color-buffer state and render-target behavior:

- `SurfaceNumber`, `SurfaceSwap`, `CBMode`, `RoundMode`, and `SourceFormat` define numeric format interpretation, component swap, color-buffer operation mode, rounding behavior, and shader export format.
- `BlendOp`, `CombFunc`, and `BlendOpt` define blend factors, blend combine functions, and hardware blend optimization conditions.
- `CmaskCode` and `CmaskAddr` describe CMASK clear/compression encodings and addressing modes.
- `CBPerfSel`, `CBPerfOpFilterSel`, and `CBPerfClearFilterSel` select color-buffer performance events and filters. `CBPerfSel` is large and includes cache hits/misses/stalls, MC read/write traffic, DCC key/compression ratio events, blend optimization events, RBP split events, fast-clear and decompression events, and color-cache pipeline occupancy signals.

These values are consumed by render-target setup, fast clear/decompress paths, command buffer construction, and performance/debug tooling. Incorrect values can silently produce valid-looking MMIO writes that program the wrong render-target mode or counter event.

### Command Processor And Address-Space Metadata

The CP-related enum families define ring, pipe, micro-engine, and performance-monitoring selectors:

- `CP_RING_ID`, `CP_PIPE_ID`, and `CP_ME_ID` encode command processor ring/pipe/ME instance IDs.
- `SPM_PERFMON_STATE`, `CP_PERFMON_STATE`, and `CP_PERFMON_ENABLE_MODE` define performance monitor state transitions and enable modes.
- `CPG_PERFCOUNT_SEL`, `CPF_PERFCOUNT_SEL`, and `CPC_PERFCOUNT_SEL` define performance counter events for the graphics command processor front end, prefetch/front-end path, and command processor control path.
- `CP_ALPHA_TAG_RAM_SEL` selects CP tag RAMs.

The adjacent macros define queue and context constants: semaphore outcomes, interrupt queue messages and interrupt types, VMID size, and register address-space ranges such as `CONFIG_SPACE_START/END`, `UCONFIG_SPACE_START/END`, `PERSISTENT_SPACE_START/END`, and `CONTEXT_SPACE_START/END`. These constants describe register address windows and queue message encodings rather than storing software state.

### Depth, Stencil, Raster, And Pipeline Counters

The DB/PA/SC section defines values for depth/stencil control and geometry/raster performance monitoring:

- `ForceControl`, `ZSamplePosition`, `ZOrder`, `ZpassControl`, `ZModeForce`, `ZLimitSumm`, `CompareFrag`, `StencilOp`, `ConservativeZExport`, and `DbPSLControl` encode depth/stencil compare, stencil operations, early/late/re-Z behavior, Z-pass query units, and conservative Z export policy.
- `PerfCounter_Vals` is the DB performance selector enum. It includes tile/quad sends, stalls, cache hits/misses/flushes, pre-Z/post-Z sample pass/fail counts, depth/stencil cache signals, tile/squad launch signals, op pipe activity, memory interface stalls, and compression/decompression counters.
- `RingCounterControl`, `PixelPipeCounterId`, and `PixelPipeStride` define query/counter ring selection, pixel pipe counter IDs, and counter stride.
- `GB_EDC_DED_MODE` and the `GB_TILING_CONFIG_*` macros describe graphics-block double-error handling and tiling table sizes.
- `GRBM_PERF_SEL` and `GRBM_SE0_PERF_SEL` through `GRBM_SE3_PERF_SEL` select global or per-shader-engine graphics register bus manager events such as CP/CB/DB/PA/SC/SPI/SX/TA/VGT/RLC/TC/CPF/CPC/CPG busy/clean states.
- `SU_PERFCNT_SEL` and `SC_PERFCNT_SEL` are large geometry/raster performance selector enums covering primitive input/output, clip/cull results, shader-engine-specific primitive activity, scissor/bounding-box discard, tile and supertile histograms, quad coverage histograms, HiZ/detail quads, PS arbitration, PA/SC FIFO activity, EOP/event/dealloc handshakes, and backend/SCB busy conditions.

These values are diagnostic and profiling surfaces. They do not implement profiling logic by themselves; surrounding code must program counter select registers, start/stop perfmon, and sample data registers correctly.

### Raster Configuration Maps

`SePairXsel`, `SePairYsel`, `SePairMap`, `SeXsel`, `SeYsel`, `SeMap`, `ScXsel`, `ScYsel`, `ScMap`, `PkrXsel2`, `PkrXsel`, `PkrYsel`, `PkrMap`, `RbXsel`, `RbYsel`, `RbXsel2`, and `RbMap` name small routing/map fields used by raster configuration registers. They select tile widths, shader-engine mapping, scan converter mapping, packer mapping, and render-backend mapping.

These values tie software configuration to physical graphics-block topology. A wrong enum value can route work to the wrong SE/SC/PKR/RB layout or produce mismatched tile distribution.

### SPI, Shader Processor, Texture, And Resource Values

The SPI/SQ/TEX/TVX section describes shader input/export, resource descriptors, texture samplers, thread tracing, and shader core performance events:

- `CSDATA_TYPE` and the `CSDATA_*_WIDTH` macros describe context-save data type/address/data widths.
- `SPI_SAMPLE_CNTL`, `SPI_FOG_MODE`, and `SPI_PNT_SPRITE_OVERRIDE` encode shader interpolation/sample/fog and point-sprite override choices.
- `SPI_PERFCNT_SEL` selects shader processor interface events for VS/GS/ES/HS/LS/CS/PS wave windows, wave allocation, crawler stalls, resource allocation failures, LDS/VGPR/SGPR/barrier limits, export arbitration, clock gating, and export counts.
- `SPI_SHADER_FORMAT` and `SPI_SHADER_EX_FORMAT` encode shader export component formats.
- `CLKGATE_SM_MODE` and `CLKGATE_BASE_MODE` define clock-gating sequencer modes.
- `SQ_TEX_*`, `SQ_RSRC_*`, `SQ_IMG_FILTER_TYPE`, `SQ_SEL_XYZW01`, `SQ_WAVE_TYPE`, and `SQ_THREAD_TRACE_*` define texture clamp/filter/mip/aniso/depth compare/border options, buffer/image/flat resource descriptor types, component selection, wave type, thread trace token types, trace instruction/reg categories, trace capture mode, VM/wave masks, issue categories, and issue masks.
- `SQ_PERF_SEL` is a large shader queue/performance selector enum. It covers waves, busy cycles, instruction classes, waits, memory instruction levels, IFETCH, branch fork, LDS conflicts, VMEM/SMEM/flat replay, SQC instruction/data cache events, GATCL1 translation/permission misses, ATC/XNACK events, TLB shootdowns, user counters, and power-related counters.
- `SQ_CAC_POWER_SEL`, `SQ_IND_CMD_CMD`, `SQ_IND_CMD_MODE`, `SQ_EDC_INFO_SOURCE`, `SQ_ROUND_MODE`, `SQ_INTERRUPT_WORD_ENCODING`, and `ENUM_SQ_EXPORT_RAT_INST` define power model selectors, indirect SQ commands, indirect command broadcast modes, EDC source IDs, floating-point rounding, interrupt encoding, and export/RAT operations.
- `SQ_IBUF_ST`, `SQ_INST_STR_ST`, `SQ_WAVE_IB_ECC_ST`, `SH_MEM_ADDRESS_MODE`, `SH_MEM_ALIGNMENT_MODE`, and `SQ_THREAD_TRACE_WAVE_START_COUNT_PREFIX` define SQ instruction-buffer state, instruction stream state, ECC state, shader memory mode, alignment mode, and thread-trace wave start prefixes.

This block bridges graphics and compute execution with shader-debug/profiling tooling. Many values are valid only for specific register fields or instruction encodings despite sharing the `SQ_` prefix.

### Shader Instruction Encoding Macros

Starting around line 2728, the chunk switches from enum typedefs to many `#define` constants for GFX8 shader instruction encoding and register numbering:

- SQ register windows and decoder ranges: `SQIND_*`, `SQ_GFXDEC_*`, `SQDEC_*`, `SQPERFSDEC_*`, `SQPERFDDEC_*`, `SQGFXUDEC_*`, and `SQPWRDEC_*`.
- Limits and field layout: `SQ_MAX_PGM_SGPRS`, `SQ_MAX_PGM_VGPRS`, `SQ_NUM_ATTR`, `SQ_NUM_VGPR`, `SQ_NUM_SGPR`, `SQ_NUM_TTMP`, `SQ_WAITCNT_*`, `SQ_HWREG_*`, `SQ_SENDMSG_*`, and VOP translation table offsets/counts.
- Instruction encoding masks/fields: `SQ_ENC_SOP1`, `SQ_ENC_SOPC`, `SQ_ENC_SOPP`, `SQ_ENC_SOPK`, `SQ_ENC_SOP2`, `SQ_ENC_SMEM`, `SQ_ENC_VOP1`, `SQ_ENC_VOPC`, `SQ_ENC_VOP2`, `SQ_ENC_VINTRP`, `SQ_ENC_VOP3`, `SQ_ENC_DS`, `SQ_ENC_MUBUF`, `SQ_ENC_MTBUF`, `SQ_ENC_MIMG`, `SQ_ENC_EXP`, and `SQ_ENC_FLAT` bit/mask/field constants.
- Opcode names for scalar, vector, data-share, buffer, image, flat, comparison, interpolation, send-message, hardware register, DPP, and export operations. Examples include `SQ_S_MOV_B32`, `SQ_S_LOAD_DWORDX4`, `SQ_V_CMP_LT_F32`, `SQ_DS_ADD_U32`, `SQ_BUFFER_ATOMIC_ADD`, `SQ_IMAGE_SAMPLE`, `SQ_FLAT_LOAD_DWORD`, `SQ_V_ADD_F32`, `SQ_V_MAD_F32`, and `SQ_MSG_SYSMSG`.
- Special source and destination encodings: `SQ_TBA_*`, `SQ_TMA_*`, `SQ_TTMP*`, `SQ_EXEC_*`, `SQ_VCC_ALL`, `SQ_SRC_*`, `SQ_SGPR0`, `SQ_VGPR0`, `SQ_M0`, and `SQ_HW_REG_*`.

These definitions can be used by disassembly, debug, trap, thread-trace, shader setup, or command generation paths. They are not generic opcodes for all AMD GPU generations; their numeric values are tied to the GFX8.1 ISA/register database.

### SX, Texture, Vertex, TVX, TC, And TCC Values

The last portion of this chunk returns to enum typedefs for export, texture/vertex descriptors, texture/vertex fetch instructions, texture-cache operations, and TCC performance events:

- `SX_BLEND_OPT`, `SX_OPT_COMB_FCN`, and `SX_DOWNCONVERT_FORMAT` define shader export/blend optimization and render-target down-conversion formats.
- `TEX_BORDER_COLOR_TYPE`, `TEX_CHROMA_KEY`, `TEX_CLAMP`, `TEX_COORD_TYPE`, `TEX_DEPTH_COMPARE_FUNCTION`, `TEX_DIM`, `TEX_FORMAT_COMP`, `TEX_MAX_ANISO_RATIO`, `TEX_MIP_FILTER`, `TEX_REQUEST_SIZE`, `TEX_SAMPLER_TYPE`, `TEX_XY_FILTER`, and `TEX_Z_FILTER` describe texture sampler/resource descriptor values.
- `VTX_CLAMP`, `VTX_FETCH_TYPE`, `VTX_FORMAT_COMP_ALL`, and `VTX_MEM_REQUEST_SIZE` describe vertex fetch behavior.
- `TVX_DATA_FORMAT`, `TVX_DST_SEL`, `TVX_ENDIAN_SWAP`, `TVX_INST`, `TVX_NUM_FORMAT_ALL`, `TVX_SRC_SEL`, `TVX_SRF_MODE_ALL`, and `TVX_TYPE` define texture/vertex fetch data formats, swizzles, endian swaps, instruction types, numeric formats, SRF modes, and resource validity/type.
- `TC_OP_MASKS`, `TC_OP`, `TC_CHUB_REQ_CREDITS_ENUM`, `CHUB_TC_RET_CREDITS_ENUM`, and `TC_NACKS` define texture-cache operation modifiers, read/write/cache invalidate/writeback/atomic operation encodings, credit constants, and no-fault/page/protection/data-error NACK causes.
- `TCC_PERF_SEL` begins at line 4576 and defines TCC cache/performance events through `TCC_PERF_SEL_CLIENT68_REQ` at the chunk end. Covered events include cycle/busy/request classes, compressed/metadata/non-cacheable/uncached/coherent request classes, read/write/atomic/hit/miss/writeback/evict/latency FIFO/tag/probe stalls, MC request/return/NACK behavior, TC cache operation writeback/evict/cycle/start/finish events, MDC events, probe filter state, and client request events 0-68.

The `TCC_PERF_SEL` enum is incomplete in this chunk. The final merged report should stitch the next chunk before treating the TCC selector list as complete.

## Control Flow

There is no runtime control flow in this chunk. The header contains C enum declarations and `#define` constants only. It has no loops, branches, functions, reads, writes, locking, allocation, error handling, or callbacks.

The implied runtime flow is:

1. GFX 8.1-specific or shared GFX8 AMDGPU/KFD code includes the appropriate register offset, shift/mask, and enum headers.
2. Driver code selects a register offset and field mask/shift from the sibling headers.
3. Driver code chooses one of these enum or macro values for the field payload.
4. The value is shifted/masked into an MMIO register write, packet field, shader/debug encoding, or decode table.
5. Hardware interprets the numeric value as a mode, operation, routing selector, instruction opcode, cache command, or performance event.

Any sequencing, ordering, polling, latching, privilege checks, timeout handling, cache flush rules, or context-save/restore behavior is implemented by surrounding driver code and hardware, not by this header.

## State And Persistence Behavior

The header itself stores no mutable software state and persists nothing. It describes hardware-visible state and encodings:

- Render-target, blend, depth/stencil, raster configuration, texture, vertex, and resource values persist in hardware context registers or command-stream state until reprogrammed, context-switched, reset, or restored.
- Performance counter selectors persist as programmed counter configuration until perfmon state changes, reset, or another selector write.
- Counter data and status registers selected by these values are hardware-updated while counters or engines are active; sampling coherency is the caller's responsibility.
- Shader instruction opcode/register constants describe encoded instruction words or debug/trap state, not driver-owned memory.
- Cache, memory, semaphore, atomic, thread-trace, SQ indirect command, and TC operation values can have direct side effects when written to the corresponding command/register fields.
- Address-space range constants define GFX register windows. They are used for classification and validation; they do not reserve memory by themselves.

Reserved values and generation-specific values should not be reused casually. Even when two generations share names, the numeric field or full enum coverage can differ.

## Dependencies And Integration Points

Primary file-level dependencies are the generated GFX 8.1 register headers in the same directory:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_1_d.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_1_sh_mask.h`

Related GFX8 infrastructure in this tree includes `amdgpu/gfx_v8_0.c`, `amdgpu/gfx_v8_0.h`, `amdgpu/vi.c`, and `amdgpu/amdgpu_amdkfd_gfx_v8.c`. In the inspected tree, those files include the GFX 8.0 generated headers directly; no direct include of `gca/gfx_8_1_enum.h` was found by text search. The GFX 8.1 IP block is still part of VI-era device setup for ASICs such as Stoney through `gfx_v8_1_ip_block`, so this header is best understood as an ASIC-specific register database available to the same low-level AMDGPU/KFD register programming layer.

Likely integration surfaces are:

- Register programming helpers such as SOC15/VI MMIO accessors and bitfield helpers that combine offsets, masks, shifts, and enum payloads.
- Command processor/ring setup, queue management, semaphore/fence/wait, CP DMA, and indirect command paths.
- Render-target clear/decompress, color/depth/stencil setup, raster configuration, tiling, and context-state programming.
- Shader trap/debug/thread-trace/disassembly paths that need SQ instruction encodings, hardware register IDs, wave state, and trace token categories.
- KFD/compute queue and shader memory mode setup where GFX8 address, alignment, trap, wave, and queue constants are relevant.
- Profiling and debugfs/perf tooling that programs CB, CP, DB, GRBM, SU, SC, SPI, SQ, TC, and TCC performance selectors.
- Register dump and diagnostics code that decodes hardware values into names or compares generated values against expected ASIC tables.

## Risks And Edge Cases

- Numeric drift is the main risk. These constants compile cleanly even if wrong, but a wrong value can program a different hardware mode, opcode, counter event, cache operation, or route.
- The chunk boundary is artificial and cuts `TCC_PERF_SEL` in half. Any final per-file summary must not treat the TCC selector enum as complete until the following chunk is merged.
- GFX8.1 values are close to, but not guaranteed identical to, GFX8.0 or later GC enum values. Reusing constants across ASIC families can produce subtle register programming bugs.
- Many enum names are broad (`SQ_*`, `TC_OP_*`, `TEX_*`) but are valid only in specific fields. Using a value with a similarly named but different field is not type-safe at runtime because the register write ultimately receives an integer.
- Performance counter values are dense and repeated across blocks. A selector mismatch can return plausible but wrong performance data, which is hard to catch without controlled workloads.
- Shader instruction opcode constants share names with ISA mnemonics but are raw encoding fields. Incorrect encoding tables affect disassembly, trace interpretation, trap/debug handling, or generated shader/control packets.
- Cache, TC, TCC, SQC, GDS, atomic, semaphore, SQ indirect command, and thread-trace values can trigger side effects when used in command/register programming. This header does not encode required ordering, barriers, timeout policy, or ownership checks.
- Address-space constants such as config/context/persistent ranges are hardware register windows. Treating them as normal memory ranges or using the wrong window for validation can misclassify MMIO access.
- Raster routing and render-backend map values are topology-sensitive. Wrong SE/SC/PKR/RB mapping can affect only certain ASIC configurations, render target counts, or multi-SE workloads.
- Reserved enum values are present throughout the file. Writing reserved values may be ignored, undefined, or harmful depending on the target register.

## Test And Validation Signals

Useful validation combines generated-header checks, compile coverage, and hardware/runtime tests:

- Build AMDGPU and KFD code paths that include GFX8 generated headers. Missing or renamed constants should fail at compile time where the header is actually consumed.
- Mechanically compare `gfx_8_1_enum.h` against AMD's authoritative GFX 8.1 register/ISA database, including enum completeness, numeric values, reserved slots, and sibling `gfx_8_1_d.h`/`gfx_8_1_sh_mask.h` consistency.
- Run static checks for monotonic or repeated performance selector ranges in `CBPerfSel`, `PerfCounter_Vals`, `SU_PERFCNT_SEL`, `SC_PERFCNT_SEL`, `SPI_PERFCNT_SEL`, `SQ_PERF_SEL`, and the covered part of `TCC_PERF_SEL`.
- Exercise render-target, blend, fast-clear, DCC/CMASK/FMASK/decompress, depth/stencil, early/late-Z, MSAA, texture sampling, vertex fetch, and context save/restore workloads on matching GFX 8.1 hardware or simulation.
- Exercise CP/KFD queue, semaphore, wait, fence, CP DMA, indirect buffer, trap, and shader memory mode paths where GFX8.1 is supported.
- Validate shader debug and trace paths by collecting thread traces, decoding wave/instruction/register state, and checking that opcode/register constants match observed hardware output.
- Validate profiling by programming CB, CP, DB, GRBM, SU, SC, SPI, SQ, TC, and TCC selector registers with controlled workloads. Expected counters should move only for the intended event families.
- Exercise cache and memory operations, especially SQC/TC/TCC invalidate/writeback/atomic/NACK-related paths, and watch for stale data, hangs, unexpected page/protection fault decoding, or lost completion events.
- For raster map/topology values, validate on hardware configurations that expose the relevant SE/SC/PKR/RB routing rather than only a single minimal device.

## Cross-Chunk Notes

This chunk begins at the file start and contains complete definitions through most of the texture/vertex/TC section. It ends mid-`TCC_PERF_SEL` at line 4,753. The next chunk must provide the remaining TCC client selectors and the closing brace before the final per-file report describes the full TCC selector enum.

### subset-b-002720: lines 4754-6808

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
