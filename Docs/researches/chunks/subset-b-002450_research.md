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
