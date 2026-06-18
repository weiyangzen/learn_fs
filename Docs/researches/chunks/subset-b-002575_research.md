# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 15147-17777

## Scope

This chunk is a generated AMD GC 12.0.0 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `__SHIFT` value and a matching `__MASK` value used by AMDGPU register helpers to compose or decode 32-bit MMIO/indexed-register values. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines begin in the tail of a graphics/VGT block, with fast-launch geometry-shader workgroup dimensions, GS output primitive type, transform-feedback memory-base high bits, ordered-ID base, and primitive-ID reset fields. The main body then covers the `gc_gfx_cpwd_cpwd_cprs64dec` address block: RS64 command-processor register fields for MES, MEC, and GFX/PFP/ME microcontroller state, interrupts, apertures, scratch/local memory windows, process quantum, instruction/data cache controls, exception status, and performance-control state. The chunk then covers `gc_gfx_cpwd_cpwd_chdec` client/DRAM/compression/credit controls, `gc_gfx_cpwd_cpwd_gl2dec` GL2 cache, address match, writeback/invalidate, reset, credit, compression, and GL2A arbitration fields, and ends in `gc_gfx_cpwd_cpwd_perfddec` after GE2 distributed performance counter 3 high-word fields.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for the GC 12.0.0 graphics IP and is not Ceph filesystem code.

## Purpose

`gc_12_0_0_sh_mask.h` supplies bit layouts for GC 12.0.0 registers. Driver code pairs these macros with register addresses from the matching `gc_12_0_0_offset.h` header and, where available, generated reset/default values. Consumers normally use the constants through helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` so register fields can be packed or extracted without hard-coded bit positions.

This chunk is centered on command processor RS64 state and cache/client fabric control:

- Geometry/VGT tail fields for GS fast-launch dimensions, output primitive type, transform-feedback address high bits, ordered ID base, and primitive-ID reset value.
- `CP_MES_*` fields for MES RS64 program counter, interrupt routine/vector addresses, control/reset/active/halt/step bits, priority counters, scratch access, machine CSR-style status/cause/bad-address/cycle/time/instruction-retired registers, cache invalidation, timer compare, process quantum, doorbell controls, general-purpose registers, local/instruction/scratch aperture windows, metadata, exception status, interrupt data, and 16 data-cache aperture descriptors.
- `CP_MEC_*` fields mirroring the RS64 MEC command-processor state: control/reset/active bits, interrupt/status registers, VMID/cache policy, data-cache operations, general-purpose registers, local/instruction/scratch aperture windows, exception and pending-interrupt status, interrupt data, and 16 data-cache aperture descriptors.
- `CP_GFX_RS64_*`, `CP_PFP_RS64_*`, and `CP_ME_RS64_*` fields for graphics command processor interrupt enables/status, data-cache controls, local/instruction/scratch apertures, exception status, perf-count controls, timer/MIP registers, per-engine general-purpose registers, instruction pointers, pending interrupts, and two banks of 16 data-cache aperture descriptors.
- `CH*` and `CHA/CHC/CHI` fields for graphics client arbitration, DRAM burst masks and enables, client credits, free delay, compression mode, compressor override, FGCG override, compression controller limits, status counters, and subchannel/decompression controls.
- `GL2C_*` and `GL2A_*` fields for L2 cache control/status, client arbitration, address match, writeback/invalidate, soft reset, credit throttling, DCC/compression modes, safe modes, hashing, response throttling, and per-channel disable behavior.
- `CPG/CPC/CPF/GRBM/GE1/GE2_DIST` performance counter and latency-stat data words.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register-address symbols live in the companion offset header, commonly with `mm...` names matching these register names.
- AMDGPU callers normally access these fields through `REG_SET_FIELD`, `REG_GET_FIELD`, read-modify-write MMIO helpers, command-packet register programming, debugfs/perf tooling, reset paths, virtualization handling, and hang-dump code.

The main macro families in this slice are:

- `GE_GS_FAST_LAUNCH_WG_DIM*`, `VGT_GS_OUT_PRIM_TYPE`, `VGT_TF_MEMORY_BASE_HI`, `GE_GS_ORDERED_ID_BASE`, and `VGT_PRIMITIVEID_RESET`: graphics pipeline fields for geometry fast launch, primitive output, transform-feedback addressing, ordered IDs, and primitive ID reset.
- `CP_MES_*`: MES RS64 control and observability. Notable fields include `MES_PIPE*_RESET`, `MES_PIPE*_ACTIVE`, `MES_HALT`, `MES_STEP`, priority counters, interrupt masks/status, indexed scratch access, instruction pointer, machine status/exception CSRs, icache/dcache operations, process quantum timers, doorbell index/enables, local and instruction aperture base/mask/window controls, scratch aperture, metadata-control mode, exception flags, and interrupt data registers 16 through 31.
- `CP_MES_DC_APERTURE0..15_{BASE,MASK,CNTL}` and `CP_MEC_DC_APERTURE0..15_{BASE,MASK,CNTL}`: data-cache aperture descriptors. Control words expose enable, no-cache, read, write, non-volatile, and cache-policy bits, while base/mask words describe the address window.
- `CP_MEC_RS64_*` and `CP_MEC_*`: MEC RS64 program counter, vector, control, interrupt, instruction pointer, MIP/timer compare, VMID/cache policy, cache operations, GP registers, local/instruction/scratch apertures, perf-count control, pending interrupt, exception status, and interrupt data.
- `CP_CPC_IC_OP_CNTL`: command processor instruction cache operation controls, including invalidation, prime, invalidate-all, prime-complete, reset-error, and error reporting fields.
- `CP_GFX_RS64_*`: graphics RS64 interrupt, interrupt enable, data-cache, local/instruction/scratch, exception, perf-count, MIP/timer, GP, instruction pointer, pending interrupt, and aperture-bank fields. The aperture definitions are split into bank `0` and bank `1`, each carrying aperture indices 0 through 15.
- `CP_PFP_RS64_EXCEPTION_STATUS` and `CP_ME_RS64_EXCEPTION_STATUS`: PFP and ME exception-status fields for instruction-access faults, illegal instruction, breakpoint, environment call, misaligned data, data-access faults, and time interrupts.
- `CH_ARB_CTRL`, `CH_DRAM_BURST_*`, `CHA_*`, `CHI_CHR_REP_FGCG_OVERRIDE`, and `CHC_*`: channel/client/fabric control fields for arbitration, burst behavior, credit accounting, compression scheme and partition behavior, compressor override, power-gating override, decompressor limits, busy/status counters, response buffer status, and ID remap.
- `GL2C_*`: GL2 cache controls for write policy, uncached behavior, clock-gating modes, virtual-miss and miss-under-miss behavior, L1 policy, queue modes, disabled request classes, address matching, writeback/invalidate, reset, DCC and compression handling, safe modes, EA credits, discard-stall control, and supported compression schemes.
- `GL2A_*`: GL2A address matching, arbitration, credit-safe registers, high-priority and write-combine timeout behavior, channel hash bit selection, disable masks, and response throttling.
- `CPG_PERFCOUNTER*`, `CPC_PERFCOUNTER*`, `CPF_PERFCOUNTER*`, `*_LATENCY_STATS_DATA`, `GRBM_PERFCOUNTER*`, `GE1_PERFCOUNTER*`, and `GE2_DIST_PERFCOUNTER*`: low/high 32-bit counter result and latency data fields. The chunk ends exactly on `GE2_DIST_PERFCOUNTER3_HI`.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU consumers:

1. Select the GC 12.0.0 register header for the active ASIC generation.
2. Choose the matching register address from `gc_12_0_0_offset.h`.
3. Read an existing register value, prepare an indexed-register/debug/perf access, or construct an MMIO/command-packet register write.
4. Use the `__SHIFT`/`__MASK` pairs, usually through generated register helpers, to pack a field value or extract status bits.
5. Feed the resulting value into graphics pipeline setup, MES/MEC/GFX command processor initialization, queue scheduling, interrupt handling, exception/debug capture, cache maintenance, L2/client fabric tuning, compression control, performance monitoring, reset, or power-management logic.

For RS64 command processor state, initialization and recovery paths program program-counter/vector registers, local/instruction/scratch apertures, VMID/cache policy, doorbells, process quantum, and interrupt enables before work is scheduled. Interrupt, debug, and hang paths decode pending-interrupt and exception-status registers, general-purpose registers, instruction pointers, and CSR-style cause/status/bad-address state. Cache-maintenance paths use icache/dcache operation controls and may poll completion/status bits defined here.

For CH and GL2 registers, runtime setup and tuning paths program arbitration, credit, compression, DCC, hash, safe-mode, throttle, and writeback/invalidate fields. Status fields are read by diagnostics, performance tooling, or recovery code to identify busy clients, response buffer occupancy, dropped/stalled traffic, cache invalidation state, and compression-controller activity. Performance monitoring code selects counters elsewhere, then reads the low/high result words and latency-stat data fields defined in this tail.

This header does not encode ordering requirements, polling loops, latching sequences, clear-on-read behavior, privilege restrictions, or reset sequencing; those rules live in AMDGPU engine code, firmware interfaces, and hardware programming guides.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe GPU register fields whose state is owned by hardware, firmware, and AMDGPU runtime programming.

RS64 command processor program-counter, vector, local/instruction/scratch aperture, VMID/cache policy, doorbell, process-quantum, and cache-operation registers are persistent engine state until reprogrammed or reset. Bad masks in these fields can start firmware or command processor execution at the wrong address, leave an RS64 pipe halted or reset, expose an incorrect local memory aperture, direct data/instruction fetches through the wrong cache policy, or attach a doorbell to the wrong queue.

Exception, pending-interrupt, interrupt data, MIP/timer, machine-status, cause, bad-address, and GP registers are live diagnostic state. Some fields may be sticky or require hardware-defined clearing. The field definitions here allow decoding and writing, but do not document which fields are write-one-to-clear, read-only, latched, or volatile.

Data-cache aperture descriptors are stateful windows. The base/mask/control triples for MES, MEC, and GFX RS64 engines define address regions with access permissions and cacheability policy. Incorrect packing can grant unintended read/write access, make a required region uncached, deny firmware access, or make command processor microcode fault on data/instruction/scratch references.

CH/CHA/CHC/CHI and GL2C/GL2A control fields persist as cache and fabric policy. They affect arbitration, credits, compression, DCC bypass, cache invalidation/writeback, reset behavior, hashing, high-priority routing, and throttling. These fields are high-risk for full-register writes because many bits control side effects or hardware modes; callers must preserve reserved bits unless a documented sequence requires otherwise.

Performance counter low/high result fields and latency-stat data are hardware-updated state. Counter reads may require a snapshot/latch sequence outside this header to avoid torn 64-bit values. Writeback/invalidate and soft-reset fields have side effects; completion and status bits must be interpreted according to hardware sequencing rules not represented by masks alone.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.0.0 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h` provides matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_default.h`, when present in the same generated register family, provides default/reset values for many registers.
- Common AMDGPU register helpers provide field packing/extraction and MMIO or command-packet access mechanisms.
- AMDGPU GFX, CP, MES, MEC, KFD/compute scheduling, ring/doorbell setup, firmware bring-up, reset/recovery, suspend/resume, SR-IOV/virtualization, debugfs, perf counter, and hang-dump paths rely on these bit assignments.

Integration points include geometry shader fast-launch programming, primitive/transform-feedback state, MES pipe reset/active/halt control, RS64 firmware vectors and apertures, queue doorbells and process quantum, cache invalidation and priming, command processor interrupt enables/status, exception attribution, data-cache aperture setup, compression and DCC policy, GL2 writeback/invalidate/reset sequences, cache/fabric arbitration tuning, response throttling, and performance counter reads.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but writes the wrong hardware bits or decodes misleading diagnostics.
- This chunk starts and ends mid-family. It begins after the `GE_GS_FAST_LAUNCH_WG_DIM` comment and ends on `GE2_DIST_PERFCOUNTER3_HI`; adjacent chunks are needed for the surrounding graphics and performance-counter families.
- MES, MEC, and GFX RS64 register groups are similar but not identical. Assuming symmetry can miss bank suffixes, pipe-specific bits, engine-specific interrupt enables, or different exception/status meanings.
- Split low/high address fields and aperture base/mask fields are easy to misuse. Firmware vectors, GP registers carrying addresses, local/instruction/scratch windows, and data-cache apertures may have alignment or address-unit constraints outside this header.
- Pipe reset, active, halt, step, cache invalidation, writeback/invalidate, soft reset, and compression override fields have direct side effects. Debug tooling should avoid casual writes and preserve reserved bits.
- Doorbell and process-quantum fields affect scheduling. Incorrect doorbell offsets, enable bits, or quantum durations can stall queues, signal the wrong pipe, or create fairness/preemption bugs.
- Exception and interrupt status can be sticky, latched, or clear-on-write. Treating these fields as passive status can lose evidence during hang analysis or leave interrupts asserted.
- Data-cache aperture permission/cacheability bits can affect command processor isolation and correctness. Bad aperture masks can expose unintended memory or fault firmware accesses.
- GL2 and CH controls are dense and mode-heavy. Incorrect DCC, compression, credit, hash, throttle, or safe-mode masks can cause GPU hangs, silent performance regressions, coherency bugs, or misleading perf data.
- Counter result high/low registers can be race-prone if read without the documented latching sequence. This header cannot describe atomic snapshot requirements or overflow behavior.

## Test Signals

Useful validation is primarily generated-data consistency, build coverage, and hardware/runtime diagnostics:

- Kernel build coverage for AMDGPU files that include `gc_12_0_0_sh_mask.h`, especially GC 12.0.0 GFX, CP, MES, MEC, KFD/compute, reset, virtualization, debug, and perf counter paths.
- Mechanical comparison against AMD's authoritative GC 12.0.0 register database to confirm every `__SHIFT` and `__MASK` value in this slice.
- Cross-checks that all registers in this chunk have matching address macros in `gc_12_0_0_offset.h` and expected defaults in the matching default header where generated.
- Static mask/shift sanity checks: masks should align with shifts, full-width data fields should use `0xFFFFFFFFL`, repeated aperture families should remain structurally aligned, banked GFX RS64 fields should keep consistent suffixes, and bitfields should not overlap unless documented.
- MES/MEC/GFX bring-up tests that validate RS64 program counter/vector setup, local/instruction/scratch apertures, VMID/cache policy, GP register capture, doorbells, process quantum, and pipe reset/halt/active transitions.
- Interrupt and exception tests that exercise pending-interrupt, interrupt-data, MIP/timer, exception-status, cause, bad-address, and instruction-pointer decode during injected faults, time interrupts, breakpoints, and recovery.
- Cache-operation tests that invalidate/prime CP instruction cache, invalidate data cache, perform GL2 writeback/invalidate, and verify completion/status bits and post-operation coherency.
- Aperture tests that program MES/MEC/GFX data-cache apertures with known base/mask/control values and verify intended read/write/cacheability behavior without unintended access.
- Graphics pipeline tests covering GS fast launch dimensions, GS output primitive type, transform-feedback base high bits, ordered IDs, and primitive-ID reset behavior.
- CH/GL2 stress tests that vary compression/DCC, credits, hash, throttling, response-buffer pressure, address match, soft reset, and safe-mode fields under graphics and compute traffic while checking for hangs, data corruption, or performance anomalies.
- Perf counter tests that read CPG/CPC/CPF/GRBM/GE1/GE2_DIST low/high results and latency-stat data under controlled workloads, checking expected activity and monotonicity while avoiding torn reads.
- Runtime warning signals include RS64 firmware startup failures, stuck MES/MEC/GFX pipes, invalid doorbell behavior, repeated CP exceptions, stale cache contents after invalidation, incorrect compression/DCC behavior, GL2 reset hangs, fabric credit starvation, misleading performance counters, and GPU reset loops.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002575`. It covers lines 15147-17777 of `gc_12_0_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the graphics/VGT context before line 15147 and the performance-counter definitions after `GE2_DIST_PERFCOUNTER3_HI`.
