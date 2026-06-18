# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 14935-17380

## Purpose

This chunk is generated AMD GC 11.0.0 register bitfield metadata. It contains no executable C code; it exposes preprocessor constants that describe where each field lives inside a 32-bit GPU MMIO register. Driver code pairs these `__SHIFT` and `_MASK` macros with register offsets from `gc_11_0_0_offset.h` and then uses AMDGPU/KFD helpers to compose, write, read, and decode command-processor, shader-processor-interface, and queue-descriptor registers.

The selected range starts with two shader reserved data registers, then covers most of the `gc_cppdec` command-processor decode block, the `gc_spipdec` SPI scheduling/debug subset, and the start of the `gc_cpphqddec` HQD block. The dominant concerns are CP ring-buffer setup, VMID/preemption/reset, interrupt and ECC reporting, doorbell ranges and hit state, draw/dispatch ID buffering, suspend/resume state-save layout, DMA watchpoints, UTCL1 fault/status fields, SPI arbitration/debug fields, and the first part of per-HQD queue setup. Although the repository path is under `ceph-client`, this file is AMD GPU hardware register metadata, not Ceph or filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, callbacks, allocations, or direct MMIO accesses in this chunk. The only API surface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field's in-register mask.
- Full-width masks such as `0xFFFFFFFFL` represent data, pointer, address, timestamp, counter, status, or debug payload fields, not necessarily safe write masks.
- Consumers normally combine these macros with `mm<REGISTER>` and `mm<REGISTER>_BASE_IDX` definitions from `gc_11_0_0_offset.h`, plus helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and KFD MQD layout code.

Major register groups in this chunk:

- `SH_RESERVED_REG0` and `SH_RESERVED_REG1` are full-width reserved shader register payloads.
- `CP_CU_MASK_*` defines compute-unit mask address and policy fields used when CP-side CU masks are installed or selected.
- `CP_EOPQ_WAIT_TIME`, `CP_CPC_MGCG_SYNC_CNTL`, `CP_PROCESS_QUANTUM`, `CP_IQ_WAIT_TIME1/2/3`, and CP/CPC/CPF busy hysteresis registers describe CP timing, scheduler retry, quantum, clock-gating, and busy-detection thresholds.
- `CPC_INT_INFO`, `CPC_INT_ADDR`, `CPC_INT_PASID`, `CPC_INT_CNTL`, `CPC_INT_STATUS`, and `CPC_INT_CNTX_ID` describe CPC interrupt metadata: address high bits, interrupt type, VMID, queue ID, PASID, bypass-PASID, enable/status bits, and context ID.
- `CP_INT_CNTL`, `CP_INT_STATUS`, `CP_INT_CNTL_RING0/1`, and `CP_INT_STATUS_RING0/1` provide graphics ring interrupt enable/status bits for resume, suspend, DMA watch, VM doorbell writes, ECC, general protection faults, write-pointer poll timeouts, busy/empty/idle transitions, privilege violations, opcode errors, timestamp events, reserved-bit errors, and generic interrupts.
- `CP_ME1/ME2_PIPE[0-3]_INT_CNTL` and matching `INT_STATUS` registers replicate the compute-pipe interrupt enable/status map for MEC pipes, including completion-query status, dequeue request, ECC, SUA violation, GPF, write-pointer poll timeout, privilege/register/opcode errors, timestamp, reserved-bit, and generic interrupts.
- `CP_ME_F32_INTERRUPT`, `CP_PFP_F32_INTERRUPT`, `CP_MEC1_F32_INTERRUPT`, `CP_MEC2_F32_INTERRUPT`, `CP_MEC1_F32_INT_DIS`, and `CP_MEC2_F32_INT_DIS` define F32 firmware/EDC interrupt and disable bits for ME/PFP/MEC front ends.
- `CP_GFX_ERROR`, `CP_FATAL_ERROR`, `CP_ECC_FIRSTOCCURRENCE*`, `GB_EDC_MODE`, and `CC_GC_EDC_CONFIG` describe CP/GC error attribution, fatal-error behavior, first ECC occurrence reporting, and EDC configuration/disabling.
- `CPG_UTCL1_CNTL`, `CPC_UTCL1_CNTL`, `CPF_UTCL1_CNTL`, `CPG_UTCL1_ERROR`, `CPC_UTCL1_ERROR`, and `CPG/CPC/CPF_UTCL1_STATUS` cover UTCL1 retry timers, invalidate/drop/fragment/snoop/permission modes, force-no-execute behavior, detected faults/retries/PRT events, and per-event UTCL1 IDs.
- `CP_RB0_*`, generic `CP_RB_*`, and `CP_RB1_*` define graphics ring buffer base, high address, control, read-pointer writeback address, read/write pointers, buffer-size masks, VMID mapping, active state, doorbell range, doorbell clear/status, and write-pointer poll address fields.
- `CP_RB_DOORBELL_RANGE_*`, `CP_MEC_DOORBELL_RANGE_*`, `CP_RB_DOORBELL_CONTROL`, `CP_RB_DOORBELL_CLEAR`, `CP_RB_STATUS`, and `CP_PQ_STATUS` describe doorbell aperture limits, doorbell modes, offsets, source/schedule-hit/enable/hit bits, and queue status reporting.
- `CP_ME0/ME1/ME2_PIPE_PRIORITY_CNTS`, `CP_RING_PRIORITY_CNTS`, `CP_ME*_PIPE*_PRIORITY`, and `CP_RING*_PRIORITY` define priority counters and per-pipe/ring priority selectors.
- `CP_RB_VMID`, `CP_ME0_PIPE*_VMID`, `CP_VMID_RESET`, `CP_VMID_PREEMPT`, and `CP_VMID_STATUS` encode VMID binding, queue reset masks, preempt requests, virtualization command fields, and preempt status for DE/CE.
- `CP_PFP/ME/MEC*_PRGRM_CNTR_START*` and `CP_PFP/ME/MEC*_INTR_ROUTINE_START*` define microcontroller program-counter and interrupt-routine entry-point fields.
- `CP_CONTEXT_CNTL` and `CP_MAX_CONTEXT` describe maximum geometry-engine and pipe-context counts.
- `CP_PWR_CNTL`, `CP_CPC_DEBUG`, `CP_SD_CNTL`, `CP_SOFT_RESET_CNTL`, and `CP_CPC_GFX_CNTL` expose power/debug/reset/control bits that affect CP/CPC/CPF behavior and debug paths.
- `CP_PQ_WPTR_POLL_CNTL` and `CP_PQ_WPTR_POLL_CNTL1` control write-pointer polling period, active/enabled state, one-shot behavior, and queue masks.
- `CPC_SUSPEND_CTX_SAVE_*`, `CPC_SUSPEND_CNTL_STACK_*`, `CPC_SUSPEND_WG_STATE_OFFSET`, `CPC_OS_PIPES`, `CP_SUSPEND_RESUME_REQ`, and `CP_SUSPEND_CNTL` describe context-save base/size/offsets, OS pipe masks, suspend/resume requests, resume lock, and ACE suspend activity.
- `CPC_DDID_*`, `CP_DDID_*`, and `CP_GFX_DDID_*` define draw/dispatch ID buffer base, control, VMID selection, policy/mode/enable, in-flight count, read/write pointers, and delta-report counts.
- `CP_GFX_HPD_*`, `CP_GFX_MQD_*`, and `CP_GFX_HQD_*` define graphics high-priority dispatch queue state: mapped/available/forced queue state, OSPRE fence address/data, index mutex, MQD base/control, HQD active/VMID/priority/quantum/base/pointers/read-pointer writeback/write-pointer poll, doorbell control, dequeue request, mapping, queue-manager control, IQ timer, HQ status/control, and GFX HQD ring control.
- `CP_HQD_GFX_CONTROL` and `CP_HQD_GFX_STATUS` provide message/status fields for HQD graphics control.
- `CP_DMA_WATCH[0-3]_*`, `CP_DMA_WATCH_STAT_ADDR_*`, and `CP_DMA_WATCH_STAT` define four DMA watchpoints, including address/mask, VMID or any-VMID selection, read/write watch enables, and trap status attribution by VMID, queue ID, client ID, pipe, watch ID, and direction.
- `CP_PFP_JT_STAT` and `CP_MEC_JT_STAT` report jump-table loaded and write-mask state.
- `CPG_RCIU_CAM_*` describes indexed CAM programming fields for address/mask/value phases and per-pipe enable/skip-write behavior.
- `CP_GPU_TIMESTAMP_OFFSET_*`, `CP_SDMA_DMA_DONE`, `CP_PFP_SDMA_CS`, `CP_ME_SDMA_CS`, and `CPF_GCR_CNTL` provide timestamp offset, SDMA completion/arbitration, and GCR command fields.
- `SPI_ARB_PRIORITY`, `SPI_ARB_CYCLES_*`, `SPI_WCL_PIPE_PERCENT_*`, `SPI_USER_ACCUM_VMID_CNTL`, `SPI_GDBG_PER_VMID_CNTL`, `SPI_COMPUTE_QUEUE_RESET`, and `SPI_COMPUTE_WF_CTX_SAVE` define SPI arbitration, workload pipe percentages for graphics/HP3D/CS pipes, per-VMID accumulation/debug/trap controls, compute queue reset, and compute wavefront context-save control/status.
- The final `gc_cpphqddec` section starts generic HQD definitions: `CP_HPD_UTCL1_*`, MQD base address, `CP_HQD_ACTIVE`, `CP_HQD_VMID`, `CP_HQD_PERSISTENT_STATE`, pipe/queue priority, quantum, PQ base/read-pointer/read-pointer report/write-pointer poll addresses, doorbell control, and the beginning of `CP_HQD_PQ_CONTROL` through `UNORD_DISPATCH__SHIFT`.

## Control Flow

This header has no runtime control flow. It is a declarative map from generated register-field names to bit positions and masks. Runtime flow is supplied by AMDGPU, AMDKFD, firmware, and hardware:

1. GC 11 driver code includes `gc_11_0_0_offset.h` and `gc_11_0_0_sh_mask.h`.
2. The caller selects an MMIO register offset and composes field values with the corresponding shift and mask macros.
3. Driver helpers perform read-modify-write, raw reads, raw writes, queue-descriptor initialization, or status decoding.
4. The CP, CPC, CPF, CPG, MEC, PFP, SPI, HQD, doorbell, VM, UTCL1, and interrupt hardware blocks define the actual state transitions, ordering, completion, and error behavior.

Important runtime flows represented by the fields include graphics-ring setup, queue/MQD setup, doorbell enablement, write-pointer polling, read-pointer writeback, VMID reset/preempt, suspend/resume context-save, interrupt enable/status handling, ECC/EDC/fatal-error reporting, DMA watchpoint trapping, UTCL1 invalidate/status handling, SDMA arbitration from CP microcontrollers, SPI compute queue reset and wavefront context-save initiation, and HQD persistent-state/priority/quantum programming. None of those sequences, timeouts, memory barriers, lock ordering, or firmware handshakes are encoded here.

## State And Persistence Behavior

The file stores no software state and persists nothing. It describes hardware state that may be programmed, sampled, or action-triggered by driver code.

State represented in this chunk includes ring-buffer bases and high address bits, ring buffer sizes, read/write pointers, read-pointer writeback addresses, write-pointer poll addresses and periods, VMID/IB VMID/VQID selections, doorbell offsets and hit/enabled state, queue active/mapped/available/idle/dequeue/preempt bits, CP/MEC/PFP firmware entry points, interrupt enables/status, ECC/EDC first-occurrence bits, UTCL1 fault and retry status, process and HQD quantum settings, context-save memory layout, DMA watchpoint configuration and trap attribution, timestamp offsets, debug CAM entries, SPI arbitration/pipe allocation, and HQD persistent state.

Persistence is hardware-defined. Some fields are stable configuration until reset, queue teardown, or power-gating; some are live counters or pointers updated by hardware; some are sticky status or interrupt bits; some are command strobes such as reset, preempt, invalidate, suspend, resume, capture, clear, or context-save initiation. The masks do not indicate read-only, write-only, self-clearing, sticky, write-one-to-clear, privileged, or reserved semantics. Consumers must follow the GC 11 programming sequences and preserve unrelated bits in mixed-purpose registers.

## Dependencies And Integration Points

The direct companion header is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h`, which provides matching `mm*` register offsets and base-index symbols. `gc_11_0_0_default.h` provides default values for some registers. The generated header must remain synchronized with the ASIC register database for GC 11.0.0.

Observed in-tree users include GC 11 KFD queue management code, especially `amdkfd/kfd_device_queue_manager_v11.c` and `amdkfd/kfd_mqd_manager_v11.c`, which include the GC 11 offset and shift/mask headers and use fields such as `CP_HQD_PERSISTENT_STATE`, `CP_HQD_QUANTUM`, `CP_HQD_PQ_CONTROL`, and `CP_HQD_PQ_DOORBELL_CONTROL` when initializing MQDs and queues. Broader integration points are AMDGPU graphics-ring initialization, KFD compute queue creation, MQD programming, doorbell aperture setup, GPU reset/recovery, preemption, VMID management, interrupt service paths, ECC/EDC reporting, suspend/resume, runtime power management, wavefront context save/restore, debug/profiling tools, and hardware validation diagnostics.

The chunk crosses address blocks. Code that touches the CP decode block should not assume the SPI or HQD fields share the same indexing, privilege, or reset semantics. The final lines stop in the middle of `CP_HQD_PQ_CONTROL`; adjacent chunks are required for its complete mask set and for the remaining generic HQD queue registers.

## Risks And Edge Cases

- Header/offset mismatch is the main correctness risk. Combining `gc_11_0_0_sh_mask.h` with offsets from another GC revision can compile cleanly while targeting incorrect bits.
- This chunk is pure macro data, so all type, range, alignment, and sequencing checks must happen in callers. A bad shift/mask choice can misprogram a ring, VMID, doorbell, interrupt, or queue descriptor without compiler help.
- The selected range starts and ends at chunk boundaries, not logical register-family boundaries. It begins after prior shader fields and ends before the rest of `CP_HQD_PQ_CONTROL`; complete HQD analysis requires the next chunk.
- Many address fields encode alignment in their masks, for example low bits omitted for ring bases, writeback addresses, doorbells, context-save bases, fence addresses, and DMA watch addresses. Callers must program aligned GPU addresses and preserve required low-bit semantics.
- Doorbell, write-pointer polling, and read-pointer writeback fields are ordering-sensitive. Missing write memory barriers, stale writeback memory, wrong doorbell offset, or an incorrect range limit can make queues appear idle, stuck, or spuriously active.
- VMID reset/preempt/status, suspend/resume, and context-save fields describe multi-stage hardware operations. Polling code must handle in-flight transitions and timeout paths rather than treating a single status read as final.
- Interrupt enable/status fields are heavily replicated across rings and MEC pipes. Copy/paste mistakes between ring0/ring1, ME1/ME2, or pipe0-3 can route or mask the wrong event.
- ECC/EDC/fatal-error and UTCL1 error bits can be sticky or hardware-owned. Blind writes using full masks risk clearing diagnostic state, suppressing faults, or hiding fatal conditions.
- Debug, chicken, power, clock, soft-reset, and CAM fields can affect global CP behavior. These should generally be programmed only by ASIC-specific initialization or recovery code that knows required defaults.
- DMA watchpoint fields can trap reads/writes across VMIDs. Incorrect `ANY_VMID`, mask, or address setup can miss the intended access or generate excessive traps.
- SPI debug/trap and wavefront context-save fields interact with per-VMID scheduling and debugger behavior. Incorrect use can stall VMIDs, trap unintended waves, or leave context-save busy bits set.
- The `CP_HQD_PERSISTENT_STATE`, `CP_HQD_PQ_DOORBELL_CONTROL`, and partial `CP_HQD_PQ_CONTROL` fields are consumed by KFD MQD setup. Queue-size, no-update-rptr, unordered-dispatch, TMZ, cache-policy, privilege, and KMD-queue bits must match the queue type and memory policy.

## Test Signals

Useful validation is mostly generated-header consistency, build coverage, and hardware queue smoke testing:

- Build AMDGPU and AMDKFD code that includes `gc_11_0_0_offset.h` and `gc_11_0_0_sh_mask.h`, including GC 11 KFD MQD and device queue manager files.
- Generated-header checks that every `__SHIFT` in this slice has the expected `_MASK`, that masks align with shifts, and that register names have matching entries in `gc_11_0_0_offset.h`.
- Static checks for overlapping fields within a register, while allowing full-width data/status aliases and known reserved fields.
- Ring bring-up tests that program `CP_RB0`, generic `CP_RB`, and `CP_RB1` base/control/read-pointer/write-pointer/writeback fields, submit graphics work, and verify read-pointer progress and idle/active transitions.
- Doorbell tests that cover range limits, offsets, enable/hit bits, clear bits, write-pointer polling, and read-pointer writeback updates.
- KFD queue/MQD tests on GC 11 hardware that validate `CP_HQD_PERSISTENT_STATE`, priority, quantum, PQ base, PQ control, doorbell control, and VMID programming through real compute dispatch completion.
- Interrupt tests that enable selected CP/CPC/MEC pipe events, trigger controlled events such as dequeue, timestamp, write-pointer poll timeout, or invalid opcode where feasible, and verify status bits and ISR routing.
- VMID reset/preempt and suspend/resume tests that force queue preemption or suspend, poll status, verify context-save memory layout, and confirm queues resume without lost progress.
- UTCL1 and VM fault tests that exercise fault/retry/PRT status, invalidate sequencing, and error-halt reporting without stale translations.
- ECC/EDC diagnostic tests that confirm first-occurrence and F32 interrupt/disabling paths report the expected block and do not mask unrelated errors.
- DMA watchpoint tests that arm each watch register for read/write and VMID/any-VMID modes, then verify trap attribution fields and status writeback addresses.
- SPI scheduler/debug tests that validate arbitration/pipe-percentage programming, per-VMID debug trap controls, compute queue reset, and wavefront context-save busy/done behavior.
- Regression indicators include stuck ring write pointers, unchanged read-pointer writeback, doorbell hits without queue progress, unexpected queue idle/active mismatch, missing or storming interrupts, false privilege/opcode errors, EDC counter growth, UTCL1 fault/retry status after drains, failed KFD queue creation, GPU reset during queue teardown, or compute wavefront context-save that never clears busy.
