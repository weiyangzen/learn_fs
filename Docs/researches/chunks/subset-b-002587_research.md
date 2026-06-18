# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h lines 2453-4938

## Scope

This chunk is a generated AMD GC 12.1.0 register-offset header segment. It contains C preprocessor register-address macros and matching `_BASE_IDX` macros only; there are no functions, structs, enums, storage objects, locks, allocation paths, or executable branches in this range. Although the repository path is under a `ceph-client` source mirror, the content is AMDGPU DRM hardware metadata for the GC 12.1.0 graphics IP.

The selected range starts at the tail of `SDMA1_SDMA_QUEUE9` state, then covers SDMA1 virtualization, PSP/reset handoff, performance, and power-control register addresses. It continues through GRBM global graphics management, command-processor public debug/status registers, PA/VGT and shader compute-dispatch registers, GC CAC/EDC power-throttle controls, GC-EA/SDP arbitration and error controls, GCR controls, CP graphics-ring and queue state, HQD queue descriptors, GFXDEC0 graphics context controls, PF/VF and PF-only virtualization windows, GFXU EOP/statistics/scratch/indirect-buffer registers, and ends in the CP RS64/MES/MEC register block at `regCP_CPC_IC_OP_CNTL`.

## Purpose

`gc_12_1_0_offset.h` maps symbolic GC 12.1.0 register names to numeric register offsets used by AMDGPU code. These addresses pair with field definitions in `gc_12_1_0_sh_mask.h`; callers use the offset macro to select the register and the shift/mask header to pack or extract individual fields. The `_BASE_IDX` companion macros select the register aperture/base bank used by AMD register access helpers.

This chunk provides offsets for several high-risk driver surfaces:

- SDMA1 queue 9 metadata: mid-command data words, utilization counters, wait threshold, MQD base/control, context status, and dummy registers.
- SDMA1 privileged blocks: VM context, active function ID, virtual reset, context/public register type maps, instruction-cache base/control, PSP reset-data offset, six performance-counter selectors/results, and clock-gating control.
- GRBM and CP global management: busy/stall/status registers, soft reset, clock/power controls, trap/read/write/IOV error reporting, scratch registers, queue FIFO availability, command-index/data windows, ring read/write pointers, privilege-violation addresses, and debug data ports.
- PA/VGT/GE/WD front-end status and UTCL1 controls, including DMA FIFO depths, pipe control, shader-array unit disables, and reset debug.
- Shader/compute context registers: dispatch dimensions, start/restart coordinates, thread counts, program address/resource registers, VMID/resource limits, temporary ring size, thread trace, dispatch IDs, DDID/checksum/interleave, per-SE destination/static-thread controls, 32 compute user-data registers, relaunch/wave-restore addresses, dispatch tunnel/end, and preallocated CR/DB buffer size.
- GC CAC/EDC/DIDT/PCC/PWRBRK power instrumentation: aggregate power counters, thresholds, stretch/throttle controls, stall patterns, hysteresis, weighted-data multipliers, soft controls, and per-block activity weights.
- GC-EA CPWD/SDP arbitration, credit reservation, backdoor credit/data controls, invalid-opcode and poison/parity error injection/logging, plus SDP enable.
- CP ring, queue, HQD, MQD, doorbell, VMID, suspend/resume, DDID, HPD, watchpoint, DMA, EOP, IB, statistics, and interrupt/fence registers.
- Virtualization-specific PF/VF and PF-only windows, including unmapped queue registers, GRBM GFX selector, CP DFY debug/fetcher controls, HPD status/ROQ offsets, GCR target controls, and PF-only CAC/EDC controls.
- RS64 CP firmware register addresses for RLC, MES, and MEC microcontroller paths: machine trap vectors, interrupt enables/pending/status, program counters, GP registers, local instruction/scratch apertures, and interrupt data registers.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this slice. The interface is the generated macro contract:

- `reg<NAME>` expands to the GC 12.1.0 register offset for `NAME`.
- `reg<NAME>_BASE_IDX` selects the register base index. In this chunk, index `0` is used for many CPWD/public blocks and index `1` for SDMA privileged/perf blocks, PF/VF or PF-only apertures, GFXU, CAC/EDC, and RS64 ranges.
- Companion field-level constants are expected in `gc_12_1_0_sh_mask.h`.
- AMDGPU register helpers and packet emitters use these symbols for MMIO reads/writes, indirect register access, PM4 command construction, queue setup, debug dumps, suspend/resume, reset, and virtualization paths.

Prominent macro families include `regSDMA1_SDMA_*`, `regGRBM_*`, `regCP_*`, `regCPC_*`, `regCPF_*`, `regCPG_*`, `regVGT_*`, `regGE_*`, `regWD_*`, `regIA_*`, `regCOMPUTE_*`, `regGC_CAC_*`, `regGC_EDC_*`, `regEDC_*`, `regDIDT_*`, `regPCC_*`, `regPWRBRK_*`, `regGC_EA_CPWD_*`, `regGCR_*`, `regRLC_*`, `regSCRATCH_REG*`, and RS64-specific `regCP_RLC_*`, `regCP_MES_*`, and `regCP_MEC_*`.

The chunk also contains intentional aliases where multiple symbolic names share one offset, such as `regCP_RB0_RPTR`/`regCP_RB_RPTR`, `regCOMPUTE_RELAUNCH`/`regCOMPUTE_RELAUNCH_STATE_PAYLOAD`, `regCOMPUTE_STATIC_THREAD_MGMT_SE*`/`regCOMPUTE_DESTINATION_EN_SE*`, `regCP_DDID_*`/`regCPC_DDID_*`, `regCP_HQD_DMA_OFFLOAD`/`regCP_HQD_OFFLOAD`, `regCP_HQD_HQ_SCHEDULER*`/`regCP_HQD_HQ_STATUS*` or `CONTROL*`, and low/high aliases for append, atomic, ring, and MQD registers. These aliases are part of the generated hardware naming surface and should not be deduplicated without checking call-site semantics.

## Control Flow

This header has no runtime control flow. Its behavior is compile-time macro substitution.

The implied driver flow is:

1. Select GC 12.1.0 ASIC support and include this offset header.
2. Choose a symbolic `reg...` offset for the relevant engine or block.
3. Use the matching `_BASE_IDX` and AMDGPU register-access helper to address the correct MMIO or indirect aperture.
4. Optionally combine the offset with field masks from `gc_12_1_0_sh_mask.h`.
5. Read status/debug registers, write control/configuration registers, emit PM4 packets, initialize queues, program compute dispatch state, collect counters, or perform reset/preemption/virtualization operations.

Runtime sequencing is defined outside this generated header. For example, queue setup must program MQD/ring/doorbell/pointer registers in the order required by CP or SDMA hardware; reset and preemption paths must coordinate status polling and quiescence; performance-counter paths must select/configure counters before reading low/high result registers; EOP and fence programming must compose address/data pairs correctly; and RS64 microcontroller registers require firmware-aware sequencing.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They name hardware registers whose state is owned by the GPU, firmware, and AMDGPU runtime.

Several groups represent persistent or semi-persistent GPU context state:

- SDMA queue and CP/HQD/MQD registers hold queue descriptors, base addresses, read/write pointers, VMIDs, priorities, quantum, dequeue state, doorbell controls, EOP buffers, IB pointers, and context-save locations. These values survive for the lifetime of a queue and are rebuilt during queue creation, suspend/resume, reset recovery, and preemption.
- `COMPUTE_*` registers represent compute dispatch and shader ABI state: program addresses, resource limits, user data, dispatch dimensions, restart coordinates, scratch bases, thread management, and relaunch/wave-restore metadata.
- GRBM, CP, PA/VGT, GCR, GC-EA, and CAC/EDC controls are global block configuration or status. Some are passive readback points; others have side effects such as soft reset, invalidation, error injection, throttle control, or command/debug-data access.
- Counter and statistics pairs such as SDMA perf counters, CAC/EDC power deltas, CP pipe statistics, shader invocation counters, primitive counters, and EOP/fence registers are live hardware state. Low/high pairs must be read and interpreted using the hardware's latching rules, not as ordinary independent variables.
- PF/VF and PF-only blocks expose virtualization-sensitive state. Unmapped queues, doorbells, privilege violations, active function IDs, IOV error FIFOs, virtual reset requests, and PF-only debug/configuration registers can affect or reveal multi-function GPU state.

Because this is an offset header, it cannot describe volatility, read-to-clear behavior, write-one-to-clear bits, alignment requirements, or register ordering constraints. Call sites must apply the hardware programming guide and surrounding AMDGPU helper contracts.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.1.0 register family remaining synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h` supplies field shifts and masks for these register names.
- Other AMDGPU GC 12.1.0 generated headers and firmware interfaces provide defaults, packet definitions, and engine-specific programming sequences.
- AMDGPU MMIO, indirect-register, and PM4 helper layers consume the `reg...` and `_BASE_IDX` symbols.

Likely integration points include SDMA ring/MQD setup, CP graphics and compute queue initialization, KFD/MES queue scheduling, GPU reset and preemption, suspend/resume context save, command submission, EOP fence signaling, doorbell programming, VMID assignment and reset, performance counter collection, debugfs/register dumps, RAS/ECC or error-injection diagnostics, virtualization/PF-VF isolation, power throttling and clock/power management, GCR/cache controls, and hang diagnosis through busy/stall/status registers.

## Risks And Edge Cases

- Generated-offset drift is the primary risk. A wrong numeric offset or `_BASE_IDX` compiles cleanly but can read or write the wrong hardware register.
- This chunk begins and ends mid-family. It starts after earlier SDMA1 queue 9 definitions and ends at the first `CP_CPC_IC_OP_CNTL` line after the MEC RS64 block; adjacent chunks are required for complete per-file conclusions.
- Aliased register names share offsets intentionally. Naive duplicate-removal or mechanical renaming can break call sites that depend on semantic names for different engines, phases, or access modes.
- Split address and data pairs are common: base addresses, read/write pointer report addresses, EOP/fence addresses, command-buffer bases, watchpoint addresses, suspend-context-save bases, and RS64 GP/local apertures. High/low mismatches can point hardware at the wrong memory or corrupt queue state.
- Queue, HQD, MQD, doorbell, VMID, dequeue, and preemption registers are synchronization-sensitive. Misprogramming can wedge queues, lose interrupts, corrupt ring pointers, or break GPU reset recovery.
- PF/VF and PF-only address blocks are security-sensitive. Accidentally exposing PF-only debug/configuration registers to VF paths could affect isolation or leak privileged state.
- Debug/index/data register pairs such as CP/GRBM/GCR/CAC indirect windows are stateful. Concurrent or unordered accesses can select the wrong index or read stale data if callers do not serialize appropriately.
- Counter low/high registers and status registers may be volatile, latched, or clear-on-read depending on hardware rules not expressed here. Test code should avoid assuming ordinary memory semantics.
- Error-injection and reset controls, including GC-EA poison/parity injection, GRBM/CP soft reset, SDMA virtual reset, and VMID reset/preempt registers, have side effects and should be gated to diagnostic or recovery paths.
- Performance and throttle controls in CAC/EDC/DIDT/PCC/PWRBRK families can affect clocks, stalls, and power behavior. Incorrect offsets may manifest as performance loss or thermal/power anomalies rather than immediate functional failure.
- Reserved, dummy, spare, and `NOWHERE` registers are present. Their symbolic existence does not make arbitrary writes safe.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, and hardware/runtime diagnostics:

- Kernel build coverage for AMDGPU GC 12.1.0 files that include `gc_12_1_0_offset.h`.
- Mechanical comparison against AMD's authoritative GC 12.1.0 register database for every offset and `_BASE_IDX` in lines 2453-4938.
- Cross-checks that registers in this chunk have matching field definitions in `gc_12_1_0_sh_mask.h` where fields are expected.
- Static checks for paired low/high registers, contiguous repeated families, intentional alias groups, and correct base-index transitions at address-block boundaries.
- Runtime queue tests covering SDMA1 queue state, CP ring setup, HQD/MQD programming, doorbell updates, EOP fence signaling, IB submission, dequeue/preemption, and VMID reset.
- Compute dispatch tests that exercise user-data registers, dispatch dimensions, scratch bases, resource limits, restart/relaunch, wave restore, and per-SE static thread controls.
- Suspend/resume and GPU reset tests that restore queue state, context-save buffers, ring pointers, CP/SDMA/GRBM status, and RS64 firmware-facing registers.
- Performance and diagnostics tests that configure SDMA counters, CP pipe stats, shader invocation counters, CAC/EDC power counters, throttle status, and debug index/data ports.
- Virtualization tests for active function ID, virtual reset, PF/VF unmapped queues, doorbell banks, privilege violation addresses, IOV errors, and PF-only register access controls.
- Error-path tests for UTCL1 errors, GC-EA invalid opcode/parity/poison logs, ECC first occurrence, fatal CP errors, read/write error registers, and stall/busy status dumps.
- Warning signals include GPU hangs during queue initialization or preemption, bad fences/EOP completion, wrong ring pointers, broken compute dispatch, missing interrupts, impossible busy/stall dumps, malformed performance counters, virtualization isolation failures, or unexpected throttling/power behavior.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002587`. It covers lines 2453-4938 of `gc_12_1_0_offset.h`; the merge/reconciliation lane should combine it with adjacent chunks to complete the full generated GC 12.1.0 offset-header analysis.
