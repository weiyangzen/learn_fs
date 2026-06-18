# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 2574-5127

## Scope

This chunk is a generated AMDGPU GC 11.0.0 register field-mask header segment. It contains preprocessor constants only: each field is represented by a `__SHIFT` value and/or an unshifted `MASK` value used by AMDGPU register helpers. The matching register offsets live in `gc_11_0_0_offset.h`, default reset values live in `gc_11_0_0_default.h`, and runtime code includes this header through GC 11 graphics, SDMA, MES, display, and KFD paths.

The range starts in the middle of `SDMA1_CNTL` field definitions, covers most of the public SDMA1 control/status and queue register layouts, repeats the SDMA1 RLC queue template for queues 0 through 7, then ends at the beginning of the SDMA hypdec microcode-control address blocks (`gc_sdma0_sdma0hypdec` and `gc_sdma0_sdma1hypdec`). Because the range begins mid-register, `SDMA1_CNTL__TRAP_ENABLE_MASK` is present in this chunk while the corresponding `TRAP_ENABLE__SHIFT` is immediately before the chunk boundary.

## Purpose

The purpose of this header slice is to give the GC 11 AMDGPU driver exact bit positions for SDMA1 engine control, status, virtual-memory translation, interrupt/error reporting, doorbell, ring-buffer, indirect-buffer, AQL, preemption, and microcode-control registers. These definitions keep low-level MMIO programming readable and let code use helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15_IP`, and `WREG32_SOC15_IP` instead of open-coded bit constants.

Although this chunk names `SDMA1_*` registers, much of the SDMA v6 runtime code programs both SDMA engines through instance arithmetic. `sdma_v6_0.c` uses `sdma_v6_0_get_reg_offset()` to start from `regSDMA0_*` offsets and add `SDMA1_REG_OFFSET` for instance 1, while KFD queue-loading code explicitly computes SDMA1 queue bases with `SOC15_REG_OFFSET(SDMA1, 0, regSDMA1_QUEUE0_RB_CNTL)`. The SDMA0 and SDMA1 field layouts must therefore remain equivalent where shared instance code uses the SDMA0 macro names for both engines.

## Register Families Covered

The `SDMA1_CNTL`, `SDMA1_CNTL1`, `SDMA1_CHICKEN_BITS`, and `SDMA1_CHICKEN_BITS_2` definitions describe engine-wide enable, interrupt, swap, mid-command preemption, world-switch, page-fault, clock-gating override, burst/combine, copy-overlap, raw-check, and polling behavior. Runtime users enable traps and preemption interrupt behavior through `REG_SET_FIELD(..., SDMA0_CNTL, TRAP_ENABLE, ...)` and use equivalent register layouts when targeting SDMA1 by offset.

The address/topology and fetch group includes `SDMA1_GB_ADDR_CONFIG`, `SDMA1_GB_ADDR_CONFIG_READ`, `SDMA1_RB_RPTR_FETCH`, `SDMA1_RB_RPTR_FETCH_HI`, `SDMA1_IB_OFFSET_FETCH`, `SDMA1_PROGRAM`, `SDMA1_PHYSICAL_ADDR_LO`, `SDMA1_PHYSICAL_ADDR_HI`, `SDMA1_GLOBAL_QUANTUM`, `SDMA1_TILING_CONFIG`, `SDMA1_TLBI_GCR_CNTL`, and `SDMA1_TIMESTAMP_CNTL`. These fields expose ring/IB fetch offsets, memory physical-address plumbing, global scheduling quantum, tiling configuration, and TLB/GCR invalidation controls.

The status and diagnostics group includes `SDMA1_STATUS_REG`, `SDMA1_STATUS1_REG`, `SDMA1_STATUS2_REG`, `SDMA1_STATUS3_REG`, `SDMA1_STATUS4_REG`, `SDMA1_STATUS5_REG`, `SDMA1_STATUS6_REG`, `SDMA1_QUEUE_STATUS0`, `SDMA1_INT_STATUS`, `SDMA1_CLOCK_GATING_STATUS`, `SDMA1_AQL_STATUS`, `SDMA1_FED_STATUS`, and `SDMA1_ERROR_LOG`. These masks decode idle bits, ring/IB command fullness, context-empty state, copy-engine stalls, UTCL1 FIFO state, interrupt latches, queue reset state, command/fetch/decode status, and error address/type information. `sdma_v6_0.c` exposes many of these registers in `sdma_reg_list_6_0[]` for debug/register dump paths and polls `SDMA*_STATUS_REG__IDLE_MASK` during idle waits.

The RAS, EDC, and microcode group includes `SDMA1_UCODE_CHECKSUM`, `SDMA1_UCODE1_CHECKSUM`, `SDMA1_EDC_CONFIG`, `SDMA1_EDC_COUNTER`, `SDMA1_EDC_COUNTER_CLEAR`, `SDMA1_EA_DBIT_ADDR_DATA`, `SDMA1_EA_DBIT_ADDR_INDEX`, `SDMA1_SCRATCH_RAM_DATA`, `SDMA1_SCRATCH_RAM_ADDR`, `SDMA1_PUB_DUMMY_REG0..3`, and `SDMA1_F32_COUNTER`. These fields are used for firmware checksum visibility, single/double error counters, counter clearing, error-address indexing, scratch RAM access, and public dummy/debug state.

The freeze, scheduling, and watchdog group includes `SDMA1_FREEZE`, `SDMA1_PROCESS_QUANTUM0`, `SDMA1_PROCESS_QUANTUM1`, `SDMA1_WATCHDOG_CNTL`, `SDMA1_QUEUE_RESET_REQ`, `SDMA1_CE_CTRL`, and `SDMA1_CRD_CNTL`. Runtime code freezes/preempts engines around reset paths, halts/unhalts the F32 microcontroller, sets queue hang watchdogs, and configures per-process quantum. Incorrect masks here directly affect reset recovery and queue scheduling fairness.

The UTCL1 and memory-translation group includes `SDMA1_UTCL1_CNTL`, `SDMA1_UTCL1_WATERMK`, `SDMA1_UTCL1_TIMEOUT`, `SDMA1_UTCL1_PAGE`, `SDMA1_UTCL1_RD_STATUS`, `SDMA1_UTCL1_WR_STATUS`, `SDMA1_UTCL1_INV0..2`, `SDMA1_UTCL1_RD_XNACK0..1`, and `SDMA1_UTCL1_WR_XNACK0..1`. `sdma_v6_0_gfx_resume_instance()` programs UTCL1 response mode, redo delay, default read/write L2 cache policy, and `LLC_NOALLOC`. The status and XNACK fields expose FIFO empty/full state, L2 interface idleness, invalidation busy state, retry attributes, VMID/client ID, address, sideband data, and page-fault retry behavior.

The queue template is repeated for `SDMA1_QUEUE0` through `SDMA1_QUEUE7`. Each queue has ring-buffer control and base/pointer registers (`RB_CNTL`, `RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, `RB_WPTR_HI`, `RB_RPTR_ADDR_LO/HI`, `RB_WPTR_POLL_ADDR_LO/HI`), indirect-buffer controls (`IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO/HI`, `IB_SIZE`, `IB_SUB_REMAIN`), context and scheduling state (`CONTEXT_STATUS`, `SCHEDULE_CNTL`, `SKIP_CNTL`), doorbell controls (`DOORBELL`, `DOORBELL_LOG`, `DOORBELL_OFFSET`), context-save address fields (`CSA_ADDR_LO/HI`), preemption (`PREEMPT`, `RB_PREEMPT`), AQL controls (`RB_AQL_CNTL`), minor pointer updates, dummy registers, and `MIDCMD_DATA0..10` plus `MIDCMD_CNTL` for mid-command preemption state.

The final hypdec section maps SDMA microcode address/data registers: `SDMA0_UCODE_ADDR`, `SDMA0_UCODE_DATA`, `SDMA0_BROADCAST_UCODE_ADDR`, `SDMA0_BROADCAST_UCODE_DATA`, `SDMA0_F32_CNTL`, and the first `SDMA1_UCODE_ADDR` fields. `sdma_v6_0_get_reg_offset()` treats the hypdec range specially with `SDMA0_HYP_DEC_REG_START`, `SDMA0_HYP_DEC_REG_END`, and `SDMA1_HYP_DEC_REG_OFFSET`, so these offsets and masks are part of the firmware/microcontroller control path rather than the ordinary public SDMA register spacing.

## Important APIs, Types, and Macros

This file defines no C functions, structs, or runtime variables. Its public API is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit shift for a field within a 32-bit MMIO register value.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted field mask.
- Register comments such as `//SDMA1_QUEUE0_RB_CNTL` and address-block comments such as `// addressBlock: gc_sdma0_sdma0hypdec` preserve generated hardware grouping.

Important consumers include `sdma_v6_0.c`, which initializes rings, doorbells, read/write pointer writeback, UTCL1 policy, watchdogs, F32 halt/reset, and SDMA idle/preemption behavior; `amdgpu_amdkfd_gfx_v11.c`, which computes SDMA RLC queue register bases for engine 0 and engine 1 and loads/restores KFD SDMA queues; and `kfd_mqd_manager_v11.c`, which builds `struct v11_sdma_mqd` values using queue-field shifts for `RB_CNTL`, `DOORBELL_OFFSET`, and `SCHEDULE_CNTL`.

The helper contract is compile-time concatenation. For example, `REG_SET_FIELD(rb_cntl, SDMA0_QUEUE0_RB_CNTL, RB_SIZE, rb_bufsz)` depends on `SDMA0_QUEUE0_RB_CNTL__RB_SIZE_MASK` and `SDMA0_QUEUE0_RB_CNTL__RB_SIZE__SHIFT`. Equivalent `SDMA1_QUEUE*_...` definitions are required when code names SDMA1 directly or when generated tables and register dump tooling decode engine 1.

## Control Flow

There is no executable control flow in this header. The control flow appears in the consumers that program the registers described here.

During SDMA resume, `sdma_v6_0_gfx_resume_instance()` programs queue 0 for each SDMA instance: ring size and privilege in `RB_CNTL`, read/write pointer registers, write-pointer polling addresses, read-pointer writeback addresses, ring base, minor pointer update, doorbell enable/offset, watchdog count, UTCL1 response/cache policy, F32 halt/reset, `RB_ENABLE`, and `IB_ENABLE`. For instance 1, the same flow reaches SDMA1 by adding the SDMA1 public-register offset.

During KFD SDMA queue creation, `kfd_mqd_manager_v11.c::update_mqd_sdma()` encodes queue size, VMID, read-pointer writeback, write-pointer polling, doorbell offset, and scheduling quantum into a `v11_sdma_mqd`. `amdgpu_amdkfd_gfx_v11.c` then computes the SDMA RLC queue register block, disables `RB_ENABLE`, waits for `CONTEXT_STATUS__IDLE`, writes doorbell and pointer/base registers, toggles `MINOR_PTR_UPDATE`, and finally re-enables `RB_ENABLE`.

During reset and diagnostics, SDMA code freezes engines with `SDMA*_FREEZE__FREEZE_MASK`, halts/resets F32 with `SDMA*_F32_CNTL` bits, checks idle through `SDMA*_STATUS_REG__IDLE_MASK`, triggers queue preemption via queue `PREEMPT` registers, and exposes status/UTCL1/XNACK/queue registers through register dump lists.

## State and Persistence

The macros themselves are compile-time constants and hold no state. The hardware registers they describe are volatile MMIO state that is reset, reprogrammed on driver init/resume, or restored through MQD state for KFD queues.

Some SDMA state is deliberately persistent across normal queue operation. Ring base addresses, read/write pointers, read-pointer writeback addresses, write-pointer polling addresses, doorbell offsets, VMID fields, queue scheduling quantum, AQL mode, and context-save addresses remain live until the queue is disabled, reset, or replaced. KFD SDMA queues persist part of this state in `struct v11_sdma_mqd` so queues can be loaded, saved, restored, and debugged.

Other fields are transient latches or status surfaces. Idle/full/stall bits, interrupt status, XNACK/fault attributes, EDC counters, error logs, frozen/preempted status, context status, doorbell captured/log bits, and mid-command data reflect hardware progress or faults and can change as DMA packets execute. Reset and suspend/resume paths must clear or reinitialize the right subset without losing required queue pointer state.

## Dependencies and Integration Points

This chunk depends on the GC 11 generated register ecosystem:

- `gc_11_0_0_offset.h` provides `regSDMA1_*`, `mmSDMA1_*`, and queue register addresses matching these field layouts.
- `gc_11_0_0_default.h` provides reset/default values for many registers in this chunk, including SDMA1 controls, status registers, queue controls, AQL controls, and mid-command data registers.
- AMDGPU SOC15 helpers perform MMIO reads/writes using the generated offsets and these masks.
- KFD `v11_sdma_mqd` layout mirrors many queue registers here, so MQD save/restore must stay aligned with the queue register template.
- NBIO doorbell range setup must match `SDMA*_QUEUE*_DOORBELL` and `DOORBELL_OFFSET` programming.
- VM/cache behavior depends on UTCL1 page, invalidation, timeout, and XNACK field definitions.
- RAS/debugfs/register-dump paths depend on status, EDC, error log, and XNACK masks for meaningful diagnostics.

Important cross-file integration is visible in `sdma_v6_0.c`: `sdma_v6_0_get_reg_offset()` maps public SDMA instance 1 by adding `0x600`, but maps hypdec registers through a separate `0x20` per-instance adjustment. That makes the transition at the end of this chunk especially sensitive; public SDMA queue fields and hypdec microcode fields are adjacent in the source header but use different address mapping logic.

## Risks

The main risk is silent hardware misprogramming. These constants compile into bit operations; a wrong mask or shift can still compile cleanly while enabling the wrong queue bit, writing a truncated address, polling the wrong status, or decoding the wrong fault.

High-risk fields include queue `RB_CNTL` fields such as `RB_ENABLE`, `RB_SIZE`, `RB_VMID`, writeback enable/timer, pointer polling, swap, and privilege, because they directly control DMA queue execution. Doorbell enable and offset fields are also high risk: an incorrect offset can cause missed queue submissions or writes to the wrong doorbell aperture.

Pointer and address masks are sensitive because most low address fields are alignment-shifted. `RB_BASE`, `IB_BASE_LO`, `CSA_ADDR_LO`, `RB_RPTR_ADDR_LO`, `RB_WPTR_POLL_ADDR_LO`, `PHYSICAL_ADDR_LO`, and XNACK/fault address fields must preserve the documented low-bit alignment semantics. Wrong shifts can corrupt GPU addresses even if the upper 32-bit registers are correct.

UTCL1 fields are high risk for memory correctness. Bad `RESP_MODE`, cache policy, page size, physical-address, invalidation, timeout, or XNACK decoding fields can produce stale reads/writes, incorrect retry behavior, VM fault storms, or misleading fault attribution.

Freeze, preemption, mid-command, and F32 control fields affect reset and recovery. Errors here can leave queues stuck non-idle, fail to save/restore mid-command state, prevent preemption interrupts, or wedge the SDMA firmware thread during suspend/resume or GPU reset.

Because this is generated hardware-description source, manual edits are risky. Seemingly unused queue templates for queues 1 through 7, reserved fields, dummy registers, and diagnostic fields can still be required by KFD, MES, firmware, register dumps, out-of-tree tools, or future ASIC workarounds.

## Test Signals

Compile-time signals include successful AMDGPU/KFD builds wherever `REG_SET_FIELD`, `REG_GET_FIELD`, direct `__SHIFT` constants, or direct `MASK` constants reference GC 11 SDMA names. Missing or renamed macros normally fail at compile time; wrong numeric values usually require runtime testing.

Strong runtime signals are successful probe and resume of GC 11 ASICs using SDMA v6, passing `amdgpu_ring_test_helper()` for each SDMA instance, correct SDMA ring read/write pointer behavior, working doorbell submissions, no SDMA queue hangs under copy/fill workloads, and clean suspend/resume and GPU reset recovery.

KFD-specific signals include successful creation, load, preemption, restore, and teardown of SDMA queues on both SDMA engines; correct `v11_sdma_mqd` programming; valid doorbell offsets; and no timeouts while waiting for `SDMA*_QUEUE*_CONTEXT_STATUS__IDLE_MASK`.

Memory-management signals include stable VM-copy workloads, no unexpected UTCL1 invalidation busy hangs, no XNACK retry storms, correct page-fault attribution in register dumps, and no stale-data symptoms after cache-policy or invalidation-sensitive workloads.

Diagnostic signals include sane SDMA register dumps for `STATUS*`, `UTCL1_*_STATUS`, `RD_XNACK*`, `WR_XNACK*`, `EDC_COUNTER`, `ERROR_LOG`, `AQL_STATUS`, `CLOCK_GATING_STATUS`, queue doorbell logs, and mid-command data. RAS/error-injection testing should show counters and clear bits behaving as expected without persistent EDC or DBIT error latches after recovery.
