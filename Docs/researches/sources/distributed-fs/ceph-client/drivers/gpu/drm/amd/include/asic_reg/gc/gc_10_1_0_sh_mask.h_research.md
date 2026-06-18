# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002449`: lines 1-2602, `Docs/researches/chunks/subset-b-002449_research.md`
- `subset-b-002450`: lines 2603-5195, `Docs/researches/chunks/subset-b-002450_research.md`
- `subset-b-002451`: lines 5196-7635, `Docs/researches/chunks/subset-b-002451_research.md`
- `subset-b-002452`: lines 7636-10058, `Docs/researches/chunks/subset-b-002452_research.md`
- `subset-b-002453`: lines 10059-12432, `Docs/researches/chunks/subset-b-002453_research.md`
- `subset-b-002454`: lines 12433-14880, `Docs/researches/chunks/subset-b-002454_research.md`
- `subset-b-002455`: lines 14881-17383, `Docs/researches/chunks/subset-b-002455_research.md`
- `subset-b-002456`: lines 17384-19837, `Docs/researches/chunks/subset-b-002456_research.md`
- `subset-b-002457`: lines 19838-22333, `Docs/researches/chunks/subset-b-002457_research.md`
- `subset-b-002458`: lines 22334-24790, `Docs/researches/chunks/subset-b-002458_research.md`
- `subset-b-002459`: lines 24791-27308, `Docs/researches/chunks/subset-b-002459_research.md`
- `subset-b-002460`: lines 27309-29911, `Docs/researches/chunks/subset-b-002460_research.md`
- `subset-b-002461`: lines 29912-32520, `Docs/researches/chunks/subset-b-002461_research.md`
- `subset-b-002462`: lines 32521-35035, `Docs/researches/chunks/subset-b-002462_research.md`
- `subset-b-002463`: lines 35036-37342, `Docs/researches/chunks/subset-b-002463_research.md`
- `subset-b-002464`: lines 37343-39656, `Docs/researches/chunks/subset-b-002464_research.md`
- `subset-b-002465`: lines 39657-42335, `Docs/researches/chunks/subset-b-002465_research.md`
- `subset-b-002466`: lines 42336-44165, `Docs/researches/chunks/subset-b-002466_research.md`

## Chunk Research

### subset-b-002449: lines 1-2602

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 1-2602

## Scope

This chunk is the opening segment of the generated AMD GC 10.1.0 shift/mask header. It covers line 1 through line 2602 and defines the include guard plus the first `gc_sdma0_sdma0dec` register-field macros. In this range there are 2,114 `#define` entries: 1,058 `__SHIFT` macros and 1,055 `_MASK` macros across 464 visible register comments. The slice starts with `SDMA0_DEC_START` and ends inside the `SDMA0_RLC7_RB_CNTL` group after `SDMA0_RLC7_RB_CNTL__RB_SWAP_ENABLE__SHIFT`, so the final register group is incomplete in this chunk.

The content is declarative only. There are no C functions, structs, enums, runtime variables, loops, branches, allocation paths, or local persistence behavior. Its exported surface is a generated preprocessor namespace describing bit positions and bit masks for SDMA0 registers on GC 10.1.0-class hardware.

## Purpose

`gc_10_1_0_sh_mask.h` supplies symbolic bitfield constants for AMDGPU and AMDKFD code that programs Graphics Core 10.1.0 registers. Consumers combine this file with `gc_10_1_0_offset.h` register offsets and helpers such as `REG_SET_FIELD`, `RREG32`, `WREG32`, and SDMA instance wrappers to construct read-modify-write values without embedding raw bit numbers in driver logic.

This chunk focuses on the SDMA0 engine and queue-control register map:

- Top-level SDMA0 decoder, power, clock, control, status, performance, error, MMU/UTCL1, tiling, hash, interrupt, and virtualization/IOV fields.
- The GFX queue register window, including ring buffer control, base/read/write pointers, writeback addresses, indirect buffer control, context status, doorbell, watermark, CSA address, preemption, AQL, minor pointer update, and mid-command state fields.
- The PAGE queue register window with the same ring/IB/doorbell/context/AQL/mid-command structure for page-related SDMA work.
- RLC compute queue windows beginning at `SDMA0_RLC0`, continuing through complete `RLC0` to `RLC6` definitions in this slice, and ending at the start of `RLC7`.

## Exported API Surface

There are no callable APIs or local types. The public interface is the macro family `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`.

Important macro families in this chunk include:

- `SDMA0_POWER_CNTL`, `SDMA0_PG_*`, `SDMA0_CLK_CTRL`, `SDMA0_CNTL`, `SDMA0_F32_CNTL`, `SDMA_POWER_GATING`, and `SDMA_PGFSM_*` for SDMA power gating, clocking, halt, trap, page interrupt, context-switch, and memory-power behavior.
- `SDMA0_STATUS_REG`, `STATUS1_REG`, `STATUS2_REG`, and `STATUS3_REG` for idle, ring, command, exception, queue-match, VM/TLBI/GCR, and interrupt-state readback.
- `SDMA0_GB_ADDR_CONFIG`, `TILING_CONFIG`, `HASH`, `PHYSICAL_ADDR_*`, `UTCL1_*`, `TLBI_GCR_CNTL`, and page/XNACK/invalidate fields for memory addressing, tiling, translation, invalidation, and address debug support.
- `SDMA0_PERFMON_CNTL`, `PERFCOUNTER*_SELECT*`, `PERFCOUNTER*_LO/HI`, and `PERFCOUNTER*_RESULT` for SDMA performance counter selection, mode, clear, enable, and readback.
- `SDMA0_GFX_*` and `SDMA0_PAGE_*` queue register groups for kernel driver SDMA rings.
- `SDMA0_RLC{0..6}_*` plus the beginning of `SDMA0_RLC7_RB_CNTL` for compute/HSA SDMA queue contexts controlled by KFD and firmware-visible MQD state.

Repeated queue windows expose a consistent set of fields: `RB_ENABLE`, `RB_SIZE`, byte-swap controls, read-pointer writeback enable/timer, VMID/privilege selection, ring base/rptr/wptr, write-pointer polling address and cadence, IB enable/base/size/offset, skip count, context selected/idle/expired/exception/preempt status, doorbell enable/capture/offset, outstanding read/write watermarks, CSA address, preempt trigger, AQL packet controls, minor pointer update, and mid-command data/control.

## Register Areas Covered

The initial SDMA0 control block describes engine-wide setup. Power-gating fields carry command/status and memory low/deep/shutdown controls. Clock-control and chicken-bit groups expose clock gating, copy efficiency, stall behavior, write burst tuning, QoS, and internal FIFO watermarks. `SDMA0_CNTL` is the main software-facing control register for traps, UTC L1, semaphore wait interrupts, data/fence swapping, mid-command preemption, page interrupts, per-channel performance counters, world switch, automatic context switching, and selected exception interrupts.

The status and memory-management section provides readbacks for idle states, ring fullness, command-progress state, exception details, page/physical address logging, UTCL1 watermarks, invalidate and XNACK controls, TLBI/GCR command credits, GPU IOV violation logging, AQL status, relaxed ordering, and tiling/hash configuration. These fields are used by bring-up, fault handling, virtualization, debugging, and performance investigation code.

The GFX and PAGE queue windows are full SDMA execution contexts. Their ring-buffer controls define enable state, ring size, endianness behavior, read-pointer writeback, VMID, privilege, and writeback-idle state. Pointer and base registers carry queue memory addresses and hardware read/write offsets. Doorbell and write-pointer polling registers select how userspace or the kernel notifies the SDMA engine of new work. IB, skip, preempt, AQL, and mid-command registers support indirect-buffer execution, queue recovery, AQL packet mode, and preemption/restoration.

The RLC queue windows repeat the same structural contract for compute queues. The chunk fully covers RLC0 through RLC6 and begins RLC7. In-tree KFD code uses the RLC0 field layout as a template for per-queue MQD values, while queue index and engine offsets select the actual hardware queue window.

## Control Flow And State Behavior

This header has no software control flow. Runtime behavior appears only when included by AMDGPU or AMDKFD code that reads and writes the corresponding MMIO registers.

The field names describe several hardware state machines and driver workflows:

- Engine lifecycle: power-gating commands, clock/halt controls, F32 halt, context-switch enable, and phase quantum fields participate in SDMA start, stop, suspend, resume, and scheduling behavior.
- Queue lifecycle: the driver programs ring base, size, read/write pointers, read-pointer writeback, doorbell offset, polling address, and finally `RB_ENABLE`/`IB_ENABLE` to make a queue runnable.
- Compute queue handoff: KFD MQD setup stores values built from `SDMA0_RLC0_*` shifts, then queue load code writes RLC registers, waits for `CONTEXT_STATUS.IDLE`, installs doorbell and pointer state, and enables the ring.
- Preemption and context save/restore: context status, CSA address, IB subremain, mid-command data, split state, and allow-preempt fields model the hardware-visible state needed to stop and later resume queued work.
- Fault and diagnostic handling: status, physical-address, UTCL1, TLBI/GCR, error/log, interrupt, performance, and IOV violation fields expose observable state for driver diagnostics and recovery.

No software state is persisted in this file. Hardware register values persist according to ASIC reset, power, firmware, and context-switch domains. In driver code, selected values are mirrored in objects such as SDMA MQDs and `amdgpu_ring` state, but this header only names the bit positions used to encode those values.

## Dependencies And Integration Points

The syntactic dependency is the C preprocessor. The semantic dependency is AMD's generated GC 10.1.0 register database and the companion offset header `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h`, which defines matching `mmSDMA0_*` register addresses in the `gc_sdma0_sdma0dec` block.

Direct in-tree include sites for `gc_10_1_0_sh_mask.h` or the matching offset header include:

- `drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c`, `gfxhub_v2_0.c`, `mmhub_v2_0.c`, `nv.c`, `mxgpu_nv.c`, and `sdma_v5_0.c` for GC 10/Navi-era graphics, memory hub, virtualization, and SDMA programming.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10.c` and related Arcturus/GFX KFD bridge code for compute queue save/load and SDMA queue offsets.
- `drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v10.c` and `kfd_device_queue_manager_v10.c` for constructing SDMA MQDs with fields such as `SDMA0_RLC0_RB_CNTL__RB_SIZE__SHIFT`, `RB_VMID__SHIFT`, and `RPTR_WRITEBACK_TIMER__SHIFT`.
- `drivers/gpu/drm/amd/amdgpu/sdma_v5_0.c` and related SDMA version files for ring bring-up, halt/unhalt, trap handling, page queue setup, doorbells, and performance/debug paths.

Common integration helpers include `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SDMA`, `WREG32_SDMA`, `RREG32`, and `WREG32`. The macro naming also aligns with firmware-visible SDMA MQD layouts, KFD queue management, GPU reset/recovery, SR-IOV, VM fault handling, and performance counter plumbing.

## Risks

- Generated-header drift is the main risk. A wrong shift or mask can silently write adjacent SDMA control bits during read-modify-write sequences.
- Ring and pointer fields are address-sensitive. Mis-shifting `RB_BASE`, `RB_RPTR_ADDR_LO`, `RB_WPTR_POLL_ADDR_LO`, IB base, doorbell offset, or CSA address fields can make SDMA fetch commands from the wrong memory or corrupt writeback state.
- Queue windows are highly repetitive. A generation or copy error in one RLC queue can create queue-index-specific compute failures that are difficult to diagnose.
- Enable ordering matters in consumer code even though the header cannot encode it. Drivers normally program size, base, read/write pointers, writeback, doorbell, polling, and VMID before asserting `RB_ENABLE` and `IB_ENABLE`.
- Status/control fields share the same macro form. Consumers must know from the hardware spec which fields are read-only, write-one-to-clear, sticky, reset-sensitive, privileged, or reserved.
- Preemption and mid-command fields are stateful hardware surfaces. Incorrect use can lose in-flight command state, break context switches, or leave a queue unable to resume.
- The chunk boundary ends inside `SDMA0_RLC7_RB_CNTL`; merge-time analysis should expect the remaining `RLC7` shift and mask definitions in the following chunk before flagging missing pairs.

## Test Signals

Useful validation is mostly build-time, generation-time, and hardware-integration oriented:

- Compile or preprocess AMDGPU and AMDKFD code that includes `gc_10_1_0_offset.h` and `gc_10_1_0_sh_mask.h`, especially `sdma_v5_0.c`, `gfx_v10_0.c`, `amdgpu_amdkfd_gfx_v10.c`, `kfd_mqd_manager_v10.c`, and `kfd_device_queue_manager_v10.c`.
- Static checks that complete register groups in the full header have matching `__SHIFT` and `_MASK` definitions; this slice has a known boundary mismatch because it ends at `SDMA0_RLC7_RB_CNTL__RB_SWAP_ENABLE__SHIFT`.
- Cross-check every register-family prefix in this chunk against `gc_10_1_0_offset.h` addresses such as `mmSDMA0_POWER_CNTL`, `mmSDMA0_GFX_RB_CNTL`, `mmSDMA0_PAGE_RB_CNTL`, and `mmSDMA0_RLC0_RB_CNTL`.
- Runtime SDMA ring tests on GC 10.1.0-class hardware: GFX ring initialization, command submission, fences, traps, indirect buffers, page queue operation, suspend/resume, reset recovery, and queue disable/enable cycles.
- KFD compute queue tests that create, load, preempt, restore, and destroy SDMA queues while validating MQD-programmed `RB_SIZE`, `RB_VMID`, read-pointer writeback, doorbell offset, and context idle behavior.
- Fault and debug tests for VM faults, UTCL1 invalidation/XNACK, TLBI/GCR activity, GPU IOV violations, performance counters, AQL status, and SDMA status register readback.

## Chunk Notes For Merge

This document intentionally covers only lines 1-2602 of `gc_10_1_0_sh_mask.h`. Later chunks should continue `SDMA0_RLC7_RB_CNTL` and the remaining GC 10.1.0 register-field namespace. The final per-file report should treat the whole file as a generated ASIC bitfield map for AMD GC 10.1.0 hardware rather than handwritten driver logic.

### subset-b-002450: lines 2603-5195

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 2603-5195

## Purpose

This chunk is a generated AMD GC 10.1.0 shift/mask header slice for SDMA register fields. It contains C preprocessor constants for field bit positions and masks; it has no executable logic. AMDGPU code includes this header with the companion GC 10.1.0 offset header so `REG_SET_FIELD`, `REG_GET_FIELD`, golden-register tables, ring setup, queue-management code, reset paths, and diagnostics can program or decode SDMA MMIO registers without hard-coded field numbers.

The requested range contains 2,593 lines, 2,121 `#define` statements, 1,060 `__SHIFT` macros, 1,061 `_MASK` macros, and 470 generated register or address-block comments. It starts inside the `SDMA0_RLC7_RB_CNTL` register field set, completes most of the `SDMA0_RLC7` queue register family, then enters the `gc_sdma1_sdma1dec` address block. Within SDMA1 it covers top-level power, clock, status, memory-translation, performance, interrupt, and debug fields; complete SDMA1 `GFX`, `PAGE`, and `RLC0` through `RLC5` queue families; and the beginning of the `SDMA1_RLC6` queue family. It ends inside `SDMA1_RLC6_IB_CNTL`, leaving the rest of that register and queue family for the next chunk.

Although the source tree is under a local `ceph-client` mirror, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, memory allocations, or direct MMIO operations in this range. The public interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field.
- `//SDMA*` comments: generated register boundaries.
- `// addressBlock: gc_sdma1_sdma1dec`: boundary where the file moves from SDMA0 register definitions into SDMA1 decoder/register definitions.

The main macro families in this chunk are:

- `SDMA0_RLC7_*`: tail of the SDMA0 RLC7 queue definition, including ring-buffer control, base/rptr/wptr registers, wptr polling, read-pointer writeback address, indirect-buffer control and address/size fields, context status, doorbell enable/capture/offset, watermark, context-save area address, preempt, AQL control, minor pointer update, and mid-command state capture registers.
- `SDMA1_DEC_START`, `SDMA1_PG_*`, `SDMA1_POWER_CNTL`, `SDMA1_CLK_CTRL`, `SDMA1_CNTL`, `SDMA1_CHICKEN_BITS`, `SDMA1_GB_ADDR_CONFIG`, and `SDMA1_GB_ADDR_CONFIG_READ`: SDMA1 decoder, power-gating, clock gating, global control, workaround, and graphics-address configuration fields.
- `SDMA1_STATUS_REG`, `SDMA1_STATUS1_REG`, `SDMA1_STATUS2_REG`, and `SDMA1_STATUS3_REG`: broad status fields for command state, ring/IB state, idle/busy reporting, AXI/UTCL1 state, command op/subop, context-empty state, queue activity, and f32/micro-engine activity.
- `SDMA1_RD_BURST_CNTL`, `SDMA1_HBM_PAGE_CONFIG`, `SDMA1_UCODE_CHECKSUM`, `SDMA1_F32_CNTL`, `SDMA1_FREEZE`, `SDMA1_PHASE0_QUANTUM`, `SDMA1_PHASE1_QUANTUM`, and `SDMA1_PHASE2_QUANTUM`: fetch/burst, firmware checksum, halt/freeze, context switch, and scheduling quantum definitions.
- `SDMA1_EDC_*`, `SDMA1_ATOMIC_*`, `SDMA1_BA_THRESHOLD`, `SDMA1_CRD_CNTL`, `SDMA1_GPU_IOV_VIOLATION_LOG*`, `SDMA1_AQL_STATUS`, `SDMA1_EA_DBIT_*`, `SDMA1_TLBI_GCR_CNTL`, `SDMA1_TILING_CONFIG`, and `SDMA1_HASH`: error detection/correction, atomics, bus/arbitration thresholds, credit control, virtualization violation logging, AQL status, ECC/double-bit address reporting, TLB invalidate/GCR control, tiling, and hashing fields.
- `SDMA1_UTCL1_*`: L1 translation/cache controls, read/write watermarks, read/write status, invalidate controls, XNACK controls, timeout handling, page control, and page-reservation/invalidating state.
- `SDMA1_PERFMON_*`, `SDMA1_PERFCOUNTER*`, and `SDMA1_PERFCOUNTER_TAG_DELAY_RANGE`: performance counter control, select, result, low/high counter, and tag-delay range fields.
- `SDMA1_GFX_*`, `SDMA1_PAGE_*`, and `SDMA1_RLC0_*` through `SDMA1_RLC5_*`: repeated queue families for graphics, paging, and RLC/compute contexts. Each full family includes ring-buffer control/base/rptr/wptr, wptr polling, rptr writeback address, IB control/base/size/offset, skip count, context status, doorbell, status, watermark, doorbell offset, CSA address, IB remaining size, preempt, dummy register, AQL control, minor pointer update, and mid-command data/control fields.
- `SDMA1_RLC6_*`: partial queue family through `SDMA1_RLC6_IB_CNTL__IB_SWAP_ENABLE__SHIFT` at the end of the requested range.

Common field names encode the hardware behavior: `RB_ENABLE`, `RB_SIZE`, `RB_SWAP_ENABLE`, `RPTR_WRITEBACK_ENABLE`, `RB_VMID`, `IB_ENABLE`, `CMD_VMID`, `CONTEXT_STATUS`, `CTXSW_READY`, `PREEMPTED`, `DOORBELL`, `WATERMARK`, `AQL_ENABLE`, `MIDCMD_PREEMPT_ENABLE`, `DATA_VALID`, `COPY_MODE`, `HALT`, `FREEZE`, `AUTO_CTXSW_ENABLE`, `IDLE`, `BUSY`, `VALID`, `FAULT`, `VIOLATION`, `PAGE`, `INV`, `XNACK`, `TIMEOUT`, `PERFCOUNTER`, and `EDC`.

## Control Flow

This header has no runtime control flow. Runtime behavior appears only when consumers expand these macros into register operations:

1. A consumer selects a GC 10.1.0 SDMA register offset, usually from `gc_10_1_0_offset.h`.
2. The consumer uses a field name plus this header's shift/mask macros through AMDGPU helper macros such as `REG_SET_FIELD` or `REG_GET_FIELD`, or through table-driven masks and values.
3. AMDGPU MMIO helpers such as `RREG32`, `WREG32`, and SOC15 register wrappers read, modify, write, poll, dump, or save the target SDMA register.
4. SDMA firmware and hardware state machines execute the actual ring, IB, context-switch, preemption, translation, interrupt, and power/clock behavior.

Examples of external sequencing described by these fields include disabling/enabling ring buffers and IBs, programming ring bases and read/write pointers, setting read-pointer writeback and wptr polling addresses, choosing doorbell offsets, enabling AQL packet interpretation, requesting IB preemption, preserving mid-command state, halting or freezing f32 execution, programming context-switch quantums, reading idle/busy/fault status, invalidating UTCL1 state, selecting performance counters, and applying golden register settings for SDMA1 queues.

## State And Persistence Behavior

The macros are stateless compile-time constants. They describe hardware-visible register state but do not store state themselves. Register values live in SDMA hardware, firmware-managed queues, GPU memory backing ring buffers, doorbell aperture state, writeback memory, and device power/clock domains.

State represented by this chunk includes:

- Queue control state: ring enable, ring size, endian swap, VMID, privilege, read-pointer writeback, write-pointer polling, IB enable, IB base/offset/size, skip counts, AQL mode, minor pointer update, and mid-command checkpoint data.
- Queue progress state: ring read/write pointers, IB read pointer and remaining sub-size, doorbell capture, write-pointer update pending/fail counters, context selected/idle/expired/exception/preempted status, and watermark outstanding read/write counters.
- SDMA1 global state: power-gating command/status/context address, clock gating, f32 halt, freeze, auto context switch, scheduling quantums, microcode checksum, decoder start, program/status registers, and workaround/chicken-bit flags.
- Memory and VM state: graphics-address configuration, UTCL1 controls, read/write watermarks, invalidate status, XNACK controls, timeout/page status, TLB invalidate/GCR control, physical address logging, IOV violation logs, EA double-bit address reporting, tiling, hash, and hole-address definitions.
- Observability state: EDC counters and clear controls, status banks, AQL status, atomic controls, performance monitor/counter select/result registers, interrupt status, and diagnostic dummy or mid-command registers.

Persistence is hardware-defined. Values may be reset by SDMA soft reset, full GPU reset, power gating, clock gating, suspend/resume, firmware reload, ring restart, per-queue reset, SR-IOV virtualization policy, or driver reinitialization. Ring base pointers, read/write pointers, writeback addresses, doorbell offsets, and context-save-area addresses must remain coherent with memory allocated by AMDGPU/KFD code; this header only supplies field layouts and does not enforce lifetime, alignment, ordering, or access rules.

## Dependencies And Integration Points

This generated header must stay synchronized with AMD's GC 10.1.0 register database and with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h`, which provides the matching `mmSDMA*` register offsets and base indices. It is included directly by AMDGPU Navi/SDMA code, including `amdgpu/sdma_v5_0.c`, `amdgpu/nv.c`, and KFD GFX10 support.

Key integration points include:

- `sdma_v5_0.c`: programs SDMA ring/IB enable bits, ring sizes, pointers, writeback addresses, polling controls, doorbells, preempt registers, f32 halt/freeze/context-switch fields, golden registers for SDMA1 queue polling, and IP dump register lists.
- KFD queue setup for GFX10: uses SDMA queue offsets and field layouts to calculate RLC queue register ranges for compute/SDMA queues.
- SOC15/Navi integration: uses `mmSDMA1_STATUS_REG` and related status registers in reset, dump, and hardware-IP register lists.
- SDMA firmware loading and ring packet code: relies on register state programmed with these fields to feed command streams, fences, traps, VM PTE updates, and copy/fill operations to hardware.
- SR-IOV and virtualization paths: consume doorbell, IB control, violation log, and queue context state under host/guest access restrictions.
- Diagnostic tooling and kernel logs: decode SDMA status, UTCL1 state, EDC counters, performance counters, IOV violations, and queue progress by pairing this header's field definitions with register dumps.

The repeated queue blocks are intentionally regular but not interchangeable across SDMA instance and queue family. `SDMA0_RLC7_*`, `SDMA1_GFX_*`, `SDMA1_PAGE_*`, and `SDMA1_RLCn_*` names must be paired with the matching offset names and the correct engine instance offset logic.

## Risks And Edge Cases

- These are untyped preprocessor constants. Incorrect shifts or masks can compile cleanly while silently changing the wrong hardware bit.
- The file is generated. Manual edits risk divergence from AMD's register database, companion offset headers, firmware expectations, and silicon documentation.
- The requested first line is inside `SDMA0_RLC7_RB_CNTL`; the register comment and initial `RB_ENABLE`, `RB_SIZE`, and `RB_SWAP_ENABLE` shift definitions are in the previous chunk.
- The requested last line is inside `SDMA1_RLC6_IB_CNTL`; the remaining shift fields and all masks for that register are in the next chunk.
- Queue-family repetition can hide copy/paste errors. Pairing an `SDMA1_RLC3_*` mask with an `SDMA1_RLC4_*` offset, or using SDMA0 field names when an SDMA1-specific path is required, may still compile but target the wrong queue.
- Address fields have alignment encoded in masks and shifts. Ring base, IB base, read-pointer writeback, write-pointer polling, doorbell offset, and CSA address programming can fail subtly if consumers ignore low-bit requirements such as `ADDR_LO` masks ending in `...FFFC` or `IB_BASE_LO` using shift 5.
- Context-switch, preemption, mid-command, AQL, and minor-pointer-update fields are sequencing-sensitive. Bad usage can cause stuck queues, corrupted command replay, lost preemption state, or hangs during ring restart.
- Doorbell fields cross CPU-visible doorbell memory, GPU MMIO, and queue scheduling. Incorrect enable, offset, or captured-state interpretation can cause missed queue wakeups or spurious updates.
- Status bits such as idle, selected, exception, pending, expired, XNACK, timeout, violation, and update-fail counters may be volatile or latch/clear according to hardware rules not expressed in this header.
- Power/clock/freeze/halt fields interact with firmware ownership, SR-IOV restrictions, and reset flows. The macros do not encode which registers are safe for bare metal, VF, or firmware-owned contexts.
- Performance, EDC, UTCL1, atomics, hash, tiling, and IOV log fields may be valid only under specific ASIC steppings, modes, or debug procedures.

## Test Signals

Useful validation for this chunk and its consumers includes:

- Build AMDGPU configurations that include Navi/GC 10.1.0 SDMA support; missing or renamed macros should break `sdma_v5_0.c`, KFD GFX10, and SOC15/Navi integration at compile time.
- Mechanically compare this range against AMD's authoritative GC 10.1.0 register specification, checking every emitted shift/mask pair and preserving split-register boundaries across adjacent chunks.
- Cross-check `SDMA1_*` register groups against `gc_10_1_0_offset.h`, especially top-level status/control registers, `GFX`, `PAGE`, `RLC0` through `RLC6`, and the offset gaps around status, doorbell log, watermark, CSA, and mid-command registers.
- Run ring bring-up, copy/fill, VM PTE update, fence, trap interrupt, suspend/resume, GPU reset, and per-queue reset tests on hardware using `sdma_v5_0`.
- Exercise KFD/compute SDMA queues that use RLC queue register families, including queue creation/destruction, preemption, context switch, AQL mode, and doorbell updates.
- Monitor SDMA IP dumps and debugfs/register dumps for ring pointer coherence, read-pointer writeback progress, wptr polling updates, doorbell offsets, context status, preemption state, update-fail counters, UTCL1/XNACK/timeouts, EDC counters, and IOV violation logs.
- Verify golden-register programming for SDMA1 queue wptr polling registers and related SDMA1 control registers across supported Navi variants.
- Test SR-IOV VF and bare-metal paths separately because some SDMA registers are host-owned or firmware-owned in virtualized environments.
- Decode known-good SDMA1 register dumps using these masks and compare against expected idle/busy, queue, VM, interrupt, EDC, and performance-counter state.

## Cross-Chunk Notes

The previous chunk owns the start of `SDMA0_RLC7_RB_CNTL`, including its register comment and the first shift fields. This chunk resumes at `SDMA0_RLC7_RB_CNTL__RPTR_WRITEBACK_ENABLE__SHIFT`, completes the rest of `SDMA0_RLC7`, then covers the beginning and most of the SDMA1 decoder/register map.

This chunk stops at `SDMA1_RLC6_IB_CNTL__IB_SWAP_ENABLE__SHIFT`. The next chunk should continue with `SDMA1_RLC6_IB_CNTL__SWITCH_INSIDE_IB__SHIFT`, the corresponding `CMD_VMID` shift and masks, and the remainder of the `SDMA1_RLC6` queue family.

### subset-b-002451: lines 5196-7635

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 5196-7635

## Purpose

This chunk is part of AMD's generated GFX/GC 10.1.0 register shift/mask header. It provides C preprocessor constants for bit-field extraction and insertion in Navi/GFX10-era AMDGPU graphics, command processor, SDMA, and primitive/rasterizer registers. It has no executable logic; its value is that in-tree drivers can use symbolic field names with `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and generated `mm*` offsets instead of hard-coded bit positions.

Although the file is stored under a local `ceph-client` source mirror, the content is AMDGPU hardware metadata, not Ceph or distributed filesystem code.

The requested range contains 2,440 lines, 2,169 `#define` statements, 1,086 `__SHIFT` macros, 1,083 `_MASK` macros, 3 address-block markers, and 262 generated register comments. It starts inside `SDMA1_RLC6_IB_CNTL` at the `SWITCH_INSIDE_IB` shift and finishes inside `PA_SC_TILE_STEERING_CREST_OVERRIDE` at the `FORCE_TILE_STEERING_OVERRIDE_USE` shift. The fully covered domains are:

- `gc_sdma1_*` tail definitions for SDMA1 RLC queues 6 and 7.
- `gc_grbmdec` global graphics register bus manager status, reset, trap, scratch, IOV, and error fields.
- `gc_cpdec` command processor CPC/CPF/ME/MEC/CE/PFP busy, stalled, status, queue, ring, and threshold fields.
- `gc_padec` primitive assembly, VGT/WD/GE, PA_CL, PA_SC, and binning/rasterizer control/status fields.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocations, locks, or direct MMIO operations in this chunk. The public interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the field in the register word.
- `// addressBlock: ...`: generated boundary mapping subsequent register comments to a hardware register block.
- `//<REGISTER>` comments: generated register group boundaries that correspond to register offsets in `gc_10_1_0_offset.h`.

Major macro families in this range:

- `SDMA1_RLC6_*` and `SDMA1_RLC7_*`: queue/ring buffer and indirect-buffer controls for SDMA1 RLC contexts. The fields cover ring enable/size/swap/VMID/privilege, read/write pointers, read-pointer writeback, write-pointer polling, IB enable/base/size/offset/read pointer, context status, doorbells and doorbell offsets, watermarking, context-save-area addresses, preemption, AQL packet controls, minor pointer update, and mid-command data/control.
- `GRBM_*`: global graphics status and management fields. These include graphics/CP busy status, per-shader-engine status (`GRBM_STATUS_SE0` through `SE3`), status2/status3 flags, power controls, soft-reset bits, clock gating controls, wait-idle timing, read/write/IOV error reporting, interrupt control, trap registers, DSM bypass, chip revision, GFX instance selection, IH credit, UTCL2 invalidation range, fence ranges, `GRBM_NOWHERE`, and scratch registers.
- `CP_CPC_*`, `CP_CPF_*`, and `CP_*`: command processor status, busy, stalled, queue, threshold, scratch, instruction-pointer, header-dump, halt/reset/cache-invalidate, preemption, ring-pointer, command-index/data, ROQ/STQ/MEQ/CEQ availability and statistics, and GRBM free-count fields. The chunk covers CPC, CPF, MEC, ME, PFP, and CE-facing state.
- `VGT_*`, `WD_*`, `GE_*`, `IA_UTCL1_*`, `CC_GC_*`, and `GC_USER_*`: vertex/geometry/tessellation and draw-dispatch front-end configuration fields, including FIFO depths, cache invalidation, shader-array configuration, DMA primitive controls, off-chip/ring sizes, UTCL1 status/control, geometry-engine status, fast clocks, and primitive configuration.
- `PA_CL_*`, `PA_SU_*`, `PA_PH_*`, and `PA_SC_*`: primitive/raster pipeline fields for clipper and setup status/enhance controls, binning event/performance controls, force-EOV counters, FIFO sizing, sideband delays, packed binning/PBB overrides, rasterizer enhancement flags, DSM force controls, and the start of tile-steering override selection.

Common field names encode hardware semantics: `ENABLE`, `IDLE`, `BUSY`, `STALL`, `HALT`, `RESET`, `STATUS`, `ERROR`, `VMID`, `ADDR`, `OFFSET`, `SIZE`, `WPTR`, `RPTR`, `POLL`, `DOORBELL`, `PREEMPT`, `CONTEXT`, `AQL`, `WATERMARK`, `SCRATCH`, `TRAP`, `INT`, `THRESHOLD`, `FREE_COUNT`, `FIFO`, `CACHE_INVALIDATION`, `FLUSH`, `BINNER`, `PBB`, `CLOCK_GATE`, `POWER`, and `RESERVED`.

## Control Flow

This header has no runtime control flow. Runtime behavior emerges only when compiled consumers combine these constants with register offsets and AMDGPU register helper macros:

1. A driver selects a register offset from `gc_10_1_0_offset.h`, such as `mmGRBM_STATUS`, `mmGRBM_SOFT_RESET`, an SDMA RLC queue register, or a CP/PA/VGT register.
2. The driver uses a field mask directly or uses `REG_SET_FIELD`/`REG_GET_FIELD`, which token-pastes the register and field names to the `__SHIFT` and `_MASK` macros in this file.
3. The driver reads, writes, modifies, polls, or dumps the hardware register with SOC15 MMIO helpers.
4. Hardware command processors, SDMA engines, GRBM reset/idle logic, and rasterization front-end state machines act on the programmed values or report status through the same fields.

In-tree examples include `gfx_v10_0.c`, which includes this header and uses `GRBM_STATUS__GUI_ACTIVE_MASK`, `GRBM_STATUS__PA_BUSY_MASK`, `GRBM_STATUS__SC_BUSY_MASK`, `GRBM_STATUS__CP_BUSY_MASK`, and `GRBM_SOFT_RESET` fields to wait for idle and decide which blocks to reset. `sdma_v5_0.c` includes this header next to `gc_10_1_0_offset.h` and uses the same register database for SDMA ring setup, diagnostics, queue stop/restore, and golden register programming. KFD queue, MQD, packet manager, gfxhub, `nv.c`, and virtualization support also include this header.

## State And Persistence Behavior

The macros are stateless compile-time constants. They describe volatile hardware register state, but do not store state themselves and do not define reset values, access permissions, read side effects, write-one-to-clear behavior, ordering constraints, or persistence across GPU resets and power states.

Hardware state represented in this chunk includes:

- SDMA1 RLC6/RLC7 ring, IB, doorbell, polling, VMID, AQL, preemption, context status, context-save, and mid-command state. These values are part of SDMA queue execution and may be initialized by AMDGPU/KFD, changed during queue scheduling, and lost or restored across SDMA stop/start, GPU reset, or suspend/resume.
- GRBM status, per-SE busy state, soft-reset request bits, trap/error/IOV reporting, clock/power controls, scratch registers, fence ranges, and graphics-instance selection. Some fields are status-only snapshots; others are control or debug registers that influence global graphics behavior.
- CP engine state for CPC/CPF/MEC/ME/PFP/CE pipelines, including busy/stalled flags, queue availability, ring pointer status, instruction pointers, command-index/data access, halt/step/reset/cache-invalidate controls, and preemption state.
- VGT/WD/GE/IA state for front-end DMA, primitive, geometry, tessellation, UTCL1, FIFO, and shader-array configuration.
- PA/SC/CL/PH state for clipping, primitive assembly, setup/rasterizer enhancements, binning/PBB behavior, binner event routing, FIFO depths, EOV counters, sideband delays, and tile steering.

Persistence is determined by the underlying hardware block and driver sequencing. Queue pointers, doorbells, scratch registers, and context-save addresses can be meaningful across normal scheduling windows, while reset, power-gate, suspend/resume, and firmware-managed reinitialization paths may clear or rewrite them. Busy/status/error fields are generally live observations and should be treated as volatile.

## Dependencies And Integration Points

This chunk must stay synchronized with the GC 10.1.0 register database and companion generated headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h` supplies the matching `mm*` register offsets.
- `gc_10_1_0_default.h` provides default values for the same generation where emitted.
- Neighbor generation headers such as `gc_10_3_0_sh_mask.h`, `gc_11_0_0_sh_mask.h`, `gc_9_4_3_sh_mask.h`, and SDMA-specific headers expose similar field families with generation-specific differences.
- AMDGPU GFX10 code (`amdgpu/gfx_v10_0.c`) uses GRBM and CP fields for idle polling, soft reset, ring management, and debug.
- AMDGPU SDMA v5 code (`amdgpu/sdma_v5_0.c`) includes this header for SDMA queue/ring and diagnostic register handling.
- KFD GFX10 queue and MQD code includes this header for compute queue metadata and packet programming.
- `gfxhub_v2_0.c`, `mxgpu_nv.c`, `nv.c`, and `amdgpu_amdkfd_gfx_v10.c` also integrate the generated GC 10.1.0 field definitions.

The file depends on AMDGPU's register helper conventions rather than C type checking. A macro pair is usually consumed by token pasting from register and field names, so spelling, casing, and register prefix must exactly match the generated offset/default headers and the consumers' `REG_*_FIELD` invocations.

## Risks And Edge Cases

- The range begins mid-register: lines 5194-5195 contain the first two `SDMA1_RLC6_IB_CNTL` shifts, while this work item starts at line 5196. A merged report needs the previous lines for the complete start-of-register context.
- The range ends mid-register: line 7635 contains the last `PA_SC_TILE_STEERING_CREST_OVERRIDE` shift, while the corresponding masks start at line 7636. The next chunk must complete that register.
- The constants are untyped preprocessor values. An incorrect mask or shift can compile cleanly but program or decode the wrong hardware bit.
- This is generated hardware metadata. Manual edits risk divergence from AMD's authoritative register database, companion offset/default headers, firmware expectations, and silicon documentation.
- SDMA ring/IB/doorbell fields are sequencing-sensitive. Wrong pointer, base, swap, VMID, AQL, preemption, or writeback fields can break queue progress, corrupt command streams, lose completions, or produce hangs that only appear under KFD or multi-queue workloads.
- GRBM status and reset fields are used in recovery paths. Incorrect busy masks can cause false idle detection, skipped resets, excessive resets, or timeout loops during GPU reset and suspend/resume.
- CP busy/stalled, halt/step/reset, queue threshold, and ring pointer fields are tightly coupled with firmware and microcode. Misdecoding them can hide command processor hangs or force a pipeline into an unrecoverable state.
- Error, IOV, trap, and interrupt-related fields may be write-clear or latch hardware faults. Consumers need to preserve documented semantics rather than blindly read/modify/write every field.
- PA/VGT/WD/GE fields affect draw front-end, primitive assembly, binning, rasterization, and cache invalidation. Regressions may show as rendering corruption, hangs, performance cliffs, or failures only with specific primitive types, NGG/tessellation paths, MSAA/binning modes, or multi-SE/RB configurations.
- `RESERVED` fields appear throughout the chunk. Driver code should preserve them unless AMD generation-specific programming guidance says otherwise.
- Similar macro names exist across GC generations and SDMA standalone headers. Mixing a GC 10.1.0 mask with another generation's offset, or with a similarly named SDMA-specific header, may compile but target incompatible field layouts.

## Test Signals

Useful validation for this chunk and its consumers includes:

- Build AMDGPU/KFD configurations that include Navi/GFX10 and SDMA v5 support; missing or renamed macros should fail compilation in `gfx_v10_0.c`, `sdma_v5_0.c`, KFD queue/MQD code, gfxhub, and NV virtualization paths.
- Mechanically compare this range against AMD's GC 10.1.0 register database and `gc_10_1_0_offset.h` to confirm each register has the expected field layout and width.
- Diff repeated SDMA1 RLC6/RLC7 groups against neighboring RLC contexts and SDMA generation headers to catch copy or generator drift while allowing intentional per-generation differences.
- Run boot, modeset, suspend/resume, GPU reset, compute queue creation/destruction, SDMA copy/fill, KFD queue scheduling, and mixed graphics/compute workloads on hardware using this register generation.
- Exercise reset and hang-recovery paths and watch for `GRBM_STATUS` idle timeouts, incorrect `GRBM_SOFT_RESET` selection, repeated CP busy/stalled states, and failed SDMA queue stop/restore.
- Inspect debugfs or register dumps for decoded GRBM, CP, SDMA, VGT, WD, GE, PA, and SC fields. Known-good dumps should decode queue pointers, busy flags, thresholds, FIFO sizes, binning controls, and tile steering consistently with hardware documentation.
- Stress workloads involving doorbells, AQL queues, preemption, indirect buffers, write-pointer polling, VMID switching, cache invalidation, streamout events, binning/PBB, MSAA/rasterizer enhancements, tessellation, and multi-shader-engine routing.
- Monitor for rendering corruption, command processor hangs, SDMA timeouts, missing interrupts, KFD queue failures, false idle detection, reset failures, and performance regressions after any generator or header update.

## Cross-Chunk Notes

The previous chunk owns the beginning of `SDMA1_RLC6_IB_CNTL`, including the register comment and the `IB_ENABLE`/`IB_SWAP_ENABLE` shift lines. This chunk resumes with `SWITCH_INSIDE_IB` and completes most subsequent SDMA1 RLC6/RLC7 queue definitions.

This chunk stops at `PA_SC_TILE_STEERING_CREST_OVERRIDE__FORCE_TILE_STEERING_OVERRIDE_USE__SHIFT`. The next chunk owns the masks for `PA_SC_TILE_STEERING_CREST_OVERRIDE` and then enters the `gc_sqdec` shader-queue address block.

### subset-b-002452: lines 7636-10058

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 7636-10058

## Purpose

This chunk is a generated AMD GC 10.1.0 shift/mask header segment. It contains C preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for graphics-core hardware registers. The constants are consumed by AMDGPU and AMDKFD code together with the companion offset header; they are not executable logic by themselves.

The requested range covers 2,423 lines with 2,175 `#define` entries: 1,087 shift macros and 1,088 mask macros, plus 238 register or address-block comment markers. It starts at the mask half of `PA_SC_TILE_STEERING_CREST_OVERRIDE`, then covers GC register blocks for shader queues (`gc_sqdec`), shader processor interpolation/input (`gc_shsdec`), texture/data path control (`gc_tpdec`), global data share (`gc_gdsdec`), and render backend/raster memory layout (`gc_rbdec`). It ends after the complete `GB_TILE_MODE24` group; `GB_TILE_MODE25` begins in the next chunk.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMD GPU hardware metadata. It has no Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, runtime variables, includes, locks, allocations, or direct MMIO calls in this range. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit of a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the full bit mask for extracting, composing, or updating that field.
- Consumers typically combine these constants with `gc_10_1_0_offset.h` register addresses and AMDGPU helper macros such as `REG_GET_FIELD`, `WREG32_SOC15`, and `SOC15_REG_GOLDEN_VALUE`.

Important register families in this chunk are:

- PA/SC tile steering tail: `PA_SC_TILE_STEERING_CREST_OVERRIDE` masks describe one-RB override enable, shader-engine, render-backend, shader-array selection, and forced tile-steering override use. The corresponding shifts are just before this chunk.
- Shader queue and scalar cache setup: `SQ_CONFIG`, `SQC_CONFIG`, `LDS_CONFIG`, `SQ_RANDOM_WAVE_PRI`, `SQG_STATUS`, `SQ_FIFO_SIZES`, `SQ_ARB_CONFIG`, and `SQ_RUNTIME_CONFIG` define shader queue tuning, cache sizing, busy hysteresis, scheduling, retry/sleep, FIFO sizing, and status fields.
- Shader memory configuration: `SH_MEM_BASES` and `SH_MEM_CONFIG` define private/shared base fields and address-mode, alignment-mode, default memory type, retry mode, instruction prefetch, illegal-instruction check, and instruction-cache GL1 behavior. These fields are directly used by AMDKFD and GFX initialization when programming queue process state.
- SQ diagnostics and commands: `SQ_DSM_CNTL`, `SQ_DSM_CNTL2`, `SP_CONFIG`, `SQ_INTERRUPT_AUTO_MASK`, `SQ_INTERRUPT_MSG_CTRL`, `SQ_SHADER_TBA_*`, `SQ_SHADER_TMA_*`, `SQ_WATCH0..3_*`, `SQ_THREAD_TRACE_*`, `SQ_IND_*`, `SQ_CMD`, `SQ_TIME_*`, `SQ_LB_*`, `SQ_EDC_*`, and `SQ_WREXEC_*` cover DSM/error injection, shader trap memory, watchpoints, thread trace buffer programming/status/counters, indirect wave inspection, wave command dispatch, timing, load-balance counters, EDC counters, and WR execution address fields.
- UTCL0 and cache controls: `SQG_UTCL0_CNTL1/2`, `SQC_ICACHE_UTCL0_CNTL1/2`, `SQC_DCACHE_UTCL0_CNTL1/2`, and matching status registers expose GPUVM response/fault modes, VMID invalidation, force-miss/in-order behavior, FIFO/cache-size reductions, EDC disable, snoop and invalidate options, and fault/retry/PRT status.
- SPI/shader input control: `SX_DEBUG_1`, `SPI_PS_MAX_WAVE_ID`, `SPI_START_PHASE`, `SPI_GFX_CNTL`, `SPI_USER_ACCUM_VMID_CNTL`, `SPI_CONFIG_CNTL`, `SPI_CONFIG_CNTL_1/2`, `SPI_DSM_*`, `SPI_EDC_CNT`, `SPI_WAVE_LIMIT_CNTL`, lifetime limit/status registers, SPI load-balance counters, GDS credits, SX export/scoreboard sizes, CSQ wave-active counters, and trap-screen registers describe shader input scheduling, wave limits, debug/golden tuning, statistics, and per-process trap-screen memory bounds.
- Texture/data path control: `TD_CNTL`, `TD_STATUS`, `TD_POWER_CNTL`, `TD_DSM_*`, `TD_SCRATCH`, `TA_POWER_CNTL`, `TA_CNTL`, `TA_CNTL_AUX`, `TA_STATUS`, and `TA_SCRATCH` define sampler/data-path precision, float and gather modes, stall tuning, power/clock behavior, DSM injection, texture credits, deterministic sampler behavior, anisotropy controls, FIFO empty/busy status, and scratch fields.
- Global Data Share: `GDS_CONFIG`, `GDS_CNTL_STATUS`, `GDS_ENHANCE`, protection fault registers, VM protection fault registers, EDC counters, OA DED/PHY/pipe counters, DSM control, and `GDS_WD_GDS_CSB` describe GDS address/configuration, command/status, interrupt or watchdog behavior, VMID/client fault capture, EDC accounting, error injection, and debug readback.
- Render backend and depth buffer: `DB_DEBUG`, `DB_DEBUG2`, `DB_DEBUG3`, `DB_DEBUG4`, stutter controls, credits, watermarks, subtile controls, free cachelines, FIFO depths, last-of-burst behavior, ring control, memory arbitration watermarks, RMI/BC GL2 cache control, exception control, DFSM config/watchdog/flush controls, and fine-grain clock-gating SRAM/interface controls expose depth/stencil compression, HiZ/HiS, cache, coherency, burst, flush, clock, and watchdog tuning.
- Raster/backend address and tile layout: `CC_RB_REDUNDANCY`, `CC_RB_BACKEND_DISABLE`, `GB_ADDR_CONFIG`, `GB_BACKEND_MAP`, `GB_GPU_ID`, `CC_RB_DAISY_CHAIN`, `GB_ADDR_CONFIG_READ`, and `GB_TILE_MODE0` through `GB_TILE_MODE24` describe render-backend enablement, backend mapping, GPU ID, pipe/interleave/SE/RB layout, and indexed tile-mode fields such as array mode, pipe config, tile split, micro-tile mode, and sample split.

Most masks are 32-bit constants with an `L` suffix. Many registers are performance, diagnostics, or bring-up controls rather than normal hot-path state. Access type, reset values, write-one-to-clear behavior, self-clearing semantics, and valid power or clock domains are not encoded here.

## Control Flow

This header has no runtime control flow. It participates in a compile-time-to-runtime chain:

1. GFX10 AMDGPU and AMDKFD source files include `gc/gc_10_1_0_offset.h` and `gc/gc_10_1_0_sh_mask.h`.
2. Driver code builds register values by shifting symbolic field values with `__SHIFT` macros, masking or extracting values with `_MASK` macros, or using generated field helper macros.
3. Runtime sequencing in AMDGPU and AMDKFD writes or reads the associated MMIO registers during GPU initialization, golden-register programming, queue setup, KFD process setup, reset/resume, fault handling, profiling, and diagnostics.
4. Hardware and firmware implement the actual state machines for shader scheduling, memory translation, thread tracing, trap handling, texture/data-path processing, GDS operation, depth/stencil render-backend behavior, and tile/address mapping.

The macros here only describe bit layout. They do not enforce legal values, ordering, barriers, polling intervals, or ASIC-specific golden settings.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible fields whose persistence is governed by the GPU:

- Queue and process configuration state includes shader memory address mode, alignment, retry behavior, prefetch policy, trap base/mask addresses, watchpoint addresses/control, and SQ command fields.
- Debug/profiling state includes SQ thread-trace buffer base/size/write-pointer, trace masks, trace control/status, dropped and marker counters, indirect inspection indices/data, SQ and SPI load-balance counters, wave lifetime limits/status, and CSQ wave-active counters.
- Cache and virtual-memory state includes UTCL0 response/fault modes, VMID invalidation selectors/toggles, force miss/in-order flags, per-cache status bits, and GPUVM fault/retry/PRT indicators.
- Error handling state includes SQ, SPI, TD, and GDS DSM/error-injection controls, EDC counters, fatal/uncorrectable flags, protection-fault status, fault client and VMID capture, and render-backend exception controls.
- Graphics pipeline state includes SPI wave limits and shader input controls, texture sampler precision/determinism/power controls, GDS credits and command/status, depth-buffer compression/cache/coherency tuning, DB flush and watchdog controls, render-backend disable/redundancy state, address layout, backend map, and tile-mode tables.

Configuration fields usually remain until driver reprogramming, context or queue updates, power-gating transitions, suspend/resume, GPU reset, or ASIC reset. Status, fault, trace, counter, watchdog, and interrupt-like fields may be latched, clear-on-write, sampled, self-clearing, or valid only while the corresponding shader, texture, GDS, render-backend, or cache block is powered and clocked. Those semantics must come from hardware documentation and the runtime code, not this generated mask file.

## Dependencies And Integration Points

The direct compile-time dependency is the C preprocessor. The semantic dependency is AMD's GC 10.1.0 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h` supplies matching addresses such as `mmSQ_CONFIG`, `mmSPI_GFX_CNTL`, `mmTD_CNTL`, `mmGDS_CONFIG`, `mmDB_DEBUG`, `mmGB_ADDR_CONFIG`, and `mmGB_TILE_MODE24`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c` includes this header and uses these fields for default `SH_MEM_CONFIG`, golden-register programming for `DB_DEBUG*`, `SPI_CONFIG_CNTL_1`, `TA_CNTL_AUX`, and `GB_ADDR_CONFIG`, and runtime decoding of `GB_ADDR_CONFIG` fields such as pipe count, compressed fragments, RB-per-SE, shader-engine count, and pipe interleave size.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10.c` programs `mmSH_MEM_CONFIG` and emits `mmSQ_CMD` for KFD/GFX10 integration.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v10.c` builds queue-process `SH_MEM_CONFIG` values using this chunk's alignment and initial instruction prefetch shifts.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v10.c`, `kfd_packet_manager_v9.c`, `gfxhub_v2_0.c`, `mxgpu_nv.c`, `sdma_v5_0.c`, `mmhub_v2_0.c`, and `nv.c` include the same generated GC headers for broader GFX10/KFD/Navi integration.

Behaviorally, this range sits under several user-visible GPU features: compute process dispatch, memory model setup, wavefront control, shader trap/watchpoint/debugging, profiling/thread trace, GDS use, texture sampling correctness, depth/stencil rendering, render-backend topology, tiling/addressing, reset handling, and power-management tuning.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong bit position can compile cleanly while corrupting adjacent hardware fields or silently decoding status incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register source, the companion offset header, firmware expectations, and silicon behavior.
- The chunk starts with only the mask definitions for `PA_SC_TILE_STEERING_CREST_OVERRIDE`; its shift definitions are in the previous chunk. Whole-register analysis must merge across that boundary.
- The chunk ends cleanly after `GB_TILE_MODE24`; `GB_TILE_MODE25` and later tile modes are in the next chunk. Tile-mode table validation must account for the split.
- Several similarly named SQ, SQC, SQG, and SPI fields have different scopes. Mixing shader-queue, scalar-cache, UTCL0, and shader-input fields can produce hard-to-debug compute, graphics, or profiling failures.
- `SH_MEM_CONFIG` is shared by graphics and KFD process setup. Incorrect address, alignment, retry, or prefetch fields can affect compute memory semantics, XNACK/retry behavior, process isolation, and trap/debug behavior.
- Thread trace and indirect SQ access registers combine buffer address/size, masks, status, and command/index fields. Bad masks can overrun profiling buffers, target the wrong VMID or wave, or misreport dropped trace data.
- Fault and clear/status fields in UTCL0, GDS, DB, and EDC groups can be latched or side-effectful. Treating them as ordinary read/write fields risks losing fault evidence, leaving interrupts stuck, or clearing counters unintentionally.
- Render-backend debug and depth/stencil fields often disable optimizations or force cache/coherency behavior. Bad golden values or wrong masks can cause rendering corruption, hangs, performance regressions, or power regressions.
- `GB_ADDR_CONFIG` and `GB_TILE_MODE*` define memory layout and tiling interpretation. Errors can break framebuffer, texture, or render-target addressing across ASIC variants and may only reproduce with specific RB/SE/pipe configurations.
- Many controls are ASIC stepping and power-domain sensitive. A mask that appears harmless on one Navi/GFX10 variant can be invalid or reserved on another.

## Test Signals

Useful validation combines generated-header checks, build coverage, and GFX/KFD runtime tests:

- Build AMDGPU with GFX10 and AMDKFD enabled so includes from `gfx_v10_0.c`, `amdgpu_amdkfd_gfx_v10.c`, and KFD queue/MQD managers compile against `gc_10_1_0_sh_mask.h`.
- Statically verify that complete register groups in this chunk have matching shift and mask definitions, while allowing the known boundary case where `PA_SC_TILE_STEERING_CREST_OVERRIDE` shifts are outside this range.
- Cross-check complete register groups against `gc_10_1_0_offset.h`, especially `SQ_CONFIG`, `SH_MEM_CONFIG`, `SQ_CMD`, `SPI_CONFIG_CNTL`, `TA_CNTL_AUX`, `GDS_CONFIG`, `DB_DEBUG*`, `GB_ADDR_CONFIG`, and `GB_TILE_MODE0..24`.
- Diff repeated register families, such as `SQ_WATCH0..3`, `SQ_THREAD_TRACE_BUF0/1`, `SPI_WF_LIFETIME_LIMIT_0..9`, `SPI_WF_LIFETIME_STATUS_0..20`, `SPI_CSQ_WF_ACTIVE_COUNT_0..7`, and `GB_TILE_MODE0..24`, to catch generator drift.
- Run GFX10 boot, modeset, suspend/resume, GPU reset, and golden-register initialization paths; failures can indicate DB/SPI/TA/GB masks or offsets no longer match runtime programming.
- Run AMDKFD compute queue creation and dispatch tests that cover `SH_MEM_CONFIG`, `SQ_CMD`, trap handling, and VMID/process memory behavior.
- Exercise shader debugging, watchpoints, trap-screen setup, profiling, and SQ thread trace where available; inspect trace buffers, dropped counters, marker counters, indirect wave data, and status fields for sane decoding.
- Exercise graphics workloads with depth/stencil, HiZ/HiS, MSAA, varied render-target tile modes, multiple RB/SE layouts, and reset/recovery scenarios to catch `DB_*`, `GB_ADDR_CONFIG`, and `GB_TILE_MODE*` issues.
- Use register dumps on failures to confirm `REG_GET_FIELD` and update helpers decode `GB_ADDR_CONFIG`, `SH_MEM_CONFIG`, GDS protection faults, UTCL0 fault status, DB exceptions, and EDC counters with the expected masks.

## Cross-Chunk Notes

The previous chunk owns the `PA_SC_TILE_STEERING_CREST_OVERRIDE` shift definitions and earlier PA/SC registers. This chunk contributes that register's masks, then covers full logical blocks from `gc_sqdec`, `gc_shsdec`, `gc_tpdec`, `gc_gdsdec`, and the start of `gc_rbdec` through `GB_TILE_MODE24`. The next chunk should continue the render-backend tile-mode table at `GB_TILE_MODE25`. The later merge/reconciliation lane should combine these boundaries before making whole-file claims about complete PA/SC and GB tile-mode coverage.

### subset-b-002453: lines 10059-12432

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 10059-12432

## Scope

This chunk is a middle segment of the generated AMD GC 10.1.0 shift/mask header. It covers line 10059 through line 12432 and defines 2,182 preprocessor constants: 1,089 `__SHIFT` macros and 1,093 `_MASK` macros, plus address-block and register-group comments. The slice starts in the tail of `GB_TILE_MODE24` with `SAMPLE_SPLIT` and its masks, then covers `GB_TILE_MODE25` through `GB_TILE_MODE31`, all `GB_MACROTILE_MODE0` through `GB_MACROTILE_MODE15`, color-buffer controls, GCEA/SDP request and error-reporting controls, SPI system knobs, RMI controls/status, PMM/GCR controls, UTCL1 controls, ATC L2 controls, GCVM L2 controls, and complete `GCVM_CONTEXT0_CNTL` and `GCVM_CONTEXT1_CNTL` definitions. It ends exactly at the `//GCVM_CONTEXT2_CNTL` marker, before that context's fields.

The content is declarative only. There are no C functions, structs, enums, branches, loops, allocations, or local runtime side effects. The exported surface is a generated macro namespace that tells driver code where each hardware register bitfield lives.

## Purpose

`gc_10_1_0_sh_mask.h` provides symbolic bit positions and bit masks for Graphics Core 10.1.0 registers. Consumers pair these macros with register offsets from `gc_10_1_0_offset.h` and access helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15` to build or decode MMIO register values without embedding raw shifts and masks in driver logic.

This chunk is primarily about memory layout, graphics backend behavior, graphics memory fabric controls, and GPU virtual-memory translation:

- `GB_TILE_MODE*` and `GB_MACROTILE_MODE*` describe surface tiling and macrotiling layout fields.
- `CB_*` and `GC_USER_RB_*` describe color-buffer cache, DCC, memory-arbiter, stutter, eviction, render-backend redundancy, and backend-disable controls.
- `GCEA_*` and `SPI_*` cover graphics command/error/address-decode plumbing, SDP credits, latency sampling, performance counters, EDC/DSM diagnostic controls, DRAM/GMI/IO arbitration, probe mapping, error status, and small SPI queue/compute knobs.
- `RMI_*`, `PMM_*`, `GCR_*`, and `UTCL1_*` describe request/return memory interface behavior, crossbar arbitration, VMID invalidation scoreboarding, clock gating, PIO/GCR controls, target disable masks, UTCL1 cache and invalidation controls, and address-log controls.
- `GC_ATC_L2_*` and `GCVM_L2_*` define ATC/GPUVM L2 cache, fault, invalidation, parity, fragment-size, group real-time class, clock-gating, and walker throttling fields.
- `GCVM_CONTEXT0_CNTL` and `GCVM_CONTEXT1_CNTL` define per-context enable, page-table shape, retry, and protection-fault policy fields.

## Exported API Surface

There are no callable APIs or local data types. The public interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low-bit position.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted register mask for the field.

Important macro families in this chunk include:

- `GB_TILE_MODE24` through `GB_TILE_MODE31`: `ARRAY_MODE`, `PIPE_CONFIG`, `TILE_SPLIT`, `MICRO_TILE_MODE_NEW`, and `SAMPLE_SPLIT`. These fields encode graphics surface tile layout choices consumed by address calculations and metadata programming.
- `GB_MACROTILE_MODE0` through `GB_MACROTILE_MODE15`: `BANK_WIDTH`, `BANK_HEIGHT`, `MACRO_TILE_ASPECT`, and `NUM_BANKS`. These define macrotiling geometry used with the tile-mode table.
- `CB_HW_CONTROL`, `CB_HW_CONTROL_1` through `_4`, `CB_DCC_CONFIG`, `CB_HW_MEM_ARBITER_RD`, `CB_HW_MEM_ARBITER_WR`, `CB_RMI_BC_GL2_CACHE_CONTROL`, `CB_STUTTER_CONTROL_*`, and `CB_CACHE_EVICT_POINTS`: color-buffer cache sizing, feature-disable, optimization, arbitration, DCC, cache-policy, latency, and eviction fields.
- `GC_USER_RB_REDUNDANCY` and `GC_USER_RB_BACKEND_DISABLE`: render-backend repair, redundancy, and backend-disable fields.
- `GCEA_*`: graphics command/error/address-decode controls for SDP request pass-through overrides, virtual-channel credits, DRAM/GMI/IO arbitration, latency sampling, performance-counter selection, EDC counters, DSM single-write/error injection controls, GL2C crossbar credits and max burst, probe mapping, error status, DRAM bank arbitration, address-hash/select controls, and SDP enable.
- `SPI_PQEV_CTRL`, `SPI_SYS_COMPUTE`, and `SPI_SYS_WIF_CNTL`: small SPI queue-duration, compute-pipe, and WIF threshold fields.
- `RMI_*`: RMI general controls, status, subblock status, crossbar muxing, probe pop logic, XNACK/misc controls, demux and xbar arbiters, UTCL1 controls, TCIW formatter controls, scoreboard controls/status, dynamic-clock control, client-ID maps, spare bits, and RMI redundancy.
- `PMM_*` and `GCR_*`: PMM mode/disable controls, GCR PIO indexing/status/data, general GCR request behavior, target-disable masks, command status, and spare bits.
- `UTCL1_*`: UTCL1 page-size, bypass, cache, invalidation, memory-hub, address-log, and target-disable fields.
- `GC_ATC_L2_*`: ATC translation request limits, cache update modes, cache data readout words, invalidate delay, ATS request credits, parity/status, memory light sleep, clock control, and SDP port clock-enable fields.
- `GCVM_L2_*` and `GCVML2_WALKER_*`: GPUVM L2 enable, cache-policy, invalidation, status, dummy page, protection-fault control/status/address, identity aperture, cache partitions, group real-time classes, reserved client IDs, parity test controls, clock gating, fragment size, GCR client, and walker throttle fields.
- `GCVM_CONTEXT0_CNTL` and `GCVM_CONTEXT1_CNTL`: context enable, page-table depth/block size, retry policy, and interrupt/default behavior for range, dummy page, PDE0, valid, read, write, and execute protection faults.

## Control Flow And State Behavior

This header has no local control flow. Runtime control flow appears when AMDGPU and KFD code include the generated constants and use them in read-modify-write sequences against GC 10.1.0 registers.

The field families imply several hardware state machines and persistent hardware states:

- Tile and macrotile mode registers hold layout table entries that influence how the graphics block interprets color/depth metadata and surface addresses. Their state persists in the hardware register file until reset or reprogramming.
- Color-buffer and RMI controls affect cache, DCC, write-combine, early write-ack, arbitration, stutter, clock-gating, and backend repair behavior. These are global or semi-global graphics-pipeline settings rather than per-process software state.
- GCEA performance, EDC, DSM, probe, and error-status registers expose diagnostic state. Some fields count errors, inject errors, clear status, select counters, or indicate busy/error conditions; consumers must know whether fields are write-one-to-clear, sticky, read-only, or destructive from the hardware spec.
- RMI, GCR, UTCL1, ATC L2, and GCVM L2 fields encode virtual-memory translation behavior, invalidation, XNACK/retry behavior, cache and fragment-size policy, parity testing, walker throttling, and fault reporting. Incorrect sequencing here can affect all queues using the graphics hub.
- `GCVM_CONTEXT0_CNTL` and `GCVM_CONTEXT1_CNTL` are context-policy registers. They determine whether a VM context is enabled, the page-table layout expected by hardware, which protection faults raise interrupts, which use default pages, and whether retry behavior is enabled.

No software persistence is implemented here. Persistence is the hardware register contents themselves, managed by ASIC reset domains, suspend/resume save/restore, golden-register programming, VM hub initialization, and any runtime KFD/AMDGPU register writes.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. Semantically, this chunk depends on the companion offset header `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h`, which provides matching `mm...` register addresses such as `mmGB_TILE_MODE25`, `mmGCEA_SDP_REQ_CNTL`, `mmRMI_GENERAL_CNTL`, `mmGC_ATC_L2_CNTL`, and `mmGCVM_CONTEXT0_CNTL`.

Direct include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_0.c`, which includes this header and uses `GCVM_CONTEXT0_CNTL` fields to enable context 0, set page-table depth/block size, compute context register distance, and program VM hub context registers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v10.c`, `kfd_mqd_manager_v10.c`, and `kfd_packet_manager_v9.c`, which include the GC 10.1.0 shift/mask namespace for queue and memory-management programming.

Related integration points include AMDGPU VM hub initialization, KFD process/queue setup, GPUVM invalidation and retry-fault handling, golden-register programming, render-backend harvesting/repair, color-buffer cache/DCC setup, RMI arbitration, ATC L2 translation behavior, and low-level diagnostics for parity, EDC, DSM, probes, and performance counters.

## Risks

- Generated-header drift is the main risk. A wrong shift or mask can silently program adjacent bits in tiling, backend disable, cache policy, invalidation, or VM fault-control registers.
- The file gives status, control, clear, inject, and reserved fields the same macro shape. Driver code must rely on hardware documentation and existing access helpers to avoid writing read-only, sticky, clear-on-read, or write-one-to-clear fields incorrectly.
- VM context and L2 fields are high blast-radius controls. Bad values in `GCVM_L2_CNTL*`, `GCVM_L2_PROTECTION_FAULT_*`, `GCVM_INVALIDATE_CNTL`, or `GCVM_CONTEXT*_CNTL` can cause page faults, incorrect retry behavior, stale translations, dummy-page use where faults were expected, or GPU hangs.
- Tile and macrotiling definitions need to remain consistent with the address library and firmware expectations. Incorrect `ARRAY_MODE`, `PIPE_CONFIG`, `TILE_SPLIT`, bank geometry, or sample-split masks can present as data corruption rather than an immediate register-programming failure.
- Error injection and parity-test fields, such as DSM controls and `GCVM_L2_CACHE_PARITY_CNTL`, are dangerous if enabled outside validation paths.
- Many controls are global to graphics or memory-fabric behavior. A change made for one queue, context, or workload can affect unrelated graphics and compute clients.
- This slice starts and ends at chunk boundaries inside register groups: `GB_TILE_MODE24` is only partially covered here, and `GCVM_CONTEXT2_CNTL` only appears as a marker with its definitions in the next chunk.

## Test Signals

Useful validation is mostly build-time, generation-time, and hardware-integration oriented:

- Compile or preprocess AMDGPU and KFD code paths that include `gc_10_1_0_offset.h` and `gc_10_1_0_sh_mask.h`, especially `gfxhub_v2_0.c` and KFD v10 queue/MQD/packet managers.
- Generation checks that complete register groups in the full header have matching `__SHIFT` and `_MASK` definitions, with explicit chunk-boundary exceptions for the tail of `GB_TILE_MODE24` and the marker-only `GCVM_CONTEXT2_CNTL`.
- Cross-check this header against the GC 10.1.0 register database and companion offset names.
- Runtime VM tests on GC 10.1.0-class hardware: VM context enablement, page-table depth/block-size programming, VMID invalidation, retry faults, no-retry faults, dummy-page behavior, read/write/execute protection faults, XNACK behavior, and suspend/resume restoration.
- Graphics memory-layout tests: color/depth rendering with tile modes 24-31, DCC/CMASK/FMASK paths, backend-disable/harvesting configurations, and cache eviction/stutter behavior.
- Diagnostics and fault-injection validation: EDC counters, DSM injection paths, GCVM L2 parity controls, GCEA/RMI error status, performance-counter selection, and register readback of clear/status behavior.

## Chunk Notes For Merge

This document is source-tree aligned and covers only lines 10059-12432 of `gc_10_1_0_sh_mask.h`. Earlier chunks should cover the beginning of `GB_TILE_MODE24` and prior GC register groups. Later chunks should start with the `GCVM_CONTEXT2_CNTL` definitions and continue the GCVM context/register map. The final per-file report should treat the whole file as a generated ASIC register bitfield map for AMD GC 10.1.0 programming, not as handwritten runtime logic.

### subset-b-002454: lines 12433-14880

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 12433-14880

## Scope

This chunk is a middle segment of the generated AMD GC 10.1.0 shift/mask header. It covers line 12433 through line 14880 and defines 1,064 `__SHIFT` macros and 1,088 `_MASK` macros across 314 visible register groups. The range begins inside the `GCVM_CONTEXT2_CNTL` field list, continues through GCVM context, invalidation, page-table address, shared GCMC aperture/TLB, and GCEA memory-client arbitration/address-decode fields, and ends inside `GCEA_ADDRDEC1_ADDR_MASK_SECCS01` before the following `SECCS23` and later address-decode fields.

The content is declarative only. There are no C functions, structs, enums, branches, loops, allocations, locks, or software-side side effects. The exported surface is a set of preprocessor constants that describe bit positions and masks for GC 10.1.0 memory-mapped registers.

## Purpose

`gc_10_1_0_sh_mask.h` supplies symbolic bitfield definitions for AMDGPU and KFD code that targets Navi/GC 10.1.0 register layouts. Consumers pair these macros with offsets from `gc_10_1_0_offset.h` and use helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, and `RREG32_SOC15` to program GPU VM contexts, invalidate VM translation caches, configure system/frame-buffer apertures, and tune GC memory-client arbitration and physical DRAM address decode without embedding raw bit numbers in driver logic.

This slice focuses on three major hardware surfaces:

- GCVM per-VMID context state, including context enable, page-table depth/block size, retry behavior, and per-fault interrupt/default routing.
- GCVM invalidate engines, including per-engine semaphores, invalidate request fields, acknowledgement bits, and optional logical page address ranges.
- GCMC and GCEA address/aperture/memory-client controls, including NB MMIO/DRAM aperture registers, system aperture/default address fields, L1 TLB control, DRAM client-to-group mappings, priority/arbitration coefficients, normalized address ranges, DRAM holes, bank/hash/harvest controls, and chip-select address decode fields.

## Exported API Surface

There are no callable APIs or local types. The public interface is the generated macro namespace:

- `GCVM_CONTEXT2_CNTL` through `GCVM_CONTEXT15_CNTL`: repeated VM context-control fields for enabling contexts, selecting page-table geometry, configuring retry behavior, and selecting interrupt/default behavior for range, dummy-page, PDE0, valid, read, write, and execute protection faults.
- `GCVM_CONTEXTS_DISABLE`: one disable bit per context 0 through 15.
- `GCVM_INVALIDATE_ENG0_SEM` through `GCVM_INVALIDATE_ENG17_SEM`: single-bit semaphore fields for 18 invalidation engines.
- `GCVM_INVALIDATE_ENG0_REQ` through `GCVM_INVALIDATE_ENG17_REQ`: invalidate request fields for per-VMID invalidation, flush type, L2 PTE invalidation, PDE0/PDE1/PDE2 invalidation, L1 PTE invalidation, protection-fault status-address clearing, and 4K-page-only invalidation.
- `GCVM_INVALIDATE_ENG0_ACK` through `GCVM_INVALIDATE_ENG17_ACK`: per-VMID acknowledge fields for invalidation completion.
- `GCVM_INVALIDATE_ENG0_ADDR_RANGE_*` through `GCVM_INVALIDATE_ENG17_ADDR_RANGE_*`: low/high logical page address range fields, split into `S_BIT`, low 31 bits, and high 5 bits.
- `GCVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_*` through `GCVM_CONTEXT15_PAGE_TABLE_BASE_ADDR_*`: 64-bit page-directory-entry base addresses split into low/high 32-bit register fields.
- `GCVM_CONTEXT0_PAGE_TABLE_START_ADDR_*` and `GCVM_CONTEXT0_PAGE_TABLE_END_ADDR_*` through context 15: logical-page-number aperture start/end fields, split into low 32 bits and high 4 bits.
- `GCMC_VM_*`: shared PF/VC decoder fields for MMIO base/limit, PCI control/arbitration, DRAM top, frame-buffer offset/location, system aperture default/low/high address, steering, reset request, memory power, cacheable DRAM ranges, APT control, local HBM address lock/range, and `GCMC_VM_MX_L1_TLB_CNTL`.
- `GCEA_DRAM_*`: DRAM read/write client mapping, group-to-VC mapping, lazy timing, CAM depth/reorder controls, page-burst limits, aging/queueing/fixed/urgency coefficients, and quantum-priority thresholds.
- `GCEA_ADDRNORM*` and `GCEA_ADDRDEC*`: normalized address base/limit/offset, DRAM hole, NP2 channel space, bank and misc masks, DRAM hash/harvest fields, and address-decode base/mask/config/selection registers for chip-select and secondary chip-select groups.

Most complete register groups follow the generated pair pattern `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. This chunk has intentional boundary exceptions: it begins after the `GCVM_CONTEXT2_CNTL` comment and ends before the complete `GCEA_ADDRDEC1_ADDR_MASK_SECCS01`/later address-decode sequence.

## Control Flow And State Behavior

This header has no local control flow. Runtime behavior appears only when driver code includes the generated constants and uses them in MMIO read-modify-write or direct write sequences.

The field names describe several hardware-controlled state machines and persistent register banks:

- VM context programming: each VMID context holds a page-table root, start/end logical-page range, enable bit, page-walk depth, page-table block size, and fault handling policy. The corresponding hardware state persists until reset, power-domain loss, driver reprogramming, or firmware/golden-register restore.
- Fault handling: context-control fields select whether range, dummy-page, PDE0, valid, read, write, and execute faults interrupt the driver or resolve through a default path. Retry fields interact with XNACK/no-retry behavior exposed through KFD per-process state.
- Translation invalidation: invalidate engines use semaphore, request, acknowledge, and optional range registers. Software composes a request word, writes the appropriate engine request register, and waits for the matching acknowledgement path outside this header.
- Aperture and TLB configuration: GCMC registers define frame-buffer, AGP, system aperture, default page address, cacheable DRAM windows, local HBM windows, and L1 TLB behavior. These are global memory-controller state, not per-process data.
- GCEA arbitration and address decode: DRAM read/write client maps, VC maps, priority coefficients, CAM limits, and address-normalization/decode/hash settings shape how GC memory traffic is routed and scheduled. These settings are hardware configuration state and may be established by firmware, BIOS, golden-register tables, or early driver init depending on ASIC mode.

Readback/status semantics are not encoded by the macro names alone. Fields named `ACK`, `STATUS`, or `*_OUT` are likely readback-oriented by naming convention, while `REQ`, `CNTL`, `BASE`, `LIMIT`, `MASK`, `CFG`, and priority fields are configuration-oriented. Actual read-only, write-only, sticky, clear-on-read, and reset semantics must come from the register database and calling driver code.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. Semantically, these macros are tied to the matching GC 10.1.0 register offsets in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h` and defaults in `gc_10_1_0_default.h`.

Important integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_0.c`, which includes this header and uses the GCVM invalidation, context-control, page-table base/start/end, GCMC frame-buffer/system aperture, and TLB fields during GFXHUB VM setup. It also derives `ctx_distance`, `ctx_addr_distance`, `eng_distance`, and `eng_addr_distance` from adjacent offsets and builds a VM fault interrupt mask from `GCVM_CONTEXT1_CNTL` masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v12_1.c` and related KFD queue-manager files, which use context retry bits together with per-process XNACK/retry policy.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0.c` and `imu_v11_0_3.c`, whose IMU/RLC golden-register tables include `GCVM_CONTEXT*_CNTL` and `GCEA_DRAM_PAGE_BURST` programming values.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c`, KFD packet/MQD management, and other GC 10.x code that includes the same generated namespace for graphics and compute queue bring-up.

At runtime the macros feed AMDGPU's register helper layer, VM hub initialization, GART aperture setup, system aperture setup, VMID context configuration, TLB/cache invalidation, suspend/resume restore, SR-IOV PF/VF split handling, and hardware fault reporting.

## Risks

- Generated-header drift is the primary risk. A wrong shift or mask can silently program the wrong VM context bit, fault policy, invalidation request field, aperture field, or DRAM address-decode bit.
- The VM context groups are highly repetitive. Driver code often programs context 1 and then walks adjacent contexts by offset distance; inconsistent context register spacing or a wrong context-specific macro can produce VMID-dependent faults.
- Invalidation request construction is sensitive to bit placement. Missing `INVALIDATE_L1_PTES`, `INVALIDATE_L2_PTES`, PDE bits, or using an incorrect `PER_VMID_INVALIDATE_REQ` mask can leave stale translations after page-table updates.
- Retry/no-retry behavior affects fault storms and process-visible XNACK behavior. Incorrect `RETRY_PERMISSION_OR_INVALID_PAGE_FAULT` handling can break KFD process isolation, recoverability, or performance.
- Page-table base/start/end fields are split across registers. Bad high/low masking or shifting can expose the wrong virtual address range or page-table root.
- GCMC aperture and default-address registers affect global memory routing. Incorrect frame-buffer, AGP, system aperture, or dummy/default page programming can convert invalid GPU accesses into host-memory corruption, unexpected VRAM access, or unrecoverable faults.
- GCEA DRAM arbitration and address-decode fields are low-level memory-controller configuration. Mistakes in bank, chip-select, row/column, hash, harvest, or priority fields may only reproduce as performance loss, ECC/RAS-like symptoms, data corruption, or ASIC-specific boot failures.
- Some registers are likely firmware- or PF-owned in SR-IOV and power-management modes. Blind writes from a VF or late driver path can conflict with PF/firmware ownership.
- This slice starts and ends at chunk boundaries inside register groups, so merge-time validation should not treat missing comments or trailing pairs at the boundaries as local omissions.

## Test Signals

Useful validation is mostly build-time, generated-data, and hardware-integration oriented:

- Compile or preprocess AMDGPU/KFD code paths that include `gc_10_1_0_offset.h`, `gc_10_1_0_sh_mask.h`, and `gc_10_1_0_default.h`.
- Static generation checks that complete register groups in the full header have matching `__SHIFT` and `_MASK` definitions, with explicit chunk-boundary exceptions for the start at `GCVM_CONTEXT2_CNTL` and the end at `GCEA_ADDRDEC1_ADDR_MASK_SECCS01`.
- Cross-check this chunk against the GC 10.1.0 register database and matching offset/default headers for register name alignment and field width consistency.
- VM bring-up tests on GC 10.1.0-class hardware: GART setup, VMID context programming, user queue creation, page-table root updates, VM fault interrupt/default routing, and per-process XNACK/no-retry behavior.
- Translation invalidation tests: update PTEs/PDEs, issue VMID and range invalidations, verify acknowledge completion, and check that stale translations do not survive context switches or queue submissions.
- Suspend/resume, GPU reset, SR-IOV VF/PF, and firmware restore tests that confirm GCVM/GCMC/GCEA state is either restored by the driver or intentionally owned by firmware/PF.
- Fault-injection and diagnostics: trigger read/write/execute/valid/PDE faults and confirm fault reporting, default-page routing, fault-status clearing, and retry behavior match the expected policy.
- Memory-controller validation: bandwidth and latency tests across read/write clients, page-burst and priority settings, VRAM/HBM aperture boundaries, and address-decode/hash/harvest configurations on affected ASIC revisions.

## Chunk Notes For Merge

This document is intentionally source-tree aligned and covers only lines 12433-14880 of `gc_10_1_0_sh_mask.h`. Earlier chunks should cover the beginning of `GCVM_CONTEXT2_CNTL` and prior GCVM/L2 fields. Later chunks should continue `GCEA_ADDRDEC1_ADDR_MASK_SECCS01`, the remaining address-decode fields, and subsequent GC register groups. The final per-file report should treat the whole file as a generated GC 10.1.0 register bitfield map used by AMDGPU and KFD hardware programming paths, not as handwritten executable logic.

### subset-b-002455: lines 14881-17383

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 14881-17383

## Scope

This chunk is a generated AMD GC 10.1.0 shift/mask header slice. The requested range spans 2,503 source lines, 2,134 `#define` entries, 1,067 `__SHIFT` definitions, 1,067 matching `_MASK` definitions, and 365 visible register-group comments. It starts at `GCEA_ADDRDEC1_ADDR_MASK_SECCS23` and ends on the `COMPUTE_USER_DATA_0` comment, before that compute user-data register's field definitions appear.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU graphics/compute hardware metadata. It is declarative C preprocessor data for GC 10.1.0 register bitfields, not Ceph or distributed-filesystem logic.

## Purpose

`gc_10_1_0_sh_mask.h` gives AMDGPU and AMDKFD code symbolic bit positions and masks for GC 10.1.0 registers. Consumers combine these constants with companion register offsets from `gc_10_1_0_offset.h` and with MMIO/register helper macros to compose, update, and decode hardware register values without open-coding raw bit numbers.

This chunk covers four major register areas:

- `GCEA_*`: graphics client external/address and I/O arbitration metadata, including address decode selectors, client-to-group mappings, read/write combine flushing, burst control, priority age/queue/fixed/urgency controls, urgency masking, quantized priority, SDP arbitration, credits, tag reserves, and VCC/VCD reserves.
- `TCP_*` and `TCI_*`: texture/cache control and status fields for invalidation, force hit/miss behavior, buffer address hashing, EDC counters, credits, and TCI control.
- `SPI_SHADER_*`: graphics shader program state for pixel, vertex, geometry, export, hull, and local shader stages, including program base addresses, resource words, checksums, user data registers, shader request controls, preferred-priority counters, accumulators, and cross-stage resource words such as GS/VS, ES/GS, and LS/HS.
- `COMPUTE_*`: compute dispatch state, dimensions, starts, thread counts, program resources, VMID, CU enable/static-thread-management masks, temp ring sizing, restart coordinates, tracing, dispatch IDs, request controls, priority accumulators, checksum, relaunch, and wave restore address fields.

## Important APIs, Types, And Macros

There are no callable functions, structs, enums, global variables, allocations, locks, or runtime register accesses in this range. The exported interface is only generated preprocessor constants of the form:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a field inside a GC 10.1.0 register.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field inside the same register.

Important macro families include:

- `GCEA_ADDRDEC1_*`: chip-select and secondary chip-select address masks, address geometry fields such as bank groups, rows, columns, banks, high-column enable, row/bank/column selection fields, row-map selection, channel bit, and even/odd row-MSB inversion.
- `GCEA_IO_*`: read/write client-to-group maps for 32 client IDs, combine flush controls, group burst enable, priority aging, queueing, fixed priority, urgency thresholds, urgency masks per CID, and priority quantum fields.
- `GCEA_SDP_*`: DRAM and final arbitration weights, urgency override/age/limit thresholds, page-hit sensitivity, per-source DRAM and I/O priorities, credit counts, tag reserve windows, and VCC/VCD reserve fields.
- `TCP_*` and `TCI_*`: invalidation command, busy and last-vmid status, forced cache hit/miss controls, cache sizing/swizzle/hash controls, EOW counts, EDC count, credit count, and TCI miscellaneous control fields.
- `SPI_SHADER_PGM_*_{PS,VS,GS,ES,HS,LS}`: shader program base low/high addresses, resource words for VGPR/SGPR counts, priority, float mode, privilege, DX10 clamp, IEEE mode, scratch/user-SGPR/trap/exception/LDS fields, wave limits, CU enables, WGP or shared VGPR controls, and program checksum fields.
- `SPI_SHADER_USER_DATA_*`: per-stage user-data payload registers. PS, VS, GS, and HS expose 32 user data slots in this slice; ES and LS expose 16 slots.
- `SPI_SHADER_REQ_CTRL_*`, `SPI_SHADER_PREF_PRI_*`, and `SPI_SHADER_USER_ACCUM_*`: shader request grouping, allocation throttling, lock thresholds, preferred-priority counter hierarchy/coefficient fields, and user/preferred contribution accumulators for PS, VS, ESGS, and LSHS.
- `COMPUTE_*`: dispatch initiator bits, dimensions/start/restart registers, thread count split fields, pipeline/perf counter enables, program and dispatch packet addresses, scratch base, program resource words, VMID, resource limits, shader-engine CU enables, static thread-management masks, temp-ring sizing, request controls, accumulators, checksum, relaunch payload/type bits, and wave restore address fields.

The chunk ends after the `COMPUTE_USER_DATA_0` comment only. The `COMPUTE_USER_DATA_0` field definitions are owned by the next chunk.

## Control Flow

This header has no local control flow. Runtime behavior comes from AMDGPU and AMDKFD code that includes this header and writes GC registers or queue descriptors using the generated constants.

Typical usage is:

1. A GC 10.1.0 driver file includes `gc_10_1_0_offset.h` and `gc_10_1_0_sh_mask.h`.
2. Driver code builds a register value by shifting a field value by `<REGISTER>__<FIELD>__SHIFT` and masking with `<REGISTER>__<FIELD>_MASK`, or it passes these constants to AMD register update macros.
3. The value is written to MMIO registers, firmware-visible MQD fields, or command/queue state that the GPU consumes.
4. Hardware graphics, compute, cache, arbitration, and shader-dispatch state machines interpret those bits.

The header does not encode ordering constraints, polling loops, access widths, reset values, clear-on-read/write-one-to-clear behavior, or privilege rules. Those semantics live in the hardware database and in consumers such as `gfx_v10_0.c`, KFD queue/MQD management, gfxhub setup, SDMA setup, and SR-IOV code.

## State And Persistence Behavior

No software state is stored or persisted by this chunk. The named fields describe hardware-visible register state whose lifetime is governed by GC reset, power, queue, VM, and firmware domains.

State described by the chunk includes:

- Address decode and memory-routing configuration in `GCEA_ADDRDEC1_*`, including chip-select geometry and bank/row/column selection. Incorrect values affect how physical addresses are interpreted by the graphics memory path.
- I/O arbitration state in `GCEA_IO_*` and `GCEA_SDP_*`, including client grouping, burst control, priority, urgency, credit, and reserve tuning. These fields affect fairness, latency, and throughput rather than data structure persistence in software.
- Texture/cache state in `TCP_*` and `TCI_*`, including invalidation commands, busy/status readback, credits, hash controls, and EDC counters.
- Graphics shader execution state in `SPI_SHADER_*`, including per-stage program locations, resource allocation, wave limits, CU masks, user data payloads, scratch/trap/exception/LDS fields, and priority accounting.
- Compute dispatch state in `COMPUTE_*`, including dispatch geometry, shader entry point, scratch base, resource usage, VMID, CU targeting, restart coordinates, relaunch/wave-restore support, and tracing/performance enables.

Fields named `STATUS`, `BUSY`, `CNT`, `COUNT`, `CHECKSUM`, `ID`, `THREADGROUP_ID`, or `*_ACCUM_*` are readback or accounting oriented by name. Fields named `CNTL`, `CTRL`, `CFG`, `SEL`, `MASK`, `LIMITS`, `EN`, `ENABLE`, `INITIATOR`, `PREF_PRI`, and `RESOURCE` are configuration oriented by name. Actual read/write permissions and sticky behavior must be taken from the hardware specification and caller context.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. Semantically, this generated header must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h`, which supplies matching register offsets and base-index values.
- AMD's GC 10.1.0 register database and any scripts that generate offset and shift/mask headers.
- Firmware and queue descriptor layouts for GFX10/Navi-class graphics and compute engines, especially where KFD MQD fields mirror hardware register fields.

Direct include sites in this tree include `amdgpu/gfx_v10_0.c`, `amdgpu/gfxhub_v2_0.c`, `amdgpu/nv.c`, `amdgpu/mxgpu_nv.c`, `amdgpu/amdgpu_amdkfd_gfx_v10.c`, `amdgpu/sdma_v5_0.c`, `amdkfd/kfd_mqd_manager_v10.c`, `amdkfd/kfd_device_queue_manager_v10.c`, and `amdkfd/kfd_packet_manager_v9.c`. These consumers use the GC 10.1.0 register contract for graphics initialization, queue setup, KFD compute queue descriptors, VM/gfxhub programming, SDMA integration, SR-IOV virtualization, and runtime register programming.

Behaviorally, this chunk integrates with:

- Graphics pipeline programming for PS, VS, GS, ES, HS, and LS shader stages.
- Compute dispatch and KFD queue setup, including resource words, static CU masks, scratch, temp-ring, VMID, dispatch geometry, and trap/exception controls.
- Cache and memory-system management, including TCP invalidation/status and address decode/arbitration settings.
- Priority, scheduling, and resource allocation controls for graphics and compute waves.
- GPU reset, suspend/resume, firmware bring-up, and virtualization paths that must restore or sanitize hardware state.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong shift or mask compiles cleanly but can write the wrong shader resource, dispatch, cache-control, address-decode, or arbitration bit.
- This range starts at a normal register group but ends on a register comment with no fields for `COMPUTE_USER_DATA_0`. The final per-file merge must avoid treating that as an empty register definition.
- `_MASK` macro naming uses the generated AMD convention where field names ending in `MASK` produce names such as `GCEA_ADDRDEC1_ADDR_MASK_SECCS23__ADDR_MASK_MASK`; tooling must not collapse those suffixes.
- Shader resource words are dense and stage-specific. PS, VS, GS, ES, HS, LS, and compute registers share similar field names but not always identical layouts, so cross-stage copy assumptions can corrupt program resource setup.
- Compute resource fields such as `TGID_*_EN`, `TIDIG_COMP_CNT`, `LDS_SIZE`, `EXCP_EN`, `WGP_MODE`, `MEM_ORDERED`, and `FWD_PROGRESS` affect queue ABI and kernel execution semantics. Incorrect values can cause hangs, bad dispatch dimensions, trap mishandling, or silent shader misexecution.
- CU enable/static-thread-management registers are per-shader-engine. Mask mistakes can disable work on valid CUs or target disabled/fused-off units, producing performance loss or dispatch failures.
- Address decode and GCEA arbitration fields can affect memory routing, quality of service, and fairness across clients. These are hardware-tuning registers rather than ordinary software policy knobs.
- Status, command, control, reserved, and readback fields are represented by identical `#define` syntax. Callers need hardware access metadata to avoid writing status or reserved bits incorrectly.
- Cache invalidation and busy/status fields can be sequencing-sensitive. Wrong bit definitions may result in incomplete invalidation, polling the wrong status bit, or over-flushing.

## Test Signals

Useful validation is mostly build-time, generator-level, and hardware-integration oriented:

- Compile or preprocess AMDGPU and AMDKFD GFX10/Navi paths that include `gc_10_1_0_offset.h` and `gc_10_1_0_sh_mask.h`.
- Mechanically verify that every complete field in this slice has one `__SHIFT` and one `_MASK` definition, with the explicit end-boundary exception for the `COMPUTE_USER_DATA_0` comment.
- Cross-check field names, shifts, and masks against AMD's authoritative GC 10.1.0 register database and the matching offset header.
- Diff repeated shader-stage families for intentional layout differences across PS, VS, GS, ES, HS, LS, ESGS, LSHS, and compute.
- Exercise KFD queue creation/destruction, MQD initialization, trap handling, scratch/temp-ring allocation, CU-mask programming, and compute dispatch on GC 10.1.0 hardware or emulation.
- Exercise graphics shader pipeline setup across pixel, vertex, geometry, tessellation/hull/local/export paths, including user-data programming and shader checksum/resource registers.
- Run reset, suspend/resume, SR-IOV, and GPU recovery flows while checking that shader, compute, cache, GCEA, and arbitration registers are restored or reinitialized correctly.
- Use register dumps around dispatch and graphics workloads to confirm decode of `COMPUTE_PGM_RSRC*`, `COMPUTE_RESOURCE_LIMITS`, `COMPUTE_STATIC_THREAD_MGMT_SE*`, `SPI_SHADER_PGM_RSRC*`, `TCP_STATUS`, and GCEA priority/arbitration fields.

## Chunk Notes For Merge

This document intentionally covers only lines 14881-17383 of `gc_10_1_0_sh_mask.h`. Adjacent chunks must provide earlier GCEA definitions and the `COMPUTE_USER_DATA_0` fields that follow this range. The final per-file research document should treat this source as generated AMD GC 10.1.0 register bitfield metadata used by AMDGPU/AMDKFD, not as handwritten runtime logic.

### subset-b-002456: lines 17384-19837

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 17384-19837

## Purpose

This chunk is a generated AMD GFX 10.1.0 shift/mask header slice. It contains C preprocessor constants that describe bit positions and masks for graphics/compute command processor and shader processor interface registers. It has no executable code, data structures, or runtime side effects by itself; its purpose is to let AMDGPU code compose, update, and decode hardware register values without open-coded bit numbers.

The requested range contains 2,163 `#define` statements across 289 generated register names: 1,083 `__SHIFT` macros and 1,080 `_MASK` macros. It starts inside the compute user-data register block at `COMPUTE_USER_DATA_0__DATA__SHIFT` and continues through compute dispatch sentinel registers, the `gc_cppdec` command-processor address block, and the beginning of the `gc_spipdec` shader-processor-interface block. It ends inside the `SPI_RESOURCE_RESERVE_CU_5` group, after the `SGPR` mask, with the remaining `LDS`, `WAVES`, and `BARRIERS` masks for that register in the next chunk.

Although the source tree path is under a local `ceph-client` mirror, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, locks, allocations, direct MMIO operations, or exported symbols in this range. The public interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field in the register value.
- `//<REGISTER>` comments: generated register boundaries.
- `// addressBlock: gc_cppdec` and `// addressBlock: gc_spipdec`: generated address-block boundaries that align these field macros with companion offset/default headers for the same GFX IP generation.

Major macro families in this chunk include:

- Compute dispatch/user payload registers: `COMPUTE_USER_DATA_0` through `COMPUTE_USER_DATA_15`, `COMPUTE_DISPATCH_TUNNEL`, `COMPUTE_DISPATCH_END`, and `COMPUTE_NOWHERE`. The user-data registers expose full 32-bit `DATA` fields; dispatch tunnel/end/nowhere fields support compute dispatch packet and sentinel behavior.
- Command processor core controls and telemetry: `CP_EOPQ_WAIT_TIME`, `CP_CPC_MGCG_SYNC_CNTL`, `CP_VIRT_STATUS`, `CP_DEVICE_ID`, `CP_PROCESS_QUANTUM`, `CP_CONTEXT_CNTL`, `CP_MAX_CONTEXT`, `CP_PWR_CNTL`, `CP_MEM_SLP_CNTL`, `CP_SD_CNTL`, `CP_SOFT_RESET_CNTL`, and `CP_CPC_GFX_CNTL`.
- CP/CPC interrupt and error surfaces: `CPC_INT_INFO`, `CPC_INT_ADDR`, `CPC_INT_PASID`, `CP_GFX_ERROR`, `CP_FATAL_ERROR`, `CP_INT_CNTL`, `CP_INT_STATUS`, `CP_INT_CNTL_RING0..2`, `CP_INT_STATUS_RING0..2`, `CPC_INT_CNTL`, `CPC_INT_STATUS`, `CPC_INT_CNTX_ID`, `CP_ME1_PIPE*_INT_CNTL`, `CP_ME1_PIPE*_INT_STATUS`, `CP_ME2_PIPE*_INT_CNTL`, `CP_ME2_PIPE*_INT_STATUS`, `CP_ME1_INT_STAT_DEBUG`, `CP_ME2_INT_STAT_DEBUG`, and `CP_MEC1/2_F32_INT_DIS`.
- UTCL1 translation/cache controls and error/status reporting: `CPG_UTCL1_CNTL`, `CPC_UTCL1_CNTL`, `CPF_UTCL1_CNTL`, `CPG_UTCL1_ERROR`, `CPC_UTCL1_ERROR`, `CPG_UTCL1_STATUS`, `CPC_UTCL1_STATUS`, and `CPF_UTCL1_STATUS`. These expose XNACK redo timers, invalidate/bypass/drop/force-snoop controls, VMID reset mode, no-PTE behavior, force-no-execute, request credits, permission-fault flags, miss-bypass counters, active flags, and TLB-miss status.
- Ring-buffer and queue plumbing: `CP_RB0_BASE`, `CP_RB_BASE`, `CP_RB1_BASE`, `CP_RB2_BASE`, corresponding high-address registers, `CP_RB0_CNTL`, `CP_RB_CNTL`, `CP_RB1_CNTL`, `CP_RB2_CNTL`, read/write pointers, read-pointer writeback addresses, buffer-size masks, `CP_RB_VMID`, `CP_RB_DOORBELL_RANGE_*`, `CP_MEC_DOORBELL_RANGE_*`, `CP_RB_DOORBELL_CONTROL`, `CP_RB_DOORBELL_CLEAR`, `CP_RB*_ACTIVE`, and `CP_RB_STATUS`.
- Pipe, ME, ring, and priority scheduling definitions: `CP_ME0/1/2_PIPE_PRIORITY_CNTS`, `CP_RING_PRIORITY_CNTS`, `CP_ME0_PIPE0..2_PRIORITY`, `CP_ME1_PIPE0..3_PRIORITY`, `CP_ME2_PIPE0..3_PRIORITY`, `CP_RING0..2_PRIORITY`, and `CP_GFX_QUEUE_INDEX`.
- Program counter and interrupt routine start registers: `CP_CE_PRGRM_CNTR_START`, `CP_PFP_PRGRM_CNTR_START`, `CP_ME_PRGRM_CNTR_START`, `CP_MEC1_PRGRM_CNTR_START`, `CP_MEC2_PRGRM_CNTR_START`, plus matching `*_INTR_ROUTINE_START` registers.
- Suspend/resume, preemption, context-save, and DDID plumbing: `CP_VMID_RESET`, `CP_VMID_PREEMPT`, `CP_VMID_STATUS`, `CPC_SUSPEND_CTX_SAVE_BASE_ADDR_*`, `CPC_SUSPEND_CTX_SAVE_CONTROL`, suspend stack/workgroup offsets and sizes, `CPC_OS_PIPES`, `CP_SUSPEND_RESUME_REQ`, `CP_SUSPEND_CNTL`, `CPC_DDID_BASE_ADDR_*`, `CP_DDID_BASE_ADDR_*`, `CPC_DDID_CNTL`, `CP_DDID_CNTL`, and `CP_GFX_DDID_*` counters/pointers.
- GFX HQD/MQD queue state: `CP_GFX_MQD_BASE_ADDR*`, `CP_GFX_HQD_ACTIVE`, `CP_GFX_HQD_VMID`, `CP_GFX_HQD_QUEUE_PRIORITY`, `CP_GFX_HQD_QUANTUM`, `CP_GFX_HQD_BASE*`, `CP_GFX_HQD_RPTR*`, `CP_GFX_HQD_WPTR*`, `CP_GFX_HQD_DEQUEUE_REQUEST`, `CP_GFX_HQD_MAPPED`, `CP_GFX_HQD_QUE_MGR_CONTROL`, `CP_GFX_HQD_HQ_STATUS0`, `CP_GFX_HQD_HQ_CONTROL0`, `CP_GFX_MQD_CONTROL`, `CP_HQD_GFX_CONTROL`, `CP_HQD_GFX_STATUS`, and the corresponding CE queue registers under `CP_GFX_HQD_CE_*`.
- Debug, watchpoint, and trace-style definitions: `CP_DMA_WATCH0..3_ADDR_*`, `CP_DMA_WATCH0..3_MASK`, `CP_DMA_WATCH0..3_CNTL`, `CP_DMA_WATCH_STAT*`, `CP_PFP_JT_STAT`, `CP_CE_JT_STAT`, `CP_MEC_JT_STAT`, `CPG_RCIU_CAM_*`, `CPF_GCR_CNTL`, `CP_GFX_INDEX_MUTEX`, and `CC_GC_EDC_CONFIG`.
- Shader processor interface controls: `SPI_ARB_PRIORITY`, `SPI_ARB_CYCLES_0/1`, `SPI_WCL_PIPE_PERCENT_GFX`, `SPI_WCL_PIPE_PERCENT_HP3D`, `SPI_WCL_PIPE_PERCENT_CS0..7`, `SPI_GDBG_WAVE_CNTL`, `SPI_GDBG_TRAP_CONFIG`, `SPI_GDBG_TRAP_MASK`, `SPI_GDBG_WAVE_CNTL2`, `SPI_GDBG_WAVE_CNTL3`, `SPI_GDBG_TRAP_DATA0/1`, `SPI_COMPUTE_QUEUE_RESET`, and `SPI_RESOURCE_RESERVE_CU_0..5`.

Common field names encode the intended hardware semantics: `RB_BASE`, `RB_RPTR`, `RB_WPTR`, `RB_BUFSZ`, `RB_BLKSZ`, `DOORBELL`, `VMID`, `PASID`, `QUEUE`, `PIPE`, `ME`, `MEC`, `HQD`, `MQD`, `ACTIVE`, `MAPPED`, `DEQUEUE`, `QUANTUM`, `PRIORITY`, `INTERRUPT`, `TIME_STAMP`, `PRIV_REG`, `BAD_OPCODE`, `ECC`, `EDC`, `UTCL1`, `XNACK`, `BYPASS`, `INVALIDATE`, `PERMISSION_FAULT`, `SUSPEND`, `RESUME`, `PREEMPT`, `DDID`, `HPD`, `OSPRE_FENCE`, `WATCH`, `SOFT_RESET`, `ARB`, `WCL`, `TRAP`, `STALL`, `VGPR`, `SGPR`, `LDS`, `WAVES`, and `BARRIERS`.

## Control Flow

This header has no direct control flow. It influences driver behavior only when included by AMDGPU source that expands these constants while building register values. Typical use is:

1. Consumer code selects a GFX 10.1.0 register offset from the matching generated offset header.
2. The consumer clears, inserts, tests, or extracts a bitfield using a `*_MASK` and `*__SHIFT` pair from this header.
3. AMDGPU register helpers perform the read/modify/write, direct write, polling loop, debug dump, or interrupt/status decode.
4. Hardware command-processor, queue, translation, interrupt, and shader-interface state machines perform the actual work.

The sequencing implied by the field names is outside this file. Examples include programming ring-buffer base/control/read-pointer writeback before enabling a queue; setting doorbell ranges and doorbell controls before user or kernel queues submit work; decoding CP/CPC interrupts after an interrupt handler reads status; clearing or masking interrupt sources in ring or pipe-specific registers; saving/restoring context state around suspend, preemption, or reset; and reserving SPI compute-unit resources before waves are admitted.

## State And Persistence Behavior

The macros are stateless compile-time constants. They describe hardware state but do not store it. Actual state lives in GFX command-processor and SPI registers, queue descriptors, memory-backed ring buffers, doorbell pages, writeback buffers, and hardware/firmware state machines.

Hardware-visible state described by this chunk includes:

- Compute user SGPR/user-data payload values and dispatch tunnel/end sentinel fields.
- CP ring-buffer bases, buffer/block sizes, read/write pointers, read-pointer writeback addresses, VMID association, buffer swap/cache/volatile/no-update controls, active/status bits, and queue execution bits.
- Doorbell aperture ranges, queue doorbell enable/source/offset bits, and doorbell clear controls.
- Interrupt masks, status bits, and error-reporting fields for CP, CPC, per-ring sources, ME1/ME2 pipe sources, bad opcodes, protected-mode faults, privilege faults, timestamp events, cache-flush events, VM faults, and ECC/EDC conditions.
- UTCL1 translation/cache controls, fault indicators, miss bypass counters, request credit state, TLB miss state, invalidation controls, and no-execute/no-PTE behavior.
- CP power, memory sleep, clock-gating/sleep-delay, soft-reset, and shader-dispatch control bits.
- Queue manager state for GFX HQDs and CE HQDs: MQD base, active/mapped state, VMID, priority, quantum, ring base and pointer fields, dequeue requests, queue manager controls, HQ status/control, and CE mirror queue state.
- Suspend/resume and preemption state, including VMID reset/preempt/status bits, suspend context-save addresses, stack/workgroup offsets and sizes, OS pipe selection, and resume request/control fields.
- DDID queue/counter state, high-priority dispatch status/control/fence fields, and OSPRE fence addresses/data.
- Debug/watch state for DMA watchpoints, watch status, jump table status, RCIU CAM access, GCR controls, and index mutex ownership.
- SPI arbitration, workload pipe-percent controls, graphics debug wave stall/trap controls, compute queue reset, and resource reservations per CU for VGPR, SGPR, LDS, waves, and barriers.

Persistence is determined by the hardware block, reset domain, power state, and firmware/driver ownership. Some registers are ordinary configuration state, some are read-only status, some are write-one-to-clear interrupt bits, some are self-clearing commands, some point to memory that persists across queues, and some are reset by GPU reset, command-processor reset, suspend/resume, power gating, or queue teardown. This header does not provide reset defaults, access permissions, legal enumerations, polling timeouts, or ordering rules; those come from hardware documentation, firmware contracts, and AMDGPU implementation code.

## Dependencies And Integration Points

This generated header must stay synchronized with the same GFX 10.1.0 register database as:

- `drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h`, which provides the register offsets that pair with these field definitions.
- `drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_default.h`, which provides reset/default values for many registers.
- Neighboring GC/GFX generation headers such as `gc_9_0_*`, `gc_10_3_0_*`, `gc_11_0_0_*`, and later `gc_12_*` headers. Their register families are similar but not layout-identical.
- AMDGPU GFX, KFD, queue, interrupt, reset, suspend/resume, VM fault, debug, and register-dump code that token-pastes or directly references register, field, shift, and mask names.
- CP firmware and microcode expectations for HQD/MQD layout, CP program counter and interrupt routine starts, suspend/context-save areas, doorbell behavior, and preemption/DDID paths.
- Hardware interrupt and fault plumbing that reports CP/CPC/UTCL1/ECC/EDC errors through DRM/KFD interrupt handlers and diagnostic paths.
- SPI scheduling/debug paths that control wave trapping/stalling, compute queue reset, arbitration, workload distribution, and per-CU resource reservation.

The range crosses two generated address blocks. The first part completes compute user-data and dispatch definitions from the previous address block; the middle and largest part is `gc_cppdec` for CP/CPC/CPG/CPF command-processor registers; the tail begins `gc_spipdec` for SPI arbitration, debug, queue reset, and CU resource reservation.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while silently programming or decoding the wrong hardware bit.
- The file is generated. Manual edits risk divergence from AMD's register source, companion offset/default headers, firmware assumptions, and existing GFX generation comparisons.
- The requested first line is inside the `COMPUTE_USER_DATA_0` group after its register comment. The previous chunk is needed for the complete start-of-register context.
- The requested last line is inside `SPI_RESOURCE_RESERVE_CU_5`; the `LDS`, `WAVES`, and `BARRIERS` masks for that register are outside this work item.
- Many register families are repeated with small differences: `CP_RB0_CNTL` versus `CP_RB_CNTL` versus `CP_RB1_CNTL`/`CP_RB2_CNTL`, global interrupt controls versus ring-specific controls, ME1 versus ME2 pipe interrupt definitions, HQD versus CE HQD fields, and `CPG`/`CPC`/`CPF` UTCL1 controls. Copying a field across a similar register can be wrong even when names look interchangeable.
- Ring-buffer and doorbell fields are sequencing-sensitive. Bad masks can cause lost submissions, write-pointer/read-pointer drift, writeback corruption, queues that never become active, or queues that cannot be unmapped.
- Interrupt/status/clear/mask fields can be edge-sensitive or write-one-to-clear in consumer code. Incorrect decoding can cause missed GPU faults, interrupt storms, stale status, false hang attribution, or failure to clear fatal error sources.
- VMID, PASID, bypass-PASID, app-VMID, permission-fault, no-execute, no-PTE, and UTCL1 fields are security and isolation sensitive. A bitfield mismatch can misattribute faults or break address-space isolation.
- Suspend/resume, preemption, context save, and DDID fields are stateful across queue lifecycle transitions. Misprogramming can leave queues suspended, lose context state, corrupt resumed queues, or wedge command processor firmware.
- Power, memory sleep, clock gating, soft reset, and shader-dispatch control fields may interact with in-flight queues. Consumers must preserve reserved bits and follow hardware sequencing.
- SPI debug and trap controls intentionally stall or redirect waves. Incorrect masks can hang graphics/compute work, trap the wrong VMID/queue, or make debug features affect normal workloads.
- SPI resource reservation fields influence occupancy. Wrong field widths can reserve too much or too little VGPR/SGPR/LDS/wave/barrier capacity and create performance loss or scheduling failures that only appear under specific shader mixes.

## Test Signals

Useful validation signals for this generated header and its consumers include:

- Build AMDGPU configurations that include GFX 10.1.0 support. Missing or renamed macros should surface as compile failures in register programming tables, GFX code, KFD queue code, interrupt paths, or debug code.
- Mechanically compare this range against the authoritative GFX 10.1.0 register database, checking that each field has the expected shift, mask, and register width.
- Cross-check register names against `gc_10_1_0_offset.h` and default values against `gc_10_1_0_default.h`, especially for CP ring, interrupt, UTCL1, HQD/MQD, doorbell, suspend/resume, and SPI resource registers.
- Diff repeated families against adjacent GFX generations to catch generator drift while allowing intentional layout changes, particularly in `CP_RB*_CNTL`, `CP_INT_*`, `CP_ME*_PIPE*_INT_*`, `CP_GFX_HQD_*`, `CP_GFX_HQD_CE_*`, `CPG/CPC/CPF_UTCL1_*`, and `SPI_GDBG_*`.
- Boot and run graphics/compute workloads on affected hardware with ring submission, doorbell writes, VM faults, queue creation/destruction, KFD workloads, and graphics queues enabled.
- Exercise suspend/resume, GPU reset, CP soft reset, queue preemption, queue eviction/restore, process teardown, VMID reset, and repeated workload start/stop cycles.
- Monitor DRM/KFD logs, interrupt counters, ring read/write pointers, fence progress, VM fault reporting, ECC/EDC reporting, CP fatal error status, and UTCL1 permission/miss status.
- Decode known-good register dumps using these masks and compare against reference tools or hardware documentation for CP ring state, interrupt masks/status, HQD/MQD state, doorbells, suspend/DDID state, debug watchpoints, and SPI trap/resource controls.
- Run shader-debug/trap and compute-queue-reset scenarios carefully, confirming that trap selection by ME/pipe/queue/VMID and wave-stall controls affect only the intended queues and recover cleanly.

## Cross-Chunk Notes

The previous chunk owns the register comment for `COMPUTE_USER_DATA_0` and likely earlier compute register definitions. This chunk starts at that register's `DATA` shift/mask pair, covers `COMPUTE_USER_DATA_1..15`, and then moves into the `gc_cppdec` command-processor address block.

This chunk stops partway through `SPI_RESOURCE_RESERVE_CU_5`. The next chunk should continue that CU resource-reservation group before covering later SPI resource or debug definitions.

### subset-b-002457: lines 19838-22333

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 19838-22333

## Purpose

This chunk is a generated AMD GC 10.1.0 shift/mask header slice. It contains C preprocessor constants for register-field bit positions and masks; it has no executable driver logic. AMDGPU and AMDKFD code combine these constants with `gc_10_1_0_offset.h` and helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, and `RREG32_SOC15` to program or decode GFX10 graphics, compute, queue, cache, debug, power-management, and render backend registers without open-coded bit numbers.

The requested range starts in the repeated `SPI_RESOURCE_RESERVE_CU_*` family, covers all of `SPI_RESOURCE_RESERVE_EN_CU_0..15`, moves through the `gc_cpphqddec` CP/MQD/HQD queue register block, then covers DIDT/CAC throttling, TCP watchpoint and TCP UTCL/performance-filter registers, GDS per-VMID/GWS/OA/context-switch state, and the beginning of `gc_gfxdec0` depth/color/scissor state. It ends inside `PA_SC_VPORT_SCISSOR_12_TL`, so the complete viewport scissor register family continues in the next chunk.

Although this path is under a local `ceph-client` source mirror, this file is AMD GPU driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, variables, locks, allocations, or exported symbols in this range. The interface is entirely the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the field.
- `// addressBlock: ...`: generated boundaries for hardware register decoder blocks.

Major macro families in this chunk are:

- `SPI_RESOURCE_RESERVE_CU_6..15` and `SPI_RESOURCE_RESERVE_EN_CU_0..15`: per-CU shader processor resource reservation fields for VGPR, SGPR, LDS, waves, barriers, enable, type mask, queue mask, and reserve-space-only behavior. These describe how SPI can reserve shader resources for selected compute queues or types.
- `SPI_COMPUTE_WF_CTX_SAVE`, `SPI_ARB_CNTL_0`, `SPI_FEATURE_CTRL`, and `SPI_SHADER_RSRC_LIMIT_CTRL`: shader/dispatch control fields for wave context-save activity, arbitration fairness/credits, feature bits, and shader resource limit behavior.
- `CP_HPD_*`, `CP_MQD_*`, and `CP_HQD_*`: command processor high-priority dispatch, MQD base/control, and hardware queue descriptor fields. These include queue active state, VMID, persistent/preload/QoS/context-switch state, pipe/queue priority, quantum, packet queue base/read/write pointers, doorbell control, packet queue control, IB/IQ control, dequeue requests, semaphore/message/atomic state, HQ scheduler/status/control, EOP base/control/pointers/events, CWSR context-save addresses/sizes/offsets, GDS resource state, error reporting, AQL control, suspend offsets, DDID counters, and dequeue status.
- `DIDT_*`, `GC_CAC_*`, `GC_DIDT_*`, `GC_THROTTLE_*`, `GC_EDC_*`, `EDC_PERF_COUNTER`, `PCC_PERF_COUNTER`, `PWRBRK_PERF_COUNTER`, `GC_CAC_IND_*`, and `SE_CAC_IND_*`: dynamic instruction-dependent throttling, current/activity control, electrical design current, power-brake/PCC throttling, threshold/status/overflow, and indirect CAC access fields.
- `TCP_WATCH0..3_*`, `TCP_CNTL2`, `TCP_UTCL0_CNTL1/2`, `TCP_UTCL0_STATUS`, and `TCP_PERFCOUNTER_FILTER*`: texture cache processor address watchpoints, cache/clock/return-order controls, UTCL0 translation/cache invalidation and fault status, and performance-counter filter selection/enables.
- `GDS_VMID0..15_BASE/SIZE`, `GDS_GWS_VMID0..15`, `GDS_OA_VMID0..15`, `GDS_GWS_RESET0/1`, `GDS_GWS_RESOURCE_RESET`, `GDS_OA_RESET_MASK`, `GDS_OA_RESET`, `GDS_ENHANCE2`, `GDS_OA_CGPG_RESTORE`, and `GDS_*_CTXSW_*`: global data share per-VMID allocation, global wave sync, ordered append, reset/resource reset, clock/power restore, and context-switch counter/status fields.
- `DB_RENDER_CONTROL`, `DB_COUNT_CONTROL`, `DB_DEPTH_VIEW`, `DB_RENDER_OVERRIDE`, `DB_RENDER_OVERRIDE2`, `DB_Z_INFO`, `DB_STENCIL_INFO`, depth/stencil read/write bases, HTILE base/size, bounds/clear values, RMI L2 cache controls, `TA_BC_BASE_ADDR*`, `COHER_DEST_BASE*`, and `PA_SC_*`/`CB_*` fields: early graphics render backend state for depth/stencil, HTILE, coherency destinations, window/clip/generic/viewport scissors, target masks, and shader output masks.

The most visible consumers in this tree are GFX10 KFD and AMDGPU paths. `kfd_mqd_manager_v10.c` initializes and updates `struct v10_compute_mqd` fields with `CP_HQD_*` and `CP_MQD_*` shifts/masks. `amdgpu_amdkfd_gfx_v10.c` writes CP HQD registers when loading/unloading queues and programs `TCP_WATCH0_CNTL` fields for debugger watchpoints. `gfx_v10_0.c` uses these fields for KIQ/compute MQD setup, GDS VMID initialization, and debug register dump lists.

## Control Flow

This header has no runtime control flow. Its influence appears after macro expansion in driver code:

1. A GFX10 consumer selects a register offset from the matching offset header.
2. The consumer uses shift/mask macros directly or via helper macros to construct, clear, extract, or test fields.
3. AMDGPU/AMDKFD register helpers write or read the selected MMIO register, often after selecting a GRBM/SRBM instance, VMID, MEC, pipe, or queue.
4. Hardware state machines, firmware, the command processor, shader processor, TCP, GDS, or graphics backend perform the actual work.

Queue setup is the clearest operational path. KFD allocates and fills a v10 MQD, encoding queue size, doorbell offset, base pointers, VMID, priority, AQL mode, EOP size, preload state, and CWSR context-save locations with these masks. `kgd_hqd_load` then selects the target MEC/pipe/queue, streams the MQD/HQD register window from `CP_MQD_BASE_ADDR` through `CP_HQD_PQ_WPTR_HI`, enables the doorbell, seeds write-pointer polling, initializes the EOP fetcher, and activates `CP_HQD_ACTIVE`.

Debugger watchpoints follow a smaller sequence: build TCP and SQ watch control words with VMID, mode, mask, and `VALID`; write the control register disabled; write high/low address registers; then set `VALID` so a partially programmed watchpoint is not exposed.

GDS initialization loops over VMIDs and clears `GDS_VMID*_BASE`, `GDS_VMID*_SIZE`, `GDS_GWS_VMID*`, and `GDS_OA_VMID*` so compute/user VMIDs start with no GDS/GWS/OA access until firmware or driver ownership grants it.

## State And Persistence Behavior

The macros are stateless compile-time constants. The state they describe lives in GPU registers, MQD memory, ring buffers, writeback memory, doorbell aperture state, firmware-owned scheduling structures, and render/queue hardware.

Persistent or semi-persistent state named in this chunk includes:

- MQD/HQD memory and register state for queue base addresses, read/write pointers, queue size, active state, VMID, priority, quantum, doorbells, AQL mode, IB/IQ/EOP rings, semaphore/message status, context-save addresses and stack offsets, suspend offsets, and dequeue status.
- User/debug state for TCP watchpoint address/mask/mode/VMID/valid registers and UTCL0 fault/retry/PRT status.
- Per-VMID GDS, GWS, and OA base/size/ownership state plus reset and context-switch counters.
- Power/throttle state for DIDT, CAC, EDC, PCC, and power-brake counters, thresholds, status, overrides, and indirect tables.
- Graphics pipeline state for depth/stencil buffers, HTILE, DB render overrides, coherency destinations, color target masks, shader output masks, and scissor rectangles.

Reset and persistence are hardware-defined. Some fields are volatile status bits, some are write-one-to-clear or self-clearing requests, some are saved in MQDs across queue eviction/preemption, and some are reset during GPU reset, mode reset, queue teardown, suspend/resume, or power/clock gating. This chunk does not define reset values, legal enum values, ordering constraints, access widths, or ownership rules.

## Dependencies And Integration Points

This generated header must stay synchronized with the GC 10.1.0 register database and the matching offset header. It also depends on shared AMDGPU register helper conventions that token-paste register and field names.

Key integration points include:

- `drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h`, which supplies register offsets matching these field names.
- `drivers/gpu/drm/amd/include/v10_structs.h`, whose `struct v10_compute_mqd` layout mirrors the CP MQD/HQD register window used by the `CP_*` macros in this chunk.
- AMDKFD queue management in `kfd_mqd_manager_v10.c`, `kfd_packet_manager_v9.c`, and `kfd_device_queue_manager_v10.c`, which uses the HQD/MQD/GDS masks to map processes, queues, GDS/GWS/OA resources, and debugger state.
- AMDGPU GFX10 code in `gfx_v10_0.c`, `amdgpu_amdkfd_gfx_v10.c`, `gfxhub_v2_0.c`, and `mxgpu_nv.c`, which programs queues, initializes GDS VMID state, decodes debug registers, handles SR-IOV paths, and exposes KFD callbacks.
- Graphics command streams and clear-state tables that rely on matching DB, CB, PA_SC, and coherency register layouts for render state.
- Hardware firmware/scheduler ownership for HWS/MES, CWSR, AQL queues, CP dequeue/offload paths, GDS save/restore, and power/throttle controls.

The chunk crosses several generated address blocks: the tail of shader/SPI resource definitions, `gc_cpphqddec`, `gc_didtdec`, `gc_gccacdec`, `gc_tcpdec`, `gc_gdspdec`, and the beginning of `gc_gfxdec0`. The merge lane should preserve those boundaries because each block has different owners and validation signals.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask compiles cleanly but can corrupt queue descriptors, route doorbells incorrectly, expose the wrong VMID, disable caches, or program render state incorrectly.
- The file is generated. Manual edits risk divergence from AMD's register database, firmware expectations, silicon documentation, and companion offset headers.
- The requested first line starts in the middle of `SPI_RESOURCE_RESERVE_CU_5`; the register comment and shift definitions are in the previous chunk. This chunk then covers complete `CU_6..15` and enable groups.
- The requested last line stops inside `PA_SC_VPORT_SCISSOR_12_TL`; the remaining `PA_SC_VPORT_SCISSOR_12_TL` masks and later viewport scissor registers are outside this work item.
- CP HQD/MQD fields are sequencing-sensitive. Queue load/unload, dequeue request, EOP fetcher initialization, doorbell enable, write-pointer polling, CWSR state, and active-bit transitions must be ordered correctly and under the right GRBM/SRBM selection.
- Address fields often encode shifted GPU addresses, such as 256-byte or dword alignment. Using raw byte addresses with these masks can silently point queues, EOP buffers, context save areas, depth/stencil buffers, or coherency destinations at the wrong memory.
- Queue size fields encode powers of two. Incorrect values can break write-pointer wrap logic, read-pointer reporting, EOP sizing, or the driver's queue overflow assumptions.
- Watchpoint masks use different address granularities across TCP and SQ. The GFX10 watchpoint code shifts TCP masks by 7 and SQ masks by 6; mixing the definitions can miss or over-trigger debugger traps.
- GDS/GWS/OA fields are per-VMID resources. Bad masks can leak access across processes or leave resources uncleared after process teardown, reset, or firmware scheduling changes.
- DIDT/CAC/EDC/throttle fields affect power, clocks, and stalls. Incorrect values may only show up as performance loss, thermal throttling, intermittent hangs, or board/ASIC-specific failures.
- DB/CB/PA_SC fields are graphics-pipeline state. Incorrect masks can cause depth/stencil corruption, broken clears/decompression, wrong scissor/clipping, missing color exports, or render-target coherency problems.

## Test Signals

Useful validation for this generated header and its consumers includes:

- Build GFX10 AMDGPU/AMDKFD configurations that include `gc_10_1_0_sh_mask.h`; missing or renamed field macros should break queue, KFD, and GFX compilation.
- Mechanically compare this range against the authoritative GC 10.1.0 register database and the matching offset header, especially around address-block boundaries.
- Boot GFX10 hardware with KFD enabled, create/destroy AQL and PM4 compute queues, use doorbells, exercise preemption/dequeue, and verify `CP_HQD_ACTIVE`, read/write pointers, EOP events, and queue priorities via debug dumps.
- Exercise CWSR/debug paths: context save/restore, debugger attach, address watchpoint set/clear, trap VMID selection, and wave state retrieval.
- Validate GDS/GWS/OA allocation and teardown with multiple processes/VMIDs, including reset and suspend/resume paths, checking that per-VMID base/size/resource registers are cleared or restored as expected.
- Run graphics render tests that cover depth/stencil clears, HTILE, decompression, scissor/window/clip rectangles, color target masks, and shader export masks.
- Monitor UTCL/TCP status, GDS protection faults, CP HQD error registers, EOP events, dequeue status, and GPU reset logs for faults that map back to fields in this chunk.
- Run power/performance stress tests across thermal and power limits to catch DIDT/CAC/EDC/throttle field regressions.

## Cross-Chunk Notes

The previous chunk owns the start of `SPI_RESOURCE_RESERVE_CU_5`; this chunk begins with its last mask lines, then covers complete SPI reservation enable groups, CP HQD/MQD queue state, TCP/GDS blocks, and the first part of `gc_gfxdec0`.

The next chunk should continue from `PA_SC_VPORT_SCISSOR_12_TL`, completing that register and the remaining viewport scissor/render backend definitions. A final per-file report should treat this document as one slice of a much larger generated GC 10.1.0 register map rather than as standalone driver logic.

### subset-b-002458: lines 22334-24790

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 22334-24790

## Scope And Purpose

This chunk is a generated AMD GC 10.1.0 register bitfield header segment. It contains C preprocessor constants for register field shifts and masks, not executable code. The constants describe how driver code should pack and unpack fields in GFX10 graphics-context registers for viewport/scissor state, rasterization, command-processor context IDs, color/depth/blend state, shader interpolation/export state, draw initiators, primitive assembly, clipping, setup, tessellation, and geometry-shader mode.

The chunk spans 2,457 lines and contains 294 register comment blocks, 1,085 `__SHIFT` macros, and 1,078 `_MASK` macros. It starts inside the `PA_SC_VPORT_SCISSOR_12_TL` block and ends inside `VGT_GS_MODE`; adjacent chunks are needed for the complete opening and closing register definitions.

## Register Areas Covered

The first section completes viewport scissor register definitions for viewports 12 through 15, then defines `PA_SC_VPORT_ZMIN_0..15` and `PA_SC_VPORT_ZMAX_0..15`. These are full-width 32-bit floating/depth payload fields used with viewport transform and depth range state. `PA_SC_RASTER_CONFIG`, `PA_SC_RASTER_CONFIG_1`, `PA_SC_SCREEN_EXTENT_CONTROL`, and `PA_SC_TILE_STEERING_OVERRIDE` describe shader-engine, shader-array, raster backend, packer, scan converter, tile-walk, and render-backend topology steering fields.

Command-processor and context identity registers include `CP_PERFMON_CNTX_CNTL`, `CP_PIPEID`, `CP_RINGID`, and `CP_VMID`. These expose small context fields and the high-bit `PERFMON_ENABLE` flag used when packet/ring/context code needs to stamp or filter GPU work.

Color-buffer and depth-buffer blocks include `CB_RMI_GL2_CACHE_CONTROL`, `CB_BLEND_RED/GREEN/BLUE/ALPHA`, `CB_DCC_CONTROL`, `CB_COVERAGE_OUT_CONTROL`, `DB_STENCIL_CONTROL`, `DB_STENCILREFMASK`, `DB_STENCILREFMASK_BF`, `DB_DEPTH_CONTROL`, `DB_EQAA`, `CB_COLOR_CONTROL`, and `DB_SHADER_CONTROL`. These macros cover cache policy, blend constants, DCC overwrite and key-clear behavior, coverage export, front/back stencil ops and masks, depth/stencil enable and compare controls, EQAA sample controls, ROP/color mode, and pixel-shader depth/coverage interactions.

Viewport, clipping, and user-clip-plane blocks include `PA_CL_VPORT_*` scale/offset registers for viewports 0 through 15, `PA_CL_UCP_0..5_{X,Y,Z,W}`, `PA_CL_PROG_NEAR_CLIP_Z`, `PA_CL_CLIP_CNTL`, `PA_CL_VTE_CNTL`, `PA_CL_VS_OUT_CNTL`, `PA_CL_NANINF_CNTL`, point radius/size/cull registers, and stereo registers. Most scale, offset, UCP, and point radius definitions are full-width data payloads; control registers expose individual enable and format bits for clip distances, cull distances, viewport transform, near/far clipping, DirectX clip-space behavior, NaN/Inf handling, and stereo render-target/viewport offsets.

Shader processor interface state is heavily represented. `SPI_PS_INPUT_CNTL_0..31` define repeated pixel-shader input mapping fields such as parameter offset, default values, flat shading, cylindrical wrapping, point-sprite texture selection, FP16 interpolation mode, duplicate/valid bits, and secondary-attribute selection. `SPI_PS_INPUT_ENA`, `SPI_PS_INPUT_ADDR`, `SPI_INTERP_CONTROL_0`, `SPI_PS_IN_CONTROL`, and `SPI_BARYC_CNTL` define interpolation modes and barycentric input selection. `SPI_TMPRING_SIZE`, `SPI_SHADER_IDX_FORMAT`, `SPI_SHADER_POS_FORMAT`, `SPI_SHADER_Z_FORMAT`, and `SPI_SHADER_COL_FORMAT` define temporary ring sizing and shader export formats for index, position, depth, and color outputs.

Blend and render-target optimization blocks include `SX_PS_DOWNCONVERT`, `SX_BLEND_OPT_EPSILON`, `SX_BLEND_OPT_CONTROL`, `SX_MRT0_BLEND_OPT..SX_MRT7_BLEND_OPT`, and `CB_BLEND0_CONTROL..CB_BLEND7_CONTROL`. These specify per-MRT downconversion formats, blend epsilon thresholds, independent MRT blend enable state, commutativity/discard optimization, color source/destination factors, color/alpha combine functions, and separate-alpha behavior.

Vertex-grouper/tessellation/geometry blocks include `VGT_DMA_BASE_HI`, `VGT_DMA_BASE`, `VGT_DRAW_INITIATOR`, `VGT_IMMED_DATA`, `VGT_EVENT_ADDRESS_REG`, `GE_MAX_OUTPUT_PER_SUBGROUP`, `VGT_OUTPUT_PATH_CNTL`, `VGT_HOS_CNTL`, `VGT_HOS_MAX_TESS_LEVEL`, `VGT_HOS_MIN_TESS_LEVEL`, `VGT_HOS_REUSE_DEPTH`, `VGT_GROUP_PRIM_TYPE`, `VGT_GROUP_FIRST_DECR`, `VGT_GROUP_DECR`, `VGT_GROUP_VECT_0/1_CNTL`, `VGT_GROUP_VECT_0/1_FMT_CNTL`, and the beginning of `VGT_GS_MODE`. These fields control draw initiation, DMA base addressing, event address writes, tessellation mode and levels, grouped primitive ordering, vector component packing, and GS execution mode flags.

## APIs, Types, And Macro Contract

There are no functions, structs, enums, or runtime control paths in this chunk. Its API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask at its final register position.
- Comment lines of the form `//REGISTER_NAME` group related field constants and serve as the only local structure.

Driver code combines these constants with register address macros from companion GC headers and with register access helpers such as SOC15/MMIO read-modify-write paths. The normal use pattern is to clear a field with the mask and insert a value shifted by the corresponding shift, or to extract a value by masking and shifting down. The constants are part of the kernel C preprocessor contract and must remain stable for code compiled against GC 10.1.0 register layouts.

## Control Flow

This file has no branches or function calls. Runtime control flow appears in consumers: AMDGPU and AMDKFD code include `gc/gc_10_1_0_sh_mask.h`, choose register values based on ASIC configuration, queue setup, graphics state, or golden-register programming, then write packed values to hardware registers. Clear-state tables such as `clearstate_gfx10.h` carry default values for many registers covered here, including viewport Z ranges, raster config, and CP context control, while this header provides the bit positions needed when code builds non-default values.

The ordering in the header follows hardware register ordering rather than software dependency order. Repeated register families, especially viewport and `SPI_PS_INPUT_CNTL_N`, are mechanically expanded. That repetition is important because packet-building or context-state code can address each numbered register independently while using identical field semantics.

## State And Persistence Behavior

The header itself has no mutable state and persists no data. The state it describes is GPU hardware context state. Values assembled with these masks may be stored in command buffers, context images, clear-state tables, queue descriptors, or written directly through MMIO/register programming paths. Once submitted, the fields affect persistent GPU context until overwritten by later context state, reset by clear-state initialization, or invalidated by GPU reset and power-management transitions.

Several blocks influence long-lived rendering behavior. Viewport and clip registers determine coordinate transforms and clipping across draws. DB/CB registers determine depth, stencil, color, coverage, blending, DCC, and compression behavior. SPI registers determine how shader inputs and exports are interpreted. VGT registers affect draw setup, tessellation, primitive grouping, and geometry-shader execution. Incorrect bit packing can therefore survive across many draws within a context and present as rendering corruption, hangs, memory faults, or invalid performance-counter behavior.

## Dependencies And Integration Points

This generated header depends on the GC 10.1.0 hardware register specification. It is paired with offset/address headers in `drivers/gpu/drm/amd/include/asic_reg/gc/`, default-value headers, and AMDGPU/KFD source files that include `gc/gc_10_1_0_sh_mask.h`.

Primary integration points include:

- AMDGPU GFX10 initialization and register programming, including golden settings, context state, clear-state initialization, graphics pipeline setup, and render/depth/blend programming.
- AMDKFD GFX10 queue and packet-management code that shares the GC register masks for compute/graphics queue configuration and context fields.
- Clear-state arrays such as `clearstate_gfx10.h`, where register defaults align with many names in this chunk.
- Mesa/userspace command streams indirectly, because userspace graphics APIs submit state that the kernel validates, schedules, resets, or restores using these hardware definitions.
- Hardware-generation compatibility code, where the same logical register names may differ between GC versions and must use the correct versioned mask header.

## Risks And Edge Cases

- This chunk starts and ends mid-register-block. `PA_SC_VPORT_SCISSOR_12_TL` is partially defined before line 22334, and `VGT_GS_MODE` has additional masks after line 24790. Any reconciliation or regeneration check must include neighboring chunks before judging completeness.
- Manual edits to generated masks are high risk. A single wrong shift or mask silently writes the wrong bitfield and can corrupt rendering, disable depth/stencil/blend behavior, select the wrong shader interpolation, or program invalid primitive/GS state.
- Many fields are full-width `0xFFFFFFFFL` payload masks. Callers must avoid shifting these values unnecessarily and must preserve intended IEEE float or raw register encoding semantics.
- Repeated families can hide copy/paste or generator errors. `SPI_PS_INPUT_CNTL_0..31`, viewport 0..15, MRT 0..7, and blend 0..7 should remain structurally consistent except where the hardware specification intentionally differs.
- Reserved fields appear in `VGT_GS_MODE` and similar registers. Consumers should not infer that reserved bits are safe to set just because masks are present; hardware programming sequences should follow the ASIC specification and golden settings.
- Register state crosses subsystem boundaries. A field used by graphics context restore, KFD queues, or power/reset paths can break only on specific ASICs, queue types, shader stages, or multi-engine configurations.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware-conformance oriented:

- Kernel build coverage for AMDGPU and AMDKFD configurations that include `gc/gc_10_1_0_sh_mask.h`.
- Static checks that every `__SHIFT`/`_MASK` pair is internally consistent, masks do not overlap unintentionally within a register, and repeated register families keep identical layouts where expected.
- Generated-header comparison against the authoritative GC 10.1.0 register database or upstream AMDGPU header.
- Smoke tests on GFX10 hardware for boot, suspend/resume, GPU reset, queue creation, graphics context restore, and clear-state programming.
- Rendering tests that exercise viewport/scissor/depth range, clipping, stencil, depth bounds, EQAA/MSAA, color blending, MRT formats, point/line/stipple state, tessellation, geometry shaders, and pixel-shader interpolation.
- GPU hang and fault monitoring during shader/export/blend/depth stress tests, because incorrect bitfield definitions often surface as command processor faults, VM faults, or ring timeouts rather than direct software errors.

### subset-b-002459: lines 24791-27308

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 24791-27308

## Scope

This chunk is a generated AMD GC 10.1.0 shift/mask header slice. The requested range spans lines 24791-27308 of `gc_10_1_0_sh_mask.h`, containing 2,143 `#define` entries and 373 visible register/comment groups. Each register field is represented as one or both of:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for the field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the field inside a 32-bit register.

The range starts in the middle of `VGT_GS_MODE`: the comment and early shift/mask fields are in the previous chunk, while this chunk starts at `VGT_GS_MODE__PARTIAL_THD_AT_EOI_MASK` and finishes that register's masks. It ends on the comment for `CP_WAIT_SEM_ADDR_LO`; that register's actual field definitions begin in the next chunk.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU graphics hardware metadata, not Ceph or distributed filesystem logic. It is declarative C preprocessor data used by the Linux AMDGPU and AMDKFD driver code for GC 10.1/Navi-era register programming.

## Purpose

`gc_10_1_0_sh_mask.h` gives driver code symbolic names for bit placement in GC 10.1.0 hardware registers. This chunk covers a large graphics pipeline and command-processor area:

- Vertex grouper/tessellator/input assembler setup: `VGT_*`, `IA_*`, and `WD_*` registers for GS/ES/VS/HS/DS topology, primitive grouping, DMA index handling, primitive IDs, streamout, shader-stage enables, NGG, and tessellation factors.
- Scan converter, setup, clipping, rasterization, antialiasing, and depth-buffer helpers: `PA_SC_*`, `PA_SU_*`, `PA_CL_*`, `DB_*`, and `GE_*` registers.
- Color buffer render-target state for slots 0-7: `CB_COLORn_*` base, pitch, slice, view, format/info, attributes, DCC, CMASK, FMASK, clear colors, extended base-address registers, and `ATTRIB2/ATTRIB3`.
- The start of the `gc_gfxudec` address block: command processor end-of-pipe, streamout, pipeline statistics, performance counter, scratch, append, atomic preoperation, memory-controller read/write, and semaphore address/timer registers.

The practical purpose is to keep register programming readable and ASIC-specific. Consumers can construct values such as `FIELD_VALUE << FIELD__SHIFT` and mask updates with `FIELD_MASK` without hard-coding numeric bit positions.

## Important APIs, Types, And Macros

There are no callable functions, structs, enums, global variables, locks, allocation paths, or runtime MMIO operations in this range. The exported interface is only C preprocessor constants.

Important macro families in this chunk include:

- `VGT_GS_MODE` tail and `VGT_GS_ONCHIP_CNTL`: geometry shader mode/on-chip sizing fields such as partial thread behavior, cut suppression, ES/GS write optimization, on-chip mode, ES vertices per subgroup, GS primitives per subgroup, and GS instance primitives per subgroup.
- `PA_SC_MODE_CNTL_0` and `PA_SC_MODE_CNTL_1`: scan-converter mode bits for MSAA, viewport scissor, line stipple, tile-walk/supertile-walk controls, ZMM extents, post-HiZ kill behavior, multi-shader-engine/multi-GPU primitive discard, GPU ID override, forced EOV behavior, and out-of-order primitive watermarks.
- `VGT_DMA_SIZE`, `VGT_DMA_MAX_SIZE`, and `VGT_DMA_INDEX_TYPE`: index-buffer DMA count, maximum count, index type, byte swap, buffer type, request policy, ATC, EOP, request path, and memory type fields.
- `VGT_PRIMITIVEID_EN`, `VGT_PRIMITIVEID_RESET`, `VGT_MULTI_PRIM_IB_RESET_EN`, `VGT_DRAW_PAYLOAD_CNTL`, `VGT_EVENT_INITIATOR`, and `VGT_DMA_EVENT_INITIATOR`: primitive ID generation/reset, multi-primitive index-buffer reset, draw payload enables, and event-initiation fields.
- `IA_MULTI_VGT_PARAM`, `VGT_ESGS_RING_ITEMSIZE`, `VGT_GSVS_RING_ITEMSIZE`, `VGT_GS_VERT_ITEMSIZE[_1..3]`, `VGT_GS_PER_ES`, `VGT_ES_PER_GS`, `VGT_GS_PER_VS`, and `VGT_GSVS_RING_OFFSET_[1..3]`: graphics pipeline sizing and ring layout values.
- `VGT_SHADER_STAGES_EN`, `VGT_LS_HS_CONFIG`, `VGT_TF_PARAM`, `VGT_TESS_DISTRIBUTION`, and `GE_NGG_SUBGRP_CNTL`: shader-stage enable fields, NGG/primitive-generation controls, tessellation partitioning/topology/distribution, DS wave count, memory type, and LS/HS patch control.
- `VGT_STRMOUT_*`: streamout buffer size, stride, offset, opaque draw offset/filled-size/stride, streamout enable/configuration, buffer enables, and primitive-needed count control.
- `DB_HTILE_SURFACE`, `DB_SRESULTS_COMPARE_STATE0/1`, `DB_PRELOAD_CONTROL`, and `DB_ALPHA_TO_MASK`: depth/HTILE surface fields, stencil result comparison state, DB preload windows, and alpha-to-mask offsets.
- `PA_SU_POLY_OFFSET_*`, `PA_SU_VTX_CNTL`, `PA_CL_GB_*`, `PA_SC_CENTROID_PRIORITY_*`, `PA_SC_LINE_CNTL`, `PA_SC_AA_CONFIG`, `PA_SC_AA_SAMPLE_LOCS_*`, `PA_SC_AA_MASK_*`, `PA_SC_SHADER_CONTROL`, `PA_SC_BINNER_CNTL_0/1`, `PA_SC_CONSERVATIVE_RASTERIZATION_CNTL`, and `PA_SC_NGG_MODE_CNTL`: viewport/depth bias, clip/discard guard bands, centroid priority, lines, AA sample locations/masks, shader control, binning, conservative rasterization, and NGG scan-converter mode.
- `CB_COLOR0_*` through `CB_COLOR7_*`: repeated render-target slot metadata. Each slot has base, pitch, slice, view, `INFO`, `ATTRIB`, `DCC_CONTROL`, CMASK/FMASK addresses and slices, clear words, DCC base, extended base fields, `ATTRIB2`, and `ATTRIB3`.
- `CP_EOP_*`, `CP_STREAM_OUT_*`, `CP_NUM_PRIM_*`, `CP_PIPE_STATS_*`, `CP_VGT_*COUNT*`, `CP_PA_*COUNT*`, `CP_SC_*COUNT*`, and `CP_VGT_CSINVOC_COUNT*`: command processor addresses/data/fences and 64-bit low/high counter registers for graphics pipeline statistics.
- `SCRATCH_REG0` through `SCRATCH_REG7`, `SCRATCH_UMSK`, and `SCRATCH_ADDR`: scratch register fields, including obsolete mask/swap/address aliases retained in the register description.
- `CP_APPEND_*`: append addresses, data, last CS/PS fence fields, DDID count, cache policy, command selection, and CS/PS selector.
- `CP_PFP_ATOMIC_*`, `CP_ME_ATOMIC_*`, `CP_GDS_ATOMIC*`, and `CP_ME_GDS_ATOMIC*`: preoperation low/high values for CP/PFP/ME atomics and GDS atomics.
- `CP_ME_MC_WADDR_*`, `CP_ME_MC_WDATA_*`, `CP_ME_MC_RADDR_*`: command-processor micro-engine memory-controller write/read address and data fields, including address alignment and cache policy.
- `CP_SEM_WAIT_TIMER`, `CP_SIG_SEM_ADDR_LO/HI`, and `CP_WAIT_REG_MEM_TIMEOUT`: semaphore wait timer, signal semaphore address/swap/use-mailbox/signal-type/client/select fields, and wait-register-memory timeout. The next chunk owns the fields for `CP_WAIT_SEM_ADDR_LO`.

## Control Flow

This header has no local control flow. It does not branch, loop, validate inputs, read registers, or write registers. Runtime behavior is supplied by driver code that includes this header and uses the macros when composing register writes or decoding register reads.

Typical usage is:

1. A GC 10.x AMDGPU or AMDKFD source file includes `gc/gc_10_1_0_offset.h` for register offsets and `gc/gc_10_1_0_sh_mask.h` for fields.
2. The driver computes a register address through SOC15 helpers or PM4 packet encoding.
3. The driver builds the field value with the matching `__SHIFT` and `_MASK` constants.
4. MMIO helpers, ring packets, queue descriptors, or command packets carry the final 32-bit register value to the GPU.

Direct include sites found in this tree include:

- `drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c`, the main GFX10 AMDGPU implementation.
- `drivers/gpu/drm/amd/amdgpu/nv.c`, `gfxhub_v2_0.c`, `mxgpu_nv.c`, `sdma_v5_0.c`, `mmhub_v2_0.c`, `amdgpu_sdma.c`, and `amdgpu_amdkfd_gfx_v10.c`.
- `drivers/gpu/drm/amd/amdkfd/kfd_packet_manager_v9.c`, `kfd_mqd_manager_v10.c`, and `kfd_device_queue_manager_v10.c`.

Many registers in this particular chunk are also represented by clear-state tables such as `amdgpu/clearstate_gfx10.h`, where the register names appear as comments with reset/clear values. The macros here provide the field-level view, while those tables provide prebuilt state packets.

## State And Persistence Behavior

This chunk stores no software state. Its constants describe hardware-visible state that persists according to GPU register, context, reset, power, VM, queue, and command-processor rules.

State represented by the VGT/IA/GE/WD portion includes:

- Primitive grouping, index-buffer interpretation, primitive ID behavior, event initiation, draw payload fields, instance step rates, shader-stage enables, tessellation parameters, GS/ES/VS ring item sizes, streamout configuration, and NGG/primitive-generation settings.
- Values written here can be per-draw, per-context, or part of graphics clear state depending on how the command stream programs them.

State represented by the PA/DB/CB portion includes:

- Rasterizer/scissor/tile-walk behavior, AA sample positions and masks, centroid priority, line rules, conservative rasterization mode, binning behavior, depth/HTILE state, alpha-to-mask behavior, and render-target slot configuration.
- Color target state is repeated for eight slots. The base, pitch, slice, view, format, DCC, CMASK, FMASK, clear color, and extended base registers together define where render output lands in memory and how compression/metadata is interpreted.

State represented by the CP/gfxudec portion includes:

- EOP and streamout memory addresses/data/fences, primitive and shader invocation counters, pipe-statistics destination/control/doorbell registers, scratch registers, append/fence state, atomic preoperation values, micro-engine memory-controller read/write state, and semaphore wait/signal address fields.
- Low/high counter pairs are effectively 64-bit values split across two 32-bit registers by hardware convention. Software must read or write paired registers consistently if it needs a coherent value.
- Doorbell offset fields are aligned from bit 2 (`0x0FFFFFFC` masks), so callers must preserve hardware-required low-bit alignment.

Fields with names such as `COUNT`, `STATUS`, `DONE`, `OBSOLETE`, `LAST_FENCE`, or `SCRATCH` can have special read/write semantics in the hardware, but this header does not encode those semantics. It only exposes bit placement.

## Dependencies And Integration Points

The syntactic dependency is the C preprocessor. Semantically, this generated header must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h`, which supplies the corresponding register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_default.h`, which supplies default values for many GC 10.1.0 registers.
- SOC15 access helpers and register-table macros in the AMDGPU driver, which combine HWIP instance, register offset, base index, shift, and mask data.
- AMDKFD packet and MQD code, which includes this header when constructing process, queue, and dispatch metadata for GFX9/GFX10-family hardware.
- User-mode graphics and compute stacks indirectly, because command streams and queue descriptors depend on these fields matching the ASIC register database.

The range is centered on the programmable graphics pipeline state used by draw and compute submission paths:

- Graphics command streams rely on VGT/PA/DB/CB fields to interpret topology, tessellation, shader stages, render-target layout, antialiasing, streamout, depth/stencil, and rasterization.
- Kernel queue management and KFD paths rely on adjacent GC 10.1 definitions for queue descriptors, process state, and trap/debug-related packet fields.
- Reset, suspend/resume, GPU recovery, virtualization, and clear-state initialization depend on these register definitions matching the firmware and hardware expectations for the selected ASIC family.

## Risks And Edge Cases

- The chunk starts in the middle of `VGT_GS_MODE`, so final per-file analysis must merge this with the previous chunk before treating `VGT_GS_MODE` as complete.
- The chunk ends on `CP_WAIT_SEM_ADDR_LO` with no fields for that register. The next chunk owns the actual wait semaphore address low definitions.
- Generated-header drift is the core risk. A wrong shift or mask compiles cleanly but can place a field into an adjacent bit, causing rendering corruption, hangs, bad counters, wrong memory addresses, or missed synchronization.
- Repeated `CB_COLOR0` through `CB_COLOR7` layouts are easy to validate mechanically but easy to misread manually. A slot-specific typo could affect only particular MRT configurations.
- Address fields split into low/high or base/ext registers require coordinated programming. Mixing old and new halves can direct CP, streamout, append, CMASK, FMASK, DCC, or color output to the wrong memory location.
- Several fields control compression metadata (`DCC`, `CMASK`, `FMASK`, HTILE). Incorrect masks can create silent corruption rather than immediate faults because metadata and surface payload no longer agree.
- Counter registers are split into low/high pairs. Reading them without rollover handling can produce inconsistent values even when bit definitions are correct.
- `OBSOLETE` fields are still defined. Their presence should not be interpreted as safe or useful for new code without checking the hardware database and driver access layer.
- Doorbell and semaphore address fields encode alignment and selection bits. Incorrect masks or shifts can break queue signaling, EOP completion, streamout completion, pipe statistics, or semaphore waits.
- Reserved, status, test, and control fields all use the same macro style. This header alone does not tell callers which fields are writable, read-only, sticky, write-one-to-clear, privileged, or context-saved.
- The file is broad GC metadata, not Ceph logic. Distributed filesystem tests will not exercise these definitions unless they build or load the mirrored AMDGPU tree.

## Test Signals

Useful validation is mostly build-time, generator-level, and hardware-integration oriented:

- Build AMDGPU and AMDKFD code paths that include `gc_10_1_0_offset.h` and `gc_10_1_0_sh_mask.h`, especially `gfx_v10_0.c`, KFD MQD management, KFD packet management, SDMA, GFXHUB, MMHUB, and NV initialization.
- Mechanically verify that each complete register field in this range has a matching `__SHIFT` and `_MASK`, with documented exceptions for the partial `VGT_GS_MODE` start and `CP_WAIT_SEM_ADDR_LO` boundary.
- Cross-check the range against the authoritative GC 10.1.0 register database and `gc_10_1_0_offset.h`, especially around address-block transition `gc_gfxudec`.
- Compare repeated render-target groups (`CB_COLOR0_*` through `CB_COLOR7_*`) for intentional symmetry and slot-number-only differences.
- Run graphics tests that exercise tessellation, geometry shaders, NGG/primitive generation, streamout, indexed draws, primitive IDs, multisampling, conservative rasterization, scissor/viewport behavior, depth/stencil/HTILE, alpha-to-mask, and multiple render targets.
- Run workloads using DCC/CMASK/FMASK and clear/decompress paths, then validate output and metadata behavior across suspend/resume and GPU reset.
- Exercise CP event, EOP, streamout, pipe-statistics, primitive-count, shader-invocation-count, append/fence, scratch, atomic-preop, memory-controller read/write, and semaphore paths with register dumps or tracepoints.
- Validate doorbell and semaphore signaling under normal queue submission, queue teardown, GPU reset, and virtualization/SR-IOV flows.
- Use register dumps before and after clear-state programming to confirm `PA_SC_MODE_CNTL_*`, `VGT_SHADER_STAGES_EN`, `VGT_TF_PARAM`, `CB_COLORn_*`, and `CP_*` fields decode as expected.

## Chunk Notes For Merge

This document intentionally covers only lines 24791-27308 of `gc_10_1_0_sh_mask.h`. Adjacent chunks must provide the earlier `VGT_GS_MODE` comment and initial fields, plus the `CP_WAIT_SEM_ADDR_LO` definitions after this chunk boundary. The final per-file document should treat this source as generated AMD GC 10.1.0 register metadata used by AMDGPU/AMDKFD, not as handwritten runtime logic.

### subset-b-002460: lines 27309-29911

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 27309-29911

## Purpose

This chunk is generated AMD GC 10.1.0 register bitfield metadata. It contains no executable C logic; it exports preprocessor constants for bit shifts and masks used when programming or decoding Graphics Core command processor, geometry, shader, GDS, MES, GUS, GL1/CH, and GL2 cache/control registers. The companion register-address definitions live in `gc_10_1_0_offset.h`, and consumers combine offset, shift, and mask macros through AMDGPU/KFD register helpers or packet-building code.

The selected range contains 2,135 `#define` lines: 1,069 `__SHIFT` definitions and 1,066 `_MASK` definitions. It starts cleanly at `CP_WAIT_SEM_ADDR_LO` and ends inside `GL2C_CTRL3`; the final three `GL2C_CTRL3` masks (`COMP_TO_CONST_CAM_CHECK_ENABLE`, `FGCG_OVERRIDE`, and `SCRATCH`) are just outside this chunk. Although the source tree is under a local `ceph-client` mirror, this file is AMDGPU hardware metadata, not distributed filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, memory allocations, callbacks, or runtime APIs in this slice. The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a field.
- `<REGISTER>__<FIELD>_MASK`: 32-bit field mask used for read-modify-write, packet construction, or status decoding.

Major register families in this range are:

- Command processor and DMA registers: `CP_WAIT_SEM_ADDR_*`, `CP_DMA_PFP_*`, `CP_DMA_ME_*`, `CP_DMA_CNTL`, `CP_DMA_READ_TAGS`, and command-address registers define semaphore wait addresses, CP DMA source/destination addresses, cache policy, volatility, byte counts, raw-wait/write-combine behavior, command-buffer pointers, and DMA status.
- CP coherency and indirect-buffer state: `CP_COHER_*`, `CP_ME_COHER_*`, `CP_PFP_IB_CONTROL`, `CP_PFP_LOAD_CONTROL`, `CP_SCRATCH_*`, `CP_RB_OFFSET`, `CP_IB*_OFFSET`, `CP_*_BASE_*`, `CP_*_BUFSZ`, `CP_*_CMD_BUFSZ`, `CP_EOP_DONE_*`, `CP_DB_*`, `CP_CE_DB_*`, completion status, metadata base addresses, indirect draw/dispatch addresses, index base/type fields, and GDS backup address fields.
- Graphics front-end state: `RLC_GPM_PERF_COUNT_*`, `GRBM_GFX_INDEX`, `VGT_*`, `GE_*`, `WD_*`, and `IA_MULTI_VGT_PARAM_PIPED` fields cover GRBM shader-engine/instance targeting, primitive and index setup, transform-feedback and streamout sizes, vertex/index bounds, draw/instance counts, geometry-engine controls, user VGPR enables, stereo control, and work-distributor buffer bases.
- Rasterization, shader, texture, and depth counters: `PA_SU_LINE_STIPPLE_VALUE`, `PA_SC_*` screen extent/trap/stipple fields, `SQ_THREAD_TRACE_USERDATA_*`, `SQC_CACHES`, `SQC_WRITEBACK`, `TA_CS_BC_BASE_ADDR*`, `DB_OCCLUSION_COUNT*`, and `DB_ZPASS_COUNT*`.
- GDS atomics and synchronization: `GDS_RD_*`, `GDS_WR_*`, `GDS_WRITE_COMPLETE`, `GDS_ATOM_*`, `GDS_GWS_RESOURCE*`, and `GDS_OA_*` fields describe direct GDS read/write windows, burst access, atomic operation inputs/results, global wave sync resource bookkeeping, ordered-append counters, and associated ring/address controls.
- SPI remap and MES registers: `SPI_CONFIG_CNTL*_REMAP`, `SPI_WAVE_LIMIT_CNTL_REMAP`, then the `gc_cprs64dec` block with `CP_MES_*` program counter, trap vector, interrupt, scratch, machine CSR, timer/cycle, process-quantum, doorbell, general-purpose, debug-module, trigger, and perfcount control fields.
- GUS arbitration/QoS/diagnostics: the `gc_gusdec` block has `GUS_IO_*`, `GUS_DRAM_*`, `GUS_SDP_*`, `GUS_MISC*`, latency sampling, perf counters, error status, backdoor credits, L1 channel counters, and write-response FIFO control fields. These tune or report IO/DRAM priority aging, fixed priority, urgency, quantum, group burst, credits, latency, and errors.
- GL1/CH/GL2 cache and channel blocks: `gc_gl1dec`, `gc_chdec`, and `gc_gl2dec` define GL1 and channel arbitration, burst masks, pipe steering, status, GL1 cache status, CH/CHC/CHCG status, GL2 cache control, address match, writeback/invalidate done, soft reset, compression metadata controls, MDC prefetch, coherency behavior, and the first part of `GL2C_CTRL3`.

## Control Flow

This header has no runtime control flow. Runtime behavior comes from driver code that includes the generated metadata and applies the fields to MMIO or packet words:

1. `amdgpu/gfx_v10_0.c`, `gfxhub_v2_0.c`, `mxgpu_nv.c`, `sdma_v5_0.c`, `nv.c`, `amdgpu_amdkfd_gfx_v10.c`, and KFD files such as `kfd_packet_manager_v9.c`, `kfd_mqd_manager_v10.c`, and `kfd_device_queue_manager_v10.c` include `gc_10_1_0_sh_mask.h`, usually with `gc_10_1_0_offset.h`.
2. Register helper macros and golden-register tables token-paste or directly reference register, field, shift, and mask constants.
3. GFX/KFD runtime paths program queue descriptors, doorbells, command rings, cache controls, DMA engines, GDS resources, MES scheduling registers, and cache arbitration registers.
4. Hardware executes the resulting command processor, shader, cache, GDS, and MES behavior; the macros only describe where fields sit inside 32-bit registers.

The chunk does not define ordering, locking, reset sequencing, timeout policy, packet format validity, read/write access type, or whether a status bit is sticky, self-clearing, read-only, or write-one-to-clear. Those rules live in AMDGPU/KFD code and the hardware programming guide.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed register state:

- CP state includes semaphore wait addresses, DMA source/destination/control values, indirect-buffer offsets and preamble ranges, scratch data, command-buffer base/size state, EOP completion controls, doorbell buffers, metadata bases, indirect draw/dispatch pointers, index state, and coherency request ranges.
- Graphics front-end state includes GRBM broadcast selection, primitive/index/instance counts, ring sizes, work-distributor base pointers, geometry engine control, line/screen trap/stipple state, and shader thread-trace userdata.
- GDS/GWS/OA state includes direct read/write cursors, atomic operands/results, synchronization resource counters, ordered-append counters, completion flags, and backup addresses.
- MES state includes scheduler program/trap vectors, interrupt and CSR state, scratch/general registers, process quantum, doorbell control, debug registers, timer/cycle counters, and performance counter control.
- GUS/GL1/CH/GL2 state includes arbitration policy, QoS weights, credits, latency sampling, error flags, L1 counters, cache control/status, coherency/compression metadata behavior, prefetch tuning, soft reset, and writeback/invalidate status.

Persistence is hardware-defined. Control fields generally last until rewritten, queue/context teardown, power gating, suspend/resume, GPU reset, or ASIC reset. Status, error, performance, counter, completion, and diagnostic fields can be live, latched, sticky, self-clearing, or valid only while the relevant clock/power domains are active. The generated shift/mask constants do not encode those access semantics.

## Dependencies And Integration Points

This chunk must remain synchronized with AMD's generated GC 10.1.0 register database and especially with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h`, which provides the matching `mm*`, `reg*`, or offset symbols for the same register names.
- AMDGPU GFX 10 code such as `gfx_v10_0.c`, which includes this header, applies golden settings for registers including `GL2C_CTRL3`, builds command packets, and controls graphics engine initialization, reset, and ring operation.
- KFD GFX 10 code such as `kfd_packet_manager_v9.c`, `kfd_mqd_manager_v10.c`, and `kfd_device_queue_manager_v10.c`, which uses GC register fields for queue management, MQD setup, doorbell/control paths, and compute scheduling.
- GFX hub, SDMA, virtualization, and SoC bring-up files that include GC offsets/masks when programming shared graphics, memory, or virtualization-facing hardware.
- Packet and helper definitions such as `soc15d.h`, where related `CP_COHER_CNTL` packet fields mirror several coherency bits exposed in this generated register header.

Important integration surfaces are command submission, CP DMA, acquire/release memory coherency, indirect buffers, queue and doorbell setup, shader/cache flush and invalidate, geometry front-end programming, streamout/transform feedback, GDS atomic/synchronization operations, MES scheduling and debug support, GUS QoS tuning, cache arbitration, and GL2 metadata/compression/cache behavior.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while corrupting adjacent fields, programming the wrong cache policy, or producing misleading status reads.
- Offset/header version mismatch is dangerous. Pairing this GC 10.1.0 mask header with a different GC offset header can silently target the wrong register layout.
- Several fields affect coherency, cache invalidation, writeback, CP DMA, and command buffer addresses. Incorrect values can cause stale memory, lost writes, ring hangs, GPU faults, or data corruption that appears far from the bad write.
- Address fields are split into low/high registers and sometimes use alignment-implied low bits. Consumers must preserve swap, high-address, and alignment fields rather than treating every address as a flat 32-bit value.
- CP, CE, PFP, ME, MES, and doorbell fields participate in command processor scheduling. Bad masks in queue or command-buffer setup can break only compute, only graphics, only preemption, or only a virtualization/SRIOV path.
- Status and counter fields are not ordinary read/write storage. Completion, perfcount, error, FIFO-full/empty, calibration, and busy fields may be read-only, sticky, self-clearing, or clear-on-write/read depending on hardware.
- GDS/GWS/OA and atomic fields are synchronization-sensitive. Incorrect resource index, counter, type, destination, or operation masks can break inter-wave synchronization or ordered append behavior without an immediate compile-time signal.
- The range crosses generated address-block boundaries and ends mid-register. Whole-file conclusions about GL2C coverage require the next chunk because `GL2C_CTRL3` is incomplete here.
- Reserved, scratch, and debug fields are exposed as masks. Driver code should preserve reserved bits and avoid enabling debug/test paths unless a validated ASIC sequence requires it.

## Test Signals

Useful validation combines generated-header checks with graphics/compute hardware coverage:

- Build AMDGPU and KFD GFX 10 paths that include `gc_10_1_0_offset.h` and `gc_10_1_0_sh_mask.h`; missing or renamed macros should surface in `gfx_v10_0.c`, KFD queue/MQD files, SDMA, GFX hub, and virtualization code.
- Static-check complete register groups in lines 27309-29911 for matching `__SHIFT` and `_MASK` definitions, allowing the known boundary exception where `GL2C_CTRL3` masks continue after line 29911.
- Cross-check this range against AMD's generated GC 10.1.0 register database and adjacent GC headers when validating ASIC-generation drift.
- Exercise graphics and compute rings, IB submission, CP DMA copies, acquire/release memory packets, cache flush/invalidate paths, queue creation/destruction, doorbell writes, preemption/reset, suspend/resume, and GPU reset.
- Run workloads that stress streamout, indirect draw/dispatch, index buffers, geometry front-end state, shader instruction/data cache invalidation, GDS atomics/GWS synchronization, ordered append, and MES scheduling.
- Inspect register dumps, debugfs output, KFD diagnostics, and kernel logs for ring timeouts, VM faults, CP/MES hangs, failed queue scheduling, stale-cache symptoms, GDS synchronization failures, GL2 writeback/invalidate stalls, GUS error flags, or unexpected GL1/CH/GL2 busy/full status.
- For performance-sensitive fields, compare counter and workload behavior before/after changes to GUS priority/credit registers and GL1/GL2 cache controls; regressions may show up as reduced throughput, elevated latency, or only on specific ASIC revisions.

## Cross-Chunk Notes

This document intentionally covers only lines 27309-29911 of `gc_10_1_0_sh_mask.h`. The previous chunk owns the preceding CP signal semaphore and `CP_WAIT_REG_MEM_TIMEOUT` fields. This chunk starts at `CP_WAIT_SEM_ADDR_LO`, spans several generated GC address blocks through the start of `GL2C_CTRL3`, and stops before the final three `GL2C_CTRL3` masks and the following `GL2C_LB_*` registers. The later merge/reconciliation lane should combine adjacent chunks before making final per-file claims about complete CP, GUS, GL1/CH, or GL2 register coverage.

### subset-b-002461: lines 29912-32520

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 29912-32520

## Purpose

This chunk is generated AMD GC 10.1.0 register bitfield metadata. It contains no executable C code; it publishes preprocessor `__SHIFT` and `_MASK` constants used by AMDGPU and AMDKFD code to compose, update, and decode 32-bit MMIO register values. The matching register addresses and base indices live in `gc_10_1_0_offset.h`.

The selected range starts at the end of the GL2 cache/control block, covers a large graphics performance-counter decode area, and ends in the first RLC streaming performance monitor accumulator controls. Although this repository subtree is named `ceph-client`, this file is GPU driver hardware metadata, not filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocations, locks, or callbacks in this range. The exposed API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the in-register bit mask for the same field.
- Consumers pair these with `mm<REGISTER>` and `mm<REGISTER>_BASE_IDX` macros from `gc_10_1_0_offset.h`, then use AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, and bitfield helper patterns.

Major register groups in this chunk:

- GL2 cache/load-balancer and routing controls: `GL2C_LB_CTR_CTRL`, `GL2C_LB_DATA0` through `GL2C_LB_DATA3`, `GL2C_LB_CTR_SEL0/1`, `GL2A_ADDR_MATCH_*`, `GL2A_PRIORITY_CTRL`, `GL2A_CTRL`, and `GL2_PIPE_STEER_0/1`. These define load-balancer counter start/load/clear bits, counter data words, counter event selectors and dividers, GL2A address-match masks and limits, return-arbitration/stay-on-burst behavior, and pipe-to-channel steering fields.
- Perf counter value registers in `addressBlock: gc_perfddec`: low/high counter data registers for command processor blocks (`CPG`, `CPC`, `CPF`), `GRBM`, `GE`, primitive assembly (`PA_SU`, `PA_SC`, `PA_PH`), shader processor input (`SPI`), shader queue (`SQ`), shader export (`SX`), GDS/GCEA, texture blocks (`TA`, `TD`, `TCP`), GL2/GL1 cache blocks, CHC/CHCG/CHA, color/depth blocks (`CB`, `DB`), RLC, RMI, UTCL1, GCR, GUS, and VM/ATC L2 counter windows. Most value registers expose a full 32-bit `PERFCOUNTER_LO`, `PERFCOUNTER_HI`, or `DATA` field.
- Additional counter address blocks: `gc_gcatcl2pfcntrdec`, `gc_gcvml2prdec`, `gc_gcvml2perfddec`, and `gc_gcatcl2perfddec`, providing ATC L2, GCMC VM L2, and GCVML2 counter data fields.
- Perf counter select/configuration registers in `addressBlock: gc_perfsdec`: `*_PERFCOUNTER*_SELECT`, `*_SELECT1`, and related controls for CPG/CPC/CPF, GRBM and per-SE GRBM, GE, PA, SPI, SQ, SX, GDS, TA/TD/TCP, GL2C/GL2A/GL1C, CHC/CHCG, CB, and DB. Common fields are `PERF_SEL`, `PERF_SEL1`, `CNTR_MODE`, `PERF_MODE`, `PERF_MODE1`, `PERFMON_STATE`, `PERFMON_SAMPLE_ENABLE`, `PERFMON_ENABLE_MODE`, `PERFMON_RING_MODE`, and per-instance filters such as shader engine, shader array, VMID, queue, SIMD, pipe, and pixel pipe selection.
- Command processor draw/perf monitor controls: `CP_PERFMON_CNTL`, `CP_DRAW_OBJECT`, `CP_DRAW_OBJECT_COUNTER`, `CP_DRAW_WINDOW_*`, and `CP_DRAW_WINDOW_CNTL`, which gate or window draw-object-oriented performance measurement.
- Shader queue controls: `SQ_PERFCOUNTER0_SELECT` through `SQ_PERFCOUNTER15_SELECT`, `SQ_PERFCOUNTER_CTRL`, and `SQ_PERFCOUNTER_CTRL2`. These define per-counter event selection plus stage enable bits (`PS`, `VS`, `GS`, `ES`, `HS`, `LS`, `CS`), counter rate, flush behavior, and force enable.
- Color/depth filtering: `CB_PERFCOUNTER_FILTER` selects shader engine/array, VMID, cache action, client, and slice-specific filter fields; DB selectors use dual event selectors and counter/perf modes.
- RLC SPM and accumulator setup: `RLC_SPM_PERFMON_CNTL`, ring base/size, segment sizing, ring read/write pointers, SE/global mux selector address/data pairs, skew and sample-delay registers, accumulator data/control RAM address/data registers, `RLC_SPM_ACCUM_STATUS`, `RLC_SPM_ACCUM_CTRL`, and the beginning of `RLC_SPM_ACCUM_MODE`. These fields define SPM ring layout, sampling interval, mux programming, sampling skew, accumulator state, reset/start/rearm strobes, and automatic accumulation/SPM enable modes.

Field naming is descriptive. `*_LO`/`*_HI` are counter halves; `*_SELECT` programs an event source; `*_SELECT1` typically holds the second event selector and counter mode; `CNTR_MODE` and `PERF_MODE` choose accumulation/sample semantics; `START`, `LOAD`, `CLEAR`, and `Strobe*` fields trigger hardware actions; `DONE`, `OVERFLOW`, `IDLE`, and `IN_PROGRESS` fields expose status; `RESERVED` fields mark bits that should be preserved by read-modify-write consumers unless an ASIC guide says otherwise.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by consumers in AMDGPU and AMDKFD:

1. GFX10/Navi code includes `gc_10_1_0_offset.h` and `gc_10_1_0_sh_mask.h`.
2. Driver paths select a concrete register using the `mm*` offset macro and base index.
3. The code composes values with the field masks and shifts from this header.
4. MMIO helpers read or write the register while firmware, CP/RLC microcode, perf tooling, or debug paths coordinate the actual hardware sequence.

The chunk describes fields needed for perf monitor setup and sampling, but it does not encode event IDs, allowed counter modes, sampling order, polling delays, reset sequencing, interrupt behavior, or locking. Safe ordering around counter clear/load/start, CP draw windows, SPM ring programming, mux selector writes, accumulator start/rearm/reset, and status polling must come from the consuming driver and hardware programming guide.

## State And Persistence Behavior

This file stores no software state and persists nothing. It describes hardware state exposed through GC 10.1 registers.

The represented hardware state includes GL2 load-balancer counter values and selectors, GL2A address-match/priority controls, GL2 pipe steering, many 64-bit performance counters exposed as low/high 32-bit registers, event-selector configuration, per-block/per-instance filters, CP draw-window state, SQ stage enable/rate controls, CB/DB filters, and RLC SPM ring and accumulator state. Persistence is hardware-defined: values may remain until explicitly changed, reset by a GPU reset, cleared by power-gating or suspend/resume, or advanced by hardware while counters are running. Several fields are action strobes or live status bits rather than durable configuration.

The macros do not identify access class. A field may be read-only, write-only, write-one-to-clear, self-clearing, sticky, latched, or reserved depending on the register definition. Consumers must preserve unrelated and reserved bits when updating mixed-control registers.

## Dependencies And Integration Points

The direct dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h`, which provides the corresponding `mm*` register offsets and base indices. The same generated register database also includes default-value and enum headers such as `navi10_enum.h`, where perf counter and SPM mode values are defined.

Known include users of the GC 10.1.0 shift/mask header include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nv.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_packet_manager_v9.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v10.c`

Integration points are graphics IP initialization, power management, GPU reset/recovery, KFD queue setup, developer/debug register access, performance counter programming, profiling, RLC SPM streaming, shader stage and VMID filtering, draw-window measurement, and hardware validation tooling. This chunk is especially relevant to perf event collection because it provides both counter data register definitions and selector/control fields for most GFX pipeline blocks.

## Risks And Edge Cases

- Header/offset mismatch is the main correctness risk. Pairing `gc_10_1_0_sh_mask.h` with a different GC offset header can compile while addressing the wrong register or field.
- The macros are untyped constants. A wrong event selector, shift, mask, or register name can silently program an unintended block, counter, shader engine, VMID, SIMD, queue, pipe, or pixel pipe.
- Performance counter registers are sequencing-sensitive. Counters often require clear/load/start/stop ordering, clock/power availability, shader-stage filtering, VMID/context selection, and stable read ordering for 64-bit low/high values.
- SPM programming is particularly stateful. Ring base/size, segment sizing, mux selector address/data writes, read/write pointers, skew/sample-delay fields, accumulator RAM programming, and start/rearm/reset strobes must be coordinated with `RLC_SPM_ACCUM_STATUS` bits such as `AccumDone`, `SpmDone`, `AccumOverflow`, `SequenceInProgress`, `FinalSequenceInProgress`, `AllFifosEmpty`, and `FSMIsIdle`.
- Full-width `0xFFFFFFFFL` masks are common for counter data and selector payloads. Consumers must avoid treating every full-width field as safe to write; many full-width registers are readback data, indirect data windows, or hardware-owned counters.
- Reserved fields appear throughout. Direct writes that do not preserve reserved bits can create ASIC-specific failures that only show up on particular SKUs, power states, or firmware revisions.
- Block-local filters can make tests look falsely idle. A counter may remain zero because the selected shader stage, VMID, SE/SA, SIMD, queue, pipe, client, or slice filter does not match current workload placement.
- The chunk boundary is artificial. It starts after `GL2C_CTRL3` and ends in `RLC_SPM_ACCUM_MODE`; adjacent chunks are needed for a complete per-file view.

## Test Signals

Useful validation is mostly build, static, and hardware/profiling coverage:

- Build coverage for AMDGPU and AMDKFD files that include `gc_10_1_0_offset.h` and `gc_10_1_0_sh_mask.h`.
- Generated-header checks that each `__SHIFT` has a matching `_MASK`, each mask is aligned to its shift, and register names match entries in `gc_10_1_0_offset.h`.
- Static checks for non-overlapping fields within each register except documented aliases or full-width data fields.
- Perf counter smoke tests that clear/load/start counters, run known graphics and compute workloads, stop/read counters, and verify low/high counter behavior is monotonic or otherwise plausible.
- Filter coverage across shader stages, VMIDs, queues, shader engines/arrays, SIMDs, pixel pipes, cache clients, and CB/DB filters to catch field-shift or mask mistakes that only appear under non-default placement.
- RLC SPM tests that configure ring base/size, mux selections, sample interval, segment size, accumulator mode, and start/rearm/reset sequences, then poll status bits for completion, overflow, empty FIFOs, and idle state.
- Reset, suspend/resume, runtime power-management, and GPU recovery tests while perf counters or SPM are active, because hardware-owned counter and ring state can be lost, stale, or require reinitialization.
- Regression indicators include zero or saturated counters for active workloads, counter overflows at unexpected rates, profiler event misattribution, SPM ring pointer stalls, accumulator overflow/done never asserted, GPU hangs during perf collection, or failures isolated to specific GFX10/Navi SKUs.

### subset-b-002462: lines 32521-35035

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 32521-35035

## Scope And Purpose

This chunk is part of the generated AMD GC 10.1.0 register shift/mask header. It provides preprocessor constants for bit positions (`__SHIFT`) and bit masks (`_MASK`) used when amdgpu and amdkfd code programs or decodes memory-mapped graphics-core registers. The matching `gc_10_1_0_offset.h` file provides register addresses; this header provides field layout.

The requested range starts in the middle of `RLC_SPM_ACCUM_MODE`: the shift definitions and the first three masks for that register are in the previous chunk, while this chunk begins with the remaining masks for global/SE load override and automatic perfmon reset behavior. It then covers a large collection of performance-monitor selectors and result-control fields for RLC, RMI, GCR, UTCL1, PA_PH, GL1A, CHA, GUS, GC ATC L2, and GC VM L2 blocks. The range continues through the `gc_rlcdec`, `gc_rlcrdec`, and `gc_rlcsdec` address blocks, ending inside `RLC_RLCS_GE_FAST_CLOCK`; the remaining masks for that register and following RLCS boot/load/power registers are outside this chunk.

There are no functions, structs, branches, loops, or direct runtime side effects in this chunk. Its exported surface is generated macro metadata. Runtime behavior occurs only when driver code combines these masks and shifts with register addresses and uses helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, `RREG32_SOC15`, and related SOC15 accessors.

## Register Blocks Covered

The opening RLC SPM/perfmon area covers the tail of `RLC_SPM_ACCUM_MODE`, accumulation threshold/sample/write-count fields, SPM perfmon segment sizes for shader engines and global data, virtualization pause/status bits, generic RLC perfmon state/sample enable, RLC perfcounter event selects, GPU IOV performance-counter control/address/data windows, and perfmon clock state controls.

The chunk then defines performance-counter selectors for several graphics sub-blocks:

- `RMI_PERFCOUNTER*` and `RMI_PERF_COUNTER_CNTL` fields for request/memory-interface event selection, counter modes, CID/VMID filters, burst thresholding, soft reset, and SPM routing.
- `GCR_PERFCOUNTER*` fields for graphics-cache-router event selection and counter mode selection.
- `UTCL1_PERFCOUNTER*` fields for UTCL1 event and counter-mode selection.
- `PA_PH_PERFCOUNTER*` fields for primitive-assembler/primitive-hardware event selection across multiple counters and extended select registers.
- `GL1A_PERFCOUNTER*`, `CHA_PERFCOUNTER*`, and `GUS_PERFCOUNTER*` fields for GL1A, CHA, and GUS event selection, counter modes, masks, and mode configuration.

The `gc_gcatcl2pfcntldec`, `gc_gcvml2pldec`, `gc_gcvml2perfsdec`, and `gc_gcatcl2perfsdec` address blocks cover ATC L2 and VM L2 performance-counter configuration. These include per-counter event select fields, clamp/clear/reset behavior, result-control fields for selecting which counter result is exposed, and secondary selector/mode registers for the `PERFCOUNTER2_*` blocks.

The `gc_rlcdec` address block is the largest portion of the chunk. It defines RLC control, status, firmware, safe-mode, memory sleep, SMU handshake, timestamp, timer, interrupt, light-sleep/load-balance, clock-gating, power-gating, WGP status, SERDES, scratch/general-purpose, SPM, SRM, CSIB, PACE, SMU, scheduler, UTCL1, semaphore, CP EOF, prewalker, R2I, SPP, PCC stretch, SPM clock count, doorbell monitor, and related status fields.

The `gc_rlcrdec` block contains RLC SPP CAM and PACE scratch address/data windows. These are small indexed register windows: address fields select an entry or extension, and data fields carry the payload.

The `gc_rlcsdec` block covers RLCS decode/control/status fields. This includes decode start/dump address fields, exception registers, RLCS general registers, CGCG request/status, SMU GFXCLK status/control, SOC and GFX deep-sleep controls, GPM status mirrors, aborted power-down sequence status, DIDT force-stall state, IOV command/context/scheduler/VM-busy status, GPM status 2, GRBM soft reset, power-gating change/read mirrors, load-balance status/control, interrupt-handler semaphore/context fields, WGP status/read mirrors, CP and SPM interrupt ack/info registers, DSM trigger, and the beginning of GE fast-clock status/control.

## Important APIs, Types, And Macros

The important API is the generated macro naming convention:

- `<register>__<field>__SHIFT` gives the bit offset for a field in a 32-bit register.
- `<register>__<field>_MASK` gives the field mask.
- `// addressBlock: ...` comments identify generated register decode blocks.
- `//<register>` comments delimit generated register groups, but they are comments rather than compiled symbols.

The practical consumers are the AMD register helper macros and SOC15 register access paths. Code includes `gc/gc_10_1_0_offset.h` for addresses and `gc/gc_10_1_0_sh_mask.h` for field layouts, then reads, writes, or updates fields with helpers such as `REG_SET_FIELD` and `REG_GET_FIELD`. GC 10.1.0 include sites in this tree include `amdgpu/gfx_v10_0.c`, `amdgpu/gfxhub_v2_0.c`, `amdgpu/mxgpu_nv.c`, `amdgpu/sdma_v5_0.c`, `amdgpu/nv.c`, `amdgpu/amdgpu_amdkfd_gfx_v10.c`, and multiple amdkfd v10 queue/packet/MQD paths.

The chunk itself defines no C types. Its "types" are hardware field classes: single-bit strobes/status bits, narrow enum-like mode fields, event selector fields, VMID/CID/VFID filters, 32-bit data windows, low/high timestamp or counter halves, packed address/size fields, and reserved masks that document bits callers should not modify.

## Functional Field Groups

The RLC SPM accumulation fields describe how streaming performance monitor samples are accumulated and segmented. Threshold, requested sample count, data RAM write count, per-SE segment size, global segment size, pause request/status, and clock state fields are part of the low-level surface used to control and observe SPM capture. The chunk starts after some `RLC_SPM_ACCUM_MODE` definitions, so adjacent chunk data is needed for the full mode register.

The performance-counter selector groups configure which hardware events are counted. Repeated `PERF_SEL`, `PERF_SEL1`, `PERF_SEL2`, `PERF_SEL3`, `PERF_MODE*`, `CNTR_MODE`, and `COUNTER_MODE` fields are the packed selector/mode surfaces for RMI, GCR, PA_PH, GL1A, CHA, GUS, ATC L2, and VM L2 counters. Result-control fields select or reset exposed counter results, while mode fields control counting windows, masks, and SPM integration.

The RLC control and firmware fields expose high-level run-control state: RLC enable/idle/status, firmware version, safe-mode commands, RLCV and SMU safe-mode paths, SMU response/message/command/argument mailboxes, GPM thread reset/priority/enable, jump-table restore, and CP DMA complete indicators. These fields are tied to firmware boot, graphics microcontroller sequencing, and recovery.

The RLC timer, clock, and interrupt fields expose monotonic hardware counters and interrupt conditions. Timer interrupt registers, timer control/status, reference timestamp halves, GPU/GFX/ref clock count registers, capture strobes, 32-bit clock selection, SPM-specific clock count, PACE timer controls, interrupt status/disable/force fields, CP EOF/spare interrupts, and CP stat invalidation fields are all stateful diagnostic or synchronization surfaces.

The power-management and clock-gating fields cover RLC memory sleep, MGCG/CGCG/CGLS controls, clock-gating ramp controls, power-gating control/status/request/delay fields, dynamic/static WGP status, always-on/maximum/initial WGP masks, auto power-gating control, load-balance counters/configuration, SOC/GFX deep-sleep controls, SMU GFXCLK request/status/control, and PCC stretch hysteresis. These fields integrate RLC firmware behavior with GPU power and clock transitions.

The UTCL1/prewalker/error fields configure or report translation/cache behavior for RLC GPM and SPM paths. The chunk includes GPM and SPM UTCL1 control fields, UTCL1 status registers, SPM and GPM per-thread error fields, prewalker controls, trigger fields, prewalker address/size registers, and R2I controls.

The SPP fields configure shader/performance profiling state. They include `RLC_SPP_CTRL`, shader-profile enable masks, SSF capture enable and thresholds, inflight readback address/data, profile info, global shader ID and validity, status, private status registers, private-level maximum, stall-state update, PBB info, reset, CAM address/data windows, and extended CAM windows.

The SRM and indexed-window fields include SRM control/command/status/abort fields plus eight indexed control address/data pairs. These represent command and indirect-access surfaces where write order and selected index matter.

The RLCS fields expose the RLC slave/decode side of this hardware block: exception registers, general registers, clock-gating request/status, deep-sleep controls, GPM status mirrors, IOV command and VM-busy status, power-gating change/read mirrors, load-balance mirrors, interrupt-handler context assembly, CP/SPM interrupt acknowledge and info fields, DSM trigger, and GE fast-clock status. The final `RLC_RLCS_GE_FAST_CLOCK` register is incomplete in this chunk because only `FAST_CLKS_CHANGED_MASK` appears before the line boundary.

## Control Flow And State Behavior

This header has no direct control flow. It participates in runtime control flow through macro expansion: driver code reads a 32-bit register, masks/shifts fields into or out of local values, then writes the register back or interprets status. The same generated field names can be used in initialization tables, register dumps, interrupt handling, performance-counter setup, power-management sequences, and debug tooling.

The hardware state described by this chunk persists in GPU registers until changed by driver writes, firmware writes, reset, suspend/resume, virtualization context switching, or hardware events. Configuration state includes event selectors, counter modes, safe-mode commands, timer controls, clock-gating and power-gating enables, WGP masks, SPM/UTCL1/SPP settings, SRM indexed addresses, interrupt controls, and IOV perf counter addressing. Status state includes idle/busy bits, timer status, interrupt status, clock counts, write counts, error reports, GPM/RLCS status, VM-busy masks, power-gating change bits, load-balance flags, IH busy/credit state, and WGP activity.

Several groups are strobe-like or clear/ack sensitive. Safe-mode commands, timer clears, capture strobes, soft reset bits, interrupt acknowledge bits, DSM trigger, perf counter reset/clear fields, CP stat invalidation controls, SPP reset, and SRM abort/command bits should not be treated as durable ordinary configuration fields. A full-register write using stale values can accidentally retrigger, clear, or acknowledge hardware state.

Many groups are indirect or banked windows. SRM indexed address/data pairs, SERDES read/write index/data fields, SPP CAM address/data fields, PACE scratch address/data fields, and GPU IOV perf counter read/write address/data fields require correct address selection before data access. The masks are necessary but not sufficient; callers also need correct ordering and serialization around the selected index.

Virtualization-related fields are visible in the SPM pause path and GPU IOV/RLCS IOV status windows. These fields can reflect PF/VF ownership, VFID selection, per-VF counter IDs, scheduler-block state, or VM-busy state. In SR-IOV paths, stale or incorrectly selected VFID/CNT_ID fields can expose misleading counter data or disturb the wrong virtual function's accounting.

## Dependencies And Integration Points

This file must stay synchronized with `gc_10_1_0_offset.h`. The offset header defines the `mm...` register symbols and base indices; this file defines field masks and shifts for those registers. A missing or renamed field usually fails at compile time when referenced by register helper macros, while an incorrect numeric mask may compile but program the wrong hardware bits.

The main direct include site is `amdgpu/gfx_v10_0.c`, which includes this header and the matching offset header for GC 10 register programming, golden settings, register dumps, RLC firmware sequencing, clock/power handling, and debug paths. That file's register dump tables include RLC status entries such as `mmRLC_STAT`, `mmRLC_RLCS_GPM_STAT_2`, and nearby RLCS boot/load status, showing this generated namespace is part of user-visible diagnostics even when many fields are not individually hand-coded.

amdkfd v10 integration includes this header through queue, packet, MQD, and amdgpu-to-KFD support files. Those paths depend on the same GC 10 field namespace when programming compute queues, packet-manager state, and interrupt/context decoding for GFX10-family hardware.

`mxgpu_nv.c` includes the header for SR-IOV support. The GPU IOV perf counter fields and RLCS IOV status fields in this chunk are specifically relevant to virtualized GPU operation, where PF-side code may coordinate counters, scheduling blocks, command status, and per-VM busy state.

Performance tooling and debug paths integrate indirectly through the repeated perfmon/perfcounter field layout. The register blocks covered here provide event selection, mode programming, result selection, counter reset/clear, and readback selection for many GC sub-blocks. Even if a particular counter group has no high-level named helper in this tree, the generated masks are used by register access helpers, register dumps, debugfs-style tooling, or hardware-validation code that speaks the register names directly.

## Risks And Edge Cases

The primary risk is generated-header drift from the hardware specification or from the matching offset header. A wrong shift or mask can silently corrupt a neighboring field in the same 32-bit register. In this chunk that can break performance-counter selection, safe-mode sequencing, clock/power gating, WGP masks, UTCL1 error handling, SPP profiling, SRM indexed access, interrupts, or virtualization status accounting.

The chunk boundaries split logical registers. `RLC_SPM_ACCUM_MODE` is only completed here, and `RLC_RLCS_GE_FAST_CLOCK` is only started here. Any per-file summary must reconcile this report with adjacent chunks before claiming complete coverage for those registers.

Reserved masks are significant. Many registers expose large `RESERVED_MASK` regions, and code should use field helpers or read-modify-write patterns that preserve reserved bits unless the hardware programming guide explicitly says otherwise. This is especially important around power/clock controls, interrupt status registers, and firmware-visible command/status windows.

Performance-counter fields are dense and repeated. Small selector-width differences matter: for example some blocks use 9-bit selectors, others use 10-bit selectors, and mode fields occupy different high bits. Reusing a selector helper across blocks without the matching generated mask can truncate event IDs or overwrite mode bits.

Status and control bits often share nearby registers. Timer status, interrupt state, clock-capture state, power-gating change flags, load-balance flags, GPM status mirrors, and CP/SPM interrupt info require careful read/clear ordering. Tests that only check for successful writes may miss lost interrupts, stale status, or counters sampled in the wrong window.

Indirect windows are ordering-sensitive. SERDES, SRM, SPP CAM, PACE scratch, and IOV perf counter address/data pairs can produce valid-looking reads or writes against the wrong selected entry if callers race, skip barriers, or reuse a stale index. This risk is amplified in virtualization and debug tooling where multiple actors may inspect hardware state.

Power-management fields are timing-sensitive. RLC clock-gating, CGCG/CGLS ramping, memory sleep, dynamic WGP power state, deep sleep, SMU GFXCLK requests, and low-busyness controls can fail only around suspend/resume, reset, mode switches, or firmware transitions. Incorrect field definitions may surface as hangs, incomplete RLC boot, stuck busy/idle state, or intermittent power-management regressions.

## Test Signals

Build-time coverage should catch missing or renamed generated macros in GC 10 include sites such as `gfx_v10_0.c`, `gfxhub_v2_0.c`, `mxgpu_nv.c`, `sdma_v5_0.c`, and amdkfd v10 files. A useful static signal is that every field referenced by `REG_SET_FIELD`, `REG_GET_FIELD`, or SOC15 register-list macros resolves against the paired offset and sh/mask headers.

RLC firmware and reset validation should watch RLC idle/status, safe-mode completion, SMU response/message paths, GPM thread enable/reset behavior, CP DMA completion flags, GRBM soft reset behavior, and RLCS/GPM status mirrors. Regressions often appear as boot hangs, failed GPU reset, stuck safe mode, or RLC firmware not reaching expected idle states.

Power-management validation should exercise clock gating, memory sleep, WGP power-gating, dynamic PG request/status, load-balance counters, SMU GFXCLK request/status, SOC/GFX deep-sleep controls, and suspend/resume. Useful signals include no stuck busy bits, expected power-state transitions, no unexpected TC transaction errors, and stable behavior across repeated reset and runtime-PM cycles.

Performance-counter validation should program representative events across RLC, RMI, GCR, UTCL1, PA_PH, GL1A, CHA, GUS, ATC L2, and VM L2 counters. Tests should cover selector width, mode fields, counter reset/clear, result selection, SPM routing, low/high readback consistency, and counter behavior under known workloads.

SPM/SPP validation should cover SPM accumulation threshold/sample counts, pause/resume virtualization status, segment sizing, SPM interrupt status, SPM clock counts, SPP shader-profile enable masks, SSF capture thresholds, SPP inflight reads, CAM indexed access, and SPP reset. Good signals include expected sample counts, no accumulation overflow under normal programmed windows, and coherent profile readback.

Virtualization validation should exercise GPU IOV perf counter read/write address/data windows, VFID/CNT_ID selection, RLCS IOV command status, context-location size, scheduler block state, VM busy status, and IH context fields with SR-IOV enabled. Tests should verify that per-VF accounting and status are isolated and that pause/ack paths do not affect the wrong VF.

Interrupt and diagnostic tests should check CP/SPM interrupt ack/info registers, IH credit/busy state, RLC timer interrupts, CP EOF/spare interrupts, CP stat invalidation status/control, GE fast-clock change reporting, and DSM trigger behavior. Hardware register-spec cross-checks remain the strongest signal because this file is generated metadata and many errors compile cleanly while changing live hardware behavior.

### subset-b-002463: lines 35036-37342

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 35036-37342

## Purpose

This chunk is generated AMD GC 10.1.0 register field metadata. It contains no executable driver logic; it publishes preprocessor constants for field shifts and bit masks used when reading or writing Graphics Core MMIO registers through AMDGPU's SOC15 register helpers.

The requested range spans two hardware decode areas:

- The tail of the `RLC_RLCS` register block, beginning in the final fields of `RLC_RLCS_GE_FAST_CLOCK` and then covering RLC bootload, idle/busy, interrupt-clear, power-brake, scratch/general, auxiliary-address, SPM/SQTT, CP DMA source override, UTCL2 override, MP1 doorbell, bootload-ID status, and EDC interrupt control fields.
- The beginning and a large repeated portion of `addressBlock: gc_pwrdec`, covering `CGTS` and `CGTT` clock-gating/throttling/status fields for shader arrays, quads, TCC disable state, read muxing, SPI clock override groups, and per-WGP/per-CU SIMD/SQ/SQC/LDS/TA/TD/TCP control registers through `SA1_WGP11_CU1_TCP_CTRL_REG`.

The chunk has 2,186 `#define` lines: 1,095 `__SHIFT` constants and 1,091 `_MASK` constants. The line boundaries are artificial: the first visible lines are the end of `RLC_RLCS_GE_FAST_CLOCK`, and the final visible lines stop inside `CGTS_SA1_WGP11_CU1_TCP_CTRL_REG`. Neighboring chunks are required for complete per-file coverage.

Although this source tree is under a local `ceph-client` mirror, this header is AMDGPU kernel-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locking primitives in this range. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a field inside a 32-bit hardware register.
- `<REGISTER>__<FIELD>_MASK`: field mask for extracting, clearing, or setting that field.

These constants are paired with address macros from `gc_10_1_0_offset.h`, such as `mmRLC_RLCS_BOOTLOAD_STATUS`, `mmCGTS_SA0_QUAD0_SM_CTRL_REG`, and `mmCGTS_TCC_DISABLE`. Runtime code then uses helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32`, `WREG32`, `REG_GET_FIELD`, and `REG_SET_FIELD`.

Major field groups in this chunk:

- `RLC_RLCS_BOOTLOAD_STATUS`: reports whether RLC/RLCG IRAM has loaded and whether bootload/autoload is complete. `BOOTLOAD_COMPLETE` is the field actively polled by GFX v10 initialization.
- `RLC_RLCS_POWER_BRAKE_CNTL` and `_TH1`: expose power-brake state, interrupt clear, and hysteresis counters.
- `RLC_RLCS_GRBM_IDLE_BUSY_STAT` and `_INT_CNTL`: expose GRBM/RLC idle status, SDMA busy bits, changed bits, and interrupt-clear bits.
- `RLC_RLCS_CMP_IDLE_CNTL`: exposes compare-idle state, interrupt clear, and hysteresis controls.
- `RLC_RLCS_GENERAL_0` through `_5`: full-width 32-bit scratch/data registers.
- `RLC_RLCS_AUXILIARY_REG_1` through `_4`: 18-bit auxiliary register address fields.
- `RLC_RLCS_SPM_SQTT_MODE`, `RLC_RLCS_CP_DMA_SRCID_OVER`, `RLC_RLCS_UTCL2_CNTL`, and `RLC_RLCS_MP1_RLC_DOORBELL_CTRL`: control or override profiling/trace mode, CP DMA source ID, UTCL2 behavior, GPA/VF values, and MP1/RLC doorbell interrupt state.
- `RLC_RLCS_BOOTLOAD_ID_STATUS1` and `_STATUS2`: 64 one-bit firmware/component loaded indicators, split across two 32-bit registers.
- `CGTS_SA*_QUAD*_SM_CTRL_REG`: shader-array quad-level clock-gating mode, override, monitor, delay, and enable fields.
- `CGTS_*_CLK_MONITOR_DELAY_REG`: off/on monitor delay fields for each shader-array quad.
- `CGTS_RD_CTRL_REG` and `CGTS_RD_REG`: mux selection and 32-bit readback data for CGTS diagnostic/status reads.
- `CGTS_TCC_DISABLE` and `CGTS_USER_TCC_DISABLE`: high and low TCC-disable bitmaps consumed by GFX code to derive the disabled TCC mask.
- `CGTS_STATUS_REG`: per-quad MGCG enabled and clock-gating status fields.
- `CGTT_SPI_CGTSSM_CLK_CTRL`: SPI CGTS state-machine group override fields.
- Repeated `CGTS_SA{0,1}_WGP{00,01,02,10,11}_CU{0,1}_{SIMD0,SIMD1,TATD,TCP}_CTRL_REG` families: per-compute-unit clock/light-sleep control fields for SIMD, SQ, SQC, LDS, TA, TD, TCPF, and TCPI subblocks.

## Control Flow

This header has no local control flow. It participates in driver control flow only through macro expansion in the AMDGPU GFX, SDMA, KFD, GFXHUB, SR-IOV, and platform glue code that includes `gc/gc_10_1_0_sh_mask.h`.

The clearest runtime sequences tied to this chunk are:

1. GFX v10 RLC autoload completion waits read `mmCP_STAT` and `mmRLC_RLCS_BOOTLOAD_STATUS`.
2. The driver extracts `RLC_RLCS_BOOTLOAD_STATUS.BOOTLOAD_COMPLETE` with `REG_GET_FIELD`.
3. If CP is idle and bootload is complete before `adev->usec_timeout`, GFX initialization continues; otherwise initialization fails with an RLC autoload timeout.

Clock-gating programming follows a separate path:

1. GFX v10 clock-gating update enters RLC safe mode.
2. For medium-grain clock-gating workarounds, the driver iterates arrays of `mmCGTS_*_TCP_CTRL_REG` offsets.
3. It reads each register, sets the shared `CGTS_SA0_WGP00_CU0_TCP_CTRL_REG__TCPI_LS_OVERRIDE_MASK` bit pattern, and writes the value back. The field layout is reused across the repeated TCP control registers, so one canonical mask is used for many homologous registers.
4. It iterates the quad SM control registers, clears `CGTS_SA0_QUAD0_SM_CTRL_REG__SM_MODE_MASK`, writes mode `2` at `SM_MODE__SHIFT`, and restores normal execution outside the workaround path.

TCC discovery is another direct integration point. GFX v10 reads `mmCGTS_TCC_DISABLE` and `mmCGTS_USER_TCC_DISABLE`, then derives `adev->gfx.config.tcc_disabled_mask` from `CGTS_TCC_DISABLE.TCC_DISABLE` and `HI_TCC_DISABLE`.

The RLC idle/busy, power-brake, UTCL2, bootload-ID, EDC, CGTS status, read-mux, and SPI override fields are hardware control/status surfaces. This chunk does not encode the ordering rules for using them; sequencing is imposed by the relevant GFX/RLC/power-management code and by ASIC programming requirements.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed GPU state.

The RLC fields represent firmware boot/autoload state, RLC scratch data, interrupt-clear bits, busy/idle state, doorbell state, EDC interrupt state, auxiliary register addressing, and memory/virtualization override controls. Some fields are status/readback fields, some are control fields, and some names imply side-effect semantics such as interrupt clear. The header does not distinguish read-only, write-one-to-clear, sticky, self-clearing, or reserved behavior beyond naming and masks.

The CGTS/CGTT fields represent graphics power-management and clock-gating state. Quad-level SM control registers can enable/disable or override medium-grain clock gating and monitor timing. Per-WGP/per-CU registers carry subblock light-sleep and busy-override state for SIMD, SQ, SQC, LDS, TA/TD, and TCP units. TCC-disable registers describe hardware-disabled or user-disabled cache slices; the driver persists the interpreted disabled bitmap in `adev->gfx.config.tcc_disabled_mask`.

Persistence is hardware-defined. Register values generally survive until a GPU reset, suspend/resume power transition, clock-gating reprogramming, firmware reload, or ASIC-specific power-management event changes them. Driver-maintained derived state, such as the disabled TCC mask, persists in `struct amdgpu_device` only for the lifetime of the initialized device instance.

## Dependencies And Integration Points

This header must stay in sync with AMD's generated GC 10.1.0 register database, especially:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h`, which provides the matching `mm...` register offsets and `_BASE_IDX` values.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_default.h`, where generated reset/default values are available for related registers.
- SOC15 register access helpers and field helpers used by AMDGPU code, including `RREG32_SOC15`, `WREG32_SOC15`, `RREG32`, `WREG32`, `REG_GET_FIELD`, and `REG_SET_FIELD`.

Direct include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nv.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_packet_manager_v9.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v10.c`

Observed direct consumers of fields from this chunk include:

- `gfx_v10_0_wait_for_rlc_autoload_complete()`, which polls `RLC_RLCS_BOOTLOAD_STATUS.BOOTLOAD_COMPLETE`.
- `gfx_v10_0_get_tcc_info()`, which reads `CGTS_TCC_DISABLE` and `CGTS_USER_TCC_DISABLE` fields to form the disabled TCC mask.
- `gfx_v10_0_apply_medium_grain_clock_gating_workaround()`, which uses CGTS TCP light-sleep override masks and quad SM mode masks/shifts.
- GFX debug/register dump tables, which include `mmRLC_RLCS_BOOTLOAD_STATUS` in the GC register list for diagnostic capture.

## Risks And Edge Cases

- The macros are untyped numeric constants. A wrong shift or mask compiles cleanly but can read the wrong bit, clear a reserved bit, miss a firmware-completion condition, or program an unintended clock-gating override.
- The range contains many structurally repeated register families. A copy or generation error in one `SA`, `WGP`, `CU`, or subblock instance may only fail on a subset of shader arrays, compute units, or ASIC variants.
- Some GFX code intentionally reuses a representative mask, such as `CGTS_SA0_WGP00_CU0_TCP_CTRL_REG__TCPI_LS_OVERRIDE_MASK`, across homologous TCP control registers. That assumes identical field layout across the repeated family; if a future generated header diverges, this pattern becomes risky.
- RLC bootload completion is on an initialization critical path. If `BOOTLOAD_COMPLETE` is wrong, GFX initialization can time out even when firmware loaded, or proceed before firmware is ready.
- Interrupt-clear and status fields are side-effect-sensitive. Misusing fields named `INT_CLEAR`, busy-changed, EDC interrupt, or doorbell clear can lose events or leave interrupt sources latched.
- Reserved masks are present throughout the RLC and CGTS fields. Driver code must avoid blindly writing reserved bits unless hardware programming guides explicitly require the full value.
- Clock-gating and light-sleep overrides affect power and stability. Incorrect CGTS programming can cause higher power draw, hangs during idle transitions, shader/TCP/SQ/LDS unit wake failures, or bugs that reproduce only under low-load or suspend/resume paths.
- The chunk's first and last register families are partial. File-level analysis must merge this document with adjacent chunks before making claims about complete `RLC_RLCS_GE_FAST_CLOCK` or `CGTS_SA1_WGP11_CU1_TCP_CTRL_REG` coverage.

## Test Signals

Useful validation signals are integration and hardware-oriented rather than unit-test oriented:

- Kernel build coverage for AMDGPU with `gfx_v10_0.c`, KFD, SDMA, GFXHUB, and SR-IOV include paths enabled catches missing or renamed macros.
- GFX v10 probe/init logs should not show `rlc autoload: gc ucode autoload timeout`; that path exercises `RLC_RLCS_BOOTLOAD_STATUS.BOOTLOAD_COMPLETE`.
- Register dumps should include sane `mmRLC_RLCS_BOOTLOAD_STATUS` values alongside RLC/CP status registers after initialization.
- TCC topology reporting should produce a stable `adev->gfx.config.tcc_disabled_mask` across boots for the same ASIC and fuse state.
- Clock-gating validation should exercise idle, load, suspend/resume, and runtime power-management transitions with `AMD_CG_SUPPORT_GFX_CGTS_LS` and related GFX CG flags enabled.
- GPU stress workloads should run cleanly after `gfx_v10_0_apply_medium_grain_clock_gating_workaround()` modifies CGTS TCP and SM control registers; failures may appear as hangs, VM faults, ring timeouts, or unstable power-state transitions.
- Low-level register tracing around CGTS writes can verify that only intended override and mode fields are changed and reserved bits are preserved.

### subset-b-002464: lines 37343-39656

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 37343-39656

## Scope

This chunk is a generated AMD GC 10.1.0 shift/mask header segment. It covers lines 37343 through 39656 and contains 2,192 `#define` entries: 1,093 `__SHIFT` macros and 1,101 `_MASK` macros. The count difference is expected for this sliced range because it starts with the tail masks of `CGTS_SA1_WGP11_CU1_TCP_CTRL_REG` and ends after only the first `GFX_PIPE_PRIORITY__HP_PIPE_SELECT__SHIFT` definition.

The content is declarative only. There are no C functions, structs, enums, variables, branches, loops, allocations, locks, or direct hardware accesses in this range. Its exported surface is a set of C preprocessor constants that describe bit positions and masks for Graphics Core hardware registers.

## Purpose

`gc_10_1_0_sh_mask.h` provides symbolic bitfield definitions for AMDGPU and AMDKFD code targeting the GC 10.1.0 register layout. Consumers pair these macros with register offsets from `gc_10_1_0_offset.h` and helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15` to build or decode MMIO register values without embedding raw bit numbers.

This chunk covers three main areas:

- The end of the compute-unit clock/tree shader control register families for shader arrays `SA0` and `SA1`, WGP 12, CU 0/1, plus the tail of `SA1_WGP11_CU1_TCP_CTRL_REG`.
- A broad set of graphics clock-throttling and clock-control registers named `CGTT_*`, plus related block controls such as `SQ_ALU_CLK_CTRL`, `TD_CGTT_CTRL`, `TA_CGTT_CTRL`, `DB_CGTT_CLK_CTRL_0`, `CB_CGTT_SCLK_CTRL`, `GL2*`, `GCEA`, `GRBM`, and `RLC_GFX_RM_CNTL`.
- The beginning of the `gc_hypdec` address block, including command processor microcode/RAM address/data fields, instruction-cache base/control/operation fields for PFP, ME, CE, CPC, and MES engines, MES data/local aperture fields, and memory instruction/data bounds.

## Exported API Surface

There are no callable APIs or local types. The public interface is the macro namespace emitted by the generated register database:

- `CGTS_SA{0,1}_WGP12_CU{0,1}_SIMD{0,1}_CTRL_REG`: per-SIMD control fields for `SIMD0` or `SIMD1`, associated scheduler/queue fields such as `SQ0` or `SQ1`, and local block fields such as `SQC` or `LDS`. Each field has value bits, an override enable bit, busy-override bits, light-sleep override bits, and SIMD-busy override bits.
- `CGTS_SA{0,1}_WGP12_CU{0,1}_TATD_CTRL_REG` and `CGTS_SA{0,1}_WGP12_CU{0,1}_TCP_CTRL_REG`: per-CU texture/address/data and texture-cache controls with the same value, override, busy, light-sleep, and SIMD-busy bitfield pattern.
- `CGTT_*_CLK_CTRL` and `*_CGTT_*_CTRL`: clock-control and clock-throttling fields for graphics front-end, shader, texture, cache, command processor, RLC, memory/cache, geometry, scan converter, DB/CB, GDS, PH, UTCL1, GRBM, and related GC blocks. Common fields include `ON_DELAY`, `OFF_HYSTERESIS`, `SOFT_OVERRIDE*`, `PERF_ENABLE`, `IDLE_THRESHOLD`, `IDLE_POLL_COUNT`, and block-specific power or clock-domain selectors.
- `SQ_ALU_CLK_CTRL`, `SQ_TEX_CLK_CTRL`, and `SQ_LDS_CLK_CTRL`: compact shader queue clock-control fields that expose `SOFT_OVERRIDE` and `CLK_READY` bits.
- `RLC_GFX_RM_CNTL`: a small RLC graphics resource-management control surface with `ATCL2_DISABLE`.
- `CP_*_UCODE_ADDR`, `CP_*_UCODE_DATA`, `CP_ME_RAM_*`, and `CP_MEC_ME{1,2}_UCODE_*`: command processor firmware and RAM address/data bit definitions.
- `CP_{PFP,ME,CE,CPC,MES}_IC_BASE_*` and `CP_{PFP,ME,CE,CPC,MES}_IC_OP_CNTL`: instruction-cache base address, VMID/cache policy/execute-disable controls, cache invalidation, cache priming, and completion/primed status fields.
- `CP_MES_*BASE*`, `CP_MES_LOCAL_*`, `CP_MES_*BOUND*`, and `CP_MES_LOCAL_APERTURE`: MES instruction/data base, local aperture, mask, and bounds fields for the micro-engine scheduler address windows.
- `GFX_PIPE_PRIORITY`: the chunk includes only `HP_PIPE_SELECT__SHIFT`; the rest of that register's masks and fields continue in the next chunk.

Most complete register groups follow the generated `<REGISTER>__<FIELD>__SHIFT` plus `<REGISTER>__<FIELD>_MASK` pattern. The only unmatched groups in this slice are the intentional boundaries: `CGTS_SA1_WGP11_CU1_TCP_CTRL_REG` has only tail masks here, and `GFX_PIPE_PRIORITY` has only its first shift.

## Register Areas Covered

The CGTS section is a per-compute-unit light-sleep and override map. It repeats a regular layout for shader arrays `SA0` and `SA1`, WGP 12, CU 0 and CU 1. The `SIMD0`/`SIMD1` register groups cover the SIMD lane itself plus related subblocks such as `SQ0`, `SQ1`, `SQC`, and `LDS`. The `TATD` and `TCP` groups cover texture address/data and texture cache interface blocks. The repeated `*_OVERRIDE`, `*_BUSY_OVERRIDE`, `*_LS_OVERRIDE`, and `*_SIMDBUSY_OVERRIDE` fields are used by GFX clock-gating/light-sleep control and diagnostics to force or inhibit hardware-controlled idle decisions.

The CGTT section maps clock-control registers for most major graphics blocks. `CGTT_SPI_PS_CLK_CTRL`, `CGTT_SPIS_CLK_CTRL`, `CGTT_SPI_CLK_CTRL`, `CGTT_PC_CLK_CTRL`, `CGTT_BCI_CLK_CTRL`, `CGTT_VGT_CLK_CTRL`, `CGTT_IA_CLK_CTRL`, `CGTT_WD_CLK_CTRL`, `CGTT_GS_NGG_CLK_CTRL`, and the `CGTT_PA`/`SC`/`SQ`/`SX` groups cover front-end, rasterization, shader, and geometry domains. The `TD`, `TA`, `TCPI`, `TCI`, `TCPF`, `GDS`, `DB`, `CB`, `GL2C`, `GL2A`, `GL1C`, `GL1A`, `CHC`, `CHCG`, `CHA`, `GCR`, `UTCL1`, `GCEA`, `GRBM`, and `PH` groups extend the same pattern into texture, cache, command/data fabric, depth/color backend, address-translation, hub, graphics reset/broadcast, and physical clock domains.

The clock-control registers are mostly structured as delay and hysteresis controls plus soft overrides. Many have `PERF_ENABLE` or `CLOCK_DOMAIN_OVERRIDE` fields that interact with performance-controlled clock gating. Others expose extra idle-count, select, or busy/status bits. This makes the chunk relevant to golden-register programming, medium/fine/coarse-grain clock gating, light-sleep transitions, and GFX power-management debug.

The `gc_hypdec` section starts with command processor firmware access and instruction-cache setup. PFP, ME, CE, MEC ME1/ME2, CPC, and MES fields define microcode address/data windows, ME RAM read/write/data windows, instruction-cache base low/high address splits, base-control fields such as `VMID`, `ADDRESS_CLAMP`, `EXE_DISABLE`, and `CACHE_POLICY`, and operation controls for invalidating or priming instruction caches. The MES portion additionally defines data-code base registers, local base/mask pairs, local aperture selection, and instruction/data memory bounds.

## Control Flow And State Behavior

This file has no software control flow. Runtime behavior is introduced only when driver code includes the header and uses the macros in register read-modify-write sequences.

The field names imply several hardware state machines and state transitions:

- Compute-unit clock/light-sleep forcing: CGTS value and override fields can force subblocks such as SIMD, SQ, SQC, LDS, TA, TD, TCPF, and TCPI away from their normal hardware-derived idle or busy state.
- Graphics clock gating: CGTT delay, hysteresis, idle threshold, poll count, soft override, performance enable, and clock-domain override fields tune when clocks may be gated, held on, or overridden for specific graphics blocks.
- RLC and golden-register initialization: in-tree GC 10 code programs many CGTT registers through golden settings and toggles `RLC_CGTT_MGCG_OVERRIDE` around medium/fine-grain clock-gating enablement. These masks provide the field-level contract behind those raw register values and helpers.
- Command processor firmware bring-up: CP microcode, ME RAM, instruction-cache base, cache policy, execute-disable, invalidate, and prime fields participate in firmware loading and instruction-cache setup for PFP/ME/CE/CPC/MES engines.
- MES address-window setup: MES base, bound, aperture, and local mask fields describe how the micro-engine scheduler sees its instruction and data ranges.

No software persistence is implemented here. Hardware register contents persist according to ASIC reset and power domains. Fields named `*_COMPLETE`, `*_PRIMED`, `CLK_READY`, or similar are readback/status-oriented by name, while `*_OVERRIDE`, `*_ENABLE`, address, cache policy, timer, delay, and bounds fields are control-oriented by name. The header itself does not encode read-only, write-one-to-clear, reset-value, security, or sequencing rules.

## Dependencies And Integration Points

The syntactic dependency is the C preprocessor. The semantic dependency is the GC 10.1.0 register database that generated this file and the companion `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h` address map.

Direct in-tree include sites for this header include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nv.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_packet_manager_v9.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v10.c`

Specific integration signals visible in this tree include `gfx_v10_0.c` golden-register arrays that program `CGTT_*` controls, GFX clock-gating enable/disable paths that manipulate `RLC_CGTT_MGCG_OVERRIDE`, CGTS light-sleep setup that iterates CU TCP control registers and uses `TCPI_LS_OVERRIDE`, and GFX firmware initialization code that programs `CP_PFP_IC_BASE_*`, `CP_ME_IC_BASE_*`, `CP_CE_IC_BASE_*`, and `CP_CPC_IC_BASE_*` registers. MES versions in later GFX blocks show the same `CP_MES_IC_BASE_*` and `CP_MES_MIBOUND_*` concepts, reinforcing this chunk's role in firmware scheduler memory setup even when exact generation-specific call sites differ.

## Risks

- Generated-header drift is the main risk. A wrong shift or mask can silently set an adjacent hardware bit during a read-modify-write update.
- The CGTS register families are highly repetitive across shader array, WGP, CU, and subblock coordinates. A generation or copy error for one coordinate can produce asymmetric CU behavior that appears only on certain harvested configurations, shader arrays, or workloads.
- Override fields are powerful and easy to misuse. Setting an override value without its corresponding override enable may have no effect, while leaving an override asserted can prevent normal clock-gating, light-sleep, or firmware-managed state transitions.
- CGTT fields affect power management, clock gating, and idle detection. Incorrect delay, hysteresis, idle threshold, or soft-override masks can cause hangs, performance loss, excess power draw, or unstable suspend/resume behavior.
- CP instruction-cache and microcode address fields participate in firmware bring-up. Incorrect base, VMID, cache policy, execute-disable, invalidate, or prime bits can prevent PFP/ME/CE/CPC/MES engines from fetching firmware correctly.
- Status and control fields are represented as identical macros. Consumer code must rely on the hardware spec and access helpers for read-only, write-one-to-clear, sticky status, polling, and reset semantics.
- Chunk boundaries split two logical registers. Merge-time validation should not treat the missing `CGTS_SA1_WGP11_CU1_TCP_CTRL_REG` shifts or missing `GFX_PIPE_PRIORITY` masks as defects in this chunk alone.

## Test Signals

Useful validation is mostly build-time, generation-time, and hardware-integration oriented:

- Compile or preprocess AMDGPU and AMDKFD GC 10 paths that include `gc_10_1_0_offset.h` and `gc_10_1_0_sh_mask.h`.
- Static generation checks that every complete register group in the full header has matching `__SHIFT` and `_MASK` definitions, with expected chunk-boundary exceptions for `CGTS_SA1_WGP11_CU1_TCP_CTRL_REG` and `GFX_PIPE_PRIORITY`.
- Cross-check this header against the matching `gc_10_1_0_offset.h` so every register-family prefix has the expected `mm...` or `reg...` address definition.
- Golden-register validation for GC 10 ASICs that touches `CGTT_CPF_CLK_CTRL`, `CGTT_SPI_CLK_CTRL`, `CGTT_SQ_CLK_CTRL`, `CGTT_SQG_CLK_CTRL`, `CGTT_VGT_CLK_CTRL`, `CGTT_WD_CLK_CTRL`, `CGTT_IA_CLK_CTRL`, `GL2C_CGTT_SCLK_CTRL`, `UTCL1_CGTT_CLK_CTRL`, and related families visible in `gfx_v10_0.c`.
- Runtime GFX power-management tests: medium/fine/coarse-grain clock-gating enable/disable, CGTS light-sleep entry/exit, suspend/resume, reset recovery, workload idle transitions, and perf/power sanity checks.
- Runtime firmware tests: PFP, ME, CE, MEC/CPC, and MES firmware loading, instruction-cache invalidation/priming, queue submission, KFD compute queue bring-up, GPU reset recovery, and virtualization paths that depend on GC 10 command processor state.
- Register readback during bring-up should confirm expected CGTT golden values, override cleanup after power-management transitions, instruction-cache base/control programming, cache invalidate/prime completion bits, and MES memory aperture/bounds setup.

## Chunk Notes For Merge

This document intentionally covers only lines 37343-39656 of `gc_10_1_0_sh_mask.h`. Earlier chunks should cover the beginning of WGP 11 and the full start of the CGTS register families. Later chunks should continue `GFX_PIPE_PRIORITY` and the remaining `gc_hypdec`/GC register definitions. The final per-file report should describe the whole file as a generated ASIC register bitfield map for AMD GC 10.1.0, with this chunk contributing the compute-unit CGTS controls, graphics CGTT clock-control fields, and initial command-processor/MES instruction-cache and aperture definitions.

### subset-b-002465: lines 39657-42335

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 39657-42335

## Purpose

This chunk is generated AMD GC 10.1 register field metadata for the AMDGPU graphics core. It contains no executable C logic; it publishes preprocessor `__SHIFT` and `__MASK` constants used by register helper macros to pack, update, and decode fields in MMIO or indirect GC registers. Consumers pair these names with the matching register address definitions in `gc_10_1_0_offset.h`, and often with default values from `gc_10_1_0_default.h`, to program Navi10-era graphics, memory-management, virtualization, SDMA, power, and profiling/debug blocks.

The selected range starts at the tail of a graphics pipe-priority field, then covers GRBM shadow-register targeting, GRBM CAM remap registers, interrupt-cookie pointers, a large RLC GPU IOV/hypervisor register group, SDMA0 and SDMA1 hypervisor/context metadata, shared GCVM virtualization and ATS fields, GC CAC and SE CAC indirect performance/power accounting controls, and SPM global/SE sample-delay registers. Although the repository path is under a `ceph-client` source tree, this file is AMDGPU hardware metadata and is unrelated to Ceph filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, locks, allocations, or callbacks in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` constants identifying the starting bit of a hardware field.
- `<REGISTER>__<FIELD>_MASK` constants identifying the full bit mask for that field.
- Register comments and `addressBlock` comments grouping fields by hardware block.
- Matching register offset names are defined in `gc_10_1_0_offset.h` as `mm*`, `reg*`, or `ix*`-style symbols, depending on the access path.

Major register families in this range:

- GRBM and CAM selection/remap: `GRBM_GFX_INDEX_SR_SELECT`, `GRBM_GFX_INDEX_SR_DATA`, `GRBM_GFX_CNTL_SR_SELECT`, `GRBM_GFX_CNTL_SR_DATA`, `GRBM_CAM_INDEX`, `GRBM_HYP_CAM_INDEX`, `GRBM_CAM_DATA`, `GRBM_HYP_CAM_DATA`, and upper-address companions. These fields select shader-engine/shader-array/instance targeting, broadcast writes, pipe/ME/VMID/queue context, and CAM address-to-remap-address entries.
- Interrupt and RLC virtualization plumbing: `GC_IH_COOKIE_0_PTR`, `RLC_IH_COOKIE`, `RLC_IH_COOKIE_CNTL`, RLC timer interrupt/control/status registers, pace timer status, interrupt status/force/disable fields, and cookie credit/reset fields.
- RLC GPU IOV and hypervisor state: `RLC_GPU_IOV_VF_ENABLE`, `RLC_GPU_IOV_CFG_REG1/2/6/8`, scheduler block and scheduler data registers, VM busy status registers, active function ID, VF/PF doorbell status/set/clear/mask, SDMA0/SDMA1 preempt/save/restore status, SMU/RLC response words, virtual reset requests, semaphores, reset-vector exit bits, bootload size/address fields, F32 enable/reset fields, scratch registers, microcode address/data windows, checksum registers, IRAM/DRAM/ARAM address/data windows, and timestamp offset registers.
- SDMA hypervisor blocks: `addressBlock: gc_sdma0_sdma0hypdec` and `gc_sdma1_sdma1hypdec` define ucode address/data fields, VM context base/control, active function ID, VF enable, virtual reset requests, context-register type masks, and VM control command fields for both SDMA engines. Context type masks enumerate which ring-buffer, IB, doorbell, CSA, status, preempt, mid-command, AQL, and pointer-poll registers are included in a context save/restore class.
- Shared GCVM hypervisor/virtualization block: `addressBlock: gc_gcvmsharedhvdec` includes per-VF framebuffer size/offset registers for VF0 through VF31, IOMMU MMIO/control/performance optimization fields, MARC base/relocation/length windows, PCIe ATS control for the PF and every VF, `GCUTCL2_CGTT_CLK_CTRL`, and `GCMC_SHARED_ACTIVE_FCN_ID`.
- GC CAC indirect block: `addressBlock: gccacind` defines stall-pattern controls for PCC and power-break throttling, stall/release lookup tables, CAC ID/control, override select/value registers, many per-block 16-bit weight fields, 32-bit or 40-bit accumulator fields, per-block override select/value fields, fixed-pattern performance counters, and `HW_LUT_UPDATE_STATUS`.
- SE CAC indirect block: `addressBlock: secacind` exposes SE-local CAC ID/control/override select/value registers.
- SPM sample-delay blocks: `addressBlock: spmglbind` and `spmind` define uniform `SAMPLEDELAY` and reserved-bit masks for global blocks (`GLB_CPG`, `GLB_CPC`, `GLB_CPF`, `GLB_GDS`, `GLB_GCR`, `GLB_PH`, `GLB_GE`, `GLB_GUS`, `GLB_CHA`, `GLB_CHCG`, `GLB_ATCL2`, `GLB_VML2`, SDMA, GL2A/GL2C, EA, CHC) and shader-engine/SA/WGP-local blocks (`SE_SPI`, `SE_SQG`, `SE_CBR`, `SE_DBR`, `SE_SA0*`, and early `SE_SA0WGP*` sample-delay registers).

The macro names encode access semantics only indirectly. Suffixes such as `STATUS`, `STAT`, `BUSY_STATUS`, `RESET_REQ`, `INT_CLEAR`, `FORCE`, `SET`, `CLR`, `RESP`, `UCODE_ADDR`, `UCODE_DATA`, `SCRATCH`, `ACC`, and `OVRD` strongly indicate status, command, reset, interrupt, firmware-loading, debug, accumulator, or override behavior, but this header does not itself declare read/write, sticky, write-one-to-clear, self-clearing, or polling requirements.

## Control Flow

This header has no runtime control flow. Runtime behavior comes from AMDGPU consumers that include the GC 10.1 register headers and use helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_GOLDEN_VALUE`, indirect register accessors, and ASIC-specific register tables.

Typical consumer flow for fields in this range is:

1. Select the correct register address from `gc_10_1_0_offset.h`.
2. Read the register or start from a known initialization value.
3. Use the matching `__MASK` and `__SHIFT` constants to clear and insert a field, or to extract a field from a readback value.
4. Write the value through the correct access path: direct SOC15 GC MMIO, GRBM-indexed instance targeting, RLC/SDMA hypervisor windows, GCVM shared registers, GC CAC/SE CAC indirect registers, or SPM indirect sample-delay registers.
5. For command/status families, poll or wait on the corresponding status bits using timeouts defined in the calling driver code.

Important sequencing lives outside this file. Examples include selecting GRBM SE/SA/instance targets before per-instance register writes, masking or clearing IOV interrupt sources, issuing RLC GPU IOV commands and reading `CMD_STATUS`/response fields, enabling VF or PF virtualization state only after context storage is initialized, loading RLC/SDMA microcode through address/data windows, programming SDMA context-save masks before preemption or reset paths, enabling PCIe ATS only when IOMMU/ATC state is coherent, and updating CAC stall/power-break LUTs only when the hardware allows the LUT update to settle.

## State And Persistence Behavior

The file stores no software state and persists nothing to disk. It describes hardware-visible state in GC registers.

The represented hardware state includes GRBM broadcast/instance selection, CAM remap table entries, interrupt-cookie bookkeeping, RLC timers and interrupt bits, virtual-function enablement and IDs, scheduler command/status state, VM busy masks, doorbell status, semaphore ownership, reset exit reason bits, bootload and microcode window addresses, scratch and IRAM/DRAM/ARAM data, SDMA context-save classification, per-VF framebuffer aperture metadata, MARC relocation windows, IOMMU and ATS enablement, clock-gating overrides, CAC weights/accumulators/overrides, stall and power-break pattern tables, fixed-pattern performance counters, and SPM sample-delay values.

Persistence is hardware-defined rather than expressed in the macros. Some fields are configuration state that may remain until reset, power-gate, function-level reset, suspend/resume, or a later driver write. Others are live status, sticky interrupt status, write-one-to-clear bits, self-clearing command bits, command response words, or counters/accumulators that can change autonomously while the GPU is running. The many `RESERVED` masks are part of the hardware ABI: register updates should preserve them unless an ASIC programming guide or golden-register table explicitly requires a value.

## Dependencies And Integration Points

This chunk depends on consistency with the rest of the AMD register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h` supplies the matching register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_default.h` supplies reset/default values for many of the same register names.
- AMDGPU GC v10 code includes these generated headers for Navi10-class graphics hardware and uses SOC15 register helpers to apply golden settings, load firmware, set up rings and VM state, control RLC, and program SPM-related sample delays.
- RLC GPU IOV and SDMA virtualization fields integrate with SR-IOV, VF/PF scheduling, function-level reset handling, doorbells, VM busy tracking, context save/restore, and firmware or hypervisor cooperation.
- GCVM and ATS fields integrate with GPU virtual memory, IOMMU/ATC programming, PCIe address translation services, per-VF framebuffer apertures, and memory aperture relocation.
- CAC and power-throttling fields integrate with power-management firmware and driver power-tuning paths. Existing AMDGPU powerplay code accesses GC CAC indirect registers through `CGS_IND_REG_GC_CAC`, and SMU firmware interfaces expose GC CAC-related feature IDs on newer parts.
- SPM sample-delay fields integrate with profiling and hardware performance-monitor setup. GC v10 code programs SPM global and per-SE sample-delay indirect addresses/data using golden-value tables for this ASIC family.

## Risks And Edge Cases

- Header version mismatch is the largest risk. Combining `gc_10_1_0_sh_mask.h` with offset/default headers from another GC generation can compile while causing writes to the wrong register or field.
- The constants are untyped preprocessor macros. Field width mistakes, off-by-one shifts, stale generated data, or typoed register names can silently corrupt unrelated bits in low-level hardware registers.
- GRBM targeting fields are high blast-radius. Incorrect SE/SA/instance indices or broadcast-write bits can program only one hardware instance, all instances, or the wrong queue/VMID context.
- Virtualization and reset fields are sequencing-sensitive. VF enable, VF/PF doorbell state, scheduler command execution, VM busy masks, FLR requests, SDMA save/restore status, and active function ID must be coordinated with PF/VF ownership and hardware quiescence.
- Address/data microcode and scratch windows are stateful. Incorrect address increments, missing reset, wrong firmware version, or overlapping RLC/SDMA access can load invalid firmware or corrupt diagnostic/scratch state.
- SDMA context-register type masks must match the actual context save/restore contract. Missing a ring, IB, doorbell, CSA, preempt, mid-command, AQL, or pointer-poll field can break preemption, suspend/resume, SR-IOV scheduling, or engine reset recovery.
- GCVM/IOMMU/ATS settings affect memory isolation and address translation. Bad per-VF framebuffer apertures, MARC relocation, ATS enablement, or active-function selection can produce page faults, data isolation failures, hangs, or DMA to the wrong physical address.
- CAC and power-break tables can affect throttling behavior. Bad weights, thresholds, stall patterns, or LUT update sequencing can under-throttle, over-throttle, destabilize clocks/power, or distort telemetry used by power management.
- Accumulator and performance-counter fields may have clear/latch/wrap behavior not visible in this header. Driver diagnostics must understand whether reads are destructive, sticky, or racing hardware increments.
- Sample-delay fields are replicated across many blocks. A wrong indirect address or delay value can produce broken SPM traces only for one block, shader array, WGP, SDMA engine, GL2C slice, or EA path.
- The chunk boundary is artificial. It begins after the `GFX_PIPE_PRIORITY__HP_PIPE_SELECT__SHIFT` definition and ends in the early `SE_SA0WGP02TA1_SAMPLEDELAY` register; neighboring chunks are required for complete per-file analysis.

## Test Signals

Useful validation is mostly build, static, and hardware integration coverage:

- Build coverage for AMDGPU GC v10 code that includes `gc_10_1_0_offset.h`, `gc_10_1_0_sh_mask.h`, and `gc_10_1_0_default.h`.
- Generated-header consistency checks that every field mask matches its shift and width, fields within each register do not unintentionally overlap, and every register in this slice has a matching offset/default entry where expected.
- Golden-register and boot tests on GC 10.1 hardware, especially paths that program RLC clocks, SPM sample delays, GCVM/ATS, GRBM instance targeting, and SDMA/RLC firmware windows.
- SR-IOV and virtualization tests covering VF enable/disable, PF/VF doorbell status set/clear/mask, scheduler commands and responses, active function ID, FLR handling, VM busy tracking, and SDMA context save/restore.
- Reset and recovery tests covering cold boot, warm reset, VDDGFX exit, VF FLR exit, RLC/SDMA preempt/save/restore bits, microcode checksum/readback, and interrupt-cookie behavior.
- GPUVM/IOMMU tests covering per-VF framebuffer apertures, MARC base/relocation/length windows, ATS enablement, VM faults, and memory isolation.
- Power and telemetry tests covering GC CAC thresholds, weights, overrides, accumulators, stall/power-break LUT programming, fixed-pattern counters, and LUT update status.
- Profiling tests covering SPM global and SE sample-delay programming and trace sanity for CPG/CPC/CPF, GDS/GCR, PH/GE/GUS, SDMA0/1, GL2A/GL2C, EA, CHC, SPI/SQG/CBR/DBR, SA-local blocks, and WGP-local TA/TD/TCP sample delays.
- Regression indicators include GPU hangs, failed ring tests, VM faults, SR-IOV isolation failures, FLR timeouts, SDMA preemption failures, missing interrupts, bad microcode checksum, unstable power throttling, malformed SPM traces, or failures isolated to one VF, engine, shader array, or hardware block.

### subset-b-002466: lines 42336-44165

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 42336-44165

## Scope

This chunk is the tail of the generated AMD GC 10.1.0 shift/mask register header. It contains only C preprocessor constants: each field has a `__SHIFT` value and a matching `__MASK` value used to pack or extract bitfields from GC 10.1/Navi10 graphics registers. There are no functions, structs, enums, variables, includes, locks, allocations, callbacks, or executable branches in this range.

The selected lines start inside the sample-delay register family, continue through the complete visible `sqind` wave-debug block, then cover the complete visible `didtind` dynamic throttling block for SQ, DB, TD, and TCP clients. The chunk ends at the file's closing `#endif`. Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata and is not Ceph filesystem code.

## Purpose

`gc_10_1_0_sh_mask.h` is generated hardware metadata for AMD's GC 10.1.0 graphics IP. Driver code includes it with `gc_10_1_0_offset.h` and, where needed, `gc_10_1_0_default.h` so register helpers can address a register and update only the intended field bits.

This chunk serves three main purposes:

- It defines sample-delay bit layouts for shader-engine and shader-array units, especially the tail of `SE_SA0...` entries and the `SE_SA1...` entries for SX, PA, GL1, CB, DB, SC, RMI, GL1C, and WGP-local TA/TD/TCP blocks. These registers expose a 6-bit `SAMPLEDELAY` field plus reserved upper bits.
- It defines indexed SQ wave debug/status layouts in the `sqind` address block. These describe a selected shader wave's mode, status, trap status, hardware identity, GPR/LDS allocation, instruction-buffer state, program counter, instruction word, scheduler mode, VGPR offset, trap temporaries, execution mask, scratch/XNACK state, and SQ interrupt payload words.
- It defines indexed DIDT/EDC layouts in the `didtind` address block for the shader queue/sequencer (`SQ`), depth buffer/backend (`DB`), texture data (`TD`), and texture cache processor (`TCP`) clients. These fields control dynamic inductive droop mitigation, energy/current-delta throttling, stall insertion, release timing, stall patterns, thresholds, weights, status, overflow, rolling power delta, PCC performance counters, and per-client stall event counters.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The important interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- The matching register addresses live in `gc_10_1_0_offset.h`, usually as `ix...` indexed-register constants for this chunk.
- Consumers normally combine these constants through AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, wave indirect read helpers, and DIDT indirect register helpers.

The sample-delay family is repetitive and intentionally uniform. Each covered `*_SAMPLEDELAY` register defines `SAMPLEDELAY` at bits `[5:0]` and `RESERVED` at bits `[31:6]`. The names encode physical graphics topology: shader engine (`SE`), shader array (`SA0`/`SA1`), WGP instance, and sub-block (`TA`, `TD`, `TCP`, plus shared blocks like `SX`, `PA`, `CB`, `DB`, `SC`, `RMI`, and `GL1*`).

The SQ wave block includes these notable register groups:

- `SQ_DEBUG_STS_GLOBAL` and `SQ_DEBUG_STS_LOCAL`: global and local wave-debug status, including busy/valid/stall/debug indicators and per-resource status.
- `SQ_WAVE_MODE`, `SQ_WAVE_STATUS`, and `SQ_WAVE_TRAPSTS`: floating-point mode bits, exception enables, halt/trap/export/GPR state, privilege/debug state, and trap/event status.
- `SQ_WAVE_HW_ID_LEGACY`, `SQ_WAVE_HW_ID1`, and `SQ_WAVE_HW_ID2`: location and identity fields such as wave, SIMD, WGP/CU, shader array, shader engine, queue, vmid, state id, and wave age/id details.
- `SQ_WAVE_GPR_ALLOC` and `SQ_WAVE_LDS_ALLOC`: per-wave VGPR/SGPR/LDS allocation metadata.
- `SQ_WAVE_IB_STS`, `SQ_WAVE_IB_DBG1`, `SQ_WAVE_IB_STS2`, `SQ_WAVE_INST_DW0`, and `SQ_WAVE_FLUSH_IB`: instruction-buffer status, debug, instruction word, and flush controls.
- `SQ_WAVE_PC_LO`, `SQ_WAVE_PC_HI`, `SQ_WAVE_M0`, `SQ_WAVE_EXEC_LO`, `SQ_WAVE_EXEC_HI`, `SQ_WAVE_FLAT_SCRATCH_LO`, `SQ_WAVE_FLAT_SCRATCH_HI`, `SQ_WAVE_FLAT_XNACK_MASK`, and `SQ_WAVE_TTMP0` through `SQ_WAVE_TTMP15`: full-width `DATA` views of selected wave scalar/debug state.
- `SQ_INTERRUPT_WORD_AUTO`, `SQ_INTERRUPT_WORD_ERROR`, and `SQ_INTERRUPT_WORD_WAVE`: interrupt payload fields for thread-trace, WLT, buffer status, error type/detail, wave id, SIMD/WGP/SA/SE location, VMID, privilege, and encoding.

The DIDT block is organized as repeated register families for `DIDT_SQ_*`, `DIDT_DB_*`, `DIDT_TD_*`, and `DIDT_TCP_*`:

- `*_CTRL0`, `*_CTRL1`, `*_CTRL2`, `*_CTRL_OCP`, and `*_CTRL3`: enable/reset/force controls, threshold fields, max/min power fields, short/long intervals, OCP max power, throttle trigger bits, power-level selection, stall-pattern selection, and local/combined enable controls.
- `*_STALL_CTRL`, `*_TUNING_CTRL`, `*_STALL_AUTO_RELEASE_CTRL`, `*_STALL_RELEASE_CNTL0`, `*_STALL_RELEASE_CNTL1`, and `*_STALL_RELEASE_CNTL_STATUS`: stall insertion policy, high/low delay fields, tuning levels, auto-release timers, release allowance limits, and release-control FSM state.
- `*_STALL_PATTERN_1_2`, `*_STALL_PATTERN_3_4`, `*_STALL_PATTERN_5_6`, and `*_STALL_PATTERN_7`: packed stall-pattern bit sequences used by DIDT throttling.
- `*_MPD_SCALE_FACTOR` and `*_WEIGHT0_3`, `*_WEIGHT4_7`, `*_WEIGHT8_11`: power-delta scaling and per-level weighting fields.
- `*_EDC_CTRL`, `*_EDC_THRESHOLD`, `*_EDC_STALL_PATTERN_*`, `*_EDC_TIMER_PERIOD`, `*_THROTTLE_CTRL`, `*_EDC_STALL_DELAY_*`, `*_EDC_STATUS`, `*_EDC_OVERFLOW`, `*_EDC_ROLLING_POWER_DELTA`, and `*_EDC_PCC_PERF_COUNTER`: EDC enable/reset/stall policy, thresholds, timer periods, throttle source enables, per-subunit delay tables, FSM/throttle level status, overflow counters, rolling power delta, and PCC performance counts.
- `DIDT_SQ_STALL_EVENT_COUNTER`, `DIDT_DB_STALL_EVENT_COUNTER`, `DIDT_TD_STALL_EVENT_COUNTER`, and `DIDT_TCP_STALL_EVENT_COUNTER`: full-width stall event counters for each DIDT client.

The DIDT families are mostly symmetrical, but not byte-for-byte identical. For example, DB exposes only `DIDT_DB_EDC_STALL_DELAY_1` in this visible range, while SQ, TD, and TCP expose delay registers 1 through 3.

## Control Flow

This header has no runtime control flow. Its behavior is compile-time substitution of numeric constants.

The implied runtime flow is in AMDGPU consumers:

1. Include the GC 10.1.0 offset and shift/mask headers for the active ASIC generation.
2. Select a register address, often an indexed `ix...` register for `sqind` or `didtind` blocks.
3. Read the current register value through the relevant SOC15, wave-indirect, or DIDT-indirect access path.
4. Use `__MASK` and `__SHIFT` constants, usually through a helper macro, to extract status fields or compose a read-modify-write update.
5. Sequence any enable/reset/stall/calibration/debug operation in higher-level GFX, KFD, debug, or power-management code.

For SQ wave state, consumers select a wave context and read the indexed registers for diagnostics, debug dumps, trap handling, or fault reporting. For DIDT/EDC state, power-management or initialization code programs thresholds, patterns, delays, and enables, then may poll status/counters. This header does not define selection order, polling timeouts, reset ordering, interrupt behavior, or read/write side effects.

## State And Persistence Behavior

The macros themselves are stateless and do not persist anything. They describe fields in GPU hardware registers.

Sample-delay registers are hardware configuration state for sampled signals across graphics pipeline sub-blocks. Their values are likely retained until graphics IP reset, ASIC reset, suspend/resume reinitialization, power-gating loss, firmware reprogramming, or explicit driver writes. The reserved bits must be preserved unless the hardware guide says otherwise.

SQ wave registers are volatile views of selected shader-wave state. Values can change as waves execute, stall, trap, flush, terminate, or are inspected by debug hardware. Many fields represent live status or debug windows rather than durable software-owned configuration.

DIDT and EDC registers hold hardware throttling policy and counters. Configuration fields may persist until reset or reprogramming; status, overflow, rolling-power, performance-counter, and stall-event fields are hardware-updated and may be sticky, clear-on-write, clear-on-read, saturating, or freely running depending on the register. The shift/mask header does not encode those access semantics, so consumers must rely on the register specification and established driver sequences.

## Dependencies And Integration Points

This chunk depends on the generated GC 10.1.0 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h` supplies matching register addresses such as `ixSQ_WAVE_MODE`, `ixSQ_INTERRUPT_WORD_ERROR`, `ixDIDT_SQ_CTRL0`, `ixDIDT_DB_CTRL0`, `ixDIDT_TD_CTRL0`, and `ixDIDT_TCP_CTRL0`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_default.h` supplies default/reset values for the same late `sqind` and `didtind` register families.
- AMDGPU GC 10.1 code, KFD queue/MQD code, GFXHUB v2.0 code, and Navi-family initialization code include this header as part of the ASIC register description.
- Register helper macros and indirect register accessors provide the actual MMIO/indexed-register read/write mechanism.

Integration points include shader wave dumps, trap/fault diagnostics, KFD/compute queue debugging, SQ interrupt decoding, graphics power management, droop-aware throttling, current/energy-delta throttling, performance counter collection, GPU reset restore paths, and suspend/resume or power-gating reinitialization. Older power-management code in the tree demonstrates the same DIDT/EDC pattern by reading `DIDT_TCP_EDC_CTRL`, updating fields such as `EDC_EN` and `EDC_SW_RST`, and writing the indexed register back.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong mask or shift compiles cleanly but can update the wrong hardware field, producing subtle shader-debug, interrupt-decoding, throttling, or performance behavior.
- This range begins mid-sample-delay family. Earlier `SE_SA0...` sample-delay entries are in the previous chunk, so final file-level research should merge adjacent chunks before claiming complete topology coverage.
- The `sqind` and `didtind` registers are indexed windows. Using the right field constants with the wrong selected wave, instance, client, or indirect address can return plausible but incorrect data.
- SQ wave fields are often live hardware state. Reading during wave scheduling, trap handling, reset, or GPU hang recovery can race with hardware changes and produce transient values.
- DIDT/EDC control fields are performance and reliability sensitive. Incorrect enable/reset/force-stall/throttle policy writes can cause unnecessary throttling, unstable power behavior, misleading counters, or workload-specific performance regressions.
- Repeated DIDT prefixes invite copy/paste mistakes. SQ, DB, TD, and TCP fields are similar but represent different hardware clients, and DB has fewer EDC stall-delay registers in this chunk.
- Reserved and unused fields appear throughout. Full-register writes that do not preserve reserved bits may alter undocumented hardware behavior.
- The header does not communicate access type. Some fields that look writable by name may be read-only status, self-clearing pulses, write-one-to-clear bits, hardware-owned counters, or sticky overflow indicators.
- Some interrupt and identity fields span high bits or encode several IDs in one register. Consumers must use the matching mask width and avoid signed or truncated intermediate values.

## Test Signals

Useful validation is mostly build, generated-data consistency, and hardware integration:

- Kernel build coverage for AMDGPU/KFD files that include `gc_10_1_0_sh_mask.h`, especially GC 10.1, GFXHUB v2.0, queue/MQD, and debug paths.
- Static comparison against AMD's authoritative generated GC 10.1.0 register database to confirm each `__SHIFT` and `__MASK` value and each register family's presence.
- Cross-checks that every register field in this chunk has a matching address macro in `gc_10_1_0_offset.h` and, where available, a default value in `gc_10_1_0_default.h`.
- Mechanical checks for mask/shift consistency: masks should align to shifts, repeated sample-delay registers should preserve the 6-bit `SAMPLEDELAY` layout, and repeated DIDT client families should match except for documented hardware omissions.
- Shader debug, trap, thread-trace, wave-dump, and GPU fault tests that exercise `SQ_WAVE_*` and `SQ_INTERRUPT_WORD_*` decoding.
- Power-management stress tests on GC 10.1/Navi10 hardware that exercise graphics load transitions, over-current or power-brake behavior, EDC/PCC controls, suspend/resume, GPU reset, and DIDT counter readback.
- Performance regression tests for shader, depth/backend, texture-data, and texture-cache-heavy workloads, since DIDT mistakes can present as unexpected throttling rather than functional failure.
- Runtime warning signals include bad wave IDs or PC values in debug dumps, incorrect SQ interrupt error decoding, GPU hang recovery regressions, persistent EDC overflow, unexpected stall event counts, thermal/power throttling anomalies, or workload-specific performance drops after DIDT programming changes.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002466`. It covers lines 42336-44165 and ends the source file. The final per-file research should merge this with earlier chunks for the complete `gc_10_1_0_sh_mask.h` register map, especially the preceding sample-delay entries and any earlier GC register families outside this tail segment.
