# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 2592-5176

## Scope

This chunk is a generated AMD GC 10.3.0 shift/mask header slice for SDMA register fields. It covers lines 2592 through 5176 and defines 2,124 preprocessor constants: 1,062 `__SHIFT` macros and 1,062 `_MASK` macros. The range begins inside the `SDMA0_RLC6_CONTEXT_STATUS` register group, completes `SDMA0_RLC6` tail fields and all `SDMA0_RLC7` queue fields, then covers the `gc_sdma1_sdma1dec` address block from `SDMA1_DEC_START` through `SDMA1_RLC4_MIDCMD_CNTL`. It ends at the start of `SDMA1_RLC5_RB_CNTL`, so the last RLC5 group continues in the next chunk.

The content is declarative only. There are no functions, structs, enums, runtime variables, branches, loops, locking operations, allocations, or direct MMIO accesses. The exported surface is the generated macro namespace that names bit positions and masks for GC 10.3.0 SDMA0/SDMA1 hardware registers.

## Purpose

`gc_10_3_0_sh_mask.h` gives AMDGPU, KFD, and MES code symbolic access to GC 10.3.0 register bitfields. Consumers combine these macros with companion register offsets from `gc_10_3_0_offset.h` and helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

This chunk focuses on SDMA command processor state:

- The tail of SDMA0 RLC queue contexts 6 and 7, including ring buffer, indirect buffer, doorbell, context status, AQL, preemption, and mid-command save/restore fields.
- The SDMA1 global decoder/control surface, including clocking, power, microcode/program/status, global timestamps, queue reset, RAS/EDC counters, address configuration, UTCL1 translation/cache state, atomic/preop configuration, and error/status reporting.
- SDMA1 queue contexts for `GFX`, `PAGE`, and RLC contexts 0 through 4, each with repeated ring buffer, indirect buffer, doorbell, context-save-area, polling, AQL, minor pointer update, preemption, and mid-command fields.

Although this source tree is under a `ceph-client` mirror, this file is AMD GPU register metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no callable APIs or local C types. The public contract is the generated pair pattern:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field.

Important macro families in this chunk include:

- `SDMA0_RLC6_*` and `SDMA0_RLC7_*`: queue-context fields for high-numbered RLC SDMA0 queues. RLC6 begins in this chunk after its `CONTEXT_STATUS` shifts/masks; RLC7 is complete.
- `SDMA1_DEC_START`, `SDMA1_GLOBAL_TIMESTAMP_{LO,HI}`, `SDMA1_PROGRAM`, `SDMA1_ID`, and `SDMA1_VERSION`: decoder, timestamp, program, identity, and version metadata fields.
- `SDMA1_PG_*`, `SDMA1_POWER_CNTL`, `SDMA1_CLK_CTRL`, `SDMA1_CLOCK_GATING_REG`, `SDMA1_FREEZE`, and `SDMA1_F32_CNTL`: power-gating, clock control, freeze, and F32 halt/control fields.
- `SDMA1_CNTL`, `SDMA1_CHICKEN_BITS`, and `SDMA1_CHICKEN_BITS_2`: global SDMA1 behavior controls, including UTC L1 enable, trap/interrupt behavior, context-empty interrupt enable, mid-command preemption enable, and implementation-specific workaround bits.
- `SDMA1_STATUS_REG`, `SDMA1_STATUS1_REG`, `SDMA1_STATUS2_REG`, `SDMA1_STATUS3_REG`, `SDMA1_STATUS4_REG`, and `SDMA1_STATUS5_REG`: engine, command, queue, CE/ME/RLC, read/write, phase, and idle/busy state readback fields.
- `SDMA1_EDC_CONFIG`, `SDMA1_EDC_COUNTER`, `SDMA1_EDC_COUNTER_CLEAR`, `SDMA1_EA_DBIT_ADDR_*`, and `SDMA1_ERROR_LOG`: RAS/error-detection and error address/log fields.
- `SDMA1_GB_ADDR_CONFIG` and `SDMA1_GB_ADDR_CONFIG_READ`: pipe, bank, shader-engine, row, column, pipe-interleave, and related graphics address geometry fields.
- `SDMA1_UTCL1_*`: UTCL1 control, watermarks, read/write status, invalidation request/status, XNACK read/write status, timeout, and page-translation/cache fields.
- `SDMA1_ATOMIC_*`, `SDMA1_RELAX_ORDERING_LUT`, `SDMA1_TLBI_GCR_CNTL`, and `SDMA1_TILING_CONFIG`: atomics, relaxed ordering, TLB invalidate/global cache request, and tiling controls.
- `SDMA1_QUEUE_RESET_REQ`: per-queue reset request/active bits for GFX, page, RLC, and extra queues; this is used by MES queue-management code through the matching offset.
- `SDMA1_GFX_*`, `SDMA1_PAGE_*`, and `SDMA1_RLC0_*` through `SDMA1_RLC4_*`: repeated queue-context register maps. Each full context includes `RB_CNTL`, `RB_BASE(_HI)`, `RB_RPTR(_HI)`, `RB_WPTR(_HI)`, `RB_WPTR_POLL_CNTL`, `RB_RPTR_ADDR_{HI,LO}`, `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_{LO,HI}`, `IB_SIZE`, `SKIP_CNTL`, `CONTEXT_STATUS`, `DOORBELL`, `STATUS`, `DOORBELL_LOG`, `WATERMARK`, `DOORBELL_OFFSET`, `CSA_ADDR_{LO,HI}`, `IB_SUB_REMAIN`, `PREEMPT`, `DUMMY_REG`, `RB_WPTR_POLL_ADDR_{HI,LO}`, `RB_AQL_CNTL`, `MINOR_PTR_UPDATE`, `MIDCMD_DATA0` through `MIDCMD_DATA10`, and `MIDCMD_CNTL`.

## Control Flow

This header has no local control flow. Runtime flow is supplied by driver code that includes this generated namespace:

1. SDMA initialization code selects the GC 10.3.0 offset and shift/mask headers.
2. Queue setup code builds ring-buffer, indirect-buffer, writeback, doorbell, VMID, and swap-control register values with `REG_SET_FIELD`.
3. Register helper calls write those values into the SDMA instance or context selected by the matching offset macros.
4. Runtime queue code updates write pointers through doorbells or direct register writes, polls read pointers/status, and uses preemption/reset/freeze paths when queues are stopped or recovered.
5. Diagnostics, RAS, reset, and MES paths read status/error fields or write queue reset request fields through the same register map.

The macros in this chunk do not encode programming order, access type, reset value, clear-on-read behavior, or write-one-to-clear semantics. Those rules live in the hardware specification, generated defaults, firmware expectations, and calling code.

## State And Persistence Behavior

The file itself stores no software state and persists nothing. It names hardware-visible SDMA state:

- Global SDMA1 state: clock/power gating, freeze/halt, trap and interrupt enables, power/phase quanta, timestamps, program counter/microcode checksum, error logs, EDC counters, atomic preop registers, physical-address debug, and status registers.
- Translation/cache state: UTCL1 enable/response behavior, watermarks, invalidation request/acknowledge/status, XNACK tracking, page/cache control, timeout behavior, and TLBI/GCR request fields.
- Queue state: ring buffer base/read/write pointers, write-pointer polling address and cadence, read-pointer writeback, VMID/privilege, indirect-buffer base/size/offset/read pointer, skip count, selected/idle/expired/exception/preempted context status, doorbell enable/capture/log/offset, context-save-area address, outstanding read/write watermarks, AQL packet controls, preemption controls, minor pointer update, and mid-command save/restore payload.
- Reset and recovery state: freeze/halt fields, queue reset request/active bits, preemption bits, context-status readbacks, and mid-command controls can participate in stop, preempt, reset, and restore flows.

Hardware register contents persist according to the SDMA and GC power/reset domains. Driver or firmware code must reprogram them after ASIC reset, GPU reset, suspend/resume, power-gating loss, or queue teardown/recreation. Context state such as ring pointers and CSA addresses is tied to live queues and must stay coherent with memory objects owned by AMDGPU/KFD.

## Dependencies And Integration Points

The only syntactic dependency is the C preprocessor. Semantically, this chunk must stay synchronized with AMD's GC 10.3.0 register database and the companion generated headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h` supplies the matching register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_default.h` supplies reset/default values for the same register generation.

Visible in-tree consumers include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c`, which includes this header for GC 10.3.0 SDMA programming, uses `REG_SET_FIELD` for ring, IB, doorbell, UTC L1, F32, preemption, and trap fields, and uses the matching offsets for SDMA instance addressing.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.c`, which includes this shift/mask file for shared SDMA helpers, context-save-area addressing, firmware/RAS plumbing, and SDMA interrupt/error handling support.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c`, which includes the GC 10.3.0 offset and shift/mask headers and derives SDMA RLC queue layout distances for KFD queue/MQD programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c`, which includes this header as part of GC 10.3.0 VM hub setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v11_0.c`, which uses `regSDMA1_QUEUE_RESET_REQ` to reset SDMA queues through MES.
- SDMA golden-register tables in related SDMA implementations use the same style of RLC IB and write-pointer polling registers; GC 10.3.0 SDMA bring-up relies on the same repeated queue-context contract.

Behaviorally, these macros integrate SDMA firmware, kernel ring management, KFD compute queues, VM translation/invalidation behavior, doorbell MMIO, RAS/ECC reporting, reset/recovery, SR-IOV ownership rules, and hardware debug/status dumps.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong bit shift or mask can compile cleanly while programming the wrong SDMA field at runtime.
- Queue-context blocks are highly repetitive. A generator or copy error in only `GFX`, `PAGE`, or one `RLCn` context can create queue-specific failures that are hard to isolate.
- This chunk has artificial boundaries. It starts after the beginning of `SDMA0_RLC6_CONTEXT_STATUS` and ends after only the first lines of `SDMA1_RLC5_RB_CNTL`; merge-time checks must reconcile adjacent chunks before making full-register completeness claims.
- Ring pointer and writeback fields are address and alignment sensitive. Bad `RB_BASE`, `RB_RPTR_ADDR_LO`, `RB_WPTR_POLL_ADDR_LO`, or high/low pointer masks can corrupt queue memory or make the scheduler see stale pointers.
- Doorbell fields are security and liveness sensitive. Incorrect `ENABLE`, `CAPTURED`, or `DOORBELL_OFFSET` masks can disable queue wakeups, alias another queue's doorbell, or cause missed submissions.
- VMID, privilege, and AQL fields affect process isolation and queue packet interpretation. Wrong masks for `RB_VMID`, `RB_PRIV`, `CMD_VMID`, AQL packet size/step, or overlap/preemption controls can affect KFD user queues.
- Preemption and mid-command fields are recovery-sensitive. Incorrect `PREEMPT`, `MIDCMD_DATA*`, `SPLIT_STATE`, or `ALLOW_PREEMPT` definitions can break context switching, mid-command restore, or queue reset recovery.
- UTCL1 invalidation, XNACK, and timeout fields are subtle. Misprogramming can leave stale translations, misreport retries, or produce process-visible memory faults under page migration or recoverable-fault workloads.
- Status, interrupt, EDC, and error-log fields may have sticky or clear-on-write semantics that are not represented in this header. Treating all `_MASK` fields as ordinary read/write bits can lose diagnostics or clear errors prematurely.
- Some SDMA registers may be firmware-, PSP-, MES-, or PF-owned depending on ASIC mode, SR-IOV, reset phase, or power state. Late or unauthorized writes can conflict with the owner.

## Test Signals

Useful validation is mostly generated-data, build, and hardware-integration oriented:

- Build or preprocess AMDGPU/KFD code paths that include `gc_10_3_0_offset.h` and `gc_10_3_0_sh_mask.h`, especially `sdma_v5_2.c`, `amdgpu_sdma.c`, `amdgpu_amdkfd_gfx_v10_3.c`, `gfxhub_v2_1.c`, and MES queue reset code.
- Static generation checks that every complete register group in this slice has matching `__SHIFT` and `_MASK` definitions, with explicit boundary exceptions for partial `SDMA0_RLC6_CONTEXT_STATUS` and `SDMA1_RLC5_RB_CNTL`.
- Cross-check register names in this chunk against `gc_10_3_0_offset.h` so each field group has a matching `mm` or `reg` offset definition and base index.
- Compare repeated queue-context blocks across `SDMA1_GFX`, `SDMA1_PAGE`, and `SDMA1_RLC0` through `SDMA1_RLC4`, and across adjacent chunks for RLC5-RLC7, allowing only intentional instance prefixes.
- Runtime SDMA queue tests on GC 10.3.0-class hardware: ring creation/destruction, IB submission, write-pointer doorbell updates, read-pointer writeback, polling mode, queue idle detection, and multi-instance SDMA traffic.
- KFD compute-queue tests that exercise RLC queues, VMID assignment, AQL packet handling, context-save-area setup, preemption, and queue reset/recovery.
- VM and memory tests that stress UTCL1 behavior: page-table updates, TLB invalidation, XNACK/retry paths, page migration, fault injection, and stale-translation detection.
- Suspend/resume, GPU reset, MES queue reset, SR-IOV VF/PF, and power-gating tests that confirm SDMA global and queue registers are restored or intentionally owned by firmware/PF.
- RAS and diagnostic tests that inject or observe SDMA EDC/ECC/error-log/status fields and verify interrupt dispatch, error counters, and reset policy.

## Chunk Notes For Merge

This document intentionally covers only lines 2592-5176 of `gc_10_3_0_sh_mask.h`. Earlier chunks should cover the start of `SDMA0_RLC6_CONTEXT_STATUS` and preceding SDMA0 queue/global fields. Later chunks should continue `SDMA1_RLC5_RB_CNTL`, the remaining SDMA1 RLC queues, and subsequent GC 10.3.0 register groups. The final per-file report should describe the whole file as a generated GC 10.3.0 ASIC bitfield map used by AMDGPU, KFD, MES, and SDMA hardware programming paths, not as handwritten executable logic.
