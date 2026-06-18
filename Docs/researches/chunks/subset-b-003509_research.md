# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vega10_enum.h lines 15209-21528

## Scope

This chunk covers the middle of the generated Vega10 AMDGPU enum header. It starts at shader-queue address-window and SQ constant definitions and ends inside the `RMIPerfSel` enum, after RMI/RB read-return counter selectors through `RMI_PERF_SEL_RMI_RB_32BRDRET_VALID_CID4`. The `RMIPerfSel` enum continues in the next chunk, so the RMI section is intentionally incomplete here.

The covered families are:

- SQ address windows, dispatcher limits, exception IDs, wait-count bit partitions, EDC controls, shader instruction encoding/opcode constants, special registers, send-message encodings, and target/format selectors.
- COMP `CSDATA_TYPE` constants for typed command-stream/debug data.
- VGT, IA, and WD primitive, draw-source, tessellation, pipeline-stage, event, and performance-counter selectors.
- GB, TA, TD, TCP, TCC, and TCA enums for tiling-table sizing, texture addressing, cache policy, watch/data selector modes, and texture/cache performance counters.
- GRBM and CP enums for global graphics block performance selectors, per-shader-engine GRBM selectors, command-processor ring/pipe/ME IDs, perfmon state, and command-processor microblock counters.
- SX and DB enums for blend optimization, color downconversion, depth/stencil behavior, DB/SX performance counters, ring counters, memory arbitration watermarks, DFSM flush events, and pixel-pipe counters.
- Texture and vertex fetch enums for sampler border/clamp/filter/dimension/format controls, texture/vertex data formats, swizzle source/destination selectors, endian swap, fetch instructions, numeric formats, and SRF/type modes.
- SU and SC performance-counter selector enums plus raster-routing/binning enums for shader engine, scan converter, packer, render backend, primitive binning, and coverage-to-shader selection.
- The beginning of RMI performance selectors for invalidation, UTCL1, and RB/RMI write/read request and return traffic.

This chunk is generated hardware-interface data. It contains `#define` constants and `typedef enum` declarations only. There are no C functions, no data structures with storage, no dynamic allocation, and no executable control flow.

## Purpose

`vega10_enum.h` provides symbolic names for numeric encodings used by Vega10 graphics, shader, cache, texture, command processor, raster, depth/color, and memory-interface blocks. The constants are an ABI between AMDGPU code and the hardware register fields, packet fields, shader/debug tools, and performance-monitor programming interfaces that expect exact numeric values.

The definitions let consumers use names such as `DI_PT_TRILIST`, `CACHE_FLUSH_AND_INV_TS_EVENT`, `SQ_OP_MUBUF`, `TEX_DIM_2D`, `CP_RING_ID_COMPUTE`, `SC_PBB_BUSY`, or `RMI_PERF_SEL_UTCL1_TRANSLATION_MISS` instead of embedding raw integers. That matters because most values are register-field encodings rather than independent software policy choices; changing a value changes what the hardware is asked to do or what event a counter measures.

## Important APIs, Types, and Constants

### SQ and Shader Instruction Constants

The chunk begins with SQ decode and performance decode address ranges such as `SQDEC_BEGIN/END`, `SQPERFSDEC_BEGIN/END`, `SQPERFDDEC_BEGIN/END`, `SQGFXUDEC_BEGIN/END`, and `SQPWRDEC_BEGIN/END`. It also defines SQ dispatcher and program-resource limits, including `SQ_DISPATCHER_GFX_MIN`, `SQ_DISPATCHER_GFX_CNT_PER_RING`, `SQ_MAX_PGM_SGPRS`, and `SQ_MAX_PGM_VGPRS`.

SQ exception and wait-count constants define hardware-visible bit positions and exception IDs:

- `SQ_EX_MODE_EXCP_*` maps VALU exception slots such as invalid operation, input denorm, divide-by-zero, overflow, underflow, inexact, integer divide-by-zero, watchpoint, and memory violation.
- `SQ_EX_MODE_EXCP_HI_*` maps additional address-watch exception slots.
- `INST_ID_*` reserves hardware-inserted instruction IDs for ECC interrupt, thread-trace PC, trap, kill sequence, SPI write-exec, and host register trap messages.
- `SIMM16_WAITCNT_*` defines the immediate partitions for VM, EXP, and LGKM wait counts.
- `SQ_EDC_FUE_CNTL_*` names fatal uncorrectable error control sources across SQ, LDS, SIMD lanes, texture address/data, and TCP.

The large `VALUE_SQ_*` block is a generated catalog of shader instruction encodings and operand spaces. It includes encoding class selectors for SOP, SMEM, VOP, VINTRP, DS, MUBUF, MTBUF, MIMG, EXP, and FLAT formats; offset/count constants for translating between VOP3 and VOP1/VOP2/VOPC/VOP3P/VINTRP encodings; register-count limits for VGPR, SGPR, TTMP, and attributes; bitfield sizes and shifts for `waitcnt`, `s_sendmsg`, and `s_setreg`/hardware register operands; opcode values for scalar, vector, LDS/DS, image, buffer, export, flat/global/scratch, interpolation, packed, SDWA, and DPP operations; and special source/destination values such as VCC, EXECZ, SCC, LDS, aperture, XNACK mask, M0, and inline constants.

These SQ values are likely consumed by shader compilation, debug, disassembly, tracing, and register-programming paths that need the Vega10 ISA encodings to match hardware exactly.

### COMP, VGT, IA, and WD

`CSDATA_TYPE` defines command-stream data record classes: thread group, state, event, and private data. The adjacent width constants (`CSDATA_TYPE_WIDTH`, `CSDATA_ADDR_WIDTH`, and `CSDATA_DATA_WIDTH`) define the packed representation size.

The VGT section defines frontend geometry and pipeline values:

- Primitive input/output enums: `VGT_OUT_PRIM_TYPE`, `VGT_DI_PRIM_TYPE`, `VGT_GRP_PRIM_TYPE`, and `VGT_GRP_PRIM_ORDER`.
- Draw/index setup enums: `VGT_DI_SOURCE_SELECT`, `VGT_DI_MAJOR_MODE_SELECT`, `VGT_DI_INDEX_SIZE`, `VGT_DMA_SWAP_MODE`, `VGT_INDEX_TYPE_MODE`, and `VGT_DMA_BUF_TYPE`.
- Pipeline routing and shader-stage enums: `VGT_OUTPATH_SELECT`, `VGT_GS_MODE_TYPE`, `VGT_GS_CUT_MODE`, `VGT_GS_OUTPRIM_TYPE`, `VGT_TESS_TYPE`, `VGT_TESS_PARTITION`, `VGT_TESS_TOPOLOGY`, and the `VGT_STAGES_*_EN` stage selectors.
- Synchronization and event enum `VGT_EVENT_TYPE`, covering cache flushes, partial flushes, streamout events, context done, pipeline statistics, perf counter start/stop/sample, thread trace start/stop/marker/flush/finish, DB/CB invalidation events, NGG/legacy pipeline enable events, and similar command processor event packet encodings.
- `VGT_PERFCOUNT_SELECT`, `IA_PERFCOUNT_SELECT`, and `WD_PERFCOUNT_SELECT`, which select geometry/frontend, input assembler, and work distributor performance events.

`WD_IA_DRAW_TYPE`, `WD_IA_DRAW_REG_XFER`, and `WD_IA_DRAW_SOURCE` identify draw transfer styles and draw sources for the IA/WD path. These definitions connect command-stream draw programming to the VGT/IA/WD hardware interpretation of primitive topology, index source, and pipeline stage routing.

### GB, Texture Cache, and Memory Cache Blocks

The GB section defines `GB_EDC_DED_MODE` plus tiling table and macrotable sizes. These constants describe graphics block error handling and table sizing rather than executable logic.

TA, TD, TCP, TCC, and TCA enums cover texture/cache behavior:

- `TA_TC_ADDR_MODES` names address calculation modes such as default and compatible modes.
- `TA_PERFCOUNT_SEL` and `TD_PERFCOUNT_SEL` select texture-address and texture-data unit events.
- `TCP_PERFCOUNT_SELECT` is a large selector space for texture cache requests, hits/misses, stalls, atomics, invalidations, tag/data behavior, FIFO pressure, and related cache-side metrics.
- `TCP_CACHE_POLICIES`, `TCP_CACHE_STORE_POLICIES`, and `TCP_WATCH_MODES` define cache read/store policy and watchpoint modes.
- `TCP_DSM_DATA_SEL`, `TCP_DSM_SINGLE_WRITE`, and `TCP_DSM_INJECT_SEL` select diagnostic/state-machine data and injection controls.
- `TCC_PERF_SEL` and `TCA_PERF_SEL` expose L2/cache-array performance selectors, covering requests, returns, probes, misses, stalls, invalidations, and backend traffic.

These enums are integration points for GPU performance monitoring, cache diagnostics, and low-level register programming. They do not implement cache behavior; they encode what hardware path or event is selected by a perf register or control field.

### GRBM and Command Processor

`GRBM_PERF_SEL` and the per-shader-engine `GRBM_SE0_PERF_SEL` through `GRBM_SE3_PERF_SEL` enumerate graphics register bus manager performance events and shader-engine-specific activity/idle/busy signals.

The command-processor section defines:

- `CP_RING_ID`, `CP_PIPE_ID`, and `CP_ME_ID` for naming graphics/compute/SDMA-style CP routing identities.
- `SPM_PERFMON_STATE`, `CP_PERFMON_STATE`, and `CP_PERFMON_ENABLE_MODE` for perf monitor state-machine and enable control encodings.
- `CPG_PERFCOUNT_SEL`, `CPF_PERFCOUNT_SEL`, and `CPC_PERFCOUNT_SEL` for graphics, frontend, and compute command processor performance selectors.
- `CP_ALPHA_TAG_RAM_SEL` for selecting CP alpha tag RAMs.
- CP-related response, retry, interrupt, VMID size, and configuration-space range constants (`CONFIG_SPACE*`, `UCONFIG_SPACE`, `PERSISTENT_SPACE`, and `CONTEXT_SPACE`).

These values tie packet execution, queue/ring selection, VMID-related addressing, and command processor perf monitoring into the rest of the AMDGPU command submission and diagnostics stack.

### SX, DB, Texture, Vertex, SU, and SC

The SX section provides render backend/color-output values such as `SX_BLEND_OPT`, `SX_OPT_COMB_FCN`, `SX_DOWNCONVERT_FORMAT`, and a large `SX_PERFCOUNTER_VALS` enum. These encode blend optimization modes, format downconversion choices, and SX performance events.

The DB section defines depth/stencil and depth-buffer operation values:

- `ForceControl`, `ZSamplePosition`, `ZOrder`, `ZpassControl`, `ZModeForce`, `ZLimitSumm`, `CompareFrag`, `StencilOp`, `ConservativeZExport`, `DbPSLControl`, and `DbPRTFaultBehavior`.
- `PerfCounter_Vals`, `RingCounterControl`, `DbMemArbWatermarks`, `DFSMFlushEvents`, `PixelPipeCounterId`, and `PixelPipeStride`.

Texture and vertex fetch enums define sampler and resource descriptor encodings:

- `TEX_BORDER_COLOR_TYPE`, `TEX_CHROMA_KEY`, `TEX_CLAMP`, `TEX_COORD_TYPE`, `TEX_DEPTH_COMPARE_FUNCTION`, `TEX_DIM`, `TEX_FORMAT_COMP`, `TEX_MAX_ANISO_RATIO`, `TEX_MIP_FILTER`, `TEX_REQUEST_SIZE`, `TEX_SAMPLER_TYPE`, `TEX_XY_FILTER`, and `TEX_Z_FILTER`.
- `VTX_CLAMP`, `VTX_FETCH_TYPE`, `VTX_FORMAT_COMP_ALL`, `VTX_MEM_REQUEST_SIZE`.
- `TVX_DATA_FORMAT`, `TVX_DST_SEL`, `TVX_ENDIAN_SWAP`, `TVX_INST`, `TVX_NUM_FORMAT_ALL`, `TVX_SRC_SEL`, `TVX_SRF_MODE_ALL`, and `TVX_TYPE`.

The SU and SC sections define `SU_PERFCNT_SEL` and `SC_PERFCNT_SEL`, both large performance selector spaces. The SC selector list covers scan converter input/output pressure, PA/SC and SC/SPI interfaces, PS arbitration, end-of-pipe/event synchronization, PBB/binning metrics, overlap/quad packer events, busy/starved states, and FIFO reads/writes.

The raster-routing enums (`SePairXsel`, `SePairYsel`, `SePairMap`, `SeXsel`, `SeYsel`, `SeMap`, `ScXsel`, `ScYsel`, `ScMap`, `PkrXsel2`, `PkrXsel`, `PkrYsel`, `PkrMap`, `RbXsel`, `RbYsel`, `RbXsel2`, and `RbMap`) encode tiling and mapping choices for shader engines, scan converters, packers, and render backends. `BinningMode`, `BinEventCntl`, and `CovToShaderSel` expose primitive binning policy and coverage-input selection.

### RMI Beginning

The final part of the chunk starts `RMIPerfSel`. The covered values include no-op/busy/clock/perf-window/event-send selectors, per-VMID and all-VMID invalidation request selectors, invalidation start/finish selectors, UTCL1 translation/permission/request/stall/FIFO events, RB-to-RMI write request selectors by client ID, write-return valid/NACK selectors, and the beginning of RB-to-RMI read request/read-return selectors. The enum does not finish in this chunk, so a complete RMI analysis must include the adjacent chunk.

## Control Flow

There is no runtime control flow in this chunk. The header contributes compile-time constants only.

The effective control flow is indirect: AMDGPU code, shader tooling, and diagnostics choose one of these values, write it into a register or command packet field, and the Vega10 hardware interprets that value. Examples include event packet dispatch using `VGT_EVENT_TYPE`, draw setup using VGT/IA/WD enums, perf counter setup using `*_PERFCOUNT_*` selectors, texture/sampler descriptor programming using `TEX_*` and `TVX_*`, or shader decode/disassembly using `VALUE_SQ_*`.

## State and Persistence Behavior

The header itself stores no state. The state represented by these constants lives in hardware registers, command packets, shader binaries, resource descriptors, and performance-monitor selector registers.

Important state categories include:

- Persistent or semi-persistent register programming, such as raster configuration maps, binning mode, texture cache policy, command processor perf monitor state, and depth/stencil control modes.
- Per-command or per-draw state, such as primitive type, draw source, index size, tessellation topology, event type, and VGT stage routing.
- Shader binary/descriptor encodings, such as SQ opcodes, operand selectors, target encodings, data formats, wait-count partitioning, send-message fields, and special register IDs.
- Diagnostic/performance state, such as which VGT/IA/WD/TA/TD/TCP/TCC/TCA/GRBM/CP/SX/DB/SU/SC/RMI event a hardware counter measures.
- Status or exceptional behavior selected by constants, such as SQ exception IDs, EDC fatal error sources, PRT fault behavior, DFSM flush events, and RMI invalidation events.

Persistence, reset values, and write semantics are not encoded in this enum header. Those semantics come from the corresponding register definitions, command packet formats, firmware conventions, shader ISA documentation, and hardware blocks that consume the numeric values.

## Dependencies and Integration Points

This header depends on the generated AMD register/header naming convention and on the Vega10 hardware ISA/register specification. It is typically included alongside Vega10 register offset and mask headers and consumed by AMDGPU ASIC-specific code.

Likely integration points include:

- Command submission and packet-building paths that emit VGT event types, primitive topology, draw source, index size, and pipeline-stage encodings.
- Shader compiler, disassembler, trap/debug, thread trace, and performance tooling that decode or generate SQ instruction formats and special operand values.
- GPU performance monitoring code that programs selectable counters for VGT, IA, WD, TA, TD, TCP, TCC, TCA, GRBM, CP, SX, DB, SU, SC, and RMI blocks.
- Texture, sampler, image, buffer, and vertex resource descriptor construction paths that use `TEX_*`, `VTX_*`, and `TVX_*` encodings.
- Depth/stencil, color backend, rasterization, binning, and scan-converter setup paths that rely on DB, SX, SU, SC, and raster routing enums.
- Cache, memory-interface, RMI, and VM/TLB diagnostic paths that interpret invalidation, request, stall, return, and error-source selector values.

The constants are ASIC-specific. Nearby AMD generations may share names but not always values or supported selectors. Mixing Vega10 enum values with non-Vega10 register layouts can silently program the wrong hardware behavior.

## Risks

- Numeric drift is high risk. A wrong enum value can select the wrong primitive topology, event packet, opcode, texture format, cache policy, perf counter source, or raster route while still compiling cleanly.
- Perf selector enums are long and repetitive. Copy/paste or generator errors can make counters report unrelated signals, which is hard to catch without hardware validation.
- SQ instruction constants are effectively ISA ABI. Incorrect opcodes, operand ranges, translation offsets, or special-register IDs can break shader disassembly, debug tooling, trap interpretation, or generated shader code.
- Event and flush enums affect synchronization. Misusing values such as cache flush, partial flush, context done, thread trace, or DB/CB invalidation events can cause hangs, stale memory visibility, bad timestamps, or missing trace data.
- Texture/vertex format and sampler constants affect memory interpretation. A bad data format, numeric format, swizzle selector, endian swap, clamp, filter, dimension, or request-size value can produce rendering corruption or memory faults.
- Raster/binning/routing constants encode hardware topology assumptions. Wrong SE/SC/PKR/RB mappings or binning controls can break load distribution, tile/bin behavior, or render backend routing.
- Security and isolation diagnostics can be affected indirectly. RMI, VMID, UTCL1, cache invalidation, and fault-related selector mistakes can hide invalidation failures or mislead debugging of GPU virtual memory faults.
- The chunk starts and ends mid-file. The full per-file report must reconcile prior SQ context before line 15209 and the continuation of `RMIPerfSel` after line 21528.

## Test and Validation Signals

Useful validation is mostly compile-time, shader/packet decode, and hardware integration coverage:

- Build AMDGPU and any Vega10 consumers that include `vega10_enum.h`; this catches missing, renamed, or syntactically invalid enum constants.
- Compare generated enum values against the authoritative Vega10 register/ISA database used to create the header, especially for SQ opcodes, VGT events, texture/vertex formats, and performance selectors.
- Run shader ISA/disassembly tests that cover SOP, SMEM, VOP, VOP3/VOP3P, VINTRP, DS, MUBUF, MTBUF, MIMG, EXP, FLAT/global/scratch, SDWA, DPP, send-message, wait-count, and trap encodings.
- Exercise command-stream tests for primitive topology, draw source, index size, tessellation, GS/HS/DS/VS stage routing, streamout, context done, cache flushes, partial flushes, thread trace events, and pipeline statistics events.
- Validate performance-counter programming for each covered block by selecting representative VGT/IA/WD/TA/TD/TCP/TCC/TCA/GRBM/CP/SX/DB/SU/SC/RMI events and checking that activity changes under targeted workloads.
- Run texture, sampler, image, buffer, and vertex-fetch tests that cover dimensions, formats, numeric formats, component selection, filtering, anisotropy, mip filtering, border color, clamp modes, endian swap, and request sizes.
- Exercise depth/stencil/color backend tests for compare/stencil ops, conservative Z export, Z order, Z mode force, PRT fault behavior, blend optimization, downconversion, and DB/SX counters.
- Validate raster routing and primitive binning on Vega10 hardware using workloads that stress multiple shader engines, scan converters, packers, render backends, PBB/binning modes, and coverage-to-shader selection.
- For the RMI beginning in this chunk, use VM/TLB invalidation and memory-traffic diagnostics to confirm UTCL1 misses/stalls, invalidation request selectors, and RB/RMI request/return selectors report plausible activity.
