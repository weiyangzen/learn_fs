# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h lines 2462-4871

## Scope And Purpose

This chunk is a declarative register-field map for the AMD GC 9.4.2 graphics IP block, used by the Aldebaran-era amdgpu/KFD driver code. It contains only preprocessor constants: each hardware register field is represented as a `__SHIFT` macro and a matching `_MASK` macro. Runtime code combines these names through helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()` from `amdgpu.h`, which token-paste `REG__FIELD__SHIFT` and `REG__FIELD_MASK`.

The slice begins in the middle of `CP_INT_STATUS_RING2` and ends in the first three shift macros of `GCEA_ADDRDEC_MISC_CFG`, so both boundaries depend on neighboring chunks for complete per-register coverage. Within the slice, the main areas are command processor interrupt/control state, command processor queue/HQD state, DIDT indirection registers, and GCEA DRAM/effective-address routing controls.

## Important APIs, Types, And Register Groups

There are no C functions or types in this chunk. The important API surface is the macro naming contract:

- `REG_FIELD_SHIFT(reg, field)` expands to `reg##__##field##__SHIFT`.
- `REG_FIELD_MASK(reg, field)` expands to `reg##__##field##_MASK`.
- `REG_SET_FIELD(orig, reg, field, val)` clears the mask and inserts `val << shift`.
- `REG_GET_FIELD(value, reg, field)` extracts `(value & mask) >> shift`.

Major register groups covered here:

- `CP_*_F32_INTERRUPT`, `CP_MEC*_F32_INTERRUPT`, and `CP_MEC*_F32_INT_DIS`: command processor F32, MEC, ECC, GPF, queue-message, wave-restore, SUA-violation, and fatal-EDC interrupt bit definitions.
- `CP_ME{1,2}_PIPE{0..3}_INT_CNTL`, matching `*_INT_STATUS`, and `CP_ME{1,2}_INT_STAT_DEBUG`: compute pipe interrupt enable, latched status, and debug-assertion fields for query-status, dequeue, ECC, GPF, WRM timeout, privileged access, opcode, timestamp, reserved-bit, and generic interrupt causes.
- `CP_PWR_CNTL`, `CP_MEM_SLP_CNTL`, `CP_CONTEXT_CNTL`, `CP_MAX_CONTEXT`, `CP_IQ_WAIT_TIME*`, `CP_VMID_RESET`, `CP_VMID_PREEMPT`, `CP_VMID_STATUS`, and `CP_PQ_STATUS`: control bits for command-processor power, memory sleep/deep sleep, context handling, VMID reset/preempt/status, and packet-queue status.
- `CPC_INT_CNTL`, `CPC_INT_STATUS`, `CPC_INT_CNTX_ID`, `CP_CPC_IC_*`, `CP_CPC_GFX_CNTL`: command processor controller interrupt, instruction-cache, and graphics-control fields.
- `CP_RB_DOORBELL_CONTROL_SCH_{0..7}`, `CP_RB_DOORBELL_CLEAR`, `CP_RB_STATUS`: scheduler ring-buffer doorbell offsets, enable/hit/update bits, and doorbell clear masks.
- `CPF/CPG/CPC/DC_*_CNT`, `CP_*_DSM_CNTL*`, and `CP_EDC_FUE_CNTL`: EDC counters, dynamic/static memory/error injection controls, and fatal uncorrectable error masking/flagging.
- `CP_GFX_MQD_*`, `CP_MQD_*`, `CP_HQD_*`: memory queue descriptor and hardware queue descriptor fields for VMID, privilege, execution disable, cache policy, queue activation, pipe/queue priority, quantum, PQ/IB/EOP base addresses, read/write pointers, doorbell control, dequeue requests, offload, scheduler/status/control, context-save addresses, GDS resource state, AQL control, and HQD error causes.
- `DIDT_IND_INDEX`, `DIDT_IND_DATA`, `DIDT_INDEX_AUTO_INCR_EN`: indirect register selector/data/autoincrement fields for dynamic instruction/dynamic throttling tables.
- `GCEA_DRAM_*`: graphics client effective-address DRAM read/write client-to-group mappings, group-to-VC mappings, lazy thresholds, CAM depth/reorder controls, page-burst limits, priority aging/queueing/fixed/urgency coefficients, and quantum thresholds.
- `GCEA_ADDRNORM_*`, `GCEA_ADDRNORMDRAM/GMI_*`, `GCEA_ADDRDEC_BANK_CFG`, and the start of `GCEA_ADDRDEC_MISC_CFG`: address range validity, legacy MMIO hole handling, interleave topology, base/limit/offset values, DRAM/GMI hole controls, NP2 channel sizing, and bank/channel/chip-select decode knobs.

## Control Flow And Runtime Behavior

This header has no executable control flow. Control flow appears in consumers that:

1. Include `gc_9_4_2_offset.h` for register addresses and this `gc_9_4_2_sh_mask.h` file for field layout.
2. Build register values with `REG_SET_FIELD()` or direct mask/shift operations.
3. Access hardware through MMIO helpers such as `RREG32`, `WREG32`, `WREG32_RLC`, `SOC15_REG_OFFSET`, and RLC-mediated register access.

For this exact ASIC generation, `gfx_v9_4_2.c` and `amdgpu_amdkfd_aldebaran.c` include this header directly. The broader amdgpu/KFD queue code uses the same `CP_HQD_*` and `CP_HQD_PQ_*` field names to initialize MQDs, program doorbell offsets, activate queues, issue dequeue requests, and poll for queue teardown. Interrupt setup paths use `CP_ME1_PIPE*_INT_CNTL`/status fields to enable and classify compute pipe events. RAS paths use nearby GCEA and CP EDC status/counter fields to identify and clear error state.

## State And Persistence Behavior

The state represented by these macros is hardware state, not software-owned persistence:

- Interrupt enable/status fields persist in MMIO registers until hardware or driver writes update or clear them.
- MQD/HQD fields describe queue identity and lifecycle state: active bit, VMID, queue priority, PQ/IB/EOP base addresses, read/write pointers, doorbell routing, dequeue requests, context-save addresses, AQL controls, and error flags.
- EDC and FUE fields expose persistent hardware error counters, injection configuration, and fatal-error flags until counters/status are cleared or reset.
- GCEA DRAM and address-normalization fields affect address routing, interleaving, DRAM/GMI hole behavior, client priority, and reorder behavior while programmed.
- Power, memory sleep, soft-reset-adjacent, and VMID controls affect hardware engine state across runtime transitions, reset, suspend/resume, and queue preemption.

The header itself stores no values. Its correctness determines whether software writes the intended hardware bits.

## Dependencies And Integration Points

Primary dependencies are:

- Companion generated files such as `gc_9_4_2_offset.h`, which define the `reg...` addresses referenced by consumers.
- `amdgpu.h` field helpers that depend on the exact `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` spellings.
- SOC15 access helpers and register entry macros, including `SOC15_REG_OFFSET`, `SOC15_REG_ENTRY`, and `SOC15_REG_FIELD`.
- GFX 9.4.2 amdgpu implementation code in `gfx_v9_4_2.c`, including golden settings, RAS/EDC counter handling, GCEA error handling, and GC programming paths.
- Aldebaran KFD integration in `amdgpu_amdkfd_aldebaran.c`, which includes this ASIC register layout for KFD/debug interaction with GC hardware.
- Common KFD MQD/HQD management code for GFX generations, which relies on `CP_HQD_*` masks and shifts when constructing queue descriptors and programming active queues.

The source-tree alignment is important: this is GPU driver hardware metadata inside the vendored Ceph-client Linux tree, not Ceph filesystem logic.

## Risks And Edge Cases

- Off-by-one or stale mask/shift values can silently corrupt unrelated bits in privileged MMIO registers, causing hangs, lost interrupts, incorrect queue scheduling, bad VMID assignment, or broken RAS reporting.
- The chunk starts and ends mid-register. Any generated report for only this slice must not claim complete coverage for `CP_INT_STATUS_RING2` or `GCEA_ADDRDEC_MISC_CFG`.
- Many pipe and queue registers are repeated with identical layouts. Copy/paste or generation drift between `CP_ME1`/`CP_ME2`, pipe indices, and status/control variants can leave one queue path misprogrammed while others work.
- Address-bearing fields have alignment encoded in their low-bit shifts and masks, for example base-address fields shifted by 2, 3, or 12 bits. Misinterpreting these as byte-granular values can produce invalid queue, EOP, IB, or address-normalization programming.
- Doorbell fields combine enable, mode, source, hit, and large offset fields. Incorrect masking can route doorbells to the wrong queue or leave queues unresponsive.
- EDC/FUE and DSM injection controls are diagnostic and fault-handling sensitive; accidentally enabling injection or masking fatal errors would make test and production behavior diverge.
- GCEA address-normalization and address-decode fields control memory fabric routing. Bad base/limit/interleave/hole settings risk memory access failures that surface far from the write site.

## Test Signals

Useful validation signals are mostly integration and hardware-facing:

- Build coverage for files that include `gc_9_4_2_sh_mask.h`, especially `gfx_v9_4_2.c` and `amdgpu_amdkfd_aldebaran.c`, catches missing or renamed macros.
- Queue lifecycle tests should exercise MQD/HQD load, active polling, doorbell update, dequeue/destroy, read/write pointer reporting, IB execution, and EOP event handling.
- KFD compute tests should cover user queues, kernel queues, VMID assignment, priority/quantum settings, and debug trap/watchpoint flows on Aldebaran/GC 9.4.2 hardware.
- Interrupt tests should confirm CP/MEC/CPC interrupt enable and status bits produce expected IRQ handling for dequeue, timestamp, ECC, GPF, opcode, privileged register/instruction, and reserved-bit conditions.
- RAS tests should inject or observe EDC/FUE events and verify counters, first-occurrence fields, clear paths, and fatal masking behavior.
- Suspend/resume, GPU reset, and preemption tests should verify that persistent HQD, VMID, doorbell, and error state is reprogrammed or cleared correctly.
- Performance and stress tests that vary memory traffic are the practical signal for GCEA priority, CAM, page-burst, and address-normalization programming regressions.
