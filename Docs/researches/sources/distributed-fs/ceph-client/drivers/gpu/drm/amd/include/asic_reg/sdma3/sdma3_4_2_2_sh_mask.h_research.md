# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma3/sdma3_4_2_2_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003390`: lines 1-2569, `Docs/researches/chunks/subset-b-003390_research.md`
- `subset-b-003391`: lines 2570-2956, `Docs/researches/chunks/subset-b-003391_research.md`

## Chunk Research

### subset-b-003390: lines 1-2569

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma3/sdma3_4_2_2_sh_mask.h lines 1-2569

## Scope

This chunk covers the first 2,569 lines of the generated AMD SDMA3 4.2.2 shift/mask header. The file is part of the AMDGPU ASIC register description tree and contains C preprocessor constants only. It does not define C functions, structs, variables, storage, or executable control flow.

The covered address block is `sdma3_sdma3dec`. The range starts with the license/header guard and the first SDMA3 microcode/VM/public-register masks, then covers the public SDMA3 control and status registers, UTCL1 translation/fault registers, GPU IOV violation logging, the full GFX and PAGE context register templates, complete RLC0 through RLC4 context templates, and most of the RLC5 context template. The chunk ends at `SDMA3_RLC5_MIDCMD_DATA8__DATA8_MASK`; the RLC5 mid-command control fields and any later file content are outside this chunk.

## Purpose

This header provides the bit-level interface used by AMDGPU SDMA code to compose and decode 32-bit register values for SDMA engine instance 3 on the SDMA 4.2.2 register map. Each register field is represented by the generated convention:

- `<REGISTER>__<FIELD>__SHIFT` for the bit offset.
- `<REGISTER>__<FIELD>_MASK` for the field mask.

The matching offset header supplies register addresses, while this file supplies field positions. Driver code normally consumes these macros through AMD register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`, or through generated tables that need field masks for initialization, debug, reset, power, virtualization, and queue management paths.

## Important Macro Families

### Public SDMA Register Classification

The early `SDMA3_CONTEXT_REG_TYPE0` through `SDMA3_CONTEXT_REG_TYPE3` and `SDMA3_PUB_REG_TYPE0` through `SDMA3_PUB_REG_TYPE3` masks classify which SDMA registers belong to public or context-save groups. The context type fields enumerate GFX queue registers such as ring buffer control/base/read/write pointers, IB control/base/size, doorbell, context status/control, CSA address, AQL control, minor pointer update, and mid-command state registers.

The public register type masks enumerate top-level SDMA registers, including microcode access, VM context controls, active function ID, virtual reset/VF enable state, MMHUB control, power/clock/control/chicken bits, GB address configuration, status registers, UTCL1 registers, performance counters, error logs, physical address registers, GPU IOV violation logs, and ULV controls. These classification masks are important for context save/restore, virtualization filtering, and privilege-aware register access tables.

### Microcode, VM, Virtualization, and Function State

The first register fields cover low-level engine programming and virtualization state:

- `SDMA3_UCODE_ADDR` and `SDMA3_UCODE_DATA` expose the microcode address/data aperture.
- `SDMA3_VM_CNTL`, `SDMA3_VM_CTX_LO`, `SDMA3_VM_CTX_HI`, and `SDMA3_VM_CTX_CNTL` describe VM command, context address, privilege, and VMID fields.
- `SDMA3_ACTIVE_FCN_ID` exposes active VF ID and VF state.
- `SDMA3_VIRT_RESET_REQ` and `SDMA3_VF_ENABLE` expose virtual-function reset request and VF enable state.
- `SDMA3_MMHUB_CNTL` provides a MMHUB unit ID field.

These masks are integration points for firmware loading, VM setup, SR-IOV or virtualized SDMA operation, and function-level reset handling.

### Engine Control, Power, Clocking, and Address Configuration

The `SDMA3_CNTL` family defines engine-level features and interrupts: trap enable, UTC L1 enable, semaphore wait interrupt enable, data/fence swap controls, mid-command preempt/world-switch enable, automatic context switch enable, context-empty interrupt, frozen interrupt, and IB preempt interrupt.

Power and clock-related fields include:

- `SDMA3_POWER_CNTL` memory power override, light/deep/sleep power enable bits, and memory power delay.
- `SDMA3_CLK_CTRL` on-delay, off-hysteresis, and soft override bits.
- `SDMA3_POWER_CNTL_IDLE` delay timers.
- `SDMA3_ULV_CNTL` ULV hysteresis, enter/exit interrupt flags, clear bits, and status.

`SDMA3_GB_ADDR_CONFIG` and `SDMA3_GB_ADDR_CONFIG_READ` define NUM_PIPES, pipe interleave size, bank interleave size, NUM_BANKS, and NUM_SHADER_ENGINES fields. These fields tie SDMA addressing behavior to the GPU memory/bank geometry expected by the rest of the graphics and memory-management stack.

`SDMA3_CHICKEN_BITS` and `SDMA3_CHICKEN_BITS_2` are ASIC-specific tuning and workaround registers. The chunk exposes copy efficiency, transaction/data-buffer stall behavior, write burst length/wait cycle, copy overlap, RAW checking, SRBM poll retrying, clock-gating status output, time-based QoS, copy-engine FIFO watermarks, and F32 command processing delay.

### Queue Fetch, Status, Freeze, and Scheduling

The public queue/status block includes:

- `SDMA3_RB_RPTR_FETCH_HI`, `SDMA3_RB_RPTR_FETCH`, and `SDMA3_IB_OFFSET_FETCH` for fetched ring-buffer read pointer and indirect-buffer offsets.
- `SDMA3_PROGRAM` for a full-width stream/program field.
- `SDMA3_STATUS_REG`, which reports engine idle, register idle, RB empty/full, RB/IB command idle/full, block idle, inside-IB state, execution idle, packet-ready, MC read/write idle and stalls, SRBM idle, context-empty, previous command idle, semaphore state, and interrupt idle/stall state.
- `SDMA3_STATUS1_REG`, which focuses on copy-engine idle/full/stall state.
- `SDMA3_STATUS2_REG` and `SDMA3_STATUS3_REG`, which expose engine ID, F32 instruction pointer, current command operation, previous VM command, exception idle, queue ID match, and interrupt queue ID.
- `SDMA3_FREEZE` and `SDMA3_F32_CNTL` for preempt/freeze/frozen/F32 freeze and F32 halt/step control.
- `SDMA3_PHASE0_QUANTUM`, `SDMA3_PHASE1_QUANTUM`, and `SDMA3_PHASE2_QUANTUM` for scheduler quantum unit/value/preference fields.

These masks are used by reset, hang detection, queue draining, context switching, and debug paths that need to poll exact idle and stall bits before or after programming SDMA queues.

### Error Detection, Atomics, Performance, and Credits

The chunk defines ECC/EDC and debug counters:

- `SDMA3_EDC_CONFIG` disables/enables EDC/ECC interrupt behavior.
- `SDMA3_EDC_COUNTER` reports single-error-detected flags for microcode buffers, RB and IB command buffers, UTCL1 FIFOs, data LUT FIFO, multiple memory-bank data buffers, split data buffer, and MC write-address FIFO.
- `SDMA3_EDC_COUNTER_CLEAR` provides a clear trigger field.
- `SDMA3_ERROR_LOG` carries override and status halves.
- `SDMA3_EA_DBIT_ADDR_DATA` and `SDMA3_EA_DBIT_ADDR_INDEX` expose double-bit error address lookup data/index fields.

Atomic and credit fields include `SDMA3_ATOMIC_CNTL` loop timer and atomic-return interrupt enable, `SDMA3_ATOMIC_PREOP_LO/HI` data words, and `SDMA3_CRD_CNTL` MC write/read request credits.

Performance fields include `SDMA3_PERFMON_CNTL`, two full-width performance counter result registers, and `SDMA3_PERFCOUNTER_TAG_DELAY_RANGE`. These are debug and profiling integration points rather than normal queue submission state.

### UTCL1 Translation, Invalidation, Fault, and XNACK State

The UTCL1 register family is one of the highest-risk parts of this chunk because it bridges SDMA memory accesses to GPU virtual memory translation:

- `SDMA3_UTCL1_CNTL` controls redo enable/delay/watermark, invalidation-ack delay, L2 request credits, and virtual-address watermark.
- `SDMA3_UTCL1_WATERMK` defines request-to-MC, request-page, invalidation-request, and XNACK watermarks.
- `SDMA3_UTCL1_RD_STATUS` and `SDMA3_UTCL1_WR_STATUS` report many FIFO empty/full states, page fault/null status, L2 idle, CE/F32 stalls, next read/write vector, merge state, write pointer polling, invalidation request size, and request/data FIFO status.
- `SDMA3_UTCL1_INV0`, `INV1`, and `INV2` define invalidation control, timeout/error interpretation, flush idle state, invalidation flush type, VMID vectors, and invalidation address fields.
- `SDMA3_UTCL1_RD_XNACK0/1` and `SDMA3_UTCL1_WR_XNACK0/1` record XNACK address, VMID, vector, and XNACK status for read and write paths.
- `SDMA3_UTCL1_TIMEOUT` supplies read/write XNACK timeout limits.
- `SDMA3_UTCL1_PAGE` exposes VM hole, request type, memory type usage, and page-table snoop fields.

These definitions integrate with GPUVM, HMM/XNACK-capable memory fault handling, page invalidation, timeout recovery, and SDMA fault diagnosis.

### GPU IOV and Physical Address Diagnostics

Virtualization diagnostics include:

- `SDMA3_GPU_IOV_VIOLATION_LOG`, with violation status, multiple-violation status, address, write operation, VF flag, and VFID.
- `SDMA3_GPU_IOV_VIOLATION_LOG2`, with initiator ID.

`SDMA3_PHYSICAL_ADDR_LO` and `SDMA3_PHYSICAL_ADDR_HI` expose translated physical address state plus data-valid, dirty, and physical-valid bits. Together with the UTCL1 fault fields, these masks help decode faults and virtualization violations when SDMA accesses memory on behalf of PF/VF contexts.

### GFX and PAGE Queue Context Templates

The GFX and PAGE blocks define parallel queue-context layouts. Each queue block includes:

- Ring buffer programming: `*_RB_CNTL`, `*_RB_BASE`, `*_RB_BASE_HI`, `*_RB_RPTR`, `*_RB_RPTR_HI`, `*_RB_WPTR`, `*_RB_WPTR_HI`, and read-pointer writeback address registers.
- Write-pointer polling: `*_RB_WPTR_POLL_CNTL`, `*_RB_WPTR_POLL_ADDR_HI`, and `*_RB_WPTR_POLL_ADDR_LO`.
- Indirect buffer programming: `*_IB_CNTL`, `*_IB_RPTR`, `*_IB_OFFSET`, `*_IB_BASE_LO`, `*_IB_BASE_HI`, and `*_IB_SIZE`.
- Context state: `*_SKIP_CNTL`, `*_CONTEXT_STATUS`, `*_DOORBELL`, `*_STATUS`, `*_DOORBELL_LOG`, `*_WATERMARK`, `*_DOORBELL_OFFSET`, CSA address low/high, IB sub-remaining size, preempt, dummy register, AQL control, minor pointer update, and mid-command data/control.

The common bit layouts are repeated with different queue prefixes. `*_RB_CNTL` exposes enable, size, swap, read-pointer writeback, privilege, and VMID. `*_IB_CNTL` exposes IB enable, swap, switch-inside-IB, and command VMID. `*_CONTEXT_STATUS` exposes selected, idle, expired, exception, context-switch able/ready, preempted, and preempt-disable. `*_DOORBELL` exposes enable and captured. `*_RB_AQL_CNTL` exposes AQL enable, packet size, and packet step. `*_MIDCMD_CNTL` exposes data-valid, copy mode, split state, and allow-preempt fields.

These blocks are the per-queue persistent programming surface for SDMA command submission and preemption.

### RLC Queue Context Templates

The chunk fully covers RLC0, RLC1, RLC2, RLC3, and RLC4 context templates, and most of RLC5. Their layouts mirror the GFX/PAGE queue templates:

- Ring buffer base/read/write pointer and writeback address fields.
- Write-pointer polling fields.
- IB base/offset/read pointer/size fields.
- Skip count, context status, doorbell, doorbell log, watermarks, doorbell offset, CSA address, IB sub-remaining size, preempt, dummy, AQL, minor pointer update, and mid-command data fields.

The repeated RLC blocks provide multiple SDMA queues under RLC control with consistent field semantics. In this chunk, RLC5 ends at `SDMA3_RLC5_MIDCMD_DATA8`; its `MIDCMD_CNTL` fields are expected in the next chunk.

## APIs, Types, and Functions

There are no functions or C types in this chunk. The exported API surface is the macro namespace itself. Important usage patterns are:

- Field extraction: `(value & REGISTER__FIELD_MASK) >> REGISTER__FIELD__SHIFT`, usually through `REG_GET_FIELD`.
- Field composition/update: clearing `REGISTER__FIELD_MASK` and OR-ing shifted field values, usually through `REG_SET_FIELD`.
- Register writes/reads: using the matching register offset macros from the SDMA3 4.2.2 offset header with AMDGPU MMIO helpers.

Because the names are generated for a specific ASIC register version, consumers must include the matching offset, default, and mask headers together. Mixing masks from adjacent SDMA generations can silently target the wrong bit positions.

## Control Flow and State Behavior

This header has no runtime control flow. It influences compiled driver behavior by defining constants that control how runtime code interprets and writes SDMA registers.

The persistent state represented by the macros lives in hardware, not in this header. Long-lived programmed state includes microcode aperture state, VM context addresses and VMIDs, engine control bits, clock/power controls, address-configuration geometry, queue ring/IB bases and pointers, doorbell offsets, CSA addresses, AQL configuration, watermarks, context switch state, and RLC queue contexts. Diagnostic or transient state includes idle/stall bits, FIFO full/empty flags, XNACK/fault addresses, physical address decode status, EDC counters, GPU IOV violation logs, doorbell logs, performance counters, freeze/preempt flags, and interrupt status bits.

Some fields are command-like or sticky in hardware, such as reset requests, EDC counter clear, interrupt clear fields, invalidation controls, preempt/freeze controls, and violation/fault/error logs. The mask file does not encode write-one-to-clear, read-clear, polling, ordering, or timeout semantics; those rules must come from the SDMA driver and hardware specification.

## Dependencies and Integration Points

This chunk depends on the AMDGPU generated register-header convention:

- The matching SDMA3 4.2.2 offset header supplies register addresses for the `SDMA3_*` names.
- Matching default headers, where present, supply reset values.
- AMDGPU SOC15/MMIO register helpers consume the shift/mask constants.

Likely source-tree integration points include:

- SDMA engine initialization, microcode loading, clock/power programming, and reset handling.
- SDMA queue setup for GFX, PAGE, and RLC queues, including ring buffers, indirect buffers, doorbells, AQL mode, read-pointer writeback, polling addresses, and VMID/privilege selection.
- GPUVM and memory-fault paths that inspect or program UTCL1 invalidation, XNACK, page, timeout, and physical address state.
- SR-IOV and GPU virtualization paths that use active function, VF enable/reset, virtual register classification, and GPU IOV violation logs.
- Hang detection, preemption, context switch, freeze, and debug paths that poll status/context-status registers and mid-command save state.
- Reliability and diagnostics paths that inspect EDC counters, error logs, performance counters, credits, status registers, and doorbell logs.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can misprogram MMIO registers while still compiling cleanly.
- Queue context fields are repetitive across GFX, PAGE, and RLC0-RLC5. Copy/generation mistakes can affect only one queue and be hard to detect until that queue is exercised.
- VMID, privilege, UTCL1, XNACK, and invalidation fields are memory-isolation sensitive. Incorrect masks can cause wrong-address accesses, failed invalidations, lost page faults, or bad fault attribution.
- Doorbell and write-pointer fields are submission-critical. Incorrect doorbell enable/offset, polling address, or pointer mask can hang command submission or cause stale pointer writeback.
- Status and error fields may be sticky, write-one-to-clear, or race with hardware. Treating them as ordinary read/write bits can lose diagnostic evidence or fail recovery.
- Power, clock, and chicken-bit fields are ASIC-specific. Incorrect writes may introduce hangs, performance regressions, or power-management instability.
- Virtualization fields such as active function ID, VF enable/reset, register-type masks, and GPU IOV violation logs are privilege-sensitive. Incorrect filtering or decoding can break PF/VF isolation or obscure violation source.
- The chunk boundary cuts off RLC5 after `MIDCMD_DATA8`. Any per-file report must merge this chunk with the next chunk before drawing conclusions about the complete RLC5 context block.

## Test and Validation Signals

Useful validation is mostly build-time plus hardware integration:

- Build AMDGPU consumers that include `sdma3/sdma3_4_2_2_sh_mask.h`; this catches renamed or missing macro references.
- SDMA initialization should load microcode, program VM/MMHUB state, enable the engine, and report expected version/status fields.
- Queue tests should submit copy/fill/fence/poll/atomic workloads through GFX, PAGE, and RLC queues, then verify ring pointers, IB pointers, doorbells, read-pointer writeback, AQL mode, and context status.
- Reset and hang-recovery tests should verify idle polling, freeze/preempt, context-empty, IB-preempt interrupt, and mid-command save/restore behavior.
- GPUVM/XNACK tests should exercise valid translations, invalidations, page faults, XNACK retry, timeout limits, and physical address logging.
- SR-IOV tests should validate VF enable/reset, active VF ID reporting, virtual register access classification, and GPU IOV violation log decoding.
- Power-management tests should cover clock gating, memory power controls, ULV entry/exit, and idle delay behavior without corrupting queues.
- Reliability/debug tests should inject or observe EDC/error conditions, clear counters, read status registers, collect performance counters, and validate doorbell-log/error-log decoding.

### subset-b-003391: lines 2570-2956

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma3/sdma3_4_2_2_sh_mask.h lines 2570-2956

## Purpose

This chunk is the terminal range of the generated AMD SDMA3 4.2.2 shift/mask header. It defines preprocessor constants for SDMA3 RLC queue-context bitfields: the end of the RLC5 mid-command control block, the complete RLC6 queue block, and the complete RLC7 queue block. The range contains 300 `#define` entries: 150 `__SHIFT` macros and 150 `_MASK` macros. It has no executable C logic, structs, functions, enums, or storage; its API is the generated macro namespace consumed by AMDGPU and KFD register programming paths.

The covered queue blocks describe live SDMA queue state: ring-buffer enablement and sizing, ring base/read/write pointers, write-pointer polling, read-pointer writeback, indirect-buffer execution state, context status, doorbell routing, diagnostic status/logs, watermarks, context-save-area addresses, preemption state, AQL packet interpretation, minor pointer update gating, and mid-command save/restore state.

## Important Macros And Register Fields

- `SDMA3_RLC5_MIDCMD_CNTL` completes the RLC5 mid-command block with `DATA_VALID`, `COPY_MODE`, `SPLIT_STATE`, and `ALLOW_PREEMPT`.
- `SDMA3_RLC6_*` defines a full per-queue RLC context: `RB_CNTL`, `RB_BASE(_HI)`, `RB_RPTR(_HI)`, `RB_WPTR(_HI)`, `RB_WPTR_POLL_CNTL`, `RB_RPTR_ADDR_{HI,LO}`, `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_{LO,HI}`, `IB_SIZE`, `SKIP_CNTL`, `CONTEXT_STATUS`, `DOORBELL`, `STATUS`, `DOORBELL_LOG`, `WATERMARK`, `DOORBELL_OFFSET`, `CSA_ADDR_{LO,HI}`, `IB_SUB_REMAIN`, `PREEMPT`, `DUMMY_REG`, `RB_WPTR_POLL_ADDR_{HI,LO}`, `RB_AQL_CNTL`, `MINOR_PTR_UPDATE`, `MIDCMD_DATA0` through `MIDCMD_DATA8`, and `MIDCMD_CNTL`.
- `SDMA3_RLC7_*` repeats the same full schema for queue 7.
- `RB_CNTL` fields encode `RB_ENABLE`, ring size, endian/swap behavior, read-pointer writeback enable/swap/timer, privileged ring mode, and VMID.
- Pointer and address registers are split across low/high words. Low address masks enforce alignment: read-pointer writeback and poll addresses use bit 2 alignment, IB base low uses bit 5 alignment, and CSA low uses bit 2 alignment.
- `RB_WPTR_POLL_CNTL` exposes hardware polling knobs: `ENABLE`, `SWAP_ENABLE`, `F32_POLL_ENABLE`, polling `FREQUENCY`, and `IDLE_POLL_COUNT`.
- `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_*`, `IB_SIZE`, and `IB_SUB_REMAIN` describe indirect-buffer execution state for a queue.
- `CONTEXT_STATUS` reports `SELECTED`, `IDLE`, `EXPIRED`, `EXCEPTION`, `CTXSW_ABLE`, `CTXSW_READY`, `PREEMPTED`, and `PREEMPT_DISABLE`.
- `DOORBELL`, `DOORBELL_OFFSET`, and `DOORBELL_LOG` describe queue notification enablement, captured state, backend errors, and captured doorbell payload.
- `STATUS` exposes write-pointer update failure count and pending state. `WATERMARK` describes read and write outstanding request limits or counters.
- `RB_AQL_CNTL` fields (`AQL_ENABLE`, `AQL_PACKET_SIZE`, `PACKET_STEP`) describe AQL packet layout for KFD/HSA-style SDMA queues.
- `MIDCMD_DATA*` and `MIDCMD_CNTL` are context save/restore and preemption-related registers for preserving a partially executed SDMA command.

## Control Flow And Usage Model

This header has no branches, loops, or functions. Runtime behavior appears in callers that combine these masks with the companion offset header `sdma3_4_2_2_offset.h` and AMDGPU MMIO helpers.

The direct include sites in this tree are `amdgpu/sdma_v4_0.c` and `amdgpu/amdgpu_amdkfd_arcturus.c`. `sdma_v4_0.c` programs SDMA rings and golden settings through `RREG32_SDMA`, `WREG32_SDMA`, `SOC15_REG_GOLDEN_VALUE`, and `REG_SET_FIELD`; the golden settings explicitly include RLC6/RLC7 writeback-address and write-pointer-poll registers. `amdgpu_amdkfd_arcturus.c` implements KFD SDMA queue load, dump, occupancy, and destroy using the RLC0 register names plus computed queue offsets. That queue-relative pattern means the RLC6/RLC7 field layout must stay schema-compatible with RLC0 even when driver code does not name `SDMA3_RLC6_*` or `SDMA3_RLC7_*` directly.

For KFD-style queue restore, the effective sequence is: compute the SDMA engine and queue register offset, clear `RB_ENABLE`, poll `CONTEXT_STATUS.IDLE`, program doorbell state, program RPTR/WPTR and base/writeback addresses, use `MINOR_PTR_UPDATE` while updating pointers, then set `RB_ENABLE`. Dump paths iterate contiguous register windows from `RB_CNTL` through `DOORBELL`, from `STATUS` through `CSA_ADDR_HI`, from `IB_SUB_REMAIN` through `MINOR_PTR_UPDATE`, and from `MIDCMD_DATA0` through `MIDCMD_CNTL`.

## State And Persistence Behavior

The macros describe hardware register fields, not persistent software data. The state is volatile MMIO state owned by the SDMA engine and can be changed by driver writes, firmware/microcode, context switches, queue preemption, device reset, or power-management transitions.

Queue configuration and execution state lives in the `RB_*`, `IB_*`, `DOORBELL*`, `RB_AQL_CNTL`, and VMID/privilege fields. Context continuity is represented by `CSA_ADDR_*`, `IB_SUB_REMAIN`, `MIDCMD_DATA*`, and `MIDCMD_CNTL`. Diagnostic state is represented by `CONTEXT_STATUS`, `STATUS`, `DOORBELL_LOG`, and `WATERMARK`; those fields should be treated as hardware snapshots that may race with active queue execution.

MQD/HQD management in KFD persists selected queue values in software structures and restores them into these registers, but the header itself does not store anything. `MINOR_PTR_UPDATE` is a synchronization aid during pointer updates, especially for 64-bit pointer pairs where consuming a partially updated value would corrupt queue progress.

## Dependencies And Integration Points

- The companion address header `sdma3_4_2_2_offset.h` provides matching `mmSDMA3_RLC5_*`, `mmSDMA3_RLC6_*`, and `mmSDMA3_RLC7_*` register offsets. In that header, RLC6 starts at `mmSDMA3_RLC6_RB_CNTL` offset `0x0340` and RLC7 starts at `mmSDMA3_RLC7_RB_CNTL` offset `0x0398`.
- The broader SDMA 4.2.2 family includes matching `sdma0` through `sdma7` headers. Arcturus KFD code selects the engine base with `SOC15_REG_OFFSET(SDMA3, 0, mmSDMA3_RLC0_RB_CNTL)` and then applies queue spacing, so SDMA3 must match the common RLC queue layout.
- AMDGPU register helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` depend on the exact `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` naming convention used here.
- Doorbell integration depends on AMDGPU doorbell allocation and KFD user queues; incorrect `DOORBELL_OFFSET` or `ENABLE` values disconnect host submissions from the hardware queue.
- SDMA firmware/microcode and hardware context-switch logic consume the mid-command, preempt, IB, and CSA fields. These masks must match the ASIC register database, not merely the software naming pattern.

## Risks And Edge Cases

- Any wrong shift or mask silently targets the wrong hardware bits. Likely symptoms include SDMA queue hangs, missed doorbells, invalid VMID/privilege state, pointer corruption, failed preemption, or stuck non-idle queues.
- Address low-word masks encode alignment. Unaligned ring bases, writeback addresses, polling addresses, IB bases, or CSA addresses lose low bits and may redirect hardware memory accesses.
- RLC queue blocks are repetitive, making copy/paste or generation drift hard to spot. RLC6 and RLC7 should remain field-compatible with RLC0-RLC5 unless the hardware spec explicitly says otherwise.
- `CONTEXT_STATUS` and `STATUS` fields are live hardware state. Polling code needs timeouts, and diagnostic code should expect transient values.
- `RB_WPTR_POLL_CNTL` values affect dispatch latency, polling traffic, and SR-IOV behavior. Incorrect `F32_POLL_ENABLE`, frequency, or idle count can cause slow queue pickup or excessive polling.
- `MIDCMD_DATA*`, `MIDCMD_CNTL.DATA_VALID`, `SPLIT_STATE`, and `ALLOW_PREEMPT` are sensitive for mid-command preemption. Clearing or decoding them incorrectly can prevent a queue from resuming a split command.
- This is generated hardware-description material. Manual edits should be avoided unless regenerated from or checked against authoritative AMD register data.

## Test Signals

- Build coverage: `amdgpu/sdma_v4_0.c` and `amdgpu/amdgpu_amdkfd_arcturus.c` should compile with this header and the companion offset header included.
- Static header checks: every complete RLC6/RLC7 register field in this chunk should have paired `__SHIFT` and `_MASK` definitions, with no divergence from the equivalent RLC0-RLC5 field schema.
- Queue lifecycle tests: KFD SDMA queues on SDMA3 queue IDs 6 and 7 should load, become idle when disabled, restore ring pointers/base addresses/doorbells, and re-enable without timeout.
- Doorbell tests: host doorbell writes should advance queue WPTR state, avoid `DOORBELL_LOG.BE_ERROR`, and not leave `STATUS.WPTR_UPDATE_PENDING` stuck.
- Pointer/writeback tests: RPTR writeback should update the programmed memory address, and pointer restore should not regress when `MINOR_PTR_UPDATE` is toggled around low/high pointer writes.
- Preemption/context-switch tests: interrupted SDMA work should preserve `MIDCMD_DATA*`, `MIDCMD_CNTL.DATA_VALID`, `SPLIT_STATE`, and `IB_SUB_REMAIN` across suspend/resume or queue preemption.
- AQL tests: KFD/HSA SDMA AQL queues should validate `AQL_PACKET_SIZE` and `PACKET_STEP` programming for queues mapped to this RLC layout.

## Chunk Boundary Notes

This document covers only lines 2570-2956 of `sdma3_4_2_2_sh_mask.h`. The range begins after the RLC5 mid-command data registers, so it only contains `SDMA3_RLC5_MIDCMD_CNTL` for RLC5. It ends at the file's closing `#endif`, so RLC6 and RLC7 are complete within this chunk. Whole-file research should merge this with earlier chunks that cover SDMA3 global fields, GFX/PAGE queues, and RLC0-RLC5.
