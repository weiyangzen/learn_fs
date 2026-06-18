# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 39878-42467

## Purpose

This chunk is generated AMD GC 10.3.0 register bitfield metadata. It contains no executable C code; it publishes preprocessor `__SHIFT` and `_MASK` constants used by AMDGPU/AMDKFD code to compose and decode 32-bit MMIO register values. The matching register offsets and base indices live in `gc_10_3_0_offset.h`.

The selected range covers the tail of the `SDMA2_PAGE` queue definitions, every replicated `SDMA2_RLC0` through `SDMA2_RLC7` queue definition, and the beginning of the public `SDMA3` register block. Although this repository subtree is under `ceph-client`, this header is GPU driver hardware metadata, not filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, memory allocations, locks, or callbacks in this range. The exposed API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit for a field inside a 32-bit hardware register.
- `<REGISTER>__<FIELD>_MASK` gives the in-register bit mask for the same field.
- Consumers combine these macros with `mm<REGISTER>` and `mm<REGISTER>_BASE_IDX` symbols from `gc_10_3_0_offset.h`, then access the register through AMDGPU helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

Major register groups in this chunk:

- `SDMA2_PAGE_*` continues the SDMA2 page-queue control block. It defines read-pointer writeback addresses, indirect-buffer enable/swap/switch controls, IB read pointer/offset/base/size fields, skip count, context status bits, doorbell enable/capture and log fields, outstanding read/write watermarks, CSA addresses, preemption, AQL enable/packet/overlap controls, minor pointer updates, and mid-command save/restore data/control registers.
- `SDMA2_RLC0_*` through `SDMA2_RLC7_*` are eight nearly identical SDMA RLC queue register windows. Each queue has ring-buffer control, base, read/write pointer, write-pointer polling control, read-pointer writeback address, indirect-buffer control and base/size, skip count, context status, doorbell state and offset, status/logging, watermarks, CSA address, IB preemption, AQL controls, minor-pointer update, and mid-command data/control fields.
- `SDMA3_DEC_START` and `SDMA3_GLOBAL_TIMESTAMP_LO/HI` begin the SDMA3 public register block with decode-start and timestamp data fields.
- `SDMA3_PG_*`, `SDMA3_POWER_CNTL`, `SDMA3_CLK_CTRL`, and `SDMA3_CNTL` define power-gating, context, clock, soft-reset, trap, halt, freeze, auto-context-switch, watch-dog, MIDCMD, and ATC/L1 enable controls.
- `SDMA3_STATUS_REG`, `SDMA3_STATUS1_REG`, `SDMA3_STATUS2_REG`, `SDMA3_STATUS3_REG`, `SDMA3_STATUS4_REG`, and the start of `SDMA3_STATUS5_REG` expose live engine, queue, command, outstanding-transaction, XNACK, SR-IOV, idle, and active-queue status. `STATUS5` begins the per-queue enable-status map for GFX, PAGE, and RLC0-RLC7 queues.
- `SDMA3_CHICKEN_BITS`, `SDMA3_CHICKEN_BITS_2`, `SDMA3_GB_ADDR_CONFIG`, `SDMA3_GB_ADDR_CONFIG_READ`, `SDMA3_RD_BURST_CNTL`, `SDMA3_HBM_PAGE_CONFIG`, `SDMA3_BA_THRESHOLD`, and `SDMA3_TILING_CONFIG` define hardware-tuning, address-layout, burst, page, boundary, and tiling fields.
- `SDMA3_RB_RPTR_FETCH*`, `SDMA3_IB_OFFSET_FETCH`, `SDMA3_SEM_WAIT_FAIL_TIMER_CNTL`, `SDMA3_PROGRAM`, `SDMA3_FREEZE`, and `SDMA3_PHASE0/1/2_QUANTUM` support queue pointer fetching, indirect-buffer progress, semaphore timeout behavior, program/control payloads, freeze behavior, and scheduler quantum configuration.
- `SDMA3_EDC_CONFIG`, `SDMA3_UCODE_CHECKSUM`, `SDMA3_ID`, `SDMA3_VERSION`, `SDMA3_EDC_COUNTER`, and `SDMA3_EDC_COUNTER_CLEAR` expose firmware/version identity and error-detection/correction accounting.
- `SDMA3_ATOMIC_*`, `SDMA3_UTCL1_*`, `SDMA3_RELAX_ORDERING_LUT`, `SDMA3_PHYSICAL_ADDR_*`, `SDMA3_EA_DBIT_ADDR_*`, and `SDMA3_TLBI_GCR_CNTL` describe atomic pre-op state, UTCL1 cache/TLB invalidation and XNACK status, relaxed-ordering lookup, translated physical address reporting, data-bit address access, and TLBI/GCR command sizing and credits.
- `SDMA3_ERROR_LOG`, `SDMA3_PUB_DUMMY_REG*`, `SDMA3_F32_COUNTER`, `SDMA3_CRD_CNTL`, `SDMA3_AQL_STATUS`, `SDMA3_INT_STATUS`, `SDMA3_HOLE_ADDR_*`, `SDMA3_CLOCK_GATING_REG`, `SDMA3_SCRATCH_RAM_*`, and `SDMA3_TIMESTAMP_CNTL` cover error override/status, dummy registers, F32 counter data, memory/request credits, AQL completion/invalid-command emptiness, raw interrupt status, hole-address values, clock-gating status, scratch RAM access, and timestamp capture.

Common field themes are `ENABLE`, `IDLE`, `STATUS`, `ADDR`, `OFFSET`, `SIZE`, `VMID`, `QUEUE_ID`, `PENDING`, `CAPTURED`, `EXCEPTION`, `PREEMPT`, `WATERMARK`, `CREDIT`, and `XNACK`. Full-width `0xFFFFFFFFL` fields are common for addresses, pointers, status payloads, scratch data, timestamps, and counter values.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by the driver and hardware:

1. GFX10.3 code includes `gc_10_3_0_offset.h` and `gc_10_3_0_sh_mask.h`.
2. Driver code selects a concrete SDMA register with the `mm*` offset and base-index macro.
3. It composes or extracts fields using the shift/mask macros in this header.
4. MMIO helpers perform the actual read or write while SDMA firmware, the scheduler, doorbell logic, memory-management blocks, and power-management code define the ordering semantics.

The chunk describes fields needed for ring setup, IB setup, queue status polling, pointer writeback, doorbells, preemption, AQL/MIDCMD state, SDMA3 power/clock/reset control, UTCL1 invalidation, XNACK reporting, and status collection. It does not encode queue bring-up order, firmware load order, reset timing, interrupt routing, doorbell aperture setup, memory barriers, or locking.

## State And Persistence Behavior

This file stores no software state and persists nothing. It describes hardware state in GC 10.3 SDMA registers.

The represented state includes ring-buffer base addresses and read/write pointers, write-pointer polling addresses and cadence, read-pointer writeback addresses, IB base/size/progress, context-selection and preemption status, doorbell enable/capture/log state, queue watermarks, CSA addresses, AQL and MIDCMD state, SDMA3 timestamps, power-gating and clock control, engine halt/freeze/watchdog settings, EDC counters, UTCL1 invalidation and XNACK status, relaxed-ordering/TLBI/GCR controls, scratch RAM, and per-queue enable status.

Persistence is hardware-defined. Some fields are durable configuration until reset or power-gating; some are live hardware-owned status; some are pointer or timestamp counters that change asynchronously; some are action strobes such as clears, invalidates, capture requests, reset bits, or preemption triggers. The masks do not state whether a field is read-only, write-only, self-clearing, sticky, write-one-to-clear, or reserved. Consumers must follow the SDMA programming sequence and preserve unrelated bits in mixed-control registers.

## Dependencies And Integration Points

The direct companion dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h`, which provides matching register offsets such as `mmSDMA2_RLC0_RB_CNTL`, `mmSDMA3_CNTL`, and `mmSDMA3_STATUS5_REG`. Generated enum/default headers and SDMA-specific headers can provide additional symbolic values, but this chunk only defines bit positions and masks.

Observed include coverage in this tree includes `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`, which includes this GC 10.3 shift/mask header for SMU/power-management register work. Related AMDGPU integration points are SDMA ring initialization, queue enable/disable, GPU reset and recovery, suspend/resume, runtime power management, doorbell setup, VMID/context handling, KFD queue management, AQL dispatch support, preemption, interrupt/debug status collection, and profiling or validation tools that read SDMA counters/status.

This header must stay synchronized with `gc_10_3_0_offset.h` and the ASIC register database. The repeated `SDMA2_RLCn` queue windows make it attractive for consumers to index queues arithmetically, but this header itself only exports flat macro names.

## Risks And Edge Cases

- Header/offset mismatch is the primary correctness risk. Pairing `gc_10_3_0_sh_mask.h` with an offset header from a different GC or SDMA revision can compile while reading or writing the wrong bits.
- The macros are untyped constants. A typo in a register family (`SDMA2_PAGE`, `SDMA2_RLCn`, or `SDMA3`) or field name can silently configure the wrong queue, VMID, pointer, address, or status check.
- The chunk starts mid-register-family at the tail of `SDMA2_PAGE_RB_WPTR_POLL_CNTL` and ends inside `SDMA3_STATUS5_REG`. Adjacent chunks are required for complete definitions of the first and last registers.
- Ring and IB fields are alignment-sensitive. Low-address masks such as `0xFFFFFFFCL` and `0xFFFFFFE0L` indicate required alignment; programming unaligned base or writeback addresses can corrupt pointer handling or fail silently.
- Doorbell, pointer polling, and writeback behavior is ordering-sensitive. Missing memory barriers, stale writeback memory, wrong poll frequency, or disabled doorbells can make queues appear idle or stuck.
- Context status, exception, preemption, and MIDCMD fields are live hardware state. Polling code must handle transitions, timeouts, and in-flight queue work rather than assuming one stable snapshot.
- Full-width masks do not imply safe writes. Many full-width fields are data windows, counters, pointers, status payloads, or hardware-owned values.
- Power, clock, reset, freeze, and watchdog fields can affect all SDMA work on the engine. Incorrect updates can hang queues, lose queue state, block recovery, or interact badly with runtime power transitions.
- UTCL1 invalidation, XNACK, TLBI, GCR, and physical-address fields are memory-management sensitive. Incorrect sequencing can produce stale translations, replay storms, false page-fault symptoms, or SR-IOV isolation issues.
- Reserved and chicken-bit fields are ASIC- and firmware-sensitive. Consumers should avoid writing undocumented bits and should preserve reserved bits during read-modify-write operations.

## Test Signals

Useful validation is mostly build, generated-header consistency, and hardware smoke coverage:

- Build AMDGPU, AMDKFD, and SMU code that includes `gc_10_3_0_sh_mask.h` with `gc_10_3_0_offset.h`.
- Generated-header checks that every `__SHIFT` has a matching `_MASK`, masks are aligned to shifts, and all register names in this slice match entries in `gc_10_3_0_offset.h`.
- Static checks for non-overlapping fields within each register, excluding documented aliases or full-width data/status fields.
- SDMA queue bring-up tests that program ring base/size, read/write pointers, pointer writeback, doorbells, and watermarks for page and RLC queues, then submit copy/fill work and verify completion.
- IB tests that enable IB processing, program IB base/size/offset fields, exercise `SWITCH_INSIDE_IB`, and verify read-pointer progress and timeout behavior.
- Preemption and context-switch tests that trigger queue preemption, poll `CONTEXT_STATUS`, inspect MIDCMD data/control restore fields, and confirm queues resume.
- AQL tests that enable AQL queue mode, vary packet size/step/overlap controls, and verify valid completion plus invalid-command status behavior.
- Reset, suspend/resume, runtime power-management, and GPU recovery tests while SDMA queues are active, because ring pointers, writeback memory, doorbell capture, clock/power-gating status, and scratch/timestamp state can be reset or stale.
- Memory-management tests that exercise UTCL1 invalidation, XNACK reporting, TLBI/GCR credit paths, atomics, and physical-address readback under VM faults and normal DMA.
- Regression indicators include stuck write pointers, unchanged read-pointer writeback, doorbell capture without progress, non-idle status after drains, unexpected XNACK/outstanding bits, EDC counter growth, zero or saturated timestamps/counters, queue enable-status mismatches, GPU reset during SDMA work, or failures isolated to one `RLCn` queue.
