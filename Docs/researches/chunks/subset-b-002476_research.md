# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 1-2591

## Scope

This chunk is the first chunk of the generated AMD GC 10.3.0 shift/mask header. It covers lines 1-2591 of `gc_10_3_0_sh_mask.h`, beginning with the license and include guard and then defining the visible `gc_sdma0_sdma0dec` register bitfields for SDMA0. The range contains 2,117 `#define` lines: the header guard plus 1,060 `__SHIFT` macros and 1,056 `_MASK` macros. The final line lands inside the `SDMA0_RLC6_CONTEXT_STATUS` mask list, so that register group continues in the next chunk.

The content is declarative only. There are no C functions, structs, enums, branches, loops, allocations, locking primitives, or local data storage. The exported surface is a large preprocessor namespace that maps SDMA0 register fields to bit positions and masks for GC 10.3.0-class hardware.

## Purpose

`gc_10_3_0_sh_mask.h` supplies symbolic bitfield definitions used by AMDGPU, KFD, SMU, and related driver code when programming or decoding GC 10.3.0 registers. Consumers pair these macros with the matching register offsets from `gc_10_3_0_offset.h` and with register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, and `RREG32_SOC15`. This avoids hard-coded bit positions in SDMA setup, power management, queue programming, VM invalidation, and diagnostics.

This slice focuses on SDMA0. It covers public/global SDMA0 control and status registers, UTCL1 virtual-memory request and invalidation state, hardware error/EDC counters, clock/power controls, and the start of the per-queue register sets for the GFX, PAGE, and RLC queues.

## Exported API Surface

There are no callable APIs or local types. The public interface is the macro naming pattern `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`.

Major complete or mostly complete register families in this chunk include:

- SDMA0 block and power/control registers: `SDMA0_DEC_START`, global timestamp low/high, `SDMA0_PG_CNTL`, page-gating context address/control, `SDMA0_POWER_CNTL`, `SDMA0_CLK_CTRL`, `SDMA0_CNTL`, and `SDMA0_CHICKEN_BITS`.
- Address and tiling configuration: `SDMA0_GB_ADDR_CONFIG`, `SDMA0_GB_ADDR_CONFIG_READ`, `SDMA0_TILING_CONFIG`, physical address low/high, hole address low/high, and page/HBM configuration fields.
- Ring and indirect-buffer fetch/program state: top-level `SDMA0_RB_RPTR_FETCH*`, `SDMA0_IB_OFFSET_FETCH`, `SDMA0_PROGRAM`, and the repeated per-queue RB/IB base, pointer, poll, size, and preempt registers.
- Status and diagnostics: `SDMA0_STATUS_REG`, `STATUS1_REG` through `STATUS5_REG`, `SDMA0_STATUS2_REG`, `SDMA0_STATUS3_REG`, `SDMA0_INT_STATUS`, `SDMA0_ERROR_LOG`, `SDMA0_CLOCK_GATING_REG`, `SDMA0_AQL_STATUS`, scratch RAM address/data, and timestamp capture.
- Microcontroller/debug controls: `SDMA0_F32_CNTL`, `SDMA0_F32_COUNTER`, checksum, freeze/preempt, phase quantum registers, mid-command data/control registers, and dummy registers.
- EDC/ECC and reliability counters: `SDMA0_EDC_CONFIG`, `SDMA0_EDC_COUNTER`, and `SDMA0_EDC_COUNTER_CLEAR`.
- UTCL1 virtual-memory path: `SDMA0_UTCL1_CNTL`, watermarks, read/write status, invalidate request/address/VMID registers, read/write XNACK address and metadata, XNACK timeout limits, and page attribute fields.
- Ordering, credits, and cache/TLB controls: `SDMA0_RELAX_ORDERING_LUT`, `SDMA0_CHICKEN_BITS_2`, `SDMA0_CRD_CNTL`, and `SDMA0_TLBI_GCR_CNTL`.
- Queue reset and enable/status registers: `SDMA0_QUEUE_RESET_REQ`, `SDMA0_STATUS5_REG`, and repeated queue groups for `GFX`, `PAGE`, `RLC0`, `RLC1`, `RLC2`, `RLC3`, `RLC4`, `RLC5`, and the beginning of `RLC6`.

The repeated queue groups share a consistent schema: `RB_CNTL`, `RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, `RB_WPTR_HI`, `RB_WPTR_POLL_CNTL`, writeback pointer address high/low, `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO`, `IB_BASE_HI`, `IB_SIZE`, skip count, context status, doorbell state/log/offset, queue status, watermark, CSA address, IB-sub-remaining, preempt, dummy, AQL control, minor pointer update, and mid-command data/control fields. In this chunk, that schema is complete for `GFX`, `PAGE`, and `RLC0` through `RLC5`; `RLC6` is only partially covered.

## Control Flow And State Behavior

This header has no software control flow. Runtime behavior appears only when other driver code includes the constants and uses them to compose MMIO read-modify-write values or decode MMIO readbacks.

The macros describe several hardware state domains:

- Power and clock state: `SDMA0_POWER_CNTL`, `SDMA0_CLK_CTRL`, `SDMA0_CLOCK_GATING_REG`, and clock-gating bits in `CHICKEN_BITS`/`CHICKEN_BITS_2` control or report SDMA power gating, memory power override, fine-grained clock gating, and delay/hysteresis timing. These settings persist in hardware registers until reset, suspend/resume restore, firmware rewrite, or driver reprogramming.
- Command processor state: `SDMA0_CNTL`, `FREEZE`, `F32_CNTL`, phase quantum registers, and mid-command fields affect trap handling, preemption, context/world switching, command processor halt/step/reset, and mid-command data restore.
- Queue state: RB/IB base, read/write pointers, pointer polling, doorbells, context status, queue resets, watermarks, CSA addresses, and AQL controls govern how SDMA queues fetch and execute work for graphics, page, and RLC queue contexts.
- VM and memory translation state: UTCL1 control, page, invalidation, XNACK, status, and timeout registers expose SDMA translation request behavior, page-fault/null handling, VMID invalidation, and read/write XNACK metadata.
- Diagnostics and error state: status, status1-5, EDC counters, error log, doorbell logs, checksums, scratch RAM, and timestamp capture provide readback points for idle detection, fault diagnosis, and reliability monitoring.

The header does not encode whether a field is read-only, write-only, sticky, write-one-to-clear, or firmware-owned. Field names such as `STATUS`, `ACK`, `FROZEN`, `IDLE`, `COUNTER`, and `LOG` imply readback or latched hardware state, while `CNTL`, `REQ`, `BASE`, `ADDR`, `SIZE`, `OFFSET`, and `ENABLE` imply configuration or command fields. The exact access semantics must be taken from the register database and the calling SDMA/AMDGPU code.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. Semantically this chunk depends on the matching GC 10.3.0 register address header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h`, and on generated defaults in the corresponding GC 10.3.0 default header.

Important integration points visible in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.c`, which includes the GC 10.3.0 mask namespace for shared SDMA handling.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_0.c` and `sdma_v5_0.c`, which use SDMA power-control masks such as `SDMA0_POWER_CNTL__MEM_POWER_OVERRIDE_MASK` and related timing/default masks while enabling/disabling SDMA memory power behavior.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c`, which includes `gc_10_3_0_sh_mask.h` for KFD/GFX 10.3 integration.
- KFD MQD managers such as `kfd_mqd_manager_v10.c`, which use SDMA queue-control shift macros like `SDMA0_RLC0_RB_CNTL__RB_SIZE__SHIFT`, `RB_VMID__SHIFT`, `RPTR_WRITEBACK_ENABLE__SHIFT`, and `RPTR_WRITEBACK_TIMER__SHIFT` to build SDMA queue descriptors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`, which includes this GC 10.3.0 register namespace for Vangogh SMU/GC power-management interaction.

At runtime these macros feed SDMA engine initialization, ring allocation and enablement, write pointer polling, doorbell setup, queue reset, KFD process queue programming, preemption/freeze flows, VM invalidation and XNACK diagnosis, power-gating setup, suspend/resume restore, and GPU reset recovery paths.

## Risks

- Generated-header drift is the main risk. A wrong shift or mask silently programs the wrong hardware bit and can break SDMA initialization, queue scheduling, power gating, VM invalidation, or status decoding.
- The queue register schema is highly repetitive across `GFX`, `PAGE`, and `RLC0` through later RLC queues. Copy-generation mistakes may affect only one queue instance, producing queue-specific hangs or KFD failures that are hard to distinguish from firmware or workload bugs.
- Ring-buffer fields are address- and alignment-sensitive. Incorrect masks for RB base, RPTR/WPTR, writeback addresses, doorbell offsets, or IB base/size fields can make SDMA fetch from the wrong memory, miss write pointer updates, or corrupt command streams.
- VM/UTCL1 fields are fault- and security-sensitive. Bad invalidation, VMID vector, page/null, XNACK, or timeout masks can leave stale translations, misreport page faults, or change retry behavior.
- Power and clock fields interact with firmware and power-management ownership. Incorrect `MEM_POWER_OVERRIDE`, clock-gating override, or delay fields can cause idle/resume races, hangs during low-power transitions, or unnecessary power use.
- Status and error fields may have special clear/read semantics not visible in the macro names. Using a `_MASK` macro from this header without the correct access protocol can clear diagnostics accidentally or poll the wrong condition.
- This chunk ends inside `SDMA0_RLC6_CONTEXT_STATUS`; merge-time validation must treat the missing remainder of that group as a chunk-boundary condition rather than a local omission.

## Test Signals

Useful validation is mostly generated-data, build, and hardware-integration oriented:

- Preprocess or compile AMDGPU, KFD, and SMU code paths that include `gc_10_3_0_offset.h`, `gc_10_3_0_sh_mask.h`, and related default headers.
- Static generation checks that complete register groups in this chunk have matching `__SHIFT` and `_MASK` definitions, with explicit exceptions for the header guard and the chunk-ending partial `SDMA0_RLC6_CONTEXT_STATUS` group.
- Cross-check macro names and field widths against the GC 10.3.0 register database and the matching offset/default headers, especially for repeated queue groups.
- SDMA bring-up tests on GC 10.3.0 hardware: enable/disable SDMA, initialize rings, submit copy/fill commands, exercise IB fetch, verify RPTR/WPTR writeback, and confirm doorbell updates.
- KFD queue tests that create SDMA queues with different VMIDs, exercise RLC queue descriptors, use AQL controls where applicable, and validate preemption/context status behavior.
- VM translation tests: update SDMA-visible page tables, issue UTCL1 invalidations, trigger controlled XNACK/page-fault/page-null paths, and confirm status/log fields decode correctly.
- Power-management tests across runtime idle, clock gating, suspend/resume, GPU reset, and firmware restore to confirm SDMA power-control and clock-gating fields remain coherent.
- Fault and reliability diagnostics: inject or observe EDC/ECC counters, doorbell backend errors, queue reset conditions, freeze/preempt flows, and status idle/outstanding bits.

## Chunk Notes For Merge

This document covers only lines 1-2591 of `gc_10_3_0_sh_mask.h`. Later chunks should continue `SDMA0_RLC6_CONTEXT_STATUS`, finish the remaining SDMA0/RLC queue definitions, and cover subsequent register blocks in the same generated header. The final per-file report should treat the whole file as a generated GC 10.3.0 register bitfield map consumed by AMDGPU, KFD, SMU, and low-level hardware programming code, not as executable driver logic.
