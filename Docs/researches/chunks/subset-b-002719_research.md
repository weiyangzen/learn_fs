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
