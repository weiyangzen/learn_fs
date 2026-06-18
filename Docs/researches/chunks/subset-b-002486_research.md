# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 24802-27455

## Scope

This chunk is a generated AMD GC 10.3.0 register shift/mask header slice. It contains 2,117 `#define` entries across lines 24802-27455 of `gc_10_3_0_sh_mask.h`. The macros expose bit positions and masks for register fields using the standard generated naming scheme:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit index of a field.
- `<REGISTER>__<FIELD>_MASK`: the field mask inside the 32-bit register word.

There are no functions, data structures, enums, includes, allocations, locks, or direct register accesses in this range. The file lives under a `ceph-client` source mirror, but this content is AMDGPU graphics-core hardware metadata, not distributed filesystem code.

The chunk starts in the tail of color-buffer render-target state with `CB_COLOR6_CLEAR_WORD1` and `CB_COLOR6_DCC_BASE`, then covers `CB_COLOR7_*`, extended color/CMASK/FMASK/DCC base registers for slots 0-7, `CB_COLORn_ATTRIB2/ATTRIB3`, a large `gc_gfxudec` command-processor and user graphics register block, a `gc_cprs64dec` MES register block, and the opening of the `gc_gusdec` graphics unified scheduler/interconnect arbitration block. It ends in the middle of `GUS_SDP_TAG_RESERVE1`: line 27455 defines `VC6_MASK`, while the following line outside this work item defines `VC7_MASK`.

## Purpose

`gc_10_3_0_sh_mask.h` gives AMDGPU and AMDKFD code symbolic field metadata for GFX10.3/GC 10.3.0 registers. Driver code combines these macros with matching register offsets from `gc_10_3_0_offset.h` and register access helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, SOC15 MMIO helpers, PM4 packet emitters, and generated clear-state/golden-register tables.

This slice covers several important hardware surfaces:

- Color-buffer render-target slot state: `CB_COLOR7_BASE`, `PITCH`, `SLICE`, `VIEW`, `INFO`, `ATTRIB`, `DCC_CONTROL`, CMASK/FMASK bases and slices, clear words, DCC base, plus extended base and attribute registers for color slots 0-7.
- Command processor user-visible graphics state under `gc_gfxudec`: EOP completion addresses/data/fences, streamout addresses, primitive and shader invocation counters, pipe statistics, scratch registers, append/fence state, atomic preoperation values, CP memory-controller address/data windows, semaphores, DMA command state, coherency state, IB offsets, command buffer sizing/base fields, doorbell buffers, metadata bases, indirect draw/dispatch addresses, index buffer metadata, GDS backup, sample status, and user VGT/GE/PA/SQ/GDS state.
- GDS and streamout/atomic support: `GDS_RD_*`, `GDS_WR_*`, `GDS_ATOM_*`, `GDS_GWS_*`, and `GDS_OA_*` fields used for global data share read/write windows, atomics, ordered-append resources, and counters.
- MES control and debug state under `gc_cprs64dec`: program counter, interrupt routine, trap/vector registers, control/reset/active bits, priority, interrupt pending state, scratch/index/data windows, RISC-V-like machine status/cause/bad-address/instruction pointer registers, cycle/time/instret counters, cache controls, quantum values, doorbell controls, general-purpose registers, data-memory index/data windows, and perfcount control.
- GUS arbitration and credit controls under `gc_gusdec`: IO read/write combine flushes, IO and DRAM priority aging/queuing/fixed/urgency/quantum coefficients, group burst limits, SDP arbitration final limits, virtual-channel QoS priorities, tag and response credits, and the first SDP tag reserve fields.

The practical goal is readability and ASIC-specific correctness. Consumers can construct or decode a register word without hard-coding numeric bit locations, while still compiling to simple constant shifts and masks.

## Important APIs, Types, And Macros

This chunk exports only preprocessor constants. The important macro families are:

- `CB_COLOR7_*`: render target address and layout fields. `CB_COLOR7_INFO` defines format, endian, number type, component swap, fast clear, compression, blend controls, DCC enable, CMASK address type, and tiling bits. `CB_COLOR7_ATTRIB` and `CB_COLOR7_DCC_CONTROL` define tile modes, FMASK settings, sample/fragment counts, DCC block sizing, color transform, independent block modes, lossy precision, and DCC compression control.
- `CB_COLOR[0-7]_*_BASE_EXT`, `CMASK_BASE_EXT`, `FMASK_BASE_EXT`, and `DCC_BASE_EXT`: high/extension address bits for the surface and compression metadata base addresses. These are paired with the low base registers from this and neighboring chunks.
- `CB_COLOR[0-7]_ATTRIB2` and `ATTRIB3`: additional render-target geometry metadata such as metadata linearity, max compressed/uncompressed block sizes, alignment, pipe/bank addressing, mip tail, resource type, and channel read/write behaviors.
- `CP_EOP_*`, `CP_STREAM_OUT_*`, `CP_NUM_PRIM_*`, `CP_VGT_*COUNT*`, `CP_PA_*COUNT*`, `CP_SC_*COUNT*`, and `CP_PIPE_STATS_*`: completion, streamout, and graphics pipeline statistics fields. Many are 64-bit hardware values represented as low/high 32-bit register pairs.
- `SCRATCH_REG0` through `SCRATCH_REG7`, `SCRATCH_REG_ATOMIC`, `SCRATCH_REG_CMPSWAP_ATOMIC`, `SCRATCH_UMSK`, `SCRATCH_ADDR`, `CP_SCRATCH_INDEX`, and `CP_SCRATCH_DATA`: scratch and indexed scratch access fields used by CP firmware, debug, and command streams.
- `CP_APPEND_*`, `CP_*ATOMIC*_PREOP_*`, `CP_ME_MC_*`, `CP_SIG_SEM_*`, `CP_WAIT_*`, `CP_DMA_*`, `CP_COHER_*`, `CP_*IB*`, `CP_*CMD*`, and `CP_*DB*`: command processor append/fence state, atomic preoperation values, memory-controller read/write windows, semaphore addressing/timers, DMA source/destination/command words, coherency control/status, indirect-buffer offsets, command buffer bases/sizes, and doorbell buffer bases/sizes.
- `VGT_*`, `GE_*`, `WD_*`, `IA_*`, `PA_*`, `SQ_THREAD_TRACE_USERDATA_*`, `SQC_CACHES`, `TA_CS_BC_*`, `DB_*`, `GDS_*`, and `SPI_CONFIG_CNTL_*_REMAP`: user graphics state exposed through the `gc_gfxudec` block for draw setup, streamout, primitive counts, shader trace userdata, cache controls, buffer constants, depth/occlusion counters, GDS operations, and SPI remap controls.
- `CP_MES_*`: MES microcontroller/control fields for reset, halt, step, active pipe state, interrupt enable/pending, scratch access, machine status, exception cause, instruction/data cache operations, counters, process quantum, doorbells, general-purpose registers, and perfcount control.
- `GUS_IO_*`, `GUS_DRAM_*`, and `GUS_SDP_*`: arbitration and flow-control fields. Repeated group coefficients define age, queuing, fixed priority, urgency, urgency mode, quantum thresholds, burst limits, virtual-channel priority, tag limits, write/read response credits, and VC tag reservations.

Field names encode likely hardware intent but not full access semantics. For example, names ending in `STATUS`, `COUNT`, `COMPLETE`, `FLUSH`, `RESET`, `HALT`, `ACTIVE`, `ADDR`, `BASE`, `HI`, `LO`, `TIMEOUT`, `CREDITS`, or `RESERVE` suggest status, counters, commands, addresses, split register pairs, timeout, or resource reservation behavior, but this header does not say whether a field is read-only, write-one-to-clear, sticky, self-clearing, privileged, or context-saved.

## Control Flow

There is no runtime control flow in this header. It is declarative compiler input.

Runtime use normally follows this pattern:

1. Driver code selects a GC 10.3.0 register offset from `gc_10_3_0_offset.h`.
2. It inserts or extracts fields with the matching `__SHIFT` and `_MASK` macros, usually through AMDGPU helpers that token-paste the register and field names.
3. It writes, reads, polls, or dumps the register via SOC15 MMIO, GRBM-indexed access, PM4 packets, command stream state emission, or firmware/MES control paths.
4. Hardware blocks then interpret those bits as render-target layout, command-processor state, MES control/debug state, GDS operation state, or GUS arbitration/credit policy.

Important sequencing lives outside this file. Examples include programming all low/high or base/extension address halves coherently, setting render-target DCC/CMASK/FMASK metadata consistently with surface layout, reading split 64-bit counters with rollover awareness, emitting EOP and streamout addresses before events that write them, programming semaphore and doorbell fields with required alignment, waiting for CP coherency/status completion, controlling MES reset/halt/step only when firmware ownership allows it, and changing GUS arbitration/credit values only in hardware-safe initialization or tuning windows.

## State And Persistence Behavior

The macros themselves are stateless compile-time constants and persist nothing. They describe hardware-visible register state.

State represented by this chunk includes:

- Color render-target layout and compression state: base addresses, extended address bits, pitch/slice/view, format, tiling, sample/fragment counts, DCC/CMASK/FMASK metadata, clear words, and additional addressing/metadata attributes.
- Command processor completion and synchronization state: EOP done address/data, last fence values, streamout destinations, semaphore wait/signal addresses, wait timeouts, append data, and doorbell buffer metadata.
- Performance and query state: primitive written/needed counters, shader invocation counters, pipe statistics, occlusion/zpass counters, MES cycle/time/instret counters, and GDS ordered-append counters.
- CP execution support state: scratch registers, indexed scratch windows, atomic preoperation values, micro-engine memory-controller read/write state, DMA commands, coherency controls/status, indirect-buffer offsets, command-buffer bases and sizes, metadata bases, indirect draw/dispatch addresses, index buffer base/type, and GDS backup addresses.
- User draw state: VGT primitive/index/instance/tessellation/user-mode fields, GE index/min/max/stereo/user VGPR fields, WD buffer bases, PA line/stipple/trap-screen state, SQ thread trace userdata, SQC cache controls, TA constant buffer bases, DB counters, and GDS read/write/atomic/resource fields.
- MES firmware/control state: MES program/vector registers, control/reset/active/halt/step flags, interrupt state, machine registers, counters, doorbell controls, quantum controls, GP registers, data-memory index/data, and perfcount control.
- GUS arbitration state: IO and DRAM priority aging, queuing, fixed, urgency, quantum, burst, virtual-channel QoS, tag limits, response credits, and tag reservations.

Persistence is hardware-defined. Some fields are per-context or command-stream state that the driver emits repeatedly. Some are long-lived initialization or tuning registers that remain until reset, suspend/resume reinitialization, power gating, or a later write. Status, counter, complete, busy, and credit fields may change autonomously while the GPU runs. The header does not provide reset values; those are supplied by companion default headers or hardware documentation.

## Dependencies And Integration Points

This chunk must remain synchronized with the rest of the GC 10.3.0 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h` provides the corresponding register offsets and address block placement.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_default.h` provides reset/default values where generated.
- AMDGPU GFX10.3 code includes these generated headers for register programming, clear-state emission, golden settings, ring and queue setup, firmware/MES control, reset/recovery, profiling, and register dumps.
- AMDKFD queue and packet-management code indirectly depends on matching CP, MES, doorbell, scratch, semaphore, and dispatch-related field layouts.
- Render-target and DB/CB consumers depend on these fields matching user-mode command stream expectations for color formats, compression metadata, DCC/CMASK/FMASK layout, clear behavior, and address extension bits.
- GUS fields integrate with graphics interconnect scheduling, DRAM/IO arbitration, SDP virtual-channel priorities, credit limits, and performance tuning or golden-register initialization.

The macros depend on C preprocessor name matching rather than type checking. A mismatch between this file and the selected offset/default header, or between GC 10.3.0 and a neighboring generation such as GC 10.1.0, can compile successfully while targeting an incompatible field layout.

## Risks And Edge Cases

- The chunk starts mid-register: `CB_COLOR6_CLEAR_WORD1` is present without its preceding comment line inside the selected range. Neighboring chunks are needed for complete per-file context.
- The chunk ends mid-register: `GUS_SDP_TAG_RESERVE1__VC7_MASK` is on line 27456, just outside the requested range. Merge/reconciliation must not treat `GUS_SDP_TAG_RESERVE1` as complete based only on this document.
- Generated-header drift is high impact. A single bad shift or mask can silently corrupt adjacent hardware fields, causing rendering corruption, hangs, bad synchronization, wrong counters, or wrong memory addresses.
- Color target state has repeated slot layouts. Slot-specific copy/generator mistakes may affect only MRT slot 7, only high-address extension bits, or only compressed render targets using CMASK/FMASK/DCC.
- Address programming is split across low/high and base/extension registers. Partially updated CP, streamout, append, DB, GDS, color, CMASK, FMASK, or DCC addresses can point hardware at stale or wrong GPU memory.
- Compression metadata fields are tightly coupled. DCC, CMASK, FMASK, clear words, sample counts, fragment counts, tile modes, and block-size attributes must match the surface layout and metadata allocation.
- Counter and status fields are volatile. Low/high counter pairs can roll over between reads, and status/complete fields may be sticky, write-clear, or firmware-owned in ways not visible here.
- CP DMA, semaphore, coherency, append, and doorbell fields are ordering-sensitive. Wrong waits, cache policies, doorbell offsets, timeout values, or coherency controls can break queue progress and completion signaling.
- MES control registers are firmware-sensitive. Incorrect reset, halt, step, active-pipe, interrupt, cache-operation, or doorbell fields can interfere with scheduling firmware and be difficult to recover without a GPU reset.
- GDS atomic/resource fields and ordered-append counters can corrupt synchronization or append/consume behavior if field widths or operation modes are decoded incorrectly.
- GUS arbitration and credit values can produce performance cliffs, starvation, deadlocks, or subtle latency regressions if programmed outside documented safe ranges.
- `RESERVED`, `UNUSED`, and `OBSOLETE` fields appear in the range. Callers should preserve reserved bits unless an ASIC-specific table explicitly requires a value.

## Test Signals

Useful validation is mostly build-time, generator-level, and hardware-integration oriented:

- Build AMDGPU and AMDKFD configurations that include GC 10.3.0 support; missing, renamed, or malformed macros should surface in GFX10.3, KFD, MES, CP, GDS, and register-table consumers.
- Mechanically verify that complete registers in this range have expected `__SHIFT`/`_MASK` pairs, non-overlapping masks, and matching offsets/defaults in `gc_10_3_0_offset.h` and `gc_10_3_0_default.h`. Account for the partial start and partial end registers.
- Compare repeated `CB_COLOR0` through `CB_COLOR7` extended base and attribute groups for intentional slot-number-only differences.
- Exercise graphics workloads using multiple render targets, high GPU addresses, DCC/CMASK/FMASK compression, fast clears, MSAA, blending, streamout, primitive counters, pipeline statistics, occlusion/zpass counters, and indirect draw/dispatch.
- Exercise CP synchronization paths: EOP events, streamout completion, append/fence updates, scratch register access, CP DMA copies, memory-controller read/write windows, semaphores, wait-reg-mem timeout behavior, coherency waits, and doorbell buffers.
- Run MES-focused boot, queue scheduling, preemption, reset/recovery, interrupt, and debug-register tests on GC 10.3 hardware.
- Run GDS atomic, ordered-append, GWS resource, and OA counter workloads to validate `GDS_*` field behavior.
- Validate GUS programming with golden-register initialization, stress workloads with mixed IO/DRAM traffic, and performance counters or register dumps that show tag/credit and VC-priority behavior.
- Watch for GPU hangs, false completion, semaphore timeouts, bad fence values, corrupted render targets, metadata decompression failures, bad primitive/query counters, MES scheduling failures, GDS atomic errors, and workload-specific performance regressions.

## Chunk Notes For Merge

This document intentionally covers only lines 24802-27455 of `gc_10_3_0_sh_mask.h`. The previous chunk must supply the beginning of the `CB_COLOR6_CLEAR_WORD1` context, and the next chunk must complete `GUS_SDP_TAG_RESERVE1` with `VC7_MASK` before continuing into `GUS_SDP_VCC_RESERVE0` and later GUS credit-reserve fields. The final per-file report should treat the whole source as generated AMD GC 10.3.0 register field metadata consumed by AMDGPU/AMDKFD, not as handwritten runtime logic.
