# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma2/sdma2_4_2_2_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003387`: lines 1-2569, `Docs/researches/chunks/subset-b-003387_research.md`
- `subset-b-003388`: lines 2570-2956, `Docs/researches/chunks/subset-b-003388_research.md`

## Chunk Research

### subset-b-003387: lines 1-2569

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma2/sdma2_4_2_2_sh_mask.h lines 1-2569

## Scope And Purpose

This chunk is the first and largest part of an AMDGPU ASIC register bitfield mask header for the `sdma2_sdma2dec` address block. It is generated-style C preprocessor data, not executable code: each `SDMA2_*__*__SHIFT` and `SDMA2_*__*_MASK` macro names a field position and mask inside a 32-bit SDMA2 register for SDMA IP version `4_2_2`.

The header is part of the kernel DRM AMD register include tree. Its purpose is to let SDMA driver code compose, decode, and preserve hardware register values without hard-coding bit numbers at each call site. In practice this file is an ABI contract between the driver and the SDMA2 hardware block: ring setup, firmware control, virtual memory behavior, virtualization reporting, clock/power control, interrupt enablement, context switching, doorbells, writeback addresses, UTCL1 translation status, error reporting, performance counters, and per-context queue state all depend on these constants matching the hardware specification.

The requested range covers the include guard, public/global SDMA2 registers, GFX and PAGE context registers, and RLC context groups 0 through most of RLC5. It stops at line 2569 immediately before the `SDMA2_RLC5_MIDCMD_CNTL` definition. Later RLC5 control fields and the RLC6/RLC7 context groups are outside this chunk.

## Register Macro Model

Every register field is represented by two macros:

- `...__SHIFT` gives the least significant bit of the field.
- `..._MASK` gives the bit mask for the field, normally with an `L` suffix and sized for a 32-bit MMIO register.

The file does not define helper functions or C types. Callers are expected to use these macros with common AMDGPU register helpers such as field set/get macros, read-modify-write helpers, and MMIO register accessors from the surrounding driver. For single-bit fields the mask is one bit wide; for address, counter, timer, status-vector, or value fields the mask spans multiple bits. Several address fields are intentionally aligned, for example low address fields often start at bit 2 or bit 5 and mask off low alignment bits.

The initial context-reg and public-reg type registers are bitmaps that classify or expose register groups. `SDMA2_CONTEXT_REG_TYPE0` through `TYPE3` enumerate context-save/register windows for GFX queues, and `SDMA2_PUB_REG_TYPE0` through `TYPE3` enumerate public SDMA2 registers. These are integration metadata for register access, context switching, save/restore, or virtualization filtering logic rather than ordinary control registers.

## Public SDMA2 Registers

The public/global section defines the hardware control plane for the SDMA2 engine:

- Firmware and VM setup: `SDMA2_UCODE_ADDR`, `SDMA2_UCODE_DATA`, `SDMA2_UCODE_CHECKSUM`, `SDMA2_VM_CNTL`, `SDMA2_VM_CTX_LO`, `SDMA2_VM_CTX_HI`, and `SDMA2_VM_CTX_CNTL`.
- Function and virtualization state: `SDMA2_ACTIVE_FCN_ID`, `SDMA2_VIRT_RESET_REQ`, `SDMA2_VF_ENABLE`, `SDMA2_GPU_IOV_VIOLATION_LOG`, and `SDMA2_GPU_IOV_VIOLATION_LOG2`.
- Power and clocking: `SDMA2_POWER_CNTL`, `SDMA2_CLK_CTRL`, `SDMA2_POWER_CNTL_IDLE`, `SDMA_POWER_GATING`, `SDMA_PGFSM_CONFIG`, `SDMA_PGFSM_WRITE`, `SDMA_PGFSM_READ`, and `SDMA2_ULV_CNTL`.
- Engine behavior: `SDMA2_CNTL`, `SDMA2_CHICKEN_BITS`, `SDMA2_CHICKEN_BITS_2`, `SDMA2_RD_BURST_CNTL`, `SDMA2_HBM_PAGE_CONFIG`, `SDMA2_BA_THRESHOLD`, `SDMA2_CRD_CNTL`, and `SDMA2_RELAX_ORDERING_LUT`.
- Status, debug, and errors: `SDMA2_STATUS_REG`, `SDMA2_STATUS1_REG`, `SDMA2_STATUS2_REG`, `SDMA2_STATUS3_REG`, `SDMA2_ERROR_LOG`, `SDMA2_EDC_CONFIG`, `SDMA2_EDC_COUNTER`, and `SDMA2_EDC_COUNTER_CLEAR`.
- Atomic and address inspection: `SDMA2_ATOMIC_CNTL`, `SDMA2_ATOMIC_PREOP_LO`, `SDMA2_ATOMIC_PREOP_HI`, `SDMA2_PHYSICAL_ADDR_LO`, `SDMA2_PHYSICAL_ADDR_HI`, `SDMA2_EA_DBIT_ADDR_DATA`, and `SDMA2_EA_DBIT_ADDR_INDEX`.
- Performance and debug counters: `SDMA2_PERFMON_CNTL`, `SDMA2_PERFCOUNTER0_RESULT`, `SDMA2_PERFCOUNTER1_RESULT`, `SDMA2_PERFCOUNTER_TAG_DELAY_RANGE`, `SDMA2_F32_CNTL`, `SDMA2_F32_COUNTER`, `SDMA2_UNBREAKABLE`, and dummy registers.

`SDMA2_CNTL` is especially central. Its fields gate trap handling, UTC L1 translation support, semaphore wait interrupts, data and fence byte swapping, mid-command preemption/world switching, automatic context switching, context-empty interrupts, frozen interrupts, and IB preempt interrupts. Misprogramming these bits changes interrupt behavior and command processor scheduling semantics.

The status registers provide test and recovery signals. `SDMA2_STATUS_REG` reports global idle, ring-buffer and indirect-buffer command fullness/idleness, memory client read/write idleness, packet readiness, context empty state, semaphore stalls, and interrupt stalls. `SDMA2_STATUS1_REG` focuses on copy engine FIFOs and stalls. `SDMA2_STATUS2_REG` exposes an engine ID, F32 instruction pointer, and current command op. `SDMA2_STATUS3_REG` exposes command op status, previous VM command, exception idle, and queue-id match/interrupt queue id data.

## UTCL1 And VM Translation Fields

The UTCL1 register group describes the SDMA unit's translation-cache and page-fault/XNACK behavior. `SDMA2_UTCL1_CNTL` configures redo handling, redo delay/watermarks, invalidation acknowledgment delay, request-to-L2 credits, and virtual-address watermark. `SDMA2_UTCL1_WATERMK` provides per-read/write request-page and return-address watermarks.

`SDMA2_UTCL1_RD_STATUS` and `SDMA2_UTCL1_WR_STATUS` expose many FIFO-empty/FIFO-full bits plus page fault, page null, ReQL2 idle, retry/vector/merge state, and request-data FIFO status. These registers are important when diagnosing GPU VM hangs, XNACK replay behavior, and page-fault handling in SDMA copy or page queues.

The invalidation and XNACK registers are split into address/control pairs:

- `SDMA2_UTCL1_INV0`, `INV1`, and `INV2` hold invalidation mode, timeout flags, invalid-address behavior, VMID vectors, high and low invalidation address bits, and non-flush VMID vectors.
- `SDMA2_UTCL1_RD_XNACK0/1` and `SDMA2_UTCL1_WR_XNACK0/1` capture read/write XNACK address low/high bits, VMID, vector, and `IS_XNACK` state.
- `SDMA2_UTCL1_TIMEOUT` defines separate read and write XNACK limits.
- `SDMA2_UTCL1_PAGE` configures VM hole, request type, MTYPE usage, and page-table snoop behavior.

These fields integrate directly with the AMDGPU VM and MMHUB/GMC subsystems. Address masks in this group must be handled carefully because high-address fragments and VMID vectors are packed into the same 32-bit register words.

## Queue Context Register Groups

The chunk contains repeated context-register layouts for SDMA queues. The first two complete groups are `SDMA2_GFX_*` and `SDMA2_PAGE_*`; the same pattern then repeats for `SDMA2_RLC0_*` through `SDMA2_RLC5_*` up to `RLC5_MIDCMD_DATA8`.

Each queue context group includes:

- Ring buffer control and pointers: `*_RB_CNTL`, `*_RB_BASE`, `*_RB_BASE_HI`, `*_RB_RPTR`, `*_RB_RPTR_HI`, `*_RB_WPTR`, and `*_RB_WPTR_HI`.
- Write-pointer polling and read-pointer writeback: `*_RB_WPTR_POLL_CNTL`, `*_RB_RPTR_ADDR_HI`, `*_RB_RPTR_ADDR_LO`, `*_RB_WPTR_POLL_ADDR_HI`, and `*_RB_WPTR_POLL_ADDR_LO`.
- Indirect buffer execution state: `*_IB_CNTL`, `*_IB_RPTR`, `*_IB_OFFSET`, `*_IB_BASE_LO`, `*_IB_BASE_HI`, `*_IB_SIZE`, and `*_IB_SUB_REMAIN`.
- Queue scheduling and context state: `*_SKIP_CNTL`, `*_CONTEXT_STATUS`, `*_PREEMPT`, `*_MINOR_PTR_UPDATE`, and for GFX only `SDMA2_GFX_CONTEXT_CNTL`.
- Doorbell and queue diagnostics: `*_DOORBELL`, `*_DOORBELL_LOG`, `*_DOORBELL_OFFSET`, `*_STATUS`, and `*_WATERMARK`.
- Context save area and debug slots: `*_CSA_ADDR_LO`, `*_CSA_ADDR_HI`, `*_DUMMY_REG`, `*_MIDCMD_DATA0` through `*_MIDCMD_DATA8`, and `*_MIDCMD_CNTL` where present in this chunk.
- AQL controls: `*_RB_AQL_CNTL` with `AQL_ENABLE`, `AQL_PACKET_SIZE`, and `PACKET_STEP`.

The repeated definitions are deliberately nearly identical across GFX, PAGE, and RLC queue instances. This lets higher-level SDMA code program multiple hardware queue contexts with shared algorithms while selecting the correct register base/name for the target queue.

Important queue fields include `RB_ENABLE`, `RB_SIZE`, `RB_SWAP_ENABLE`, `RPTR_WRITEBACK_ENABLE`, `RPTR_WRITEBACK_TIMER`, `RB_PRIV`, and `RB_VMID` in `*_RB_CNTL`; `IB_ENABLE`, `IB_SWAP_ENABLE`, `SWITCH_INSIDE_IB`, and `CMD_VMID` in `*_IB_CNTL`; `SELECTED`, `IDLE`, `EXPIRED`, `EXCEPTION`, `CTXSW_ABLE`, `CTXSW_READY`, `PREEMPTED`, and `PREEMPT_DISABLE` in `*_CONTEXT_STATUS`; and `ENABLE`/`CAPTURED` in `*_DOORBELL`.

## Control Flow Implications

There is no C control flow in this header, but the bitfields encode SDMA hardware state-machine transitions that driver code relies on:

- Firmware loading writes through `SDMA2_UCODE_ADDR` and `SDMA2_UCODE_DATA`, then may check checksum/version/id fields.
- Queue bring-up programs ring base addresses, writeback addresses, VMID/privilege bits, swap behavior, doorbell offsets, and polling controls before enabling ring buffers and IB execution.
- Runtime submission advances write pointers through memory polling or doorbells; hardware advances read pointers and can write them back through the programmed writeback address.
- Preemption and context switching use `FREEZE`, `PREEMPT`, `CONTEXT_STATUS`, `MIDCMD_DATA*`, `MIDCMD_CNTL`, `PHASE*_QUANTUM`, and automatic context-switch bits.
- Page/translation faults and XNACK replay flow through UTCL1 status, invalidation, timeout, and XNACK capture fields.
- Error handling and diagnostics poll idle/status bits, EDC counters, IOV violation logs, error logs, and performance counters.

Because the macros are used in register programming paths, a wrong mask or shift can cause silent hardware misconfiguration rather than a normal compile-time failure.

## State And Persistence Behavior

The header itself has no storage, locks, or persistence. It defines constants for persistent hardware-visible state in MMIO registers and queue memory. Programmed register values remain in the SDMA block until reset, power gating, context save/restore, virtualization intervention, or explicit driver reprogramming changes them.

Several fields point at persistent GPU or system memory structures: ring buffers, indirect buffers, read-pointer writeback memory, write-pointer polling memory, context save areas, and AQL packet streams. Address fields with low-bit alignment masks must match the allocation and mapping constraints of those backing objects. VMID and privilege fields determine how SDMA interprets those addresses through GPU VM translation.

The register groups also support state preservation and recovery. Context status, mid-command data, IB sub-remaining, CSA addresses, phase quantums, preemption fields, and freeze/frozen bits are used when saving, restoring, preempting, or debugging an SDMA queue. IOV violation logs and EDC counters persist diagnostic evidence until cleared or overwritten by hardware behavior.

## Dependencies And Integration Points

This header is consumed by AMDGPU kernel code alongside the matching register-offset header for SDMA2 4.2.2 and common AMD register helper macros. It depends on the exact ASIC register specification but has no runtime includes beyond the include guard.

Key integration points are:

- SDMA engine initialization and firmware upload code that uses ucode, version, checksum, clock, power, and control fields.
- Ring management code that configures GFX, PAGE, and RLC queue ring buffers, write pointers, read-pointer writeback, doorbells, IBs, and AQL mode.
- GPU VM/MMHUB code that configures VM context, UTCL1, invalidations, page-fault/XNACK behavior, and physical address reporting.
- Interrupt and recovery code that enables context-empty/frozen/IB-preempt interrupts and polls status/idleness/stall fields during reset or hang recovery.
- SR-IOV and virtualization paths that interpret VF/PF enable/reset/function-id fields and IOV violation logs.
- Power management paths that program memory power, clock-gating, power-gating FSM, idle delay, and ultra-low-voltage bits.
- Debug/performance tooling that reads status registers, EDC counters, error logs, F32 counters, and performance counters.

## Risks And Edge Cases

- The file is a generated hardware contract. Manual edits risk diverging from hardware documentation and from sibling offset/mask headers for other SDMA instances or ASIC versions.
- Address masks encode alignment. Writing unaligned ring, IB, CSA, writeback, or polling addresses will drop low bits and can point hardware at the wrong memory.
- Many status and control registers pack unrelated concerns into one 32-bit word. Callers must use read-modify-write discipline and preserve reserved bits where required by the hardware spec.
- Repeated queue groups are easy to mix up. Accidentally using a GFX macro for PAGE/RLC or the wrong RLC instance can configure or diagnose a different queue than intended.
- Virtualization fields such as `VFID`, `VF`, `PF`, and IOV violation logs carry isolation-sensitive state. Incorrect decoding can hide or misattribute guest access violations.
- UTCL1 XNACK and invalidation fields combine address fragments, VMID vectors, timeout modes, and status flags. Incorrect field extraction can break fault attribution and replay recovery.
- Interrupt enable bits in `SDMA2_CNTL` and atomic/EDC controls can produce missed interrupts, excess interrupts, or unhandled error paths if programmed inconsistently with driver handlers.
- Some registers are diagnostics or clear-on-write style by hardware convention, such as EDC clear and interrupt clear fields. Tests and tools should avoid destructive reads/writes unless the hardware behavior is known.

## Test Signals

Useful validation for this chunk is mostly compile-time, register-programming, and hardware bring-up oriented:

- Build tests for AMDGPU configurations that include this header and exercise SDMA2 4.2.2 code paths, catching misspelled macros or type-width issues.
- Static comparison against the generated source of truth or AMD register database to verify each `SHIFT`/`MASK` pair and reserved-bit region.
- Unit or macro tests, where available, that compose and extract fields such as `RB_SIZE`, `RB_VMID`, `CMD_VMID`, `INV_VMID_VEC`, `XNACK_VECTOR`, and status fields.
- Hardware smoke tests that initialize SDMA2, load firmware, enable GFX/PAGE queues, submit copy/fill/fence packets, and verify ring read/write pointer movement and read-pointer writeback.
- VM fault and XNACK tests that trigger page faults, invalidations, and replay paths, then verify UTCL1 status and XNACK capture fields decode correctly.
- Suspend/resume, reset, preemption, and context-switch tests that observe `FREEZE`, `FROZEN`, `PREEMPT`, `CONTEXT_STATUS`, `MIDCMD_DATA*`, and phase quantum behavior.
- SR-IOV tests that validate VF enable/reset/function-id fields and IOV violation logging across host and guest contexts.
- Power-management tests around clock gating, memory power controls, power-gating FSM fields, idle delays, and ULV interrupt/status bits.

### subset-b-003388: lines 2570-2956

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma2/sdma2_4_2_2_sh_mask.h lines 2570-2956

## Scope

This chunk is the final section of the generated AMD SDMA2 4.2.2 shift/mask header. It begins at the tail of `SDMA2_RLC5_MIDCMD_*`, covers the complete field geometry for SDMA2 RLC queue contexts 6 and 7, and ends with the file's closing include guard.

The file is C preprocessor metadata only. It defines `*_SHIFT` and `*_MASK` constants for hardware register fields. It contains no functions, structs, enums, storage, allocation, locking, branches, loops, or direct MMIO accesses. The macros become useful when paired with the matching offset header, `sdma2_4_2_2_offset.h`, and AMDGPU register helpers such as `REG_SET_FIELD()`, `REG_GET_FIELD()`, `RREG32()`, `WREG32()`, and `SOC15_REG_OFFSET()`.

Although the repository path is under a `ceph-client` source mirror, this chunk documents AMD GPU SDMA register programming state. It is not distributed filesystem logic.

## Purpose

`sdma2_4_2_2_sh_mask.h` supplies symbolic bit positions and masks for SDMA engine 2 on the Arcturus-era SDMA 4.2.2 register layout. The covered range describes high-numbered RLC queue contexts:

- The first lines finish `SDMA2_RLC5_MIDCMD_CNTL`, exposing `DATA_VALID`, `COPY_MODE`, `SPLIT_STATE`, and `ALLOW_PREEMPT`.
- `SDMA2_RLC6_*` defines the full register-field layout for RLC queue 6.
- `SDMA2_RLC7_*` defines the full register-field layout for RLC queue 7.

RLC6 and RLC7 are structurally identical in this header. Each queue context exposes ring-buffer setup, read/write pointer state, write-pointer polling, read-pointer writeback, indirect-buffer execution state, queue status, doorbell state, memory watermarks, context-save addresses, preemption control, AQL packet controls, minor-pointer update, and mid-command snapshot/control words.

## Important Macro Families

The chunk exports these macro groups:

- `SDMA2_RLC[6|7]_RB_CNTL__*`: ring-buffer enablement and attributes. Fields include `RB_ENABLE`, `RB_SIZE`, `RB_SWAP_ENABLE`, `RPTR_WRITEBACK_ENABLE`, `RPTR_WRITEBACK_SWAP_ENABLE`, `RPTR_WRITEBACK_TIMER`, `RB_PRIV`, and `RB_VMID`.
- `SDMA2_RLC[6|7]_RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, and `RB_WPTR_HI`: ring base-address and producer/consumer pointer fields. The low base is full 32-bit and the high base carries a 24-bit address field.
- `SDMA2_RLC[6|7]_RB_WPTR_POLL_CNTL__*`: write-pointer polling configuration. It defines polling enable, swap enable, 32-bit polling mode, polling frequency, and idle poll count.
- `SDMA2_RLC[6|7]_RB_RPTR_ADDR_HI/LO` and `RB_WPTR_POLL_ADDR_HI/LO`: memory addresses for read-pointer writeback and write-pointer polling. Low address fields are 4-byte aligned with `ADDR__SHIFT = 0x2` and `ADDR_MASK = 0xFFFFFFFC`; `RB_RPTR_ADDR_LO` also contains `RPTR_WB_IDLE`.
- `SDMA2_RLC[6|7]_IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO`, `IB_BASE_HI`, `IB_SIZE`, and `IB_SUB_REMAIN`: indirect-buffer enablement, VMID selection for commands, base address, current pointer/offset, total size, and remaining sub-IB size.
- `SDMA2_RLC[6|7]_CONTEXT_STATUS__*`: hardware scheduling and context-switch status. Fields cover selected, idle, expired, exception bits, context-switch ability/readiness, preempted, and preempt-disable state.
- `SDMA2_RLC[6|7]_DOORBELL`, `DOORBELL_LOG`, and `DOORBELL_OFFSET`: doorbell enable/captured state, logged backend error/data, and the aligned doorbell aperture offset.
- `SDMA2_RLC[6|7]_STATUS__*`: write-pointer update failure count and pending-update state.
- `SDMA2_RLC[6|7]_WATERMARK__*`: read and write outstanding-watermark fields.
- `SDMA2_RLC[6|7]_CSA_ADDR_LO/HI`: context-save area address fields, with the low address aligned on bit 2.
- `SDMA2_RLC[6|7]_PREEMPT__IB_PREEMPT`: command bit used to request IB preemption.
- `SDMA2_RLC[6|7]_DUMMY_REG`: a full-width scratch/dummy field.
- `SDMA2_RLC[6|7]_RB_AQL_CNTL__*`: AQL/HSA queue controls for AQL enablement, packet size, and packet step.
- `SDMA2_RLC[6|7]_MINOR_PTR_UPDATE__ENABLE`: latch/control bit around minor pointer updates.
- `SDMA2_RLC[6|7]_MIDCMD_DATA0` through `MIDCMD_DATA8` and `MIDCMD_CNTL`: mid-command snapshot data and control fields for validity, copy mode, split state, and preemption allowance.

There are no callable APIs or C types in this chunk. The macro namespace is the public interface.

## Control Flow and Data Flow

This header has no local runtime control flow. Runtime behavior appears when AMDGPU code combines these masks with register addresses and MMIO accessors:

1. Code selects the SDMA engine and queue context. For Arcturus KFD SDMA queue management, `amdgpu_amdkfd_arcturus.c` includes `sdma2/sdma2_4_2_2_offset.h` and `sdma2/sdma2_4_2_2_sh_mask.h` alongside SDMA0 through SDMA7 headers.
2. `get_sdma_rlc_reg_offset()` computes a per-engine base and queue offset from `mmSDMA[0-7]_RLC0_RB_CNTL` plus a queue stride derived from `mmSDMA0_RLC1_RB_CNTL - mmSDMA0_RLC0_RB_CNTL`. For engine 2, this uses `SOC15_REG_OFFSET(SDMA2, 0, mmSDMA2_RLC0_RB_CNTL) - mmSDMA2_RLC0_RB_CNTL`.
3. Queue load, dump, occupancy, and destroy paths use RLC0 register names plus the computed queue offset. For queue ids 6 and 7 on SDMA engine 2, that addressing lands on the RLC6/RLC7 registers whose fields are described by this chunk.
4. Register helpers compose or test fields using the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` names. For example, queue load clears and later sets `RB_ENABLE`, waits for `CONTEXT_STATUS.IDLE`, programs doorbell offset/enable, writes ring pointers and base addresses, and toggles `MINOR_PTR_UPDATE` around write-pointer updates.
5. Hardware consumes the programmed register state to fetch ring commands, poll or write back pointers, process doorbells, execute IBs, save/resume context state, report queue status, and honor preemption/AQL controls.

The SDMA v4.0 initialization code also includes this header. Its SDMA 4.2 golden-setting tables program related high RLC queue registers for pointer-writeback idle state and write-pointer polling. In `sdma_v4_0.c`, SDMA0/SDMA1 golden settings include RLC6/RLC7 `RB_RPTR_ADDR_LO` and `RB_WPTR_POLL_CNTL` entries; the same field contract applies to the SDMA2 4.2.2 generated namespace when the Arcturus multi-SDMA engine path addresses engine 2.

## State and Persistence Behavior

The header stores no software state and persists nothing on disk. It describes hardware register state whose lifetime is controlled by SDMA engine reset, queue programming, context switching, power management, firmware behavior, and driver teardown.

Register-state categories in this chunk include:

- Ring state: enablement, queue size, base addresses, read/write pointers, byte-swap behavior, privilege, VMID, and read-pointer writeback settings.
- Pointer-memory state: memory addresses used by hardware for read-pointer writeback and write-pointer polling, including idle indication and polling cadence.
- Doorbell state: doorbell enablement, captured indication, offset, logged data, and backend-error indication.
- IB state: indirect-buffer enablement, base, size, current read pointer, current offset, command VMID, and remaining sub-IB size.
- Scheduler/context state: selected, idle, expired, exception bits, context-switch readiness, preempted, and preempt-disabled status.
- Context-save/preemption state: context-save area address, IB preempt request, mid-command data words, and mid-command control flags used to recover or continue interrupted work.
- AQL state: AQL enablement, packet size, and packet step.
- Live status/counters: write-pointer update failures, pending updates, and read/write outstanding-watermark values.

The header does not specify reset values, read/write permissions, sticky-bit behavior, write-one-to-clear semantics, or ordering rules. Those requirements come from the hardware register specification and the driver sequences that use the fields.

## Dependencies and Integration Points

Primary dependencies and integration points are:

- `sdma2_4_2_2_offset.h`: provides the concrete register addresses that match these masks. In the matching offset header, RLC6 starts at `mmSDMA2_RLC6_RB_CNTL = 0x0340` and RLC7 starts at `mmSDMA2_RLC7_RB_CNTL = 0x0398`, with the related status, context-save, preemption, polling, AQL, and mid-command registers laid out afterward.
- AMDGPU SOC15 register helpers: `SOC15_REG_OFFSET()` maps logical IP block/register names to MMIO addresses, while `RREG32()` and `WREG32()` perform 32-bit MMIO reads and writes.
- AMDGPU field helpers: `REG_SET_FIELD()` and related macros depend on the exact generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming convention.
- `amdgpu/amdgpu_amdkfd_arcturus.c`: includes this SDMA2 4.2.2 mask header and uses matching offset headers for KFD SDMA queue load, dump, occupancy, and destroy operations across SDMA engines and RLC queue ids.
- `amdgpu/sdma_v4_0.c`: includes the header in SDMA v4 bring-up code and uses related RLC queue register names in golden settings for pointer writeback and write-pointer polling.
- MQD state structures such as `struct v9_sdma_mqd`: queue load/destroy paths move software-saved queue state into and out of the hardware RLC registers whose fields are described here.
- Hardware doorbell, GPUVM/VMID, KFD queue scheduling, AQL/HSA queueing, and preemption/context-save mechanisms.

The RLC6/RLC7 layouts are part of a repeated generated pattern across SDMA engines 0 through 7. Engine-specific headers keep the same field concepts under distinct `SDMA<n>_` prefixes so callers do not mix IP blocks accidentally.

## Risks and Edge Cases

- The chunk starts inside `SDMA2_RLC5_MIDCMD_CNTL`; a whole-file report must merge this boundary with the preceding chunk before making complete RLC5 claims.
- These macros are untyped constants. A stale mask, wrong shift, or wrong IP-version header can compile cleanly but program the wrong hardware bits.
- RLC6 and RLC7 are almost identical. Generator, copy/paste, or merge errors are easy to miss unless checked against the authoritative register database and matching offset header.
- Queue addressing in Arcturus KFD is stride-based from RLC0. If the assumed RLC stride or offset-header layout drifts, queue id 6 or 7 can target the wrong context register block even though field masks still compile.
- Low address fields are alignment-sensitive. `ADDR__SHIFT = 0x2` and masks such as `0xFFFFFFFC` mean unaligned ring pointer writeback, write-pointer polling, CSA, IB, or doorbell offsets will lose low bits.
- `RB_CNTL.RB_VMID` and `RB_PRIV` affect address translation and privilege. Bad values can route SDMA work through the wrong VMID or trigger GPUVM faults/isolation failures.
- Doorbell offset and enable fields connect user/kernel queue signaling to hardware. Misprogramming can wake the wrong queue, miss queue updates, or leave stale captured/logged doorbell state.
- Pointer polling and writeback fields connect hardware to memory. Wrong addresses or swap settings can corrupt memory or make hardware consume stale producer pointers.
- `CONTEXT_STATUS`, `STATUS`, `WATERMARK`, `IB_SUB_REMAIN`, `DOORBELL_LOG`, and `MIDCMD_*` are live hardware-updated state. Diagnostics must account for races unless the queue is quiesced or the driver has explicit polling rules.
- Preemption and mid-command state are scheduler-sensitive. Writing `PREEMPT` or `MIDCMD_CNTL` outside the expected context-switch sequence can leave work partially saved, corrupt resume state, or stall the queue.
- The field layout is SDMA2 4.2.2-specific. Similar SDMA 4.2, SDMA 4.4, and GC-generated headers contain related but not necessarily identical address maps or mid-command data counts; mixing masks and offsets across generations is unsafe.

## Test and Validation Signals

Useful validation signals are mostly build-time, generated-header consistency, and hardware integration tests:

- Build AMDGPU/KFD code paths that include `sdma2/sdma2_4_2_2_sh_mask.h` with the matching offset header. Missing or renamed macros should fail at compile time.
- Static generation checks should verify every field in this chunk has a paired `_SHIFT` and `_MASK`, full-width fields use `0xFFFFFFFFL`, low aligned address fields mask off the low two or five bits as expected, and RLC6/RLC7 definitions remain structurally identical where the hardware requires it.
- Cross-check against `sdma2_4_2_2_offset.h`: every RLC6/RLC7 register in the offset header should have field definitions here, and the RLC6/RLC7 address ranges should preserve the queue-context stride used by KFD queue-offset calculations.
- Compare packed fields against the authoritative AMD register database, especially `RB_CNTL`, `RB_WPTR_POLL_CNTL`, `IB_CNTL`, `CONTEXT_STATUS`, `DOORBELL`, `STATUS`, `WATERMARK`, `RB_AQL_CNTL`, and `MIDCMD_CNTL`.
- On matching Arcturus/SDMA 4.2.2 hardware, KFD SDMA queue load should clear `RB_ENABLE`, observe `CONTEXT_STATUS.IDLE`, program doorbell, ring pointer, ring base, and read-pointer writeback registers, then set `RB_ENABLE` without timeout.
- Queue submission tests should verify ring write-pointer movement, read-pointer writeback, write-pointer polling, and doorbell notification for SDMA engine 2 high RLC queues when exposed by the driver configuration.
- Queue destroy tests should verify `RB_ENABLE` clearing, idle polling, doorbell disablement, and persistence of read-pointer values back into the MQD.
- Register dump tests should decode RLC6/RLC7 state using these masks and compare decoded values against expected queue configuration, VMID, privilege, doorbell offset, AQL mode, and idle/preempt status.
- Preemption/context-switch tests should exercise `PREEMPT`, `CONTEXT_STATUS`, `CSA_ADDR_*`, `IB_SUB_REMAIN`, and `MIDCMD_*` state around forced SDMA IB preemption and resume.

## Chunk Boundary Notes

This is the final chunk of `sdma2_4_2_2_sh_mask.h`. Merge/reconciliation should attach the initial RLC5 mid-command control lines to the previous RLC5 chunk, treat RLC6 and RLC7 as complete queue-context field blocks, and retain the closing include-guard note.
