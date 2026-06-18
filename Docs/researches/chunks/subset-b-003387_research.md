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
