# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h lines 12154-14604

## Scope

This chunk is a generated AMD GC 9.1 shift/mask register-header segment. It contains preprocessor constants only: every hardware register field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro for composing or decoding 32-bit GPU register values. There are no functions, structs, enums, global variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines begin in the mask tail for `CPF_UTCL1_CNTL`, then cover a large command-processor block, the `gc_cppdec2` scheduler/doorbell/status block, the `gc_spipdec` SPI scheduling/resource-reservation block, the `gc_cpphqddec` hardware queue descriptor block, and the beginning of DIDT/CAC/EDC power-management controls. Although the path is under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata, not Ceph filesystem logic.

## Purpose

`gc_9_1_sh_mask.h` supplies bit layouts for the GC 9.1 graphics IP. Driver code pairs these masks with register addresses from `gc_9_1_offset.h` and uses AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32*`, `WREG32*`, and SOC15 register-offset helpers to pack fields for MMIO writes, command-processor setup, KFD/MQD queue setup, interrupt programming, debug collection, and status decoding.

This chunk describes these hardware areas:

- CPF/CP UTCL1 fields for cache/TLB-related command-processor behavior, including bypass, invalidate, snoop, VMID dirty, no-PTE mode, and no-execute policy.
- Graphics command-processor ring-buffer state: base addresses, control words, read/write pointers, read-pointer report addresses, write-pointer polling addresses, buffer-size masks, VMID selection, active bits, doorbell control/ranges, ring priorities, and fatal/interrupt state.
- Per-ring and per-ME/MEC interrupt enable/status registers for VM doorbell writes, ECC, general protection faults, busy/empty/idle state, privileged instruction/register faults, opcode errors, timestamps, reserved-bit errors, and generic interrupts.
- CP power, memory-sleep, ECC first-occurrence, VMID reset/preempt/status, program-counter start, interrupt-routine start, context-control, context-count, instruction-queue wait-time, CPC instruction-cache, CPC op-control, and MEC F32 interrupt-disabling fields.
- `gc_cppdec2` scheduler doorbell controls for scheduler slots 0-7, doorbell clear/range fields, GFX MQD base/control, CP ring status, CPG/CPC/CPF UTCL1 status, SD control, soft reset controls, and CPC graphics control.
- `gc_spipdec` SPI arbitration, pipe cycle/percentage controls, compute-queue reset, per-CU resource-reservation masks, per-CU reservation enable masks, compute wavefront context-save control, and arbitration control.
- `gc_cpphqddec` HQD/MQD queue registers: GFX queue state, HPD status/UTCL1 error reporting, MQD base, HQD active/VMID/persistent state, queue priorities/quantum, packet-queue and indirect-buffer base/pointer/control, doorbell controls, dequeue requests, DMA/offload/semaphore/message fields, HQ scheduler/status/control, EOP ring, context-save buffers, GDS resource state, HQD error bits, AQL control, and packet-queue write-pointer memory fields.
- DIDT/CAC/EDC controls for dynamic inductive droop throttling, compute activity counters, clock-gating override, aggregation counters, power bounds, weighting by block, and the first EDC control bits.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit index of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask.
- Address symbols live in the matching GC 9.1 offset header; this file only describes field positions.

Notable macro families in this slice are:

- `CP_RB0_*`, `CP_RB1_*`, `CP_RB2_*`, and generic `CP_RB_*`: ring-buffer base/control, read/write pointer, read-pointer report address, write-pointer polling, buffer-size mask, VMID, and active-state fields.
- `CP_RB_DOORBELL_CONTROL`, `CP_RB_DOORBELL_RANGE_*`, `CP_MEC_DOORBELL_RANGE_*`, and `CP_RB_DOORBELL_CONTROL_SCH_[0-7]`: doorbell routing, offset, enable, hit-clear, range, and scheduler-slot doorbell controls.
- `CP_INT_CNTL`, `CP_INT_STATUS`, `CP_INT_CNTL_RING[0-2]`, `CP_INT_STATUS_RING[0-2]`, `CP_ME[1-2]_PIPE[0-3]_INT_CNTL`, `CP_ME[1-2]_PIPE[0-3]_INT_STATUS`, `CPC_INT_CNTL`, and `CPC_INT_STATUS`: interrupt enables and status bits for CP/CPC/MEC rings and pipes.
- `CP_ME*_PIPE_PRIORITY_CNTS`, `CP_RING_PRIORITY_CNTS`, `CP_ME*_PIPE*_PRIORITY`, and `CP_RING*_PRIORITY`: priority count and priority-selection fields for graphics and compute rings.
- `CP_FATAL_ERROR`, `CP_PWR_CNTL`, `CP_MEM_SLP_CNTL`, `CP_ECC_FIRSTOCCURRENCE*`, `GB_EDC_MODE`, `CC_GC_EDC_CONFIG`, `CP_VMID_RESET`, `CP_VMID_PREEMPT`, `CP_VMID_STATUS`, `CP_PQ_STATUS`, `CP_CONTEXT_CNTL`, and `CP_MAX_CONTEXT`: fault, power, ECC, VMID, queue, and context-control/status fields.
- `CP_CE/PFP/ME/MEC*_PRGRM_CNTR_START` and `CP_CE/PFP/ME/MEC*_INTR_ROUTINE_START`: micro-engine program counter and interrupt-routine start addresses.
- `CP_CPC_IC_*`, `CP_CPC_IC_OP_CNTL`, `CP_CPC_GFX_CNTL`, `CPG_UTCL1_*`, `CPC_UTCL1_*`, and `CPF_UTCL1_*`: CPC instruction cache, CPC graphics control, and command-processor UTCL1 error/status/control fields.
- `SPI_ARB_PRIORITY`, `SPI_ARB_CYCLES_*`, `SPI_WCL_PIPE_PERCENT_*`, `SPI_COMPUTE_QUEUE_RESET`, `SPI_RESOURCE_RESERVE_CU_*`, `SPI_RESOURCE_RESERVE_EN_CU_*`, `SPI_COMPUTE_WF_CTX_SAVE`, and `SPI_ARB_CNTL_0`: SPI queue arbitration, pipe-share, queue reset, CU reservation, and context-save controls.
- `CP_HQD_*`, `CP_HPD_*`, `CP_MQD_*`, and `CP_GFX_MQD_*`: HQD/MQD queue state, persistent state, PQ/IB/EOP rings, doorbells, dequeue/offload/semaphore/message operations, AQL control, GDS resources, context-save locations, and error reporting.
- `DIDT_IND_*`, `GC_CAC_*`, `GC_DIDT_*`, and `GC_EDC_CTRL`: indirect DIDT access, activity counter windows/aggregation, soft snapshot, droop-throttle power limits/weights, and EDC enable/reset/clock/stall control bits.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Detect a GC 9.1 ASIC and include/select the matching generated register headers.
2. Choose a register address from `gc_9_1_offset.h` or a SOC15 register-offset table.
3. Read an existing register value, construct a new register value, or decode a status/debug value.
4. Use these `__SHIFT` and `__MASK` constants directly or through helpers such as `REG_SET_FIELD` and `REG_GET_FIELD`.
5. Apply the value during ring initialization, MQD/HQD programming, doorbell setup, interrupt enablement, queue scheduling, power-management setup, reset/recovery, debugfs collection, hang analysis, or KFD queue management.

For graphics rings, callers typically program ring base addresses, read-pointer report addresses, write-pointer poll addresses, ring size/block size, VMID, and doorbell ranges before enabling the ring active bit. Write/read pointers and active/status fields then become live state used by scheduling and hang recovery.

For compute queues, KFD and MES/MQD paths populate HQD/MQD fields for packet-queue base, queue size, read/write pointer behavior, doorbells, privilege/KMD/TMZ state, priorities, EOP ring storage, indirect buffers, context-save buffers, and AQL behavior. Dequeue, offload, DMA, semaphore, message, and scheduler-control fields are command-state knobs rather than autonomous code in this header.

For interrupts, driver code writes enable fields in CP/CPC/ring/pipe interrupt-control registers and later decodes matching status registers. The names in this chunk show the intended one-to-one relationship between enable and status bits, but clear/ack behavior and ordering are governed by hardware and higher-level interrupt code.

For SPI and power-management fields, initialization/golden-setting paths can program persistent arbitration percentages, CU reservation masks, compute queue resets, context-save policy, CAC/DIDT windows, power bounds, weights, clock-gating overrides, and EDC enable/reset/stall controls. Status fields are read by diagnostics and recovery paths.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe stateful GPU registers whose values are owned by hardware, firmware, command submission, AMDGPU initialization, KFD queue management, and reset/recovery code.

Ring-buffer and HQD/MQD fields are persistent execution state until rewritten, queue-dequeued, or reset. Base addresses, pointer-report addresses, doorbell offsets, VMIDs, queue sizes, priority/quantum fields, context-save addresses, and EOP/PQ/IB controls must match allocated GPU memory, VM mappings, and scheduler state. Pointer and status fields can change while the GPU is executing and should be treated as volatile.

Interrupt enable fields persist until disabled or reset. Interrupt status fields may be live, sticky, clear-on-read, or write-one-to-clear depending on the register behavior outside this header. Incorrectly mixing enable and status masks can either hide faults or create interrupt storms.

SPI CU reservation, arbitration, queue-reset, and context-save fields affect scheduling and occupancy. A bad mask or stale value can disable compute units, reserve the wrong CU ranges, reset the wrong compute queue, or break CWSR/context-save behavior.

UTCL1, CPC instruction-cache, power, CAC, DIDT, and EDC fields represent hardware policy and counters. Some are persistent controls, some are snapshots or aggregates, and some are live status. Full-register writes are risky because generated headers include reserved/unused masks but do not encode which reserved bits must be preserved.

## Dependencies And Integration Points

This chunk depends on the generated GC 9.1 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_offset.h` provides matching register addresses.
- Common AMDGPU field helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32*`, `WREG32*`, and `SOC15_REG_OFFSET` consume these macros.
- AMDGPU GFX ring setup, CP interrupt handling, reset/recovery, debug and register-dump paths use the CP ring, interrupt, status, and doorbell definitions.
- AMDKFD/MQD/MES-style queue setup uses the `CP_HQD_*`, `CP_MQD_*`, and queue-control bit definitions to create and update compute queue descriptors.
- Power and reliability paths consume `CP_PWR_CNTL`, `CP_MEM_SLP_CNTL`, `GB_EDC_MODE`, `CC_GC_EDC_CONFIG`, `GC_CAC_*`, `GC_DIDT_*`, and `GC_EDC_CTRL` fields for clock/power/error behavior.

Integration points include graphics ring bring-up, compute queue creation and teardown, MQD save/restore, VMID assignment and preemption, doorbell aperture programming, KFD user-queue scheduling, interrupt enable/disable and ISR decode, GPU reset/hang diagnostics, golden-register programming, power gating/clock gating, ECC/EDC reporting, UTCL1 fault diagnosis, and shader/SPI resource scheduling.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong shift or mask compiles cleanly but writes the wrong hardware bits or decodes misleading status.
- The range starts and ends mid-register family. It begins with only the tail masks for `CPF_UTCL1_CNTL` and ends before the remaining `GC_EDC_CTRL` masks plus later EDC status/threshold registers.
- Similar ring and queue families are not interchangeable. `CP_RB0_*`, generic `CP_RB_*`, `CP_RB1_*`, `CP_RB2_*`, scheduler doorbells, and HQD PQ/EOP/IB fields have similar names but different scopes and side effects.
- Address fields are often split into low/high registers or aligned fields. Full-width masks such as `0xFFFFFFFFL` do not remove alignment, VM, aperture, or high/low ordering constraints.
- Doorbell offset and range mistakes can route writes to the wrong ring, allow unintended user access, or leave a queue unable to receive work.
- Pointer-control fields such as no-update, polling, read-pointer reports, write-pointer high/low fields, and queue-full behavior can cause silent queue stalls if packed incorrectly.
- Interrupt fields can be volatile or sticky. Enabling the wrong bits can produce interrupt storms, while failing to preserve unrelated bits can hide GPU faults.
- `CP_VMID_RESET`, `CP_VMID_PREEMPT`, and HQD dequeue/offload controls can affect running queues; writes require hardware-specific sequencing outside this header.
- SPI CU reservation and arbitration fields can produce workload-dependent failures: disabled CUs, unfair scheduling, bad occupancy, or broken context-save behavior may only appear under compute pressure.
- CAC/DIDT/EDC controls affect throttling and power reliability. Incorrect windows, weights, bounds, or reset/clock override bits can cause performance collapse, unexpected throttling, or missed droop/error reporting.
- Reserved and unused masks are present. Callers should preserve reserved bits unless an ASIC programming guide or golden-register table explicitly specifies the value.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, and hardware runtime behavior:

- Kernel build coverage for AMDGPU and AMDKFD code that includes GC 9.1 generated register headers.
- Mechanical comparison against AMD's authoritative GC 9.1 register database to confirm every `__SHIFT` and `__MASK` value in this line range.
- Cross-checks that every register family in this chunk has matching address symbols in `gc_9_1_offset.h`.
- Static mask/shift sanity checks: masks align with shifts, fields do not overlap unexpectedly, full-width data fields use full-width masks, and repeated ring/pipe/HQD families remain structurally consistent where hardware expects them to.
- GFX ring bring-up tests that validate `CP_RB0_*`, doorbell range/control, read-pointer reporting, write-pointer polling, VMID, and active-state programming.
- KFD compute queue tests that create, run, preempt, dequeue, destroy, and restore queues while exercising HQD PQ/IB/EOP/context-save/AQL fields.
- Interrupt tests that enable CP/CPC/ring/pipe interrupt bits, trigger known events where possible, and verify status decode, ack/clear behavior, and absence of interrupt storms.
- GPU reset and hang-recovery tests that read CP ring status, HQD state, UTCL1 status/error fields, VMID status, and ECC/EDC first-occurrence fields after induced faults.
- SPI scheduling tests that exercise CU reservation masks, compute queue reset, arbitration percentages, and wavefront context save under graphics and compute workloads.
- Power/reliability tests that validate CAC aggregation, DIDT throttling controls, EDC control/reset/stall behavior, memory sleep, and clock-gating override settings across suspend/resume and runtime power transitions.
- Runtime warning signals include stuck CP/HQD pointers, inactive rings after doorbell writes, VMID reset/preempt hangs, bad queue priority/fairness, missing or excessive interrupts, UTCL1 error bits, ECC/EDC first-occurrence reports, unexpected throttling, and repeated GPU resets.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002637`. It covers lines 12154-14604 of `gc_9_1_sh_mask.h`. The final per-file research should merge this with adjacent chunks to recover the full `CPF_UTCL1_CNTL` context before line 12154 and the remainder of `GC_EDC_CTRL` plus later EDC fields after line 14604.
