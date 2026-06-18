# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma4/sdma4_4_2_2_sh_mask.h lines 1-2569

## Scope

This chunk covers the first 2,569 lines of the generated AMDGPU SDMA4 4.2.2 shift/mask register header for the `sdma4_sdma4dec` address block. The range starts with the license, include guard, and SDMA4 public-engine register fields, then continues through the GFX, PAGE, and RLC0 through RLC5 queue-context register families. It ends after `SDMA4_RLC5_MIDCMD_DATA8`; the next chunk begins with `SDMA4_RLC5_MIDCMD_CNTL`.

This file chunk defines preprocessor constants only. There are no C functions, structs, variables, allocations, or executable control-flow constructs in the covered range.

## Purpose

The header provides bit offsets and masks for programming the SDMA4 hardware engine in AMD GPUs. Each hardware field is represented by the generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK`, the field mask used to isolate or compose register values.

Consumers combine this mask header with the matching SDMA offset/default headers and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`. The offset header supplies addresses such as `regSDMA4_CNTL` or `regSDMA4_RLC0_RB_CNTL`; this file supplies the bit layout for values read from or written to those addresses.

## Important Macro Families

### Public SDMA4 Engine, Virtualization, and Context Type Maps

The opening public register fields cover microcode access, VM command context, active function identity, virtualization reset, and VF enable state:

- `SDMA4_UCODE_ADDR` and `SDMA4_UCODE_DATA` expose the indexed microcode address/data path.
- `SDMA4_VM_CNTL`, `SDMA4_VM_CTX_LO`, `SDMA4_VM_CTX_HI`, and `SDMA4_VM_CTX_CNTL` define VM command, address, privilege, and VMID fields.
- `SDMA4_ACTIVE_FCN_ID`, `SDMA4_VIRT_RESET_REQ`, and `SDMA4_VF_ENABLE` expose PF/VF identity, reset request, and virtual-function enablement.

`SDMA4_CONTEXT_REG_TYPE0` through `TYPE3` and `SDMA4_PUB_REG_TYPE0` through `TYPE3` are register-type bitmaps. They encode which public or per-context SDMA registers belong to each save/restore or access-control category. These maps include GFX queue registers, public control/status registers, UTCL1 registers, physical address/log registers, performance counters, credit control, GPU IOV violation logging, and ULV controls. They are used as hardware-visible register membership maps, not as ordinary software data structures.

### Engine Control, Status, Power, and Addressing

Core SDMA engine behavior is described by:

- `SDMA4_POWER_CNTL`, `SDMA4_POWER_CNTL_IDLE`, and `SDMA4_CLK_CTRL` for memory power gating, idle delays, clock on/off hysteresis, and soft override bits.
- `SDMA4_CNTL` for trap, UTC L1, semaphore-wait interrupt, byte-swap, fence-swap, mid-command preemption, world switch, automatic context switch, and context/frozen/IB-preempt interrupt enables.
- `SDMA4_CHICKEN_BITS` and `SDMA4_CHICKEN_BITS_2` for implementation-specific copy-efficiency, stall, burst, overlap, RAW-check, QoS, FIFO watermark, and F32 command delay tuning.
- `SDMA4_GB_ADDR_CONFIG` and `SDMA4_GB_ADDR_CONFIG_READ` for pipes, pipe interleave, bank interleave, bank count, and shader-engine count fields.
- `SDMA4_STATUS_REG`, `STATUS1_REG`, `STATUS2_REG`, and `STATUS3_REG` for idle/full/stall state, copy-engine sub-block state, current command opcode, F32 instruction pointer, previous VM command, exception-idle state, and interrupt queue-id status.

These macros support initialization, reset, hang detection, diagnostics, and low-level tuning of the SDMA engine. Status fields are especially important for timeout paths that need to distinguish ring-buffer, indirect-buffer, memory-client, semaphore, interrupt, and copy-engine stalls.

### Microcode, Freeze, Scheduling, Error, and Performance State

The chunk also maps smaller public register families:

- `SDMA4_UCODE_CHECKSUM`, `SDMA4_F32_CNTL`, `SDMA4_FREEZE`, and `SDMA4_F32_COUNTER` for microcode validation, F32 halt/step, freeze/preempt/frozen state, and firmware counter observation.
- `SDMA4_PHASE0_QUANTUM`, `PHASE1_QUANTUM`, and `PHASE2_QUANTUM` for scheduler quantum unit/value/preference fields.
- `SDMA4_EDC_CONFIG`, `EDC_COUNTER`, and `EDC_COUNTER_CLEAR` for EDC/ECC enablement, per-buffer single-error detection counters, and counter clearing.
- `SDMA4_ERROR_LOG`, `SDMA4_GPU_IOV_VIOLATION_LOG`, `GPU_IOV_VIOLATION_LOG2`, `EA_DBIT_ADDR_DATA`, and `EA_DBIT_ADDR_INDEX` for error/status override, virtualization access violations, initiator ID, and double-bit-address indexed data.
- `SDMA4_PERFMON_CNTL`, `PERFCOUNTER0_RESULT`, `PERFCOUNTER1_RESULT`, and `PERFCOUNTER_TAG_DELAY_RANGE` for two performance counter channels and tag-delay range filtering.
- `SDMA4_CRD_CNTL` for memory-client read/write request credit fields.

These definitions are integration points for firmware loading, reliability handling, performance debugging, and SR-IOV or GPU IOV fault attribution.

### UTCL1, VM Fault/XNACK, and Ordering Controls

The UTCL1 block maps SDMA's local translation-cache and VM fault interface:

- `SDMA4_UTCL1_CNTL` and `UTCL1_WATERMK` cover redo enable/delay/watermark, invalidation acknowledgement delay, L2 request credit, virtual-address watermark, and outstanding request watermarks.
- `SDMA4_UTCL1_RD_STATUS` and `WR_STATUS` expose detailed read/write translation/cache state, including address pipeline state, return credit, fault status, invalidation and flush state, redo/XNACK status, buffer fullness, client response state, and timeout flags.
- `SDMA4_UTCL1_INV0`, `INV1`, and `INV2` define invalidation request controls, VMID vectors, address bits, flush type, and non-flush vectors.
- `SDMA4_UTCL1_RD_XNACK0/1` and `WR_XNACK0/1` capture read/write XNACK address, VMID, vector, and validity state.
- `SDMA4_UTCL1_TIMEOUT` and `UTCL1_PAGE` define read/write XNACK timeout limits and page-request attributes such as VM hole, request type, MTYPE, and page-table snoop usage.
- `SDMA4_RELAX_ORDERING_LUT` assigns relaxed-ordering behavior to packet classes such as copy, write, fence, poll memory, conditional execute, atomic, constant fill, PTE/PDE, timestamp, world switch, read-pointer writeback, write-pointer poll, IB fetch, and RB fetch.

These masks are central to memory-management integration. Incorrect UTCL1 field definitions can change fault reporting, invalidation sequencing, retry behavior, request ordering, or VMID attribution for SDMA traffic.

### Queue Contexts: GFX, PAGE, and RLC0-RLC5

From `SDMA4_GFX_RB_CNTL` onward, the chunk defines a repeated queue-context layout for several SDMA queues:

- `GFX`
- `PAGE`
- `RLC0`
- `RLC1`
- `RLC2`
- `RLC3`
- `RLC4`
- `RLC5` through `MIDCMD_DATA8`

Each queue family follows the same register pattern:

- Ring-buffer control and addressing: `RB_CNTL`, `RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, `RB_WPTR_HI`, `RB_RPTR_ADDR_HI`, and `RB_RPTR_ADDR_LO`.
- Write-pointer polling: `RB_WPTR_POLL_CNTL`, `RB_WPTR_POLL_ADDR_HI`, and `RB_WPTR_POLL_ADDR_LO`.
- Indirect-buffer execution: `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO`, `IB_BASE_HI`, `IB_SIZE`, and `IB_SUB_REMAIN`.
- Context execution state: `SKIP_CNTL`, `CONTEXT_STATUS`, `DOORBELL`, `STATUS`, `DOORBELL_LOG`, `WATERMARK`, `DOORBELL_OFFSET`, `CSA_ADDR_LO`, `CSA_ADDR_HI`, `PREEMPT`, `DUMMY_REG`, `RB_AQL_CNTL`, `MINOR_PTR_UPDATE`, `MIDCMD_DATA0` through `MIDCMD_DATA8`, and usually `MIDCMD_CNTL`.

The repeated bit layouts are consistent across these queue types. `RB_CNTL` includes enable, ring size, swap, read-pointer writeback, privilege, and VMID fields. `IB_CNTL` includes IB enable, swap, inside-IB switching, and command VMID. `CONTEXT_STATUS` exposes selected/idle/expired/exception/context-switch/preempted/preempt-disable bits. Doorbell fields include enable/captured state, offsets, and logged data. AQL fields describe AQL enablement, packet size, and packet step. Mid-command data registers are full-width payload words, while mid-command control registers encode data-valid, copy mode, split state, and preempt allowance.

The chunk boundary is significant: it includes the complete `SDMA4_RLC5_MIDCMD_DATA8` field pair but not `SDMA4_RLC5_MIDCMD_CNTL`, which appears immediately after the requested range.

## Control Flow and State Behavior

This header has no runtime control flow. It influences compiled driver behavior by defining how code composes and decodes 32-bit hardware register values.

The persistent state represented here is SDMA hardware state rather than software-owned state in the header. Important state includes microcode index/data access, VM command state, PF/VF identity and reset requests, power/clock controls, engine control bits, scheduler quantum values, UTCL1 translation-cache state, XNACK/fault capture, status and error logs, performance counters, and per-queue ring/IB/doorbell/context-save state.

Some fields are configuration controls that persist until reset or explicit reprogramming, such as ring-buffer base addresses, queue VMIDs, doorbell offsets, power/clock controls, relaxed-ordering LUT bits, UTCL1 watermarks, and interrupt enables. Other fields are status, counter, sticky fault, or command-like fields, such as idle/stall status, EDC counters, XNACK captures, GPU IOV violation status, freeze/preempt bits, performance clear bits, and write-pointer update pending/fail counts. Correct use depends on the hardware's reset, write-one-to-clear, polling, and timeout semantics; the macro names alone do not encode those access rules.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention:

- `sdma4_4_2_2_offset.h` supplies register addresses and base indices for the `SDMA4_*` names.
- A matching default header, when present for this ASIC generation, supplies reset/default values.
- AMDGPU SOC15 register helpers consume the `__SHIFT` and `_MASK` macros to avoid hard-coded bit positions.

Likely source-tree integration points include:

- SDMA v4 initialization, golden-register programming, reset, suspend/resume, and hang-detection paths. For example, SDMA v4 code references `SDMA4_UTCL1_TIMEOUT` golden values.
- AMDGPU queue setup paths that program ring base, read/write pointers, read-pointer writeback, write-pointer polling, IB state, doorbells, VMIDs, and AQL controls.
- KFD/HSA integration for AQL queues, context save areas, preemption, minor pointer updates, and page or RLC queues.
- SR-IOV/GPU IOV paths that use active function ID, VF enable/reset, GPU IOV violation logs, and virtualization fault attribution.
- VM/MMU code and fault handlers that inspect UTCL1 invalidation, XNACK, fault, redo, and page-request fields.
- Debugfs, diagnostics, performance monitoring, and reliability code that reads status registers, EDC counters, error logs, performance counters, watermarks, and queue context status.

Consumers must include the SDMA4 4.2.2 offset and mask headers together. Nearby SDMA generations expose similar register names and repeated queue layouts, but bit positions, queue count, reserved bits, and supported controls can differ.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can corrupt ring setup, doorbell routing, IB execution, VMID selection, or engine control programming.
- Queue register layouts are highly repetitive. Copy/paste or generation mistakes can silently affect only one queue family, such as `RLC3` or `RLC5`, while leaving others apparently correct.
- VM and UTCL1 fields are correctness- and security-sensitive. Incorrect invalidation, VMID vector, XNACK, page-request, or fault-status masks can misattribute faults, break retry behavior, or affect address-translation isolation.
- SR-IOV/GPU IOV fields are privilege-sensitive. Incorrect PF/VF identity, VF enable/reset, or violation-log masks can hide unauthorized access or break virtual-function reset/reporting.
- Status and error fields may be sticky, counter-like, or write-one-to-clear. Treating them as ordinary read/write state can lose diagnostic evidence or fail to clear a real condition.
- Power, clock, and chicken-bit fields may depend on ASIC-specific sequencing. Incorrect writes can cause hangs, unstable idle behavior, or performance regressions.
- Doorbell, read-pointer writeback, and write-pointer polling address fields are address-alignment sensitive. Bad masks can truncate or misalign GPU/CPU-visible queue pointers.
- The chunk ends before the `RLC5_MIDCMD_CNTL` definition, so any per-file summary must reconcile this document with the following chunk for the complete RLC5 context.

## Test and Validation Signals

Useful validation is mostly build and hardware integration coverage:

- Build AMDGPU with SDMA4 4.2.2 headers enabled; this catches missing, renamed, or syntactically invalid macros.
- Exercise SDMA ring initialization for GFX, PAGE, and RLC queues and verify ring base, size, read/write pointers, read-pointer writeback, write-pointer polling, VMID, and doorbell offset programming.
- Run SDMA copy/fill/fence/poll/atomic/IB workloads and check `STATUS_REG`, `STATUS1_REG`, `STATUS2_REG`, `STATUS3_REG`, queue `CONTEXT_STATUS`, and watermark fields during normal operation and timeout injection.
- Validate suspend/resume, reset, freeze, and preemption paths, including `SDMA4_FREEZE`, queue `PREEMPT`, context-save addresses, mid-command data, and context-switch ready/preempted state.
- Exercise VM fault and invalidation scenarios to confirm UTCL1 invalidation, XNACK capture, page attributes, timeout fields, and fault-status bits decode correctly.
- On SR-IOV-capable hardware, validate VF enable/reset behavior and GPU IOV violation logs, including VF/VFID and initiator attribution.
- Verify EDC/ECC and error-log handling where supported by injecting or observing errors and confirming counter clear and status reporting behavior.
- Use performance counter tests to confirm `PERFMON_CNTL`, result registers, tag-delay range selection, and clear/enable behavior.
- Compare register dumps against expected SDMA4 4.2.2 hardware documentation or known-good traces, especially for repeated RLC queue blocks and reserved-bit preservation.
