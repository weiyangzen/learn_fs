# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 15119-17740

## Scope

This chunk is a generated AMD GC 12.1.0 shift/mask register-header segment. It contains C preprocessor constants only: hardware register fields are represented by `__SHIFT` values and matching `__MASK` values for 32-bit register packing and decoding. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines begin inside the `CP_MES_IC_OP_CNTL` definition, covering MES instruction-cache operation bits after the preceding chunk's register comment. The body then covers MES and MEC RS64 command-processor state, a large banked GFX RS64 data-cache aperture region, CP/GFX/PFP/ME exception and interrupt status, CH and GLARB client arbitration/fabric controls, performance counter result and select registers, CP draw-window/perfmon controls, and RLC streaming performance monitor setup. The chunk ends mid-register at `RLC_SPM_ACCUM_STATUS`: it includes the status field shifts but not the corresponding masks, which are in the next chunk.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for the GC 12.1.0 graphics IP and is not Ceph filesystem code.

## Purpose

`gc_12_1_0_sh_mask.h` supplies bit layouts for GC 12.1.0 registers. Driver code pairs these macros with register addresses from the matching offset header, and often with generated default/reset values, so AMDGPU code can compose register values without hard-coded bit positions. Consumers usually use helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` around these generated constants.

This chunk is centered on command processor RS64 state, client/fabric controls, and performance monitoring:

- `CP_MES_*` fields for MES instruction/data cache operations, CSR-style cycle/time/instret/ISA/vendor/hart/timer state, VMID/cache/scope policy, process quantum, doorbells, general-purpose registers, local/instruction/scratch apertures, performance selection, pending interrupt, exception status, interrupt payload registers 16 through 31, and metadata control.
- `CP_MEC_*` and `CP_MEC_RS64_*` fields for MEC RS64 program counter/vector setup, reset/active/halt/step controls, interrupt masks/status, instruction pointer, data-cache policy and invalidate completion, timer compare, GP registers, local/instruction/scratch apertures, performance selection, pending interrupt, exception status, and interrupt payload registers 16 through 31.
- `CP_CPC_IC_OP_CNTL` fields for command processor instruction-cache invalidation, priming, completion, invalidate-all, reset-error, and error reporting.
- `CP_GFX_RS64_*`, `CP_PFP_RS64_*`, and `CP_ME_RS64_*` fields for graphics command processor interrupts, cache controls, local/instruction/scratch apertures, exception status, perf controls, timer/MIP state, GP registers, instruction pointers, pending interrupts, and two banks of 16 GFX RS64 data-cache apertures.
- `CH*`, `CHA*`, and `CHI*` fields for CPWD channel arbitration, DRAM burst controls, client credits, free-delay tuning, repeater fine-grain clock-gating overrides, CHC buffering/credit controls, stall/busy status, and DCC error reporting.
- `GLARB*`, `GLARBA*`, `GLARBI*`, and `GLARBC*` fields for GLARB arbitration, memory burst behavior, NPS/target-disable mode, GLARBC credits, clock-gating overrides, buffer controls, CREST mode, status/error reporting, and DCC compression control.
- `CPG`, `CPC`, `CPF`, `GRBM`, `GE1`, `GE2_DIST`, `GC_EA_CPWD`, `CHC`, `GLARBA`, `GLARBC`, `RLC`, `GCR`, and `CHA` performance counter result registers and performance-counter select registers.
- `CP_PERFMON_CNTL`, latency-stat selectors, TC performance-counter window selectors, CP draw object/window fields, and RLC SPM ring, segment, mux select, user data, accumulator RAM, and accumulator status fields.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register-address symbols live in the companion GC 12.1.0 offset header with matching register names.
- AMDGPU code normally uses these through generated field helpers, MMIO read-modify-write helpers, command-packet register programming, debug/perf paths, and reset/recovery logic.

Notable macro families in this exact slice:

- `CP_MES_IC_OP_CNTL`, `CP_MES_DC_BASE_CNTL`, and `CP_MES_DC_OP_CNTL`: MES instruction/data cache controls. They expose invalidate, prime, primed, VMID, cache policy, scope, invalidate-complete, and bypass-all fields.
- `CP_MES_MCYCLE_*`, `CP_MES_MTIME_*`, `CP_MES_MINSTRET_*`, `CP_MES_MISA_*`, `CP_MES_MVENDORID_*`, `CP_MES_MARCHID_*`, `CP_MES_MIMPID_*`, `CP_MES_MHARTID_*`, and `CP_MES_MTIMECMP_*`: 64-bit CSR-style MES observability and timer registers represented as low/high 32-bit halves.
- `CP_MES_PROCESS_QUANTUM_PIPE0/1`: MES scheduling quantum fields, including duration, expired flag, scale, and enable.
- `CP_MES_DOORBELL_CONTROL1..6`: doorbell offset, enable, and hit fields for MES doorbell routing.
- `CP_MES_GP0..9_{LO,HI}` and `CP_MEC_GP0..9_{LO,HI}`: GP register views, with special fields such as `PG_VIRT_HALTED`, return-address high halves, read/write selector halves, and stack-pointer halves.
- `CP_MES_LOCAL_*` and `CP_MEC_LOCAL_*`: local, instruction, and scratch aperture base/mask/control fields. Low halves generally start at bit 16, high halves are 25-bit values, and aperture controls expose aperture, scope, and temporal fields where applicable.
- `CP_MES_RS64_EXCEPTION_STATUS`, `CP_MEC_RS64_EXCEPTION_STATUS`, `CP_PFP_RS64_EXCEPTION_STATUS`, and `CP_ME_RS64_EXCEPTION_STATUS`: RS64 exception decoding for illegal instruction, misaligned address, unaligned instruction, page fault, and instruction address.
- `CP_MEC_RS64_CNTL`: MEC pipe reset/active state, instruction-cache invalidate, halt, and step controls for four MEC pipes.
- `CP_CPC_IC_OP_CNTL`: CPC instruction-cache operation fields, including invalidate-all, prime-complete, reset-error, and error-status bits.
- `CP_GFX_RS64_DC_APERTURE0..15_{BASE,MASK,CNTL}0` and `CP_GFX_RS64_DC_APERTURE0..15_{BASE,MASK,CNTL}1`: two GFX RS64 data-cache aperture banks. Each aperture has base, mask, and control words; control fields include enable, no-cache, read/write permissions, non-volatile, and cache-policy bits.
- `CH_ARB_CTRL`, `CH_DRAM_BURST_*`, `CHA_CHC_CREDITS`, `CHA_CLIENT_FREE_DELAY`, `CHI_CHR_REP_FGCG_OVERRIDE`, `CHC_CTRL`, `CHC_STATUS`, and `CHC_STATUS2`: CPWD channel/fabric controls and diagnostics.
- `GLARB_ARB_CTRL`, `GLARB_DRAM_BURST_*`, `GLARBA_GLARBC_CREDITS`, `GLARBA_CLIENT_FREE_DELAY`, `GLARBI_GLARBR_REP_FGCG_OVERRIDE`, `GLARBC_CTRL`, `GLARBC_STATUS`, and `GLARBC_CTRL2`: GLARB/GLARBC arbitration, burst, credit, DCC, CREST, and status fields.
- `*_PERFCOUNTER*_LO/HI`: 32-bit low/high result halves for CPG, CPC, CPF, GRBM, GE1, GE2 distributed, GC EA CPWD, CHC, GLARBA, GLARBC, RLC, GCR, and CHA counters.
- `*_PERFCOUNTER*_SELECT` and `*_SELECT1`: event selection and counter mode fields. Common patterns include 10-bit `PERF_SEL` lanes, paired select registers for multiple events, `CNTR_MODE`, `PERF_MODE`, and `SPM_MODE` fields.
- `GRBM_PERFCOUNTER*_SELECT` and `_SELECT_HI`: GRBM select fields with many user-defined busy/clean masks across DB, CB, TA, SX, CP, RLC, TCP, SPI, UTCL2, and related blocks.
- `CP_PERFMON_CNTL`, `*_LATENCY_STATS_SELECT`, and `*_TC_PERF_COUNTER_WINDOW_SELECT`: global CP perfmon state, SPM perfmon state, sample enable, latency-stat index/clear/enable, and TC window index/always/enable fields.
- `CP_DRAW_OBJECT`, `CP_DRAW_OBJECT_COUNTER`, `CP_DRAW_WINDOW_*`, and `CP_DRAW_WINDOW_CNTL`: draw object counters and draw-window bounds/control fields.
- `RLC_SPM_*`: RLC streaming performance monitor control, ring base/size/pointers, segment thresholds, global/SE mux select address/data, SE user data words, accumulator data/SWA/control RAM addressing/data, control RAM offsets, and the start of accumulator status.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU consumers:

1. Select the GC 12.1.0 register headers for the active ASIC generation.
2. Choose the matching register address from `gc_12_1_0_offset.h`.
3. Read an existing register value, prepare an indexed/debug/perf access, or construct a command-packet/MMIO register write.
4. Use the `__SHIFT` and `__MASK` pairs to pack a field value or extract a status bitfield.
5. Apply the resulting value in command processor bring-up, queue scheduling, cache maintenance, interrupt/exception handling, aperture setup, client/fabric tuning, draw-window gating, perf counter programming, SPM setup, hang analysis, or reset/recovery.

For MES and MEC RS64 state, initialization and recovery paths program vectors, program counters, local/instruction/scratch aperture windows, VMID/cache policy, timer compare registers, doorbells, process quantum, interrupt enables, and pipe reset/halt/step controls before or during queue execution. Interrupt and hang-dump paths decode pending interrupts, exception status, instruction pointers, GP registers, CSR-style counters, and interrupt data words.

For GFX RS64 aperture state, consumers program base/mask/control triples for two banks of 16 data-cache apertures. Cache maintenance paths use instruction/data cache operation fields and may poll completion/status bits. The header does not encode the ordering, polling, privilege, or clear semantics required by hardware.

For CH/GLARB and performance monitoring, runtime setup code configures arbitration, burst, credit, DCC/compression, CREST, and clock-gating override fields, then diagnostics read status and counter fields. Perf code programs select registers, enables global perfmon/SPM state, optionally configures TC windows and latency-stat selectors, and reads low/high counter result halves. RLC SPM setup programs ring memory, mux selections, segment layout, accumulator RAMs, and status/overflow handling through fields defined here and in the following chunk.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe GPU register fields whose state is owned by hardware, firmware, and AMDGPU runtime programming.

MES/MEC/GFX RS64 program-counter, vector, local/instruction/scratch aperture, VMID/cache policy, timer, doorbell, quantum, cache-operation, and aperture-control registers are persistent engine state until reprogrammed, reset, or power-cycled. Incorrect field packing can start firmware execution at the wrong address, leave a pipe halted or reset, send doorbells to the wrong queue, misconfigure process scheduling, deny firmware access to local memory, or apply the wrong cacheability policy.

Exception, pending-interrupt, interrupt-data, GP, MIP/timer, cycle/time/instret, and instruction-pointer registers are live diagnostic state. Some status bits may be sticky, latched, read-only, clear-on-write, or write-one-to-clear, but those semantics are not represented by the generated masks.

Data-cache aperture descriptors are stateful memory windows. Base/mask/control triples determine which address regions RS64 engines can read/write and how those accesses are cached. Misaligned bases, incorrect masks, stale permissions, or bad non-volatile/cache-policy bits can cause command processor faults, coherency bugs, unintended memory exposure, or silent performance regressions.

CH/GLARB controls persist as client/fabric policy. They affect arbitration, burst behavior, credits, repeater clock gating, DCC compression behavior, error detection/clearing, CREST mode, buffer depth, and request/data flow control. Full-register writes are risky because adjacent bits may be reserved, status-like, or side-effecting.

Performance counter and latency-stat result fields are hardware-updated state. Low/high counter pairs may require a documented latch/snapshot sequence to avoid torn 64-bit reads. `CP_PERFMON_CNTL` and SPM fields persist global measurement state, while RLC SPM ring base/size/pointers and mux/accumulator RAM fields describe memory-backed sample collection state that can outlive a single read.

The chunk boundary matters for `RLC_SPM_ACCUM_STATUS`: lines 17735-17740 define status field shifts for `NumbSamplesCompleted`, `AccumDone`, `SpmDone`, `AccumOverflow`, and `AccumArmed`, but the matching masks are outside this assigned range.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.1.0 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h` provides matching register addresses.
- The matching generated default/reset header, when present for this register family, provides expected reset values for many fields.
- Common AMDGPU register helpers provide field packing/extraction and MMIO, indexed-register, or command-packet access mechanisms.
- AMDGPU GFX, CP, MES, MEC, KFD/compute scheduling, queue doorbell setup, firmware bring-up, reset/recovery, suspend/resume, SR-IOV/virtualization, debugfs, perf counter, SPM, and hang-dump paths rely on these bit assignments.

Integration points include MES/MEC firmware startup, RS64 exception reporting, CP instruction/data cache invalidation, process quantum and doorbell routing, local/instruction/scratch memory windows, GFX RS64 data-cache aperture programming, CH/GLARB fabric tuning, DCC/compression diagnostics, GRBM/CPG/CPC/CPF/GE/CH/GLARB counter programming, CP draw-window filtering, latency-stat collection, TC window selection, and RLC SPM ring/mux/accumulator configuration.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but writes the wrong hardware bits or decodes misleading status.
- This chunk starts inside `CP_MES_IC_OP_CNTL` and ends inside `RLC_SPM_ACCUM_STATUS`; adjacent chunks are required for complete register comments and the final status masks.
- MES, MEC, and GFX RS64 groups are similar but not interchangeable. Assuming symmetry can miss pipe counts, bank suffixes, cache-policy fields, scope fields, or engine-specific interrupt/exception meanings.
- Low/high address and counter halves are easy to misuse. Firmware vectors, GP registers carrying addresses, aperture bases/masks, ring bases, and 64-bit perf counters may have alignment, address-unit, or snapshot rules outside this header.
- Reset, halt, step, cache invalidate, bypass-all, DCC error-clear, perfmon state, sample-enable, latency clear, and SPM arm/status fields can have side effects. Debug tooling should avoid casual writes and preserve reserved bits.
- Doorbell and process-quantum fields affect scheduling. Incorrect offsets, enable bits, hit-bit handling, quantum duration, or scale can stall queues, target the wrong pipe, or distort preemption/fairness.
- Data-cache aperture permission/cacheability bits can affect isolation and correctness. Bad base/mask/control values can expose unintended memory, make required memory uncached, or fault RS64 firmware.
- CH/GLARB credit, burst, DCC, CREST, and clock-gating controls are dense mode registers. Incorrect packing can cause hangs, stalls, DCC errors, bandwidth regressions, or misleading performance data.
- Performance counter select registers encode multiple event lanes per register. Mixing `PERF_SEL`, `PERF_SEL1/2/3`, `CNTR_MODE`, `PERF_MODE`, and `SPM_MODE` fields can produce valid-looking but semantically wrong measurements.
- RLC SPM ring and accumulator fields involve memory-backed sampling. Wrong ring base/size/pointers, segment counts, mux selections, accumulator RAM addresses, or status interpretation can corrupt samples or hide overflow.

## Test Signals

Useful validation is primarily generated-data consistency, build coverage, and hardware/runtime diagnostics:

- Kernel build coverage for AMDGPU files that include `gc_12_1_0_sh_mask.h`, especially GC 12.1.0 GFX, CP, MES, MEC, KFD/compute, reset, virtualization, debug, perf, and SPM paths.
- Mechanical comparison against AMD's authoritative GC 12.1.0 register database to confirm every `__SHIFT` and `__MASK` value in this slice.
- Cross-checks that registers in this chunk have matching address macros in `gc_12_1_0_offset.h` and expected defaults in the matching default header where generated.
- Static sanity checks that masks align with shifts, full-width fields use `0xFFFFFFFFL`, low/high address halves retain expected widths, aperture families remain structurally consistent, and repeated perfcounter select layouts do not overlap unexpectedly.
- MES/MEC/GFX bring-up tests that validate RS64 vectors, program counters, local/instruction/scratch apertures, VMID/cache policy, pipe reset/halt/active transitions, process quantum, and doorbell behavior.
- Interrupt and exception tests that exercise pending-interrupt, interrupt-data, instruction-pointer, GP register, MIP/timer, and exception-status decode during injected faults, time interrupts, breakpoints, and recovery.
- Cache-operation tests that invalidate/prime CP instruction caches, invalidate data caches, exercise bypass-all behavior, and verify completion/status bits and post-operation coherency.
- Aperture tests that program GFX RS64 data-cache aperture banks with known base/mask/control values and verify intended read/write/cacheability behavior without unintended access.
- CH/GLARB stress tests that vary credits, burst controls, DCC compression/error handling, clock-gating overrides, CREST mode, and buffer depths under graphics/compute traffic while checking for stalls, hangs, DCC errors, or performance regressions.
- Perf counter tests that program CPG/CPC/CPF/GRBM/GE/CH/GLARB/RLC/GCR/CHA selects under controlled workloads, verify expected activity, and read low/high result halves using the required snapshot sequence.
- RLC SPM tests that configure ring base/size, write/read pointers, segment thresholds, mux selections, SE user data, accumulator RAMs, and status handling, then verify sample collection, done bits, armed state, and overflow reporting.
- Runtime warning signals include RS64 firmware startup failures, stuck MES/MEC/GFX pipes, invalid doorbell hits, repeated CP exceptions, stale cache contents after invalidation, CH/GLARB credit starvation, DCC error codes, perf counters stuck at zero, SPM ring pointer corruption, accumulator overflow, and GPU reset loops.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002598`. It covers lines 15119-17740 of `gc_12_1_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to recover the beginning of `CP_MES_IC_OP_CNTL` and the masks after `RLC_SPM_ACCUM_STATUS`.
