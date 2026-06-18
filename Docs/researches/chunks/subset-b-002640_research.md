# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h lines 19599-22320

## Scope

This chunk is a generated AMD GC 9.1 register bitfield header segment. It contains C preprocessor `#define` constants for register field shifts and masks, not executable driver logic. The visible range starts in the middle of `CB_COLOR1_INFO`, continues through color buffer targets 1-7, covers a large `gc_gfxudec` graphics/command-processor register block, covers `gc_perfddec` performance counter data registers, and ends at the beginning of `gc_perfsdec` with `CPG_PERFCOUNTER1_SELECT`.

The chunk exports 2,103 macro definitions across 605 register names. Each field generally appears as:

- `REGISTER__FIELD__SHIFT`, the low bit position for the field.
- `REGISTER__FIELD_MASK`, the full 32-bit mask for the field.

These macros are paired with the matching GC 9.1 offset header, primarily `gc_9_1_offset.h`, and with common AMDGPU helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()`.

## Purpose

The purpose of this chunk is to let GC 9.1 software program and decode hardware registers using symbolic field names instead of raw bit positions. The register families in this range support:

- Color-buffer render-target setup, including base addresses, views, formats, sample counts, swizzle modes, DCC/CMASK/FMASK metadata, fast-clear words, and compression controls for CB color targets 1-7.
- Command processor event, streamout, primitive/statistics, scratch, append/fence, atomic pre-operation, semaphore, CP DMA, coherency, indirect-buffer, command-buffer, metadata, draw/dispatch, index, and GDS backup registers.
- VGT/IA/WD/PA registers for primitive/index state, transform feedback, vertex/index buffers, multi-VGT parameters, screen extents, line stipple, and trap-screen controls.
- Shader and cache diagnostics, especially SQ thread trace setup/status, SQC cache invalidate/writeback controls, and SPI configuration.
- Depth/occlusion counters and GDS/GWS/OA/atomic registers for global data store access, synchronization resources, ordered append state, and GDS atomic operations.
- Performance counter readback registers for CP, GRBM, WD, IA, VGT, PA, SPI, SQ, SX, GDS, TA, TD, TCP, TCC, TCA, CB, DB, RLC, RMI, ATC L2, and MC VM L2 blocks.

The file is hardware metadata. It declares no functions, structs, variables, locks, or software-owned storage.

## Important Macro Groups

Color-buffer groups include `CB_COLOR1_*` through `CB_COLOR7_*`. For targets 2-7, this chunk includes complete visible groups for `BASE`, `BASE_EXT`, `ATTRIB2`, `VIEW`, `INFO`, `ATTRIB`, `DCC_CONTROL`, `CMASK`, `CMASK_BASE_EXT`, `FMASK`, `FMASK_BASE_EXT`, `CLEAR_WORD0`, `CLEAR_WORD1`, `DCC_BASE`, and `DCC_BASE_EXT`. Target 1 starts mid-register with late `CB_COLOR1_INFO` fields, then continues with `ATTRIB`, `DCC_CONTROL`, metadata base, clear-word, and DCC base fields. Important fields encode render target format/number type/component swap, fast clear, compression, blend optimization, DCC enablement, CMASK address type, resource type, color and FMASK swizzle modes, sample/fragment counts, RB/pipe alignment, MIP dimensions, slice ranges, and 256-byte-aligned base-address pieces.

Command processor event and query groups include `CP_EOP_DONE_ADDR_*`, `CP_EOP_DONE_DATA_*`, `CP_EOP_LAST_FENCE_*`, streamout addresses, primitive written/needed counters 0-3, `CP_PIPE_STATS_ADDR_*`, `CP_VGT_*INVOC*` and `CP_PA_*COUNT*` statistics, `CP_SC_PSINVOC_COUNT*`, `CP_PIPE_STATS_CONTROL`, `CP_STREAM_OUT_CONTROL`, and `CP_STRMOUT_CNTL`. These fields describe where the CP writes event/fence/query data and how streamout or pipeline statistics are controlled.

CP scratch, append, atomic, semaphore, and wait groups include `SCRATCH_REG0..7`, `SCRATCH_UMSK`, `SCRATCH_ADDR`, `CP_APPEND_*`, `CP_ATOMIC_PREOP_*`, `CP_ME_ATOMIC_PREOP_*`, `CP_PFP_ATOMIC_PREOP_*`, `CP_GDS_ATOMIC*_PREOP_*`, `CP_ME_GDS_ATOMIC*_PREOP_*`, `CP_PFP_GDS_ATOMIC*_PREOP_*`, `CP_ME_MC_*ADDR*`, `CP_ME_MC_WDATA_*`, `CP_SEM_WAIT_TIMER`, `CP_SIG_SEM_ADDR_*`, `CP_WAIT_SEM_ADDR_*`, and `CP_WAIT_REG_MEM_TIMEOUT`. Several high-address registers carry address bits plus `SEL`/`SWAP` fields, so consumers must preserve both addressing and access-mode bits.

CP DMA and coherency groups include `CP_DMA_PFP_CONTROL`, `CP_DMA_ME_CONTROL`, `CP_DMA_ME_COMMAND`, `CP_DMA_PFP_COMMAND`, source/destination address pairs, `CP_DMA_CNTL`, `CP_DMA_READ_TAGS`, `CP_COHER_BASE*`, `CP_COHER_SIZE*`, `CP_COHER_START_DELAY`, `CP_COHER_CNTL`, `CP_COHER_STATUS`, and the equivalent `CP_ME_COHER_*` controls. Coherency fields enable actions for TC noncoherent/write-combine/writeback, metadata invalidation, TCL1, CB, DB, shader K-cache, shader volatile K-cache, shader I-cache, and K-cache writeback. DMA command fields encode byte count and source/destination address-space/cache/increment behavior.

Indirect-buffer and command-buffer groups include `CP_PFP_IB_CONTROL`, `CP_PFP_LOAD_CONTROL`, `CP_*_OFFSET`, `CP_IB*_PREAMBLE_*`, `CP_CE_*`, `CP_IB*_BASE_*`, `CP_IB*_BUFSZ`, `CP_ST_*`, and command buffer size registers. These fields define IB base/size/offset state, preamble ranges, CE command buffers, and state-shadow buffer addresses.

Draw, dispatch, index, and metadata groups include `CP_PFP_METADATA_BASE_ADDR*`, `CP_CE_METADATA_BASE_ADDR*`, `CP_DRAW_INDX_INDR_ADDR*`, `CP_DISPATCH_INDR_ADDR*`, `CP_INDEX_BASE_ADDR*`, `CP_INDEX_TYPE`, `CP_GDS_BKUP_ADDR*`, `CP_SAMPLE_STATUS`, `CP_PFP_COMPLETION_STATUS`, `CP_CE_COMPLETION_STATUS`, and `CP_PRED_NOT_VISIBLE`. `CP_SAMPLE_STATUS` is relatively dense, exposing request/enabled/done bits for counters, pixels, vertices, primitives, and GDS.

VGT/IA/WD/PA groups include `VGT_GSVS_RING_SIZE`, `VGT_PRIMITIVE_TYPE`, `VGT_INDEX_TYPE`, streamout filled sizes, max/min vertex index, index offset, multi-primitive reset enable, index and instance counts, transform feedback ring/base registers, HS off-chip parameters, WD position/control/index buffer bases, `IA_MULTI_VGT_PARAM`, `VGT_INSTANCE_BASE_ID`, line stipple, screen extent min/max pairs, and P3D/HP3D/general trap-screen controls. `GRBM_GFX_INDEX` selects shader engine, shader array, and instance broadcast behavior for instance-scoped GC accesses.

SQ/SQC/SPI groups include `SQ_THREAD_TRACE_BASE`, `SIZE`, `MASK`, `TOKEN_MASK`, `PERF_MASK`, `CTRL`, `MODE`, `BASE2`, `TOKEN_MASK2`, `WPTR`, `STATUS`, `HIWATER`, `CNTR`, and `USERDATA_0..3`, plus `SQC_CACHES`, `SQC_WRITEBACK`, `TA_CS_BC_BASE_ADDR*`, and `SPI_CONFIG_CNTL*`. Thread trace fields control CU/SH/SIMD/VMID selection, token filtering, shader-stage masking, capture mode, autoflush, performance capture, issue/test/interrupt/wrap behavior, write pointer status, buffer reset, and full/busy/error indications.

DB and GDS groups include occlusion counters 0-3, zpass count, direct GDS read/write/burst registers, `GDS_ATOM_*`, `GDS_GWS_RESOURCE*`, `GDS_OA_*`, and `GDS_WRITE_COMPLETE`. These fields expose low-level global data store access, GDS atomic operand/result registers, global wave sync resource ownership/head-queue state, and ordered-append allocation counters/addresses.

Performance counter data groups include `*_PERFCOUNTER{0..15}_{LO,HI}` style registers for many GC blocks. Most low/high halves are simple full-width `PERFCOUNTER_LO` or `PERFCOUNTER_HI` fields. ATC L2 and MC VM L2 high halves split `COUNTER_HI` from `COMPARE_VALUE`. The final visible selector group, `CPG_PERFCOUNTER1_SELECT`, starts the performance-select block and exposes `CNTR_SEL0`, `CNTR_SEL1`, `SPM_MODE`, and `CNTR_MODE1`; the rest of that select register is outside this chunk.

## Control Flow

There is no control flow in this header. Runtime control flow is created by consumers that combine these masks with GC register offsets and MMIO access helpers:

1. Choose the ASIC-specific offset macro for a GC 9.1 register from the matching offset header.
2. Build a 32-bit value with `REG_SET_FIELD()` or direct `FIELD << REGISTER__FIELD__SHIFT` operations, masked by `REGISTER__FIELD_MASK`.
3. Write the value through AMDGPU accessors such as `WREG32_SOC15()`, `WREG32_SOC15_RLC()`, packet emission paths, or firmware-mediated register paths.
4. Read status or counter registers with `RREG32_SOC15()` or command/query readback and decode fields with `_MASK` tests or `REG_GET_FIELD()`.
5. Branch in driver code based on decoded completion, busy, counter, semaphore, cache, trace, or query status.

Typical driver flows affected by this macro surface include render-target setup, clear-state programming, end-of-pipe events, streamout/statistics queries, CP DMA copies, cache flush/invalidate sequences, indirect-buffer setup, shader thread tracing, GDS/GWS synchronization, and performance monitoring.

## State And Persistence Behavior

This chunk defines bit layouts for hardware state, not software state. The represented state falls into several categories:

- Persistent configuration until rewritten or reset: CB target format/base/metadata layout, DCC behavior, CP coherency action masks, CP DMA control, IB/command-buffer bases and sizes, VGT/IA/WD setup, SQ thread trace mode/masks, SQC cache command bits, SPI configuration, GDS atomic/resource/OA setup, and performance counter selectors.
- Command-like or doorbell-style state: CP DMA commands, coherency requests, semaphore addresses, wait/reg-mem timeouts, thread trace buffer reset, SQC invalidate/writeback requests, and GDS atomic/ordered-append operations.
- Status or readback state: CP completion/fence/query data, primitive/statistics counters, CP coherency status, DMA tags and FIFO state, PFP/CE completion status, SQ thread trace status/write pointer/counter/high-water, SQC completion/dirty state, DB occlusion/zpass counters, GDS write/atomic completion, GWS head/resource state, and perf counter low/high halves.
- Address state: many registers encode GPU addresses split into low/high pieces and often in 256-byte units. Consumers must pair low/high/base-ext registers correctly and must respect address alignment implied by field names such as `BASE_256B`.

Hardware persistence is register-defined. Configuration fields usually survive until reset, suspend/resume reinitialization, ring/queue setup, or a later programming sequence. Status fields are volatile and may change while engines are active. Some status bits are sticky or completion-style and require the corresponding hardware clear or reset sequence rather than ordinary software memory semantics.

## Dependencies And Integration Points

The generated naming convention is the primary API contract. AMDGPU macros concatenate register and field tokens, so a spelling or layout change in this header can break `REG_SET_FIELD(value, REGISTER, FIELD, x)` / `REG_GET_FIELD(value, REGISTER, FIELD)` users even when no C symbol is directly referenced.

Important dependencies and integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_offset.h`, which provides register addresses for the field layouts in this file. In this tree, `amdgpu/psp_v10_0.c` directly includes the GC 9.1 offset header for PSP register interactions; other generated GC 9.x paths use the same offset-plus-mask pattern.
- SOC15 and AMDGPU register helpers such as `SOC15_REG_OFFSET()`, `RREG32_SOC15()`, `WREG32_SOC15()`, `WREG32_SOC15_RLC()`, `WREG32()`, `REG_SET_FIELD()`, and `REG_GET_FIELD()`.
- Clear-state and graphics setup tables for GFX generations. This tree has GC color-target clear-state tables in files such as `amdgpu/clearstate_gfx9.h`, where `CB_COLOR1_INFO` through `CB_COLOR7_INFO` and related CB registers are part of the saved/programmed hardware context.
- Command processor packet paths that emit event, DMA, cache, semaphore, query, streamout, draw, dispatch, and IB setup state. Some CP fields may be programmed indirectly by packet commands rather than by CPU MMIO writes.
- Profiling and debug paths that consume SQ thread trace and performance counter registers. The accompanying enum headers, such as `vega10_enum.h`, provide event/token selector values that are written into selector fields defined in generated mask headers.
- Per-instance register selection through `GRBM_GFX_INDEX`. Any code that writes instance-scoped VGT/PA/SQ/SPI/GDS/perf state must select or broadcast the intended shader engine, shader array, and instance before using these bitfields.

The source path is under a `ceph-client` mirror, but the content is AMD GPU driver register metadata. There is no Ceph filesystem logic in this chunk.

## Risks And Edge Cases

- Bitfield mistakes are high impact and low visibility. A wrong shift or mask compiles cleanly but can program the wrong hardware bit, corrupt render-target state, break cache flushes, stall CP DMA, misreport counters, or wedge debug/profiling flows.
- This range starts and ends mid-family. It begins partway through `CB_COLOR1_INFO`, so the complete target-1 color-buffer layout must be reconciled with the previous chunk. It ends after the first fields of `CPG_PERFCOUNTER1_SELECT`, so performance selector coverage is incomplete until later chunks are merged.
- Repeated CB target definitions invite generator or copy/paste drift. `CB_COLOR2_*` through `CB_COLOR7_*` should remain layout-identical where the hardware register families are replicated; a single mismatched mask can affect only one render target and be hard to diagnose.
- Address fields are alignment-sensitive. Many bases are in 256-byte units or have separate extension registers; using byte addresses directly or omitting high/ext pieces can redirect CB metadata, CP event writes, DMA transfers, IBs, or trace buffers.
- Cache and coherency fields are ordering-sensitive. Incorrect `CP_COHER_CNTL` or `CP_ME_COHER_CNTL` action masks can leave CB/DB/TC/SQ caches stale or force unnecessary flushes that hurt performance.
- Status registers are volatile. Polling `CP_COHER_STATUS`, DMA tags/FIFO bits, SQ thread trace status, SQC completion, GDS completion, or perf counters can race with active hardware and needs existing driver synchronization.
- Thread trace and perf counter controls can perturb workloads. Trace stall, interrupt, wrap, autoflush, and performance event masks affect shader execution and profiling data; invalid combinations can produce empty traces, full buffers, or unexpected stalls.
- GDS/GWS/OA and atomic registers are synchronization-sensitive. Misprogrammed resource/head/counter fields can affect queue synchronization, ordered append allocation, or global data store atomics.
- Generation-specific names are not interchangeable. GC 9.0, GC 9.1, GC 9.4.x, GC 10+, and GC 11+ headers have many matching register names but can differ in field availability or bit positions.

## Test And Validation Signals

Useful validation signals for this chunk are:

- Build AMDGPU with GC 9.1/Vega-era support enabled so generated macro names resolve wherever this ASIC's offset and mask headers are consumed.
- Run graphics workloads that bind multiple color targets, use DCC/CMASK/FMASK, fast clears, MSAA, and varied render-target formats. Problems in `CB_COLOR*_INFO`, `ATTRIB`, metadata-base, or clear-word fields tend to show as rendering corruption, bad clears, compression faults, or GPU hangs.
- Exercise CP event/query paths: fences, EOP writes, streamout, primitive statistics, occlusion/zpass queries, and pipeline statistics should complete and return plausible low/high counter values.
- Exercise CP DMA and coherency paths with buffer copies, cache flush/invalidate waits, and VM-visible data synchronization. Failures can appear as stale data, coherency wait timeouts, DMA tag stalls, or ring timeouts.
- Validate indirect-buffer and command-buffer execution under normal graphics and compute submissions. Incorrect IB base/size/offset or preamble fields can show as command processor hangs or malformed packet execution.
- Run shader thread trace/profiling flows and confirm trace buffers fill, wrap/interrupt/full/busy/status bits behave coherently, and token filters produce expected data.
- Run GDS/GWS/OA and atomic-sensitive compute workloads where available, especially queue synchronization and ordered append behavior.
- Compare generated masks mechanically against AMD's authoritative GC 9.1 register database and against neighboring GC 9.x headers, allowing only documented ASIC-version differences.

## Cross-Chunk Notes

This chunk should be merged with adjacent chunks before producing the final per-file research document. The previous chunk is needed for the beginning of `CB_COLOR1_INFO` and likely earlier `CB_COLOR1_*` state. Later chunks are needed for the rest of `gc_perfsdec` performance selector registers and any remaining GC 9.1 register-mask families.
