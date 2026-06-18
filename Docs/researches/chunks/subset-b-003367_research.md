# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_0_sh_mask.h lines 10410-13008

## Scope

This chunk is a generated AMD SDMA 4.4.0 shift/mask header slice. It starts in the middle of the `SDMA3_RLC4_RB_WPTR_POLL_CNTL` register field list and ends in the middle of `SDMA4_RLC3_IB_CNTL`, after the `SWITCH_INSIDE_IB` shift field and before the remaining fields and masks. The document therefore covers a complete view of several repeated SDMA queue contexts, but not the full source header or even every register family touched by the first and last lines.

The covered register groups are:

- The tail of SDMA3 RLC4 queue-context masks, including write-pointer polling, read-pointer writeback address, indirect-buffer, doorbell, watermark, preempt, AQL, minor pointer, and mid-command fields.
- Full SDMA3 RLC5, RLC6, and RLC7 queue-context definitions with the same ring-buffer, indirect-buffer, context-status, doorbell, CSA, AQL, and mid-command layouts.
- The `sdma0_sdma4dec` address block for SDMA4 engine-public registers, including microcode access, VF enable, power/clock/control, status, error, UTCL1, performance counter, RAS, scratch, and copy-engine control registers.
- SDMA4 GFX and PAGE queue contexts.
- SDMA4 RLC0, RLC1, and RLC2 queue contexts.
- The beginning of SDMA4 RLC3 queue context through the first `IB_CNTL` shift fields.

This header chunk defines preprocessor constants only. It has no C functions, structs, variables, allocation paths, locks, or executable control flow.

## Purpose

The purpose of this range is to encode the bit-level contract between AMDGPU SDMA v4.4 code and the corresponding SDMA hardware registers. Every exported definition follows the generated convention:

- `REGISTER__FIELD__SHIFT` gives the bit position of a field.
- `REGISTER__FIELD_MASK` gives the raw register mask used to isolate or compose the field.

The companion header `sdma_4_4_0_offset.h` supplies register addresses such as `regSDMA4_POWER_CNTL`, `regSDMA4_GFX_RB_CNTL`, and `regSDMA4_RLC0_RB_CNTL`. This `_sh_mask` header supplies the field positions used with AMDGPU/SOC15 helpers such as `SOC15_REG_FIELD`, `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32`, and `WREG32`.

`drivers/gpu/drm/amd/amdgpu/sdma_v4_4.c` includes this header directly. That driver calculates per-instance SDMA register offsets, queries and clears SDMA RAS counters, and programs or observes SDMA hardware using the matching generated address and mask names.

## Important Macro Families

### SDMA Queue Contexts

Most of the chunk is generated repetition for queue contexts. The common layout appears for SDMA3 RLC queues, SDMA4 GFX/PAGE queues, and SDMA4 RLC queues:

- `*_RB_CNTL` fields control ring-buffer enablement, ring size, byte swapping, read-pointer writeback, writeback timer, privilege bit, and VMID.
- `*_RB_BASE` and `*_RB_BASE_HI` provide the ring-buffer base address fields.
- `*_RB_RPTR`, `*_RB_RPTR_HI`, `*_RB_WPTR`, and `*_RB_WPTR_HI` expose the ring read/write pointer offsets.
- `*_RB_WPTR_POLL_CNTL` controls hardware polling of the write pointer, including enable, swap enable, F32 polling, polling frequency, and idle poll count.
- `*_RB_RPTR_ADDR_HI` and `*_RB_RPTR_ADDR_LO` encode the read-pointer writeback address and the low-register `RPTR_WB_IDLE` status bit.
- `*_IB_CNTL`, `*_IB_RPTR`, `*_IB_OFFSET`, `*_IB_BASE_LO`, `*_IB_BASE_HI`, `*_IB_SIZE`, and `*_IB_SUB_REMAIN` describe indirect-buffer execution state.
- `*_SKIP_CNTL`, `*_PREEMPT`, `*_CONTEXT_STATUS`, `*_CSA_ADDR_LO`, and `*_CSA_ADDR_HI` describe command skipping, IB preemption, context-switch readiness/status, and context save area addresses.
- `*_DOORBELL`, `*_DOORBELL_LOG`, and `*_DOORBELL_OFFSET` define doorbell enable/captured state, logged backend error/data, and the doorbell offset.
- `*_WATERMARK` controls read and write outstanding request watermarks.
- `*_RB_AQL_CNTL` exposes AQL enablement, AQL packet size, and packet step.
- `*_MINOR_PTR_UPDATE` enables minor pointer update behavior.
- `*_MIDCMD_DATA0` through `*_MIDCMD_DATA10` plus `*_MIDCMD_CNTL` encode the mid-command preemption snapshot/control surface, including data-valid, copy-mode, split-state, and allow-preempt fields.

The RLC context families are especially repetitive. SDMA3 RLC5-RLC7 and SDMA4 RLC0-RLC2 are complete in this chunk. SDMA3 RLC4 lacks the earlier ring-control/base/pointer definitions because those are in the previous chunk. SDMA4 RLC3 starts here but continues in the next chunk.

### SDMA4 Engine Control and Status

The `sdma0_sdma4dec` block defines fields for SDMA4 itself:

- Microcode access: `SDMA4_UCODE_ADDR`, `SDMA4_UCODE_DATA`, `SDMA4_UCODE_CHECKSUM`, and `SDMA4_PUB_REG_TYPE0`.
- Virtualization enablement: `SDMA4_VF_ENABLE`.
- Power and clock control: `SDMA4_POWER_CNTL`, `SDMA4_POWER_CNTL_IDLE`, `SDMA4_CLK_CTRL`, `SDMA4_CLK_STATUS`, and `SDMA4_ULV_CNTL`.
- Top-level control: `SDMA4_CNTL`, `SDMA4_CHICKEN_BITS`, `SDMA4_CHICKEN_BITS_2`, `SDMA4_FREEZE`, `SDMA4_F32_CNTL`, `SDMA4_PHASE0_QUANTUM`, `SDMA4_PHASE1_QUANTUM`, and `SDMA4_PHASE2_QUANTUM`.
- Memory and address configuration: `SDMA4_GB_ADDR_CONFIG`, `SDMA4_GB_ADDR_CONFIG_READ`, `SDMA4_HBM_PAGE_CONFIG`, `SDMA4_PHYSICAL_ADDR_LO`, and `SDMA4_PHYSICAL_ADDR_HI`.
- Fetch/progress registers: `SDMA4_RB_RPTR_FETCH`, `SDMA4_RB_RPTR_FETCH_HI`, `SDMA4_IB_OFFSET_FETCH`, `SDMA4_PROGRAM`, and `SDMA4_SEM_WAIT_FAIL_TIMER_CNTL`.
- Status families: `SDMA4_STATUS_REG`, `SDMA4_STATUS1_REG`, `SDMA4_STATUS2_REG`, `SDMA4_STATUS3_REG`, and `SDMA4_STATUS4_REG`.

These fields describe engine idle state, ring and IB command fullness, packet readiness, memory-client read/write idle status, semaphore and interrupt stalls, context empty state, active queue ID, SR-IOV command activity, freeze/preempt state, and scheduler quantum selection.

### UTCL1, Address Translation, and XNACK

The `SDMA4_UTCL1_*` registers expose translation-cache and retry/error behavior:

- `SDMA4_UTCL1_CNTL` configures request mode, bypass flags, invalidation mode, retry disablement, redirection behavior, client ID, and queue depth.
- `SDMA4_UTCL1_WATERMK` sets read/write watermark thresholds.
- `SDMA4_UTCL1_RD_STATUS` and `SDMA4_UTCL1_WR_STATUS` expose FIFO empty/full state, page fault/null status, L2 idle state, next vector, merge state, and read/write routing or pointer-data FIFO state.
- `SDMA4_UTCL1_INV0`, `INV1`, and `INV2` describe invalidation requests, timeout/error controls, VMID vectors, flush type, and invalidate address pieces.
- `SDMA4_UTCL1_RD_XNACK*` and `WR_XNACK*` record XNACK address, VMID, vector, and XNACK state for read and write paths.
- `SDMA4_UTCL1_TIMEOUT` controls read/write XNACK timeout limits.
- `SDMA4_UTCL1_PAGE` defines page-fault request attributes such as VM hole, request type, memory type use, and page-table snoop use.

These fields are integration points with GPUVM, retryable page faults, memory translation, and diagnostic paths. The masks themselves do not encode the legal sequencing for invalidation or XNACK recovery.

### RAS, EDC, Error, and Performance Monitoring

The chunk includes SDMA4 reliability and observability fields:

- `CC_SDMA4_EDC_CONFIG` exposes EDC disablement.
- `SDMA4_EDC_COUNTER` has per-data-buffer single-error-detect counters for MBANK buffers 0 through 15.
- `SDMA4_EDC_COUNTER2` covers additional single-error-detect counters, including microcode, ring-buffer command, indirect-buffer command, UTCL1 read/write, data LUT, split data, and memory-client FIFOs.
- `SDMA4_RAS_STATUS` exposes ECC and NACK-generated error status for ring fetch, IB fetch, F32 data, semaphore/write-pointer atomic paths, copy data, SRAM, write-return data, and write/read pointer atomic paths.
- `SDMA4_ERROR_LOG` provides override and status fields.
- `SDMA4_PERFCNT_*` registers configure two performance counters, select result counters, set start/stop triggers, clear counters, stop on saturation, and read low/high counter values plus compare value.

`sdma_v4_4.c` has RAS query/reset code that uses shared SDMA counter masks through `SOC15_REG_FIELD` entries. The chunk's SDMA4-specific counter definitions are the generated per-instance equivalents of the same hardware layout.

## Control Flow and State Behavior

This chunk has no runtime control flow. Its effect is compile-time substitution:

1. AMDGPU code includes `sdma_4_4_0_offset.h` and `sdma_4_4_0_sh_mask.h`.
2. Code reads or prepares a 32-bit SDMA register value at an address from the offset header.
3. Code applies a generated mask and shift to decode a field or compose a new value.
4. Hardware state changes only when code outside this header writes the corresponding register.

The state represented by these macros is hardware state. Persistent or semi-persistent configuration includes ring bases, ring sizes, VMIDs, privilege bits, read-pointer writeback addresses, doorbell offsets, AQL settings, context save area addresses, watermarks, power/clock controls, UTCL1 control policy, performance counter configuration, and scheduler quantum registers. Transient state includes read/write pointers, context selected/idle/preempted flags, doorbell captured/log fields, status registers, FIFO full/empty flags, XNACK records, RAS/error status, EDC counters, and performance counter results.

Some fields are command-like or side-effectful at the hardware level, such as preempt, freeze, F32 halt/step/reset, counter clear, interrupt clear, invalidation controls, and RAS/counter clear behavior. The header does not indicate write-one-to-clear, sticky, polling, timeout, reset, or ordering requirements; those rules must come from the SDMA v4.4 driver and hardware specification.

## Dependencies and Integration Points

The immediate dependencies are the generated SDMA register headers:

- `sdma_4_4_0_offset.h` for register addresses and base indices.
- `sdma_4_4_0_sh_mask.h` for the shifts and masks in this chunk.
- Other SDMA generation headers such as `sdma_4_4_2_*` for nearby ASIC variants, which must not be mixed with 4.4.0 definitions without checking generation compatibility.

The main source-tree integration point is `drivers/gpu/drm/amd/amdgpu/sdma_v4_4.c`, which includes this header and the offset header. That driver provides per-instance register offset calculation, RAS error query/reset paths, and SDMA v4.4 hardware management. SDMA ring, VM, RAS, interrupt, reset, SR-IOV, and power-management code use the same generated naming convention through AMDGPU and SOC15 helpers.

Semantically, the queue-context fields integrate with AMDGPU ring scheduling and doorbells; IB fields integrate with indirect command submission; CSA and mid-command fields integrate with context switch and preemption; UTCL1 fields integrate with GPUVM, page-fault, and XNACK handling; EDC/RAS fields integrate with AMDGPU RAS reporting; performance counters integrate with profiling and debug paths; power/clock fields integrate with runtime power management and suspend/resume.

## Risks and Maintenance Notes

- The range starts and ends mid-family. Adjacent chunks are required for the complete SDMA3 RLC4 and SDMA4 RLC3 context descriptions.
- Bitfield drift is high impact. A wrong shift or mask can program the wrong ring size, VMID, address, doorbell, preempt bit, UTCL1 behavior, power state, or error counter.
- The queue-context blocks are highly repetitive. Copy or generation errors can be hard to review because only the SDMA instance and queue prefix changes.
- Address fields have alignment encoded in masks, such as ring-pointer writeback lows and IB base lows. Consumers must preserve the expected low-bit alignment and not treat full-width masks as arbitrary byte addresses.
- Doorbell and pointer fields are synchronization-sensitive. Incorrect polling frequency, stale read/write pointer decode, or bad doorbell offset can hang queues or lose submissions.
- Context-switch and mid-command fields are preemption-sensitive. Incorrect masks can break context save/restore, IB preemption, or SR-IOV/RLC scheduling behavior.
- UTCL1 invalidation and XNACK fields are VM-sensitive. Incorrect writes can turn translation faults into hangs, mask retry state, or invalidate the wrong VMID/address range.
- RAS and EDC counters may have clear-on-write or sticky semantics outside this header. Treating counter/status masks as normal read/write fields can lose diagnostic evidence.
- Full-width constants use the generated `L` suffix, including `0xFFFFFFFFL`; callers should continue using the established AMDGPU register helper types to avoid signedness or truncation problems.
- Cross-generation reuse is risky. The 4.4.0 and 4.4.2 headers look similar, but queue count, offsets, and masks can differ.

## Test and Validation Signals

Useful validation for this chunk is mostly build, static consistency, and hardware integration coverage:

- Build AMDGPU with SDMA v4.4 support so all includes of `sdma_4_4_0_sh_mask.h` and `sdma_4_4_0_offset.h` resolve.
- Static checks should confirm that each complete field in this chunk has matching `__SHIFT` and `_MASK` definitions and that masks are aligned with their shift positions.
- Cross-header checks should confirm every complete register family in this chunk has a matching address macro in `sdma_4_4_0_offset.h`.
- SDMA ring tests should submit GFX, PAGE, and RLC queue work and verify ring base, size, read/write pointer, doorbell, writeback, and IB progress fields decode correctly.
- Preemption/context-switch tests should exercise `CONTEXT_STATUS`, `CSA_ADDR`, `PREEMPT`, and `MIDCMD_*` behavior under IB preemption and context switching.
- VM and page-fault tests should exercise UTCL1 read/write status, invalidation, timeout, and XNACK reporting under GPUVM and retryable fault workloads.
- RAS validation should inject or observe SDMA EDC/ECC/NACK conditions and confirm `EDC_COUNTER`, `EDC_COUNTER2`, `RAS_STATUS`, and reset paths report and clear the intended fields.
- Power-management tests should cover SDMA clock/power gating, ULV entry/exit, freeze/unfreeze, suspend/resume, and idle status polling.
- Performance-counter validation should configure both SDMA4 counters, trigger start/stop/clear paths, and verify low/high result decoding without disturbing queue execution.
- SR-IOV or virtualization validation should cover VF enablement, RLC queue ownership/VMID fields, and status fields such as active queue ID and SR-IOV command activity.
