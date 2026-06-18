# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma4/sdma4_4_2_2_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003393`: lines 1-2569, `Docs/researches/chunks/subset-b-003393_research.md`
- `subset-b-003394`: lines 2570-2956, `Docs/researches/chunks/subset-b-003394_research.md`

## Chunk Research

### subset-b-003393: lines 1-2569

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

### subset-b-003394: lines 2570-2956

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma4/sdma4_4_2_2_sh_mask.h lines 2570-2956

## Scope

This chunk is the final section of the generated AMD SDMA4 4.2.2 shift/mask header. It starts at `SDMA4_RLC5_MIDCMD_CNTL`, then defines the complete bitfield layout for SDMA4 RLC queue contexts 6 and 7, and ends with the closing include guard.

The file is C preprocessor metadata only. It contains no functions, structs, enums, allocation, locking, branches, loops, MMIO calls, or direct runtime control flow. Its exported surface is a dense namespace of `*_SHIFT` and `*_MASK` macros that AMDGPU code combines with matching offset headers and register helpers.

Although the repository path is under a `ceph-client` source mirror, this chunk documents AMD GPU SDMA hardware registers. It does not implement distributed filesystem behavior.

## Purpose

`sdma4_4_2_2_sh_mask.h` supplies symbolic bit positions and masks for fields inside SDMA4 4.2.2 registers. It is paired with `sdma4_4_2_2_offset.h`, which provides the register addresses. Consumers use the address macros plus these field macros through helpers such as `REG_SET_FIELD()`, `REG_GET_FIELD()`, `SOC15_REG_OFFSET()`, `RREG32()`, and `WREG32()`.

The covered range describes high RLC queue-context registers for SDMA engine 4:

- `SDMA4_RLC5_MIDCMD_CNTL` appears at the chunk boundary and exposes the mid-command control bits `DATA_VALID`, `COPY_MODE`, `SPLIT_STATE`, and `ALLOW_PREEMPT`.
- `SDMA4_RLC6_*` defines the full RLC6 queue-context bit layout.
- `SDMA4_RLC7_*` defines the full RLC7 queue-context bit layout.

RLC6 and RLC7 are structurally identical in this header. They describe ring-buffer configuration, read/write pointer registers, write-pointer polling, read-pointer writeback, indirect-buffer state, context status, doorbell state, queue status, watermarks, context-save addresses, preemption, AQL mode, minor-pointer update, and mid-command snapshot/control fields.

## Important Macro Families

The exported macros follow the generated `SDMA4_RLC[6|7]_<REGISTER>__<FIELD>_{SHIFT,MASK}` convention:

- `RB_CNTL` defines queue enablement and identity fields: `RB_ENABLE`, `RB_SIZE`, `RB_SWAP_ENABLE`, `RPTR_WRITEBACK_ENABLE`, `RPTR_WRITEBACK_SWAP_ENABLE`, `RPTR_WRITEBACK_TIMER`, `RB_PRIV`, and `RB_VMID`.
- `RB_BASE` and `RB_BASE_HI` describe the split ring-buffer base address. The low word is full width and the high word is masked to `0x00FFFFFF`.
- `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, and `RB_WPTR_HI` describe 64-bit read/write pointer offsets split across low/high registers.
- `RB_WPTR_POLL_CNTL` controls hardware polling of a memory-backed write pointer through `ENABLE`, `SWAP_ENABLE`, `F32_POLL_ENABLE`, `FREQUENCY`, and `IDLE_POLL_COUNT`.
- `RB_RPTR_ADDR_HI/LO` describes the memory location used for read-pointer writeback. The low register has `RPTR_WB_IDLE` at bit 0 and a 4-byte-aligned `ADDR` field at bits 31:2.
- `RB_WPTR_POLL_ADDR_HI/LO` describes the memory location hardware polls for write-pointer updates, with the low address field also aligned to bits 31:2.
- `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO`, `IB_BASE_HI`, `IB_SIZE`, and `IB_SUB_REMAIN` describe indirect-buffer enablement, address, progress, size, and remaining sub-IB state.
- `CONTEXT_STATUS` exposes scheduler/context-switch state: `SELECTED`, `IDLE`, `EXPIRED`, packed `EXCEPTION`, `CTXSW_ABLE`, `CTXSW_READY`, `PREEMPTED`, and `PREEMPT_DISABLE`.
- `DOORBELL`, `DOORBELL_LOG`, and `DOORBELL_OFFSET` describe doorbell enable/captured state, logged data or bus-error state, and the aligned doorbell aperture offset.
- `STATUS` reports write-pointer update failure count and whether a write-pointer update is pending.
- `WATERMARK` packs read and write outstanding-watermark fields.
- `CSA_ADDR_LO/HI` describes the context-save area address used by context-switch/preemption machinery.
- `PREEMPT` exposes the `IB_PREEMPT` control bit.
- `DUMMY_REG` is a full-width scratch or placeholder register field.
- `RB_AQL_CNTL` defines AQL queue enablement, packet size, and packet step fields.
- `MINOR_PTR_UPDATE` exposes an `ENABLE` bit used around pointer update sequencing.
- `MIDCMD_DATA0` through `MIDCMD_DATA8` are full 32-bit mid-command snapshot data words, and `MIDCMD_CNTL` marks validity, copy mode, split state, and preemption allowance.

There are no callable APIs or C types in this chunk. The macros themselves are the interface.

## Control Flow and Data Flow

The header has no local runtime control flow. The effective data flow happens when AMDGPU and AMDKFD code program SDMA queue registers:

1. Driver code chooses an SDMA RLC register address from `sdma4_4_2_2_offset.h`, for example `mmSDMA4_RLC6_RB_CNTL` or `mmSDMA4_RLC7_RB_WPTR_POLL_CNTL`.
2. Code composes or decodes register values with the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros from this header.
3. SOC15/MMIO helpers read or write the selected register.
4. Hardware interprets the fields as queue state for ring execution, pointer polling/writeback, doorbell notification, indirect-buffer execution, context switching, preemption, AQL packet handling, and mid-command resume.

Two integration paths include this exact SDMA4 4.2.2 header pair:

- `amdgpu/sdma_v4_0.c` includes `sdma4/sdma4_4_2_2_offset.h` and `sdma4/sdma4_4_2_2_sh_mask.h` along with the other SDMA engines. Its golden-setting tables program related RLC fields such as `RB_RPTR_ADDR_LO` and `RB_WPTR_POLL_CNTL` for RLC queues on SDMA engines.
- `amdgpu/amdgpu_amdkfd_arcturus.c` includes the same header pair and computes an RLC register base from `engine_id` and `queue_id`. The KFD path uses the RLC register stride to load, dump, and destroy SDMA HQD/MQD state; RLC6 and RLC7 are reached by the same queue-indexed address math even though many field helper calls use the RLC0 macro names because the per-queue bit layouts are intentionally repeated.

## State and Persistence Behavior

This header stores no software state and persists nothing to disk. It describes hardware-owned register state:

- Ring-buffer state persists enablement, size, base address, read/write pointers, byte-swap behavior, read-pointer writeback policy, privilege, and VMID until the SDMA context is reset or reprogrammed.
- Polling state persists whether the engine polls a write-pointer memory address, how it swaps data, how often it polls, and how it behaves while idle.
- Doorbell state persists enablement, doorbell offset, captured-doorbell indication, and logged doorbell data or bus-error status.
- Indirect-buffer state persists IB enablement, base address, size, current read pointer, current offset, command VMID, and remaining sub-IB size while work executes.
- Context status, queue status, and watermarks are live hardware state reflecting selection, idleness, expiration, exception conditions, context-switch readiness, preemption state, pointer-update activity, and outstanding read/write pressure.
- Context-save and mid-command registers hold preemption/context-switch resume state, including context-save area address and mid-command snapshot words.
- AQL state persists whether AQL mode is active and how AQL packets are sized and stepped.
- `MINOR_PTR_UPDATE` is a transient sequencing control used when updating pointer fields.

The header does not encode reset values, access permissions, sticky-bit behavior, write-one-to-clear semantics, ordering requirements, or firmware ownership rules. Those constraints come from the hardware register database and the driver sequences that use these masks.

## Dependencies and Integration Points

Direct dependencies and integration contracts include:

- The matching offset header `sdma4_4_2_2_offset.h`. In that file, RLC6 starts at `mmSDMA4_RLC6_RB_CNTL = 0x0340` and RLC7 starts at `mmSDMA4_RLC7_RB_CNTL = 0x0398`, both with base index 1.
- Generated AMD register naming conventions. Helpers such as `REG_SET_FIELD(value, SDMA4_RLC6_RB_CNTL, RB_ENABLE, 1)` depend on exact `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` names.
- SOC15 register access and offset calculation through `SOC15_REG_OFFSET()`, `RREG32()`, `WREG32()`, and SDMA-specific wrappers in `sdma_v4_0.c`.
- AMDKFD Arcturus SDMA queue management. `get_sdma_rlc_reg_offset()` computes engine and queue offsets, and queue load/dump/destroy paths touch the same categories of RLC registers covered here.
- Memory-backed queue data: ring base, read/write pointers, read-pointer writeback address, write-pointer poll address, context-save area, and doorbell offset all connect these bitfields to GPU-visible memory and doorbell apertures.
- Firmware and scheduler behavior: context status, preemption, CSA, IB, and mid-command fields are meaningful only within SDMA firmware/hardware context-switch rules.

The same high-level field layout appears in adjacent engine headers (`sdma0` through `sdma7`) and newer multi-instance `sdma_4_4_0` headers, but names and offset namespaces differ. The 4.2.2 header uses `mmSDMA4_*` offsets in the engine-specific directory; later multi-instance headers use `regSDMA4_*` forms.

## Risks and Edge Cases

- This chunk begins at the RLC5 mid-command control register. Whole-file reconciliation should merge the RLC5 discussion with the preceding chunk before treating RLC5 as complete.
- The macros are untyped integer constants. A wrong mask or shift compiles cleanly but can program the wrong hardware bits.
- RLC6 and RLC7 are nearly identical to each other and to lower RLC queue contexts. Copy/paste or generator mistakes are easy to miss, and using the wrong queue offset can silently target a different queue context.
- Offsets and masks must come from the same IP-version header set. Mixing `sdma4_4_2_2_sh_mask.h` with unrelated SDMA4 or `sdma_4_4_0` offsets risks writes to the wrong register or wrong bit positions.
- Split address fields require correct low/high composition and alignment. `RB_RPTR_ADDR_LO`, `RB_WPTR_POLL_ADDR_LO`, `CSA_ADDR_LO`, and `DOORBELL_OFFSET` use low bits as reserved/control space rather than address payload.
- `IB_BASE_LO` starts at bit 5, so IB base programming must respect a stronger alignment than the 4-byte ring pointer address fields.
- `RB_CNTL` contains `RB_PRIV` and `RB_VMID`. Incorrect values can route work under the wrong privilege or GPUVM address space and can produce isolation failures or GPUVM faults.
- Pointer writeback, pointer polling, and doorbell fields connect hardware execution to memory and notification paths. Bad addresses or stale queue pointers can stall queues, corrupt memory, or wake the wrong queue.
- `CONTEXT_STATUS`, `STATUS`, `DOORBELL_LOG`, `WATERMARK`, `IB_SUB_REMAIN`, and `MIDCMD_*` are live hardware-updated fields. Debug code and tests should avoid assuming stable values unless the queue is idle or the driver follows documented polling rules.
- `PREEMPT`, `CSA_ADDR_*`, and `MIDCMD_*` are scheduler-sensitive. Writing them outside expected context-switch or preemption sequences can corrupt resume state or leave a queue wedged.

## Test and Validation Signals

Useful validation is mostly generated-header consistency plus hardware integration coverage:

- Build AMDGPU paths that include `sdma4/sdma4_4_2_2_sh_mask.h`, especially `sdma_v4_0.c` and `amdgpu_amdkfd_arcturus.c`; missing or renamed macros should fail at compile time.
- Static generation checks should verify every field in this chunk has a matching `_SHIFT` and `_MASK` pair and that full-width fields use `0xFFFFFFFFL`.
- Cross-check the masks against the authoritative SDMA4 4.2.2 register database, especially packed fields in `RB_CNTL`, `RB_WPTR_POLL_CNTL`, `CONTEXT_STATUS`, `DOORBELL`, `STATUS`, `WATERMARK`, `RB_AQL_CNTL`, and `MIDCMD_CNTL`.
- Check offset/header consistency: every RLC6/RLC7 register in `sdma4_4_2_2_offset.h` should have the corresponding field definitions here, and the RLC6-to-RLC7 stride should match the queue-index arithmetic used by AMDKFD.
- Boot/probe on Arcturus-class hardware should apply SDMA golden settings without SDMA register access faults or queue hangs.
- KFD SDMA queue load/dump/destroy tests should exercise high queue IDs that resolve to RLC6 and RLC7, verifying idle polling, doorbell setup, ring base/pointers, pointer writeback, and write-pointer polling.
- Queue submission tests should confirm ring pointer movement, read-pointer writeback memory updates, doorbell notification, IB execution, and VMID/privilege behavior for queues backed by these register contexts.
- Preemption/context-switch testing should observe `CONTEXT_STATUS`, `PREEMPT`, `CSA_ADDR_*`, `IB_SUB_REMAIN`, and `MIDCMD_*` before and after forced SDMA IB preemption.
- Register dump decoders should use these masks to decode live RLC6/RLC7 values and compare them with expected MQD/HQD configuration.

## Chunk Boundary Notes

This is the final chunk of `sdma4_4_2_2_sh_mask.h`. Merge/reconciliation should combine the initial `SDMA4_RLC5_MIDCMD_CNTL` block with the previous RLC5 chunk, treat RLC6 and RLC7 as complete context-register field blocks, and retain the closing include-guard note.
