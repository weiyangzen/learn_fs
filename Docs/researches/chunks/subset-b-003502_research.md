# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h lines 14961-20490

## Scope And Purpose

This chunk is a large section of AMD's generated SOC24 enum header. It contains C `typedef enum` value tables only; it does not define executable functions, structs with storage, global variables, locks, allocations, or direct MMIO operations.

The values are a compile-time ABI between AMDGPU code and SOC24/GC 12-era hardware register fields, command packets, state descriptors, and performance-counter muxes. Companion register offset and shift/mask headers define where fields live; this file defines the legal symbolic values that may be written into those fields or decoded from them.

The range starts in the middle of `PH_PERFCNT_SEL`, covers many complete graphics/raster/shader/cache/texture/depth enum domains, and ends in the middle of `SU_PERFCNT_SEL`. Final per-file reconciliation should merge the adjacent chunks before making complete claims about those two boundary enums.

## Major Enum Groups

### Primitive Hub, Raster, And Scan Converter

The first part closes the tail of `PH_PERFCNT_SEL`. The covered values continue the per-scan-converter/per-primitive-assembler matrix for `SC3` through `SC7`, including PA FIFO reads/writes, empty/full status, null/event/FPOV/FPOP/EOP/EOPG/dealloc writes, arbiter stalls/starvation/busy, send credit states, graphics-pipe transitions, and `PH_PERF_SC*_FIFO_STATUS_*` selectors. This enum began before the chunk and has 1,024 total values, of which 592 are in this range.

Small primitive/raster configuration enums follow:

- `PhSPIstatusMode` selects PH-to-SPI status reporting by largest PA/PH FIFO count, arbiter-selected count, or disabled mode.
- `BinEventCntl`, `BinMapMode`, `BinSizeExtend`, and `BinningMode` describe binner event behavior, bin mapping mode, bin dimensions from 32 to 512 pixels, and force/disable/one-primitive-per-batch binning controls.
- `PkrMap`, `PkrXsel`, `PkrXsel2`, `PkrYsel`, `RbMap`, `RbXsel`, `RbXsel2`, `RbYsel`, `ScMap`, `ScXsel`, `ScYsel`, `SeMap`, `SePairMap`, `SePairXsel`, `SePairYsel`, `SeXsel`, and `SeYsel` provide raster-configuration mapping and tile-width selectors for packers, render backends, scan converters, shader engines, and shader-engine pairs.
- `ScUncertaintyRegionMode` and `ScUncertaintyRegionMult` select half-LSB/one-sided/two-sided uncertainty-region behavior and 1x/2x/4x/8x scale.
- `VRSCombinerModeSC` and `VRSrate` encode variable-rate shading combiner behavior and legal shading rates, including 1x1 through 4x4, conservative variants, and SSAA rates.

`SC_PERFCNT_SEL` is a complete 662-value scan-converter performance selector table. It covers SRPS/PSSW windows, tile and supertile flow, scissor/viewport/bounding-box rejection, quad and coarse-pixel activity, clip/cull and rasterization outcomes, HiZ/detail interactions, event/EOP/dealloc handshakes, SC-to-DB/SPI traffic, packer activity, PS wave flow, stalls, busy states, and repeated per-SC/per-PA FIFO status families. Consumers use these values as event IDs for SC performance counter select registers.

### Texture, TCP, TC, And Cache Operation Domains

`TC_EA_CID` names 16 export-address client IDs, including RT, FMASK, DB, UTL, TCP, command processor, SDMA, GCR, CPF, and PA-like clients. `TC_NACKS` describes no-fault, page-fault, protection-fault, and data-error NACK classes.

`TC_OP` is a 128-value operation-code table for texture/cache memory operations. It includes reads, atomics, writes, compare-swap and return/no-return variants, non-temporal and special memory forms, Z export variants, and reserved 64-bit/non-floating encodings. `TC_OP_MASKS` provides bit masks that classify flush-denorm, 64-bit, and no-return operation attributes.

Texture and sampler state enums include `TA_PERFCOUNT_SEL`, `TEX_BC_SWIZZLE`, `TEX_BORDER_COLOR_TYPE`, `TEX_CHROMA_KEY`, `TEX_CLAMP`, `TEX_COORD_TYPE`, `TEX_DEPTH_COMPARE_FUNCTION`, `TEX_FORMAT_COMP`, `TEX_MAX_ANISO_RATIO`, `TEX_MIP_FILTER`, `TEX_REQUEST_SIZE`, `TEX_SAMPLER_TYPE`, `TEX_XY_FILTER`, `TEX_Z_FILTER`, `TVX_TYPE`, `TA_TC_ADDR_MODES`, and `TA_TC_REQ_MODES`. Together they define texture-addressing performance events and legal sampler/resource encodings for border color, chroma keying, clamp behavior, normalized coordinates, depth compare function, signedness, anisotropy, mip/xy/z filtering, request size, resource validity, and TA-to-TC address/request modes.

TCP and GL cache enums include `TCP_CACHE_POLICIES`, `TCP_CACHE_STORE_POLICIES`, `TCP_COMPRESSION_BYPASS`, `TCP_COMPRESSION_OVERRIDE`, `TCP_OPCODE_TYPE`, `TCP_PERFCOUNT_SELECT`, `TCP_WATCH_MODES`, `TCP_WRITE_COMPRESSION_DISABLE`, `TD_PERFCOUNT_SEL`, `GL1A_PERF_SEL`, `GL1C_PERF_SEL`, `GL1XA_PERF_SEL`, `GL1XC_PERF_SEL`, `GL2A_PERF_SEL`, and `GL2C_PERF_SEL`. These encode L0/L1/L2 cache request classes, compression controls, watchpoint modes, texture data events, GL1/GL2 busy/stall/miss/hit/invalidating/request/return-credit activity, and per-client GL2 observations.

### SPI, SQ, PC, GRBMH, And Shader State

`PC_PERFCNT_SEL` is a 165-value primitive-assembler/parameter-cache selector table covering SC-to-PC pointer sends/valids, index and parameter-cache activity, vertex/primitive status, wave and work-launch counters, visibility and boundary-crossing events, and related busy or stall points.

SPI enums cover both state encoding and performance measurement:

- `SPI_FOG_MODE`, `SPI_LB_WAVES_SELECT`, `SPI_PNT_SPRITE_OVERRIDE`, `SPI_PS_LDS_GROUP_SIZE`, `SPI_SAMPLE_CNTL`, `SPI_SHADER_EX_FORMAT`, and `SPI_SHADER_FORMAT` define fog mode, late-branch wave selection, point-sprite coordinate override, PS LDS grouping, sample source, shader export format, and shader component count encodings.
- `SPI_PERFCNT_SEL` is a 284-value SPI selector table for shader-stage window validity, busy/idle states, wave launches, interpolator and parameter-cache activity, LDS/VGPR allocation, barrier and scoreboard behavior, stalls, wave limits, and RA request/allocation observations.

SQ and SQG enums include `SH_MEM_ADDRESS_MODE`, `SH_MEM_ALIGNMENT_MODE`, `SQG_PERF_SEL`, `SQ_CAC_POWER_SEL`, `SQ_EDC_INFO_SOURCE`, `SQ_IBUF_ST`, `SQ_IMG_FILTER_TYPE`, `SQ_IND_CMD_CMD`, `SQ_IND_CMD_MODE`, `SQ_INST_STR_ST`, `SQ_INST_TYPE`, `SQ_LLC_CTL`, `SQ_NO_INST_ISSUE`, `SQ_OOB_SELECT`, `SQ_PERF_SEL`, `SQ_ROUND_MODE`, `SQ_RSRC_BUF_TYPE`, `SQ_RSRC_FLAT_TYPE`, `SQ_RSRC_IMG_TYPE`, `SQ_SEL_XYZW01`, `SQ_TEX_ANISO_RATIO`, `SQ_TEX_BORDER_COLOR`, `SQ_TEX_CLAMP`, `SQ_TEX_DEPTH_COMPARE`, `SQ_TEX_MIP_FILTER`, `SQ_TEX_XY_FILTER`, `SQ_TEX_Z_FILTER`, `SQ_WATCH_MODES`, `SQ_WAVE_FWD_PROG_INTERVAL`, `SQ_WAVE_SCHED_MODES`, and `SQ_WAVE_TYPE`.

These values describe shader memory modes, alignment modes, global SQ performance events, CAC power attribution, EDC info sources, instruction-buffer state, image filter modes, indirect halt/resume/debug command modes, instruction classes, issue-block reasons, out-of-bounds behavior, rounding modes, resource descriptor types, component swizzles, texture filtering/clamping/depth compare fields as seen by SQ, watchpoint classes, wave progress intervals, scheduling modes, and wave types. `SQ_PERF_SEL` is the largest complete shader selector in this chunk, with 382 values spanning wave/instruction issue, stalls, LDS/VGPR/SGPR pressure, cache/memory behavior, branch and wait states, and scalar/vector/matrix activity.

`GRBMH_PERF_SEL` provides GRBMH-side selector values for count/user-defined and graphics/compute front-end, command, GE, and RLC busy states.

### SX, DB, Pixel Pipe, And Depth/Stencil State

SX enums include `SX_BLEND_OPT`, `SX_DOWNCONVERT_FORMAT`, `SX_OPT_COMB_FCN`, and `SX_PERFCOUNTER_VALS`. They define color blend optimization behavior, render-target export down-conversion formats, optimization-combine functions, and SX counter events for PA/SPI/SX/CB/DB interactions, exports, stalls, wave lifetimes, discard cases, and end-of-wave signals.

Depth/stencil and DB state enums include `CompareFrag`, `ConservativeZExport`, `DbMemArbWatermarks`, `DbPRTFaultBehavior`, `DbPSLControl`, `ForceControl`, `GLCompressionMode`, `OreoMode`, `StencilOp`, `ZLimitSumm`, `ZModeForce`, `ZOrder`, and `ZSamplePosition`. These values encode fragment compare functions, conservative Z-export promises, DB memory-arbiter watermark sizes, PRT fault result behavior, PSL control, force enable/disable/default behavior, GL compression/bypass modes, OREO ordering, stencil operations, Z-limit summary forcing, early/late/re-Z forcing, Z test ordering, and center/centroid sample position selection.

`PerfCounter_Vals` is the DB performance selector enum. Its 384 values cover SC-to-DB tile/quad/wave traffic, depth/stencil cache hits and misses, tile and quad stalls, Z/stencil read/write paths, pre-Z/post-Z sample and quad pass/fail counts, compression/decompression and fast-clear paths, HiZ/HiS behavior, SX/DB export formats, RMI request/return/ack traffic, VRS rates, PWS stalls, OREO table/cache events, and backend conflict or liveness stalls.

`PixelPipeCounterId`, `PixelPipeStride`, and `RingCounterControl` describe pixel-pipe counter selection and result layout: occlusion count slots, screen min/max extent counters, 32/64/128/256-bit strides, and split/ring-0/ring-1 counter routing.

### SU Boundary Enum

The chunk begins `SU_PERFCNT_SEL` at line 20281 and includes its first 209 selector values through `PERF_PH_SEND_4_SC` at line 20490. The enum continues after this chunk to line 20530. Covered values include PA/clip/SU primitive input and output counts, null/event/EOP flags, clipping and culling reasons, PASX/CLPR/CLIP/SU busy-starved-stalled state, per-shader-engine primitive-filter/output/null/stalled counters for SE0 through SE5, small-primitive culling histograms, SC qualified-send busy/not-busy events, PA FIFO-full signals, ENGG CSB/index/position request/return stalls, GE/SPI memory full/empty state, and PH send/output primitive counts for up to four scan converters.

## Important APIs And Integration Points

The API surface is the enum type and enumerator namespace:

- `typedef enum <Name> { ... } <Name>;` creates a C enum type for register field values or performance event IDs.
- Individual enumerators, such as `SC_SRPS_WINDOW_VALID`, `TC_OP_READ`, `SPI_PERF_GS_BUSY`, `SQ_PERF_SEL_NONE`, `DB_PERF_SEL_SC_DB_tile_sends`, `STENCIL_KEEP`, and `PERF_PAPC_SU_OUTPUT_PRIM`, are the constants consumers pass into register programming paths.

These definitions integrate with AMDGPU register programming for SOC24/GC 12 hardware. Typical consumers are graphics initialization, command/state packet construction, performance counter selection, debugfs/perf tooling, shader debugging, cache/watchpoint setup, raster/binning/VRS setup, texture/sampler descriptor programming, DB/SX state programming, and RAS/EDC diagnostics. In-tree users generally combine these enum values with companion files such as GC register offset headers, shift/mask headers, generated packet definitions, and AMDGPU helpers for `RREG32`, `WREG32`, `REG_SET_FIELD`, `REG_GET_FIELD`, SOC15 register offsets, and command processor packet emission.

The path sits under a `ceph-client` source mirror, but the file is AMDGPU DRM hardware metadata, not Ceph distributed-filesystem logic.

## Control Flow

There is no runtime control flow in this chunk. Runtime behavior appears in code that selects one of these values and writes it into a hardware field, command stream packet, performance counter select register, or resource descriptor.

The implied control flow for a performance-counter user is:

1. Choose the hardware block and counter register, such as SC, SPI, SQ, TCP, GL1, GL2, SX, DB, PH, PC, TD, TA, or SU.
2. Write an enum value from the matching selector table into that block's event-select field.
3. Enable, sample, stop, and read the hardware counter through the block-specific performance-monitoring sequence.
4. Decode the result using the same enum domain so profiling tools can label the event correctly.

The implied control flow for state programming is to map a driver-visible state, API state, or command-stream packet field onto the corresponding enum value, pack it into the register or descriptor field using generated masks/shifts, and submit or write it through AMDGPU's normal register or ring path.

## State And Persistence Behavior

This header persists no software state. It describes values for stateful hardware registers, packets, descriptors, counters, and debug/status paths. Persistence is therefore owned by the hardware block and the driver code that programs or restores it.

State represented by this chunk includes raster/binning/VRS modes, shader export and sample modes, memory and cache policy bits, texture sampler and resource descriptor fields, shader debug/indirect command controls, watchpoint modes, DB/SX/Z/stencil policy, pixel-pipe counter selection, and many performance counter mux selections.

Performance counter select values remain in their hardware select fields until overwritten, reset, power-gated, or restored during GPU reset and suspend/resume handling. State descriptor values may live in command streams or GPU memory descriptors rather than MMIO registers. Some enum domains represent read-only status decodes or event classes rather than writable control state. This header does not encode access permissions, reset values, sticky behavior, or side effects.

## Dependencies

The chunk depends on the surrounding generated AMDGPU hardware-description set:

- Companion SOC24/GC register offset headers provide addresses for registers that consume these values.
- Shift/mask headers define bit positions for fields whose legal values are named here.
- Command processor packet and resource descriptor definitions define where state values are embedded in command streams or descriptors.
- AMDGPU KMS, Mesa/userspace-facing state translation, KFD, debug/perf tooling, and RAS/EDC code may rely on matching numeric values when programming hardware or decoding diagnostics.

Generated naming and numeric encodings are the contract. Renaming an enumerator breaks compile-time users; changing a numeric value can compile cleanly but program a different hardware behavior or count a different event.

## Risks And Edge Cases

- Boundary incompleteness: `PH_PERFCNT_SEL` starts before this range and `SU_PERFCNT_SEL` ends after it. A merged report must account for the missing starts/ends before treating them as complete enums.
- Event-selector drift: large tables such as `SC_PERFCNT_SEL`, `SPI_PERFCNT_SEL`, `SQ_PERF_SEL`, `PerfCounter_Vals`, `TA_PERFCOUNT_SEL`, `TD_PERFCOUNT_SEL`, `GL2C_PERF_SEL`, and `SU_PERFCNT_SEL` are dense. One inserted, deleted, or renumbered value can silently make profiling or debug data misleading.
- Cross-block namespace similarity: many blocks expose similarly named busy, stall, FIFO, read, write, hit, miss, and wave events. Using an enum value from the wrong block may still fit the field width while selecting an unrelated event.
- Hardware generation specificity: these SOC24 values should not be assumed valid for older SOC15/SOC21/Navi/Vega headers unless the generated database shows exact compatibility.
- Side-effectful debug controls: `SQ_IND_CMD_CMD` and `SQ_IND_CMD_MODE` include halt, resume, fatal-halt, and single-step controls. Incorrect use can disrupt running waves or leave shader hardware in a debug state.
- Memory/cache policy hazards: TC/TCP/GL/cache operation, compression, and address-mode enums affect memory ordering, compression, eviction, and fault behavior. Bad values can create data corruption, missed faults, or severe performance regressions.
- Rendering correctness hazards: VRS, binning, raster map, texture filtering, Z/stencil, conservative Z, blend optimization, down-conversion, and compression enums directly affect rendered output. Incorrect mappings may only show under specific formats, sample counts, VRS rates, or depth/stencil state combinations.
- Status-vs-control ambiguity: some domains name status or event IDs rather than writable controls. Consumers need the companion register spec to know whether a field is writable, read-only, sticky, self-clearing, or packet-only.

## Test Signals

Useful validation signals for consumers of this chunk include:

- Build coverage for SOC24/GC 12 AMDGPU code paths that include `soc24_enum.h`, catching missing or renamed enum symbols.
- Mechanical comparison against AMD's authoritative generated register database, especially numeric monotonicity and intentional gaps in large performance selector tables.
- Perf-counter smoke tests for SC, PH, SPI, SQ/SQG, PC, TA/TD/TCP, GL1/GL2, SX, DB, and SU blocks, verifying that selected events respond to workloads designed to exercise the named block.
- Rendering conformance tests covering VRS rates/combiners, binning modes, raster maps, texture clamp/filter/depth-compare modes, blend optimization/down-conversion, Z ordering, stencil operations, conservative Z export, and compression controls.
- Shader debug tests that exercise SQ indirect halt/resume/single-step commands only in controlled debug paths and verify waves recover.
- Cache and memory tests that cover TC/TCP operation classes, watch modes, compression bypass/override, cache policy, write compression disable, fault/NACK decoding, and address/request modes.
- GPU reset and suspend/resume tests that verify hardware state or descriptor programming using these values is restored or intentionally reinitialized.
- Cross-generation compile and runtime checks that ensure SOC24-specific enum values are not accidentally reused by incompatible ASIC families.

## Cross-Chunk Notes

Lines 14961-15553 are the tail of `PH_PERFCNT_SEL`; the first PH selector values are in the previous chunk. Lines 20281-20490 are the start and majority of `SU_PERFCNT_SEL`; the remaining SU selector values and the next `RMIPerfSel` enum begin after this chunk. The final merged file-level research should reconcile these boundaries before summarizing complete enum sizes.
