# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002476`: lines 1-2591, `Docs/researches/chunks/subset-b-002476_research.md`
- `subset-b-002477`: lines 2592-5176, `Docs/researches/chunks/subset-b-002477_research.md`
- `subset-b-002478`: lines 5177-7648, `Docs/researches/chunks/subset-b-002478_research.md`
- `subset-b-002479`: lines 7649-10057, `Docs/researches/chunks/subset-b-002479_research.md`
- `subset-b-002480`: lines 10058-12395, `Docs/researches/chunks/subset-b-002480_research.md`
- `subset-b-002481`: lines 12396-14895, `Docs/researches/chunks/subset-b-002481_research.md`
- `subset-b-002482`: lines 14896-17371, `Docs/researches/chunks/subset-b-002482_research.md`
- `subset-b-002483`: lines 17372-19900, `Docs/researches/chunks/subset-b-002483_research.md`
- `subset-b-002484`: lines 19901-22380, `Docs/researches/chunks/subset-b-002484_research.md`
- `subset-b-002485`: lines 22381-24801, `Docs/researches/chunks/subset-b-002485_research.md`
- `subset-b-002486`: lines 24802-27455, `Docs/researches/chunks/subset-b-002486_research.md`
- `subset-b-002487`: lines 27456-30093, `Docs/researches/chunks/subset-b-002487_research.md`
- `subset-b-002488`: lines 30094-32558, `Docs/researches/chunks/subset-b-002488_research.md`
- `subset-b-002489`: lines 32559-35036, `Docs/researches/chunks/subset-b-002489_research.md`
- `subset-b-002490`: lines 35037-37447, `Docs/researches/chunks/subset-b-002490_research.md`
- `subset-b-002491`: lines 37448-39877, `Docs/researches/chunks/subset-b-002491_research.md`
- `subset-b-002492`: lines 39878-42467, `Docs/researches/chunks/subset-b-002492_research.md`
- `subset-b-002493`: lines 42468-45147, `Docs/researches/chunks/subset-b-002493_research.md`
- `subset-b-002494`: lines 45148-47858, `Docs/researches/chunks/subset-b-002494_research.md`
- `subset-b-002495`: lines 47859-49396, `Docs/researches/chunks/subset-b-002495_research.md`

## Chunk Research

### subset-b-002476: lines 1-2591

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

### subset-b-002477: lines 2592-5176

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

### subset-b-002478: lines 5177-7648

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 5177-7648

## Scope

This chunk is a generated AMD GC 10.3.0 shift/mask header segment. It covers line 5177 through line 7648 and defines 1,081 `__SHIFT` macros and 1,079 `_MASK` macros across 306 visible register comments. The range begins inside the `SDMA1_RLC5_RB_CNTL` field list, completes most of the `SDMA1_RLC5`, `SDMA1_RLC6`, and `SDMA1_RLC7` register groups, then enters the `gc_grbmdec`, `gc_cpdec`, and `gc_padec` address blocks. It ends inside `PA_SC_BINNER_EVENT_CNTL_3`, before the remaining masks for that register and later PA/SC fields.

The content is declarative only. There are no C functions, structs, enums, branches, loops, allocations, locks, or direct software-side state changes. The exported surface is a set of preprocessor constants that describe hardware register bit positions and bit masks.

## Purpose

`gc_10_3_0_sh_mask.h` supplies symbolic bitfield definitions for AMDGPU, KFD, SMU, and common SOC15 code that targets GC 10.3.0-class ASIC register layouts. Consumers pair these macros with matching offsets from `gc_10_3_0_offset.h` and use helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, `RREG32_SOC15`, `WREG32_SOC15`, and golden-register table helpers to program or inspect hardware without embedding raw bit positions.

This slice covers three broad hardware surfaces:

- SDMA1 RLC queue contexts 5 through 7, including ring-buffer base/pointer registers, write-pointer polling, indirect-buffer state, doorbells, context save area addresses, preemption, AQL controls, minor pointer update, and mid-command save/restore data.
- GRBM global graphics register-bus management, including busy/idle status, soft reset controls, graphics clock gating, shader-engine status, read/write error reporting, trap controls, scratch registers, fence ranges, UTCL2 invalidation range registers, and async VF violation data.
- Command-processor and primitive/raster front-end fields, including CP status/stall counters, MEC/ME controls, ring/queue thresholds, instruction pointers, command-index/data windows, VGT/WD/GE/IA controls, shader-array configuration, primitive setup/cache invalidation, PA clip/setup controls, and SC binner event routing.

## Exported API Surface

There are no callable APIs or local types. The public interface is the generated macro namespace:

- `SDMA1_RLC5_*`, `SDMA1_RLC6_*`, and `SDMA1_RLC7_*`: repeated register groups for each RLC SDMA context. Common fields include `RB_ENABLE`, `RB_SIZE`, `RB_SWAP_ENABLE`, read/write pointer offsets, writeback enable/timer/idle bits, write-pointer poll enable/frequency/idle count, IB enable/swap/switch/VMID fields, context status bits, doorbell enable/captured bits, doorbell data/error logging, outstanding read/write watermarks, CSA address fields, IB preemption, AQL packet controls, and mid-command data/control fields.
- `GRBM_*`: global graphics block management registers. Important fields include `READ_TIMEOUT`, `GUI_ACTIVE`, `CP_BUSY`, `CP_COHERENCY_BUSY`, graphics-block busy bits for PA/SC/BCI/SX/TA/DB/CB/GDS/SPI/GE, per-shader-engine busy/status fields, soft-reset bits for CP/GFX/RLC/HI/SEM/GRBM, graphics clock-enable and wait-idle timing fields, read/write error metadata, interrupt/trap controls, GFX pipe/queue selection, IH credits, power controls, UTCL2 invalidate ranges, fence ranges, and scratch register data.
- `VIOLATION_DATA_ASYNC_VF_PROG`: async virtual-function violation metadata, including VMID, client ID, source ID, write/read indicator, and data/protection/permission flags.
- `CP_*`: command-processor status and diagnostic fields for CPC, CPF, PFP, ME, CE, and MEC units. This includes busy/stalled status fields, GRBM free-count fields, privileged violation addresses, header dumps, scratch index/data access, halt hysteresis, event/de counts, instruction pointers, CSF status, MEC/ME halt controls, context status, preemption controls, ROQ/STQ/MEQ/CEQ thresholds and availability, ring-buffer pointers, write-pointer polling, command-index/data windows, and queue/IB/doorbell status registers.
- `VGT_*`, `WD_*`, `GE_*`, `IA_*`, `CC_GC_*`, `GC_USER_*`, and `GFX_PIPE_CONTROL`: primitive assembly, draw dispatch, geometry engine, input assembler, shader-array, and graphics pipe control fields. Examples include VGT cache invalidation policy, ESGS/GSVS/tessellation ring sizes, tessellation memory base, FIFO depths, vertex reuse, DMA primitive/control settings, WD QoS and UTCL1 status/control, GE status/private control, shader-array disables/configuration, and graphics pipe clock/ordering controls.
- `PA_*` and `PA_SC_BINNER_EVENT_CNTL_*`: primitive assembly clipping/setup and scan-converter binner fields. This chunk includes clipping enhancements, PA/SU busy status, SC FIFO depth, trap-screen hypervisor lock bits, forced end-of-vector maximum counters, and binner event routing fields for cache flushes, pipeline-stat/perf-counter events, streamout synchronization, thread-trace markers, context suspend, NGG/legacy pipeline enable events, and draw/pixel-shader completion.

Most complete register groups follow the generated pair pattern `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. The exceptions are chunk-boundary artifacts: the first lines are the tail of `SDMA1_RLC5_RB_CNTL`, whose comment and earlier fields are in the prior chunk, and the last line stops after `PA_SC_BINNER_EVENT_CNTL_3__PIXEL_PIPE_STAT_DUMP_MASK`, while the remaining `PA_SC_BINNER_EVENT_CNTL_3` masks continue in the next chunk.

## Control Flow And State Behavior

This header has no local control flow. Runtime behavior appears only when callers include the generated constants and use them to build MMIO register values, decode readbacks, or populate golden-register tables.

The names in this slice describe several hardware state machines and persistent register banks:

- SDMA RLC queue contexts persist ring-buffer addresses, read/write pointers, poll addresses, doorbell offsets, VMID/privilege selection, CSA state, AQL packet geometry, and mid-command preemption data. Driver or firmware writes these registers during queue setup, reset, suspend/resume restore, or golden-register initialization; hardware mutates pointer/status/log fields as it consumes packets and receives doorbells.
- GRBM status and reset fields expose global graphics progress. AMDGPU polling paths read `GRBM_STATUS`/`GRBM_STATUS2` to decide whether graphics is idle and build `GRBM_SOFT_RESET` requests when PA/SC/CP/RLC-like blocks stay busy.
- GRBM error, trap, fence, scratch, and UTCL2 invalidation fields are stateful hardware diagnostics or control windows. Some are intended for debug/error reporting, some are scratch storage, and some affect address-range invalidation or access filtering.
- CP registers expose command-processor pipeline state, queue/ring thresholds, stalled/busy conditions, instruction pointers, privileged violation addresses, and command data windows. The associated state is maintained by CP firmware/microcode and queue-management paths, while driver code reads it for debug, hang diagnosis, reset decisions, and queue programming.
- VGT/WD/GE/IA/PA/SC fields are graphics front-end and rasterization state. Cache invalidation, ring sizes, FIFO depths, primitive type/control, shader-array config, binner event mappings, clock-gating controls, and hypervisor lock bits persist until reprogrammed, reset, or restored by firmware/golden-register logic.

Read/write semantics are not encoded by the macro format alone. Fields named `STATUS`, `BUSY`, `STALLED`, `*_COUNT`, `*_DUMP`, `*_LOG`, `READ_ERROR`, `WRITE_ERROR`, and `VIOLATION` are readback or diagnostic by naming convention, while `CNTL`, `CONTROL`, `THRESHOLD`, `BASE`, `SIZE`, `OFFSET`, `SOFT_RESET`, `PREEMPTION`, and `*_POLL_*` fields are configuration-oriented. Actual read-only, sticky, write-one-to-clear, privileged, RLC-safe, PF-owned, and reset-default behavior must be verified against the register database and the calling driver path.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. Semantically, these definitions are tied to the matching GC 10.3.0 offset and default headers in the same `asic_reg/gc` directory. They are also consumed through AMDGPU's SOC15 register access layer and golden-register programming infrastructure.

Important integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c`, which uses GC 10.x GRBM fields to test graphics idleness, wait for `GUI_ACTIVE` to clear, inspect `GRBM_STATUS`/`GRBM_STATUS2` busy bits, compose `GRBM_SOFT_RESET`, and program PA/SC golden registers such as `PA_SC_BINNER_EVENT_CNTL_0` and `PA_SC_BINNER_TIMEOUT_COUNTER`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_0.c`, whose golden-register tables program `SDMA1_RLC5_RB_RPTR_ADDR_LO`, `SDMA1_RLC5_RB_WPTR_POLL_CNTL`, and the corresponding RLC6/RLC7 registers covered by this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c`, which includes `gc_10_3_0_offset.h` and `gc_10_3_0_sh_mask.h` for GC 10.3 KFD queue and shader-memory programming paths.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc15.c`, whose common golden-register write helper treats PA/SC and SH registers specially with RLC-safe writes, including `PA_SC_BINNER_EVENT_CNTL_3` and `PA_SC_ENHANCE`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`, which includes the GC 10.3.0 offset and shift/mask headers for Vangogh SMU/GC register interactions.
- AMDGPU diagnostics and reset tables across SOC generations use the same GRBM and CP naming model for register dump lists, idle checks, hang analysis, and soft-reset decisions, even when exact offset macro prefixes differ between generations.

At runtime these macros sit between generated register metadata and hardware-facing subsystems: SDMA queue bring-up, KFD queue management, graphics idle/reset logic, RLC/golden-register restore, command-processor diagnostics, front-end/raster setup, SR-IOV violation reporting, and power-management flows that need GC register fields.

## Risks

- Generated-header drift is the primary risk. A wrong bit position or mask can silently program the wrong SDMA queue context, GRBM reset bit, CP control field, or graphics front-end control.
- The SDMA1 RLC5/RLC6/RLC7 groups are highly repetitive. Copy-generation mistakes can affect only one queue context, producing queue-specific hangs, missed write-pointer polling, incorrect read-pointer writeback, broken doorbells, or failed preemption.
- Split address fields such as RB base, IB base, poll address, and CSA address require correct high/low masking and alignment. Bad masks can point DMA hardware at the wrong VRAM/system-memory page.
- Doorbell, AQL, and poll-control bits are externally visible to user queue submission. Incorrect enable, swap, timer, frequency, or VMID fields can cause missed submissions, stale pointers, wrong-endian pointer fetches, or privilege/VMID isolation problems.
- GRBM busy and reset masks directly affect hang detection and recovery. Misdecoded busy bits can trigger unnecessary resets or miss a stuck block; wrong `GRBM_SOFT_RESET` fields can reset the wrong sub-block or fail to recover the actual one.
- CP diagnostic and threshold fields are microcode-facing. Incorrect threshold, halt, ring, or queue availability fields can deadlock command submission or make hang dumps misleading.
- PA/SC binner event-control fields map hardware events into binner behavior. Wrong event encodings can break cache flush ordering, pipeline statistics, perf counters, thread trace, streamout synchronization, NGG/legacy pipeline switching, or draw completion signaling.
- Some registers are likely privileged, PF-owned, firmware-owned, or RLC-mediated in SR-IOV, power-management, and reset flows. Direct writes from the wrong context can be ignored, fault, or conflict with firmware state.
- The chunk starts and ends inside register groups. Merge-time validation should account for missing pairs at `SDMA1_RLC5_RB_CNTL` and `PA_SC_BINNER_EVENT_CNTL_3` as chunking artifacts, not local generation failures.

## Test Signals

Useful validation is mostly build-time, generated-data, and hardware-integration oriented:

- Compile or preprocess AMDGPU, KFD, SMU, and SOC15 paths that include `gc_10_3_0_offset.h`, `gc_10_3_0_sh_mask.h`, and the matching default header.
- Run generated-header consistency checks over the full file: every complete register field should have matching `__SHIFT` and `_MASK` definitions, with explicit boundary exceptions for this chunk's partial `SDMA1_RLC5_RB_CNTL` start and `PA_SC_BINNER_EVENT_CNTL_3` end.
- Cross-check register names and field widths against the GC 10.3.0 register database and offset header, especially repeated SDMA1 RLC context spacing and GRBM/CP/PA address-block transitions at lines 5774, 6252, and 7105.
- SDMA validation on GC 10.3.0-class hardware: initialize RLC5/RLC6/RLC7 queues, submit ring and indirect-buffer work, exercise doorbells and write-pointer polling, verify read-pointer writeback, test AQL mode when enabled, and validate preemption/context-save behavior.
- Graphics idle/reset testing: submit graphics and compute workloads, verify `GRBM_STATUS`/`GRBM_STATUS2` polling, force hang/reset paths, and confirm `GRBM_SOFT_RESET` recovery selects the intended sub-blocks.
- CP diagnostics: capture register dumps during normal operation and induced hangs, confirm busy/stall/header/instruction-pointer fields decode coherently, and check privileged violation addresses for expected values during negative tests.
- Front-end/raster tests: draw workloads that exercise VGT cache invalidation, tessellation/geometry ring sizing, WD/GE/IA status, shader-array configuration, PA clipping/setup, SC binner event routing, pipeline stats, perf counters, and thread trace markers.
- Suspend/resume, GPU reset, SR-IOV VF/PF, and firmware restore tests that ensure SDMA, GRBM, CP, and PA/SC state is restored by the correct owner and that RLC-safe writes are used where required.

## Chunk Notes For Merge

This document is intentionally source-tree aligned and covers only lines 5177-7648 of `gc_10_3_0_sh_mask.h`. Earlier chunks should cover the start of `SDMA1_RLC5_RB_CNTL` and RLC0 through RLC4 definitions. Later chunks should complete `PA_SC_BINNER_EVENT_CNTL_3`, continue PA/SC binner performance and enhancement fields, and cover the remaining GC 10.3.0 register groups. The final per-file report should treat the whole header as generated GC 10.3.0 hardware bitfield metadata used by AMDGPU/KFD/SMU register programming paths, not as handwritten executable driver logic.

### subset-b-002479: lines 7649-10057

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 7649-10057

## Scope

This chunk is a generated AMDGPU GC 10.3.0 shader-mask header segment. It contains C preprocessor constants only: each register field has a `__SHIFT` constant and a matching `MASK` constant. The paired register-address definitions live in the corresponding GC offset headers, while driver code consumes these names through helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and golden-register table initializers.

The range starts in the primitive assembly/scanner (`PA_SC`) binner event/control area, then covers full register-field maps for the `gc_sqdec`, `gc_shsdec`, `gc_tpdec`, `gc_gdsdec`, and most of `gc_rbdec` address blocks, ending at the first part of `CB_HW_CONTROL_4`.

## Purpose

The purpose of this header slice is to make GC 10.3.0 register bit layouts available to the AMDGPU kernel driver without hand-coded numeric shifts at every call site. These masks let runtime code extract hardware topology from registers, apply ASIC-specific golden settings, program diagnostics such as thread trace and watchpoints, and decode or control low-level GPU blocks.

Important consumers are in the GC 10 driver path, especially `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c`. That file includes the GC 10.1 header directly but also defines/adapts GC 10.3 aliases, uses the same field-name contract, and programs many registers represented by this chunk. For GC 10.3 ASICs, `gfx_v10_0_gpu_early_init()` reads `mmGB_ADDR_CONFIG` and derives `adev->gfx.config.gb_addr_config_fields` with `REG_GET_FIELD(..., GB_ADDR_CONFIG, NUM_PKRS/NUM_PIPES/MAX_COMPRESSED_FRAGS/NUM_RB_PER_SE/NUM_SHADER_ENGINES/PIPE_INTERLEAVE_SIZE)`. The same source carries GC 10.3 golden settings for `mmPA_SC_BINNER_TIMEOUT_COUNTER`, `mmPA_SC_ENHANCE_2`, `mmLDS_CONFIG`, `mmSQ_CONFIG`, `mmSPI_CONFIG_CNTL_1`, `mmDB_DEBUG3`, `mmDB_DEBUG4`, `mmDB_EXCEPTION_CONTROL`, `mmGB_ADDR_CONFIG`, and `mmCB_HW_CONTROL_4`, all of which depend on the register-field definitions remaining aligned with hardware.

## Register Families Covered

The PA/SC portion covers binner event, batching, clock-gating, FIFO, steering, and enhancement controls. It includes `PA_SC_BINNER_TIMEOUT_COUNTER`, `PA_SC_BINNER_PERF_CNTL_0..3`, `PA_SC_ENHANCE_2`, `PA_SC_BINNER_CNTL_OVERRIDE`, `PA_SC_PBB_OVERRIDE_FLAG`, `PA_PH_INTERFACE_FIFO_SIZE`, `PA_PH_ENHANCE`, `PA_SC_BC_WAVE_BREAK`, `PA_SC_ENHANCE_3`, `PA_SC_FIFO_SIZE`, `PA_SC_IF_FIFO_SIZE`, `PA_SC_PKR_WAVE_TABLE_CNTL`, `PA_SIDEBAND_REQUEST_DELAYS`, `PA_SC_ENHANCE`, `PA_SC_ENHANCE_1`, `PA_SC_DSM_CNTL`, and `PA_SC_TILE_STEERING_CREST_OVERRIDE`. These fields tune primitive batch breaking, persistent state thresholds, PBB behavior, SC/DB/BCI/SPI interface gating, FIFO depths, timeout thresholds, and tile steering override. In `gfx_v10_0.c`, GC 10.3 golden settings repeatedly program `mmPA_SC_BINNER_TIMEOUT_COUNTER` to `0x00000800` and `mmPA_SC_ENHANCE_2` with ASIC-specific masks/values, so drift in these definitions can surface as hangs or incorrect primitive binning behavior.

The `gc_sqdec` block maps shader core and shader-cache registers. It includes `SQ_CONFIG`, `SQC_CONFIG`, `LDS_CONFIG`, `SQ_RANDOM_WAVE_PRI`, `SQG_STATUS`, `SQ_FIFO_SIZES`, `SQ_DSM_CNTL`, `SQ_DSM_CNTL2`, `SQ_RUNTIME_CONFIG`, `SH_MEM_BASES`, `SP_CONFIG`, `SQ_ARB_CONFIG`, `SH_MEM_CONFIG`, shader trap addresses (`SQ_SHADER_TBA_*`, `SQ_SHADER_TMA_*`), SQC UTCL0 instruction/data cache control and status, `SQG_CONFIG`, shader-rate config, interrupt masking/message control, watchpoint registers `SQ_WATCH0..3`, SQ thread-trace buffer/mask/token/control/status/counter registers, indirect index/data access, `SQ_CMD`, time registers, load-balancer counters, EDC counters, and WREXEC address fields. These definitions back shader dispatch behavior, memory aperture defaults, per-VMID cache invalidation, thread trace capture, debugger watchpoints, and error-reporting controls.

The `gc_shsdec` block maps shader processor input/export controls. It includes `SX_DEBUG_1`, `SPI_PS_MAX_WAVE_ID`, `SPI_START_PHASE`, `SPI_GFX_CNTL`, `SPI_DSM_CNTL`, `SPI_DSM_CNTL2`, `SPI_EDC_CNT`, `SPI_USER_ACCUM_VMID_CNTL`, `SPI_CONFIG_CNTL`, `SPI_WAVE_LIMIT_CNTL`, `SPI_CONFIG_CNTL_2`, `SPI_CONFIG_CNTL_1`, `SPI_CONFIG_PS_CU_EN`, wavefront lifetime control/limit/status registers, SPI load-balancer counters, static WGP masks, `SPI_GDS_CREDITS`, SX export and scoreboard buffer sizes, CSQ wavefront active counters, per-WGP active wave counters, and trap screen base/mask/minimum GPR registers for pipes 0 and 1. `gfx_v10_0.c` programs `mmSPI_CONFIG_CNTL_1` and remaps `mmSPI_CONFIG_CNTL_REMAP` to the proper `mmSPI_CONFIG_CNTL` offset on some GC 10.3 ASICs, so these masks are part of the user-mode register-remap and golden-setting boundary.

The `gc_tpdec` block covers texture pipe status and diagnostics: `TD_STATUS`, `TD_DSM_CNTL`, `TD_DSM_CNTL2`, `TD_SCRATCH`, `TA_CNTL`, `TA_RESERVED_010C`, `TA_STATUS`, and `TA_SCRATCH`. Fields expose busy bits, FIFO empty/busy status, DSM single-write/error-injection controls, and TA/TD credit tuning. These are low-level debug and bring-up surfaces rather than normal filesystem or memory-management code paths.

The `gc_gdsdec` block covers global data share state. It includes `GDS_CONFIG`, `GDS_CNTL_STATUS`, `GDS_ENHANCE`, protection fault registers (`GDS_PROTECTION_FAULT`, `GDS_VM_PROTECTION_FAULT`), EDC counters, physical and pipe open-address counters, DSM controls, and `GDS_WD_GDS_CSB`. These fields are used for GDS/GWS/OA arbitration, VMID fault reporting, address/counter diagnostics, and EDC/FUE accounting. Any KFD or compute path that enables GDS/GWS/OA resources relies on these field meanings for fault attribution and debug visibility.

The `gc_rbdec` block covers depth-buffer, render-backend, graphics-block topology, and the beginning of color-buffer controls. It includes `DB_DEBUG`, `DB_DEBUG2`, `DB_DEBUG3`, `DB_DEBUG4`, multiple stutter controls, credit and watermark registers, subtile/cacheline/FIFO controls, burst/ring/RMI/cache/exception controls, DFSM configuration/status/watchdog/flush controls, DB fine-grain clock-gating SRAM/interface overrides, `CC_RB_REDUNDANCY`, `CC_RB_BACKEND_DISABLE`, `GB_ADDR_CONFIG`, `GB_BACKEND_MAP`, `GB_GPU_ID`, `CC_RB_DAISY_CHAIN`, `GB_ADDR_CONFIG_READ`, and the first `CB_HW_CONTROL_4` fields. This block is especially important because `GB_ADDR_CONFIG` fields are persisted into `adev->gfx.config` during early init and drive downstream tile-pipe, RB, SE, compressed-fragment, and pipe-interleave assumptions.

## Important APIs, Types, and Macros

This file defines no functions, structs, or runtime storage. Its API is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the right shift for a field within a 32-bit register value.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted 32-bit field mask.
- Register-group comments such as `// addressBlock: gc_sqdec` and `//GB_ADDR_CONFIG` provide the hardware grouping used by generated register headers and review tools.

The main external helper contract is that AMDGPU macros concatenate register and field names. For example, `REG_GET_FIELD(gb_addr_config, GB_ADDR_CONFIG, NUM_PKRS)` expands using `GB_ADDR_CONFIG__NUM_PKRS_MASK` and `GB_ADDR_CONFIG__NUM_PKRS__SHIFT`. `REG_SET_FIELD` and golden-setting macros use the same convention when constructing masked writes. This makes field-name stability an ABI-like source contract inside the driver: changing a macro spelling or numeric value breaks compile-time expansion or silently targets the wrong hardware bits.

## Control Flow

There is no executable control flow in this header. Control flow appears at the integration points:

- During GPU early init, `gfx_v10_0_gpu_early_init()` reads `mmGB_ADDR_CONFIG`, extracts fields via this register-field convention, and stores derived values in `adev->gfx.config`.
- During golden-register initialization, GC 10.3 tables in `gfx_v10_0.c` apply masked writes to many registers covered here. These writes happen as part of ASIC initialization and resume paths.
- During user-mode register remapping, `gfx_v10_0.c` writes `mmGRBM_CAM_DATA` entries so UMD-facing register aliases map to hardware registers such as `mmSPI_CONFIG_CNTL`; the field masks in this header document the target register layout.
- Diagnostic or debug paths can read status/fault/thread-trace/watchpoint fields after hardware events. The masks define how raw register dumps are decoded.

## State and Persistence

The macros themselves are compile-time constants and hold no state. The hardware registers they describe are volatile GPU state, usually reset or reprogrammed during GPU initialization, suspend/resume, and reset recovery.

Some decoded values become persistent driver state for the life of an initialized device. `GB_ADDR_CONFIG` is the clearest example: `gfx_v10_0_gpu_early_init()` saves the raw register value in `adev->gfx.config.gb_addr_config` and derives `num_pipes`, `max_tile_pipes`, `max_compress_frags`, `num_rb_per_se`, `num_se`, `pipe_interleave_size`, and, for GC 10.3, `num_pkrs`. Those values feed later memory-layout, tiling, and render-backend decisions. Incorrect masks here can persist as wrong topology even if the raw register read was correct.

Other fields describe diagnostic state that persists only until cleared or reset, such as SQ/GDS/DB EDC counters, GDS protection fault latches, thread-trace write pointers/status, SPI lifetime interrupt status, and DB DFSM watchdog/flush state. Golden-setting writes persist in hardware until overwritten, GPU reset, or power-management transitions reapply them.

## Dependencies and Integration Points

This chunk depends on the generated AMD ASIC register ecosystem:

- Matching offset headers provide `mm*` or `reg*` addresses for the same register names.
- `amdgpu` SOC15 register helpers perform raw MMIO reads/writes using those offsets.
- Register helper macros in the AMDGPU codebase compose the `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` names defined here.
- ASIC-specific code in `gfx_v10_0.c` chooses which golden-setting table applies to IP versions such as GC 10.3.0, 10.3.2, 10.3.3, 10.3.4, 10.3.5, 10.3.6, and 10.3.7.
- KFD/compute, debugfs, perf/trace, RAS/EDC, and GPU-reset tooling can indirectly depend on these bit layouts when they inspect shader, GDS, DB/RB, or thread-trace state.

Notable cross-block integration:

- `PA_SC_*`, `DB_*`, `CB_*`, and `GB_*` fields jointly affect graphics frontend/binning, depth/color backend, and render-backend topology.
- `SQ_*`, `SQC_*`, `SPI_*`, and `SX_*` fields jointly affect shader wave scheduling, cache behavior, thread trace, trap handling, and export buffering.
- `GDS_*` and `SPI_GDS_CREDITS` connect shader dispatch with shared data-store resource flow.
- `GB_ADDR_CONFIG` and `CC_RB_*` connect topology discovery with RB disable/redundancy and backend mapping.

## Risks

The main risk is silent hardware misprogramming. These are all numeric constants; a one-bit shift or mask error can compile cleanly but make the driver program the wrong feature, decode the wrong topology, or miss a fault/status bit.

High-risk fields in this chunk include `GB_ADDR_CONFIG` and `GB_ADDR_CONFIG_READ`, because they drive persistent topology in `adev->gfx.config`; `PA_SC_ENHANCE_2`, `LDS_CONFIG`, `SQ_CONFIG`, `SPI_CONFIG_CNTL_1`, `DB_DEBUG3`, `DB_DEBUG4`, `DB_EXCEPTION_CONTROL`, and `CB_HW_CONTROL_4`, because GC 10.3 golden settings write them during initialization; SQC UTCL0 invalidation fields, because cache-invalidation and VMID handling failures can cause stale instruction/data fetches; SQ thread trace and watchpoint fields, because debug tooling depends on precise buffer, VMID, and mask semantics; and GDS protection-fault fields, because fault attribution depends on correct VMID, address, CU/SIMD/wave, TMZ, GWS, and OA decoding.

The chunk also contains reserved, unused, and diagnostic/error-injection fields. Accidentally enabling DSM/error-injection bits or reserved clock-gating overrides can create hangs that are difficult to tie back to a header-only change. Conversely, overzealous cleanup of apparently unused fields can break out-of-tree tooling, register dump decoders, or future ASIC-specific workarounds.

Because this is generated source, hand edits are risky. Regeneration from the authoritative AMD register database should preserve ordering, names, and values; if manual patches are unavoidable, they should be reviewed against the matching offset header and hardware documentation.

## Test Signals

Useful compile-time signals are straightforward: AMDGPU builds must continue to compile anywhere `REG_GET_FIELD`, `REG_SET_FIELD`, or golden settings reference these names. Missing or renamed macros fail at compile time.

Runtime validation needs hardware or register-emulation coverage. Strong signals include successful boot/probe of GC 10.3 ASICs, correct `adev->gfx.config` topology values from `GB_ADDR_CONFIG`, no regressions in GPU reset and suspend/resume, no graphics or compute hangs during golden-register application, and stable rendering/compute under workloads that stress binning, DB/CB paths, shader waves, and GDS.

Debug and diagnostic signals include sane register dumps for `SQ_THREAD_TRACE_*`, working SQ watchpoints/thread trace, expected EDC/fault counter behavior, correct GDS protection-fault attribution, and no unexpected DB DFSM watchdog or exception-control events. For changes near `CB_HW_CONTROL_4`, render correctness and cache/scoreboard behavior under color/depth-heavy workloads are important. For changes near cache invalidation fields, VM and shader-cache stress tests should show no stale-data or stale-instruction symptoms.

### subset-b-002480: lines 10058-12395

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 10058-12395

## Chunk Scope

This chunk is part of AMD's generated GC 10.3.0 register shift/mask header. It contains C preprocessor constants only: register-field `__SHIFT` macros and matching `_MASK` macros. There are no functions, structs, enums, executable statements, or kernel-owned storage declarations.

The range starts at the tail of `CB_HW_CONTROL_4`, containing only the last five mask macros for that register, then covers full field definitions for color-buffer controls, GCEA/RMI/GCR/UTCL1 control/status blocks, GCVM L2 and fault registers, and GCVM context-control registers from context 0 through most of context 15. The final line is `GCVM_CONTEXT15_CNTL__VALID_PROTECTION_FAULT_ENABLE_INTERRUPT_MASK`; the remaining context 15 masks appear in the next chunk.

## Purpose

The macros define bit positions and masks for GC 10.3.0 register fields used by AMDGPU graphics, memory-management, KFD, SDMA, and power-management code. The matching `gc_10_3_0_offset.h` file supplies `mm...` register offsets; this header supplies the field layout inside each register. Driver code combines them through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, `RREG32_SOC15`, and `WREG32_SOC15`.

The hardware areas represented here are:

- Color buffer (`CB_*`) tuning: cache fetch depths, quad scoreboard behavior, clock gating disables, blend and DCC/CMASK/FMASK optimization controls, FIFO/tag depths, DCC overwrite-combiner controls, and CB memory-arbiter read/write weighting.
- GCEA blocks: fabric/cache arbitration, early write return, data-store memory test/error-injection controls, GL2C crossbar credits/burst limits, probe mapping, error status, request blocking, and RRET memory reservation.
- SPI throttling: PQ event control and exponential throttle controls.
- RMI blocks: request-interface burst/VMID/xbar controls, status counters, subblock FIFO/inflight status, xbar arbitration, UTCL1/XNACK behavior, demux controls, scoreboard flush/status controls, clock control, RB/GLX CID map, redundancy, and spare/debug registers.
- GCR/PMM/UTCL1 blocks: GCR request control, command/status, PIO access, page-size/cache bypass controls, invalidation force/done bits, fragment-size overrides, status, and targets disable fields.
- GCVM L2 and context blocks: L2 cache controls, invalidation controls, fault handling/default-page registers, identity aperture and physical offset registers, MM group routing class fields, reserved CID bank selection, parity controls, GCR linkage, walker throttles, PTE cache dump controls, and per-VM context fault policy.

## Important APIs, Types, and Macros

There are no callable APIs. The exported interface is the macro namespace:

- `CB_HW_CONTROL_4`, `CB_HW_CONTROL_3`, `CB_HW_CONTROL`, `CB_HW_CONTROL_1`, `CB_HW_CONTROL_2`, `CB_DCC_CONFIG`, `CB_HW_MEM_ARBITER_RD`, and `CB_HW_MEM_ARBITER_WR` define color-buffer cache, compression, blend, clock-gating, FIFO-depth, and memory arbitration fields. These are sensitive performance/errata controls; many fields are named as disables or chicken bits.
- `GCEA_MISC`, `GCEA_LATENCY_SAMPLING`, `GCEA_DSM_CNTL*`, `GCEA_GL2C_XBR_*`, `GCEA_PROBE_*`, `GCEA_ERR_STATUS`, `GCEA_MISC2`, and `GCEA_RRET_MEM_RESERVE` define graphics cache/external-agent traffic policy, sampling, test/error injection, crossbar crediting, probe routing, and error-reporting fields.
- `SPI_PQEV_CTRL` and `SPI_EXP_THROTTLE_CTRL` define shader processor throttle enable, periods, up/down steps, stall thresholds, and reset fields.
- `RMI_GENERAL_CNTL*`, `RMI_GENERAL_STATUS`, `RMI_SUBBLOCK_STATUS*`, `RMI_XBAR_CONFIG`, `RMI_XBAR_ARBITER_CONFIG*`, `RMI_PROBE_POP_LOGIC_CNTL`, `RMI_UTC_XNACK_N_MISC_CNTL`, `RMI_DEMUX_CNTL`, `RMI_UTCL1_CNTL*`, `RMI_UTC_UNIT_CONFIG`, `RMI_TCIW_FORMATTER*`, `RMI_SCOREBOARD_CNTL`, `RMI_SCOREBOARD_STATUS*`, `RMI_CLOCK_CNTRL`, `RMI_UTCL1_STATUS`, `RMI_RB_GLX_CID_MAP`, `RMI_SPARE*`, `CC_RMI_REDUNDANCY`, and `GC_USER_RMI_REDUNDANCY` cover request-interface routing, arbitration, flush, retry, PRT/XNACK, CID, status, and redundancy fields.
- `GCR_GENERAL_CNTL`, `GCR_CMD_STATUS`, `GCR_SPARE`, `PMM_GENERAL_CNTL`, `GCR_PIO_CNTL`, and `GCR_PIO_DATA` define graphics-cache request controls, PIO transactions, command status, and spare/test controls.
- `UTCL1_CTRL`, `UTCL1_ALOG`, `UTCL1_UTCL0_INVREQ_DISABLE`, `GCRD_SA_TARGETS_DISABLE`, and `UTCL1_STATUS` define UTCL1 page-size controls, bypasses, invalidation force/done/status fields, adaptive log fields, and target-disable controls.
- `GCVM_L2_CNTL`, `GCVM_L2_CNTL2`, `GCVM_L2_CNTL3`, `GCVM_L2_CNTL4`, `GCVM_L2_CNTL5`, `GCVM_L2_STATUS`, `GCVM_INVALIDATE_CNTL`, `GCVM_DUMMY_PAGE_FAULT_*`, `GCVM_L2_PROTECTION_FAULT_*`, `GCVM_L2_CONTEXT1_IDENTITY_APERTURE_*`, `GCVM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET_*`, `GCVM_L2_MM_GROUP_RT_CLASSES`, `GCVM_L2_BANK_SELECT_RESERVED_CID*`, `GCVM_L2_CACHE_PARITY_CNTL`, `GCVM_L2_GCR_CNTL`, `GCVML2_WALKER_*`, and `GCVM_L2_PTE_CACHE_DUMP_*` define the graphics VM L2 cache, invalidation, page-fault/default-address, identity mapping, routing, parity, GCR, walker throttle, and diagnostic cache-dump fields.
- `GCVM_CONTEXT0_CNTL` through the chunk-local part of `GCVM_CONTEXT15_CNTL` define repeated per-VM context policy fields: context enable, page-table depth, block size, retry behavior, and interrupt/default-page behavior for range, dummy-page, PDE0, valid, read, write, and execute protection faults.

The macro naming convention is important for generated helper use: `REG_SET_FIELD(reg, REGISTER, FIELD, value)` expects `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` to exist. A missing or renamed macro breaks those helper expansions at compile time.

## Control Flow

This file has no software control flow. The behavioral flow appears in consumers that program hardware registers:

- `gfxhub_v2_1.c` includes `gc_10_3_0_offset.h`, `gc_10_3_0_sh_mask.h`, and `gc_10_3_0_default.h`; it programs GCVM invalidation requests, prints L2 protection fault status with `REG_GET_FIELD`, initializes cache/TLB state, toggles GCVM L2 fault default-page behavior, and installs VM context fault-interrupt masks.
- VM invalidation requests are built by setting invalidation and flush fields, then written to GCVM invalidate-engine registers outside this chunk. The `GCVM_INVALIDATE_CNTL` fields in this chunk configure global invalidation queue behavior, while request/ack fields live elsewhere in the same generated header family.
- Fault-handling flow uses `GCVM_L2_PROTECTION_FAULT_STATUS` to decode faults, `GCVM_L2_PROTECTION_FAULT_CNTL` to decide whether faults redirect to a default page or crash, and per-context `GCVM_CONTEXTn_CNTL` bits to enable interrupt reporting and default handling for individual fault classes.
- Cache/TLB setup sequences write `GCVM_CONTEXT0_CNTL` plus offsets for all 16 contexts to disable or reprogram contexts, then configure L2 cache behavior through `GCVM_L2_CNTL*`.
- RMI and UTCL1 fields describe hardware handshakes and queues around retries, flushes, invalidations, XNACK, PRT, and scoreboard completion. Sequencing and polling requirements live in the code using these registers or in hardware programming tables, not in this generated header.

## State and Persistence

The state represented by these macros lives in GC hardware registers. The header itself persists nothing and allocates no memory. Register values persist according to hardware lifetime: until explicitly rewritten, reset by the relevant GC/GMC block, power-gated, restored after suspend, or reset with the ASIC.

Important state categories include:

- Render/backend state: CB cache depths, compression controls, blend optimization toggles, arbiter weights, stutter thresholds, and RB/RMI redundancy settings.
- Fabric/request state: GCEA arbitration, RMI xbar and demux modes, FIFO/inflight status, scoreboard flush state, CID maps, RRET reservations, and request-blocking/error state.
- Translation/cache state: UTCL1 page size and bypass controls, L1/L2 invalidation state, L2 cache mode, PTE/PDE cache behavior, bank-selection reserved CIDs, parity controls, and walker throttle settings.
- Fault state: dummy-page/default fault addresses, protection fault status/address registers, fault clearing controls, crash-on-fault policy, no-retry client interrupts, and per-context fault interrupt/default bits.
- Diagnostic/test state: GCEA DSM error-injection bits, probe routing, SPI throttle counters, RMI/GCR spare bits, GCR PIO access, and GCVM PTE cache dump controls.

`gfxhub_v2_1_save_regs()` and `gfxhub_v2_1_restore_regs()` explicitly save and restore many GCVM L2 and context registers named in this chunk into `adev->gmc` fields. That makes these register values part of driver-managed GPU power-management and reset recovery state, even though the generated header itself has no persistence logic.

## Dependencies and Integration Points

Direct GC 10.3.0 include sites in this tree are:

- `drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c`, the main semantic consumer for the GCVM L2/context/fault macros in this chunk.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c`, which bridges GFX 10.3 hardware programming to KFD.
- `drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c` and `drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.c`, which include the generated GC 10.3 masks for SDMA-related register work.
- `drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`, which includes the same offset and mask pair for Vangogh SMU power-management programming.

This chunk depends on:

- `gc_10_3_0_offset.h` for register offsets such as `mmCB_HW_CONTROL_4` at `0x1422`, `mmCB_HW_CONTROL_3` at `0x1423`, `mmCB_HW_CONTROL` at `0x1424`, `mmCB_DCC_CONFIG` at `0x1427`, `mmGCEA_MISC` at `0x14a2`, `mmRMI_GENERAL_CNTL` at `0x1520`, and the GCVM L2/context offset family used by `gfxhub_v2_1.c`.
- `gc_10_3_0_default.h` for hardware reset/default values used alongside these masks.
- AMD SOC15 register access helpers and field helpers (`SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `WREG32_FIELD15`, `REG_SET_FIELD`, `REG_GET_FIELD`).
- Core AMDGPU VM/GMC structures that store VM hub offsets, context distances, fault masks, and saved GCVM register values.
- Hardware generator inputs for GC 10.3.0. Legal values, timing delays, register access restrictions, and ordering constraints are not encoded by these macros.

## Risks and Maintenance Notes

- This is generated hardware ABI. A one-bit shift or mask error can alter MMU fault policy, cache invalidation, render backend behavior, arbitration, or diagnostic/test paths.
- The range has split register definitions at both boundaries. `CB_HW_CONTROL_4` starts before this chunk, and `GCVM_CONTEXT15_CNTL` completes after it. Merge/reconciliation should combine adjacent chunk notes before treating either register as fully described.
- Many fields are named as disables, overrides, chicken bits, or error-injection controls. Accidentally enabling a disable bit or writing test fields outside intended flows can cause performance regressions, hangs, silent corruption, or spurious faults.
- Context-control macros are repeated for 16 VM contexts with identical field layouts. Copy/paste or offset-distance mistakes can program the wrong VMID context and affect unrelated processes or queues.
- Fault policy fields have high impact: switching between interrupt, retry, default-page, and crash behavior changes whether GPUVM errors are recoverable, logged, hidden by a dummy page, or escalated.
- RMI/UTCL1 invalidation, retry, and scoreboard fields interact with in-flight memory transactions. Writes likely require quiescent hardware, polling, or ordered flushes supplied by higher-level code.
- Reserved/spare fields are present throughout the chunk. Whole-register writes should preserve unknown bits unless generated defaults or hardware documentation explicitly requires them.
- SR-IOV access restrictions matter. `gfxhub_v2_1_set_fault_enable_default()` skips some GCVM L2 programming for VFs because the PF owns those registers.

## Test Signals

Useful validation for changes touching this area includes:

- Build coverage for all direct include paths: `gfxhub_v2_1.c`, KFD GFX 10.3, SDMA 5.2, shared SDMA, and Vangogh SMU.
- Static consistency checks that every `REGISTER__FIELD__SHIFT` in this range has a matching `REGISTER__FIELD_MASK` in the correct chunk after boundary reconciliation, and that corresponding `mmREGISTER` offsets exist in `gc_10_3_0_offset.h`.
- Cross-generation diffs against nearby GC headers such as `gc_10_1_0_sh_mask.h`, `gc_10_3_1_sh_mask.h`, or later GCVM/GFX hub headers to distinguish intentional generated deltas from accidental drift.
- GPUVM runtime tests: VM context creation/destruction, page-table updates, invalidation stress, eviction/migration paths, userptr/BO fault behavior, no-retry fault logging, and recovery after retry/default-page faults.
- Suspend/resume, BACO, reset, and SR-IOV VF/PF tests that exercise `gfxhub_v2_1_save_regs()` and `gfxhub_v2_1_restore_regs()` for the GCVM L2/context registers.
- Render and compute smoke tests on affected GC 10.3 ASICs to catch CB/RMI/UTCL1 regressions: modeset-independent graphics workloads, KFD queues, SDMA copies, memory pressure, GPU fault injection where available, and performance-counter sanity for arbitration/throttle changes.

### subset-b-002481: lines 12396-14895

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 12396-14895

## Purpose

This chunk is generated AMD GC 10.3.0 register bitfield metadata. It contains no executable C code; it publishes preprocessor `__SHIFT` and `_MASK` constants used by AMDGPU and AMDKFD code to compose and decode 32-bit MMIO register values. The matching register addresses and base indices live in `gc_10_3_0_offset.h`.

The selected range starts at the end of `GCVM_CONTEXT15_CNTL`, covers GCVM context disable, GCVM invalidate engines, VM aperture/location controls, GCEA memory and IO arbitration controls, TCP invalidate/status fields, and begins the shader program register definitions for pixel and vertex stages. Although this repository subtree is named `ceph-client`, this file is GPU driver hardware metadata, not filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocations, locks, or callbacks in this range. The exposed API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the in-register bit mask for the same field.
- Consumers pair these constants with `mm<REGISTER>` and `mm<REGISTER>_BASE_IDX` macros from `gc_10_3_0_offset.h`, then use AMDGPU helper patterns such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`.

Major register groups in this chunk:

- GCVM context controls: the chunk begins with `GCVM_CONTEXT15_CNTL` protection-fault enable/default masks, then defines `GCVM_CONTEXTS_DISABLE` bits for disabling VM contexts 0 through 15.
- GCVM invalidate engines 0 through 17: each engine has a `*_SEM` semaphore bit, `*_REQ` fields for per-VMID invalidation, flush type, L2 PTE/PDE0/PDE1/PDE2 invalidation, L1 PTE invalidation, protection-fault status-address clear, request logging, and 4K-only invalidation, plus `*_ACK` acknowledgement status and `*_ADDR_RANGE_LO32/HI32` physical address range fields. `gfxhub_v2_0.c` and `gfxhub_v2_1.c` use the engine 0 request masks via `REG_SET_FIELD` and derive engine spacing from the adjacent offset macros.
- GCVM page-table base and range registers: contexts 0 through 15 expose low/high 32-bit page-table base, start, and end address fields. These describe VM context page-table placement and logical address bounds but do not implement the page-table programming sequence.
- Per-PF/VF PTE cache fragment sizing: `GCVM_L2_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` and context 0 through 15 variants define small-page fragment size, large-page fragment size, and bank select fields used by the GCVM L2 PTE cache path.
- Shared GCVM PF decode controls: `GCMC_VM_NB_MMIOBASE`, `GCMC_VM_NB_MMIOLIMIT`, `GCMC_VM_NB_PCI_CTRL`, PCI arbitration, top-of-DRAM registers, framebuffer offset, system aperture default address, VM steering, virtual reset request/status fields, memory power light sleep, cacheable DRAM ranges, APT control, local HBM aperture lock/start/end, active function ID, XGMI LFB control/size, framebuffer no-allocate controls, and `GCUTCL2_HARVEST_BYPASS_GROUPS`.
- Shared GCVM VC decode controls: framebuffer location base/top, AGP top/bottom/base, system aperture low/high logical addresses, and `GCMC_VM_MX_L1_TLB_CNTL` fields such as L1 TLB enable, system access mode, unmapped access behavior, advanced driver model enable, ECO bits, and memory type.
- GCEA arbitration controls: DRAM and IO read/write client-to-group maps assign client IDs 0 through 31 to four groups; group-to-VC maps assign groups to virtual channels; lazy, CAM, burst, age, queueing, fixed-priority, urgency, urgency-mask, and quantization registers tune read/write arbitration for DRAM and IO traffic.
- TCP and TCI controls: `TCP_INVALIDATE` exposes a start bit, `TCP_STATUS` reports pending/stalled/invalidate and UTCL1 request state, `TCP_EDC_CNT` reports parity/EDC counts, `TCI_STATUS` exposes VM/TLB status, and `TCI_CNTL_1/2` publish control fields for the texture cache interface.
- Pixel shader program setup: `SPI_SHADER_PGM_RSRC4_PS`, checksum, `RSRC3`, program low/high address, `RSRC1`, `RSRC2`, 32 user data registers, request-control fields, and four user accumulation contribution fields. Important resource fields include VGPR/SGPR counts, priority, float mode, privilege, DX10 clamp, IEEE mode, VGPR component count, CU group enable, memory ordered and forward progress bits, FP16 overflow behavior, scratch enable, user SGPR count, trap presence, LDS and stream-output enables, exception enable mask, PC base enable, dispatch/draw enable, and shared VGPR count.
- Vertex shader program setup: equivalent VS program resource, checksum, late allocation, address, `RSRC1/RSRC2`, and user data registers 0 through 30 within this chunk. The next chunk continues with `SPI_SHADER_USER_DATA_VS_31` and `SPI_SHADER_REQ_CTRL_VS`.

Many full-register data fields use `0xFFFFFFFFL` masks, especially address/data and shader user-data registers. Field names are descriptive, but access permissions and programming sequences are not encoded in this header.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU and AMDKFD consumers:

1. GFX10.3 code includes `gc_10_3_0_offset.h` and `gc_10_3_0_sh_mask.h`.
2. Driver paths select a concrete register using the `mm*` offset macro and base index.
3. The code composes or extracts fields using the shift and mask macros from this header.
4. MMIO helper calls read or write the register while higher-level VM, cache, shader, reset, power, or firmware paths provide ordering and synchronization.

The GCVM invalidate fields are a good example: the header only defines bits. `gfxhub_v2_0.c`/`gfxhub_v2_1.c` build a request with `PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, and L1/L2 invalidation bits, program optional address ranges, write invalidate request registers, and poll acknowledgement through hub structures that use the register offsets. The header does not encode semaphore acquisition, acknowledgement polling, timeout policy, VMID ownership, or fault logging decisions.

Shader program resource fields are similarly declarative. The chunk defines how PS and VS resource registers are packed, but command submission, pipeline state assembly, shader upload, trap/debug setup, scratch allocation, stream-output configuration, and wave scheduling rules live in the driver, firmware, and hardware programming model.

## State And Persistence Behavior

This file stores no software state and persists nothing. It describes hardware state exposed through GC 10.3 registers.

The represented hardware state includes VM context enable/disable bits, per-engine TLB/cache invalidation request and acknowledgement state, invalidate address ranges, page-table base/start/end addresses for contexts 0 through 15, PTE cache fragment sizing, PCI/MMIO/DRAM/framebuffer/aperture/TLB configuration, virtual reset and active-function state, GCEA client grouping and arbitration policy, TCP/TCI invalidate and status state, and PS/VS shader program configuration.

Persistence is hardware-defined. Some fields are durable configuration until GPU reset, suspend/resume, power-gating, VF reset, or explicit reprogramming. Others are live status bits, write-triggered strobes, self-clearing request bits, hardware-owned counters/status, or address/data payload registers. The macros do not identify read-only, write-only, write-one-to-clear, sticky, latched, protected, or reserved behavior, so consumers must rely on the ASIC programming guide and preserve unrelated bits when updating mixed-control registers.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h`, which provides the corresponding MMIO offsets and base indices. Enum/default/generated headers such as AMD ASIC enum files provide values for fields where a mask alone is not enough.

Known direct include users of this GC 10.3.0 shift/mask header include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`

The same field names are also used by common GFX hub code patterns in nearby IP versions, especially for `GCVM_INVALIDATE_ENG0_REQ`, address-range programming, semaphore/request/ack register offsets, and engine-distance calculations. Integration points include GPU VM setup, page-table aperture programming, TLB and PTE-cache invalidation, memory partitioning and virtualization, PCI/MMIO aperture setup, XGMI/local framebuffer handling, reset and power management, cache invalidation, shader stage programming, KFD queue setup, and profiling/debug paths that read status or program shader resources.

## Risks And Edge Cases

- Header/offset mismatch is the primary correctness risk. Pairing `gc_10_3_0_sh_mask.h` with a different GC offset header can compile while programming the wrong register or field.
- The macros are untyped constants. A wrong register name or stale mask can silently affect the wrong VMID, invalidate engine, context, aperture, GCEA client group, priority coefficient, texture cache control, or shader resource field.
- GCVM invalidation is sequencing-sensitive. Semaphore ownership, request construction, optional address range setup, VMID masks, flush type, L1/L2/PDE selections, acknowledgement polling, timeout handling, and fault-status clearing must be coordinated by consumers.
- Context and aperture registers are security- and isolation-sensitive. Incorrect base/start/end addresses, AGP/framebuffer/system aperture bounds, active function IDs, VF reset controls, or PF/VF cache fragment settings can cause VM faults, memory exposure across processes or VFs, or GPU hangs.
- Several register families are replicated by context or invalidate engine. Code that assumes wrong spacing between engine or context registers can pass static compilation but program a neighboring engine/context at runtime.
- GCEA arbitration knobs can create performance cliffs or starvation. Client-to-group, group-to-VC, age, urgency, queueing, burst, and masking fields need ASIC-specific defaults and workload validation; small bitfield mistakes may appear only as bandwidth or latency regressions.
- Full-width masks do not imply safe writes. Address payloads, user-data registers, status fields, and hardware-owned state can all expose `0xFFFFFFFFL`; access semantics still come from the hardware spec and call site.
- Shader `RSRC1/RSRC2` fields interact with compiler output and queue state. Incorrect VGPR/SGPR counts, scratch enable, user SGPR count, trap, exception, stream-output, PC base, shared VGPR, or forward-progress fields can produce invalid waves, bad memory accesses, missed traps, or hard-to-debug rendering and compute failures.
- The chunk boundary is artificial. It starts after part of `GCVM_CONTEXT15_CNTL` and ends at `SPI_SHADER_USER_DATA_VS_30`; adjacent chunks are needed for the complete context-control and VS request-control view.

## Test Signals

Useful validation is mostly build, static, and hardware coverage:

- Build coverage for AMDGPU, AMDKFD, SDMA, GFX hub, and SMU files that include the GC 10.3.0 shift/mask header with `gc_10_3_0_offset.h`.
- Generated-header checks that every `__SHIFT` has a matching `_MASK`, masks are aligned to their shifts, replicated engine/context/register families have consistent spacing and field layouts, and register names match entries in the offset header.
- Static checks for non-overlapping fields within each register except documented aliases or full-width data/status fields.
- VM stress tests that create and destroy many GPUVM mappings, update page tables, trigger per-VMID invalidations, use address-range invalidation, and verify acknowledgement polling and timeout behavior.
- Fault-path tests for valid/read/write/execute/range/dummy/PDE protection faults, including logging and fault-status-address clearing where supported.
- Reset, suspend/resume, runtime power-management, and SR-IOV/PF/VF tests that verify context, aperture, cache fragment, active-function, and virtual reset state is restored or reinitialized correctly.
- Memory aperture tests covering framebuffer, AGP, system aperture, cacheable DRAM, local HBM, XGMI LFB, and no-allocate settings, with attention to VM faults and cross-process or cross-VF isolation.
- GCEA bandwidth/latency tests using DRAM and IO read/write workloads to catch client mapping, priority, urgency, burst, or masking field regressions.
- TCP/TCI cache invalidation smoke tests that write the `TCP_INVALIDATE` start bit, poll relevant status, and run texture/cache-heavy workloads after invalidation.
- Graphics and compute shader tests that exercise PS/VS resource programming across VGPR/SGPR pressure, scratch use, traps/exceptions, stream output, user SGPR/user-data registers, shared VGPR count, and forward progress; regression signals include zero or corrupted output, VM faults, hangs, missed traps, or failures isolated to GFX10.3 ASICs.

### subset-b-002482: lines 14896-17371

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 14896-17371

## Scope

This chunk is a generated AMD GC 10.3.0 shift/mask register-header slice. It contains only C preprocessor `#define` constants for register bit positions and masks. There are no functions, structs, enums, global variables, allocations, locks, direct MMIO operations, or executable branches in this range.

The requested lines contain 2,151 `#define` statements: 1,076 `__SHIFT` macros and 1,075 `_MASK` macros. The range starts in the middle of the `SPI_SHADER_USER_DATA_VS_30` group, covers shader-stage programming for VS/GS/ES/HS/LS, compute dispatch and compute resource registers, then enters the `gc_cppdec` command-processor address block. It ends in the middle of `CP_SUSPEND_RESUME_REQ`, after the `SUSPEND_REQ` mask and before the `RESUME_REQ` mask in the next chunk.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU DRM hardware metadata and is unrelated to Ceph filesystem behavior.

## Purpose

`gc_10_3_0_sh_mask.h` describes the bit layout of registers for AMD graphics core 10.3.0. Driver code pairs these field macros with register offsets from `gc_10_3_0_offset.h` and uses AMDGPU helper macros to build, update, and decode 32-bit hardware register values without open-coded bit numbers.

This chunk covers three major surfaces:

- Shader processor interface state for graphics pipeline shader stages. It defines user-data payload registers, shader program base registers, shader program resource fields, request allocation controls, shader checksums, and per-stage user accumulator fields for VS, GS, ESGS, HS, LSHS, and LS related paths.
- Compute dispatch state. It defines compute dispatch initiation bits, dispatch dimensions and starts, per-axis full/partial thread counts, program and packet addresses, scratch-base addresses, compute program resources, VMID, CU destination masks, static thread management per shader engine, temp-ring sizing, restart coordinates, thread tracing, request controls, dispatch IDs, wave restore/relaunch fields, and compute user-data payloads.
- Command processor and CPC state in the `gc_cppdec` address block. It defines ring-buffer bases and controls, read/write pointer fields, doorbell ranges, queue/pipe priorities, interrupt controls and statuses, UTCL1 controls and errors, graphics error surfaces, fatal/ECC/EDC status, CP power and memory sleep controls, VMID reset/preempt/status fields, and early suspend/context-save controls.

## Important APIs, Types, And Macros

The only interface in this chunk is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field's in-register bit mask.
- `//<REGISTER>` comments mark generated register boundaries.
- `// addressBlock: gc_cppdec` marks the transition into command processor/CPC register definitions.

There are no callable APIs or C types here. Consumers typically use these constants through AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, and queue/debug/power-management code that token-pastes register and field names.

Important shader-stage families in this chunk include:

- `SPI_SHADER_USER_DATA_VS_30` and `SPI_SHADER_USER_DATA_VS_31`, followed by `SPI_SHADER_USER_DATA_GS_0..31` and `SPI_SHADER_USER_DATA_HS_0..31`. These expose full 32-bit `DATA` payload fields used as user SGPR inputs to shader stages.
- `SPI_SHADER_REQ_CTRL_VS`, `SPI_SHADER_REQ_CTRL_ESGS`, and `SPI_SHADER_REQ_CTRL_LSHS`. These share allocation-control fields such as `SOFT_GROUPING_EN`, `NUMBER_OF_REQUESTS_PER_CU`, allocation timeout, hard-lock threshold/hysteresis, producer request lockout, global scanning enable, and allocation-rate throttling threshold.
- `SPI_SHADER_USER_ACCUM_VS_0..3`, `SPI_SHADER_USER_ACCUM_ESGS_0..3`, and `SPI_SHADER_USER_ACCUM_LSHS_0..3`. Each exposes a small `CONTRIBUTION` field for accumulated user-data contribution accounting.
- `SPI_SHADER_PGM_LO_*` and `SPI_SHADER_PGM_HI_*` registers for ES_GS, GS, LS_HS, HS, ES, and LS program base addresses. Low halves are full-width; high halves in this chunk use low 8-bit `MEM_BASE` fields.
- `SPI_SHADER_PGM_RSRC1_GS` and `SPI_SHADER_PGM_RSRC1_HS`. These define shader resource metadata including `VGPRS`, `SGPRS`, `PRIORITY`, `FLOAT_MODE`, privilege, DX10 clamp, IEEE mode, CU grouping, memory ordering, forward progress, WGP mode, stage-specific VGPR component count, and FP16 overflow behavior.
- `SPI_SHADER_PGM_RSRC2_GS_VS`, `SPI_SHADER_PGM_RSRC2_GS`, and `SPI_SHADER_PGM_RSRC2_HS`. These cover scratch enable, user SGPR count, trap presence, exception enables, LDS sizing, VGPR component count, off-chip LDS, user SGPR MSB/skip behavior, and shared VGPR count.
- `SPI_SHADER_PGM_RSRC3_GS`, `SPI_SHADER_PGM_RSRC3_HS`, `SPI_SHADER_PGM_RSRC4_GS`, and `SPI_SHADER_PGM_RSRC4_HS`. These define CU enable masks, wave limits, lock thresholds, group FIFO depth, and late allocation fields.
- `SPI_SHADER_PGM_CHKSUM_GS` and `SPI_SHADER_PGM_CHKSUM_HS` expose full-width shader checksum fields.

Important compute families include:

- `COMPUTE_DISPATCH_INITIATOR` with dispatch enable and mode bits including partial thread-group enable, ordered append controls, thread-dimension usage, ordering mode, scalar/vector L1 invalidation, tunnel enable, restore, and wave32 enable (`CS_W32_EN`).
- `COMPUTE_DIM_X/Y/Z`, `COMPUTE_START_X/Y/Z`, `COMPUTE_RESTART_X/Y/Z`, `COMPUTE_DISPATCH_ID`, and `COMPUTE_THREADGROUP_ID`, all full-width coordinate or identity fields.
- `COMPUTE_NUM_THREAD_X/Y/Z`, each splitting full and partial thread counts into low and high 16-bit halves.
- `COMPUTE_PGM_LO/HI`, `COMPUTE_DISPATCH_PKT_ADDR_LO/HI`, and `COMPUTE_DISPATCH_SCRATCH_BASE_LO/HI`, which describe shader, packet, and scratch address fields.
- `COMPUTE_PGM_RSRC1`, `COMPUTE_PGM_RSRC2`, and `COMPUTE_PGM_RSRC3`, which define compute shader VGPR/SGPR allocation, priority, float mode, privilege, clamp/IEEE flags, bulky and FP16 behavior, WGP mode, memory ordering, forward progress, scratch, trap, TGID/TG-size enables, thread ID component count, LDS size, exception enables, and shared VGPR count.
- `COMPUTE_RESOURCE_LIMITS`, `COMPUTE_DESTINATION_EN_SE0..3`, and `COMPUTE_STATIC_THREAD_MGMT_SE0..3`, which gate work distribution across shader engines, shader arrays, CUs, waves, and thread groups.
- `COMPUTE_TMPRING_SIZE`, `COMPUTE_REQ_CTRL`, `COMPUTE_USER_ACCUM_0..3`, `COMPUTE_DDID_INDEX`, `COMPUTE_SHADER_CHKSUM`, `COMPUTE_RELAUNCH`, `COMPUTE_RELAUNCH2`, `COMPUTE_WAVE_RESTORE_ADDR_LO/HI`, `COMPUTE_USER_DATA_0..15`, `COMPUTE_DISPATCH_TUNNEL`, `COMPUTE_DISPATCH_END`, and `COMPUTE_NOWHERE`.

Important command-processor families include:

- CP/CPC timing and virtualization: `CP_EOPQ_WAIT_TIME`, `CP_CPC_MGCG_SYNC_CNTL`, `CP_VIRT_STATUS`, `CP_DEVICE_ID`, `CP_PROCESS_QUANTUM`, `CP_CONTEXT_CNTL`, `CP_MAX_CONTEXT`, and instruction-queue wait timers `CP_IQ_WAIT_TIME1/2`.
- Interrupt metadata and error reporting: `CPC_INT_INFO`, `CPC_INT_ADDR`, `CPC_INT_PASID`, `CP_GFX_ERROR`, `CP_FATAL_ERROR`, `CP_INT_CNTL`, `CP_INT_STATUS`, `CP_INT_CNTL_RING0..2`, `CP_INT_STATUS_RING0..2`, `CPC_INT_CNTL`, `CPC_INT_STATUS`, `CPC_INT_CNTX_ID`, and F32 interrupt sources/disables for ME, PFP, CE, MEC1, and MEC2.
- UTCL1 translation/cache controls and errors: `CPG_UTCL1_CNTL`, `CPC_UTCL1_CNTL`, `CPF_UTCL1_CNTL`, `CPG_UTCL1_ERROR`, and `CPC_UTCL1_ERROR`. These include XNACK redo timers, VMID reset mode, drop/invalidate/fragment-limit modes, force snoop, MTYPE no-PTE mode, force no-execute, permission-fault and TLB-miss flags.
- Ring-buffer and doorbell state: `CP_RB0_BASE`, `CP_RB_BASE`, `CP_RB1_BASE`, `CP_RB2_BASE`, their high-base registers, `CP_RB0_CNTL`, `CP_RB_CNTL`, `CP_RB1_CNTL`, `CP_RB2_CNTL`, `CP_RB_RPTR_WR`, read-pointer writeback addresses, `CP_RB*_BUFSZ_MASK`, `CP_RB*_WPTR`, `CP_RB*_WPTR_HI`, `CP_RB_VMID`, `CP_RB_DOORBELL_RANGE_*`, `CP_MEC_DOORBELL_RANGE_*`, and `CP_PQ_STATUS`.
- Scheduling and priority state: `CP_ME0/ME1/ME2_PIPE_PRIORITY_CNTS`, `CP_RING_PRIORITY_CNTS`, per-pipe priorities for ME0/ME1/ME2, ring priorities, `CP_GFX_QUEUE_INDEX`, and program-counter/interrupt-routine start registers for CE, PFP, ME, MEC1, and MEC2.
- Reliability and power state: `CP_PWR_CNTL`, `CP_MEM_SLP_CNTL`, `CP_ECC_FIRSTOCCURRENCE`, obsolete ring-specific first occurrence registers, `GB_EDC_MODE`, `CC_GC_EDC_CONFIG`, `CP_PQ_WPTR_POLL_CNTL`, and `CP_PQ_WPTR_POLL_CNTL1`.
- VM, preemption, and suspend surfaces: `CP_VMID_RESET`, `CP_VMID_PREEMPT`, `CP_VMID_STATUS`, `CPC_SUSPEND_CTX_SAVE_BASE_ADDR_LO/HI`, `CPC_SUSPEND_CTX_SAVE_CONTROL`, suspend stack/workgroup offsets and sizes, `CPC_SUSPEND_CTX_SAVE_SIZE`, `CPC_OS_PIPES`, and the start of `CP_SUSPEND_RESUME_REQ`.

## Control Flow

This header has no runtime control flow. It affects runtime behavior only when C code expands these macros while composing or decoding register values.

The typical implied flow is:

1. Driver code selects a GC 10.3.0 register offset from the companion offset header.
2. It reads, writes, or read-modify-writes a register through AMDGPU MMIO/SOC15 helpers.
3. It uses the `__SHIFT` and `_MASK` pair, often via `REG_SET_FIELD` or `REG_GET_FIELD`, to isolate the intended field.
4. Hardware command processor, shader processor interface, compute dispatch, ring-buffer, VM, interrupt, or power-management state machines execute the real operation.

For shader and compute dispatch programming, higher-level AMDGPU/KFD paths program shader program bases, resource registers, user-data registers, scratch/temporary-ring controls, VMID association, and dispatch initiator bits in a required hardware order. This chunk only provides the field layout; it does not define queue setup order, cache invalidation order, wave launch ordering, or trap/relaunch sequencing.

For CP/CPC rings, higher-level code programs ring-buffer bases and sizes, read-pointer writeback addresses, write pointers, VMIDs, doorbell apertures, and control bits before queue execution. Interrupt handlers and fault paths then read CP/CPC status, error, PASID, address, VMID, and ring-specific interrupt fields to attribute and clear events. The header does not specify clear-on-read, write-one-to-clear, polling, or reset timing semantics.

## State And Persistence Behavior

The macros are stateless compile-time constants. Persistent and volatile state exists only in GPU hardware registers, firmware-managed queue state, ring buffers, doorbell pages, and memory-backed save/restore areas.

Hardware state described by the shader and compute portions includes shader program addresses, shader resource allocation, user SGPR/user-data payloads, trap/exception enable bits, LDS and scratch requirements, CU and shader-engine targeting masks, compute dimensions, dispatch IDs, relaunch payloads, wave restore addresses, and thread tracing/performance counter enables. These values normally persist until queue teardown, shader stage reprogramming, graphics or compute pipeline state change, GPU reset, power-gating loss, suspend/resume reinitialization, or firmware intervention.

Hardware state described by the CP/CPC portions includes ring-buffer base addresses, read/write pointer fields, writeback addresses, queue VMID assignment, doorbell ranges and status, interrupt masks and latched statuses, UTCL1 control/error state, ECC/EDC first occurrence fields, power and memory sleep configuration, VMID reset/preempt status, and suspend context-save addresses and sizes. Some are ordinary configuration registers; some are live status bits; some are hardware-updated counters or first-fault latches; some are self-clearing command bits; and some may be clear-on-write or write-one-to-clear depending on the register. This generated shift/mask header does not encode access permissions or side-effect classes.

Reserved fields appear in several registers. Consumers must preserve reserved bits during read-modify-write unless hardware documentation or existing driver sequences say otherwise.

## Dependencies And Integration Points

This chunk depends on the generated GC 10.3.0 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h` supplies matching offsets for the register names in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_default.h` supplies reset/default values for related registers where generated defaults exist.
- AMDGPU helper macros provide the actual bitfield operations and MMIO access.
- GC 10.3.0 consumers in this tree include `amdgpu/amdgpu_amdkfd_gfx_v10_3.c`, `amdgpu/gfxhub_v2_1.c`, `amdgpu/sdma_v5_2.c`, `amdgpu/amdgpu_sdma.c`, and `pm/swsmu/smu11/vangogh_ppt.c`, which include this shift/mask header directly or alongside the matching offset header.
- Similar register families exist in neighboring generation headers such as GC 10.1.0, GC 9.x, GC 11.x, and GC 12.x. Names are intentionally familiar, but layouts are not guaranteed to be identical.

The runtime integration points are broad: graphics shader-stage programming, compute queue setup, KFD process/queue dispatch, ring submission, doorbell programming, VM fault attribution, CP interrupt handling, GPU reset and hang diagnosis, power/clock/memory sleep configuration, ECC/EDC reporting, preemption, suspend/resume, and context save/restore.

## Risks And Edge Cases

- Generated-header drift is the central risk. A wrong shift or mask can compile successfully while programming the wrong hardware bit.
- This work item starts and ends inside register groups. The first visible line belongs to `SPI_SHADER_USER_DATA_VS_30`, whose register comment and possibly earlier paired context are in the previous chunk. The last visible register, `CP_SUSPEND_RESUME_REQ`, is incomplete until the next chunk provides `RESUME_REQ_MASK`.
- Many families are repeated with small differences. `SPI_SHADER_PGM_RSRC2_GS_VS`, `SPI_SHADER_PGM_RSRC2_GS`, `SPI_SHADER_PGM_RSRC2_HS`, and `COMPUTE_PGM_RSRC2` look similar but encode different stage-specific fields. CP ring controls likewise differ between `CP_RB0_CNTL`, `CP_RB_CNTL`, `CP_RB1_CNTL`, and `CP_RB2_CNTL`.
- Full-width `DATA`, address, ID, and mask registers are easy to treat as interchangeable, but their consumers have different ordering, alignment, VMID, and firmware-ownership rules.
- Shader program resource fields control occupancy, scratch, LDS, exception, trap, WGP mode, forward-progress, and memory-order behavior. Bad field widths or stale generation assumptions can cause shader launch failures, hangs, trap misbehavior, or performance regressions.
- Compute dispatch fields are sequencing-sensitive. Misprogramming dispatch dimensions, thread counts, scratch base, relaunch payloads, or restore addresses can corrupt queue execution or make hangs hard to attribute.
- Ring-buffer and doorbell fields are queue-liveness critical. Incorrect size, block size, pointer, writeback, cache policy, VMID, or doorbell range masks can lead to lost submissions, stuck fences, pointer drift, or command processor faults.
- CP/CPC interrupt/status fields can be latched, masked, or clear-sensitive. Wrong masks can miss GPU faults, fail to clear an interrupt, create interrupt storms, or report errors against the wrong ring, pipe, queue, VMID, or PASID.
- UTCL1 and VM/PASID fields are isolation-sensitive. Mis-decoding or misprogramming fault, no-PTE, no-execute, bypass-PASID, or VMID-reset bits can hide real address-space faults or break process attribution.
- Power, memory sleep, and clock halt fields can interact with active queues. Consumers must follow established enable/disable sequencing and avoid full-register writes that trample reserved bits.
- Suspend, resume, preempt, and context-save fields are cross-boundary state. Offsets and sizes must match firmware/hardware expectations or queues can resume with corrupted or incomplete state.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware integration:

- Build AMDGPU/KFD configurations that include GC 10.3.0 support. Missing, renamed, or malformed macros should surface as compile failures in queue, VM, interrupt, SDMA/GFXHUB, or power-management code.
- Mechanically compare every `__SHIFT` and `_MASK` in this chunk against AMD's authoritative GC 10.3.0 register database.
- Cross-check that each register group has matching offset entries in `gc_10_3_0_offset.h` and, where applicable, reset/default entries in `gc_10_3_0_default.h`.
- Run mask/shift consistency checks: masks should align with shifts, full-width `DATA` fields should be `0xFFFFFFFFL`, high address fields should use the expected reduced width, and repeated CP interrupt/pipe families should differ only where the hardware definition says so.
- Boot affected hardware and run graphics plus compute workloads that exercise shader program resource programming, compute dispatch dimensions, user SGPR/user-data payloads, scratch/LDS usage, wave32 mode, traps, relaunch/restore, and thread tracing.
- Exercise KFD queue creation/destruction, process VM faults, doorbell submissions, ring write-pointer updates, read-pointer writeback, fence progress, and multi-ring interrupt handling.
- Exercise GPU reset, suspend/resume, queue preemption, VMID reset, context save/restore, power gating, and memory sleep transitions while checking for stuck rings or corrupted queue state.
- Check runtime diagnostics: DRM/KFD logs, CP fatal error and `CP_GFX_ERROR`, UTCL1 permission/TLB errors, ECC/EDC first occurrence fields, ring-specific interrupt status, MEC F32 interrupt/disables, VMID preempt status, and suspend context-save status.
- Decode known-good register dumps with these masks and compare against reference tooling or hardware documentation, especially for shader resource fields, compute dispatch state, CP ring controls, doorbells, interrupt attribution, PASID/VMID fields, and suspend/preempt state.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002482`. The final per-file research should merge this with neighboring chunks for full `gc_10_3_0_sh_mask.h` coverage. In particular, the previous chunk owns the beginning of `SPI_SHADER_USER_DATA_VS_30`, and the next chunk completes `CP_SUSPEND_RESUME_REQ` before continuing later CP/DDID/HQD and subsequent register families.

### subset-b-002483: lines 17372-19900

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 17372-19900

## Purpose

This chunk is generated AMD GC 10.3.0 register bitfield metadata. It contains no executable C logic; it exports preprocessor `__SHIFT` and `_MASK` constants that AMDGPU, AMDKFD, power-management, debug, and profiling code use to compose and decode 32-bit MMIO register values. The matching register offsets and base indices are in `gc_10_3_0_offset.h`.

The selected range starts in the command-processor suspend/DDID/HQD area, spans SPI, compute HQD, DIDT/CAC, TCP, and GDS address blocks, and ends at the first depth-buffer render/count registers in `gc_gfxdec0`. Although this repository subtree is under `ceph-client`, this file is AMD GPU hardware-description metadata rather than filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocations, locks, or callbacks in this range. The API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask for that field inside the register.
- Consumers combine these with `mm<REGISTER>` and `mm<REGISTER>_BASE_IDX` macros from `gc_10_3_0_offset.h`, usually via `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `SOC15_REG_OFFSET`, or KFD MQD initialization code.

Major register groups in this chunk:

- Command processor suspend and draw-dispatch ID state: `CP_SUSPEND_CNTL`, `CP_IQ_WAIT_TIME3`, `CPC_DDID_*`, `CP_DDID_*`, and graphics DDID counters/pointers. These define suspend enable/lock/status bits, DDID buffer base addresses, VMID selection, policy/mode/enable fields, in-flight counts, read/write pointers, and delta-report counters.
- Graphics HPD/HQD and MQD queue state: `CP_GFX_HPD_*`, `CP_GFX_MQD_*`, `CP_GFX_HQD_*`, `CP_RB_*`, `CP_CE_*`, and `CP_HQD_GFX_*`. Fields describe mapped/active queue state, queue priority and quantum, ring-buffer base/read/write pointers, read-pointer report addresses, write-pointer poll addresses, doorbell offsets and enables, buffer sizing, cache policy, execute/volatile/no-update flags, dequeue requests, idle/preempt status, HQ control messages, CE queue mirrors, and MQD VMID/privilege/cache controls.
- CP DMA watchpoints and miscellaneous CP status/control: `CP_DMA_WATCH0..3_*`, `CP_DMA_WATCH_STAT_*`, `CP_PFP_JT_STAT`, `CP_CE_JT_STAT`, `CP_MEC_JT_STAT`, `CP_FETCHER_SOURCE`, `CP_CE_CS_PARTITION_INDEX`, ring active/status registers, `CPG_RCIU_CAM_*`, timestamp offsets, UTCL1 status registers, `CP_SD_CNTL`, `CP_SOFT_RESET_CNTL`, and `CP_CPC_GFX_CNTL`. These fields support DMA address watch setup, read/write watch masks, VMID filtering, trap/status reporting, command-source selection, ring activity inspection, timestamp adjustment, translation-cache status, soft reset, and CP graphics control.
- `addressBlock: gc_spipdec` shader-processor input controls: `SPI_ARB_PRIORITY`, arbitration cycle registers, workload-control pipe percentage registers for GFX/HP3D/CS pipes, graphics debug wave/trap control and mask registers, `SPI_COMPUTE_QUEUE_RESET`, CU resource reservation masks `SPI_RESOURCE_RESERVE_CU_0..9`, corresponding enable registers, compute wavefront context-save control, arbiter control, feature controls, and shader resource limit controls.
- `addressBlock: gc_cpphqddec` compute packet-processor HQD/MQD registers: `CP_HPD_*`, `CP_MQD_*`, `CP_HQD_*`, EOP base/control/pointers/events, context-save base/control/size/offset registers, GDS resource state, AQL control, suspend context-stack/workgroup-state offsets, DDID pointers/counts, and dequeue status. These macros are central to compute queue creation, MES/HWS interaction, KFD MQD layout, doorbells, packet queue behavior, indirect-buffer handling, semaphores, atomics, scheduler controls, EOP event queues, context save/restore, and suspend/resume.
- `addressBlock: gc_didtdec` and `gc_gccacdec` power/telemetry controls: DIDT indirect index/data/auto-increment registers and GC/SE CAC, EDC, throttle, perf counter, stretch, hysteresis, and indirect index/data registers. These fields are used for dynamic-inductive-droop and chip-activity/power-control programming by firmware or power-management code.
- `addressBlock: gc_tcpdec` texture/cache watch and perf filter registers: `TCP_WATCH0..3_ADDR_H/L`, `TCP_WATCH0..3_CNTL`, `TCP_UTCL0_STATUS`, `TCP_PERFCOUNTER_FILTER`, `TCP_PERFCOUNTER_FILTER_EN`, and `TCP_PERFCOUNTER_FILTER2`. Fields define watched address windows, VMID/mode/valid controls, translation-cache status, and performance counter filter selection.
- `addressBlock: gc_gdspdec` GDS/GWS/OA state: `GDS_VMID0..15_BASE/SIZE`, `GDS_GWS_VMID0..15`, `GDS_OA_VMID0..15`, GWS resource reset masks, OA reset mask/reset, GDS clock/enhancement controls, OA CGPG restore selectors, compute max wave ID, CS/GFX context-switch status and counters, VS/PS/GS context-switch counters and index, and `GDS_MEMORY_CLEAN`. These fields partition GDS, global wave sync, and ordered append resources per VMID, reset or clean resources, expose context-switch read/write activity, and control GDS memory cleanup.
- The beginning of `addressBlock: gc_gfxdec0`: `DB_RENDER_CONTROL` and `DB_COUNT_CONTROL`. These depth-buffer fields control depth/stencil clear/copy/decompress/resummarize behavior, pixel-shader invocation disable, Z-pass/Z-fail/stencil/depth-fail counting, sample rate, and slice enables.

Field naming is hardware-descriptive. `*_BASE_ADDR_*`, `*_ADDR_*`, and `*_POLL_ADDR_*` fields carry aligned GPU addresses; `*_RPTR` and `*_WPTR` fields carry queue pointers; `DOORBELL_*` fields map queue notification; `ACTIVE`, `MAPPED`, `IDLE`, `STATUS`, `FINISH`, `HIT`, and `INFLIGHT_COUNT` fields expose live hardware state; `START`, `RESET`, `CLEAR`, `DEQUEUE_REQ`, and `SUSPEND_ENABLE` fields trigger state transitions; `RSVD` and `UNUSED` fields identify bits that consumers should not repurpose.

## Control Flow

This header has no runtime control flow. Runtime behavior is implemented by driver and firmware code that includes the generated offset and shift/mask headers:

1. ASIC-specific code selects the GC 10.3 register namespace and includes `gc_10_3_0_offset.h` plus `gc_10_3_0_sh_mask.h`.
2. Driver paths choose a register offset such as `mmCP_HQD_PQ_CONTROL`, `mmCP_GFX_HQD_CNTL`, `mmGDS_VMID0_BASE`, or `mmTCP_WATCH0_CNTL`.
3. The code composes or decodes register values with the macros in this chunk, often using `REG_SET_FIELD` or direct shift/mask operations for MQD memory images.
4. MMIO helpers or MQD writes apply the value while higher-level driver code serializes access with GRBM/SRBM selection, reset state, queue ownership, firmware handoff, or power-management sequencing.

Representative consumer flows in this tree include `gfx_v10_0.c` building graphics and compute MQDs with `CP_GFX_HQD_CNTL`, `CP_RB_DOORBELL_CONTROL`, `CP_HQD_PQ_DOORBELL_CONTROL`, `CP_MQD_CONTROL`, and `CP_HQD_PQ_CONTROL`; GDS VMID initialization clearing `GDS_VMID0_BASE/SIZE`, `GDS_GWS_VMID0`, and `GDS_OA_VMID0`; KFD MQD managers setting `CP_HQD_PQ_CONTROL__QUEUE_SIZE`, `RPTR_BLOCK_SIZE`, `NO_UPDATE_RPTR`, `SLOT_BASED_WPTR`, `QUEUE_FULL_EN`, `PRIV_STATE`, and `KMD_QUEUE`; and KFD debug paths programming TCP watch registers.

The macros do not encode valid ordering. Queue setup still requires correct MQD zeroing/restoration, base-address alignment, ring pointer initialization, doorbell programming, GRBM selection, queue activation/dequeue sequencing, and GPU reset/suspend handling. Similarly, GDS resource programming, TCP watchpoint updates, SPI queue resets, power telemetry controls, and DB render/count changes depend on hardware-defined ordering outside this header.

## State And Persistence Behavior

This file stores no software state and persists nothing. It describes hardware state exposed through GC 10.3 registers.

The represented state is highly stateful in hardware:

- Queue state persists in CP MQD/HQD registers and in MQD memory images until reprogrammed, overwritten by firmware, or lost/reset by GPU reset and power events.
- Doorbell and ring-pointer registers bridge CPU-visible queues, writeback memory, and CP scheduling state; stale base addresses, VMID fields, or pointer fields can redirect hardware queue traffic.
- Suspend, dequeue, preempt, idle, active, mapped, in-flight, and status fields are live hardware state rather than ordinary durable configuration.
- GDS/GWS/OA VMID windows and reset/clean bits define per-VMID access to scarce global resources; initialization commonly clears non-firmware VMID access and relies on firmware or later queue setup to re-enable valid allocations.
- TCP watchpoint and CP DMA watchpoint state can affect debugging and memory-fault observability for selected VMIDs and address windows.
- DIDT/CAC/EDC/throttle controls describe power and reliability telemetry/control state that may be firmware-owned and power-state-sensitive.
- DB render/count registers affect graphics pipeline behavior and counters for active draws.

The macros do not mark fields as read-only, write-only, write-one-to-clear, self-clearing, sticky, reserved, shadowed in an MQD, or firmware-owned. Consumers must preserve unrelated fields on read-modify-write paths and respect the access semantics from the ASIC register specification.

## Dependencies And Integration Points

Direct dependency:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h` for the corresponding `mm*` register offsets and base indices.

Known direct include users of this GC 10.3.0 shift/mask header in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`

Broader integration points include:

- AMDGPU graphics ring and compute ring initialization, reset recovery, suspend/resume, and MQD backup/restore.
- AMDKFD process queue creation, debug trap/watchpoint support, VMID setup, and hardware scheduler or MES interactions.
- GDS/GWS/OA allocation and cleanup for graphics, compute, and firmware-owned VMIDs.
- CP queue doorbells, EOP queues, indirect buffers, context-save areas, dequeue/preempt handling, and DDID tracking.
- SPI queue reset, wave debug/trap controls, resource-reservation controls, and shader resource limits.
- TCP watchpoints and perf-counter filtering used by debugging, profiling, and validation.
- Power-management and firmware paths using DIDT, CAC, EDC, throttle, and hysteresis registers.
- Depth-buffer render/count state used by clear/decompress/copy and z/stencil count paths.

## Risks And Edge Cases

- Header/offset pairing is critical. Using these `gc_10_3_0_sh_mask.h` fields with a different GC offset header can compile cleanly while programming the wrong register bits.
- The constants are untyped and carry no access semantics. A field that looks writable may actually be read-only, write-one-to-clear, self-clearing, firmware-owned, or reserved.
- Queue fields are sequencing-sensitive. Wrong `QUEUE_SIZE`, `RB_BUFSZ`, `RB_BLKSZ`, `RPTR_BLOCK_SIZE`, base address alignment, VMID, `PRIV_STATE`, `KMD_QUEUE`, `NO_UPDATE_RPTR`, `SLOT_BASED_WPTR`, or doorbell offset can cause lost packets, stuck queues, memory corruption, preemption failures, or GPU hangs.
- Several address fields intentionally start at bit 2, 6, 7, 8, or 12 because the hardware stores aligned addresses. Consumers must shift or mask GPU addresses exactly as expected by the register, not as generic byte addresses.
- Many status/action registers mix live status bits with control bits. Blind writes can clear status, retrigger resets, force dequeue/suspend behavior, or preserve stale live bits into an MQD image.
- GDS/GWS/OA VMID programming is resource-partitioning state. Failing to clear or restore the correct VMID windows can leak global data-share access across processes or prevent firmware from saving/restoring needed entries.
- TCP and CP DMA watchpoint registers are VMID and address-window sensitive. Incorrect masks, valid bits, or mode fields can silently miss debug events or trigger on unrelated traffic.
- DIDT/CAC/EDC/throttle fields are power and reliability controls. Driver-side changes must be coordinated with SMU/firmware ownership and power state, or telemetry and throttling behavior can become misleading or unstable.
- Reserved/unused fields are common. ASIC revisions may assign different meanings to those bits, so read-modify-write preservation matters.
- The chunk boundary is artificial: it starts immediately after `CP_SUSPEND_RESUME_REQ` and ends before the rest of `gc_gfxdec0` DB state. Adjacent chunks are required for a complete per-file register map.

## Test Signals

Useful validation is mostly build, static, and hardware behavior coverage:

- Build coverage for AMDGPU, AMDKFD, SDMA, GFXHUB, and SMU paths that include `gc_10_3_0_offset.h` and `gc_10_3_0_sh_mask.h`.
- Generated-header checks that every `__SHIFT` has a matching `_MASK`, masks are aligned to their shifts, fields do not overlap unexpectedly, and register names match `gc_10_3_0_offset.h`.
- Graphics ring and compute ring smoke tests that initialize MQDs, enable doorbells, submit packets, observe read/write pointer movement, idle queues, and recover correctly after reset and suspend/resume.
- KFD queue tests covering user queues, kernel queues, AQL queues, queue full/no-update-pointer modes, dequeue/preempt, EOP handling, and MQD save/restore.
- GDS/GWS/OA tests that verify per-VMID base/size/mask programming, reset behavior, memory clean start/finish, and context-switch counters.
- Debug/watchpoint tests for CP DMA and TCP watch registers using multiple VMIDs and address ranges, confirming expected trap/status behavior and no false positives on unrelated traffic.
- SPI tests that exercise compute queue reset, trap/debug controls, wave context save, and CU resource reservation enable masks.
- Power-management validation for DIDT/CAC/EDC/throttle registers across runtime PM, suspend/resume, and SMU firmware transitions.
- DB render/count tests around depth/stencil clears, copies, decompression/resummarization, zpass/zfail/stencil/depth-fail counts, sample-rate selection, and slice enable fields.
- Regression indicators include stuck or unmapped queues, doorbell misses, non-advancing ring pointers, incorrect queue idle/preempt status, VMID resource leakage, missed watchpoint traps, unexpected throttling telemetry, failed depth/stencil clears, and GPU hangs isolated to GC 10.3 ASICs.

### subset-b-002484: lines 19901-22380

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 19901-22380

## Purpose

This chunk is part of AMD's generated GC 10.3.0 register bitfield header. It defines `__SHIFT` and `__MASK` macros for graphics-context registers in the `gc_gfxdec0` address block, starting in the tail of `DB_COUNT_CONTROL`, covering depth-buffer, rasterizer/scissor, viewport, shader-pixel-input, color/blend state, and ending in the middle of the `CB_BLEND*` control series. The header itself contains no executable code; its purpose is to provide stable symbolic bit positions for users of `REG_SET_FIELD`, `REG_GET_FIELD`, packet builders, clear-state tables, and direct MMIO register programming in the AMDGPU/KFD driver.

The covered area is mostly context/register state used by graphics command submission and GPU initialization/reset paths. It is source-tree-aligned with the AMD DRM driver register stack: offset headers name registers, this `*_sh_mask.h` header names fields, and driver code composes or decodes register values through those macros.

## Important APIs, Types, and Macros

There are no C functions, structs, or runtime APIs in this slice. The exported interface is a large set of preprocessor constants following the pattern:

- `<REGISTER>__<FIELD>__SHIFT`: bit position of a hardware field.
- `<REGISTER>__<FIELD>_MASK`: mask for the field in the register word.

Important register groups in this chunk:

- `DB_*`: depth-buffer and stencil state, including `DB_DEPTH_VIEW`, `DB_RENDER_OVERRIDE`, `DB_RENDER_OVERRIDE2`, `DB_Z_INFO`, `DB_STENCIL_INFO`, depth/stencil read/write bases, HTILE base high/low, clears, bounds, and stencil reference masks. These fields encode depth/stencil formats, mip/slice selection, compression/decompression behavior, expclear support, read-only state, VRS overrides, cache policy, and base addresses.
- `PA_SC_*` and `PA_CL_*`: scan converter, rasterizer, and clip/viewport state. This includes screen/window/generic scissor rectangles, cliprects, 16 viewport scissor pairs, 16 viewport Z min/max pairs, raster configuration, tile steering, viewport scale/offset registers, user clip planes, and near-clip Z programming.
- `CB_*` and `SX_*`: color buffer, shader export, and blend state. This includes target and shader write masks, color blend constants, DCC control, coverage output, render-backend L2/cache control, pixel shader down-convert controls, blend optimization controls, `SX_MRT0..7_BLEND_OPT`, and `CB_BLEND0..3_CONTROL` within the requested range.
- `SPI_*`: shader processor interpolation and pixel shader input state, including `SPI_PS_INPUT_CNTL_0..31`, `SPI_PS_INPUT_ENA`, `SPI_PS_INPUT_ADDR`, interpolation control, PS input control, barycentric control, temporary ring size, and shader index/position/Z/color export formats.
- `CP_*`, `VGT_*`, and context placeholders: `CP_PERFMON_CNTX_CNTL`, `CP_PIPEID`, `CP_RINGID`, `CP_VMID`, `CONTEXT_RESERVED_REG0/1`, and index bound/reset registers for graphics command processor and vertex grouper/tessellator context.

Representative consumer patterns elsewhere in the tree show how this generated interface is intended to be used. For example, `gfx_v10_0_set_user_wgp_inactive_bitmap_per_sh()` builds `GC_USER_SHADER_ARRAY_CONFIG` by shifting a bitmap by the matching `__SHIFT`, masking with the matching `__MASK`, and writing the register. KFD wave-control code writes `SQ_CMD` through the same offset/mask framework. The same convention applies to fields in this chunk when callers need to update `DB_Z_INFO`, `SPI_PS_INPUT_CNTL_*`, or blend/scissor fields without hard-coding bit positions.

## Control Flow

This header has no direct control flow. Its influence is compile-time substitution into driver code that performs these runtime flows:

- Graphics context construction: command stream or kernel driver paths program DB/PA/SPI/SX/CB registers using these masks to encode depth/stencil, viewport, interpolation, export, and blending state.
- Initialization and reset: clear-state tables and default context-state programming include many of these registers, such as `DB_RENDER_OVERRIDE`, `DB_Z_INFO`, viewport scissors, `SPI_PS_INPUT_CNTL_*`, `SX_MRT*_BLEND_OPT`, and `CB_BLEND*_CONTROL`.
- Runtime register updates: direct MMIO paths use `REG_SET_FIELD`/`REG_GET_FIELD` with the register/field names to alter specific fields while preserving unrelated bits.
- Debug and validation: register dumps, hang analysis, and bring-up code rely on the symbolic field names to interpret or compose GC state consistently with the hardware packet/register ABI.

Because the file is generated-style data, the main "flow" is dependency flow: hardware specifications feed the header, the header feeds C macros, and those macros feed the driver register writes emitted during GPU initialization, command submission, context restore, and KFD/GFX management.

## State and Persistence Behavior

The macros describe hardware state, but they do not hold state themselves. Persistence depends on the target register:

- DB/PA/SPI/SX/CB registers are graphics context state. Their values can persist in GPU context images, command streams, or kernel-managed clear/default states until overwritten by later context programming or reset.
- Base address fields such as `DB_Z_READ_BASE`, `DB_Z_WRITE_BASE`, stencil base registers, HTILE base registers, `TA_BC_BASE_ADDR`, and `COHER_DEST_BASE*` represent GPU-address state. Incorrect high/low field composition can redirect depth/stencil, metadata, or coherency operations.
- Cache-control and compression fields (`DB_RMI_L2_CACHE_CONTROL`, `CB_RMI_GL2_CACHE_CONTROL`, `DB_Z_INFO`, `DB_STENCIL_INFO`, `CB_DCC_CONTROL`) affect memory visibility, compression validity, decompression, and export/clear behavior across draws.
- Viewport, scissor, cliprect, and shader-input fields persist as pipeline state for following draws until a new command stream changes them.
- `CP_VMID`, `CP_PIPEID`, and `CP_RINGID` describe command processor context identity and are sensitive to queue/context management.

## Dependencies

This chunk depends on the AMD GPU register ABI for GC 10.3.0 and must remain synchronized with sibling generated headers:

- `gc_10_3_0_offset.h` supplies register offsets for names whose field layout is defined here.
- AMDGPU helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` depend on the exact `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` naming convention.
- SOC15 register accessors such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32`, and `SOC15_REG_OFFSET` combine offset headers with these field definitions.
- Clear-state arrays such as `clearstate_gfx10.h` include default values for several registers in this group and must match the same hardware layout.
- Userspace-visible command submission and shader compilation flows indirectly depend on these layouts because command buffers and kernel state setup must agree on register field semantics.

## Integration Points

Primary integration points are in the AMD DRM GPU driver:

- GFX initialization and context setup in `drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c` and related generation-specific files.
- KFD wave/control and compute dispatch support, which uses the same generated register field convention for GC register programming.
- Clear-state headers and context restore paths that seed DB/PA/SPI/SX/CB defaults.
- Command processor, ring, and VMID management paths that need `CP_*` context fields.
- Render backend and depth/stencil code paths that compose DB/CB cache, compression, format, base-address, and blend fields.
- Shader and pipeline programming paths that populate SPI pixel-input controls, interpolation state, export formats, viewport transforms, and clipping/scissor state.

The file is not standalone; it becomes meaningful when included with the matching offset header and AMDGPU register helper macros.

## Risks and Edge Cases

- Bitfield drift is the highest risk. A wrong mask or shift silently writes the wrong hardware bits and can cause rendering corruption, GPU hangs, invalid memory access, or broken context save/restore.
- This chunk starts after the `DB_COUNT_CONTROL` heading and includes only its trailing masks. Chunk-level readers should reconcile the earlier lines during final merge so that `DB_COUNT_CONTROL` is not documented as beginning here.
- This chunk ends at `CB_BLEND3_CONTROL`; the `CB_BLEND4..7_CONTROL` continuation appears after the requested range. Final per-file reconciliation must merge the repeated blend-control pattern across adjacent chunks.
- Repeated register families create copy/paste or generator risks: viewport scissors/Z ranges, viewport scale/offsets, clip planes, `SPI_PS_INPUT_CNTL_0..31`, `SX_MRT0..7_BLEND_OPT`, and `CB_BLEND*` controls all rely on identical or near-identical layouts with only index changes.
- Address split registers (`*_BASE` plus `*_BASE_HI`) are sensitive to lost high bits and alignment assumptions such as 256-byte base fields.
- Reserved fields (`DB_RESERVED_REG_*`, `CONTEXT_RESERVED_REG*`, and named reserved subfields) must not be repurposed casually; hardware may require preserving reset values.
- Cache/compression fields in DB/CB registers are high-impact because stale compression metadata or wrong cache policy can produce subtle data corruption rather than immediate failures.
- VRS, viewport, scissor, and raster-config fields interact with draw clipping and sample locations. Invalid combinations may only appear under multisample, multi-viewport, or variable-rate shading workloads.

## Test Signals

Useful signals for changes touching this header or consumers of these fields:

- Compile coverage for AMDGPU/KFD with GC 10.x enabled; macro naming errors usually surface as build failures in `REG_SET_FIELD`/`REG_GET_FIELD` users.
- Boot and driver probe on a GC 10.3 ASIC or emulation target, checking register initialization and clear-state loading.
- Graphics smoke tests that exercise depth/stencil clears, HTILE compression, depth bounds, stencil read/write, color blending, DCC, multiple render targets, and MSAA.
- Piglit/dEQP/Vulkan CTS coverage for viewport/scissor arrays, clip planes, barycentric interpolation, PS input locations, MRT blend controls, color export formats, and depth/stencil formats.
- GPU hang and register-dump analysis: `DB_*`, `PA_SC_*`, `SPI_*`, `SX_*`, and `CB_*` values should decode consistently with the expected field masks.
- KFD/compute coexistence tests when command processor context fields or shared register helper conventions are modified.
- Static comparison against AMD-generated register headers for the same ASIC revision to catch accidental mask/shift edits.

### subset-b-002485: lines 22381-24801

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 22381-24801

## Scope

This chunk is a generated AMD GC 10.3.0 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `__SHIFT` value and a matching `__MASK` value used by AMDGPU register helpers to compose or decode 32-bit MMIO/indexed-register values. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines begin at the final visible mask for `CB_BLEND3_CONTROL`, then cover complete `CB_BLEND4_CONTROL` through `CB_BLEND7_CONTROL` entries, graphics pipeline state registers, primitive assembly/setup/scissor/rasterizer controls, geometry/tessellation/NGG/streamout controls, depth/color test controls, sample-location state, binner/conservative-raster controls, and color-buffer target state for `CB_COLOR0` through most of `CB_COLOR6`. The chunk ends at the `//CB_COLOR6_CLEAR_WORD1` marker before that register's field macros, so the `CB_COLOR6` render-target slot is intentionally incomplete in this chunk and continues in the next adjacent slice.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for the GC 10.3 graphics IP and is not Ceph filesystem code.

## Purpose

`gc_10_3_0_sh_mask.h` supplies the bit layouts for GC 10.3.0 registers. Driver code pairs these macros with register addresses from `gc_10_3_0_offset.h` and, where useful, defaults from `gc_10_3_0_default.h`. Consumers use the constants through helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` so they can change or inspect one hardware field without hard-coding magic bit positions.

This chunk focuses on the graphics draw and render-backend state needed to issue draws and configure rasterization/output-merger behavior:

- Blend-state controls for render targets 4 through 7, including source/destination blend factors, color/alpha combine functions, separate alpha blending, enable, and ROP3 disable.
- Draw and index-fetch controls such as `VGT_DMA_BASE`, `VGT_DMA_BASE_HI`, `VGT_DMA_SIZE`, `VGT_DMA_MAX_SIZE`, `VGT_DMA_INDEX_TYPE`, `VGT_DRAW_INITIATOR`, `VGT_IMMED_DATA`, `VGT_EVENT_ADDRESS_REG`, `VGT_DMA_EVENT_INITIATOR`, and multi-primitive reset state.
- Depth, stencil, EQAA, alpha-to-mask, shader depth/export, and color-control fields in `DB_DEPTH_CONTROL`, `DB_EQAA`, `DB_SHADER_CONTROL`, `DB_ALPHA_TO_MASK`, and `CB_COLOR_CONTROL`.
- Clip/setup/rasterization controls under `PA_CL_*`, `PA_SU_*`, and `PA_SC_*`, including clip distance enables, viewport transform enables, vertex output controls, NaN/Inf handling, point and line sizing, line stipple, polygon offset, primitive filtering, conservative rasterization, binner behavior, variable-rate shading, stereo routing, centroid priority, MSAA sample locations, AA masks, and scan-converter behavior.
- Vertex-geometry-tessellation state under `VGT_*` and `GE_*`, including output path, tessellation parameters, LS/HS/GS stage enable/configuration, GS ring offsets/item sizes, NGG subgroup controls, primitive grouping, streamout buffers, instance stepping, primitive ID behavior, and shader-stage enable flags.
- Color-buffer render-target descriptors for `CB_COLOR0` through `CB_COLOR5`, plus most of `CB_COLOR6`, including base addresses, pitch/slice/view geometry, format/type/swap/compression bits, sample/fragment counts, tiling, DCC control, CMASK/FMASK/DCC metadata bases, and fast-clear words.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register-address symbols live in the companion offset header, typically with names such as `mmCB_COLOR0_INFO` or `mmVGT_DRAW_INITIATOR` depending on the register space.
- AMDGPU callers normally access these fields through `REG_SET_FIELD`, `REG_GET_FIELD`, read-modify-write MMIO helpers, packet-building code, or PM4/state-emission paths.

The main register families in this slice are:

- `CB_BLEND4_CONTROL` through `CB_BLEND7_CONTROL`: repeated render-target blend layouts. Each has color and alpha source/destination blend fields, color and alpha combine-function fields, `SEPARATE_ALPHA_BLEND`, `ENABLE`, and `DISABLE_ROP3`.
- `CS_COPY_STATE` and `GFX_COPY_STATE`: small state-copy selector registers with `SRC_STATE_ID`.
- Point/clip full-width data registers: `PA_CL_POINT_X_RAD`, `PA_CL_POINT_Y_RAD`, `PA_CL_POINT_SIZE`, `PA_CL_POINT_CULL_RAD`, and guard-band adjust registers all expose 32-bit data fields.
- `DB_DEPTH_CONTROL`, `DB_EQAA`, `DB_SHADER_CONTROL`, and `DB_ALPHA_TO_MASK`: depth/stencil test enables and functions, EQAA sample counts and over-rasterization, shader Z/stencil/export order behavior, alpha-to-mask enable and per-sample offsets.
- `PA_CL_CLIP_CNTL`, `PA_CL_VTE_CNTL`, `PA_CL_VS_OUT_CNTL`, `PA_CL_NANINF_CNTL`, `PA_CL_NGG_CNTL`, and `PA_CL_VRS_CNTL`: clipper and viewport-transform control, vertex shader output component enables, NaN/Inf treatment, NGG vertex reuse controls, and VRS rate-combiner policy.
- `PA_SU_SC_MODE_CNTL`, `PA_SU_*`, and `PA_SC_*`: setup and scan-converter controls for culling, polygon mode, provoking vertex, small primitive filtering, over-rasterization, stereo, point/line dimensions, stipple, binner, conservative rasterization, sample locations, AA config, shader control, and viewport/scissor-related behavior.
- `VGT_*` and `GE_*`: draw initiation, DMA/index type, event initiation, output path, hull/tessellation parameters, group primitive/vector formatting, GS mode/on-chip controls, LS/HS config, GS ring/item sizing, streamout setup, primitive ID handling, instance step rates, shader-stage enablement, NGG subgroup sizing, and tessellation distribution.
- `CB_COLORn_*` for `n = 0..5` and partial `n = 6`: render-target state. The repeated layout includes `BASE`, `PITCH`, `SLICE`, `VIEW`, `INFO`, `ATTRIB`, `DCC_CONTROL`, `CMASK`, `CMASK_SLICE`, `FMASK`, `FMASK_SLICE`, `CLEAR_WORD0`, `CLEAR_WORD1`, and `DCC_BASE`. For `CB_COLOR6`, this chunk reaches `CLEAR_WORD0` and the `CLEAR_WORD1` marker, but not the actual `CLEAR_WORD1` shift/mask macros.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU consumers:

1. Select the GC 10.3.0 register header for the active ASIC generation.
2. Choose the matching register address from `gc_10_3_0_offset.h`.
3. Read an existing register value or prepare a command-stream register write.
4. Use the `__SHIFT`/`__MASK` pairs, often through field helper macros, to pack a field value or extract a status/configuration field.
5. Submit the resulting MMIO write or PM4 register packet in a larger draw, pipeline-state, streamout, render-target, reset, or resume sequence.

For draw setup, higher-level code programs VGT/IA/GE shader-stage and DMA/index state before draw initiation. For rasterization, PA/SC/SU state controls clipping, sample positions, binner/conservative-raster behavior, VRS, culling, line/point/polygon details, and primitive filtering. For output-merger state, DB and CB registers configure depth/stencil behavior, blending, alpha-to-mask, color target formats, compression, metadata, and clear values. This file does not define ordering constraints, packet sequences, cache flushes, waits, or hardware side effects; those are owned by the surrounding AMDGPU pipeline code and hardware programming guide.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe GPU register fields whose state is owned by hardware and by the AMDGPU command stream.

Most fields in this chunk represent graphics pipeline context state. Values persist in the GPU context or hardware register file until overwritten by later command packets, context switch restore, graphics IP reset, suspend/resume reinitialization, power-gating loss, or driver/firmware reprogramming.

The `CB_COLORn_*` registers describe render-target surfaces and associated metadata. `BASE`, `CMASK`, `FMASK`, and `DCC_BASE` fields are GPU address fragments in 256-byte units. `PITCH`, `SLICE`, `VIEW`, `INFO`, and `ATTRIB` encode image geometry, format, tiling, samples/fragments, compression, and view selection. `CLEAR_WORD0/1` store fast-clear color words. Incorrect persistence or stale restore of these fields can make later draws write the wrong surface, use the wrong compression mode, or interpret metadata incorrectly.

Depth/stencil, sample-location, streamout, and shader-stage registers are also stateful. Some fields are pure configuration; others initiate events or describe DMA/draw operations, such as `VGT_DRAW_INITIATOR`, `VGT_DMA_EVENT_INITIATOR`, and related VGT DMA fields. The shift/mask header does not encode whether a field is read-only, write-only, pulse-style, sticky, clear-on-read, or preserved across resets, so callers must rely on the hardware specification and established AMDGPU programming sequences.

Reserved bits and partial-register fields should be preserved during read-modify-write unless a documented full-register value is being emitted. This is especially important for PA/SC/VGT feature controls and CB/DCC compression state, where undocumented or generation-specific bits can change behavior.

## Dependencies And Integration Points

This chunk depends on the generated GC 10.3.0 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h` provides the matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_default.h` provides default/reset values for many of the same registers.
- AMDGPU GC 10.3 graphics code, command submission paths, KFD/compute integration, Mesa/userspace command-stream producers, debug tooling, and suspend/resume/reset code rely on the same hardware bit assignments being accurate.
- Common AMDGPU register helpers provide the actual packing, extraction, MMIO, and command-packet emission mechanisms.

Integration points include draw packet emission, index-buffer setup, primitive assembly, NGG/GS/tessellation enablement, streamout, depth/stencil tests, MSAA/EQAA/VRS, conservative rasterization, viewport/clip setup, render-target binding, fast clears, DCC/CMASK/FMASK metadata programming, GPU reset restoration, and hardware bring-up diagnostics. The repeated `CB_COLORn_*` layout is particularly important for render-target arrays and MRT rendering because userspace and kernel code must agree on slot numbering and field packing.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but writes the wrong hardware bits, which can present as rendering corruption, hangs, incorrect blending, broken depth tests, bad compression metadata, or performance regressions.
- The chunk starts and ends mid-family. It starts with only the last visible `CB_BLEND3_CONTROL` mask and ends before `CB_COLOR6_CLEAR_WORD1` field macros, so file-level conclusions must be merged with adjacent chunks.
- Repeated render-target layouts invite copy/paste or generator errors. `CB_COLOR0` through `CB_COLOR6` should remain structurally aligned where hardware requires it, but a single slot-specific mismatch can affect only one MRT target.
- Address fields are expressed as base units, commonly `BASE_256B`, not raw byte addresses. Consumers that shift or align addresses incorrectly can program plausible but invalid GPU addresses.
- Compression-related fields are high risk: `DCC_ENABLE`, `DCC_COMPRESS_DISABLE`, CMASK/FMASK base and slice fields, lossy precision, independent block settings, and fast-clear words must match the surface metadata layout and cache/flush protocol.
- DB/CB/PA/SC/VGT registers interact. For example, MSAA sample counts, sample locations, EQAA settings, alpha-to-mask, FMASK attributes, and color/depth target state must be mutually consistent.
- Event/draw initiator and DMA fields can have command-like side effects. Treating them as passive state or performing unsafely ordered writes may trigger wrong draws/events or undefined hardware behavior.
- Reserved fields and undocumented bits appear throughout this generated map. Full-register writes that do not preserve these bits can break generation-specific behavior.
- Some fields use high bits, full-width masks, or packed repeated nibbles. Callers should use unsigned 32-bit intermediates and helper macros rather than signed arithmetic or ad hoc constants.

## Test Signals

Useful validation is primarily build coverage, generated-data consistency, and hardware/runtime rendering coverage:

- Kernel build coverage for AMDGPU files that include `gc_10_3_0_sh_mask.h`, especially GC 10.3/Navi 2x graphics, display-interacting render paths, KFD, reset, and suspend/resume code.
- Mechanical comparison against AMD's authoritative GC 10.3.0 register database to confirm each `__SHIFT` and `__MASK` value and each repeated register family.
- Cross-checks that all registers in this slice have matching address macros in `gc_10_3_0_offset.h` and expected defaults in `gc_10_3_0_default.h` where defaults are generated.
- Static mask/shift sanity checks: masks should align with shifts, repeated `CB_COLORn_*` and `CB_BLENDn_CONTROL` layouts should be consistent across slots, and full-width data fields should use `0xFFFFFFFFL`.
- Render tests covering MRT blending, separate alpha blend, ROP3 behavior, depth/stencil compare and writes, alpha-to-mask, MSAA/EQAA sample positions, VRS, conservative rasterization, line/point rendering, polygon offset, and clip/guard-band behavior.
- Streamout, GS, tessellation, NGG, primitive ID, indirect/indexed draw, and multi-instance draw tests that exercise the VGT/GE fields in this chunk.
- Fast-clear and compression tests for color targets using CMASK/FMASK/DCC, including suspend/resume and GPU-reset restore paths.
- Runtime warning signals include GPU hangs during draw initiation, corrupted render targets, bad MRT slot output, incorrect depth/stencil behavior, mismatched fast-clear colors, DCC/metadata corruption, unexpected fallback to uncompressed rendering, or workload-specific regressions around binner/conservative-raster/VRS features.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002485`. It covers lines 22381-24801 of `gc_10_3_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the partial `CB_BLEND3_CONTROL` and `CB_COLOR6` families and to place this draw/raster/render-target state in the full GC 10.3.0 register map.

### subset-b-002486: lines 24802-27455

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 24802-27455

## Scope

This chunk is a generated AMD GC 10.3.0 register shift/mask header slice. It contains 2,117 `#define` entries across lines 24802-27455 of `gc_10_3_0_sh_mask.h`. The macros expose bit positions and masks for register fields using the standard generated naming scheme:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit index of a field.
- `<REGISTER>__<FIELD>_MASK`: the field mask inside the 32-bit register word.

There are no functions, data structures, enums, includes, allocations, locks, or direct register accesses in this range. The file lives under a `ceph-client` source mirror, but this content is AMDGPU graphics-core hardware metadata, not distributed filesystem code.

The chunk starts in the tail of color-buffer render-target state with `CB_COLOR6_CLEAR_WORD1` and `CB_COLOR6_DCC_BASE`, then covers `CB_COLOR7_*`, extended color/CMASK/FMASK/DCC base registers for slots 0-7, `CB_COLORn_ATTRIB2/ATTRIB3`, a large `gc_gfxudec` command-processor and user graphics register block, a `gc_cprs64dec` MES register block, and the opening of the `gc_gusdec` graphics unified scheduler/interconnect arbitration block. It ends in the middle of `GUS_SDP_TAG_RESERVE1`: line 27455 defines `VC6_MASK`, while the following line outside this work item defines `VC7_MASK`.

## Purpose

`gc_10_3_0_sh_mask.h` gives AMDGPU and AMDKFD code symbolic field metadata for GFX10.3/GC 10.3.0 registers. Driver code combines these macros with matching register offsets from `gc_10_3_0_offset.h` and register access helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, SOC15 MMIO helpers, PM4 packet emitters, and generated clear-state/golden-register tables.

This slice covers several important hardware surfaces:

- Color-buffer render-target slot state: `CB_COLOR7_BASE`, `PITCH`, `SLICE`, `VIEW`, `INFO`, `ATTRIB`, `DCC_CONTROL`, CMASK/FMASK bases and slices, clear words, DCC base, plus extended base and attribute registers for color slots 0-7.
- Command processor user-visible graphics state under `gc_gfxudec`: EOP completion addresses/data/fences, streamout addresses, primitive and shader invocation counters, pipe statistics, scratch registers, append/fence state, atomic preoperation values, CP memory-controller address/data windows, semaphores, DMA command state, coherency state, IB offsets, command buffer sizing/base fields, doorbell buffers, metadata bases, indirect draw/dispatch addresses, index buffer metadata, GDS backup, sample status, and user VGT/GE/PA/SQ/GDS state.
- GDS and streamout/atomic support: `GDS_RD_*`, `GDS_WR_*`, `GDS_ATOM_*`, `GDS_GWS_*`, and `GDS_OA_*` fields used for global data share read/write windows, atomics, ordered-append resources, and counters.
- MES control and debug state under `gc_cprs64dec`: program counter, interrupt routine, trap/vector registers, control/reset/active bits, priority, interrupt pending state, scratch/index/data windows, RISC-V-like machine status/cause/bad-address/instruction pointer registers, cycle/time/instret counters, cache controls, quantum values, doorbell controls, general-purpose registers, data-memory index/data windows, and perfcount control.
- GUS arbitration and credit controls under `gc_gusdec`: IO read/write combine flushes, IO and DRAM priority aging/queuing/fixed/urgency/quantum coefficients, group burst limits, SDP arbitration final limits, virtual-channel QoS priorities, tag and response credits, and the first SDP tag reserve fields.

The practical goal is readability and ASIC-specific correctness. Consumers can construct or decode a register word without hard-coding numeric bit locations, while still compiling to simple constant shifts and masks.

## Important APIs, Types, And Macros

This chunk exports only preprocessor constants. The important macro families are:

- `CB_COLOR7_*`: render target address and layout fields. `CB_COLOR7_INFO` defines format, endian, number type, component swap, fast clear, compression, blend controls, DCC enable, CMASK address type, and tiling bits. `CB_COLOR7_ATTRIB` and `CB_COLOR7_DCC_CONTROL` define tile modes, FMASK settings, sample/fragment counts, DCC block sizing, color transform, independent block modes, lossy precision, and DCC compression control.
- `CB_COLOR[0-7]_*_BASE_EXT`, `CMASK_BASE_EXT`, `FMASK_BASE_EXT`, and `DCC_BASE_EXT`: high/extension address bits for the surface and compression metadata base addresses. These are paired with the low base registers from this and neighboring chunks.
- `CB_COLOR[0-7]_ATTRIB2` and `ATTRIB3`: additional render-target geometry metadata such as metadata linearity, max compressed/uncompressed block sizes, alignment, pipe/bank addressing, mip tail, resource type, and channel read/write behaviors.
- `CP_EOP_*`, `CP_STREAM_OUT_*`, `CP_NUM_PRIM_*`, `CP_VGT_*COUNT*`, `CP_PA_*COUNT*`, `CP_SC_*COUNT*`, and `CP_PIPE_STATS_*`: completion, streamout, and graphics pipeline statistics fields. Many are 64-bit hardware values represented as low/high 32-bit register pairs.
- `SCRATCH_REG0` through `SCRATCH_REG7`, `SCRATCH_REG_ATOMIC`, `SCRATCH_REG_CMPSWAP_ATOMIC`, `SCRATCH_UMSK`, `SCRATCH_ADDR`, `CP_SCRATCH_INDEX`, and `CP_SCRATCH_DATA`: scratch and indexed scratch access fields used by CP firmware, debug, and command streams.
- `CP_APPEND_*`, `CP_*ATOMIC*_PREOP_*`, `CP_ME_MC_*`, `CP_SIG_SEM_*`, `CP_WAIT_*`, `CP_DMA_*`, `CP_COHER_*`, `CP_*IB*`, `CP_*CMD*`, and `CP_*DB*`: command processor append/fence state, atomic preoperation values, memory-controller read/write windows, semaphore addressing/timers, DMA source/destination/command words, coherency control/status, indirect-buffer offsets, command buffer bases/sizes, and doorbell buffer bases/sizes.
- `VGT_*`, `GE_*`, `WD_*`, `IA_*`, `PA_*`, `SQ_THREAD_TRACE_USERDATA_*`, `SQC_CACHES`, `TA_CS_BC_*`, `DB_*`, `GDS_*`, and `SPI_CONFIG_CNTL_*_REMAP`: user graphics state exposed through the `gc_gfxudec` block for draw setup, streamout, primitive counts, shader trace userdata, cache controls, buffer constants, depth/occlusion counters, GDS operations, and SPI remap controls.
- `CP_MES_*`: MES microcontroller/control fields for reset, halt, step, active pipe state, interrupt enable/pending, scratch access, machine status, exception cause, instruction/data cache operations, counters, process quantum, doorbells, general-purpose registers, and perfcount control.
- `GUS_IO_*`, `GUS_DRAM_*`, and `GUS_SDP_*`: arbitration and flow-control fields. Repeated group coefficients define age, queuing, fixed priority, urgency, urgency mode, quantum thresholds, burst limits, virtual-channel priority, tag limits, write/read response credits, and VC tag reservations.

Field names encode likely hardware intent but not full access semantics. For example, names ending in `STATUS`, `COUNT`, `COMPLETE`, `FLUSH`, `RESET`, `HALT`, `ACTIVE`, `ADDR`, `BASE`, `HI`, `LO`, `TIMEOUT`, `CREDITS`, or `RESERVE` suggest status, counters, commands, addresses, split register pairs, timeout, or resource reservation behavior, but this header does not say whether a field is read-only, write-one-to-clear, sticky, self-clearing, privileged, or context-saved.

## Control Flow

There is no runtime control flow in this header. It is declarative compiler input.

Runtime use normally follows this pattern:

1. Driver code selects a GC 10.3.0 register offset from `gc_10_3_0_offset.h`.
2. It inserts or extracts fields with the matching `__SHIFT` and `_MASK` macros, usually through AMDGPU helpers that token-paste the register and field names.
3. It writes, reads, polls, or dumps the register via SOC15 MMIO, GRBM-indexed access, PM4 packets, command stream state emission, or firmware/MES control paths.
4. Hardware blocks then interpret those bits as render-target layout, command-processor state, MES control/debug state, GDS operation state, or GUS arbitration/credit policy.

Important sequencing lives outside this file. Examples include programming all low/high or base/extension address halves coherently, setting render-target DCC/CMASK/FMASK metadata consistently with surface layout, reading split 64-bit counters with rollover awareness, emitting EOP and streamout addresses before events that write them, programming semaphore and doorbell fields with required alignment, waiting for CP coherency/status completion, controlling MES reset/halt/step only when firmware ownership allows it, and changing GUS arbitration/credit values only in hardware-safe initialization or tuning windows.

## State And Persistence Behavior

The macros themselves are stateless compile-time constants and persist nothing. They describe hardware-visible register state.

State represented by this chunk includes:

- Color render-target layout and compression state: base addresses, extended address bits, pitch/slice/view, format, tiling, sample/fragment counts, DCC/CMASK/FMASK metadata, clear words, and additional addressing/metadata attributes.
- Command processor completion and synchronization state: EOP done address/data, last fence values, streamout destinations, semaphore wait/signal addresses, wait timeouts, append data, and doorbell buffer metadata.
- Performance and query state: primitive written/needed counters, shader invocation counters, pipe statistics, occlusion/zpass counters, MES cycle/time/instret counters, and GDS ordered-append counters.
- CP execution support state: scratch registers, indexed scratch windows, atomic preoperation values, micro-engine memory-controller read/write state, DMA commands, coherency controls/status, indirect-buffer offsets, command-buffer bases and sizes, metadata bases, indirect draw/dispatch addresses, index buffer base/type, and GDS backup addresses.
- User draw state: VGT primitive/index/instance/tessellation/user-mode fields, GE index/min/max/stereo/user VGPR fields, WD buffer bases, PA line/stipple/trap-screen state, SQ thread trace userdata, SQC cache controls, TA constant buffer bases, DB counters, and GDS read/write/atomic/resource fields.
- MES firmware/control state: MES program/vector registers, control/reset/active/halt/step flags, interrupt state, machine registers, counters, doorbell controls, quantum controls, GP registers, data-memory index/data, and perfcount control.
- GUS arbitration state: IO and DRAM priority aging, queuing, fixed, urgency, quantum, burst, virtual-channel QoS, tag limits, response credits, and tag reservations.

Persistence is hardware-defined. Some fields are per-context or command-stream state that the driver emits repeatedly. Some are long-lived initialization or tuning registers that remain until reset, suspend/resume reinitialization, power gating, or a later write. Status, counter, complete, busy, and credit fields may change autonomously while the GPU runs. The header does not provide reset values; those are supplied by companion default headers or hardware documentation.

## Dependencies And Integration Points

This chunk must remain synchronized with the rest of the GC 10.3.0 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h` provides the corresponding register offsets and address block placement.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_default.h` provides reset/default values where generated.
- AMDGPU GFX10.3 code includes these generated headers for register programming, clear-state emission, golden settings, ring and queue setup, firmware/MES control, reset/recovery, profiling, and register dumps.
- AMDKFD queue and packet-management code indirectly depends on matching CP, MES, doorbell, scratch, semaphore, and dispatch-related field layouts.
- Render-target and DB/CB consumers depend on these fields matching user-mode command stream expectations for color formats, compression metadata, DCC/CMASK/FMASK layout, clear behavior, and address extension bits.
- GUS fields integrate with graphics interconnect scheduling, DRAM/IO arbitration, SDP virtual-channel priorities, credit limits, and performance tuning or golden-register initialization.

The macros depend on C preprocessor name matching rather than type checking. A mismatch between this file and the selected offset/default header, or between GC 10.3.0 and a neighboring generation such as GC 10.1.0, can compile successfully while targeting an incompatible field layout.

## Risks And Edge Cases

- The chunk starts mid-register: `CB_COLOR6_CLEAR_WORD1` is present without its preceding comment line inside the selected range. Neighboring chunks are needed for complete per-file context.
- The chunk ends mid-register: `GUS_SDP_TAG_RESERVE1__VC7_MASK` is on line 27456, just outside the requested range. Merge/reconciliation must not treat `GUS_SDP_TAG_RESERVE1` as complete based only on this document.
- Generated-header drift is high impact. A single bad shift or mask can silently corrupt adjacent hardware fields, causing rendering corruption, hangs, bad synchronization, wrong counters, or wrong memory addresses.
- Color target state has repeated slot layouts. Slot-specific copy/generator mistakes may affect only MRT slot 7, only high-address extension bits, or only compressed render targets using CMASK/FMASK/DCC.
- Address programming is split across low/high and base/extension registers. Partially updated CP, streamout, append, DB, GDS, color, CMASK, FMASK, or DCC addresses can point hardware at stale or wrong GPU memory.
- Compression metadata fields are tightly coupled. DCC, CMASK, FMASK, clear words, sample counts, fragment counts, tile modes, and block-size attributes must match the surface layout and metadata allocation.
- Counter and status fields are volatile. Low/high counter pairs can roll over between reads, and status/complete fields may be sticky, write-clear, or firmware-owned in ways not visible here.
- CP DMA, semaphore, coherency, append, and doorbell fields are ordering-sensitive. Wrong waits, cache policies, doorbell offsets, timeout values, or coherency controls can break queue progress and completion signaling.
- MES control registers are firmware-sensitive. Incorrect reset, halt, step, active-pipe, interrupt, cache-operation, or doorbell fields can interfere with scheduling firmware and be difficult to recover without a GPU reset.
- GDS atomic/resource fields and ordered-append counters can corrupt synchronization or append/consume behavior if field widths or operation modes are decoded incorrectly.
- GUS arbitration and credit values can produce performance cliffs, starvation, deadlocks, or subtle latency regressions if programmed outside documented safe ranges.
- `RESERVED`, `UNUSED`, and `OBSOLETE` fields appear in the range. Callers should preserve reserved bits unless an ASIC-specific table explicitly requires a value.

## Test Signals

Useful validation is mostly build-time, generator-level, and hardware-integration oriented:

- Build AMDGPU and AMDKFD configurations that include GC 10.3.0 support; missing, renamed, or malformed macros should surface in GFX10.3, KFD, MES, CP, GDS, and register-table consumers.
- Mechanically verify that complete registers in this range have expected `__SHIFT`/`_MASK` pairs, non-overlapping masks, and matching offsets/defaults in `gc_10_3_0_offset.h` and `gc_10_3_0_default.h`. Account for the partial start and partial end registers.
- Compare repeated `CB_COLOR0` through `CB_COLOR7` extended base and attribute groups for intentional slot-number-only differences.
- Exercise graphics workloads using multiple render targets, high GPU addresses, DCC/CMASK/FMASK compression, fast clears, MSAA, blending, streamout, primitive counters, pipeline statistics, occlusion/zpass counters, and indirect draw/dispatch.
- Exercise CP synchronization paths: EOP events, streamout completion, append/fence updates, scratch register access, CP DMA copies, memory-controller read/write windows, semaphores, wait-reg-mem timeout behavior, coherency waits, and doorbell buffers.
- Run MES-focused boot, queue scheduling, preemption, reset/recovery, interrupt, and debug-register tests on GC 10.3 hardware.
- Run GDS atomic, ordered-append, GWS resource, and OA counter workloads to validate `GDS_*` field behavior.
- Validate GUS programming with golden-register initialization, stress workloads with mixed IO/DRAM traffic, and performance counters or register dumps that show tag/credit and VC-priority behavior.
- Watch for GPU hangs, false completion, semaphore timeouts, bad fence values, corrupted render targets, metadata decompression failures, bad primitive/query counters, MES scheduling failures, GDS atomic errors, and workload-specific performance regressions.

## Chunk Notes For Merge

This document intentionally covers only lines 24802-27455 of `gc_10_3_0_sh_mask.h`. The previous chunk must supply the beginning of the `CB_COLOR6_CLEAR_WORD1` context, and the next chunk must complete `GUS_SDP_TAG_RESERVE1` with `VC7_MASK` before continuing into `GUS_SDP_VCC_RESERVE0` and later GUS credit-reserve fields. The final per-file report should treat the whole source as generated AMD GC 10.3.0 register field metadata consumed by AMDGPU/AMDKFD, not as handwritten runtime logic.

### subset-b-002487: lines 27456-30093

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 27456-30093

## Scope

This chunk is a generated AMDGPU ASIC register bitfield header slice for GC 10.3.0. It covers the tail of a GUS SDP tag-reserve register, the remaining GUS/GL1/CH/GL2 control and status fields in this region, a large set of graphics-core performance counter data registers, VM L2 and SDMA performance counter data registers, and the beginning of the performance-counter selector block through `SQ_PERFCOUNTER15_SELECT`.

The source is declarative C preprocessor data only. It exports `*_SHIFT` and `*_MASK` constants used by AMDGPU register access helpers to encode and decode fields in MMIO register values.

## Purpose

The definitions in this chunk let AMDGPU code manipulate individual fields in GC 10.3.0 registers without hard-coding bit positions at call sites. The covered registers fall into several functional groups:

- GUS/SDP fabric credits, request policy, latency sampling, error status, L1 traffic counters, floating-point atomic logging, and write-response FIFO thresholding.
- GL1/CH/GL2 cache and channel control, arbitration status, burst/pipe steering, invalidation/reset controls, metadata/compression behavior, address match controls, and load-balance counters.
- Performance counter readback registers for command processor, GRBM, geometry, primitive assembly, shader processor, shader queue, texture/cache, color/depth, RLC, RMI, UTCL, GCR, SDMA, and VM L2 blocks.
- Performance counter select/control registers that choose events, counter modes, SPM modes, latency stat indexes, draw windows, and busy-mask qualification for the same hardware blocks.

## Important Exports

This chunk contributes 2,119 `#define` entries. Each register field follows the local generated naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit index.
- `<REGISTER>__<FIELD>_MASK` gives the already-shifted field mask.

Representative control/status exports include:

- `GUS_SDP_VCC_RESERVE0/1` and `GUS_SDP_VCD_RESERVE0/1`: 6-bit virtual-channel credit reservations, with `DISTRIBUTE_POOL` in the `*_RESERVE1` registers.
- `GUS_SDP_REQ_CNTL`: request pass-predicate overrides for reads, writes, atomics, DRAM chaining, and inner-domain mode.
- `GUS_MISC`, `GUS_MISC2`, `GUS_MISC3`: arbitration priority, link manager timing, early SDP behavior, L1/perf masks, FP atomic enable/logging, and clock-gating related bits.
- `GUS_LATENCY_SAMPLING` and `GUS_ERR_STATUS`: sampler selection for DRAM/IO/read/write/atomic/VC traffic and SDP response/error status bits including clear and busy-on-error controls.
- `GL1C_STATUS`, `GL1C_UTCL0_CNTL2`, `GL1C_UTCL0_STATUS`, `GL1C_UTCL0_RETRY`: GL1 cache/UTCL status, fault/retry/PRT detection, invalidation, snoop, page-size, and clock-gating controls.
- `CH_ARB_CTRL`, `CH_DRAM_BURST_CTRL`, `CHC_CTRL`, `CHC_STATUS`, `CHCG_CTRL`, `CHCG_STATUS`: channel arbitration, burst gathering controls, cache/client controls, protection fault handling, and status.
- `GL2C_CTRL`, `GL2C_CTRL2`, `GL2C_WBINVL2`, `GL2C_SOFT_RESET`, `GL2C_CM_CTRL1`: GL2 cache/coherency, writeback/invalidate completion, reset halting, compression/metadata, prefetch, arbitration, and volatile-mode controls.
- `GL2_PIPE_STEER_0/1`, `GL1_PIPE_STEER`, `CH_PIPE_STEER`: pipe-to-channel steering bitfields.

Representative performance counter exports include:

- `*_PERFCOUNTER*_LO` and `*_PERFCOUNTER*_HI` readback registers across CP (`CPG`, `CPC`, `CPF`), `GRBM`, `GE1`, `GE2_DIST`, `GE2_SE`, `PA_SU`, `PA_SC`, `SPI`, `SQ`, `SX`, `GCEA`, `GDS`, `TA`, `TD`, `TCP`, `GL2C`, `GL2A`, `GL1C`, `CHC`, `CHCG`, `CB`, `DB`, `RLC`, `RMI`, `UTCL1`, `GCR`, `PA_PH`, `GL1A`, `CHA`, and `GUS`.
- `GCMC_VM_L2_PERFCOUNTER_*`, `GCUTCL2_PERFCOUNTER_*`, and `GCVML2_PERFCOUNTER2_*` for VM L2 performance readback.
- `SDMA0` through `SDMA3` `PERFCNT_PERFCOUNTER_*` and `PERFCOUNTER0/1_*` readback registers.
- `CPG/CPC/CPF_*_SELECT`, `GRBM_*_SELECT`, `GE1/GE2_*_SELECT`, `PA_SU/PA_SC_*_SELECT`, `SPI_*_SELECT`, and `SQ_PERFCOUNTER0_SELECT` through the `SQ_PERFCOUNTER15_SELECT` marker for selecting counted events and modes.

## Address Blocks And Boundaries

The chunk starts at line 27456 inside the previous GUS group with only `GUS_SDP_TAG_RESERVE1__VC7_MASK`; the corresponding comment and other fields are in the previous chunk. It then defines 48 additional GUS registers before explicit address blocks begin.

Address blocks visible in this chunk:

- `gc_gl1dec`: 7 GL1/GL1C registers.
- `gc_chdec`: 12 CH/CHA/CHC/CHCG registers.
- `gc_gl2dec`: 23 GL2C/GL2A pipe, address-match, cache, reset, and load-balance registers.
- `gc_perfddec`: 267 performance-counter data/readback registers.
- `gc_gcvml2prdec`: 4 VM L2/UTCL2 performance readback registers.
- `gc_gcvml2perfddec`: 4 additional GCVML2 performance counter data registers.
- `gc_sdma0_sdma0perfddec`, `gc_sdma1_sdma1perfddec`, `gc_sdma2_sdma2perfddec`, `gc_sdma3_sdma3perfddec`: 6 performance readback registers per SDMA engine.
- `gc_perfsdec`: 97 performance selector/control registers in this slice, ending at the `SQ_PERFCOUNTER15_SELECT` comment on line 30093.

The chunk ends before the `SQ_PERFCOUNTER15_SELECT` field macros, which begin on line 30094, and before `SQ_PERFCOUNTER_CTRL`. A merge pass must treat `SQ_PERFCOUNTER15_SELECT` as split across chunks.

## Control Flow

There is no runtime control flow in this header. Control flow is imposed by external AMDGPU code that:

1. Reads or constructs a 32-bit register value.
2. Uses `FIELD_PREP`, `REG_SET_FIELD`, `REG_GET_FIELD`, or equivalent AMDGPU bitfield helpers with these masks and shifts.
3. Writes the encoded value to a GC 10.3.0 MMIO register or decodes readback/status/performance data.

For counters, a common external flow is: program a `*_SELECT` register, enable/control the perfmon state, sample or stop the counter, then read paired `*_LO`/`*_HI` values. For cache and fabric controls, external flows typically program policy bits, poll status bits such as busy/done/fault flags, and issue clear/reset/invalidate operations.

## State And Persistence

The header itself has no persistent state. The state represented by these constants lives in hardware registers:

- Control registers such as `GUS_MISC`, `GL2C_CTRL`, `CHC_CTRL`, and `CP_PERFMON_CNTL` persist in GPU hardware until reset, power transitions, firmware programming, or driver reconfiguration.
- Status and error registers such as `GUS_ERR_STATUS`, `GL1C_STATUS`, and `CHC_STATUS` expose transient or sticky hardware state; some include explicit clear bits.
- Counter registers expose sampled hardware counters. Their values depend on counter-selection programming, perfmon enable state, reset/clear operations, and the hardware block being measured.
- Address-match and pipe-steering registers affect hardware routing/filter behavior and can change the meaning of later memory/cache traffic.

Because these are pure macros, no software state is allocated, reference-counted, locked, or serialized here.

## Dependencies

This chunk depends on the broader generated AMDGPU register ecosystem:

- Companion GC 10.3.0 address headers provide register offsets; this file only provides field masks and shifts.
- AMDGPU register helper macros/functions consume the `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` naming convention.
- The definitions are ASIC-specific and must match the GC 10.3.0 hardware spec and firmware expectations.
- No C includes appear in this file before the chunk; the only top-level structure is the include guard `_gc_10_3_0_SH_MASK_HEADER`.

## Integration Points

Likely consumers include AMDGPU initialization, debugfs/perfmon, RLC/firmware setup, VM/cache management, performance monitoring, and diagnostic paths under `drivers/gpu/drm/amd/`. Integration is by macro name, so compile-time breakage is immediate if a consumer references a missing or renamed field.

The performance-counter data and selector definitions integrate especially with code that exposes GPU metrics, configures streaming performance monitor modes, filters draw windows, or reads block-local counters for profiling. Cache/fabric definitions integrate with low-level GPU bring-up, reset, coherency, flush/invalidate, and error-reporting paths.

## Risks

- Incorrect mask/shift values can silently program wrong hardware bits, causing cache coherency failures, bad performance data, hangs, or misreported faults.
- Split chunk boundaries are risky: this chunk includes only the mask for `GUS_SDP_TAG_RESERVE1__VC7` and only the comment for `SQ_PERFCOUNTER15_SELECT`; the adjacent chunks are required for complete register-level research.
- Many register families are repetitive. Mechanical edits can accidentally change one instance while leaving related engines or counters inconsistent.
- Several fields control reset, invalidation, coherency, protection fault, prefetch, volatile, and atomic behavior; misuse by consumers can affect correctness, not only metrics.
- Counter high registers sometimes contain both counter bits and compare values, for example `*_PERFCOUNTER_HI__COUNTER_HI` plus `COMPARE_VALUE`; consumers must not assume every high register is a plain 32-bit extension.

## Test Signals

Useful validation signals for this chunk are compile-time and hardware-facing:

- Build the AMDGPU driver with GC 10.3.0 support and treat undefined macro references or duplicate definitions as failures.
- Compare generated masks and shifts against the authoritative GC 10.3.0 register database used to generate the header.
- Exercise perfmon/debugfs paths that program `*_SELECT` registers and read `*_LO`/`*_HI` counter pairs across CP, GRBM, SPI, SQ, SDMA, VM L2, GL1/GL2, CB/DB, and RLC/RMI blocks.
- Run cache/VM stress tests that trigger GL1/GL2 invalidation, VM fault/retry reporting, SDMA traffic, and graphics workloads while checking for GPU hangs or fault-status regressions.
- For static checks, verify paired field definitions have coherent masks and shifts and that adjacent chunks complete the split `GUS_SDP_TAG_RESERVE1` and `SQ_PERFCOUNTER15_SELECT` definitions.

### subset-b-002488: lines 30094-32558

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 30094-32558

## Purpose

This chunk is a middle slice of AMD's generated GC 10.3.0 shift/mask register-field header. It contains no executable C logic; it exports preprocessor constants that describe bit positions and masks for graphics core MMIO register fields. Driver code combines these constants with the companion GC 10.3.0 offset header to pack, unpack, and update individual fields through AMDGPU register helper macros.

The requested range contains 2,149 `#define` entries: 1,080 `__SHIFT` macros and 1,069 `_MASK` macros. The imbalance is an artificial chunk-boundary artifact: this slice ends after the first eleven `RLC_PG_CNTL` shift definitions, while the remaining `RLC_PG_CNTL` shifts and all `RLC_PG_CNTL` masks continue after line 32558.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU hardware metadata for GC/GFX blocks. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, allocation paths, or locks in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the bit offset used when constructing or decoding a register value.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate, clear, or preserve that field during register reads and writes.

The major register families in this range are:

- Shader/graphics-block performance counters: `SQ_PERFCOUNTER_CTRL`, `SQ_PERFCOUNTER_CTRL2`, and repeated `*_PERFCOUNTER*_SELECT`, `*_SELECT1`, `*_MODE`, `*_CFG`, and `*_RSLT_CNTL` families for `GCEA`, `SX`, `GDS`, `TA`, `TD`, `TCP`, `GL2C`, `GL2A`, `GL1C`, `CHC`, `CHCG`, `CB`, `DB`, `RMI`, `GCR`, `UTCL1`, `PA_PH`, `GL1A`, `CHA`, and `GUS`.
- Color/depth block filtering: `CB_PERFCOUNTER_FILTER` provides per-shader-engine/shader-array and windowing fields used to constrain CB performance-counter collection.
- RLC streaming performance monitor and accumulator control: `RLC_SPM_PERFMON_CNTL`, ring base high/low, ring size, segment sizes, ring read/write pointers, mux-select address/data registers, skew/sample-delay controls, accumulator data/control RAM address/data windows, `RLC_SPM_ACCUM_STATUS`, `RLC_SPM_ACCUM_CTRL`, `RLC_SPM_ACCUM_MODE`, thresholds, requested sample counts, 32-bit counter regions, virtualization pause/status, and GFX clock high/low counters.
- RLC perfmon and IOV performance plumbing: `RLC_PERFMON_CNTL`, `RLC_PERFCOUNTER[0-1]_SELECT`, `RLC_GPU_IOV_PERF_CNT_*`, and `RLC_PERFMON_CLK_CNTL`.
- VM L2 and GC UTCL2 performance counters under `addressBlock: gc_gcvml2pldec`: `GCMC_VM_L2_PERFCOUNTER[0-7]_CFG`, `GCMC_VM_L2_PERFCOUNTER_RSLT_CNTL`, `GCUTCL2_PERFCOUNTER[0-3]_CFG`, and `GCUTCL2_PERFCOUNTER_RSLT_CNTL`.
- GCVML2 perfs decoder fields under `addressBlock: gc_gcvml2perfsdec`: `GCVML2_PERFCOUNTER2_[0-1]_SELECT`, matching `SELECT1`, and `MODE` registers.
- Four SDMA performance-counter blocks under `gc_sdma0_sdma0perfsdec` through `gc_sdma3_sdma3perfsdec`: each has `SDMAx_PERFCNT_PERFCOUNTER[0-1]_CFG`, result control, misc control, and repeated `SDMAx_PERFCOUNTER[0-1]_SELECT/SELECT1` fields.
- RTAVFS control under `addressBlock: gc_grtavfsdec`: register address/data windows, read data, control/status, target frequency/voltage, soft reset, PSM control, and clock control.
- RLC core control under `addressBlock: gc_rlcdec`: `RLC_CNTL`, F32 microcode version, busy/status bits, memory sleep control, SMU/RLCV safe-mode handshakes, RLCV command, reference-clock timestamp, GPM timers, legacy interrupts, CP/RLC interrupt status, load-balance counters/control, MGCG control, GPU clock counters, GPM thread reset, CP DMA completion bits, RLCG doorbell control/status/data, CGTT/MGCG override, 32-bit GPU clock select/value, and the beginning of `RLC_PG_CNTL`.

## Control Flow

This header has no runtime control flow. It participates in runtime behavior through generated register access patterns:

1. GC 10.3.0-capable AMDGPU code includes `gc_10_3_0_offset.h` and this shift/mask header.
2. Register table macros and helper calls token-paste register and field names into offset, shift, and mask constants.
3. Runtime code reads or writes GC MMIO registers using helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, and block-specific wrappers.
4. Hardware-side sequencing is handled by consumers, not by this header: consumers must program counter selectors before enabling counters, configure SPM rings before sampling, poll status before consuming results, clear interrupt bits with the right semantics, and coordinate RLC/SMU/power-management handshakes with the relevant clocks and power domains active.

The chunk therefore describes field layout, not policy. It does not encode which registers are read-only, write-one-to-clear, self-clearing, privileged, clock-gated, or safe to access only in a particular IP state.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes hardware state in GC 10.3.0 registers:

- Performance-counter selection state, including event selectors, selector banks, counter modes, performance modes, compare modes/values, enable bits, clear bits, start/stop triggers, and saturation behavior.
- Shader-stage and pipe gating for SQ counters via `SQ_PERFCOUNTER_CTRL`, including per-stage enables for PS/VS/GS/ES/HS/LS/CS, counter rate, flush behavior, and per-ME/pipe disable bits.
- SPM ring and accumulator state, including ring base/size/read/write pointers, per-SE/global segment sizing, mux selector RAM windows, sample-delay/skew fields, accumulated sample counts, done/overflow/armed/in-progress bits, strobe controls, automatic accumulation/SPM modes, and virtualization pause status.
- VM L2, UTCL2, GCVML2, and SDMA performance-counter configuration and result-control state.
- RTAVFS state for indirect register access, target frequency/voltage, reset, PSM, and clock-control behavior.
- RLC firmware and control state, including enable/step/cache-disable bits, F32 thread microcode versions, busy flags, memory light/deep sleep timing, SMU/RLCV safe-mode command/response fields, timestamps, timers, load-balance counters, MGCG settings, clock counters, thread reset, CP DMA completion flags, doorbell mode/data/status, CGTT/MGCG overrides, and early power-gating fields.

Persistence is hardware-defined. Configuration fields usually persist until driver reprogramming, power-gating, suspend/resume, GPU reset, or ASIC reset. Status and interrupt fields may be transient, sticky, sampled, self-clearing, or write-one-to-clear depending on the underlying register. The generated shift/mask header does not document those access semantics.

## Dependencies And Integration Points

This chunk must remain synchronized with AMD's generated GC 10.3.0 register database and with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h`, which supplies the matching MMIO offsets.

Direct include users in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`, which includes the GC 10.3.0 offset and shift/mask headers for SMU/power-management interactions on VanGogh-class hardware.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.c`, which includes this shift/mask header for shared SDMA register-field handling.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c`, which includes GC 10.3.0 offsets and masks for KFD/GFX v10.3 integration.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c`, which includes GC 10.3.0 register metadata for SDMA v5.2 programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c`, which includes GC 10.3.0 metadata for GFXHUB/VM-related register access.

The strongest behavioral integration points for this specific chunk are GPU profiling/performance monitoring, SDMA performance-counter programming, VM/GFXHUB performance diagnostics, RLC SPM capture, RLC firmware/status polling, RLC/SMU power-management handshakes, clock/power-gating control, and RLCG doorbell handling.

## Risks And Edge Cases

- These constants are untyped preprocessor values. A wrong shift or mask can compile cleanly while touching the wrong MMIO bits, corrupting adjacent fields, missing interrupts, breaking power management, or producing invalid performance data.
- The file is generated metadata. Manual edits can diverge from AMD's authoritative register database, the matching offset header, firmware expectations, and ASIC documentation.
- Repeated perf-counter families are easy to validate incompletely. `SDMA0` working does not prove `SDMA1-3`; one `GL2*`/`GL1*`/`CH*` instance can carry a generator error while sibling blocks appear correct.
- Counter fields have width and mode differences. Some selectors carry four events through `SELECT`/`SELECT1`, while other counters expose fewer selector fields; generic setup code must not assume every block has the same arity.
- SPM and accumulator controls are sequencing-sensitive. Starting sampling before the ring base/size, segment sizes, mux selectors, delays, and accumulator mode are coherent can produce overflows, stale samples, bad write pointers, or stuck in-progress status.
- RLC control, safe-mode, timer, interrupt-clear, thread-reset, and power-gating fields may have side effects. Using masks without respecting required handshakes can hang RLC firmware, race SMU coordination, lose timer interrupts, or destabilize clock/power transitions.
- Doorbell and indirect data registers carry full 32-bit payloads. Incorrect low/high ordering or stale valid bits can mis-handle RLCG messages.
- The chunk ends inside `RLC_PG_CNTL`; any per-file merge must join the next chunk before making complete claims about RLC power-gating fields.

## Test Signals

Useful validation combines generated-header checks with hardware behavior:

- Build AMDGPU with GC 10.3.0, SDMA v5.2, GFXHUB v2.1, KFD GFX v10.3, and VanGogh SMU paths enabled. Missing or renamed macros should fail at compile time in direct include users and any register-table construction that references these fields.
- Mechanically verify that every field in lines 30094-32558 has a matching `__SHIFT` and `_MASK` pair where expected, while allowing the known chunk-boundary exception for the partial `RLC_PG_CNTL` group.
- Diff this range against AMD's authoritative GC 10.3.0 register database and neighboring generated GC/GFX10 headers where layouts are expected to match.
- Exercise GPU performance monitoring through perf/debug tooling on GC 10.3.0 hardware, covering SQ stage enables, CB/DB filters, GL1/GL2/cache counters, VM L2/UTCL2 counters, and counter start/stop/clear/saturation behavior.
- Exercise SDMA performance counters on all four SDMA instances, not only SDMA0, and compare selected events with expected DMA workload changes.
- Validate RLC SPM capture by programming ring base/size, segment sizing, mux selectors, sample intervals, accumulator mode, and then checking write-pointer movement, sample counts, done bits, overflow bits, and pause/resume behavior.
- Run suspend/resume, GPU reset, clock-gating, power-gating, and SMU/RLC safe-mode paths while watching for RLC busy bits that never clear, timer/interrupt storms, bad load-balance counters, broken doorbell status, or power-gating regressions.

## Cross-Chunk Notes

This slice starts immediately after the `SQ_PERFCOUNTER15_SELECT` group began in an earlier chunk and ends inside `RLC_PG_CNTL`. The final per-file research document should merge adjacent chunks before making whole-file claims about all SQ performance-counter selectors or the complete RLC power-gating register layout.

### subset-b-002489: lines 32559-35036

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 32559-35036

## Purpose

This chunk is generated AMD GC 10.3.0 register field metadata. It contains no executable C logic; it exports preprocessor constants for bit shifts and bit masks used to compose, read, and update fields inside Graphics Core MMIO registers. Consumers pair this file with the matching GC 10.3.0 offset header and AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

The requested range starts in the `RLC_PG_CNTL` field definitions and then covers a large RunList Controller / RunList Compute (`RLC`) region, two RLC decode address blocks (`gc_rlcrdec` and `gc_rlcsdec`), and the beginning of the GC power decoder (`gc_pwrdec`) clock-gating controls. Although the source tree path is under `ceph-client`, this file is AMDGPU hardware metadata, not distributed filesystem code.

Major hardware themes in this range are:

- RLC graphics power gating, clock gating, low-bandwidth power, SMU handshakes, GPM thread controls, and WGP status/request fields.
- RLC firmware-facing general-purpose, safe-mode, scheduler, scratch, semaphore, interrupt, doorbell, PACE timer, SPM, SPP, SRM, UTCL1, and prewalker controls.
- RLC RLCS decode/status registers for bootload status, power-state sequencing, load-balancing status, interrupt-handling metadata, GRBM idle/busy state, SDMA busy changes, virtualization/IOV status, UTCL2 overrides, SMU voltage-change handshakes, and KMD logging.
- GC power clock-gating controls for CGTS status and CGTT blocks including SPI, PC, BCI, VGT, IA, WD, GS/NGG, PA, and SC clock domains. The chunk ends inside `CGTT_SC_CLK_CTRL1`; the next chunk is needed for the rest of the power decoder block.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or local includes in this slice. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a field inside a 32-bit register.
- `<REGISTER>__<FIELD>_MASK`: field mask for preserving, clearing, or extracting that field.

Important register families covered by the chunk:

- `RLC_PG_CNTL`, `RLC_DYN_PG_STATUS`, `RLC_DYN_PG_REQUEST`, `RLC_PG_DELAY`, `RLC_STATIC_PG_STATUS`, `RLC_PG_DELAY_3`, `RLC_PG_ALWAYS_ON_WGP_MASK`, `RLC_MAX_PG_WGP`, `RLC_AUTO_PG_CTRL`, and `RLC_LB_*`: graphics and per-WGP power-gating policy, delays, masks, load-balancing parameters, and status.
- `RLC_CGCG_CGLS_CTRL`, `RLC_CGCG_RAMP_CTRL`, `RLC_CGCG_CGLS_CTRL_3D`, and `RLC_CGCG_RAMP_CTRL_3D`: coarse-grain clock gating and clock-gating light sleep enablement, idle thresholds, compensation delays, sleep modes, and ramp timing.
- `RLC_GPM_THREAD_PRIORITY`, `RLC_GPM_THREAD_ENABLE`, `RLC_GPM_GENERAL_0` through `RLC_GPM_GENERAL_16`, `RLC_GPM_INT_*`, and `RLC_GPM_LOG_*`: RLC GPM microcontroller thread enablement, priority, scratch/general registers, logging, interrupt masking, forcing, and status.
- `RLC_SPM_*`, `RLC_SPP_*`, and `RLC_SPM_THREAD_TRACE_CTRL`: streaming/performance monitor controls, memory-client attributes, sample counts, shader/power profiling, PVT counters, SSF capture, CAM access, and reset/status fields.
- `RLC_SRM_*`, `RLC_SRM_INDEX_CNTL_ADDR_*`, and `RLC_SRM_INDEX_CNTL_DATA_*`: SRM command queues, indexed control addresses/data, FIFO status, busy state, and abort fields.
- `RLC_RLCG_*`, `RLC_RLCV_*`, `RLC_RLCP_*`, and `RLC_XT_*` doorbell ranges, controls, status, and data registers: doorbell range bounds, mode selection, doorbell IDs, valid bits, and 64-bit data payload halves for several RLC clients.
- `RLC_GPM_UTCL1_*`, `RLC_SPM_UTCL1_*`, `RLC_PREWALKER_UTCL1_*`, `RLC_UTCL1_STATUS`, and UTCL1 error registers: translation retry timers, drop/bypass/invalidate controls, transaction-stall/busy status, prewalker trigger and address/size fields, and translated request error VMID/address reporting.
- `RLC_RLCS_*`: RLCS decode block fields for power, clock, boot, IOV, interrupt, GRBM idle/busy, CP/SPM interrupt info, IH packet metadata, WGP state, bootload ID loaded bits, power brake, UTCL2 overrides, and SMU/MP1 handshakes.
- `CGTS_*` and `CGTT_*`: power decoder readback, TCC disable/status, and clock-control fields. Common CGTT patterns include `ON_DELAY`, `OFF_HYSTERESIS`, `SOFT_STALL_OVERRIDE*`, `SOFT_OVERRIDE*`, `GRP*_OVERRIDE`, domain-specific core override bits, and `REG_OVERRIDE`.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU graphics and power-management code:

1. GC 10.3 consumers include `gc_10_3_0_sh_mask.h` with `gc_10_3_0_offset.h`.
2. Driver code reads a GC register through the SOC15 helpers, clears or sets masks from this header, and writes the result back. Field helpers also use the `__SHIFT` and `_MASK` definitions to update individual fields.
3. Power-management paths program `RLC_PG_CNTL`, `RLC_CGCG_CGLS_CTRL`, and `RLC_CGCG_CGLS_CTRL_3D` around power-gating and clock-gating transitions. The same mask names are used in nearby GC generations, and GC 10.x code uses this exact header for GC 10.3 hardware.
4. Firmware/load paths poll status fields such as `RLC_RLCS_BOOTLOAD_STATUS__BOOTLOAD_COMPLETE_MASK` after RLC firmware setup, and interrupt paths use the RLCS, SPM, GPM, PACE, and doorbell fields to report or acknowledge hardware events.
5. Golden-register programming and low-power setup code use the `CGTT_*` fields and whole-register masks to tune clock gating for individual graphics blocks.

The macros do not encode required ordering. Callers must still sequence firmware loading, safe mode, SMU handshakes, power-gating enables, idle waits, interrupt clear/ack operations, and suspend/resume restore ordering correctly.

## State And Persistence Behavior

This chunk stores no software state and performs no persistence. It describes MMIO-backed hardware state.

The represented state includes:

- Persistent configuration until reset or power transition: RLC power-gating policy, CGCG/CGLS enables and thresholds, thread enables/priorities, memory-client attributes, SRM controls, doorbell ranges, SPP/SPM profiling controls, UTCL1/UTCL2 behavior, and CGTT clock-gating override values.
- Volatile status and counters: WGP work pending and power status, load-balancing counters, RLC clock-valid/busy state, UTCL1 fault/retry/PRT and busy/stall bits, RLCS bootload status, GRBM/SDMA idle-busy status, PVT counters, GPU clock counters, and CGTS status/readback fields.
- Event and handshake state: spare interrupts, CP EOF interrupts, SPM/GPM/RLCS interrupt info and ack controls, PACE timers, doorbell valid/data fields, SMU message/argument/command fields, MP1/RLC doorbell control, SMUIO voltage-change request/ack fields, and power-brake status.

Some fields are likely read-only status bits, write-one-to-clear bits, sticky interrupt status, self-clearing command bits, or reserved fields. This header does not mark access direction or side effects; those semantics come from the ASIC register database and the consuming driver paths.

## Dependencies And Integration Points

This generated mask header must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h`, which defines the corresponding `mm...` register offsets.
- SOC15 GC base-address tables and register-access helpers used by AMDGPU.
- AMDGPU graphics, SDMA, GFXHUB, KFD, and SMU code that includes `gc/gc_10_3_0_sh_mask.h`.

Observed direct include sites for the exact GC 10.3.0 mask header include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`

Important cross-file consumers and patterns in the AMDGPU tree include GC 10.x graphics code that reads/writes `RLC_PG_CNTL`, sets `RLC_GPM_THREAD_ENABLE` bits, programs `RLC_CGCG_CGLS_CTRL` and `_3D`, polls `RLC_RLCS_BOOTLOAD_STATUS`, and applies golden values for `CGTT_*_CLK_CTRL` registers. Those consumers rely on this file's masks being bit-accurate for GC 10.3.0 silicon.

## Risks And Edge Cases

- Generated-mask drift is the main correctness risk. A wrong shift or mask compiles cleanly but can modify the wrong hardware field, especially where adjacent reserved bits surround power, interrupt, or command fields.
- Reserved bits must be preserved. Many registers expose large `RESERVED` masks; callers should read-modify-write targeted fields instead of writing arbitrary whole-register constants unless those constants are known golden settings.
- Power and clock controls are sequencing-sensitive. Misprogramming `RLC_PG_CNTL`, `RLC_CGCG_CGLS_CTRL`, `RLC_CGCG_RAMP_CTRL`, or `CGTT_*_CLK_CTRL` fields can cause hangs, wake failures, excessive power draw, broken suspend/resume, or intermittent failures only under idle/load transitions.
- Doorbell, interrupt, and command fields can have side effects. Incorrect ack/clear/mode/data handling in `RLC_*_DOORBELL_*`, `RLC_RLCS_*_INT_*`, `RLC_SPM_INT_*`, `RLC_GPM_INT_*`, PACE timer, SMU command, and safe-mode registers can lose events or wedge firmware communication.
- Firmware and boot status fields are ABI-like. Polling the wrong `RLC_RLCS_BOOTLOAD_STATUS` bit or misinterpreting bootload ID status can make firmware initialization appear complete too early or time out even when hardware is healthy.
- Virtualization and address-translation fields are security-sensitive. `RLC_RLCS_IOV_*`, UTCL1 error address/VMID fields, `RLC_RLCS_UTCL2_CNTL` GPA/VF overrides, and IH VF metadata must remain matched to the hardware generation to avoid incorrect fault attribution or isolation behavior.
- The chunk boundary is artificial. It begins after the start of `RLC_PG_CNTL` and ends inside `CGTT_SC_CLK_CTRL1`; adjacent research chunks are required for full-file reasoning.

## Test Signals

Useful validation signals for code that consumes this chunk are hardware and integration oriented:

- Kernel build coverage for GC 10.3 AMDGPU paths confirms macro names still match consumers.
- GPU initialization logs should show successful RLC firmware load and no timeout polling `RLC_RLCS_BOOTLOAD_STATUS__BOOTLOAD_COMPLETE`.
- Suspend/resume, runtime power management, and idle-to-load transitions should complete without GC/RLC hangs, SMU handshake errors, or GRBM idle timeout messages.
- Stress tests for graphics, compute, SDMA, and KFD workloads should not report UTCL1/UTCL2 translation errors, CP status invalidation storms, or doorbell/interrupt loss.
- Power telemetry should show expected clock-gating and power-gating behavior when CGCG/CGLS and CGTT golden settings are applied.
- Debugfs or driver diagnostics reading RLC/SPM/SPP/GPM status should report coherent busy, interrupt, profile, and counter values rather than stuck or impossible bit combinations.

### subset-b-002490: lines 35037-37447

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 35037-37447

## Scope

This chunk is generated AMD GC 10.3.0 register field metadata. It contains only C preprocessor constants: each hardware register field is represented by a `__SHIFT` macro and a matching `__MASK` macro. There are no functions, structs, enums, global variables, includes, locks, allocations, callbacks, or executable branches in this range.

The selected lines begin in the middle of `CGTT_SC_CLK_CTRL1`, then cover a large clock-gating control block, the `addressBlock: gc_hypdec` command-processor/RLC hypervisor decode block, all visible SDMA0 hypervisor decode field masks, and the start of the SDMA1 hypervisor decode block through `SDMA1_PUB_REG_TYPE1`. Although the repository path is under a `ceph-client` source tree, this is AMDGPU DRM hardware metadata and is unrelated to Ceph filesystem logic.

## Purpose

`gc_10_3_0_sh_mask.h` describes bit layouts for AMD GC 10.3.0 graphics registers. Driver code pairs these constants with register-address definitions from `gc_10_3_0_offset.h` and, where useful, default values from `gc_10_3_0_default.h`. The constants let AMDGPU code compose read-modify-write updates and decode register readbacks without embedding literal bit positions throughout the driver.

This chunk serves four main purposes:

- It defines clock-gating and clock-stall override fields for graphics sub-blocks such as SC, SQ, SQG, SX, TD, TA, TCPI/TCPF, GDS, DB, CB, GL2A/GL2C, CP/CPF/CPC, RLC, RMI, GCR, UTCL1, GCEA, CAC, GRBM, GUS, and PH.
- It defines command-processor hypervisor decode fields for firmware upload and instruction-cache base/control registers for PFP, ME, CE, CPC, MEC, and MES engines.
- It defines GRBM, RLC, interrupt-cookie, GPU IOV, reset, timer, scheduler, semaphore, scratch, firmware, and SDMA status fields used by virtualization and reset/recovery paths.
- It defines SDMA0 and SDMA1 hypervisor decode masks for microcode windows, VM context state, active VF/PF identity, virtual reset requests, VF enablement, context-save register classes, public register classes, and status/control/performance register grouping.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The important interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Comment lines such as `//CGTT_SQ_CLK_CTRL` and `// addressBlock: gc_hypdec` group macros by hardware register or address block.
- Consumers normally use these constants indirectly through AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, indexed-register accessors, golden-register tables, firmware loaders, reset code, and virtualization paths.

Major register families in this range:

- Clock gating controls: `CGTT_SC_CLK_CTRL1/2`, `CGTT_SQ_CLK_CTRL`, `CGTT_SQG_CLK_CTRL`, `SQ_ALU_CLK_CTRL`, `SQ_TEX_CLK_CTRL`, `SQ_LDS_CLK_CTRL`, `CGTT_SX_CLK_CTRL0` through `4`, `TD_CGTT_CTRL`, `TA_CGTT_CTRL`, `CGTT_TCPI_CLK_CTRL`, `CGTT_GDS_CLK_CTRL`, `DB_CGTT_CLK_CTRL_0`, `CB_CGTT_SCLK_CTRL`, `GL2C_CGTT_SCLK_CTRL`, `GL2A_CGTT_SCLK_CTRL`, `GL2A_CGTT_SCLK_CTRL_1`, `CGTT_CP_CLK_CTRL`, `CGTT_CPF_CLK_CTRL`, `CGTT_CPC_CLK_CTRL`, `CGTT_RLC_CLK_CTRL`, `RMI_CGTT_SCLK_CTRL`, `CGTT_TCPF_CLK_CTRL`, `GCR_CGTT_SCLK_CTRL`, `UTCL1_CGTT_CLK_CTRL`, `GCEA_CGTT_CLK_CTRL`, `SE_CAC_CGTT_CLK_CTRL`, `GC_CAC_CGTT_CLK_CTRL`, `GRBM_CGTT_CLK_CNTL`, `GUS_CGTT_CLK_CTRL`, and `CGTT_PH_CLK_CTRL0` through `3`. These use repeated `ON_DELAY`, `OFF_HYSTERESIS`, `SOFT_STALL_OVERRIDE*`, `SOFT_OVERRIDE*`, block-specific override, performance-monitor override, dynamic override, and register-clock override fields.
- Shader/WGP force-on controls: `SQ_ALU_CLK_CTRL`, `SQ_TEX_CLK_CTRL`, and `SQ_LDS_CLK_CTRL` expose `FORCE_WGP_ON_SA0` and `FORCE_WGP_ON_SA1` masks, allowing per-shader-array WGP clock behavior to be forced for ALU, texture, and LDS units.
- Command processor firmware and instruction-cache fields: `CP_HYP_*_UCODE_ADDR/DATA`, non-hypervisor `CP_*_UCODE_ADDR/DATA`, `CP_ME_RAM_RADDR/WADDR/DATA`, `CP_PFP/ME/CE/CPC/MES_IC_BASE_LO/HI/CNTL`, and `CP_*_IC_OP_CNTL` fields cover microcode address/data windows, instruction-cache base address windows, VMID selection, address clamping, execute-disable, cache policy, cache invalidation, and cache priming completion.
- MES memory-window fields: `CP_MES_MIBASE_*`, `CP_MES_MDBASE_*`, `CP_MES_LOCAL_BASE0_*`, `CP_MES_LOCAL_MASK0_*`, `CP_MES_LOCAL_APERTURE`, `CP_MES_MIBOUND_*`, and `CP_MES_MDBOUND_*` describe instruction/data/local aperture base, mask, and bound fields for MES-managed firmware memory.
- GRBM selection and remapping: `GFX_PIPE_PRIORITY`, `GRBM_GFX_INDEX_SR_SELECT/DATA`, `GRBM_GFX_CNTL_SR_SELECT/DATA`, `GRBM_CAM_INDEX`, `GRBM_HYP_CAM_INDEX`, `GRBM_CAM_DATA`, `GRBM_HYP_CAM_DATA`, `GRBM_CAM_DATA_UPPER`, `GRBM_HYP_CAM_DATA_UPPER`, and `GRBM_SE_REMAP_CNTL` expose pipe priority, selected shadow-register context, shader-engine/shader-array/instance targeting, broadcast controls, CAM remap address pairs, and per-SE remap enables for SE0 through SE7.
- RLC and GPU IOV controls: `RLC_GPU_IOV_VF_ENABLE`, `RLC_GPU_IOV_CFG_REG1/2/6/8`, `RLC_GPU_IOV_SCH_BLOCK`, `RLC_GPU_IOV_SCH_0` through `3`, `RLC_GPU_IOV_ACTIVE_FCN_ID`, `RLC_GPU_IOV_VM_BUSY_STATUS`, `RLC_GPU_IOV_VF_DOORBELL_STATUS` plus set/clear variants, `RLC_GPU_IOV_VF_MASK`, `RLC_GPU_IOV_INT_STAT`, `RLC_GPU_IOV_INT_DISABLE`, `RLC_GPU_IOV_INT_FORCE`, `RLC_GPU_IOV_SMU_RESPONSE`, `RLC_GPU_IOV_RLC_RESPONSE`, `RLC_GPU_IOV_VIRT_RESET_REQ`, `RLC_GPU_IOV_F32_CNTL`, and `RLC_GPU_IOV_F32_RESET` define VF enable/count, PF/VF active ID, scheduler commands, command status, context location/size/offset, VM busy state, doorbell state, interrupt routing, responses, reset requests, and F32 controls.
- RLC timers, reset, semaphores, and firmware windows: `RLC_RLCV_TIMER_INT_0/1`, `RLC_RLCV_TIMER_CTRL`, `RLC_RLCV_TIMER_STAT`, `RLC_PACE_TIMER_STAT`, `RLC_PACE_INT_FORCE`, `RLC_PACE_INT_CLEAR`, `RLC_HYP_SEMAPHORE_0` through `3`, `RLC_HYP_RESET_VECTOR`, `RLC_HYP_BOOTLOAD_SIZE`, `RLC_HYP_BOOTLOAD_ADDR_LO/HI`, `RLC_HYP_RLCG/RLCP/RLCV_UCODE_CHKSUM`, RLC GPM/PACE/GPU_IOV microcode address/data windows, RLCV/RLCP IRAM windows, SRM DRAM/ARAM windows, scratch windows, and GTS offset registers.
- SDMA status and hypervisor decode fields: RLC-level `RLC_SDMA0..3_STATUS` and `RLC_SDMA0..3_BUSY_STATUS`, GPU IOV `RLC_GPU_IOV_SDMA0..7_STATUS` and `BUSY_STATUS`, plus `addressBlock: gc_sdma0_sdma0hypdec` and `addressBlock: gc_sdma1_sdma1hypdec`.
- SDMA0/SDMA1 context and public register grouping: `SDMA0_CONTEXT_REG_TYPE0` through `3` and `SDMA1_CONTEXT_REG_TYPE0` through `3` enumerate ring-buffer, read/write pointer, write-pointer polling, IB, skip, context status, doorbell, CSA, preempt, AQL, minor pointer update, mid-command data, and reserved context classes. `SDMA0_PUB_REG_TYPE0` through `3` and visible `SDMA1_PUB_REG_TYPE0/1` enumerate microcode, VM, active function, context class, power, clock, control, status, atomic, UTCL1, performance, interrupt, scratch, timestamp, queue reset, and other public SDMA registers.

## Control Flow

This header has no runtime control flow. Runtime behavior is implied by driver users that include the generated register headers:

1. Select the correct register address from `gc_10_3_0_offset.h`, including the correct direct MMIO, indexed, hypervisor-decode, or SDMA-decode access path.
2. Read a current value or start from a default/golden value.
3. Use the `__MASK` and `__SHIFT` constants, usually through helper macros, to extract fields or compose an updated register value.
4. Write the value through the appropriate AMDGPU register accessor.
5. For command, reset, interrupt, firmware-load, or status fields, poll or wait on companion status bits in higher-level driver code.

The important sequencing is outside this file. Examples include enabling or overriding clock gates only during safe initialization or debug windows, loading CP/RLC/SDMA firmware through address/data registers in the expected order, invalidating or priming instruction caches before firmware execution, selecting GRBM shadow or CAM entries before data access, issuing GPU IOV scheduler commands and checking command status/responses, masking or clearing interrupts with the correct set/clear semantics, and coordinating SDMA context-save masks with preemption, FLR, suspend/resume, and reset recovery.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe fields in GPU hardware registers whose behavior is defined by the ASIC specification and the AMDGPU access sequence.

Clock-gating fields are hardware configuration state. Values may persist until graphics IP reset, function-level reset, suspend/resume reinitialization, power-gating loss, firmware reprogramming, or explicit driver writes. Fields named `ON_DELAY`, `OFF_HYSTERESIS`, `SOFT_STALL_OVERRIDE*`, and `SOFT_OVERRIDE*` influence whether sub-block clocks can gate, stall, or remain forced on.

Command-processor, RLC, and SDMA address/data windows are stateful hardware portals. The address register selects a firmware, RAM, IRAM, DRAM, ARAM, scratch, or context location, and subsequent data accesses operate on that selection. Incorrect interleaving between windows can corrupt firmware loading or diagnostics.

RLC/GPU IOV and SDMA virtualization fields include both durable configuration and volatile hardware-owned state. VF enable bits, active function IDs, scheduler configuration, context storage location, VM context bases, and doorbell masks are configuration. Status, busy, interrupt, response, timer, reset, checksum, and counter-like fields can change autonomously, be sticky, be write-one-to-clear, or be self-clearing depending on the register.

Reserved fields are part of the hardware ABI. This header exposes many `RESERVED`, `VOID_REG2`, and `RESERVED_FOR_PSPSMU_ACCESS_ONLY` masks; normal read-modify-write code should preserve them unless an ASIC programming guide, firmware contract, or golden-register table explicitly requires a value.

## Dependencies And Integration Points

This chunk depends on the rest of the generated GC 10.3.0 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h` supplies the matching register addresses for these field names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_default.h` supplies reset/default values for many registers in the same generated family.
- AMDGPU GFX v10.3 code consumes these macros through SOC15 register helpers, golden-register tables, firmware loading paths, clock-gating setup, RLC initialization, GPU reset code, SDMA setup, and SR-IOV virtualization paths.
- CP/PFP/ME/CE/CPC/MEC/MES fields integrate with command processor firmware loading, instruction cache setup, MES firmware memory windows, queue management, and compute/graphics scheduling.
- RLC GPU IOV fields integrate with PF/VF scheduling, active function tracking, virtual function enablement, doorbell delivery, FLR handling, VM busy tracking, SMU/RLC response handshakes, interrupt routing, and context storage.
- SDMA0/SDMA1 fields integrate with DMA ring setup, VM context setup, microcode loading, SDMA public/status registers, AQL and IB handling, context save/restore, preemption, queue reset, and SDMA performance/status diagnostics.
- GRBM and SE remap fields integrate with instance-targeted register writes, shader-engine remapping, CAM table programming, broadcast write behavior, and debugging or virtualization control over per-engine state.

## Risks And Edge Cases

- Generated-header drift is high impact. A wrong mask or shift can compile cleanly while changing the wrong hardware bit in low-level graphics, firmware, reset, power, or virtualization paths.
- This chunk starts mid-`CGTT_SC_CLK_CTRL1` and ends mid-SDMA1 public-register coverage. Adjacent chunks are required for complete per-file conclusions about those register families.
- Clock-gating override fields can hide timing or power bugs. Forcing clocks on may improve debug stability but change power/performance behavior; forcing stalls or disabling gates at the wrong time can hang or throttle workloads.
- Address/data windows are order-sensitive. CP, RLC, and SDMA microcode, RAM, scratch, and IRAM/DRAM/ARAM windows rely on the selected address state; concurrent or misordered access can write plausible values to the wrong hardware location.
- Virtualization fields are security and isolation sensitive. Bad VF enablement, active function ID, doorbell status/mask, VM context, scheduler command, context storage, or FLR state can affect the wrong PF/VF or break isolation.
- Status, interrupt, reset, and response fields may have access semantics not visible here. Names like `STATUS`, `INT_CLEAR`, `SET`, `CLR`, `RESET_REQ`, `RESP`, `CHECKSUM`, and `BUSY_STATUS` are not enough to infer whether reads are destructive, writes are pulse-like, bits are sticky, or polling requires timeouts.
- SDMA context-register type masks must match the hardware context-save contract. Missing a ring pointer, IB field, CSA address, doorbell, preempt field, mid-command register, AQL register, or pointer-poll address can break preemption, reset, suspend/resume, or SR-IOV scheduling.
- Repeated SDMA0/SDMA1 register families invite copy/paste mistakes. The names are nearly symmetric, but using SDMA0 masks with SDMA1 addresses, or vice versa, can silently target the wrong engine.
- Reserved and PSPSMU-only fields must be preserved. Full-register writes that overwrite these bits can trigger undocumented behavior or conflict with firmware-owned state.
- GRBM broadcast and remap fields have wide blast radius. A bad instance index, SE/SA index, broadcast-write bit, or SE remap value can program only one instance, all instances, or the wrong physical shader engine.

## Test Signals

Useful validation is mostly build, generated-data consistency, and hardware integration:

- Kernel build coverage for AMDGPU files that include `gc_10_3_0_sh_mask.h`, especially GFX v10.3, RLC, SDMA, reset, SR-IOV, firmware loading, and golden-register paths.
- Static generated-header checks that every mask aligns with its shift, fields within a register do not overlap except for intentional full-width masks, and every register in this chunk has matching offset/default entries where expected.
- Cross-generation consistency checks against AMD's authoritative GC 10.3.0 register database, especially for repeated clock-gating, SDMA0/SDMA1, RLC GPU IOV, and CP firmware/cache families.
- Boot and ring tests on GC 10.3 hardware covering CP firmware load, RLC firmware load, SDMA0/SDMA1 firmware load, graphics and compute queues, and SDMA copy/fill paths.
- Clock-gating and power tests that exercise idle transitions, graphics load transitions, suspend/resume, runtime power management, performance counters, and debug modes that force clocks on or override stall behavior.
- SR-IOV and virtualization tests covering VF enable/disable, PF/VF active function IDs, doorbell status set/clear, scheduler commands and responses, VM busy status, virtual reset requests, FLR, and context save/restore storage.
- Reset and recovery tests covering cold boot, warm reset, VDDGFX exit, VF FLR exit, RLC/SDMA busy/status fields, RLC/SDMA checksums, interrupt-cookie behavior, and queue reset requests.
- SDMA-specific tests covering ring-buffer pointer handling, IB execution, write-pointer polling, CSA address use, preemption, AQL mode, mid-command state, UTCL1 status, atomic controls, and performance/status register readback.
- Regression indicators include GPU hangs, failed ring tests, SDMA timeouts, firmware checksum mismatch, bad VM faults, SR-IOV isolation failures, FLR timeouts, missing or stuck interrupts, unexpected busy bits, malformed debug dumps, power-management instability, or workload-specific performance changes after clock-gating or virtualization programming changes.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002490`. It covers lines 35037-37447 of `gc_10_3_0_sh_mask.h`. The final per-file research should merge it with adjacent chunks to recover the complete `CGTT_SC_CLK_CTRL1` definition before line 35037 and the remaining `SDMA1_PUB_REG_TYPE1`/later SDMA1 register families after line 37447.

### subset-b-002491: lines 37448-39877

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 37448-39877

## Scope

This chunk is part of the generated AMD GC 10.3.0 shift/mask register header. It contains only C preprocessor constants: each hardware field is represented by a `<REGISTER>__<FIELD>__SHIFT` value and a matching `<REGISTER>__<FIELD>_MASK` value. There are no functions, structs, enums, includes, memory allocations, locks, callbacks, runtime branches, or direct MMIO operations in this range.

The selected lines begin in the tail of the `SDMA1_PUB_REG_TYPE1` masks, cover SDMA1 public register type summaries 2 and 3, then define the visible GC SDMA2 and SDMA3 hypervisor decode summaries. The chunk continues through GCVM shared hypervisor/SR-IOV and MARC virtual-memory controls, PSP-facing firewall and translation-assist controls, and the start of the concrete `gc_sdma2_sdma2dec` register block through `SDMA2_PAGE_RB_WPTR_POLL_CNTL`. The range ends mid-register, so the matching `SDMA2_PAGE_RB_WPTR_POLL_CNTL` masks continue in the next source lines outside this chunk. Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata and is not Ceph filesystem logic.

## Purpose

`gc_10_3_0_sh_mask.h` supplies bitfield layouts for AMD graphics IP version 10.3.0. Driver code includes it with the matching GC 10.3.0 offset and default headers so register helpers can compose, extract, or preserve field values for the active ASIC generation.

This chunk serves five main purposes:

- It finishes SDMA1 public register type masks and enumerates SDMA2/SDMA3 hypervisor-visible register-summary bitmaps. The `*_CONTEXT_REG_TYPE*` and `*_PUB_REG_TYPE*` registers act as compact capability/visibility maps for groups of SDMA context, public, VM, microcode, VF, and status registers.
- It describes virtualization state for SDMA2 and SDMA3 hypervisor decoders: microcode address/data windows, VM context low/high addresses, active VF identity, VF/PF reset requests, VF enable, VMID/privilege controls, and per-engine register availability summaries.
- It defines GCVM shared hypervisor fields used by SR-IOV and GPU virtual memory. These include framebuffer size/offset registers for VF0 through VF31, MARC aperture base/relocation/length registers for four regions, IOMMU MARC enable, IOMMU control/performance knobs, and XGMI GPU IOV enable bits for VFs and the PF.
- It defines PSP-facing security and translation fields: CPG/CPC PSP GPA override bits, first firewall violation address/op/aperture reporting for RLC and SRM, VMID/client/group fault status, VMID bypass/GPA controls, GPU-host translation enable, and GPUVA-to-VMID translation-assist request/response payload fields.
- It starts the concrete SDMA2 decode register layout used to initialize, control, monitor, and recover the second SDMA engine. Covered fields include power and clock gating, engine control, copy-engine tuning, address swizzle configuration, idle/status registers, error detection counters, UTCL1 translation controls, invalidation/XNACK details, public status registers, GFX ring/IB/doorbell/context state, mid-command preemption state, and the beginning of the PAGE ring controls.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The important interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the corresponding 32-bit field mask.
- Matching register addresses live in `gc_10_3_0_offset.h`; matching reset values, where generated, live in `gc_10_3_0_default.h`.
- Consumers normally use these constants through AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, SDMA MMIO helpers, PSP/VM accessors, and SR-IOV register programming paths.

The SDMA public summary macros in this chunk are grouped by engine:

- `SDMA1_PUB_REG_TYPE2` and `SDMA1_PUB_REG_TYPE3` enumerate SDMA1 public registers such as UTCL1 invalidate/XNACK/timeout/page controls, physical address capture, phase2 quantum, error logs, dummy registers, F32/performance counters, CRD control, AQL status, EA double-bit address capture, TLBI/GCR control, tiling configuration, interrupt/status registers, scratch RAM, timestamp, and queue reset.
- `SDMA2_CONTEXT_REG_TYPE0..3` and `SDMA3_CONTEXT_REG_TYPE0..3` enumerate GFX context register groups: ring base/read/write pointers, write-pointer polling, read-pointer writeback addresses, IB controls and base/size registers, context status/control, doorbell, watermark, CSA, preempt, AQL, minor pointer update, and mid-command data/control slots.
- `SDMA2_PUB_REG_TYPE0..3` and `SDMA3_PUB_REG_TYPE0..3` enumerate public engine registers such as reset/start, timestamps, power/clock/control/chicken bits, address configuration, status pages, UTCL1 status/invalidation/XNACK controls, TLBI/GCR, scratch/timestamp, status, and queue reset.

The GCVM and virtualization macros include these notable families:

- `GCMC_VM_FB_SIZE_OFFSET_VF0..VF31`: each has `VF_FB_SIZE` in bits `[15:0]` and `VF_FB_OFFSET` in bits `[31:16]`, giving a compact per-VF framebuffer aperture size/offset encoding.
- `GCVM_IOMMU_MMIO_CNTRL_1__MARC_EN`: controls MARC enablement.
- `GCMC_VM_MARC_BASE_LO/HI_0..3`, `GCMC_VM_MARC_RELOC_LO/HI_0..3`, and `GCMC_VM_MARC_LEN_LO/HI_0..3`: describe four MARC base, relocation, enable/read-only, and length windows. Low address fields commonly start at bit 12, reflecting page-aligned apertures.
- `GCVM_IOMMU_CONTROL_REGISTER`, `GCVM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER`, and `GCMC_VM_XGMI_GPUIOV_ENABLE`: control IOMMU behavior and per-function GPU IOV enablement.
- `GCVM_L2_ID_CTRL0..7`, `GCVM_L2_ID_CTRL_HI`, and `GCVM_L2_ID_STATUS`: define VMID enable vectors and fault reporting fields for VMID, client ID, group ID, and interrupt-on-fault status.
- `GCUTCL2_TRANSLATION_BYPASS_BY_VMID`, `GCVM_IOMMU_GPU_HOST_TRANSLATION_ENABLE`, and `GCUTC_GPUVA_VMID_TRANSLATION_ASSIST_*`: encode translation bypass/GPA mode, host translation enable, and request/response data for GPU virtual address translation assistance.

The SDMA2 concrete register macros include these major groups:

- Engine lifecycle and power: `SDMA2_DEC_START`, global timestamp registers, `SDMA2_PG_CNTL`, `SDMA2_PG_CTX_LO/HI`, `SDMA2_PG_CTX_CNTL`, `SDMA2_POWER_CNTL`, and `SDMA2_CLK_CTRL`.
- Global engine control and tuning: `SDMA2_CNTL`, `SDMA2_CHICKEN_BITS`, `SDMA2_GB_ADDR_CONFIG`, `SDMA2_GB_ADDR_CONFIG_READ`, burst and page-size controls, phase quantum registers, BA threshold, ID/version, and F32 control/counter/checksum registers.
- Runtime status and error reporting: `SDMA2_STATUS_REG`, `SDMA2_STATUS1_REG`, `SDMA2_STATUS2_REG`, `SDMA2_STATUS3_REG`, `SDMA2_STATUS4_REG`, `SDMA2_STATUS5_REG`, `SDMA2_EDC_CONFIG`, `SDMA2_EDC_COUNTER`, `SDMA2_EDC_COUNTER_CLEAR`, `SDMA2_ERROR_LOG`, `SDMA2_INT_STATUS`, and queue reset request bits.
- Translation and memory-system controls: `SDMA2_UTCL1_CNTL`, `SDMA2_UTCL1_WATERMK`, read/write UTCL1 status registers, invalidation registers, read/write XNACK registers, timeout/page registers, physical address registers, TLBI/GCR control, tiling config, and credit control.
- GFX queue context: `SDMA2_GFX_RB_CNTL`, ring base/RPTR/WPTR registers, WPTR polling and polling address registers, read-pointer writeback address registers, IB control/base/size/offset/read-pointer registers, context status/control, doorbell and doorbell log/offset, watermark, CSA address, IB sub-remaining, preempt, AQL, minor pointer update, and mid-command data/control registers.
- PAGE queue context begins with `SDMA2_PAGE_RB_CNTL`, ring base/RPTR/WPTR registers, and the first `SDMA2_PAGE_RB_WPTR_POLL_CNTL` shift definitions. The mask definitions for that final register are outside this chunk.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time substitution of numeric constants.

The implied driver flow is:

1. Include `gc_10_3_0_offset.h`, `gc_10_3_0_sh_mask.h`, and sometimes `gc_10_3_0_default.h` for the selected ASIC family.
2. Select the correct register address and base index for GC 10.3.0.
3. Read a 32-bit register value, or prepare a 32-bit value for writing.
4. Use the generated mask/shift pair, usually through `REG_GET_FIELD` or `REG_SET_FIELD`, to extract status fields or update a single field while preserving unrelated bits.
5. Execute the sequencing in higher-level AMDGPU code: SDMA engine init/resume, queue setup, VM programming, SR-IOV configuration, PSP firewall handling, reset recovery, or fault diagnostics.

For SDMA2 queue setup, the higher-level flow normally programs ring base addresses, writeback addresses, polling controls, doorbell offset/enable, VMID/privilege bits, and ring size, then enables the ring. For fault or hang diagnostics, code reads the status, UTCL1, XNACK, physical address, and queue-status fields to infer whether an SDMA queue is idle, stalled, faulted, preempted, or waiting on translation/memory-system resources. For virtualization, SR-IOV and hypervisor-facing code uses the VF identity, enable, reset, framebuffer aperture, MARC, and GPU IOV masks to isolate or expose GPU resources to guest functions.

## State And Persistence Behavior

The macros themselves are stateless and do not persist anything. They describe fields in GPU hardware registers.

SDMA public and context summary registers are hardware-visible metadata/capability bitmaps. Their values are generally fixed by the ASIC/register block or programmed by firmware/hypervisor control paths, not by normal per-command driver flow. They may be read to determine which context or public registers are available for a VF/PF or to build save/restore masks.

GCVM and virtualization registers represent persistent hardware configuration state: VF framebuffer apertures, MARC mappings, IOMMU policy, GPU IOV enablement, VMID fault behavior, and translation-assist control. These values may persist until GPU reset, graphics IP reset, suspend/resume reinitialization, virtualization teardown, or explicit hypervisor/driver writes. Fault status and translation-assist request/response fields are hardware-owned and volatile or handshake-driven.

Concrete SDMA2 registers mix configuration state with live hardware state. Ring base addresses, VMID/privilege bits, polling address, doorbell setup, AQL controls, timing knobs, and power/clock controls are driver-owned configuration that must be restored after reset or power loss. Ring pointers, status registers, UTCL1 status, XNACK details, error counters, timestamps, interrupt status, doorbell captured/log bits, and mid-command state are hardware-updated live state. Some fields may be sticky, self-clearing, write-one-to-clear, read-only, or side-effectful; this generated header does not encode access semantics.

## Dependencies And Integration Points

This chunk depends on the generated GC 10.3.0 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h` supplies matching register addresses such as `mmSDMA2_CONTEXT_REG_TYPE0`, `mmSDMA2_GFX_RB_CNTL`, and `mmSDMA2_PAGE_RB_CNTL`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_default.h` supplies reset/default values such as `mmSDMA2_CONTEXT_REG_TYPE0_DEFAULT`, `mmSDMA2_GFX_RB_CNTL_DEFAULT`, and `mmSDMA2_PAGE_RB_CNTL_DEFAULT`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c`, `amdgpu_sdma.c`, `gfxhub_v2_1.c`, `amdgpu_amdkfd_gfx_v10_3.c`, and `pm/swsmu/smu11/vangogh_ppt.c` include this GC 10.3.0 mask header or depend on the same register namespace.
- The broader AMDGPU register-helper layer provides SOC15 MMIO access, read-modify-write helpers, and register-field extraction helpers.

Integration points include:

- SDMA v5.2 initialization, ring setup, queue preemption/reset, command submission, timeout/hang recovery, and suspend/resume restore.
- GFXHUB v2.1 and GCVM programming for address translation, VMID policy, translation bypass, GPU host translation, and page-fault diagnostics.
- KFD/GFX 10.3 compute integration, where SDMA queues, AQL controls, VMIDs, doorbells, and preemption state matter for user-mode queues.
- SR-IOV and hypervisor paths that manage VF identity, VF enable/reset, per-VF framebuffer aperture maps, MARC windows, GPU IOV enable masks, and PSP/firewall reporting.
- Power-management and clock-gating code that relies on SDMA power/clock control and status fields to gate or resume the engine safely.

## Risks And Edge Cases

- Generated-header drift is the primary risk. Incorrect mask or shift values compile cleanly but can set the wrong hardware bit, causing queue setup failures, VM faults, virtualization isolation bugs, broken power gating, or misleading diagnostics.
- This chunk starts mid-`SDMA1_PUB_REG_TYPE1` and ends mid-`SDMA2_PAGE_RB_WPTR_POLL_CNTL`. The final per-file research must merge adjacent chunks before claiming complete coverage of those register families.
- The SDMA2 and SDMA3 hypervisor summary registers are highly repetitive. Copy/paste or generation mistakes can silently expose or omit the wrong register in a VF/PF context.
- SR-IOV and MARC fields are isolation-sensitive. Bad framebuffer offsets/sizes, relocation windows, read-only flags, or GPU IOV enable bits can break guest memory isolation or block legitimate VF access.
- Translation-assist request/response fields are handshake-style hardware state. Polling, acknowledging, or writing them with the wrong field width can lose requests, misreport permissions, or return stale translations.
- SDMA ring fields include 64-bit addresses split across low/high registers with alignment-implied low bits. Truncating high bits, forgetting low-bit shifts, or mixing GFX and PAGE ring fields can point the engine at the wrong memory.
- Ring pointer and doorbell state are live. Reads can race command submission, preemption, reset, or hardware writeback, so diagnostics must tolerate transient and partially updated values.
- Reserved fields appear throughout. Full-register writes that do not preserve reserved bits may alter undocumented behavior.
- The header does not express field access type. Some bits that look writable by name may be read-only status, self-clearing commands, write-one-to-clear status, sticky overflow flags, or firmware-owned values.
- Power, clock, and queue reset controls are sequencing-sensitive. Incorrect ordering around `SDMA2_POWER_CNTL`, `SDMA2_CLK_CTRL`, `SDMA2_FREEZE`, or `SDMA2_QUEUE_RESET_REQ` can leave rings hung or status bits inconsistent.

## Test Signals

Useful validation is mostly build, generated-data consistency, and hardware integration:

- Kernel build coverage for all GC 10.3.0 AMDGPU/KFD/SMU files that include `gc_10_3_0_sh_mask.h`.
- Static comparison against AMD's authoritative GC 10.3.0 register database to confirm every shift, mask, register family, and generated omission in this range.
- Mechanical checks that each field mask aligns with its shift, that each field in this chunk has a matching register address in `gc_10_3_0_offset.h`, and that available defaults in `gc_10_3_0_default.h` match the same register names.
- Consistency checks across SDMA2 and SDMA3 hypervisor summary families, allowing only documented engine-specific differences.
- SDMA queue tests on GC 10.3 hardware that exercise GFX and PAGE rings: ring enable/disable, doorbell updates, pointer writeback, IB submission, AQL packet mode, preemption, mid-command restore, and reset recovery.
- GPUVM and GFXHUB tests that trigger translation, invalidation, XNACK, page-fault, and translation-assist paths, then verify the decoded status fields are plausible.
- SR-IOV validation with multiple VFs to confirm framebuffer aperture, MARC, VF enable/reset, active function ID, and GPU IOV enable behavior.
- Suspend/resume, runtime power management, and GPU reset tests to confirm SDMA power/clock/ring configuration is restored and live status registers return to expected values.
- Runtime warning signals include SDMA ring timeouts, failed WPTR updates, unexpected doorbell captured/log data, persistent UTCL1 page fault/XNACK status, bad active queue IDs, EDC error counter growth, PSP firewall first-violation reports, VMID/client fault status, and guest VF access failures.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002491`. It covers lines 37448-39877 of `gc_10_3_0_sh_mask.h`. The final per-file research should merge it with neighboring chunks for complete SDMA1 public masks before line 37448 and the continuation of `SDMA2_PAGE_RB_WPTR_POLL_CNTL` plus the remaining SDMA2/PAGE/RLC and later GC register families after line 39877.

### subset-b-002492: lines 39878-42467

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

### subset-b-002493: lines 42468-45147

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 42468-45147

## Purpose

This chunk is generated AMD GC 10.3.0 register bitfield metadata. It contains no executable C code; it publishes `__SHIFT` and `_MASK` constants that AMDGPU, AMDKFD, power-management, and register-debug paths use to compose or decode 32-bit MMIO and indirect-register values. The matching offsets for these fields are provided by companion generated offset headers, especially `gc_10_3_0_offset.h` for GC registers and SDMA register offset headers for similarly named SDMA blocks.

The selected range starts in SDMA3 queue control/status definitions and then moves into the `gccacind` address block for graphics clock/activity/capacitance or power-throttling accounting. Although this repository subtree is under `ceph-client`, this file is AMD GPU driver hardware metadata, not filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, allocations, locks, or callbacks in this range. The exposed interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit.
- `<REGISTER>__<FIELD>_MASK` gives the in-register bit mask.
- Consumers combine these constants with register offset macros and helpers such as `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_IP`, `WREG32_SOC15_IP`, and `SOC15_REG_OFFSET`.

Major register groups in this chunk:

- SDMA3 queue reset and enable status: `SDMA3_STATUS5_REG` and `SDMA3_QUEUE_RESET_REQ` expose enable state, active queue IDs, and reset request bits for the GFX, PAGE, and RLC0-RLC7 queues.
- SDMA3 GFX queue registers: `SDMA3_GFX_RB_*`, `SDMA3_GFX_IB_*`, `SDMA3_GFX_CONTEXT_*`, `SDMA3_GFX_DOORBELL*`, `SDMA3_GFX_STATUS`, `SDMA3_GFX_WATERMARK`, `SDMA3_GFX_CSA_ADDR_*`, `SDMA3_GFX_PREEMPT`, `SDMA3_GFX_RB_AQL_CNTL`, `SDMA3_GFX_MINOR_PTR_UPDATE`, and `SDMA3_GFX_MIDCMD_*`. These define ring-buffer enable/size/swap/VMID/read-pointer writeback, base and pointer registers, write-pointer polling, indirect-buffer state, context status, doorbells, preemption, AQL, and mid-command preempt-save data fields.
- SDMA3 PAGE and RLC queues: the same queue-control pattern is repeated for `SDMA3_PAGE_*` and for each `SDMA3_RLC0_*` through `SDMA3_RLC7_*` queue. The RLC queue definitions are particularly relevant to KFD/HSA compute queues and MQD programming.
- GC CAC indirect block: after the `addressBlock: gccacind` marker, the chunk defines `PCC_*`, `PWRBRK_*`, `EDC_*`, `GC_CAC_ID`, `GC_CAC_CNTL`, `GC_CAC_OVR_SEL`, `GC_CAC_OVR_VAL`, many `GC_CAC_WEIGHT_*` registers, and the beginning of `GC_CAC_ACC_*` accumulator registers. These fields describe stall-pattern control, power-brake hysteresis, EDC stretch counters, CAC enable/status/override control, per-block signal weights, and readback accumulators.
- Per-block CAC weights: the weight tables cover many graphics blocks, including BCI, CB, CP, DB, GDS, LDS, PA, PC, SC, SPI, SQ, SX/SXRB, TA/TCP/TD, RMI, EA, UTCL2/ATCL2/router/VML2/walker, CU, UTCL1, GE, PMM, GL2C, GUS, PH, SDMA, SP, GL1C, CHC, SQC, and RLC. Most weight registers pack one or two 16-bit signal weights into a 32-bit word.
- CAC accumulators: the range ends after `GC_CAC_ACC_LDS0` through `GC_CAC_ACC_LDS8` and starts `GC_CAC_ACC_BCI0`; these are full 32-bit `ACCUMULATOR_31_0` readback fields.

Important field families include queue `RB_ENABLE`, `RB_SIZE`, `RB_SWAP_ENABLE`, `RPTR_WRITEBACK_ENABLE`, `RPTR_WRITEBACK_TIMER`, `RB_PRIV`, `RB_VMID`, `RPTR_WB_IDLE`, pointer/base `ADDR` and `OFFSET` fields, `DOORBELL` `ENABLE`/`CAPTURED` and `DOORBELL_OFFSET`, context `IDLE`/`EXPIRED`/`EXCEPTION`/`CTXSW_*`/`PREEMPTED` state, AQL `PACKET_SIZE`/`PACKET_STEP`/mid-command preemption fields, CAC stall-pattern step and throttle-pattern fields, CAC enable/override/status fields, weight signal fields, and accumulator readback fields.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by consumers:

1. ASIC-specific code includes `gc/gc_10_3_0_sh_mask.h` together with compatible offset headers.
2. Driver code chooses a concrete register by ASIC/IP block and instance.
3. The code composes a value with the generated masks and shifts, or decodes a value read from hardware.
4. Register helpers perform MMIO or indirect index/data accesses while surrounding driver code handles locking, reset ordering, queue ownership, and firmware interaction.

For SDMA rings, the driver sequence normally disables a ring, programs ring size/base, initializes read/write pointers and writeback addresses, configures write-pointer polling and doorbells, enables indirect buffers and pointer writeback, then re-enables the ring. In `sdma_v5_2.c`, similar fields are used through `REG_SET_FIELD` and direct shifts for SDMA ring startup, shutdown, doorbell writes, MQD construction, and debug register dumps.

For CAC and power-brake control, the fields are accessed through GC CAC indirect index/data registers. `soc15.c` serializes these indirect accesses with `adev->reg.gc_cac.lock`, and `gfx_v10_0.c` programs Sienna Cichlid power-brake stall patterns with `mmGC_CAC_IND_INDEX`, `ixPWRBRK_STALL_PATTERN_CTRL`, and `PWRBRK_STALL_PATTERN_CTRL__*` shifts.

## State And Persistence Behavior

This file stores no software state and persists nothing by itself. It describes hardware state.

The SDMA3 portion represents live queue and context state: ring enablement, queue reset requests, ring bases, read/write pointers, write-pointer polling locations, read-pointer writeback, doorbell capture state, indirect-buffer pointers, context-save addresses, preemption status, AQL mode, mid-command preemption scratch data, and watermark/status counters. These values are hardware-owned once queues run and are reset or reprogrammed during driver init, GPU reset, suspend/resume, queue eviction/restore, or KFD MQD reload.

The CAC portion represents indirect GC power/accounting state: stall patterns, hysteresis, EDC stretch counters, global CAC control, override selectors/values, per-block signal weights, and accumulators. Some fields are persistent configuration until reset or reprogramming; others are counters, status bits, or override controls whose meaning depends on current clocks, power state, workload, and firmware policy.

The macros do not encode access class. A field may be read-only, write-only, write-one-to-clear, self-clearing, sticky, latched, reserved, or indirect-only according to the hardware specification. Consumers must preserve unrelated and reserved bits when updating mixed-control registers.

## Dependencies And Integration Points

Direct dependencies are the generated offset headers that define the corresponding `mm*`, `reg*`, `ix*`, and base-index symbols. For this GC 10.3.0 header, include users found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`

Important integration points include:

- SDMA engine initialization, shutdown, reset recovery, ring tests, write-pointer submission, and interrupt handling in `sdma_v5_2.c`.
- KFD/HSA compute queue setup and MQD programming, where RLC queue ring-control, doorbell, context-save, AQL, and preemption fields are used to describe user queues.
- Doorbell and NBIO integration, since SDMA doorbell enable/offset fields must match the doorbell aperture and range programmed by NBIO.
- GPU reset, suspend/resume, and runtime power-management paths, because SDMA queue state and CAC configuration can be lost or become stale across power transitions.
- GC CAC indirect access helpers in `soc15.c`, which guard `mmGC_CAC_IND_INDEX`/`mmGC_CAC_IND_DATA` with `adev->reg.gc_cac.lock`.
- GFX 10.3 power-brake setup in `gfx_v10_0.c`, which writes `PWRBRK_STALL_PATTERN_CTRL` through the GC CAC indirect window and combines it with `GC_THROTTLE_CTRL` and DIDT throttle control.
- SMU/power-management code that interprets CAC/EDC signals as part of power, throttling, or telemetry policy.

## Risks And Edge Cases

- Header/offset mismatch is the main structural risk. These untyped constants can compile against the wrong generated offset family while programming an unintended register or field.
- SDMA queue registers are sequencing-sensitive. Enabling `RB_ENABLE` before base, pointer, writeback, doorbell, or polling registers are correct can corrupt queue state or hang the engine.
- Pointer units differ by field. Several low address fields start at bit 2 or bit 5, ring bases may be shifted by more than two bits in consumers, and doorbell offsets are DWORD-oriented. Incorrect shifts can place rings, polling memory, writebacks, or doorbells at the wrong GPU address.
- Ring buffer size fields are encoded sizes, not byte counts. Consumers must use the expected order/log encoding and maintain alignment with firmware or MQD ABI requirements.
- Doorbells are vulnerable to power-state races. `sdma_v5_2.c` contains fallback behavior for missed SDMA doorbells during power gating, so tests that pass only with MMIO write-pointer updates may hide doorbell problems.
- RLC queue fields are replicated across eight queues. Off-by-one register selection or wrong per-queue offset arithmetic can configure a valid but unintended queue.
- Context, preemption, and mid-command fields are hardware/firmware coordinated. Misprogramming `PREEMPT`, `MIDCMD_CNTL`, `DATA_VALID`, `ALLOW_PREEMPT`, or context-save addresses can break queue eviction, reset recovery, or HSA preemption.
- CAC indirect registers require serialized index/data access. Missing the GC CAC lock can interleave index and data writes from different paths and corrupt unrelated power-management state.
- CAC weights and accumulators are generated numeric fields without semantic validation. Wrong weights, overrides, or stall patterns can produce incorrect power estimates, overly aggressive throttling, or misleading telemetry while remaining syntactically valid.
- Full-width masks such as `0xFFFFFFFFL` appear on data and accumulator registers. Full width does not imply safe writeability; many such registers are readback, indirect data windows, or hardware-owned counters.
- The chunk boundary is artificial. It starts after earlier SDMA3 status/scratch/timestamp definitions and ends in the middle of the CAC accumulator list, so adjacent chunks are needed for the complete source-file picture.

## Test Signals

Useful validation is mostly build, static, hardware, and power-management coverage:

- Build coverage for GFX10.3/Vangogh/Sienna Cichlid paths that include `gc_10_3_0_sh_mask.h`, especially `sdma_v5_2.c`, `gfxhub_v2_1.c`, and SMU11 power-management files.
- Generated-header consistency checks that every `__SHIFT` has a matching `_MASK`, masks are aligned to shifts, fields do not overlap within a register except documented aliases/reserved fields, and all register names match compatible offset headers.
- SDMA ring smoke tests that initialize rings, submit copies/fills, advance write pointers through both doorbell and MMIO fallback paths, read back pointers, and verify fences complete.
- KFD queue tests that create and destroy HSA queues using RLC queue MQDs, exercise AQL packet submission, preemption/eviction/restore, and validate doorbell offsets and context-save addresses.
- Reset, suspend/resume, runtime power-gating, and GPU recovery tests while SDMA queues are active, because ring state, pointer writeback, and doorbell capture can be lost or need reprogramming.
- Negative indicators include stalled SDMA fences, write-pointer update failure counts, pending write-pointer updates, incorrect active queue IDs, context status stuck non-idle, doorbell captured/error logs, or preemption never completing.
- CAC/power tests that program power-brake stall patterns, verify GC throttle behavior, read EDC/CAC counters under known workloads, and compare telemetry before and after suspend/resume or GPU reset.
- Locking tests or code review for GC CAC indirect accesses: all index/data pairs should route through serialized helpers or otherwise prove exclusive access.
- Regression signals include unexpected throttling, missing power-brake effect, nonsensical CAC accumulator values, workload-independent counters, or ASIC-specific failures limited to GC 10.3 variants.

### subset-b-002494: lines 45148-47858

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 45148-47858

## Purpose

This chunk is generated AMD GC 10.3.0 register bitfield metadata. It contains no executable C; it publishes C preprocessor `__SHIFT` and `_MASK` constants for composing and decoding 32-bit graphics-core MMIO and indirect-register values. The matching register offsets and indirect indices are provided by the sibling GC 10.3.0 offset header.

The selected range covers four related hardware metadata areas:

- GC CAC accumulator readback and override fields for graphics, shader, memory, cache, SDMA, geometry, and MMU-facing blocks.
- CAC power-state pattern tables and fixed-pattern counters used around release, stall, and power-break transitions.
- SE CAC control and override fields, plus SPM global/per-SE sample-delay fields.
- RTAVFS indexed fields for closed-loop adaptive voltage/frequency sensing, CPO ripple counters, voltage-code selection, temperature ring oscillator controls, and AVFS FSM timing counters.

Although this tree is rooted under `sources/distributed-fs/ceph-client`, the file is AMDGPU hardware-description data, not Ceph or filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocation sites, callbacks, locks, or direct hardware accesses in this chunk. The API surface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the in-register mask for that field.
- Consumers pair these constants with `mm*` register-offset macros or `ix*` indirect-index macros from `gc_10_3_0_offset.h`, then use AMDGPU MMIO and indirect-register helpers.

Major macro groups in this chunk:

- `GC_CAC_ACC_*` accumulator registers. Most blocks expose a single full-width `ACCUMULATOR_31_0` field, for example `GC_CAC_ACC_CB*`, `DB*`, `CP*`, `GDS*`, `PA*`, `SPI*`, `TCP*`, `TD*`, `RMI*`, `EA*`, `UTCL2_*`, `GE*`, `GL2C*`, `SDMA*`, `GL1C*`, `SQC*`, and `RLC0`. Shader-centric `SQ*_LOWER` and `SP*_LOWER` registers expose the lower 32 bits, while `SQ*_UPPER` and `SP*_UPPER` expose `ACCUMULATOR_39_32` plus reserved/unused upper bits. These fields are readback windows for CAC activity accumulation.
- `GC_CAC_OVRD_*` override registers. Each block has `OVRRD_SELECT` and `OVRRD_VALUE` fields. Field widths vary by hardware block: small one-bit or few-bit overrides for blocks such as `RLC`, wider packed override selectors/values for blocks such as `CB`, `DB`, `TCP`, `TD`, `GE`, `SDMA`, and a high-half `GC_CAC_OVRD_GE_HI`. These are configuration/forcing controls, not counters.
- CAC power-transition LUTs. `RELEASE_TO_STALL_LUT_*`, `STALL_TO_RELEASE_LUT_*`, `STALL_TO_PWRBRK_LUT_*`, `PWRBRK_STALL_TO_RELEASE_LUT_*`, and `PWRBRK_RELEASE_TO_STALL_LUT_*` pack several `FIRST_PATTERN_*` entries into one register. Release-to-stall and power-break release-to-stall use compact 3-bit entries at 4-bit spacing; stall-to-release uses 5-bit entries at 8-bit spacing; stall-to-power-break uses 3-bit entries at 8-bit spacing.
- `FIXED_PATTERN_PERF_COUNTER_1` through `FIXED_PATTERN_PERF_COUNTER_10` define a 17-bit `PERF_COUNTER` field used to observe fixed CAC pattern counters.
- `HW_LUT_UPDATE_STATUS` exposes per-table `DONE`, `ERROR`, and `ERROR_STEP` fields for five hardware LUT update tables. It is a status register for table update completion and fault diagnosis.
- `addressBlock: secacind` contains `SE_CAC_ID`, `SE_CAC_CNTL`, `SE_CAC_OVR_SEL`, and `SE_CAC_OVR_VAL`. `SE_CAC_ID` separates CAC block and signal IDs, `SE_CAC_CNTL` exposes `CAC_FORCE_DISABLE` and a 16-bit threshold field, and the override selection/value registers are full-width data windows.
- `addressBlock: spmglbind` contains global SPM sample-delay fields. Every `GLB_*_SAMPLEDELAY` register in this block has the same layout: a 6-bit `SAMPLEDELAY` field at bits 0-5 and reserved bits 6-31. Covered blocks include CPG, CPC, CPF, GDS, GCR, PH, GE, GUS, CHA/CHC/CHCG, ATCL2, VML2, SDMA0-3, GL2A0-3, GL2C0-15, EA0-15, and GE2SE0-3.
- `addressBlock: spmind` contains per-shader-engine/per-shader-array sample-delay fields. The same 6-bit `SAMPLEDELAY` plus reserved-bit pattern appears for `SE_SPI`, `SE_SQG`, `SE_CBR`, `SE_DBR`, `SE_PA`, SA0 and SA1 blocks, GL1 blocks, CB/DB/SC/RMI, and WGP-local TA/TD/TCP blocks for WGP00 through WGP04.
- `addressBlock: grtavfsind` starts the RTAVFS indexed register set. `RTAVFS_REG0` through `RTAVFS_REG127` are repeated CPO measurement registers: even registers define 16-bit `RTAVFSCPO<N>_STARTCNT` and `RTAVFSCPO<N>_STOPCNT` fields, while odd registers define a 16-bit `RTAVFSCPO<N>_RIPPLECNT` field plus reserved high bits. This gives CPO entries 0 through 63.
- `RTAVFS_REG128` through `RTAVFS_REG148` define AVFS control/readback fields: raw AVFS voltage in `RTAVFS_REG130`, clock-divider and loop controls in `RTAVFS_REG131` and `RTAVFS_REG138`, ripple-counter/CPO final result selection and min/max accumulation in `RTAVFS_REG132` through `RTAVFS_REG139`, PSM controls/readbacks for VDD and VREG in `RTAVFS_REG140` through `RTAVFS_REG143`, and temperature ring oscillator controls/readbacks/calibration coefficients in `RTAVFS_REG144` through `RTAVFS_REG148`.
- `RTAVFS_REG149` through `RTAVFS_REG159` define 16-bit FSM timing/count fields, including startup, idle, CPO/ripple-counter reset/start/done, CPO final-result ready, voltage-code ready, target-voltage ready, stop-CPO, and wait-for-ack counts. The chunk ends at the first line of `RTAVFS_REG160`, so the complete definition for that register is in the following chunk.

Field names are descriptive but not sufficient to infer access rules. `RESERVED` and `UNUSED_0` fields mark bits that consumers should preserve unless the ASIC programming guide or generated defaults explicitly say otherwise.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU and related driver code:

1. GC 10.3.0 users include `gc_10_3_0_offset.h` and `gc_10_3_0_sh_mask.h`.
2. Driver code selects a direct MMIO register, an indexed GC CAC register, an indexed SE CAC register, an SPM sample-delay indirect address, or a GRTAVFS indirect register.
3. The code composes a 32-bit value with this chunk's masks and shifts, preserving unrelated fields as required.
4. Register access helpers perform the actual read/write over MMIO or an indirect index/data pair.

The indirect CAC path is lock-protected in `soc15.c`: GC CAC accesses write `mmGC_CAC_IND_INDEX` and read/write `mmGC_CAC_IND_DATA`, while SE CAC accesses write `mmSE_CAC_IND_INDEX` and read/write `mmSE_CAC_IND_DATA`. This matters because many macros in this chunk describe indexed registers rather than independently addressable direct MMIO registers.

For SPM sample-delay programming, `gfx_v10_0.c` golden settings write `mmRLC_SPM_GLB_SAMPLEDELAY_IND_ADDR` followed by `mmRLC_SPM_GLB_SAMPLEDELAY_IND_DATA`. The `*_SAMPLEDELAY` masks in this chunk describe the data payload once the correct indirect address is selected.

For CAC power-transition LUT and pattern-control programming, driver code writes GC CAC indirect indices such as `ixPWRBRK_STALL_PATTERN_CTRL` through `mmGC_CAC_IND_INDEX` and data through `mmGC_CAC_IND_DATA`. The LUT, fixed-pattern counter, and update-status masks in this chunk describe the packed fields used by that hardware state machine.

The RTAVFS definitions describe hardware fields used by firmware or power-management paths, but this chunk does not encode polling loops, wait times, reset sequencing, thermal conversion formulas, voltage-code policy, or ownership between SMU firmware, RLC, and host driver code.

## State And Persistence Behavior

This file stores no software state and persists nothing on disk. It describes hardware state exposed by GC 10.3.0 registers.

Represented hardware state includes CAC activity accumulators, forced override selectors/values, CAC power-transition lookup tables, fixed-pattern performance counters, LUT update status, SE CAC IDs/control/overrides, SPM sample-delay configuration for global and per-SE blocks, CPO start/stop/ripple counters, AVFS voltage and target-voltage selections, PSM min/max/average measurements, temperature ring oscillator configuration and readback, and RTAVFS FSM timing counters.

Persistence is hardware-defined. Some fields are configuration bits that remain until reset or reprogramming. Others are live counters, latched measurement results, status bits, or action-control fields that may change while the GPU is running. GPU reset, suspend/resume, clock-gating, power-gating, runtime power management, SMU intervention, and RLC firmware activity can clear, overwrite, or make stale the state described by these fields.

The macros do not describe access class. A register field may be read-only, write-only, read/write, write-one-to-clear, self-clearing, sticky, firmware-owned, or invalid on a subset of SKUs. Consumers need read-modify-write discipline for mixed control/reserved registers and explicit sequencing for status/counter reads.

## Dependencies And Integration Points

The direct companion dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h`, which supplies corresponding register offsets and indirect indices. The broader generated register set also includes enum/default headers for related GC 10.3.0 values.

Known include users of the GC 10.3.0 shift/mask header in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c`

Important integration points:

- AMDGPU SOC15 register-access plumbing, especially indirect GC CAC and SE CAC helpers guarded by `adev->reg.gc_cac.lock` and `adev->reg.se_cac.lock`.
- GFX v10 golden register programming, which initializes many RLC SPM sample-delay indirect registers from tables.
- Power-management and SMU paths for Van Gogh/GC 10.3-era parts, where RTAVFS and voltage/temperature fields are relevant to AVFS and thermal behavior.
- Profiling, diagnostics, and hardware validation paths that read CAC accumulators, fixed-pattern counters, LUT status, and sample-delay settings.
- GPU reset, runtime PM, suspend/resume, and ASIC bring-up flows, because these hardware fields are tied to clocks, power states, RLC firmware, and SMU-owned policy.

This chunk is source-tree aligned to AMDGPU generated register metadata. It does not provide the semantic event IDs, legal LUT entries, voltage-code interpretation, temperature calibration units, or firmware contracts; those must come from adjacent generated headers, firmware interfaces, ASIC documentation, and consuming driver code.

## Risks And Edge Cases

- Header/offset mismatch is a primary risk. Pairing GC 10.3.0 masks with a different generation's offsets or indirect indices can compile while programming the wrong hardware field.
- The macros are untyped integer constants. A swapped register name, incorrect shift, or missing mask can silently alter unrelated fields.
- Full-width `0xFFFFFFFFL` accumulator and override windows are common. Full-width masks do not mean every value is safe to write; many are readback counters, packed override payloads, or firmware/hardware-owned data windows.
- `SQ` and `SP` accumulators are split into lower and upper registers with only 8 valid high bits. Consumers need correct low/high ordering and should not treat reserved upper bits as part of a 64-bit counter.
- Indirect registers require serialized index/data access. Missing the GC CAC or SE CAC lock, reusing the wrong index register, or interleaving reads and writes from another path can corrupt the transaction.
- LUT fields are densely packed. Release/stall/power-break tables use different entry widths and spacing, so table programming code cannot safely reuse one packing formula across all LUT types.
- `HW_LUT_UPDATE_STATUS` has separate done/error/error-step fields for five tables. Polling only the done bits can miss partial update failures.
- Sample-delay fields have only 6 valid bits. Values outside `0x3f` must be masked, and reserved high bits should be preserved. Incorrect sample delays may show up as profiling data skew rather than an immediate fault.
- Per-SE/per-SA/per-WGP sample-delay registers encode topology assumptions. A field can be present in the generated header but irrelevant or fused off on a particular SKU.
- RTAVFS registers cross firmware, power, voltage, and thermal domains. Host writes that race SMU/RLC ownership or ignore enable/reset sequencing can destabilize AVFS behavior, produce invalid voltage targets, or create hard-to-reproduce hangs.
- RTAVFS CPO registers are repetitive and easy to index incorrectly. Off-by-one errors between even start/stop registers and odd ripple-count registers can associate a measurement with the wrong CPO.
- The chunk boundary is artificial. It starts in the middle of the CAC accumulator block and ends at `RTAVFS_REG160`; adjacent chunks are needed for a complete per-file analysis.

## Test Signals

Useful validation is mostly build, static, and hardware/profiling coverage:

- Build coverage for GC 10.3.0 AMDGPU, AMDKFD, SDMA, GFXHUB, and SMU users that include `gc_10_3_0_sh_mask.h`.
- Generated-header consistency checks that each `__SHIFT` has a matching `_MASK`, masks align to their shifts, fields do not overlap except documented full-width aliases, and register names match `gc_10_3_0_offset.h`.
- Static checks that reserved/unused fields are not written as literal one-filled values by consumers.
- Indirect-access tests or review checks confirming GC CAC and SE CAC operations use the proper index/data registers and the existing locks.
- CAC accumulator smoke tests on real GC 10.3 hardware: reset/clear or sample counters, run known graphics/compute workloads, read block accumulators, and confirm plausible nonzero activity in expected blocks.
- Power-transition LUT tests that program release/stall/power-break patterns, poll `HW_LUT_UPDATE_STATUS`, and verify both done and error fields.
- SPM sample-delay validation through GFX golden settings and profiler runs, including checks for skewed, zero, or unstable SPM streams after reset and resume.
- RTAVFS validation under power-management test matrices: boot, runtime PM, suspend/resume, GPU reset, thermal load, voltage changes, and firmware handoff. Watch for invalid voltage-code readbacks, stuck `RUNLOOP`, bad CPO final results, temperature calibration failures, or FSM counters that stop advancing.
- Regression indicators include GPU hangs during CAC/SPM/AVFS programming, profiler data becoming all zero or saturated, table update error bits, sample-delay values outside the 6-bit field, temperature/voltage telemetry discontinuities, or failures isolated to GC 10.3 SKUs and firmware revisions.

### subset-b-002495: lines 47859-49396

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 47859-49396

## Purpose

This chunk is generated AMD GC 10.3.0 register bitfield metadata. It contains no executable C code; it exports preprocessor `__SHIFT` and `_MASK` constants used by AMDGPU, AMDKFD, SDMA, and SMU/PM code to compose and decode MMIO register values for this graphics IP generation. The matching register offsets and base-index macros are in `gc_10_3_0_offset.h`.

The selected range covers the tail of the RTAVFS tuning/status register block, a small `spiind` block selector, shader queue (`sqind`) debug and wave-state registers, SQ interrupt payload layouts, and the full `didtind` Dynamic Inductive Droop Throttling / Electrical Design Current control tables for SQ, DB, TD, and TCP blocks. Although the repository path is under `ceph-client`, this file is GPU driver hardware metadata, not filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, locks, memory allocations, or direct I/O operations in this range. The public API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit for a hardware register field.
- `<REGISTER>__<FIELD>_MASK` gives the in-register bit mask for that field.
- Consumers pair these macros with `mm<REGISTER>`/`ix<REGISTER>` address macros from generated offset headers and register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, indirect register accessors, and `REG_GET_FIELD`/`REG_SET_FIELD`-style bit helpers.

Major register groups in this chunk:

- `RTAVFS_REG160` through `RTAVFS_REG165`: real-time adaptive voltage/frequency scaling style fields. They define CPO average divider slots, proportional/integral gains, voltage code thresholds, binary-search and hardware-calibration enables, FSM state, guard-band values, and ripple-counter readback.
- `SA_WGP_BLK_ID`: `spiind` selector fields for block ID, WGP side, and shader-array ID. This is used to target per-WGP/per-SA indexed state.
- `SQ_DEBUG`, `SQ_DEBUG_STS_GLOBAL`, `SQ_DEBUG_STS_GLOBAL2`, and `SQ_DEBUG_STS_LOCAL`: shader queue debug and busy/occupancy state, including single-memory-operation debug mode, global busy flags, interrupt-message busy status, graphics/compute FIFO levels, wave levels by SA, and block-local busy bits for SQ, instruction scheduler, instruction buffer, arbiter, export, broadcast-message, and VM subunits.
- `SQ_WAVE_*`: wavefront inspection and state-register layouts. The range includes active/valid wave-slot masks, wave mode bits, status bits, trap status, legacy and split hardware IDs, GPR/LDS allocation fields, instruction-buffer counters, program counter low/high words, current instruction word, flat scratch address words, POPS packer state, scheduler mode, VGPR offset fields, shader-cycle count, all TTMP scratch registers, `M0`, and `EXEC_LO`/`EXEC_HI`.
- `SQ_INTERRUPT_WORD_AUTO`, `SQ_INTERRUPT_WORD_ERROR`, and `SQ_INTERRUPT_WORD_WAVE`: packed SQ interrupt payload formats. They expose thread-trace/WLT flags, buffer-full and UTC-error bits, error detail/type, privilege, wave/SIMD/WGP/SA/SE identity, payload data, and encoding fields. These masks are wider than 32 bits for context payload layouts.
- `DIDT_SQ_*`, `DIDT_DB_*`, `DIDT_TD_*`, and `DIDT_TCP_*`: parallel DIDT/EDC control families for shader queue, depth block, texture data, and texture cache pipeline blocks. Each family has repeated layouts for enable/reset/clock override, high-power and over-current thresholds, short/long interval sizing, stall delay and max-stall limits, tuning limits, auto-release timing, throttle policy and force-stall controls, stall patterns, MPD scale factors, stall-release FSM configuration/status, weight tables, EDC enable/reset/threshold/pattern/timer controls, throttle source enables, per-instance EDC stall delays, EDC status/overflow/readback, rolling power delta, and PCC performance counter readback.
- `DIDT_{SQ,DB,TD,TCP}_STALL_EVENT_COUNTER`: full-width stall event counter readback registers for the DIDT-controlled blocks.

The field names are hardware-oriented and generated directly from AMD register descriptions. Fields named `RESERVED` or `UNUSED` still have masks, but consumers should normally preserve them unless a programming guide explicitly defines a safe write value.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by driver code that includes the generated header:

1. A GC 10.3.0 consumer includes `gc_10_3_0_offset.h` and `gc_10_3_0_sh_mask.h`.
2. The consumer chooses a direct or indirect register address using the matching `mm*` or `ix*` offset macro.
3. It composes or decodes a value with this chunk's shift/mask constants.
4. AMDGPU, AMDKFD, PM, or SDMA register helpers perform the actual MMIO or indirect-register access while the relevant hardware block, firmware, interrupt path, debug path, or power-management sequence owns ordering.

The chunk describes fields needed for wave inspection, interrupt decoding, adaptive voltage/frequency tuning, and DIDT/EDC throttling, but it does not encode when those fields may be accessed, which bits are read-only or self-clearing, how to sequence reset/enable/stall operations, or how to coordinate with firmware and power-gated hardware. Those rules live in the consuming driver paths and the ASIC programming guide.

## State And Persistence Behavior

The file stores no software state and persists nothing. It only names hardware state exposed through GC 10.3.0 registers.

The represented hardware state is substantial:

- RTAVFS tuning and status state includes divider/gain tables, voltage-code thresholds, FSM state, guard-band values, calibration mode, and ripple-counter readback.
- SQ debug and wave state includes live busy flags, queue occupancy, active and idle wave slots, wave execution mode, status/trap flags, hardware identity, program counter, allocation state, outstanding counter state, TTMP scratch state, `M0`, `EXEC`, and instruction readback.
- SQ interrupt word fields describe context payloads generated by hardware for thread-trace, WLT, wave, and error interrupts.
- DIDT and EDC state includes enable bits, reset strobes, clock overrides, thresholds, interval and delay parameters, stall/throttle policies, weight tables, state-machine status, overflow counters, rolling power values, PCC performance counters, and stall event counters for SQ, DB, TD, and TCP blocks.

Persistence is hardware-defined. Some values are durable configuration until GPU reset, suspend/resume, power-gating, or explicit reprogramming; others are live status, counters, indirect readback windows, write-one/self-clearing control strobes, sticky overflow indicators, or hardware-owned state that changes while the GPU is running. The macros do not tell consumers which category a field belongs to, so callers must preserve unrelated bits and respect access restrictions from the hardware guide.

## Dependencies And Integration Points

The direct companion dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h`, which provides corresponding `mm*` register offsets and base indices. Indirect registers in this range are associated with the `spiind`, `sqind`, and `didtind` address blocks, so consumers also depend on the correct indirect-index/data access path for the target block.

Observed include users of the GC 10.3.0 shift/mask header in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c`

Integration points include GFX 10.3 initialization, KFD queue and trap/debug support, wavefront save/restore and inspection tooling, interrupt decoding, SMU/Vangogh power management, adaptive voltage/frequency tuning, droop and current throttling, EDC/PCC monitoring, GPU reset/recovery, suspend/resume, runtime power management, and low-level hardware validation. The SQ interrupt word layouts also align conceptually with KFD interrupt-processing code that decodes SQ-generated context payloads, although some paths carry local copies of related field definitions for older IP families.

## Risks And Edge Cases

- Header/offset mismatch is the primary correctness risk. Pairing `gc_10_3_0_sh_mask.h` with another GC generation's offset header can compile while silently targeting the wrong register or field.
- These macros are untyped constants. A wrong register family, field name, shift, or mask can alter hardware throttling, decode the wrong wave identity, or misinterpret interrupt/error payloads without compiler help.
- Several SQ interrupt masks are wider than 32 bits, such as fields above bit 31. Consumers must use a sufficiently wide integer type when decoding these payloads; truncating to `u32` loses WGP/SE/encoding fields.
- SQ wave state is live and per-wave/per-SIMD/per-WGP. Reads can race with scheduling, trap handling, context save/restore, wave completion, or reset unless the caller has halted or otherwise synchronized the target wave.
- DIDT and EDC controls are power/performance sensitive. Incorrect thresholds, interval sizes, weights, stall patterns, force-stall bits, or throttle-source enables can cause unnecessary stalls, missed protection throttling, performance regressions, or GPU hangs.
- Reset and enable fields are mixed with status and configuration in many registers. Blind writes can drop active configuration, assert reset unexpectedly, clear counters, or write reserved/unused fields.
- Full-width masks such as `0xFFFFFFFFL` often describe readback values or counters, not necessarily safe write payloads.
- `RESERVED` and `UNUSED` fields appear throughout. Code should use read-modify-write patterns or documented reset values rather than fabricating whole-register writes.
- The chunk boundary is artificial. It starts in the middle of the RTAVFS register family and ends at the file trailer, so adjacent chunks are needed for the complete per-file register-map narrative.

## Test Signals

Useful validation is mostly build, generated-header consistency, and hardware/profiling coverage:

- Build coverage for GC 10.3.0 AMDGPU, AMDKFD, SDMA, GFXHUB, and SMU/Vangogh paths that include this header.
- Generated-header checks that every field has aligned shift/mask pairs, masks do not overlap within a register except documented aliases, and each register name has a matching offset entry in `gc_10_3_0_offset.h`.
- Static checks that 64-bit SQ interrupt word fields are decoded with 64-bit-capable types and that whole-register writes do not trample reserved bits.
- SQ debug smoke tests that halt or safely sample waves, read active/valid/idle slots, decode mode/status/trap/hardware ID fields, and verify program counter, allocation, TTMP, `M0`, and `EXEC` readbacks are plausible.
- KFD interrupt tests that exercise thread-trace, wave, and error interrupt payload decoding and verify SE/SA/WGP/SIMD/wave/privilege/error fields are not truncated or shifted incorrectly.
- DIDT/EDC tests on supported GC 10.3.0 ASICs that enable/disable throttling, program thresholds and stall patterns, observe FSM status, overflow, rolling power delta, PCC counters, and stall event counters under known graphics/compute workloads.
- Power-management and recovery tests across suspend/resume, runtime power-gating, SMU interactions, and GPU reset while DIDT/EDC or wave debug features are active.
- Regression indicators include unexpected zero or saturated counters, stuck DIDT/EDC FSM state, overflow counters climbing immediately, excessive throttling or no throttling under stress, lost SQ interrupt identity bits, invalid wave debug snapshots, and hangs isolated to GFX 10.3/Vangogh-class hardware.
