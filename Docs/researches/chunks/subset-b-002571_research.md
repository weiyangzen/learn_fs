# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 5107-7581

## Scope

This chunk is a generated AMD GC 12.0.0 shift/mask register-header segment. It contains only C preprocessor constants: each register field has a `__SHIFT` bit position and a matching `_MASK` bit mask used by AMDGPU register helpers to compose and decode 32-bit hardware register values. There are no functions, structs, enums, executable branches, memory allocations, locks, callbacks, or persistence mechanisms in this range.

The selected lines start inside the SDMA1 queue 5 mid-command state family, after the `SDMA1_QUEUE5_MIDCMD_DATA0` comment from the previous chunk. The range then covers the remaining SDMA1 queue 5 tail fields, complete SDMA1 queue 6 and queue 7 queue-control/state fields, SDMA1 hypervisor/PSP/performance/power address blocks, GRBM status/control/error/trap/scratch fields, CP CPC/CPF/ME/PFP queue and diagnostic fields, PA/GE/VGT/UTCL1 fields, and the first part of compute dispatch state. The chunk ends in the middle of `COMPUTE_REQ_CTRL`; the remaining masks and any following compute registers continue in the adjacent chunk.

Although the repository path is nested under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata for the GC 12.0.0 graphics IP and is not Ceph filesystem logic.

## Purpose

`gc_12_0_0_sh_mask.h` describes hardware bit layouts for GC 12.0.0 registers. Driver code pairs these macros with register address symbols from the companion GC 12.0.0 offset header and, where available, generated default/reset-value headers. The usual consumers are AMDGPU low-level register helpers such as `REG_SET_FIELD` and `REG_GET_FIELD`, MMIO read/write paths, command-packet register programming, debug dump decoders, performance-counter tools, reset handling, virtualization paths, and queue setup code.

This chunk focuses on four broad surfaces:

- SDMA1 queue programming and SDMA1 engine control: ring buffers, indirect buffers, doorbells, CSA/MQD addresses, VMIDs, AQL controls, preemption, context switch/error status, mid-command save/restore data, instruction cache controls, virtualization reset/active function state, performance counters, and SDMA1 clock-gating override fields.
- GRBM global graphics management: busy/clean status by shader engine, read/write/invalid-pipe error attribution, soft reset controls, interrupt enables, trap registers, UTCL2 invalidation ranges, fence ranges, clock/power tuning fields, scratch registers, SA disable fields, and generated workaround-style clock-gating fields.
- CP command-processor diagnostics and queue internals: CPC/CPF status, busy/stall breakdowns, free-count registers, scratch index/data, command index/data windows, ROQ/STQ/MEQ thresholds and pointers, ring read-pointer state, write-pointer polling delay, debug/interrupt status, and privilege-violation addresses.
- PA/GE/VGT/UTCL1 and compute launch state: geometry/watchdog and UTCL1 fault/control fields, DMA/draw FIFO depths, GE privilege/status, VGT debug/reset fields, compute dispatch dimensions, program address/resource registers, scratch/dispatch-packet addresses, VMID, resource limits, CU enable/static-thread-management fields, temporary ring sizing, restart coordinates, thread trace, dispatch IDs, and the beginning of compute request-control throttling fields.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public contract is the generated macro naming scheme:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the field's 32-bit mask.
- Matching register addresses are expected in the GC 12.0.0 offset header, commonly as `mm...` register symbols.
- Consumers should pack and extract values through the AMDGPU register-field helpers instead of hard-coding these constants again.

Important macro families in this slice include:

- `SDMA1_QUEUE5_*`, `SDMA1_QUEUE6_*`, and `SDMA1_QUEUE7_*`: SDMA queue state for mid-command data, wait thresholds, MQD base/control, dequeue requests, context status, ring buffer base/read/write pointers, writeback/poll addresses, indirect-buffer base/offset/size, doorbell enable/capture/log/offset, CSA addresses, scheduling IDs and quantum, AQL packet controls, minor pointer updates, preemption, and context-switch exception bits.
- `SDMA1_VM_*`, `SDMA1_ACTIVE_FCN_ID`, `SDMA1_VIRT_RESET_REQ`, `SDMA1_MCU_*`, and `SDMA1_IC_*`: SDMA1 virtualization context address, active PF/VF attribution, virtual reset requests, VM commands, microcontroller halt/reset/debug selection, instruction-cache base/control, invalidate/prime state, VMID, execute-disable, MALL policy, GPA, and auto-prime controls.
- `SDMA1_PERFCNT_*` and `SDMA1_PERFCOUNTER*`: SDMA1 event selection, selector extensions, counter modes, enable/clear controls, result-selection triggers, low/high result words, and compare-value fields.
- `GFX_ICG_SDMA1_CTRL`: SDMA1 medium-grain clock-gating soft override and hysteresis bits for register, pointer, PIO, MCU, copy, serving, command fetch, memory request/cache/channel, instruction cache, performance counter, and core sub-block clocks.
- `GRBM_*`: global graphics register bus manager controls and status. These include global busy/clean bits, per-SE status for SE0-SE3, status3 MES/GL/cache busy bits, soft reset bits for CP/RLC/UTCL2/GFX/CPF/CPC/CPG/CAC/EA/SDMA, read/write error attribution, interrupt enables, trap operation/address/data masks, DSM bypass, chip revision, IH credit, power-halt requests, UTCL2 invalidation range start/end, invalid pipe attribution, fence ranges, clock-gating workaround fields, scratch registers, and interface bridge disable.
- `CP_CPC_*`, `CP_CPF_*`, and generic `CP_*`: command processor status, busy, stalled, free-count, header dump, scratch, command window, ROQ/STQ/MEQ threshold/availability/stat pointer fields, ring read pointer fields, write-pointer delay/polling, context status, interrupt debug status, and privilege violation address fields.
- `VGT_*`, `GE_*`, `GFX_PIPE_CONTROL`, `WD_UTCL1_*`, and `IA_UTCL1_*`: primitive assembly/draw FIFO depth, VGT debug/reset masks, geometry-engine busy and privilege/status fields, graphics pipe control, and UTCL1 fault/retry/PRT status/control for work distributor and input assembler clients.
- `COMPUTE_*`: compute dispatch state through the start of `COMPUTE_REQ_CTRL`, including dispatch initiator flags, X/Y/Z dimensions and starts, X/Y/Z thread counts and interleave fields, pipeline/perf enable, program and dispatch/scratch addresses, program resource descriptors, VMID, resource limits, per-SE CU routing/static thread management for SE0-SE3, temporary ring size, restart coordinates, thread tracing, miscellaneous reserved state, dispatch ID, and threadgroup ID.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied driver flow is:

1. Select GC 12.0.0 register metadata for the active ASIC.
2. Select the matching register address from the GC 12.0.0 offset header.
3. Read an existing register value or construct a new MMIO/command-packet register value.
4. Use the `__SHIFT` and `_MASK` pairs, usually via `REG_SET_FIELD` or `REG_GET_FIELD`, to encode or decode the relevant fields.
5. Apply the value in SDMA queue setup, SDMA preemption/recovery, virtualization, performance-counter programming, clock/power management, GRBM reset/status/error handling, CP diagnostics, geometry/UTCL fault handling, or compute dispatch setup.

For SDMA queues, typical runtime sequencing programs ring bases and sizes, writeback/polling addresses, doorbells, VMID/MQD state, AQL/preemption controls, and then monitors context status or context-switch exception bits during execution and recovery. For performance counters, consumers select events and modes, clear/enable counters, gate result collection with result-control triggers, and read low/high result registers. For GRBM/CP status, reset, and diagnostics, code usually polls clean/busy bits, decodes failed read/write/pipe access attribution, asserts soft reset bits during recovery, and dumps CP/CPC/CPF busy and stall registers for hang analysis. For compute state, command processor or queue setup code writes dispatch dimensions, program addresses/resource descriptors, VMID, CU enable masks, scratch/temporary-ring information, and initiator flags before work is launched.

This generated header does not encode ordering rules, required waits, clear-on-read semantics, sticky status behavior, latching rules for high/low counters, reset timing, or reserved-bit preservation policies. Those requirements live in AMDGPU engine code, firmware contracts, and hardware programming documentation.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe stateful GPU registers controlled by hardware, firmware, and AMDGPU runtime code.

SDMA queue fields represent persistent queue programming until the queue is disabled, reprogrammed, preempted, reset, or lost over a power transition. Ring base/control, read/write pointers, writeback and polling addresses, doorbell offsets, VMID/MQD fields, CSA addresses, AQL controls, and scheduling state must remain consistent with queue memory and process ownership. Mid-command data registers are save/restore state for preemptible operations and can become critical during queue preemption or recovery.

SDMA hypervisor and PSP-facing fields carry virtualization and microcontroller state. Active function ID, virtual reset request bits, VM context addresses, instruction-cache base/control, and execute-disable controls can affect PF/VF isolation, firmware execution, and queue recovery. These fields should be treated as privileged, side-effecting control state rather than passive metadata.

GRBM and CP status/error/interrupt/debug fields are a mixture of live status, sticky diagnostic state, and side-effecting controls. Busy/clean bits reflect active hardware pipelines. Soft reset and power-halt fields directly change engine state. Read/write error, invalid pipe, privilege-violation, interrupt debug, and UTCL1 fault fields are diagnostic state that may require hardware-specific clear or acknowledge sequences outside this header.

Compute registers are active dispatch state. Program address, resource descriptors, VMID, dispatch dimensions, thread counts, static thread/CU masks, scratch addresses, temporary-ring sizing, restart coordinates, and initiator bits can remain relevant across dispatch execution, preemption, debug capture, or recovery. Incorrect field packing can launch the wrong shader, use invalid resource counts, target disabled compute units, or corrupt scratch/restart behavior.

Performance counter selectors and controls persist while counters accumulate. Low/high result registers may need a hardware-defined snapshot or read sequence to avoid torn values; the mask header cannot express that atomicity requirement.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.0.0 register family staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h` should provide matching register address macros for these field definitions.
- Any matching GC 12.0.0 default/reset header should remain consistent with these masks.
- Common AMDGPU register helpers provide the actual field packing/extraction and MMIO or command-packet access mechanisms.
- AMDGPU SDMA, GFX, CP, KFD/compute, virtualization/SR-IOV, reset, suspend/resume, performance monitoring, debugfs, and hang-dump paths are the likely consumers.

Integration points include SDMA ring creation/teardown, SDMA doorbell programming, MQD/CSA setup, SDMA AQL/preemption handling, SDMA context-switch exception reporting, SDMA instruction-cache and microcontroller control, per-engine performance counters, GRBM idle polling and soft reset, GRBM read/write/invalid-pipe diagnostics, trap/debug plumbing, CP command queue diagnostics, CP ring pointer and ROQ/STQ/MEQ introspection, privilege violation reporting, PA/GE/VGT debug controls, UTCL1 fault handling, compute dispatch packet setup, compute shader resource programming, CU enable/static thread management, and compute tracing/debug paths.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask still compiles but can write the wrong hardware bits or decode misleading diagnostics.
- The chunk starts and ends mid-family. `SDMA1_QUEUE5_MIDCMD_DATA0` is only partially visible at the start, and `COMPUTE_REQ_CTRL` continues after line 7581; final file-level research must merge adjacent chunks before drawing complete conclusions for those registers.
- SDMA queue 6 and 7 definitions are highly repetitive. Copy/generator mistakes can affect one queue only, producing queue-specific hangs, wrong doorbell behavior, or incorrect exception attribution.
- Address fields are not uniformly full byte addresses. Many low address fields start at bit 2 or bit 12, while high words may be full or narrow. Callers must respect alignment and split-address semantics for ring bases, read-pointer writeback, write-pointer polling, IB bases, CSA/MQD bases, SDMA IC bases, compute program addresses, and dispatch/scratch addresses.
- Doorbell, VMID, MQD, active function, and virtual reset fields are isolation-sensitive. Incorrect masks can route work to the wrong VMID/VF, lose queue notifications, or mis-handle PF/VF reset.
- Soft reset and power/clock-gating controls are side-effecting. Full-register writes that fail to preserve reserved bits around `GRBM_SOFT_RESET`, `GRBM_PWR_CNTL*`, `GFX_ICG_SDMA1_CTRL`, or clock-gating workaround fields can destabilize unrelated blocks.
- Status and error registers often contain sticky or latched bits. Decoding with the wrong mask can hide read/write errors, invalid-pipe events, privilege violations, UTCL faults, or CP interrupts during recovery.
- CP busy/stall families are dense and similar across CPC, CPF, ME, PFP, MEC, MES, ROQ, STQ, and MEQ blocks. Assuming symmetry between registers can produce incorrect hang diagnoses.
- Compute resource fields are densely packed. Incorrect widths for VGPR/SGPR counts, LDS size, exception enables, WGP mode, scratch enable, user SGPR counts, CU masks, or resource limits can cause invalid dispatches, GPU faults, or silent performance/debug anomalies.
- Performance counter high/low results can be race-prone if read without the documented latching sequence. This header only identifies bits; it does not make counter reads atomic.

## Test Signals

Useful validation for this chunk is generated-data consistency plus build/runtime coverage:

- Kernel build coverage for AMDGPU files that include `gc_12_0_0_sh_mask.h`, especially SDMA, GFX, CP, KFD/compute, reset, virtualization, debug, and perf counter paths.
- Mechanical comparison against AMD's authoritative GC 12.0.0 register database to confirm every `__SHIFT` and `_MASK` value in this line range.
- Cross-checks that every register family in this chunk has matching address macros in `gc_12_0_0_offset.h` and expected defaults in the matching generated default header where applicable.
- Static mask sanity checks: masks should align with shifts, repeated SDMA queue 6/7 families should remain structurally identical where hardware intends, full-width data fields should use full masks, split address masks should match documented alignment, and fields should not overlap unless explicitly documented.
- SDMA tests that initialize queues 5 through 7, program ring bases, writeback/polling addresses, doorbells, MQD/CSA state, AQL controls, preempt/dequeue requests, and verify pointer progress plus context status under normal and preempted workloads.
- Virtualization tests that exercise SDMA active function ID, VF/PF reset requests, VM context registers, and doorbell/error attribution with expected VF/VMID isolation.
- Perf counter tests that select SDMA1 events, clear/enable counters, run controlled copy workloads, read low/high results, and verify monotonic or expected event activity.
- GRBM reset/idle tests that poll global and per-SE busy/clean bits, issue reset paths, and verify recovery without stale busy bits or unexpected soft-reset side effects.
- Hang/debug dump tests that decode GRBM read/write errors, invalid-pipe events, CP/CPC/CPF busy and stalled bits, CP interrupt debug bits, privilege violations, and scratch/header dump registers coherently.
- UTCL1/GE/VGT tests that exercise fault/retry/PRT reporting, geometry status, DMA/draw FIFO depth reporting, and VGT reset/debug fields under controlled fault and draw workloads.
- Compute dispatch tests that validate program address/resource packing, VMID, dispatch dimensions, thread counts, CU masks, scratch/temporary-ring state, restart coordinates, thread trace enablement, dispatch IDs, and request-control throttling once the adjacent `COMPUTE_REQ_CTRL` masks are included.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002571`. It covers lines 5107-7581 of `gc_12_0_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the partial SDMA1 queue 5 and `COMPUTE_REQ_CTRL` register families and to place these SDMA, GRBM, CP, PA/GE/VGT/UTCL1, and compute definitions in the full GC 12.0.0 register map.
