# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002569`: lines 1-2558, `Docs/researches/chunks/subset-b-002569_research.md`
- `subset-b-002570`: lines 2559-5106, `Docs/researches/chunks/subset-b-002570_research.md`
- `subset-b-002571`: lines 5107-7581, `Docs/researches/chunks/subset-b-002571_research.md`
- `subset-b-002572`: lines 7582-10044, `Docs/researches/chunks/subset-b-002572_research.md`
- `subset-b-002573`: lines 10045-12529, `Docs/researches/chunks/subset-b-002573_research.md`
- `subset-b-002574`: lines 12530-15146, `Docs/researches/chunks/subset-b-002574_research.md`
- `subset-b-002575`: lines 15147-17777, `Docs/researches/chunks/subset-b-002575_research.md`
- `subset-b-002576`: lines 17778-20327, `Docs/researches/chunks/subset-b-002576_research.md`
- `subset-b-002577`: lines 20328-22793, `Docs/researches/chunks/subset-b-002577_research.md`
- `subset-b-002578`: lines 22794-25201, `Docs/researches/chunks/subset-b-002578_research.md`
- `subset-b-002579`: lines 25202-27680, `Docs/researches/chunks/subset-b-002579_research.md`
- `subset-b-002580`: lines 27681-30173, `Docs/researches/chunks/subset-b-002580_research.md`
- `subset-b-002581`: lines 30174-32555, `Docs/researches/chunks/subset-b-002581_research.md`
- `subset-b-002582`: lines 32556-35081, `Docs/researches/chunks/subset-b-002582_research.md`
- `subset-b-002583`: lines 35082-37536, `Docs/researches/chunks/subset-b-002583_research.md`
- `subset-b-002584`: lines 37537-40041, `Docs/researches/chunks/subset-b-002584_research.md`
- `subset-b-002585`: lines 40042-40550, `Docs/researches/chunks/subset-b-002585_research.md`

## Chunk Research

### subset-b-002569: lines 1-2558

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 1-2558

## Scope

This chunk covers the opening 2,558 lines of the generated GC 12.0.0 register shift/mask header. The covered address block starts at `gc_gfx_cpwd_sdma0_sdmadec` and defines C preprocessor constants for SDMA0 control/status registers and the first SDMA0 RLC queue windows. The chunk ends in the middle of the `SDMA0_QUEUE7` register template at `SDMA0_QUEUE7_IB_OFFSET`, so queue 7 is only partially represented here.

## Purpose

The header provides hardware bitfield metadata for AMD GPU GC 12 SDMA registers. Each register field is expressed as a `__SHIFT` constant and a matching `_MASK` constant, which lets driver code use `REG_SET_FIELD`, `REG_GET_FIELD`, explicit shifts, and explicit masks without embedding numeric bit positions directly in SDMA, MES, and KFD code.

The covered lines are centered on SDMA0. They describe global SDMA engine control, microcode/status/diagnostic fields, UTCL1 translation and XNACK fields, interrupt/error reporting, queue reset state, and repeated per-queue ring/IB/doorbell/MQD/context-status fields for queues 0 through 6 plus the beginning of queue 7.

## Important Definitions

- Header guard: `_gc_12_0_0_SH_MASK_HEADER`.
- Global engine controls: `SDMA0_DEC_START`, `SDMA0_MCU_MISC_CNTL`, `SDMA0_UCODE_REV`, `SDMA0_POWER_CNTL`, `SDMA0_CNTL`, `SDMA0_CNTL1`, `SDMA0_FREEZE`, `SDMA0_WATCHDOG_CNTL`, `SDMA0_QUEUE_RESET_REQ`.
- Engine status and diagnostics: `SDMA0_STATUS_REG`, `SDMA0_STATUS1_REG`, `SDMA0_STATUS2_REG`, `SDMA0_STATUS3_REG`, `SDMA0_STATUS4_REG`, `SDMA0_STATUS5_REG`, `SDMA0_STATUS6_REG`, `SDMA0_STATUS7_REG`, `SDMA0_STATUS8_REG`, `SDMA0_FED_STATUS`, `SDMA0_AQL_STATUS`, `SDMA0_ERROR_LOG`, `SDMA0_GPU_IOV_VIOLATION_LOG`, `SDMA0_INVALID_ADDR_*`, and global timestamps/counters.
- Performance, ordering, and cache policy fields: `SDMA0_CACHE_CNTL`, `SDMA0_DCC_CNTL`, `SDMA0_RELAX_ORDERING_LUT`, `SDMA0_CHICKEN_BITS`, `SDMA0_CHICKEN_BITS_2`, `SDMA0_GLOBAL_QUANTUM`, `SDMA0_CRD_CNTL`, `SDMA0_RLC_CGCG_CTRL`, and `SDMA0_CLOCK_GATING_STATUS`.
- Translation/cache interaction fields: `SDMA0_UTCL1_CNTL`, `SDMA0_UTCL1_WATERMK`, `SDMA0_UTCL1_TIMEOUT`, `SDMA0_UTCL1_PAGE`, `SDMA0_UTCL1_RD_STATUS`, `SDMA0_UTCL1_WR_STATUS`, `SDMA0_UTCL1_INV0/1/2`, and read/write XNACK fields.
- Queue templates: `SDMA0_QUEUE0_*` through full `SDMA0_QUEUE6_*`, and partial `SDMA0_QUEUE7_*`. The repeated fields include ring buffer control/base/read/write pointers, read-pointer writeback address, IB control/rptr/offset/base/size, doorbell enable/log/offset, context save area address, scheduling, IB preemption, write-pointer poll address, AQL control, minor pointer update, context-switch exception status, mid-command save/restore data, MQD base/control, dequeue request, and context status.

There are no functions, structs, or executable algorithms in this chunk. The public API surface is the macro namespace consumed by compiled driver code.

## Control Flow

This file has no runtime control flow. Its effect is compile-time substitution of constants into consumers. Runtime control flow appears in the users:

- `sdma_v7_0.c` uses queue and status masks while enabling/disabling SDMA rings, configuring ring-buffer and IB registers, programming doorbells, setting UTCL1 retry behavior, polling `SDMA0_STATUS_REG.UCODE_INIT_DONE`, and testing SDMA rings/IBs.
- `kfd_mqd_manager_v12.c` uses queue bit positions to fill `struct v12_sdma_mqd` fields for KFD SDMA queues, including queue size, VMID, writeback timer, doorbell offset, scheduling quantum, and `SWITCH_INSIDE_IB`.
- `amdgpu_amdkfd_gfx_v12.c` relies on the regular queue register spacing from `regSDMA0_QUEUE0_RB_CNTL` to `regSDMA0_QUEUE0_CONTEXT_STATUS` when dumping SDMA HQD state.
- `mes_v12_0.c` writes `SDMA0_QUEUE_RESET_REQ` or the SDMA1 peer to reset one SDMA queue and polls until the bit clears.

## State and Persistence

The macros describe persistent hardware state held in MMIO registers, MQD memory images, and queue context-save areas, but the header does not store state by itself.

Important state described by this chunk includes:

- Ring-buffer state: base address, size, read/write pointers, write-pointer polling, and read-pointer writeback.
- IB state: enable bit, VMID, base, offset, size, rptr, sub-remaining count, and preemption controls.
- Doorbell state: enable/captured bits, doorbell offset, and error/log data.
- Scheduling/context state: global/process/local IDs, context quantum, selected/idle/expired flags, exception class bits, VF/private/preempt-disable indicators, pending write-pointer updates, and update-fail counts.
- Error and recovery state: page fault/null/retry timeout bits, VM-hole and page exceptions, queue-hang and doorbell-error exceptions, SRAM/DRAM ECC indicators, invalid address logs, external frozen state, and queue reset request bits.
- Power/clock state: light-sleep enable, fine-grain clock-gating override/status bits, and RLC clock-gating control.

Because these fields map directly to hardware, incorrect shifts or masks can persist as corrupted queue descriptors, missed interrupts, hung queues, or wrong diagnostic dumps until the engine or GPU is reset.

## Dependencies and Integration Points

This header is included by GC 12 AMDGPU/KFD components such as `gfx_v12_0.c`, `sdma_v7_0.c`, `mes_v12_0.c`, `gfxhub_v12_0.c`, `imu_v12_0.c`, `soc24.c`, `amdgpu_amdkfd_gfx_v12.c`, `kfd_device_queue_manager_v12.c`, and `kfd_mqd_manager_v12.c`.

It pairs with the corresponding address-definition header for symbols like `regSDMA0_QUEUE0_RB_CNTL`; this file only defines field positions and masks. It also depends on AMDGPU register helper conventions:

- `REG_SET_FIELD(value, REGISTER, FIELD, field_value)` expects `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`.
- `REG_GET_FIELD(value, REGISTER, FIELD)` expects the same pair for decoding register reads.
- Some code uses shifts and masks directly when constructing MQD words, for example `SDMA0_QUEUE0_RB_CNTL__RB_SIZE__SHIFT` and `SDMA0_QUEUE0_SCHEDULE_CNTL__CONTEXT_QUANTUM_MASK`.

The repeated queue macros are designed to share field layout across hardware queue windows. Consumers usually program queue 0 register names plus computed register offsets for the target SDMA engine and queue.

## Risks

- Generated-header drift is the main risk. If GC 12 hardware XML/register specifications change and this header is not regenerated consistently with the address header, the driver can write valid-looking values into the wrong bitfields.
- The queue template repetition increases copy/paste or generation risks. A one-off mismatch between queue 0 and later queues could affect only KFD or RLC queues that are less frequently tested.
- Address-width fields have alignment assumptions, commonly low two bits omitted in `_LO` fields. Wrong shifts for base, poll, RPTR, CSA, MQD, or doorbell offsets can silently corrupt GPU addresses.
- Status and exception bits are used for timeout and reset decisions. Misdecoded `IDLE`, `UCODE_INIT_DONE`, context exception, or queue reset bits can produce false hangs or missed recovery paths.
- Several fields are security and isolation sensitive, including VMID, private queue, GPU IOV violation, VM-hole/page exception, doorbell error, and invalid address fields. Incorrect masks could weaken diagnostics or route queues into the wrong VM context.
- Because this file is a macro-only include, compilers provide little type checking. Errors surface as hardware behavior, self-test failures, hangs, or diagnostics mismatches rather than ordinary compile failures unless a macro is missing.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-facing:

- Build coverage for all GC 12 consumers that include `gc_12_0_0_sh_mask.h`; missing or renamed macros fail compilation in `sdma_v7_0.c`, `kfd_mqd_manager_v12.c`, `amdgpu_amdkfd_gfx_v12.c`, and MES/KFD paths.
- SDMA startup should successfully load/unhalt firmware, poll `SDMA0_STATUS_REG.UCODE_INIT_DONE`, configure RB/IB/doorbell registers, and enable rings without timeout.
- `sdma_v7_0_ring_test_ring` should write the expected test value through an SDMA packet, proving ring buffer, pointer, doorbell, and writeback fields are coherent.
- `sdma_v7_0_ring_test_ib` should schedule an IB and observe fence completion, exercising `IB_ENABLE`, `IB_SWAP_ENABLE`, IB pointer/base/size, and queue execution state.
- KFD SDMA queue creation should produce valid MQDs, correct doorbell offsets, correct scheduling quantum, and stable context switching under queue dumps.
- Queue reset via `SDMA0_QUEUE_RESET_REQ` should clear the requested bit within the timeout.
- Debug and hang diagnostics should decode status registers consistently: idle bits, page fault/null/retry timeout bits, UTCL1 XNACK status, queue exception bits, invalid address logs, and IOV violation logs should match hardware events.

### subset-b-002570: lines 2559-5106

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 2559-5106

## Purpose

This chunk is a generated AMD GPU register field header for the GC 12.0.0 SDMA register space. It defines `*_SHIFT` and `*_MASK` constants used by AMDGPU kernel code to pack and unpack bitfields in memory-mapped SDMA control, status, virtualization, performance, cache, fault, and queue registers. The file contains no functions or runtime control flow; its behavior is entirely compile-time exposure of register ABI constants.

The covered range starts at the tail of the `SDMA0_QUEUE7` queue definition, then covers SDMA0 hypervisor/decode, PSP/decode, performance counter, and power-control blocks. It then enters the `SDMA1` block and defines global SDMA1 controls/status registers plus per-queue templates for SDMA1 queues 0 through part of queue 5.

## Important APIs, Types, and Macro Families

- `SDMA0_QUEUE7_*`: remaining queue-7 fields for indirect buffer base/offset/size, doorbell enable/capture/log/offset, CSA address, schedule control, preemption, write-pointer polling, AQL control, context-switch exception status, mid-command save/restore data, MQD base/control, dequeue request, and context status.
- `SDMA0_VM_CTX_*`, `SDMA0_ACTIVE_FCN_ID`, `SDMA0_VIRT_RESET_REQ`, `SDMA0_VM_CNTL`: SDMA0 virtualization and VM context masks, including VF/PF reset request bits and active VF identification.
- `SDMA0_MCU_CNTL`, `SDMA0_IC_*`: microcontroller halt/reset/debug bits and instruction-cache base/control/operation masks, including invalidate, prime, primed, VMID, execute-disable, and MALL policy fields.
- `SDMA0_PERFCNT_*` and `SDMA0_PERFCOUNTER*`: SDMA0 performance counter selector, mode, clear/enable, result-control, low/high counter result, compare, and multi-selector masks.
- `GFX_ICG_SDMA0_CTRL`: SDMA0 power/clock gating override masks for register, pointer, PIO, MCU, copy/serve engines, command fetch, memory request, invalidation, caches, memory channels, performance counters, and hysteresis.
- `SDMA1_*` global registers: second SDMA engine decode start, MCU wakeup, ucode revision, global timestamp, power control, main control, tuning bits, cache policy, fetch offsets, program stream, status registers, freeze/preempt controls, process/global quantum, watchdog, queue status, EDC/ECC, ID/version, atomic controls, DCC controls, UTCL1 translation/cache controls, XNACK/fault state, relaxed ordering, credit/clock gating, IOV violation logs, invalid-address logs, interrupt status, scratch RAM, timestamp capture, queue reset, CE control, and FED/ECC status.
- `SDMA1_QUEUE{0..5}_*` templates: per-queue ring-buffer, indirect-buffer, doorbell, scheduling, AQL, preemption, mid-command, MQD, dequeue, and context-status field masks. The chunk fully covers queues 0 through 4 and continues through the start/middle of queue 5.

There are no C structs, enums, functions, or callable APIs in this range. Consumers include these macros directly in register read/modify/write expressions, usually through AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32`, and `RREG32` in nearby driver code.

## Control Flow and Data Flow

Runtime control flow is supplied by code outside this header. The effective data flow is:

1. Driver code reads a 32-bit MMIO register value or prepares a new 32-bit value.
2. A field macro pair identifies the bit offset and bit mask for a hardware field.
3. The caller shifts, masks, inserts, tests, or clears the field.
4. The caller writes the value back to the SDMA register or interprets the readback as queue, fault, power, or performance state.

The per-queue definitions describe repeated SDMA queue state machines. `RB_*` fields configure or observe ring buffers; `IB_*` fields configure indirect-buffer execution; `DOORBELL*` fields connect host/user write-pointer updates to hardware; `AQL_*` fields configure HSA/AQL packet handling; `CONTEXT_SWITCH_STATUS` and `CONTEXT_STATUS` expose preemption, idle, exception, VF, privilege, and pointer-update state.

## State and Persistence Behavior

The header does not allocate or persist state. The state represented by these masks lives in GPU hardware registers and hardware-managed memory structures:

- Ring-buffer bases, read/write pointers, writeback addresses, polling addresses, and MQD bases are persistent hardware programming state until reset, queue teardown, or driver reprogramming.
- Doorbell enable/offset/capture and doorbell log fields reflect host-to-GPU queue notification state and error capture.
- Context status, context-switch status, status registers, XNACK fault registers, invalid-address registers, ECC/FED registers, IOV violation logs, and queue status registers are hardware-observed diagnostic state.
- Performance counter selector/control and counter-result fields persist while enabled and are cleared by explicit clear bits.
- Freeze, preempt, reset, watchdog, quantum, and clock/power gating fields affect ongoing SDMA scheduling and power-management behavior.

Because the constants are compile-time ABI definitions, persistence risks are not in this file itself; they arise when caller code writes incorrect field values or uses the wrong mask for the active ASIC generation.

## Dependencies and Integration Points

This header depends only on the C preprocessor and the AMD register naming convention. It is part of the generated AMDGPU ASIC register set and should be paired with the corresponding address header for GC 12.0.0 registers. Typical integration points are:

- SDMA engine initialization and teardown paths that configure `SDMA1_CNTL`, power control, cache policy, clock gating, ucode, instruction cache, queue rings, MQDs, and doorbells.
- Queue management paths for KFD/AMDGPU compute queues, especially AQL, MQD, VMID, context-switch, preemption, and dequeue handling.
- Virtualization/SR-IOV paths that inspect active VF IDs, VF/PF reset requests, GPU IOV violation logs, and VF context status.
- Fault handling paths for page faults, null/retry timeout XNACKs, invalid addresses, UTCL1 invalidation, and read/write translation status.
- Debug and health paths that poll idle/status bits, ECC/FED status, watchdog state, queue enable status, and active queue IDs.
- Performance monitoring code that selects SDMA performance events, enables/clears counters, and reads 32-bit/64-bit counter values.

## Risks and Edge Cases

- **Generated ABI drift:** A one-bit shift or mask mismatch silently corrupts register programming. This is especially risky for queue base addresses, VMIDs, doorbell offsets, reset bits, and fault-log interpretation.
- **Partial queue coverage:** The chunk starts mid-`SDMA0_QUEUE7` and ends mid-`SDMA1_QUEUE5`; readers must merge adjacent chunks for complete per-file coverage.
- **Repeated queue templates:** Queue macros are mechanically similar. Copy/paste mistakes in consumers can use a queue-0 mask with a queue-3 register or vice versa; the compiler will not catch this because all values are integer constants.
- **Reserved fields:** Several masks expose reserved ranges. Callers should preserve reserved bits during read/modify/write unless hardware documentation says otherwise.
- **Address alignment fields:** Many address fields shift by two and mask low bits off. Callers must provide aligned GPU addresses and split low/high parts consistently.
- **Privilege and virtualization bits:** `VF`, `VFID`, `RB_PRIV`, VMID, IOV log, and PF/VF reset fields affect isolation. Incorrect use can break SR-IOV or leak/misattribute faults.
- **Status-vs-control ambiguity:** Some registers are control writes, some are status readbacks, and some are write-one action bits. The header does not encode access type, so behavior depends on the matching register-address/spec metadata and caller discipline.

## Test Signals

Useful validation for changes around this header is mostly integration and hardware-observation based:

- Build coverage for AMDGPU/KFD code that includes GC 12.0.0 register headers; compile errors catch missing/renamed macros.
- Queue bring-up tests should show SDMA1 ring buffers enabled, valid MQD base/control programming, doorbell updates accepted, and no `WPTR_LT_RPTR`, doorbell, page, or queue-hang exceptions.
- Suspend/resume and GPU reset tests should exercise `FREEZE`, queue reset, context status, and idle/status polling paths.
- SR-IOV testing should validate active VF identification, VF/PF reset request handling, VF context status, and IOV violation log decoding.
- Fault-injection or negative tests should verify page fault, retry timeout, null page, invalid address, and XNACK read/write logs decode to the expected VMID/address/vector fields.
- Performance counter tests should confirm event selection, enable/clear behavior, low/high counter reads, and stop-on-saturate behavior.
- Power-management tests should monitor clock-gating status and confirm clock/power override fields do not leave SDMA stuck non-idle or unavailable.

### subset-b-002571: lines 5107-7581

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 5107-7581

## Scope

This chunk is a generated AMD GC 12.0.0 shift/mask register-header segment. It contains only C preprocessor constants: each register field has a `__SHIFT` bit position and a matching `_MASK` bit mask used by AMDGPU register helpers to compose and decode 32-bit hardware register values. There are no functions, structs, enums, executable branches, memory allocations, locks, callbacks, or persistence mechanisms in this range.

The selected lines start inside the SDMA1 queue 5 mid-command state family, after the `SDMA1_QUEUE5_MIDCMD_DATA0` comment from the previous chunk. The range then covers the remaining SDMA1 queue 5 tail fields, complete SDMA1 queue 6 and queue 7 queue-control/state fields, SDMA1 hypervisor/PSP/performance/power address blocks, GRBM status/control/error/trap/scratch fields, CP CPC/CPF/ME/PFP queue and diagnostic fields, PA/GE/VGT/UTCL1 fields, and the first part of compute dispatch state. The chunk ends in the middle of `COMPUTE_REQ_CTRL`; the remaining masks and any following compute registers continue in the adjacent chunk.

Although the repository path is nested under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata for the GC 12.0.0 graphics IP and is not Ceph filesystem logic.

## Purpose

`gc_12_0_0_sh_mask.h` describes hardware bit layouts for GC 12.0.0 registers. Driver code pairs these macros with register address symbols from the companion GC 12.0.0 offset header and, where available, generated default/reset-value headers. The usual consumers are AMDGPU low-level register helpers such as `REG_SET_FIELD` and `REG_GET_FIELD`, MMIO read/write paths, command-packet register programming, debug dump decoders, performance-counter tools, reset handling, virtualization paths, and queue setup code.

This chunk focuses on four broad surfaces:

- SDMA1 queue programming and SDMA1 engine control: ring buffers, indirect buffers, doorbells, CSA/MQD addresses, VMIDs, AQL controls, preemption, context switch/error status, mid-command save/restore data, instruction cache controls, virtualization reset/active function state, performance counters, and SDMA1 clock-gating override fields.
- GRBM global graphics management: busy/clean status by shader engine, read/write/invalid-pipe error attribution, soft reset controls, interrupt enables, trap registers, UTCL2 invalidation ranges, fence ranges, clock/power tuning fields, scratch registers, SA disable fields, and generated workaround-style clock-gating fields.
- CP command-processor diagnostics and queue internals: CPC/CPF status, busy/stall breakdowns, free-count registers, scratch index/data, command index/data windows, ROQ/STQ/MEQ thresholds and pointers, ring read-pointer state, write-pointer polling delay, debug/interrupt status, and privilege-violation addresses.
- PA/GE/VGT/UTCL1 and compute launch state: geometry/watchdog and UTCL1 fault/control fields, DMA/draw FIFO depths, GE privilege/status, VGT debug/reset fields, compute dispatch dimensions, program address/resource registers, scratch/dispatch-packet addresses, VMID, resource limits, CU enable/static-thread-management fields, temporary ring sizing, restart coordinates, thread trace, dispatch IDs, and the beginning of compute request-control throttling fields.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public contract is the generated macro naming scheme:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the field's 32-bit mask.
- Matching register addresses are expected in the GC 12.0.0 offset header, commonly as `mm...` register symbols.
- Consumers should pack and extract values through the AMDGPU register-field helpers instead of hard-coding these constants again.

Important macro families in this slice include:

- `SDMA1_QUEUE5_*`, `SDMA1_QUEUE6_*`, and `SDMA1_QUEUE7_*`: SDMA queue state for mid-command data, wait thresholds, MQD base/control, dequeue requests, context status, ring buffer base/read/write pointers, writeback/poll addresses, indirect-buffer base/offset/size, doorbell enable/capture/log/offset, CSA addresses, scheduling IDs and quantum, AQL packet controls, minor pointer updates, preemption, and context-switch exception bits.
- `SDMA1_VM_*`, `SDMA1_ACTIVE_FCN_ID`, `SDMA1_VIRT_RESET_REQ`, `SDMA1_MCU_*`, and `SDMA1_IC_*`: SDMA1 virtualization context address, active PF/VF attribution, virtual reset requests, VM commands, microcontroller halt/reset/debug selection, instruction-cache base/control, invalidate/prime state, VMID, execute-disable, MALL policy, GPA, and auto-prime controls.
- `SDMA1_PERFCNT_*` and `SDMA1_PERFCOUNTER*`: SDMA1 event selection, selector extensions, counter modes, enable/clear controls, result-selection triggers, low/high result words, and compare-value fields.
- `GFX_ICG_SDMA1_CTRL`: SDMA1 medium-grain clock-gating soft override and hysteresis bits for register, pointer, PIO, MCU, copy, serving, command fetch, memory request/cache/channel, instruction cache, performance counter, and core sub-block clocks.
- `GRBM_*`: global graphics register bus manager controls and status. These include global busy/clean bits, per-SE status for SE0-SE3, status3 MES/GL/cache busy bits, soft reset bits for CP/RLC/UTCL2/GFX/CPF/CPC/CPG/CAC/EA/SDMA, read/write error attribution, interrupt enables, trap operation/address/data masks, DSM bypass, chip revision, IH credit, power-halt requests, UTCL2 invalidation range start/end, invalid pipe attribution, fence ranges, clock-gating workaround fields, scratch registers, and interface bridge disable.
- `CP_CPC_*`, `CP_CPF_*`, and generic `CP_*`: command processor status, busy, stalled, free-count, header dump, scratch, command window, ROQ/STQ/MEQ threshold/availability/stat pointer fields, ring read pointer fields, write-pointer delay/polling, context status, interrupt debug status, and privilege violation address fields.
- `VGT_*`, `GE_*`, `GFX_PIPE_CONTROL`, `WD_UTCL1_*`, and `IA_UTCL1_*`: primitive assembly/draw FIFO depth, VGT debug/reset masks, geometry-engine busy and privilege/status fields, graphics pipe control, and UTCL1 fault/retry/PRT status/control for work distributor and input assembler clients.
- `COMPUTE_*`: compute dispatch state through the start of `COMPUTE_REQ_CTRL`, including dispatch initiator flags, X/Y/Z dimensions and starts, X/Y/Z thread counts and interleave fields, pipeline/perf enable, program and dispatch/scratch addresses, program resource descriptors, VMID, resource limits, per-SE CU routing/static thread management for SE0-SE3, temporary ring size, restart coordinates, thread tracing, miscellaneous reserved state, dispatch ID, and threadgroup ID.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied driver flow is:

1. Select GC 12.0.0 register metadata for the active ASIC.
2. Select the matching register address from the GC 12.0.0 offset header.
3. Read an existing register value or construct a new MMIO/command-packet register value.
4. Use the `__SHIFT` and `_MASK` pairs, usually via `REG_SET_FIELD` or `REG_GET_FIELD`, to encode or decode the relevant fields.
5. Apply the value in SDMA queue setup, SDMA preemption/recovery, virtualization, performance-counter programming, clock/power management, GRBM reset/status/error handling, CP diagnostics, geometry/UTCL fault handling, or compute dispatch setup.

For SDMA queues, typical runtime sequencing programs ring bases and sizes, writeback/polling addresses, doorbells, VMID/MQD state, AQL/preemption controls, and then monitors context status or context-switch exception bits during execution and recovery. For performance counters, consumers select events and modes, clear/enable counters, gate result collection with result-control triggers, and read low/high result registers. For GRBM/CP status, reset, and diagnostics, code usually polls clean/busy bits, decodes failed read/write/pipe access attribution, asserts soft reset bits during recovery, and dumps CP/CPC/CPF busy and stall registers for hang analysis. For compute state, command processor or queue setup code writes dispatch dimensions, program addresses/resource descriptors, VMID, CU enable masks, scratch/temporary-ring information, and initiator flags before work is launched.

This generated header does not encode ordering rules, required waits, clear-on-read semantics, sticky status behavior, latching rules for high/low counters, reset timing, or reserved-bit preservation policies. Those requirements live in AMDGPU engine code, firmware contracts, and hardware programming documentation.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe stateful GPU registers controlled by hardware, firmware, and AMDGPU runtime code.

SDMA queue fields represent persistent queue programming until the queue is disabled, reprogrammed, preempted, reset, or lost over a power transition. Ring base/control, read/write pointers, writeback and polling addresses, doorbell offsets, VMID/MQD fields, CSA addresses, AQL controls, and scheduling state must remain consistent with queue memory and process ownership. Mid-command data registers are save/restore state for preemptible operations and can become critical during queue preemption or recovery.

SDMA hypervisor and PSP-facing fields carry virtualization and microcontroller state. Active function ID, virtual reset request bits, VM context addresses, instruction-cache base/control, and execute-disable controls can affect PF/VF isolation, firmware execution, and queue recovery. These fields should be treated as privileged, side-effecting control state rather than passive metadata.

GRBM and CP status/error/interrupt/debug fields are a mixture of live status, sticky diagnostic state, and side-effecting controls. Busy/clean bits reflect active hardware pipelines. Soft reset and power-halt fields directly change engine state. Read/write error, invalid pipe, privilege-violation, interrupt debug, and UTCL1 fault fields are diagnostic state that may require hardware-specific clear or acknowledge sequences outside this header.

Compute registers are active dispatch state. Program address, resource descriptors, VMID, dispatch dimensions, thread counts, static thread/CU masks, scratch addresses, temporary-ring sizing, restart coordinates, and initiator bits can remain relevant across dispatch execution, preemption, debug capture, or recovery. Incorrect field packing can launch the wrong shader, use invalid resource counts, target disabled compute units, or corrupt scratch/restart behavior.

Performance counter selectors and controls persist while counters accumulate. Low/high result registers may need a hardware-defined snapshot or read sequence to avoid torn values; the mask header cannot express that atomicity requirement.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.0.0 register family staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h` should provide matching register address macros for these field definitions.
- Any matching GC 12.0.0 default/reset header should remain consistent with these masks.
- Common AMDGPU register helpers provide the actual field packing/extraction and MMIO or command-packet access mechanisms.
- AMDGPU SDMA, GFX, CP, KFD/compute, virtualization/SR-IOV, reset, suspend/resume, performance monitoring, debugfs, and hang-dump paths are the likely consumers.

Integration points include SDMA ring creation/teardown, SDMA doorbell programming, MQD/CSA setup, SDMA AQL/preemption handling, SDMA context-switch exception reporting, SDMA instruction-cache and microcontroller control, per-engine performance counters, GRBM idle polling and soft reset, GRBM read/write/invalid-pipe diagnostics, trap/debug plumbing, CP command queue diagnostics, CP ring pointer and ROQ/STQ/MEQ introspection, privilege violation reporting, PA/GE/VGT debug controls, UTCL1 fault handling, compute dispatch packet setup, compute shader resource programming, CU enable/static thread management, and compute tracing/debug paths.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask still compiles but can write the wrong hardware bits or decode misleading diagnostics.
- The chunk starts and ends mid-family. `SDMA1_QUEUE5_MIDCMD_DATA0` is only partially visible at the start, and `COMPUTE_REQ_CTRL` continues after line 7581; final file-level research must merge adjacent chunks before drawing complete conclusions for those registers.
- SDMA queue 6 and 7 definitions are highly repetitive. Copy/generator mistakes can affect one queue only, producing queue-specific hangs, wrong doorbell behavior, or incorrect exception attribution.
- Address fields are not uniformly full byte addresses. Many low address fields start at bit 2 or bit 12, while high words may be full or narrow. Callers must respect alignment and split-address semantics for ring bases, read-pointer writeback, write-pointer polling, IB bases, CSA/MQD bases, SDMA IC bases, compute program addresses, and dispatch/scratch addresses.
- Doorbell, VMID, MQD, active function, and virtual reset fields are isolation-sensitive. Incorrect masks can route work to the wrong VMID/VF, lose queue notifications, or mis-handle PF/VF reset.
- Soft reset and power/clock-gating controls are side-effecting. Full-register writes that fail to preserve reserved bits around `GRBM_SOFT_RESET`, `GRBM_PWR_CNTL*`, `GFX_ICG_SDMA1_CTRL`, or clock-gating workaround fields can destabilize unrelated blocks.
- Status and error registers often contain sticky or latched bits. Decoding with the wrong mask can hide read/write errors, invalid-pipe events, privilege violations, UTCL faults, or CP interrupts during recovery.
- CP busy/stall families are dense and similar across CPC, CPF, ME, PFP, MEC, MES, ROQ, STQ, and MEQ blocks. Assuming symmetry between registers can produce incorrect hang diagnoses.
- Compute resource fields are densely packed. Incorrect widths for VGPR/SGPR counts, LDS size, exception enables, WGP mode, scratch enable, user SGPR counts, CU masks, or resource limits can cause invalid dispatches, GPU faults, or silent performance/debug anomalies.
- Performance counter high/low results can be race-prone if read without the documented latching sequence. This header only identifies bits; it does not make counter reads atomic.

## Test Signals

Useful validation for this chunk is generated-data consistency plus build/runtime coverage:

- Kernel build coverage for AMDGPU files that include `gc_12_0_0_sh_mask.h`, especially SDMA, GFX, CP, KFD/compute, reset, virtualization, debug, and perf counter paths.
- Mechanical comparison against AMD's authoritative GC 12.0.0 register database to confirm every `__SHIFT` and `_MASK` value in this line range.
- Cross-checks that every register family in this chunk has matching address macros in `gc_12_0_0_offset.h` and expected defaults in the matching generated default header where applicable.
- Static mask sanity checks: masks should align with shifts, repeated SDMA queue 6/7 families should remain structurally identical where hardware intends, full-width data fields should use full masks, split address masks should match documented alignment, and fields should not overlap unless explicitly documented.
- SDMA tests that initialize queues 5 through 7, program ring bases, writeback/polling addresses, doorbells, MQD/CSA state, AQL controls, preempt/dequeue requests, and verify pointer progress plus context status under normal and preempted workloads.
- Virtualization tests that exercise SDMA active function ID, VF/PF reset requests, VM context registers, and doorbell/error attribution with expected VF/VMID isolation.
- Perf counter tests that select SDMA1 events, clear/enable counters, run controlled copy workloads, read low/high results, and verify monotonic or expected event activity.
- GRBM reset/idle tests that poll global and per-SE busy/clean bits, issue reset paths, and verify recovery without stale busy bits or unexpected soft-reset side effects.
- Hang/debug dump tests that decode GRBM read/write errors, invalid-pipe events, CP/CPC/CPF busy and stalled bits, CP interrupt debug bits, privilege violations, and scratch/header dump registers coherently.
- UTCL1/GE/VGT tests that exercise fault/retry/PRT reporting, geometry status, DMA/draw FIFO depth reporting, and VGT reset/debug fields under controlled fault and draw workloads.
- Compute dispatch tests that validate program address/resource packing, VMID, dispatch dimensions, thread counts, CU masks, scratch/temporary-ring state, restart coordinates, thread trace enablement, dispatch IDs, and request-control throttling once the adjacent `COMPUTE_REQ_CTRL` masks are included.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002571`. It covers lines 5107-7581 of `gc_12_0_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the partial SDMA1 queue 5 and `COMPUTE_REQ_CTRL` register families and to place these SDMA, GRBM, CP, PA/GE/VGT/UTCL1, and compute definitions in the full GC 12.0.0 register map.

### subset-b-002572: lines 7582-10044

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 7582-10044

## Scope

This chunk is a generated AMD GC 12.0.0 shift/mask header slice. It contains C preprocessor `#define` constants only: each hardware register field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro. There are no functions, structs, enums, global variables, allocations, locks, MMIO operations, or executable branches in this range.

The selected lines contain 2,148 `#define` statements. The chunk starts in the middle of `COMPUTE_REQ_CTRL`, continues through compute shader dispatch and user-data fields, then covers RAS signature state, PF-only GC current/activity counter and throttle controls, EA/SDP fabric controls, GCR/PMM controls, GCUTCL2 shared VM aperture controls, GCVM L2 translation-cache and protection-fault controls, GCVM context control registers for contexts 0-15, and the beginning of the GCVM invalidate-engine semaphore family. It ends at `GCVM_INVALIDATE_ENG2_SEM`, so the remainder of the invalidate-engine register family is in the next chunk.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU DRM hardware metadata and is unrelated to Ceph filesystem behavior.

## Purpose

`gc_12_0_0_sh_mask.h` gives GC 12.0.0 AMDGPU code the bit positions and masks needed to compose, update, and decode graphics-core registers without embedding raw bit constants in driver code. Consumers pair these field definitions with register offsets from `gc_12_0_0_offset.h` and access helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and RLC/golden-register table macros.

This chunk covers these hardware surfaces:

- Compute queue and dispatch state: request throttling in `COMPUTE_REQ_CTRL`, CU enable masks for static thread management, user accumulators, program resource field 3, dispatch interleave, relaunch payload/state flags, wave restore address, prescaled dimensions, 16 compute user-data registers, dispatch tunnel/end markers, and reserved shader registers.
- RAS and power telemetry: `RAS_GE_SIGNATURE0` plus GC CAC aggregation, per-SE aggregation, EDC/DIDT/PCC/PWRBRK throttle controls, status, overflow, rolling-power, clock-monitor, soft snapshot, indirect index/data, and per-block weighting fields.
- EA/SDP fabric controls for CPWD and SE paths: VC mapping, arbitration, priority, tag and credit reserve registers, request controls, miscellaneous/error fields, backdoor credit programming, and enable bits.
- GCR and PMM controls: `GCR_PIO_CNTL`, `GCR_PIO_DATA`, `PMM_CNTL`, and `PMM_STATUS`.
- GCUTCL2/GCMC shared virtual-memory controls: MMIO aperture, PCI, top-of-DRAM, framebuffer offset/location, system aperture defaults, steering, shared virtual reset, cacheable/local sysmem/local framebuffer ranges, local-FB locking, clock-gating controls, active function ID, harvest bypass, and group fault status.
- GCVM L2 and context controls: L2 cache/TLB configuration, invalidation controls, protection fault defaults and status decode, identity aperture registers, bank/partition controls, parity controls, clock-gating controls, GCR integration, walker throttling, PTE cache dump fields, GPUVA VMID translation-assist request/response fields, credit-safety controls, contexts 0-15 enable/page-table/fault-policy fields, context disable bits, and the first invalidate-engine semaphore bits.

## Important APIs, Types, And Macros

The only interface in this chunk is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the starting bit index for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the register-width mask for the same field.
- `// addressBlock:` comments identify the generated hardware address block that owns the following register fields.
- Plain `//<REGISTER>` comments group the field macros by register.

There are no callable APIs or C types here. Important macro families include:

- `COMPUTE_*`: shader/compute dispatch and queue fields, especially `COMPUTE_STATIC_THREAD_MGMT_SE4..SE8`, `COMPUTE_PGM_RSRC3`, `COMPUTE_RELAUNCH*`, `COMPUTE_WAVE_RESTORE_ADDR_*`, `COMPUTE_PRESCALED_DIM_*`, and `COMPUTE_USER_DATA_0..15`.
- `GC_CAC_*`, `SE*_CAC_*`, `GC_EDC_*`, `GC_THROTTLE_*`, `DIDT_*`, `PCC_*`, and `PWRBRK_*`: current/activity counting, power estimation, hysteresis, throttle pattern, status, performance counter, and weighting fields.
- `GC_EA_CPWD_*` and `GC_EA_SE_*`: EA fabric virtual-channel, credit, priority, arbitration, request-control, backdoor, error, and enable fields.
- `GCMC_VM_*`, `GCUTCL2_*`, `GCVM_L2_*`, and `GCUTC_GPUVA_*`: graphics hub aperture, L1/L2 VM cache, translation, fault, invalidate, parity, clock-gating, and translation-assist fields.
- `GCVM_CONTEXT0_CNTL` through `GCVM_CONTEXT15_CNTL`: repeated per-VMID context controls for enabling a context, page-table depth/block size, retry behavior, and interrupt/default handling of range, dummy-page, PDE0, valid, read, write, and execute protection faults.
- `GCVM_CONTEXTS_DISABLE` and `GCVM_INVALIDATE_ENG0_SEM..ENG2_SEM`: context disable and invalidate engine semaphore fields at the chunk boundary.

## Control Flow

This header has no runtime control flow. Its effect is compile-time substitution of symbolic bit positions and masks into driver code.

The implied runtime flow is:

1. A GC 12.0.0 driver path selects a register offset from `gc_12_0_0_offset.h` and field macros from this header.
2. The driver composes or extracts a value with `REG_SET_FIELD`, `REG_GET_FIELD`, explicit shifts, or masks.
3. The value is written to or read from the GPU through SOC15 MMIO helpers, RLC-safe helpers, indirect GC CAC helpers, IMU/RLC golden initialization tables, queue descriptor setup, or KFD queue-management code.
4. The hardware block applies the resulting state to dispatch scheduling, queue descriptors, VM translation, cache invalidation, fault reporting, throttling, power telemetry, or fabric credit behavior.

Observed consumers in this tree include `gfxhub_v12_0.c`, which programs `GCVM_L2_CNTL*`, context controls, protection fault defaults/status, and invalidate request/ack/semaphore spacing; `imu_v12_0.c`, which uses GC 12 golden values for EA/SDP and GCVM setup; KFD MQD code for compute queue descriptors; and the v12.1 device queue manager, which toggles `GCVM_CONTEXT0_CNTL__RETRY_PERMISSION_OR_INVALID_PAGE_FAULT__SHIFT` for XNACK behavior.

## State And Persistence Behavior

The macros themselves are stateless compile-time constants. Persistent and volatile state exists in the GPU registers or in memory descriptors interpreted by the GPU.

The represented hardware state includes compute dispatch inputs, CU selection masks, user SGPR payloads, shader program resource flags, relaunch/wave-restore state, RAS signatures, CAC/EDC/DIDT/PCC/PWRBRK counters and throttle policy, EA fabric credit allocation, GCR/PMM status, VM aperture/range configuration, GCVM L2 cache behavior, fault-default and fault-status registers, identity aperture mappings, translation-assist request/response state, per-context translation and fault policy, and invalidate engine semaphores.

Many of these registers persist until rewritten, GPU reset, graphics hub reinitialization, queue teardown/reload, VM context reprogramming, suspend/resume restore, clock/power-gating loss, or PF-level management intervention. Others are counters, status latches, command bits, self-clearing controls, or clear-on-write status fields. This generated header does not encode access permissions, reset values, polling requirements, clear semantics, or required ordering; those rules live in hardware documentation and in the sequencing of the AMDGPU/KFD consumers.

## Dependencies And Integration Points

This chunk depends on the GC 12.0.0 register set remaining synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h` supplies matching register offsets for the fields named here.
- AMDGPU field helpers in the broader driver expect each `__SHIFT`/`_MASK` pair to match the hardware bit layout.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v12_0.c` uses the GCVM field macros for cache setup, context setup, fault decoding, invalidate request construction, aperture setup, and hub spacing calculations.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v12_0.c` includes this header and programs golden values for `GC_EA_CPWD_*`, `GC_EA_SE_*`, and `GCVM_L2_*` registers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v12.c` includes this header for compute queue descriptor fields such as HQD, CP, and compute state macros, with this chunk contributing compute static-thread and shader-resource field definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v12.c` includes this header for queue-manager setup, and the adjacent v12.1 implementation shows the same GCVM context retry bit pattern for XNACK.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc24.c`, `mes_v12_0.c`, `sdma_v7_0.c`, `gfx_v12_0.c`, and `amdgpu_amdkfd_gfx_v12.c` include this generated header as part of GC 12 platform integration.
- `amdgpu_reg_gc_cac_rd32`/`amdgpu_reg_gc_cac_wr32`, exposed through `RREG32_GC_CAC` and `WREG32_GC_CAC`, integrate with the `GC_CAC_IND_INDEX`/`GC_CAC_IND_DATA` indirect register access pattern.

Runtime integration points include graphics hub initialization, VMID/context programming, page-table setup, GPUVM invalidation, page-fault reporting, retry/XNACK policy, KFD process queue state, compute CU masking, IMU/RLC golden-register programming, SR-IOV PF/VF aperture and active function handling, throttling/power telemetry, and diagnostic register dumps.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong bit shift or mask compiles cleanly but causes driver writes to modify the wrong hardware bits or driver reads to decode fault/status fields incorrectly.
- The chunk starts mid-register at `COMPUTE_REQ_CTRL`; the first fields of that register are in the previous chunk. Any per-register review must merge both chunks before treating `COMPUTE_REQ_CTRL` coverage as complete.
- The chunk ends mid-family at `GCVM_INVALIDATE_ENG2_SEM`; later invalidate engine semaphores, requests, acknowledgements, and address ranges continue in following lines/chunks.
- Repeated fields are easy to mis-index. The per-SE compute masks, 16 compute user-data registers, SE0-SE3 CAC aggregators, multiple CAC weight tables, GCVM contexts 0-15, and invalidate engines rely on stable numbering and identical field layouts.
- GCVM context bit positions are security and reliability sensitive. Incorrect retry/default/interrupt bits can convert recoverable VM faults into hangs, hide page faults, disable fault interrupts, or break XNACK behavior.
- `GCVM_L2_PROTECTION_FAULT_STATUS_LO32` decoding is user-visible during GPU fault reporting. Incorrect `CID`, `VMID`, `VF/VFID`, `PRT`, `UCE`, permission, mapping, or read/write fields can mislead debugging and automated recovery.
- Cache and invalidate fields have ordering-sensitive behavior. Incorrect `GCVM_L2_CNTL*`, `GCVM_INVALIDATE_CNTL`, or invalidate semaphore/request/ack fields can leave stale PTE/PDE data, trigger intermittent VM faults, or stall the graphics hub.
- PF-only CAC/EDC/DIDT/PWRBRK controls affect power, throttling, and reliability telemetry. Exposing or programming them incorrectly can affect virtualization isolation, performance, thermal behavior, or fault evidence.
- EA/SDP credit and priority fields are fabric-performance sensitive. Bad masks for tag/credit reserves or VC mapping can produce deadlock-like stalls, traffic starvation, or performance cliffs.
- Some registers are status, latch, clear, or self-clearing command registers, but this file only describes bit layout. Consumers must not infer read/write safety from the existence of a mask.
- Nearby GC 12.1 and older GC headers use similar names but may not share identical layouts. Cross-generation code must include the correct ASIC-specific header.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware integration:

- Build AMDGPU/KFD configurations that include GC 12.0.0 support. Missing or malformed macros should surface in `gfxhub_v12_0.c`, `imu_v12_0.c`, `gfx_v12_0.c`, KFD MQD/queue manager code, MES, SDMA, and SOC24 integration.
- Mechanically compare every shift and mask in this chunk against AMD's authoritative GC 12.0.0 register database.
- Cross-check that every field family here has matching register offsets in `gc_12_0_0_offset.h`, especially chunk-boundary families such as `COMPUTE_REQ_CTRL` and `GCVM_INVALIDATE_ENG*`.
- Verify repeated-family consistency for `COMPUTE_USER_DATA_0..15`, `COMPUTE_STATIC_THREAD_MGMT_SE4..SE8`, CAC weight groups, `GCVM_CONTEXT0_CNTL..GCVM_CONTEXT15_CNTL`, and invalidate engine semaphores.
- Exercise GC 12 graphics hub initialization and teardown, checking that `GCVM_L2_CNTL*`, context controls, system aperture, default fault address, and identity aperture programming match expected register dumps.
- Exercise GPUVM invalidation under graphics, compute, SDMA, and KFD workloads while watching invalidate semaphores, request/ack progress, page-table update visibility, and absence of stale PTE/PDE faults.
- Trigger or inject VM faults where possible and confirm `GCVM_L2_PROTECTION_FAULT_STATUS_*` decoding reports the expected client ID, VMID, access type, VF/VFID, PRT, and UCE state.
- Run KFD compute queues with CU masks, debugger/CWSR paths, user-data payloads, and XNACK on/off process settings to validate compute and GCVM context fields.
- Run IMU/RLC golden-setting initialization and compare EA/SDP and GCVM programmed values against reference hardware traces.
- In SR-IOV configurations, validate PF/VF behavior around shared aperture registers, active function ID fields, PF-only CAC/throttle controls, and fault reporting isolation.
- Monitor power/throttle telemetry under high-load workloads to catch regressions in CAC/EDC/DIDT/PCC/PWRBRK status, counters, hysteresis, and throttle pattern fields.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002572`. The final per-file research should merge it with neighboring chunks for complete `gc_12_0_0_sh_mask.h` coverage. The previous chunk owns the beginning of `COMPUTE_REQ_CTRL`, while the next chunk continues the GCVM invalidate-engine register family after `GCVM_INVALIDATE_ENG2_SEM`.

### subset-b-002573: lines 10045-12529

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 10045-12529

## Scope

This chunk is a large middle section of the generated AMD GC 12.0.0 shader-mask header. It contains C preprocessor constants only: no functions, structs, enums, includes, storage, locks, or executable branches are introduced here. The macros define bit shifts and masks for register fields used by the GC virtual-memory hub, GCVM L2 performance counters and translation controls, and graphics/compute command-processor registers.

The range starts in the middle of the `GCVM_INVALIDATE_ENG2_SEM` definition: line 10045 contains only the `SEMAPHORE_MASK`, while the matching `SEMAPHORE__SHIFT` is in the previous chunk. It then covers:

- `GCVM_INVALIDATE_ENG3_SEM` through `GCVM_INVALIDATE_ENG17_SEM`.
- `GCVM_INVALIDATE_ENG0_REQ` through `GCVM_INVALIDATE_ENG17_REQ`.
- `GCVM_INVALIDATE_ENG0_ACK` through `GCVM_INVALIDATE_ENG17_ACK`.
- `GCVM_INVALIDATE_ENG0_ADDR_RANGE_LO32/HI32` through engine 17.
- `GCVM_CONTEXT0..15_PAGE_TABLE_BASE_ADDR`, `START_ADDR`, and `END_ADDR` low/high field masks.
- Per-PF/VF GCVM L2 PTE cache fragment-size fields for the global register and contexts 0 through 15.
- GCVML2, GCMC VM L2, and GCUTCL2 performance-counter result, select, mode, and configuration fields.
- GCUTCL2/GCVM IOMMU, translation-bypass, translation-assist, translation-fault, and compression override controls.
- Command-processor and CPC fields for CU mask programming, EOP queue wait, clock-gating sync, interrupt info/status/control, virtualization status, PASID, GFX errors, UTCL1 controls and errors, ring-buffer programming, doorbells, priorities, debug registers, ECC/EDC reporting, suspend/resume, VMID reset/preempt/status, context save, and DDID control.

The range ends at the `//CP_DDID_CNTL` comment on line 12529. The `CP_DDID_CNTL__*` field definitions that follow that comment are outside this chunk and should be covered by the next chunk.

Although this repository is under a `ceph-client` source tree, this file is AMDGPU DRM hardware metadata for the GC 12.0.0 graphics IP block, not distributed-filesystem code.

## Purpose

`gc_12_0_0_sh_mask.h` is generated register-layout metadata. Each `REGISTER__FIELD__SHIFT` macro tells callers how far to shift a logical field, and each `REGISTER__FIELD_MASK` macro identifies the occupied bits in the 32-bit register value. AMDGPU code combines these macros through helpers such as `REG_SET_FIELD()` and raw mask operations before writing MMIO registers through `WREG32_SOC15*()` helpers, or decodes readback values through matching `REG_GET_FIELD()`-style usage.

The GCVM portion of this chunk supports graphics VM invalidation and address-space programming. Driver code builds invalidation requests by setting per-VMID request bits, flush type, L2 PTE/PDE invalidation bits, L1 PTE invalidation, optional logging, protection-fault address clearing, and optional 4 KiB-only invalidation fields. It also programs per-engine invalidation address ranges and per-context page-table base/start/end address registers. The companion offset header supplies the register addresses; this header supplies the field layout.

The GCVML2/GCMC/GCUTCL2 performance-counter portion provides selector, mode, counter result, and result-control fields for low-level performance collection around graphics VM L2 and UTCL2. The translation-control fields cover VMID translation bypass, GPU host translation enable, GPUVA VMID translation assist, IOMMU control/performance optimization, translation fault control, and compression-enable override behavior.

The CP/CPC portion supports command-processor setup and observability. GC v12 graphics code uses `CP_RB0_CNTL` masks to size and configure the graphics ring buffer, `CP_INT_CNTL_RING0` masks to enable or disable timestamp, generic, busy/empty, idle, privileged-register, privileged-instruction, and opcode-error interrupts, and CPC interrupt masks for KFD compute queue interrupt enablement. Other fields in this chunk define the bit layout for ring pointers, doorbell ranges, queue priorities, debug/status registers, fatal-error and ECC reporting, suspend/resume context save, VMID reset/preempt/status, and DDID controls.

## Important APIs, Types, And Macros

There are no callable APIs or C data types in this chunk. The exported interface is the macro naming contract consumed by AMDGPU and KFD source files that include `gc/gc_12_0_0_sh_mask.h`.

Important macro families include:

- `GCVM_INVALIDATE_ENGn_SEM__SEMAPHORE_MASK` and `GCVM_INVALIDATE_ENGn_SEM__SEMAPHORE__SHIFT` for invalidation-engine ownership/semaphore fields. This chunk contains a partial engine-2 entry plus full engine-3 through engine-17 entries.
- `GCVM_INVALIDATE_ENGn_REQ__PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, `INVALIDATE_L2_PTES`, `INVALIDATE_L2_PDE0/1/2`, `INVALIDATE_L1_PTES`, `CLEAR_PROTECTION_FAULT_STATUS_ADDR`, `LOG_REQUEST`, and `INVALIDATE_4K_PAGES_ONLY` fields. These are repeated for engines 0 through 17.
- `GCVM_INVALIDATE_ENGn_ACK__PER_VMID_INVALIDATE_ACK` and `GCVM_INVALIDATE_ENGn_ACK__PAGE_TABLE_ID` fields for invalidation completion/status.
- `GCVM_INVALIDATE_ENGn_ADDR_RANGE_LO32__ADDR_RANGE_LO32`, `__SYSTEM_ACCESS_MODE`, and `__ENABLE` plus `GCVM_INVALIDATE_ENGn_ADDR_RANGE_HI32__ADDR_RANGE_HI32` for range-limited invalidations.
- `GCVM_CONTEXTn_PAGE_TABLE_BASE_ADDR_LO32/HI32`, `START_ADDR_LO32/HI32`, and `END_ADDR_LO32/HI32` fields for contexts 0 through 15. These expose low/high halves of page-table base and virtual-address range registers.
- `GCVM_L2_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` and `GCVM_L2_CONTEXTn_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` fields for PF/VF-specific PTE cache fragment sizing. The repeated fields are `VF0`, `VF1`, and `VF2`.
- `GCVML2_PERFCOUNTER2_0_SELECT`, `GCVML2_PERFCOUNTER2_1_SELECT`, `*_SELECT1`, and `*_MODE` fields for selecting up to four events, counter modes, performance modes, and counter-mode options.
- `GCMC_VM_L2_PERFCOUNTERn_CFG`, `GCUTCL2_PERFCOUNTERn_CFG`, and their result-control registers for selecting sources, increments, client IDs, read counts, clear behavior, and pulse width.
- `GCUTCL2_TRANSLATION_BYPASS_BY_VMID`, `GCVM_IOMMU_GPU_HOST_TRANSLATION_ENABLE`, `GCUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL`, `GCVM_IOMMU_CONTROL_REGISTER`, `GCVM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER`, `GCUTC_TRANSLATION_FAULT_CNTL0/1`, and `GCUTCL2_COMP_EN_OVERRIDES`.
- `CP_CU_MASK_ADDR_LO/HI` and `CP_CU_MASK_CNTL` for command-processor compute-unit mask location and control.
- `CP_RB0_CNTL` and `CP_RB_CNTL`, with fields such as `RB_BUFSZ`, `RB_BLKSZ`, `BUF_SWAP`, `MIN_AVAILSZ`, `MIN_IB_AVAILSZ`, `CACHE_POLICY`, `RB_NO_UPDATE`, and `RB_RPTR_WR_ENA`.
- `CP_RB0_BASE`, `CP_RB_BASE`, `CP_RB0_BASE_HI`, `CP_RB0_WPTR`, `CP_RB_WPTR`, `CP_RB0_RPTR_ADDR`, `CP_RB_RPTR_ADDR`, and high-half variants for graphics ring-buffer base, write pointer, and read-pointer writeback addresses.
- `CP_INT_CNTL`, `CP_INT_STATUS`, `CP_INT_CNTL_RING0`, `CP_INT_STATUS_RING0`, `CPC_INT_CNTL`, and `CPC_INT_STATUS` for command-processor interrupt enables and status bits.
- `CP_GFX_ERROR`, `CP_FATAL_ERROR`, `CP_ECC_FIRSTOCCURRENCE`, `CP_ECC_FIRSTOCCURRENCE_RING0`, `GB_EDC_MODE`, and `CC_GC_EDC_CONFIG` for error and EDC/ECC reporting.
- `CPG_UTCL1_CNTL`, `CPC_UTCL1_CNTL`, `CPF_UTCL1_CNTL`, `CPG_UTCL1_ERROR`, and `CPC_UTCL1_ERROR` for command-processor UTCL1 controls and error observability.
- `CP_VIRT_STATUS`, `CPC_INT_PASID`, `CP_RB_VMID`, `CP_ME0_PIPE0_VMID`, `CP_VMID_RESET`, `CP_VMID_PREEMPT`, and `CP_VMID_STATUS` for virtualization, PASID/VMID attribution, reset, preemption, and status.
- `CP_ME0_PIPE_PRIORITY_CNTS`, `CP_RING_PRIORITY_CNTS`, `CP_ME1_PIPE_PRIORITY_CNTS`, `CP_ME0_PIPE0_PRIORITY`, `CP_RING0_PRIORITY`, `CP_ME1_PIPE0_PRIORITY`, and `CP_ME1_PIPE1_PRIORITY` for queue and pipe priority programming.
- `CP_DEBUG`, `CP_DEBUG_2`, `CP_CPF_DEBUG`, `CP_CPC_DEBUG`, `CP_ME3_INT_STAT_DEBUG`, and `CP_ME1_INT_STAT_DEBUG` for debug snapshots.
- `CPC_SUSPEND_CTX_SAVE_BASE_ADDR_LO/HI`, `CPC_SUSPEND_CTX_SAVE_CONTROL`, stack/state offsets and sizes, `CP_SUSPEND_RESUME_REQ`, `CP_SUSPEND_CNTL`, and `CP_IQ_WAIT_TIME3` for CPC/CP suspend and resume handling.
- `CPC_DDID_BASE_ADDR_LO/HI`, `CP_DDID_BASE_ADDR_LO/HI`, and `CPC_DDID_CNTL`. The chunk reaches the `CP_DDID_CNTL` comment but not its field definitions.

Representative direct consumers in this repository include:

- `amdgpu/gfxhub_v2_1.c`, where `gfxhub_v2_1_get_invalidate_req()` builds a `GCVM_INVALIDATE_ENG0_REQ` value with `REG_SET_FIELD()` and where hub initialization records the offsets and spacing for `GCVM_INVALIDATE_ENG0_SEM`, `REQ`, `ACK`, and address-range registers.
- `amdgpu/gfxhub_v2_1.c`, where `gfxhub_v2_1_program_invalidation()` writes all 18 invalidation engines' address ranges using `mmGCVM_INVALIDATE_ENG0_ADDR_RANGE_LO32/HI32` plus the generated engine address stride.
- `amdgpu/gfx_v12_0.c`, where graphics-ring setup uses `CP_RB0_CNTL` field macros to write ring-buffer size and block size before programming base, read pointer, and write pointer registers.
- `amdgpu/gfx_v12_0.c`, where interrupt handlers use `CP_INT_CNTL_RING0` fields for context busy/empty, compare busy, graphics idle, timestamp, generic, privileged register, opcode error, and privileged instruction interrupts.
- `amdgpu/amdgpu_amdkfd_gfx_v12.c`, where KFD enables CPC timestamp and opcode-error interrupts using `regCPC_INT_CNTL` plus the corresponding CP interrupt-mask bits.
- `amdkfd/kfd_mqd_manager_v12.c` and `amdkfd/kfd_device_queue_manager_v12.c`, which include this header for GC v12 queue-management field definitions used alongside `v12_structs.h` and `soc24_enum.h`.

## Control Flow

This header has no runtime control flow. The direct behavior is compile-time macro substitution.

The implied runtime flow for GCVM invalidation is:

1. GC v12 gfxhub initialization records the base offsets for context page-table registers and invalidation engine 0, plus register distances between contexts and engines.
2. The driver programs page-table base/start/end registers for each VM context using the offset header for addresses and this header's field layout for packing values when field helpers are used.
3. The driver initializes invalidation address ranges for engines 0 through 17, commonly to a broad range when full-range invalidations are expected.
4. On a TLB/cache invalidation request, the driver builds a `GCVM_INVALIDATE_ENG0_REQ` value with the requested VMID bit, flush type, L2 PTE/PDE invalidation bits, L1 PTE invalidation bit, and related controls.
5. The VM hub invalidation code writes the selected engine request register, waits for the corresponding `ACK` state through the vmhub machinery, and uses semaphore/engine spacing to coordinate repeated requests.

The implied flow for GC v12 graphics-ring setup is:

1. `gfx_v12_0` switches to the target graphics pipe under SRBM serialization.
2. The driver computes the ring-buffer size as a power-of-two log value.
3. `REG_SET_FIELD(0, CP_RB0_CNTL, RB_BUFSZ, rb_bufsz)` and `REG_SET_FIELD(..., RB_BLKSZ, rb_bufsz - 2)` pack the ring-control value.
4. The driver writes `regCP_RB0_CNTL`, resets `CP_RB0_WPTR`/`CP_RB0_WPTR_HI`, programs read-pointer writeback addresses, write-pointer polling addresses, and writes ring base low/high values.
5. Later runtime ring updates use doorbells and write-pointer registers defined in this generated register family.

The implied flow for command-processor interrupt programming is:

1. The driver maps a ME/pipe to the proper CP interrupt-control register, such as `regCP_INT_CNTL_RING0`.
2. It reads the register, updates selected fields with `REG_SET_FIELD()` using `CP_INT_CNTL_RING0__*` masks and shifts, then writes the value back.
3. Different IRQ sources toggle different fields: timestamp/generic interrupts for fence/event paths, busy/empty/idle signals for scheduling and queue state, and privileged-register/opcode/privileged-instruction interrupts for fault reporting.
4. KFD compute paths can select a MEC/pipe through SRBM and write CPC interrupt-control bits for queue-level timestamp and opcode-error handling.

Performance-counter and debug-control macros follow similar write-read sequences: a consumer programs select/config/mode fields, triggers or lets counters run, then reads low/high result registers and decodes result-control/status fields. This chunk only supplies the bit layout; it does not implement PMU scheduling, counter ownership, reset sequencing, or user-space exposure.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe fields in hardware registers whose state is owned by the GPU and by the AMDGPU runtime.

GCVM page-table base/start/end fields represent persistent per-context hardware configuration while the device is initialized and while a VM context remains active. Wrong masks here can redirect GPU virtual-address translation, expand or shrink an address range incorrectly, or cause VM faults under otherwise valid workloads.

GCVM invalidation request, semaphore, ACK, and address-range fields are transient synchronization and cache-control state. Request bits initiate hardware work; ACK bits report completion or status; semaphore fields coordinate engine use. The address-range registers may persist as part of invalidation-engine configuration until reprogrammed. A stale or incorrectly packed request can leave old PTE/PDE translations in GCVM L1/L2 caches, which is a high-impact correctness failure because subsequent command-processor or shader memory accesses can use obsolete mappings.

Performance-counter select, mode, and config fields persist while a profiling session is active. Result low/high registers are hardware-updated observations. Result-control fields can clear, pulse, or select result behavior; incorrect writes can silently corrupt profiling data or interfere with another owner of the counter block.

Translation-bypass, IOMMU, GPUVA translation-assist, translation-fault, and compression override fields alter memory-translation behavior. These are not ordinary debug bits. They can change whether VMIDs bypass translation, whether GPU host translation is enabled, how faults are controlled/reported, and whether compression behavior is overridden. A bad field definition or cross-generation mismatch can break isolation, fault attribution, or host-memory access behavior.

CP ring-buffer control and pointer fields are persistent command-processor configuration. `CP_RB0_CNTL`, base address, read-pointer writeback address, write pointer, doorbell range, and VMID fields define how the hardware consumes commands from memory. Incorrect `RB_BUFSZ`, `RB_BLKSZ`, `RB_RPTR_WR_ENA`, base high/low, or pointer masks can lead to command stream stalls, reads from the wrong memory, lost fences, or GPU resets.

Interrupt control fields persist until disabled or reset. Interrupt status fields are hardware-reported and may be write-to-clear or otherwise side-effected depending on the register. These masks are used around scheduling, fence/event signaling, KFD queue errors, privileged access faults, opcode errors, ECC/EDC errors, and debug notifications.

Suspend/resume and context-save fields persist across CP/CPC suspend windows and are tied to GPU queue preemption and recovery state. Address, offset, size, policy, and enable bits must be packed exactly or context save areas and workgroup state can be misaddressed.

Debug, ECC, fatal-error, UTCL1 error, PASID, VMID, preempt, and status registers expose live hardware state. Readback values can change while queues run. Diagnostic consumers should treat them as snapshots unless they have quiesced, halted, or reset the relevant engine.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.0.0 register family being used consistently:

- `gc_12_0_0_offset.h` supplies the corresponding `reg...` and `mm...` register offsets. This chunk supplies only field shifts and masks.
- `soc24_enum.h` supplies enum values for some GC v12/SOC24 register fields, including DDID-related modes and sizes.
- `soc15_common.h` and AMDGPU register helpers provide `REG_SET_FIELD()`, `REG_GET_FIELD()`-style field manipulation and `RREG32_SOC15*()`/`WREG32_SOC15*()` MMIO access.
- `amdgpu/gfxhub_v2_1.c` integrates GCVM invalidation masks with the generic `amdgpu_vmhub` layout, engine spacing, context spacing, invalidation request construction, and fault-control plumbing.
- `amdgpu/gfx_v12_0.c` integrates CP ring, interrupt, debug, error, power, and queue fields with graphics-engine initialization, IRQ state transitions, fence signaling, queue scheduling, and reset recovery.
- `amdgpu/amdgpu_amdkfd_gfx_v12.c` integrates CPC interrupt fields with KFD compute queue handling under SRBM engine selection.
- `amdkfd/kfd_mqd_manager_v12.c` and `amdkfd/kfd_device_queue_manager_v12.c` integrate GC v12 mask definitions with MQD setup, CU masks, queue properties, SDMA/compute queue setup, and process-device cache policy.
- Runtime consumers rely on include selection matching the active ASIC/IP generation. Logical register names such as `CP_RB0_CNTL`, `CP_INT_CNTL_RING0`, and `GCVM_INVALIDATE_ENG0_REQ` recur across GC versions, but masks can vary by generation.

The chunk is intentionally low level. It does not decide which VMID to invalidate, how long to poll, which CP interrupt sources are enabled for a given workload, how KFD prioritizes queues, how performance counters are multiplexed, or how debug/status values are presented to users. Those policy decisions live in AMDGPU, KFD, PMU, and debug code.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong mask or shift compiles cleanly but packs or decodes the wrong hardware bits.
- The chunk starts mid-register and ends before the `CP_DDID_CNTL__*` field definitions. File-level research must merge adjacent chunks to avoid treating `GCVM_INVALIDATE_ENG2_SEM` or `CP_DDID_CNTL` as complete in this chunk alone.
- The invalidation-engine families are repeated for 18 engines. Copy/paste or generation errors in a single engine's `REQ`, `ACK`, or address-range fields can affect only some VM hub invalidation paths, making failures intermittent.
- `PER_VMID_INVALIDATE_REQ` and `PER_VMID_INVALIDATE_ACK` are 16-bit VMID bitmaps. Callers must avoid shifting beyond the represented VMID width and must preserve the expected VMID-to-bit mapping.
- Invalidation address ranges are split into low/high registers with enable and system-access-mode fields in the low half. Mis-pairing high/low fields or leaving range enable in the wrong state can make invalidation too broad, too narrow, or inactive.
- Page-table base/start/end fields are split across low/high registers and are page-aligned. Incorrect masking of low address bits can produce subtle VM faults or aliasing rather than an immediate build failure.
- Performance-counter fields include selectors, modes, clear controls, pulse widths, and client IDs. A counter may appear to work while counting the wrong event or wrong client if only selector packing is wrong.
- Translation-bypass and IOMMU control fields can affect VM isolation and fault behavior. These fields should not be casually reused from another GC generation.
- CP ring-buffer fields are sensitive during initialization. Wrong `RB_BUFSZ`/`RB_BLKSZ` packing can make hardware consume the wrong ring size, while wrong pointer high/low masks can break 64-bit GPU addresses.
- Interrupt enable/status macros share many similarly named fields across `CP_INT_CNTL`, `CP_INT_STATUS`, `CP_INT_CNTL_RING0`, `CP_INT_STATUS_RING0`, `CPC_INT_CNTL`, and `CPC_INT_STATUS`. Mixing status masks with control registers or generic CP masks with ring-specific masks can suppress interrupts or create interrupt storms.
- The KFD GC v12 code writes `regCPC_INT_CNTL` using timestamp and opcode-error mask names from the CP interrupt ring layout. That pattern relies on compatible bit positions; any generated-layout divergence must be reviewed carefully.
- Debug, fatal-error, ECC/EDC, PASID, VMID, and preempt/status readbacks are volatile. Interpreting them without quiescing the relevant engine can create inconsistent diagnostic snapshots.
- Suspend/resume context save fields combine addresses, offsets, sizes, policy, and enable bits. Off-by-alignment errors can corrupt context save buffers or make preemption/resume fail only under load.
- Doorbell range and write-pointer-poll fields are security- and stability-sensitive because they bound user/queue signaling into the command processor.
- Cross-generation copy/paste is risky. GC v9/v10/v11/v12 headers share names but are not interchangeable; the active `gc_12_0_0_*` offset and mask headers must be paired.

## Test Signals

Useful validation is a mix of generated-data checks, build coverage, and hardware/runtime behavior:

- Build AMDGPU and KFD configurations that include `gc/gc_12_0_0_sh_mask.h`, especially `gfx_v12_0.c`, `gfxhub_v2_1.c`, `amdgpu_amdkfd_gfx_v12.c`, `kfd_mqd_manager_v12.c`, and `kfd_device_queue_manager_v12.c`. This catches missing or renamed macros but not wrong numeric masks.
- Mechanically compare this chunk against AMD's authoritative GC 12.0.0 register database, with special attention to repeated engine/context families, split low/high registers, and fields that recur across CP/CPC interrupt control and status registers.
- Validate that `gc_12_0_0_offset.h` and `gc_12_0_0_sh_mask.h` are from the same generated source version. Offset/mask mismatches are especially dangerous for `GCVM_INVALIDATE_ENGn_*`, `GCVM_CONTEXTn_*`, `CP_RB0_*`, and interrupt registers.
- Exercise VM map/unmap, BO eviction, VM fault, GPU reset, and multi-VMID workloads on GC v12 hardware. Healthy signals include completed TLB invalidations, no stale-mapping faults after unmap/remap, correct fault attribution, and no invalidation timeouts.
- Check invalidation-engine programming through debug traces or register dumps: engine address ranges should match the intended broad or targeted invalidation range, and ACK bitmaps should correspond to requested VMIDs.
- Run graphics-ring initialization and command submission tests. Expected signals include correct ring pointer writeback, advancing write/read pointers, completed fences, no unexpected command processor hangs, and stable operation across suspend/resume or reset.
- Exercise IRQ enable/disable paths for timestamp, generic, idle, busy/empty, privileged-register, privileged-instruction, and opcode-error interrupts. Regressions show up as missed fences/events, unexpected IRQ floods, or lost fault reports.
- Run KFD compute queue tests with timestamp and opcode-error handling enabled. Signals include correct queue error reporting, no unexpected CPC interrupt masking, and stable queue teardown/recreation.
- Run performance-counter collection for GCVML2/GCMC/GCUTCL2 blocks and verify event selection, clear behavior, result low/high pairing, and client/source selection against known workloads.
- Test IOMMU/GPUVA translation-assist and translation-fault paths where supported. Expected behavior includes correct fault status, no unauthorized bypass, and correct behavior under host-memory translation modes.
- Exercise CP/CPC suspend, resume, preemption, and VMID reset paths. Useful signals include successful context save/restore, sane `CP_VMID_STATUS` values, no stuck preempt status, and no corrupted context-save buffers.
- Inspect GPU hang/debug dumps for plausible `CP_GFX_ERROR`, `CP_FATAL_ERROR`, `CP_DEBUG*`, `CP_CPF_DEBUG`, `CP_CPC_DEBUG`, UTCL1 error, PASID, VMID, and ECC/EDC values.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002573`. It covers lines 10045-12529 of `gc_12_0_0_sh_mask.h`. The previous chunk contains the opening `GCVM_CONTEXTS_DISABLE` tail plus complete `GCVM_INVALIDATE_ENG0_SEM`, `ENG1_SEM`, and most of `ENG2_SEM`. The next chunk begins with the `CP_DDID_CNTL__*` fields that are introduced by the final comment in this chunk. The final per-file research should merge those adjacent pieces with this chunk to present a complete GC 12.0.0 field-mask map.

### subset-b-002574: lines 12530-15146

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 12530-15146

## Scope

This chunk is a generated AMD GC 12.0.0 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `__SHIFT` value and a matching `__MASK` value used by AMDGPU register helpers to compose or decode 32-bit register values. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines begin in the middle of the command processor DDID control family, with `CP_DDID_CNTL` field masks immediately preceding the `CP_GFX_DDID_*` counters. The chunk then covers graphics HQD/MQD queue state, compute HQD/MQD queue state, CP DMA watch/debug controls, CP busy/UTCL1/reset controls, graphics-draw context registers, CP ME/MEC reset and halt controls, unmapped queue tracking, PF-only HPD/GCR controls, GFXU CP counters and scratch/atomic/append/DMA registers, ME coherence controls, RLC GPM counters, GRBM instance selection, and VGT/GE draw and primitive fields. It ends at the `GE_GS_FAST_LAUNCH_WG_DIM` comment; that register's field definitions continue in the next adjacent chunk.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for the GC 12.0.0 graphics IP and is not Ceph filesystem code.

## Purpose

`gc_12_0_0_sh_mask.h` supplies the bit layouts for GC 12.0.0 registers. Driver code pairs these masks with register addresses from the matching `gc_12_0_0_offset.h` header and generated/default values used by GC 12 runtime code. Consumers normally use `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, `RREG32_SOC15`, KFD queue loading code, command-packet emission, or debug/perf code so register fields can be packed and decoded without hand-coded bit positions.

This chunk is centered on queue execution and draw/dispatch plumbing:

- Graphics CP queue state: DDID counts, HPD status/control/fence values, MQD base/control, GFX HQD active/VMID/priority/quantum/ring base/read/write pointers, write-pointer polling, doorbells, dequeue/mapped state, queue-manager policy, HQ status/control, and GFX HQD-to-MQD handshakes.
- Compute CP queue state: HPD UTCL1 controls/errors, compute MQD base/control, compute HQD active/VMID/persistent state/priority/quantum/PQ/IB/EOP/context-save/GDS/error/AQL/DDID/dequeue fields.
- CP debug and diagnostic state: DMA watch address/mask/control sets, watch status, PFP/MEC JT status, busy hysteresis, doorbell clear/hit vectors, ring active/status, RCIU CAM data phases, GPU timestamp offset, SDMA completion and checksum/status fields, CP soft reset and CPC graphics controls.
- Per-draw graphics context state: coherence destination bases, perfmon context enable, pipe/ring/VMID context registers, VGT DMA/draw/event/tessellation/shader-stage/streamout fields, and reserved context/config registers.
- PF/VF and PF-only CP/GCR control state: MEC/ME reset and halt controls, unmapped queue bitmaps and doorbell status, PF/VF GRBM graphics control, CP fetcher/DFY data path, PF-only HPD ROQ/status, GCR general/target/command/spare controls, and PMM interrupt/flush controls.
- GFXU CP user-facing registers: EOP done address/data/fence, pipe statistics address/control, many 64-bit pipeline invocation counters, scratch registers and scratch atomics, append/fence address/data, CP atomic preop registers, CP ME memory copy/DMA source/destination/command fields, wait timeout, DMA controls, IB/preamble offsets, command buffer sizes, draw/dispatch/index indirect addresses, sample status, and ME coherence commands.
- Late graphics register families: RLC GPM performance counters, `GRBM_GFX_INDEX` broadcast/instance selection, primitive/index/count registers, GE throttling/control/user VGPR/stereo/VRS fields, and primitive ID reuse control.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register address symbols live in the companion offset header, commonly as `reg...` or `mm...` names matching these register names.
- AMDGPU callers use the masks through helpers such as `REG_SET_FIELD` and `REG_GET_FIELD`; direct bit tests also occur for single-bit status fields such as `CP_HQD_ACTIVE__ACTIVE_MASK`.

The major macro families in this slice are:

- `CP_GFX_DDID_*` and `CP_HQD_DDID_*`: inflight, read pointer, write pointer, and delta report count fields for DDID accounting on graphics and compute HQDs.
- `CP_GFX_HPD_*`, `CP_HPD_*`, `CP_HPD_MES_ROQ_OFFSETS`, and `CP_HPD_ROQ_OFFSETS`: queue slot status, mapped queue selection, suspend/freeze/force controls, OSPRE fence address/data fields, and request-offset layout.
- `CP_GFX_MQD_*`, `CP_GFX_HQD_*`, `CP_MQD_*`, and `CP_HQD_*`: MQD/HQD base addresses, active bits, VMID, priority, quantum, persistent state, ring/PQ base and pointer registers, doorbell controls, PQ/IB/EOP controls, context-save state, GDS resource state, AQL controls, dequeue request/status, and error status.
- `CP_RB_*` and `CP_HQD_PQ_*`: ring buffer and packet queue write-pointer polling, doorbell offset/enable/hit/source/drop fields, buffer sizing, block sizing, privilege/KMD/TMZ/cache controls, and read/write pointer report addresses.
- `CP_DMA_WATCH{0..3}_*` and `CP_DMA_WATCH_STAT*`: watchpoint address/mask/control and status fields for CP DMA diagnostics.
- `CP_CPC_*`, `CP_CPF_*`, `CP_CPG_*`, `CP_SD_CNTL`, and `CP_SOFT_RESET_CNTL`: busy hysteresis, UTCL1 status, soft reset, VMID check, SDMA command checksum, ECC/fault-status forwarding, and CPC graphics enable/status controls.
- `COHER_DEST_BASE*`, `CP_ME_COHER_*`: coherence destination base, size, control, and status fields for CP ME coherence operations.
- `VGT_*` and `GE_*`: draw initiator, DMA index base/size/type, event initiator/address, shader-stage enablement, tessellation parameters/distribution, LS/HS config, primitive type, index type, primitive/index/instance counts, geometry throttling, GE control, user VGPRs, stereo, primitive ID, and VRS fields.
- `CP_MEC_CNTL` and `CP_ME_CNTL`: reset, disable, invalidate, halt, and step fields for MEC/ME/PFP/CE pipelines.
- `CP_UNMAPPED_QUEUE0..63`, `CP_UNMAPPED_DOORBELL`, and `CP_UNMAPPED_QUEUE_BANK*`: unmapped queue and doorbell status bitmaps used by queue management and virtualization paths.
- `GCR_GENERAL_CNTL`, `GCR_TARGET_DISABLE`, `GCR_CMD_STATUS`, and `GCR_SPARE`: GCR/UTCL2 control, target disable/status, command/error/nack status, TLB shootdown VMID, and credit/spare fields.
- `CP_EOP_*`, `CP_PIPE_STATS_*`, `CP_VGT_*_COUNT_*`, `CP_PA_*_COUNT_*`, `CP_SC_*_COUNT_*`: EOP/fence writeback and 64-bit pipeline statistics counters.
- `SCRATCH_REG*`, `SCRATCH_REG_ATOMIC`, and `SCRATCH_REG_CMPSWAP_ATOMIC`: scratch storage plus immediate/id/op encoding for scratch atomic operations.
- `CP_APPEND_*`, `CP_ATOMIC_PREOP_*`, `CP_PFP_ATOMIC_PREOP_*`, and `CP_ME_ATOMIC_PREOP_*`: append/fence memory address/data selection and CP atomic pre-operation fields.
- `CP_DMA_*`, `CP_PFP_IB_CONTROL`, `CP_PFP_LOAD_CONTROL`, `CP_SCRATCH_*`, `CP_RB_OFFSET`, `CP_IB*_OFFSET`, `CP_IB*_PREAMBLE_*`, `CP_*_CMD_ADDR_*`, and command-buffer size/base fields: packet DMA, indirect-buffer, scratch, preamble, and command-buffer plumbing.
- `RLC_GPM_PERF_COUNT_0/1` and `GRBM_GFX_INDEX`: performance event selection by feature/SE/SA/WGP plus GRBM targeted/broadcast register selection.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU and KFD consumers:

1. Select the GC 12.0.0 register headers for the active ASIC generation.
2. Choose a register address from `gc_12_0_0_offset.h` or an SOC15 `reg...` symbol.
3. Read an existing register value or start from a generated default.
4. Use the `__SHIFT`/`__MASK` pairs, usually through `REG_SET_FIELD` or `REG_GET_FIELD`, to pack a field value or extract status.
5. Write the value to hardware, store it in an MQD image, emit it into a command path, or use it while decoding status/debug state.

The graphics queue setup path in `gfx_v12_0.c` is representative. `gfx_v12_0_cp_gfx_set_doorbell()` reads `regCP_RB_DOORBELL_CONTROL`, updates `CP_RB_DOORBELL_CONTROL.DOORBELL_OFFSET` and `DOORBELL_EN`, and writes doorbell range registers. `gfx_v12_0_cp_gfx_resume()` programs ring buffer size, read/write pointers, write-pointer poll addresses, ring base, active state, and then starts the graphics CP. `gfx_v12_0_gfx_mqd_init()` fills a `v12_gfx_mqd` image with `CP_GFX_MQD_CONTROL`, `CP_GFX_HQD_VMID`, `CP_GFX_HQD_QUEUE_PRIORITY`, `CP_GFX_HQD_QUANTUM`, `CP_GFX_HQD_CNTL`, and `CP_RB_DOORBELL_CONTROL` fields from this chunk before the queue is loaded.

The compute queue setup path uses the compute HQD side of this chunk. `gfx_v12_0_compute_mqd_init()` builds a `v12_compute_mqd` with EOP base/control, PQ doorbell control, MQD base/control, PQ base/control, read-pointer report and write-pointer poll addresses, VMID, persistent state, IB control, queue priority, active state, and static thread masks. `gfx_v12_0_kiq_init_register()` then writes the MQD/HQD register image to selected hardware queue registers, optionally dequeues an active queue, resets PQ pointers, and reactivates the HQD.

KFD queue-management code has the same conceptual flow for user queues: select a MEC/pipe/queue, write the range from `CP_MQD_BASE_ADDR` through HQD registers, enable doorbell logic, reconstruct a 64-bit write pointer when needed, start the EOP fetcher by setting `CP_HQD_EOP_RPTR.INIT_FETCHER`, and set `CP_HQD_ACTIVE.ACTIVE`. Queue teardown writes `CP_HQD_DEQUEUE_REQUEST` and polls `CP_HQD_ACTIVE__ACTIVE_MASK` until the queue drains or resets.

For GRBM selection, wave/debug paths write `GRBM_GFX_INDEX` with targeted instance/SA/SE fields, execute a command such as `SQ_CMD`, then restore broadcast writes by setting `INSTANCE_BROADCAST_WRITES`, `SA_BROADCAST_WRITES`, and `SE_BROADCAST_WRITES`. That flow makes the broadcast bits in this chunk critical for avoiding accidental per-instance targeting after debug operations.

Draw, DMA, GCR, perf, and counter fields are generally programmed by command streams, golden-register tables, debugfs/perf tooling, reset paths, and firmware-mediated paths. This header does not encode required ordering, polling, clear-on-read, write-one-to-clear, latching, or reset sequencing; those rules live in AMDGPU engine code, firmware interfaces, and hardware programming guides.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe GPU register fields whose state is owned by hardware, firmware, command streams, and AMDGPU runtime programming.

MQD/HQD and ring fields are persistent queue execution state. Active bits, VMID, queue priority, quantum, buffer base/size, read/write pointers, pointer report addresses, write-pointer poll addresses, doorbells, EOP base/control, IB base/control, context-save offsets/sizes, GDS allocation, and AQL controls remain live until reprogrammed, dequeued, reset, or lost through suspend/resume or GPU reset. Driver code also persists queue images in MQD memory and backup copies, so mask mistakes can survive across restore paths.

Doorbell fields are externally visible synchronization state between CPU/KFD/user queues and the CP. Incorrect offset, enable, source, or range programming can send writes to the wrong queue, drop writes through BIF/drop policy, miss user submissions, or make a disabled queue appear active. `DOORBELL_HIT` and unmapped doorbell/queue registers are diagnostic/status state and may have hardware-specific clear behavior outside this header.

Pointer and address fields often use aligned, shifted, or truncated addresses. Examples include MQD base addresses masked with low bits cleared, HQD/PQ base values derived from GPU addresses shifted by 8, read-pointer report and write-pointer poll addresses aligned to dword boundaries, EOP/context-save addresses, CP append/DMA/source/destination addresses, and ME coherence base/size fields expressed in 256-byte units. Treating all fields as unshifted byte addresses is unsafe.

CP reset/halt/invalidate controls and GCR controls have immediate side effects. `CP_MEC_CNTL`, `CP_ME_CNTL`, `CP_SOFT_RESET_CNTL`, `CP_CPC_GFX_CNTL`, `GCR_GENERAL_CNTL`, `GCR_TARGET_DISABLE`, `GCR_CMD_STATUS`, and `PMM_CNTL2` can stop engines, invalidate caches, alter target routing, trigger TLB shootdowns, disable interrupts, or change request credits. Full-register writes must preserve reserved or unrelated fields unless a documented reset sequence requires otherwise.

Pipeline statistics and performance counters are hardware accumulation state. Low/high counter pairs can be torn if read without a hardware-defined latch/snapshot sequence, and obsolete counter fields such as `CP_SC_PSINVOC_COUNT1_*__OBSOLETE` should not be treated as valid telemetry. RLC GPM counter selection persists while counters are enabled and can perturb or misattribute measurements if feature/SE/SA/WGP/event fields are wrong.

Draw context fields such as VGT DMA base/size/type, draw initiator, shader-stage enablement, tessellation parameters, streamout opaque state, primitive type/index/count, GE throttle/control, user VGPRs, stereo, primitive ID, and VRS are active graphics pipeline state. They are normally command-stream driven and persist in context until overwritten or reset. Bad masks can cause malformed draws, wrong topology, incorrect tessellation/streamout behavior, broken primitive restart, or hangs.

Scratch, append, atomic, DMA, and ME coherence fields can write GPU memory. Incorrect address, size, command, cache-policy, or data-selection fields can corrupt memory, signal the wrong fence, report stale EOP completion, or leave caches incoherent. Many diagnostic/status fields are sticky or latched by hardware; this generated header does not document how to clear them.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.0.0 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h` provides matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_default.h`, where present for this generated family, provides default/reset values that runtime code uses before applying these masks.
- AMDGPU register helpers in the driver tree provide field packing/extraction and MMIO access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_0.c` consumes many of these fields for graphics ring setup, async graphics MQD initialization, compute MQD initialization, KIQ register programming, doorbell range setup, GRBM selection, reset/resume, and firmware/cache operations.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v11.c` is a close KFD queue-management consumer pattern for HQD load, active polling, dequeue, and GRBM index restore; the same HQD macro families are carried into GC 12 paths.
- Firmware and command processor microcode consume MQD/HQD images and command-stream register writes whose layout is defined by these masks.

Integration points include graphics ring resume/start, async graphics queues, compute queue creation/destruction, KIQ/HIQ queue programming, KFD user queue load/unload, SR-IOV PF/VF queue tracking, doorbell routing, EOP/fence signaling, writeback pointer polling, context save/restore, GDS/GWS allocation, AQL dispatch handling, CP DMA and copy operations, indirect buffer preambles, draw and dispatch indirect addresses, pipeline statistics, RLC/GPM perf monitoring, GCR/TLB shootdown and target routing, GRBM per-instance access, wave control/debug, and hang/reset diagnostics.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask compiles cleanly but writes the wrong hardware bits or decodes misleading queue/status state.
- This range starts and ends mid-family. It begins after the `CP_DDID_CNTL` comment and field shifts and ends at the `GE_GS_FAST_LAUNCH_WG_DIM` comment before the actual field definitions. Adjacent chunks are required for complete per-file conclusions.
- Graphics and compute HQD families are similar but not identical. Reusing `CP_GFX_HQD_*` assumptions for `CP_HQD_*`, or vice versa, can break queue setup because PQ, EOP, IB, AQL, context-save, and error fields differ.
- Address fields have mixed alignment contracts. Some masks clear low two bits, some use 8-bit-shifted queue bases, and coherence fields use 256-byte units. Incorrect packing can point hardware at the wrong MQD, ring, EOP buffer, writeback slot, DMA address, fence, or coherence range.
- Queue-size fields encode powers of two in register-specific ways. Runtime code derives values with `order_base_2()` and comments such as EOP size being `2^(EOP_SIZE+1)` dwords; wrong masks produce queues that wrap, overflow, or starve.
- Doorbell offsets and ranges are high risk. Off-by-one or missing shifts can route user submissions to the wrong engine/queue or make a queue unreachable.
- Active/dequeue polling depends on exact status bits. If `CP_HQD_ACTIVE__ACTIVE_MASK`, dequeue request/type bits, or HQ status bits are wrong, teardown can time out, fail to drain waves, or assume an active queue is idle.
- GRBM targeting must be restored after per-instance operations. Missing broadcast bits in `GRBM_GFX_INDEX` can leave subsequent register writes aimed at only one SE/SA/instance.
- GCR and CP reset/halt bits have side effects, and many fields are PF-only or PF/VF scoped. Writing them from the wrong virtualization context can be ineffective or disruptive.
- GFXU counters and status fields include obsolete or split low/high pairs. Consumers need latch/ordering rules not present in the header to avoid torn reads or bogus telemetry.
- Scratch atomic, append, DMA, and ME coherence commands can write memory or signal fences. Incorrect field widths for commands, cache policy, fence size, or addresses can corrupt memory or hide completion/fault information.
- Reserved fields appear throughout this generated region. Read-modify-write paths should preserve reserved and unrelated bits unless the hardware programming sequence says otherwise.

## Test Signals

Useful validation is generated-data consistency, build coverage, and hardware/runtime diagnostics:

- Kernel build coverage for AMDGPU files that include `gc_12_0_0_sh_mask.h`, especially GC 12 graphics, compute/KFD, queue setup, reset/resume, virtualization, debug, and perf paths.
- Mechanical comparison against AMD's authoritative GC 12.0.0 register database to confirm every `__SHIFT` and `__MASK` value in lines 12530-15146.
- Cross-check that all register names in this chunk have matching address macros in `gc_12_0_0_offset.h` and expected defaults in the matching default header where generated.
- Static sanity checks that each mask aligns with its shift, repeated queue/counter families remain structurally consistent, full-width data fields use `0xFFFFFFFFL`, and repeated queue banks/counters are not missing members.
- Graphics ring tests that resume/start the ring, program `CP_RB_DOORBELL_CONTROL`, write/read ring pointers, and verify doorbell submission reaches the expected queue.
- Async graphics MQD tests that initialize `CP_GFX_MQD_CONTROL`, `CP_GFX_HQD_*`, write-pointer poll addresses, doorbell control, queue priority/quantum, and active state, then submit work and recover through suspend/reset.
- Compute/KFD queue tests that create and destroy user queues, load MQD/HQD state, enable doorbells, reconstruct write pointers, start the EOP fetcher, set `CP_HQD_ACTIVE`, dequeue with drain/reset requests, and poll for inactive state without timeouts.
- Doorbell range and unmapped queue tests that exercise valid and invalid user queues, unmapped queue banks, unmapped doorbell bits, and PF/VF behavior.
- GRBM/wave-control tests that select a targeted SE/SA/instance, issue wave/debug commands, then confirm broadcast writes are restored for later register programming.
- CP DMA, scratch atomic, append/fence, and ME coherence tests that write known memory/fence patterns and verify no address truncation, cache-policy, or command-field mistakes.
- Pipeline statistics and RLC GPM perf tests that enable counters, run controlled draw/dispatch workloads, latch/read low/high pairs, and compare monotonic or expected activity.
- Draw-path tests covering primitive type/index type, primitive restart, draw initiator, tessellation config, shader-stage enablement, streamout opaque state, GE throttle/control, stereo, primitive ID, and VRS fields.
- GCR/TLB/reset diagnostics that exercise GCR command status, UTCL2 nack/error fields, CP soft reset, MEC/ME halt/reset/invalidate, and PMM interrupt/flush controls under recovery paths.
- Runtime warning signals include queue activation failures, dequeue/preemption timeouts, stuck EOP fetcher, lost doorbell updates, wrong writeback pointers, VM/UTCL1 errors in `CP_HQD_ERROR`, stale or incorrect pipeline counters, failed CP DMA/fence writes, unexpected GCR nack errors, GRBM writes affecting only one instance, and GPU reset loops after ring or compute queue setup.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002574`. It covers lines 12530-15146 of `gc_12_0_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the partial `CP_DDID_CNTL` and `GE_GS_FAST_LAUNCH_WG_DIM` families and to place these CP/HQD/GCR/GFXU/VGT/GE definitions in the full GC 12.0.0 register map.

### subset-b-002575: lines 15147-17777

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 15147-17777

## Scope

This chunk is a generated AMD GC 12.0.0 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `__SHIFT` value and a matching `__MASK` value used by AMDGPU register helpers to compose or decode 32-bit MMIO/indexed-register values. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines begin in the tail of a graphics/VGT block, with fast-launch geometry-shader workgroup dimensions, GS output primitive type, transform-feedback memory-base high bits, ordered-ID base, and primitive-ID reset fields. The main body then covers the `gc_gfx_cpwd_cpwd_cprs64dec` address block: RS64 command-processor register fields for MES, MEC, and GFX/PFP/ME microcontroller state, interrupts, apertures, scratch/local memory windows, process quantum, instruction/data cache controls, exception status, and performance-control state. The chunk then covers `gc_gfx_cpwd_cpwd_chdec` client/DRAM/compression/credit controls, `gc_gfx_cpwd_cpwd_gl2dec` GL2 cache, address match, writeback/invalidate, reset, credit, compression, and GL2A arbitration fields, and ends in `gc_gfx_cpwd_cpwd_perfddec` after GE2 distributed performance counter 3 high-word fields.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for the GC 12.0.0 graphics IP and is not Ceph filesystem code.

## Purpose

`gc_12_0_0_sh_mask.h` supplies bit layouts for GC 12.0.0 registers. Driver code pairs these macros with register addresses from the matching `gc_12_0_0_offset.h` header and, where available, generated reset/default values. Consumers normally use the constants through helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` so register fields can be packed or extracted without hard-coded bit positions.

This chunk is centered on command processor RS64 state and cache/client fabric control:

- Geometry/VGT tail fields for GS fast-launch dimensions, output primitive type, transform-feedback address high bits, ordered ID base, and primitive-ID reset value.
- `CP_MES_*` fields for MES RS64 program counter, interrupt routine/vector addresses, control/reset/active/halt/step bits, priority counters, scratch access, machine CSR-style status/cause/bad-address/cycle/time/instruction-retired registers, cache invalidation, timer compare, process quantum, doorbell controls, general-purpose registers, local/instruction/scratch aperture windows, metadata, exception status, interrupt data, and 16 data-cache aperture descriptors.
- `CP_MEC_*` fields mirroring the RS64 MEC command-processor state: control/reset/active bits, interrupt/status registers, VMID/cache policy, data-cache operations, general-purpose registers, local/instruction/scratch aperture windows, exception and pending-interrupt status, interrupt data, and 16 data-cache aperture descriptors.
- `CP_GFX_RS64_*`, `CP_PFP_RS64_*`, and `CP_ME_RS64_*` fields for graphics command processor interrupt enables/status, data-cache controls, local/instruction/scratch apertures, exception status, perf-count controls, timer/MIP registers, per-engine general-purpose registers, instruction pointers, pending interrupts, and two banks of 16 data-cache aperture descriptors.
- `CH*` and `CHA/CHC/CHI` fields for graphics client arbitration, DRAM burst masks and enables, client credits, free delay, compression mode, compressor override, FGCG override, compression controller limits, status counters, and subchannel/decompression controls.
- `GL2C_*` and `GL2A_*` fields for L2 cache control/status, client arbitration, address match, writeback/invalidate, soft reset, credit throttling, DCC/compression modes, safe modes, hashing, response throttling, and per-channel disable behavior.
- `CPG/CPC/CPF/GRBM/GE1/GE2_DIST` performance counter and latency-stat data words.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register-address symbols live in the companion offset header, commonly with `mm...` names matching these register names.
- AMDGPU callers normally access these fields through `REG_SET_FIELD`, `REG_GET_FIELD`, read-modify-write MMIO helpers, command-packet register programming, debugfs/perf tooling, reset paths, virtualization handling, and hang-dump code.

The main macro families in this slice are:

- `GE_GS_FAST_LAUNCH_WG_DIM*`, `VGT_GS_OUT_PRIM_TYPE`, `VGT_TF_MEMORY_BASE_HI`, `GE_GS_ORDERED_ID_BASE`, and `VGT_PRIMITIVEID_RESET`: graphics pipeline fields for geometry fast launch, primitive output, transform-feedback addressing, ordered IDs, and primitive ID reset.
- `CP_MES_*`: MES RS64 control and observability. Notable fields include `MES_PIPE*_RESET`, `MES_PIPE*_ACTIVE`, `MES_HALT`, `MES_STEP`, priority counters, interrupt masks/status, indexed scratch access, instruction pointer, machine status/exception CSRs, icache/dcache operations, process quantum timers, doorbell index/enables, local and instruction aperture base/mask/window controls, scratch aperture, metadata-control mode, exception flags, and interrupt data registers 16 through 31.
- `CP_MES_DC_APERTURE0..15_{BASE,MASK,CNTL}` and `CP_MEC_DC_APERTURE0..15_{BASE,MASK,CNTL}`: data-cache aperture descriptors. Control words expose enable, no-cache, read, write, non-volatile, and cache-policy bits, while base/mask words describe the address window.
- `CP_MEC_RS64_*` and `CP_MEC_*`: MEC RS64 program counter, vector, control, interrupt, instruction pointer, MIP/timer compare, VMID/cache policy, cache operations, GP registers, local/instruction/scratch apertures, perf-count control, pending interrupt, exception status, and interrupt data.
- `CP_CPC_IC_OP_CNTL`: command processor instruction cache operation controls, including invalidation, prime, invalidate-all, prime-complete, reset-error, and error reporting fields.
- `CP_GFX_RS64_*`: graphics RS64 interrupt, interrupt enable, data-cache, local/instruction/scratch, exception, perf-count, MIP/timer, GP, instruction pointer, pending interrupt, and aperture-bank fields. The aperture definitions are split into bank `0` and bank `1`, each carrying aperture indices 0 through 15.
- `CP_PFP_RS64_EXCEPTION_STATUS` and `CP_ME_RS64_EXCEPTION_STATUS`: PFP and ME exception-status fields for instruction-access faults, illegal instruction, breakpoint, environment call, misaligned data, data-access faults, and time interrupts.
- `CH_ARB_CTRL`, `CH_DRAM_BURST_*`, `CHA_*`, `CHI_CHR_REP_FGCG_OVERRIDE`, and `CHC_*`: channel/client/fabric control fields for arbitration, burst behavior, credit accounting, compression scheme and partition behavior, compressor override, power-gating override, decompressor limits, busy/status counters, response buffer status, and ID remap.
- `GL2C_*`: GL2 cache controls for write policy, uncached behavior, clock-gating modes, virtual-miss and miss-under-miss behavior, L1 policy, queue modes, disabled request classes, address matching, writeback/invalidate, reset, DCC and compression handling, safe modes, EA credits, discard-stall control, and supported compression schemes.
- `GL2A_*`: GL2A address matching, arbitration, credit-safe registers, high-priority and write-combine timeout behavior, channel hash bit selection, disable masks, and response throttling.
- `CPG_PERFCOUNTER*`, `CPC_PERFCOUNTER*`, `CPF_PERFCOUNTER*`, `*_LATENCY_STATS_DATA`, `GRBM_PERFCOUNTER*`, `GE1_PERFCOUNTER*`, and `GE2_DIST_PERFCOUNTER*`: low/high 32-bit counter result and latency data fields. The chunk ends exactly on `GE2_DIST_PERFCOUNTER3_HI`.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU consumers:

1. Select the GC 12.0.0 register header for the active ASIC generation.
2. Choose the matching register address from `gc_12_0_0_offset.h`.
3. Read an existing register value, prepare an indexed-register/debug/perf access, or construct an MMIO/command-packet register write.
4. Use the `__SHIFT`/`__MASK` pairs, usually through generated register helpers, to pack a field value or extract status bits.
5. Feed the resulting value into graphics pipeline setup, MES/MEC/GFX command processor initialization, queue scheduling, interrupt handling, exception/debug capture, cache maintenance, L2/client fabric tuning, compression control, performance monitoring, reset, or power-management logic.

For RS64 command processor state, initialization and recovery paths program program-counter/vector registers, local/instruction/scratch apertures, VMID/cache policy, doorbells, process quantum, and interrupt enables before work is scheduled. Interrupt, debug, and hang paths decode pending-interrupt and exception-status registers, general-purpose registers, instruction pointers, and CSR-style cause/status/bad-address state. Cache-maintenance paths use icache/dcache operation controls and may poll completion/status bits defined here.

For CH and GL2 registers, runtime setup and tuning paths program arbitration, credit, compression, DCC, hash, safe-mode, throttle, and writeback/invalidate fields. Status fields are read by diagnostics, performance tooling, or recovery code to identify busy clients, response buffer occupancy, dropped/stalled traffic, cache invalidation state, and compression-controller activity. Performance monitoring code selects counters elsewhere, then reads the low/high result words and latency-stat data fields defined in this tail.

This header does not encode ordering requirements, polling loops, latching sequences, clear-on-read behavior, privilege restrictions, or reset sequencing; those rules live in AMDGPU engine code, firmware interfaces, and hardware programming guides.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe GPU register fields whose state is owned by hardware, firmware, and AMDGPU runtime programming.

RS64 command processor program-counter, vector, local/instruction/scratch aperture, VMID/cache policy, doorbell, process-quantum, and cache-operation registers are persistent engine state until reprogrammed or reset. Bad masks in these fields can start firmware or command processor execution at the wrong address, leave an RS64 pipe halted or reset, expose an incorrect local memory aperture, direct data/instruction fetches through the wrong cache policy, or attach a doorbell to the wrong queue.

Exception, pending-interrupt, interrupt data, MIP/timer, machine-status, cause, bad-address, and GP registers are live diagnostic state. Some fields may be sticky or require hardware-defined clearing. The field definitions here allow decoding and writing, but do not document which fields are write-one-to-clear, read-only, latched, or volatile.

Data-cache aperture descriptors are stateful windows. The base/mask/control triples for MES, MEC, and GFX RS64 engines define address regions with access permissions and cacheability policy. Incorrect packing can grant unintended read/write access, make a required region uncached, deny firmware access, or make command processor microcode fault on data/instruction/scratch references.

CH/CHA/CHC/CHI and GL2C/GL2A control fields persist as cache and fabric policy. They affect arbitration, credits, compression, DCC bypass, cache invalidation/writeback, reset behavior, hashing, high-priority routing, and throttling. These fields are high-risk for full-register writes because many bits control side effects or hardware modes; callers must preserve reserved bits unless a documented sequence requires otherwise.

Performance counter low/high result fields and latency-stat data are hardware-updated state. Counter reads may require a snapshot/latch sequence outside this header to avoid torn 64-bit values. Writeback/invalidate and soft-reset fields have side effects; completion and status bits must be interpreted according to hardware sequencing rules not represented by masks alone.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.0.0 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h` provides matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_default.h`, when present in the same generated register family, provides default/reset values for many registers.
- Common AMDGPU register helpers provide field packing/extraction and MMIO or command-packet access mechanisms.
- AMDGPU GFX, CP, MES, MEC, KFD/compute scheduling, ring/doorbell setup, firmware bring-up, reset/recovery, suspend/resume, SR-IOV/virtualization, debugfs, perf counter, and hang-dump paths rely on these bit assignments.

Integration points include geometry shader fast-launch programming, primitive/transform-feedback state, MES pipe reset/active/halt control, RS64 firmware vectors and apertures, queue doorbells and process quantum, cache invalidation and priming, command processor interrupt enables/status, exception attribution, data-cache aperture setup, compression and DCC policy, GL2 writeback/invalidate/reset sequences, cache/fabric arbitration tuning, response throttling, and performance counter reads.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but writes the wrong hardware bits or decodes misleading diagnostics.
- This chunk starts and ends mid-family. It begins after the `GE_GS_FAST_LAUNCH_WG_DIM` comment and ends on `GE2_DIST_PERFCOUNTER3_HI`; adjacent chunks are needed for the surrounding graphics and performance-counter families.
- MES, MEC, and GFX RS64 register groups are similar but not identical. Assuming symmetry can miss bank suffixes, pipe-specific bits, engine-specific interrupt enables, or different exception/status meanings.
- Split low/high address fields and aperture base/mask fields are easy to misuse. Firmware vectors, GP registers carrying addresses, local/instruction/scratch windows, and data-cache apertures may have alignment or address-unit constraints outside this header.
- Pipe reset, active, halt, step, cache invalidation, writeback/invalidate, soft reset, and compression override fields have direct side effects. Debug tooling should avoid casual writes and preserve reserved bits.
- Doorbell and process-quantum fields affect scheduling. Incorrect doorbell offsets, enable bits, or quantum durations can stall queues, signal the wrong pipe, or create fairness/preemption bugs.
- Exception and interrupt status can be sticky, latched, or clear-on-write. Treating these fields as passive status can lose evidence during hang analysis or leave interrupts asserted.
- Data-cache aperture permission/cacheability bits can affect command processor isolation and correctness. Bad aperture masks can expose unintended memory or fault firmware accesses.
- GL2 and CH controls are dense and mode-heavy. Incorrect DCC, compression, credit, hash, throttle, or safe-mode masks can cause GPU hangs, silent performance regressions, coherency bugs, or misleading perf data.
- Counter result high/low registers can be race-prone if read without the documented latching sequence. This header cannot describe atomic snapshot requirements or overflow behavior.

## Test Signals

Useful validation is primarily generated-data consistency, build coverage, and hardware/runtime diagnostics:

- Kernel build coverage for AMDGPU files that include `gc_12_0_0_sh_mask.h`, especially GC 12.0.0 GFX, CP, MES, MEC, KFD/compute, reset, virtualization, debug, and perf counter paths.
- Mechanical comparison against AMD's authoritative GC 12.0.0 register database to confirm every `__SHIFT` and `__MASK` value in this slice.
- Cross-checks that all registers in this chunk have matching address macros in `gc_12_0_0_offset.h` and expected defaults in the matching default header where generated.
- Static mask/shift sanity checks: masks should align with shifts, full-width data fields should use `0xFFFFFFFFL`, repeated aperture families should remain structurally aligned, banked GFX RS64 fields should keep consistent suffixes, and bitfields should not overlap unless documented.
- MES/MEC/GFX bring-up tests that validate RS64 program counter/vector setup, local/instruction/scratch apertures, VMID/cache policy, GP register capture, doorbells, process quantum, and pipe reset/halt/active transitions.
- Interrupt and exception tests that exercise pending-interrupt, interrupt-data, MIP/timer, exception-status, cause, bad-address, and instruction-pointer decode during injected faults, time interrupts, breakpoints, and recovery.
- Cache-operation tests that invalidate/prime CP instruction cache, invalidate data cache, perform GL2 writeback/invalidate, and verify completion/status bits and post-operation coherency.
- Aperture tests that program MES/MEC/GFX data-cache apertures with known base/mask/control values and verify intended read/write/cacheability behavior without unintended access.
- Graphics pipeline tests covering GS fast launch dimensions, GS output primitive type, transform-feedback base high bits, ordered IDs, and primitive-ID reset behavior.
- CH/GL2 stress tests that vary compression/DCC, credits, hash, throttling, response-buffer pressure, address match, soft reset, and safe-mode fields under graphics and compute traffic while checking for hangs, data corruption, or performance anomalies.
- Perf counter tests that read CPG/CPC/CPF/GRBM/GE1/GE2_DIST low/high results and latency-stat data under controlled workloads, checking expected activity and monotonicity while avoiding torn reads.
- Runtime warning signals include RS64 firmware startup failures, stuck MES/MEC/GFX pipes, invalid doorbell behavior, repeated CP exceptions, stale cache contents after invalidation, incorrect compression/DCC behavior, GL2 reset hangs, fabric credit starvation, misleading performance counters, and GPU reset loops.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002575`. It covers lines 15147-17777 of `gc_12_0_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the graphics/VGT context before line 15147 and the performance-counter definitions after `GE2_DIST_PERFCOUNTER3_HI`.

### subset-b-002576: lines 17778-20327

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 17778-20327

## Scope

This chunk covers generated shift and mask macros from the AMD GC 12.0.0 register bitfield header. It begins at the field definitions for `GE2_DIST_PERFCOUNTER3_HI` without that register's leading comment, then covers complete blocks for CP/GC performance counter selection, RLC SPM and accumulator control, GDFLL/GRTAVFS/RTAVFS indirect power-management windows, RLC hypervisor-visible status and memory windows, GL2/channel pipe steering, CP hypervisor microcode and instruction-cache address fields, GRBM hypervisor selection/data windows, and much of the RLC core control/power/clock/doorbell section. It ends in the middle of `RLC_GPM_LEGACY_INT_DISABLE`, after the `STORE_LOAD_TIMER3_EXPIRED_T0` field and before any later fields in that same register.

The file is a generated hardware interface header. This chunk defines preprocessor constants only: it contains no C functions, structs, variables, persistent storage, runtime branches, or executable control flow.

## Purpose

The purpose of this range is to supply the bit-level ABI used by AMDGPU code when reading and writing GC 12.0.0 graphics, command-processor, RLC, performance-monitor, power-management, and virtualization registers. Each register field normally appears as a pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for composing or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit mask for isolating that field.

The sibling offset header for this ASIC generation provides register addresses. This `*_sh_mask.h` file provides the field layout used by helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, `RREG32_SOC15`, `WREG32_SOC15`, and firmware/hardware programming paths that compose register values directly.

## Important Macro Families

### Performance Counter Values and Selection

The chunk starts with low/high 32-bit performance counter value fields for `GC_EA_CPWD`, `GC_EA_SE`, `GL2C`, `GL2A`, `CHC`, `RLC`, `GCR`, and `CHA`. These registers expose the lower and upper halves of hardware counters through full-width `PERFCOUNTER_LO` and `PERFCOUNTER_HI` masks.

The following `gc_gfx_cpwd_cpwd_perfsdec` address block defines selector registers used to choose events and counter modes for many GC blocks:

- CP front-end blocks: `CPG_PERFCOUNTER*`, `CPC_PERFCOUNTER*`, and `CPF_PERFCOUNTER*`.
- Command-processor global control: `CP_CP_PERFMON_CNTL`.
- TC performance windows and latency statistic selectors: `CPF_TC_PERF_COUNTER_WINDOW_SELECT`, `CPG_TC_PERF_COUNTER_WINDOW_SELECT`, `CPC_TC_PERF_COUNTER_WINDOW_SELECT`, and `*_LATENCY_STATS_SELECT`.
- Draw-window/object counters: `CP_DRAW_OBJECT`, `CP_DRAW_OBJECT_COUNTER`, `CP_DRAW_WINDOW_*`, and `CP_DRAW_WINDOW_CNTL`.
- GRBM, geometry, cache, channel, RLC, GCR, and CHA performance selectors: `GRBM_PERFCOUNTER*`, `GE1_PERFCOUNTER*`, `GE2_DIST_PERFCOUNTER*`, `GC_EA_*`, `GL2C_*`, `GL2A_*`, `CHC_*`, `RLC_PERFCOUNTER*`, `GCR_*`, and `CHA_*`.

The selector pattern is regular. `*_SELECT` registers usually pack `PERF_SEL` and `PERF_SEL1` 10-bit event selectors plus `CNTR_MODE`/`PERF_MODE` fields in the high bits. `*_SELECT1` registers usually pack `PERF_SEL2`, `PERF_SEL3`, and mode fields for additional events. Single-counter forms expose only `PERF_SEL` plus a high-bit mode field. These macros are consumed by profiling, debugfs, perf, and internal diagnostic paths that program hardware counters.

### CP Performance Monitor Control and Draw Windows

`CP_CP_PERFMON_CNTL` exposes state fields for CP performance collection, SPM performance state, enable mode, sample enable, and start/end offset fields. This is a control register rather than a passive counter register, so incorrect field packing can leave the CP performance monitor stopped, permanently sampling, or sampling the wrong interval.

The draw-window/object macros define object identity, object counter, upper/lower draw-window bounds, and draw-window control fields such as included/excluded draw ranges and clock-enable behavior. They are integration points for command-processor performance capture that needs to filter by draw scope rather than count across all submitted work.

### RLC Streaming Performance Monitor and Accumulator

The `RLC_SPM_*` section is the densest stateful block in this chunk. It describes the RLC-owned streaming performance monitor path and its accumulator:

- `RLC_SPM_PERFMON_CNTL` selects ring mode, sample interval start/type, and sample interval.
- `RLC_SPM_PERFMON_RING_BASE_LO/HI`, `RLC_SPM_PERFMON_RING_SIZE`, `RLC_SPM_RING_WRPTR`, and `RLC_SPM_RING_RDPTR` define the sample ring buffer and producer/consumer pointers.
- `RLC_SPM_SEGMENT_THRESHOLD` and `RLC_SPM_PERFMON_SEGMENT_SIZE` define segment thresholds and split global versus shader-engine sample segments.
- `RLC_SPM_GLOBAL_MUXSEL_*` and `RLC_SPM_SE_MUXSEL_*` provide indirect address/data ports for selecting global and per-SE sampled signals.
- `RLC_SPM_ACCUM_DATARAM_*`, `RLC_SPM_ACCUM_SWA_DATARAM_*`, and `RLC_SPM_ACCUM_CTRLRAM_*` expose accumulator data/control RAM windows.
- `RLC_SPM_ACCUM_STATUS`, `RLC_SPM_ACCUM_CTRL`, and `RLC_SPM_ACCUM_MODE` expose the accumulator lifecycle, including done, overflow, armed, FIFO-empty, idle, pending rearm, abort, start, reset, rearm, 32-bit mode, accumulation mode, shader-array/engine selection, and SWA accumulation mode fields.
- Threshold/sample-count/write-count registers define how many samples are requested and how accumulator memory is interpreted.
- `RLC_SPM_PAUSE`, `RLC_SPM_STATUS`, `RLC_SPM_GFXCLOCK_LOWCOUNT`, `RLC_SPM_GFXCLOCK_HIGHCOUNT`, `RLC_SPM_GTS_TRIGGER_VALUE_*`, and `RLC_SPM_MODE` support pause control, status polling, clock/sample timing, global timestamp triggers, and mode selection.

Several fields in this family are command strobes, not durable settings. For example, start/reset/rearm/sample-wire fields in `RLC_SPM_ACCUM_CTRL` should be treated as hardware actions, while `RLC_SPM_ACCUM_STATUS` and `RLC_SPM_STATUS` should be polled or sampled to verify completion, overflow, idle, abort, and sample-count state.

### RSPM Request/Response Ports

`RLC_SPM_RSPM_REQ_DATA`, `RLC_SPM_RSPM_REQ_OP`, `RLC_SPM_RSPM_RET_DATA`, `RLC_SPM_RSPM_RET_OP`, and the matching `RLC_SPM_SE_RSPM_*` registers define request and response windows for RSPM access. `RLC_SPM_RSPM_CMD` and `RLC_SPM_RSPM_CMD_ACK` expose command and acknowledgement bits. These are indirect hardware ports; callers must respect request/ack sequencing and should not treat the data registers as ordinary persistent storage.

### Dynamic Frequency, Voltage, and RTAVFS Access

The chunk includes small address blocks for graphics dynamic frequency/voltage support:

- `GDFLL_EDC_HYSTERESIS_CNTL` and `GDFLL_EDC_HYSTERESIS_STAT` define EDC hysteresis configuration and observed status.
- `XVMIN_XVMIN_WR_DATA` provides a write-data field for XVMIN programming.
- `GRTAVFS_RTAVFS_REG_ADDR`, `GRTAVFS_RTAVFS_WR_DATA`, `GRTAVFS_RTAVFS_RD_DATA`, `GRTAVFS_RTAVFS_REG_CTRL`, and `GRTAVFS_RTAVFS_REG_STATUS` define an indirect RTAVFS register access window with read/write enables and acknowledgement/data-valid status.
- `GRTAVFS_TARG_FREQ` and `GRTAVFS_TARG_VOLT` carry requested target frequency and voltage plus request/valid bits.
- `GRTAVFS_SOFT_RESET`, `GRTAVFS_PSM_CNTL`, `GRTAVFS_CLK_CNTL`, and `GFX_ICG_GRTAVFS_CTRL` define reset override, PSM sampling/count configuration, clock mux override, and dynamic clock-gating override.
- A separate `gc_gfx_cpwd_grtavfs_rtavfs_rtavfs_rtavfs_reg_blk` block exposes direct `RTAVFS_RTAVFS_REG_ADDR` and `RTAVFS_RTAVFS_WR_DATA` field definitions.

These macros integrate with power-management and firmware-mediated flows. Wrong field composition can request incorrect voltage/frequency targets, break an indirect access sequence, or force clock selection/clock gating in a way that affects the entire graphics block.

### RLC Hypervisor Status, Microcode, and Memory Windows

The `gc_gfx_cpwd_cpwd_hypdec` block exposes RLC-side status and privileged access fields:

- `RLC_SDMA0_STATUS` through `RLC_SDMA3_STATUS` and matching busy-status registers provide full-width status snapshots for SDMA engines.
- `RLC_HYP_SEMAPHORE_0..3` provide small `CLIENT_ID` fields for privileged synchronization.
- `RLC_BUSY_CLK_CNTL` and `RLC_CLK_CNTL` define RLC busy-off latency, GRBM busy-off latency, and many clock-gating override bits for RLC subblocks such as SRM, IMU, SPM, GPM, common logic, TC, register access, SRAM, LX6 core, UTCL2, IH gasket, and bridge.
- `RLC_IH_COOKIE` and `RLC_IH_COOKIE_CNTL` expose interrupt-cookie data, credit, and reset-counter control.
- `RLC_HYP_RLCG_UCODE_CHKSUM` exposes the RLCG microcode checksum.
- `RLC_GPM_UCODE_ADDR/DATA`, `RLC_GPM_IRAM_ADDR/DATA`, `RLC_LX6_DRAM_ADDR/DATA`, `RLC_LX6_IRAM_ADDR/DATA`, `RLC_GPM_SCRATCH_ADDR/DATA`, `RLC_SRM_DRAM_ADDR/DATA`, and `RLC_SRM_ARAM_ADDR/DATA` expose indirect address/data windows into microcode, instruction RAM, data RAM, scratch, and SRM memory.
- `RLC_GTS_OFFSET_*` and `RLC_GTS_OFFSET_SNAP_*` provide global timestamp offset and snapshot fields.

The address/data pairs are stateful indirect ports. Driver or firmware code normally writes an address register and then reads/writes the matching data register. Races, missing barriers, or wrong address masks can corrupt firmware-visible state.

### Pipe Steering and User Disable Masks

`GL2_PIPE_STEER_0..3` map graphics pipes 0-7 to GL2 channels across queue groups. Each pipe mapping uses a 3-bit channel field, with separate registers for pipes 0-3 and 4-7 and queue groups Q0-Q3. `CH_PIPE_STEER` maps pipes 0-3 with 2-bit fields and a mode bit.

`GC_USER_FULL_SA_UNIT_DISABLE`, `GRBM_GC_USER_SA_UNIT_DISABLE`, `GC_USER_GL2C_DISABLE_0`, and `GC_USER_GL2C_DISABLE_1` expose user-visible shader-array and GL2C disable masks. These fields are tied to harvesting, fusing, partitioning, or repair state. Programming them incorrectly can expose disabled hardware, hide working units, or misroute cache traffic.

### CP Hypervisor Microcode and Instruction/Data Cache Fields

The `gc_gfx_cpwd_cpwd_cphypdec` block describes command-processor privileged windows:

- Context-range registers: `CP_HYP_CONTEXT_RANGE_BASE` and `CP_HYP_CONTEXT_RANGE_END`.
- PFP, ME, and MEC microcode address/data ports: `CP_HYP_PFP_UCODE_ADDR/DATA`, `CP_PFP_UCODE_ADDR/DATA`, `CP_HYP_ME_UCODE_ADDR/DATA`, `CP_ME_RAM_RADDR`, `CP_ME_RAM_WADDR`, `CP_ME_RAM_DATA`, `CP_HYP_MEC1_UCODE_ADDR/DATA`, and `CP_MEC_ME1_UCODE_ADDR/DATA`. Address registers include a high `PIPE_SEL` bit where applicable.
- Microcode checksum registers: `CP_HYP_PFP_UCODE_CHKSUM`, `CP_HYP_ME_UCODE_CHKSUM`, and `CP_HYP_MEC_ME1_UCODE_CHKSUM`.
- Instruction-cache base/control/operation fields for PFP, ME, CPC, and MES: base low/high, VMID, execute-disable, cache policy, per-pipe/scope/temporal fields where present, invalidate-cache, invalidate-complete, prime-start-PC, prime-cache, and primed status.
- MES data-cache base and bound fields: `CP_MES_DC_BASE_*`, `CP_MES_MDBASE_*`, `CP_MES_MIBOUND_*`, and `CP_MES_MDBOUND_*`.
- Version and RS64 memory-bound fields: `CP_HYP_PFP_UCODE_VERS`, `CP_HYP_ME_UCODE_VERS`, `CP_GFX_RS64_DC_BASE*`, `CP_GFX_RS64_MIBOUND_*`, and MEC data/cache bound fields.

These macros support firmware loading, privileged CP setup, cache invalidation/priming, and MES/MEC/GFX RS64 memory aperture programming. The cache operation bits include both command and completion fields, so tests should verify that code waits for completion rather than only issuing the command bit.

### GRBM Hypervisor Selection and Remap

The `gc_gfx_cpwd_cpwd_grbm_hypdec` block defines indirect GRBM selection/data fields:

- `GRBM_GFX_INDEX_SR_SELECT` and `GRBM_GFX_INDEX_SR_DATA` select and expose instance, shader array, shader engine, WGP, broadcast, and VF/PF state.
- `GRBM_GFX_CNTL_SR_SELECT` and `GRBM_GFX_CNTL_SR_DATA` select and expose GRBM graphics-control state.
- `GC_IH_COOKIE_0_PTR` provides an interrupt-cookie pointer field.
- `GRBM_SE_REMAP_CNTL` and `GRBM_GRBM_SA_REMAP_CNTL` define shader-engine and shader-array remap fields.

These are virtualization and topology integration points. Selection register writes affect what subsequent data-register accesses mean, so callers must serialize access to the indirect pair.

### RLC Core Control, Interrupts, Timers, Clocks, Doorbells, and Power

The `gc_gfx_cpwd_cpwd_rlcdec` block in this chunk covers RLC core state:

- `RLC_CNTL`, `RLC_F32_UCODE_VERSION`, `RLC_STAT`, `RLC_ACTIVE_MASK`, `RLC_GFX_SE_STATUS`, and reference-clock timestamp registers define basic RLC enablement, version, busy/idle/interrupt state, activity masks, shader-engine status, and timestamp counters.
- `RLC_GPM_TIMER_INT_0..4`, `RLC_GPM_TIMER_CTRL`, and `RLC_GPM_TIMER_STAT` define GPM timer values, modes, enable/clear flags, and timer status.
- `RLC_GPM_LEGACY_INT_STAT`, `RLC_GPM_LEGACY_INT_CLEAR`, `RLC_INT_STAT`, and the start of `RLC_GPM_LEGACY_INT_DISABLE` define legacy interrupt status/clear/disable fields for SPP PVT changes, EOF, PG control, and store/load timer events visible in this range.
- `RLC_MGCG_CTRL`, `RLC_CGTT_MGCG_OVERRIDE`, `RLC_CGCG_CGLS_CTRL`, and `RLC_CGCG_RAMP_CTRL` define medium-grain/clock-gating, clock-throttling, light sleep, controller, sleep-mode, ramp, delay, and override fields.
- `RLC_JUMP_TABLE_RESTORE`, `RLC_PG_DELAY_2`, `RLC_PG_DELAY`, `RLC_PG_DELAY_3`, `RLC_PG_CNTL`, `RLC_DYN_PG_STATUS`, `RLC_DYN_PG_REQUEST`, `RLC_PG_ALWAYS_ON_WGP_MASK`, `RLC_MAX_PG_WGP`, `RLC_AUTO_PG_CTRL`, and `RLC_STATIC_PG_STATUS` define RLC-controlled power-gating behavior, delay values, dynamic/static WGP power status/request masks, always-on WGPs, max powered-up WGP limits, and automatic power-gating thresholds.
- `RLC_GPU_CLOCK_COUNT_*`, `RLC_CAPTURE_GPU_CLOCK_COUNT`, `RLC_CLK_COUNT_*`, `RLC_CLK_COUNT_CTRL`, `RLC_CLK_COUNT_STAT`, `RLC_GPU_CLOCK_32_RES_SEL`, and `RLC_GPU_CLOCK_32` define clock capture, counter selection, busy/done state, and 32-bit clock outputs.
- `RLC_UCODE_CNTL`, `RLC_GPM_THREAD_RESET`, `RLC_GPM_CP_DMA_COMPLETE_T0/T1`, `RLC_GPM_THREAD_INVALIDATE_CACHE`, `RLC_GPM_THREAD_PRIORITY`, `RLC_GPM_THREAD_ENABLE`, and `RLC_GPM_INT_DISABLE_TH0` control RLC/GPM firmware execution, thread reset, DMA completion, cache invalidation, priority, enablement, and interrupt masking.
- `RLC_RLCG_DOORBELL_CNTL`, `RLC_RLCG_DOORBELL_STAT`, `RLC_RLCG_DOORBELL_0..3_DATA_LO/HI`, and `RLC_RLCG_DOORBELL_RANGE` define RLCG doorbell control, status, per-doorbell payload data, and lower/upper address range fields.
- `RLC_SERDES_RD_INDEX`, `RLC_SERDES_RD_DATA_0..3`, `RLC_SERDES_MASK`, `RLC_SERDES_CTRL`, `RLC_SERDES_DATA`, and `RLC_SERDES_BUSY` define serial-deserializer read selection, masks, command/address/data fields, busy state, read FIFO state, and pending-read status.
- `RLC_GPM_GENERAL_0..7`, `RLC_GPM_GENERAL_16`, `RLC_GPR_REG1`, and `RLC_GPR_REG2` provide full-width firmware/general-purpose fields.

Many of these macros represent live hardware control rather than static description. Interrupt clear fields may be write-one-to-clear, doorbell fields can trigger firmware work, power-gating fields can change active WGP state, and clock-gating overrides can affect power and hang behavior.

## Dependencies and Integration Points

This header depends on C preprocessor inclusion and on the matching GC 12.0.0 register offset definitions. It does not include other files itself in this range, but AMDGPU source typically uses these macros together with ASIC-specific offset headers and register helper macros from the AMD GPU driver stack.

The main integration surfaces are:

- AMDGPU graphics IP initialization and teardown code that programs RLC, CP, GRBM, and topology registers.
- Firmware loading and verification paths for CP PFP/ME/MEC, RLC GPM, LX6, SRM, and related microcode memory windows.
- Performance monitoring and profiling paths that configure CP, GRBM, GE, GL2, CHC, RLC, GCR, CHA, GC_EA, RLC SPM, and accumulator counters.
- Power-management paths that coordinate GDFLL, RTAVFS/GRTAVFS, clock gating, clock counting, dynamic power gating, and WGP masks.
- Virtualization/SR-IOV or hypervisor paths that use RLC hypervisor semaphores, SDMA busy/status registers, GRBM VF/PF selection, CP hypervisor context ranges, and privileged microcode/cache windows.

## State and Persistence Behavior

The macros themselves have no runtime state. The hardware registers they describe are stateful and often persistent across parts of a GPU reset domain until firmware, driver initialization, or a hardware reset rewrites them.

Important stateful patterns in this chunk include:

- Indirect address/data windows: CP microcode, RLC GPM/IRAM/LX6/SRM memory, RTAVFS, GRBM selection/data, RSPM request/response, SPM muxsel, accumulator RAM, and SERDES access all depend on a prior address/select/command register write.
- Producer/consumer state: SPM ring base/size/wrptr/rdptr and segment configuration persist during a capture session.
- Command and acknowledgement fields: RTAVFS read/write enables and acks, SPM/RSPM command/ack fields, cache invalidate/prime commands and completion bits, clock-count clear/start/done bits, and SERDES busy/pending fields require sequencing.
- Global hardware policy state: clock-gating overrides, power-gating masks/delays, WGP masks, GL2/CH pipe steering, and voltage/frequency target fields can affect all users of the graphics block.

## Risks

- Generated-header drift: masks and shifts must match the GC 12.0.0 hardware specification. A single wrong mask in this header can silently corrupt register programming across many call sites.
- Partial-register chunk boundary: this chunk begins after the `GE2_DIST_PERFCOUNTER3_HI` comment and ends before all `RLC_GPM_LEGACY_INT_DISABLE` fields are visible. The merge lane should reconcile adjacent chunks before making whole-register conclusions for those two boundary registers.
- Indirect-port races: address/data pairs and select/data pairs require serialization. Concurrent users of GRBM, RLC memory windows, RTAVFS, SPM muxsel, RSPM, or SERDES registers can read or write the wrong target.
- Write-one or strobe semantics: status clear, start, reset, invalidate, prime, clock-count, timer clear, doorbell, and command bits should not be modified through naive read-modify-write unless the hardware semantics are verified.
- Privilege and reset-domain sensitivity: CP/RLC microcode, hypervisor, clock/power, and virtualization fields may only be valid in PF/privileged contexts or during tightly ordered firmware initialization.
- Topology/harvest sensitivity: pipe steering and disable masks can misrepresent available hardware if programmed without fuse/harvest awareness.

## Test Signals

Useful validation signals for code that consumes this chunk include:

- Compile coverage for all GC 12.0.0 AMDGPU objects that include this header and use these field names.
- Static checks that every `_MASK`/`__SHIFT` pair composes and extracts expected values with `REG_SET_FIELD`/`REG_GET_FIELD`, especially high-bit fields such as `PIPE_SEL`, mode fields, clock-gating overrides, and cache-control bits.
- Hardware or emulator tests that program performance counters, verify nonzero low/high counter reads, and confirm selector/mode fields route expected events.
- RLC SPM tests that allocate a ring, configure mux selections, start sampling/accumulation, observe write-pointer movement, and poll done/overflow/idle status.
- Firmware-loading tests that write CP/RLC address/data windows, verify checksum/version registers, and wait for instruction-cache invalidate/prime completion bits.
- Power-management tests that exercise RTAVFS/GRTAVFS indirect read/write acknowledgement, target frequency/voltage request/valid bits, and clock-count status without leaving override bits asserted.
- Virtualization or privileged-mode tests that verify GRBM VF/PF selection, RLC semaphores, SDMA busy/status snapshots, and CP hypervisor context-range behavior.
- Reset/resume tests that confirm RLC clock/power/doorbell/timer/interrupt fields are restored in the expected order after GPU reset, suspend/resume, or mode changes.

### subset-b-002577: lines 20328-22793

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 20328-22793

## Scope

This chunk is a generated AMDGPU GC 12.0.0 register shift/mask header segment. It contains C preprocessor constants only: each hardware register field is exposed as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. The matching register offsets live in `gc_12_0_0_offset.h`; default values, where present, live in the corresponding GC default header.

The range is centered on RLC and power-control register fields. It starts in the tail of `RLC_GPM_LEGACY_INT_DISABLE`, then covers RLC SRM/GPM command and status fields, UTCL1 and UTCL2 controls/errors, RLC clock/count capture, SPP/SPM profiling and residency counters, RLC interrupt-handler client status, LX6/Xtensa-style RLC core controls, doorbell capture, safe-mode and SMU command mailboxes, IMU bootload fields, the `gc_gfx_cpwd_cpwd_rlcsdec` RLCS decoder block, the `gc_gfx_cpwd_cpwd_pfvfdec_rlc` PF/VF RLC block, and the beginning of `gc_gfx_cpwd_cpwd_pwrdec` power/clock-gating fields through `GFX_ICG_GL2C_CTRL`.

## Purpose

The purpose of this header slice is to give GC 12 AMDGPU, KFD, MES, SDMA, GFXHUB, IMU, and SOC24 code stable symbolic bit definitions for low-level MMIO register programming. Driver code uses these masks with the matching offset macros through `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, `REG_GET_FIELD`, golden-register helpers, and firmware-facing queue or initialization paths.

The fields in this chunk are mostly management-plane fields rather than shader execution fields. They describe how the RLC firmware complex coordinates GPU power transitions, register save/restore, bootload/autoload completion, interrupt delivery, profiling/sample collection, doorbells, IMU communication, memory sleep/deep-sleep behavior, and clock-gating overrides. Because the macros are pure constants, correctness depends on generated names, bit positions, masks, and register-family continuity matching the hardware register database.

## Register Families

`RLC_SRM_*` and `RLC_GPM_*` fields describe save/restore manager and graphics power-management control. The chunk includes SRM enable/reset/autoincrement, GPM command FIFO empty/full/overflow status, eight indexed SRM control address/data slots, `RLC_SRM_STAT`, GPM interrupt force/status/general scratch fields, SRM/GPM command encodings (`OP`, `INDEX_CNTL`, `INDEX_CNTL_NUM`, `SIZE`, `START_OFFSET`), and abort controls. These fields are the bit-level surface used when firmware or driver paths initiate or inspect register save/restore and GPM command activity.

`RLC_*_UTCL1_*` and `RLC_RLCS_UTCL2_*` fields cover translation/cache interface behavior and error reporting. The UTCL1 controls for GPM, SPM, SRM, and LX6 share the same shape: retry timer count, drop/bypass/invalidate, fragment-limit mode, force-snoop, and reserved fields. Error registers split translated request error type, VMID, high address bits, and low address bits. Status registers report faults, retries, PRT detection, busy status, stalls, and per-client IDs. The later RLCS UTCL2 controls add GPA/VF override, no-PTE memory type behavior, ignore-permission behavior, busy handshakes, and request/ack status.

`RLC_CGCG_CGLS_CTRL_3D`, `RLC_CGCG_RAMP_CTRL_3D`, `RLC_MEM_SLP_CNTL`, the RLCS deep-sleep controls, and the final `CGTT_*`/`GFX_ICG_*` block are power-management fields. They define clock-gating enables, ramp timing, sleep modes, memory light-sleep/deep-sleep enables and overrides for SRM/SPM/SPP/TC, SOC/GFX deep-sleep allow masks, GDFLL allow masks, shader-engine power/reset bits, GL2C disable masks, and per-block clock-gating delay/override bits for IA, WD, CP, CPF, CPC, RLC, GCR, EA/CPWD, GC CAC, GRBM, GL2A, and GL2C.

`RLC_SPP_*`, `RLC_SPM_*`, and residency-counter fields support profiling, power profiling, streaming performance monitor paths, and power residency instrumentation. The chunk includes SPP enable/pause/power-opt controls, shader-stage profiling enables and start conditions, SSF capture enables and thresholds, inflight readback address/data, profiling info, global shader IDs, SPP status and PVT counters, stall-state update, PBB override information, SPP reset bits, SPM delay/mask indirect address/data, SPM sample count, MC control attributes, interrupt control/status/info, and power/clock/DS/ULV/PCC/general residency counter reset/enable/ack/overflow plus event/reference counter data.

`RLC_GFX_IH_*`, `RLC_RLCS_*_INT_*`, `RLC_CP_EOF_INT*`, and spare interrupt fields describe interrupt plumbing. The RLC GFX IH control masks SE, SDMA, UTCL2, and PMM interrupt clients and has matching error-clear fields. Status registers report arbiter grants, per-SE0..SE7 buffer level/loading/protocol-error/overflow, per-SDMA0..SDMA3 status, and UTCL2/PMM status. RLCS CP, SPM, SDMA, GRBM idle/busy, GPM legacy, spare, and EOF interrupt fields provide ack/auto-ack, interrupt IDs, pending bits, status histories, and clear bits.

`RLC_LX6_*`, `RLC_XT_*`, `RLC_IMU_*`, and `RLC_RLCS_IMU_*` describe the embedded RLC/IMU control and messaging surfaces. They include LX6 reset/runstall/debug/status/firmware status/version, XT core status/interrupt/fault/alternate-vector fields, vector force/clear bits for interrupt sources, doorbell range/mode/status/data fields, IMU bootload address/size/misc/reset-vector fields, bidirectional IMU-RLC message data/control/toggle fields, telemetry current/voltage/temperature/rail fields, mutex control, IMU/RLC status, IMU RAM address/data handshakes, and a GFX doorbell fence.

`RLC_RLCS_*` fields define the RLCS decoder block. The chunk includes exception and auxiliary register address fields, CGCG request/status, SOC and GFX deep-sleep controls, GPM status mirrors, aborted power-down sequence, GRBM soft reset, power-gating change status/read, IH semaphores, bootload status, GRBM idle/busy status and interrupt controls, compute-idle hysteresis, general scratch registers, bootload ID loaded bitmaps for IDs 0..63, GCR data/status, perfmon clock state, GFX memory power control data registers, shader-engine power controls, and decoder block sentinels.

## Important APIs, Types, and Functions

This header defines no functions, structs, enums, or runtime storage. Its API is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the masked bit range in the register word.
- Full-width payload fields use mask `0xFFFFFFFFL`; reserved fields are explicitly named so generated consumers can preserve or clear the correct bit ranges.

The main external helpers are `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and table macros such as SOC15 golden-register entries. Important in-tree GC 12 consumers include `amdgpu/gfx_v12_0.c`, `amdgpu/amdgpu_amdkfd_gfx_v12.c`, `amdkfd/kfd_mqd_manager_v12.c`, `amdkfd/kfd_device_queue_manager_v12.c`, `amdgpu/mes_v12_0.c`, `amdgpu/sdma_v7_0.c`, `amdgpu/gfxhub_v12_0.c`, `amdgpu/imu_v12_0.c`, and `amdgpu/soc24.c`, all of which include `gc_12_0_0_sh_mask.h` directly or use it alongside the matching offset header.

Concrete examples visible in this tree include `gfx_v12_0_wait_for_rlc_autoload_complete()`, which reads `regRLC_RLCS_BOOTLOAD_STATUS` and extracts `RLC_RLCS_BOOTLOAD_STATUS.BOOTLOAD_COMPLETE`, and `gfx_v12_0_set_safe_mode()`, which builds a value with `RLC_SAFE_MODE__CMD_MASK` and `RLC_SAFE_MODE__MESSAGE__SHIFT`, writes `regRLC_SAFE_MODE`, and polls `RLC_SAFE_MODE.CMD`.

## Control Flow

There is no executable control flow in this header. Runtime control flow is imposed by register consumers:

- GC 12 RLC autoload waits read CP and RLC bootload status repeatedly until CP is idle and the RLCS bootload complete bit is set.
- Safe-mode entry writes the RLC safe-mode command/message bits and polls for command completion; safe-mode exit writes the command bit again with the exit message encoding.
- Power-management paths program clock-gating and memory sleep/deep-sleep fields during initialization, power-state transitions, suspend/resume, reset recovery, or firmware-managed transitions.
- RLC/IMU messaging uses data/control registers plus toggle, done, ack, mutex, and fence fields to handshake ownership and command completion.
- Interrupt paths mask, acknowledge, clear, or inspect RLC-facing interrupt clients, including SE, SDMA, UTCL2, PMM, CP, SPM, spare, EOF, and GRBM idle/busy sources.
- Profiling and telemetry paths enable SPP/SPM capture, configure thresholds or memory attributes, read sample/residency counters, and use status bits to detect overflow or completion.

## State and Persistence

The macros themselves are compile-time constants and hold no state. The hardware registers they describe are volatile GPU state, but many fields have effects that persist until reset, firmware action, or explicit driver writes.

RLC safe-mode, SMU message/argument, SRM/GPM command, IMU bootload, IMU-RLC mailbox, and doorbell fields represent command or handshake state. A stale toggle, ack, command, or doorbell-valid bit can make firmware and driver code disagree about ownership or completion.

Power and clock controls persist across the active power state of the GC block. Clock-gating override bits, memory light-sleep/deep-sleep enables, GFX/SOC deep-sleep allow masks, and shader-engine reset/clock-enable fields can change performance, power, idle detection, and reset behavior until reprogrammed by init, resume, or recovery code.

Status and counter registers are diagnostic state. Bootload status, GPM status, GRBM idle/busy state, UTCL1/UTCL2 fault or busy bits, residency event/reference counters, SPP/PVT counters, interrupt info, and SDMA/SE buffer status can be latched, accumulated, or cleared by side-effect depending on the hardware register semantics. Driver diagnostics and timeout paths depend on reading these fields with the exact masks defined here.

## Dependencies and Integration Points

This chunk depends on the broader generated GC 12 register set: `gc_12_0_0_offset.h` supplies the register addresses, this file supplies field positions, and driver helpers perform the read/modify/write and field extraction. It also depends on SOC24 register access plumbing, firmware loading policy, RLC/IMU firmware contracts, MES/KFD queue management, and GPU power-management policy.

Important integration points include:

- `amdgpu/gfx_v12_0.c` for RLC autoload completion, safe-mode entry/exit, firmware bring-up, reset, and GFX power behavior.
- `amdgpu/imu_v12_0.c` for IMU initialization and RLC/IMU coordination, using the same GC 12 register namespace.
- `amdgpu/mes_v12_0.c`, `amdgpu/amdgpu_amdkfd_gfx_v12.c`, and KFD v12 queue managers for compute queue setup, command processor integration, and RLC-visible state around queue scheduling.
- `amdgpu/gfxhub_v12_0.c` and `amdgpu/sdma_v7_0.c`, which include this header for GC 12 field extraction and register programming adjacent to VM and DMA flows.
- Interrupt handling and diagnostics that read RLC GFX IH, CP/SPM/SDMA interrupt info, bootload status, idle/busy status, and fault information.
- Firmware and hardware-generation tooling: because this is generated, downstream code assumes macro spellings and field positions match the authoritative register database.

## Risks

The main risk is silent hardware misprogramming. These macros are constants; a wrong shift or mask can compile cleanly while causing driver code to set the wrong bits, preserve reserved bits incorrectly, or poll a field that never changes.

High-risk fields in this chunk include `RLC_SAFE_MODE`, `RLC_RLCS_BOOTLOAD_STATUS`, IMU bootload and IMU-RLC mailbox controls, SRM/GPM command/abort fields, `RLC_MEM_SLP_CNTL`, deep-sleep allow masks, clock-gating override controls, UTCL1/UTCL2 error/status fields, and interrupt ack/clear/status fields. Errors in these areas can produce initialization timeouts, failed RLC autoload, broken reset recovery, hangs during power transitions, lost interrupts, incorrect fault attribution, or performance/power regressions.

Reserved-bit masks are also important. Read/modify/write code must avoid accidentally setting reserved fields, while generated masks must still describe the reserved ranges accurately enough for table or diagnostic tooling to preserve them. The file should therefore be regenerated from hardware definitions rather than hand-edited.

## Test Signals

Compile-time signals include successful AMDGPU/KFD builds for GC 12 code that includes `gc_12_0_0_sh_mask.h`, especially `gfx_v12_0.c`, `amdgpu_amdkfd_gfx_v12.c`, `kfd_mqd_manager_v12.c`, `kfd_device_queue_manager_v12.c`, `mes_v12_0.c`, `sdma_v7_0.c`, `gfxhub_v12_0.c`, `imu_v12_0.c`, and `soc24.c`. Renamed or removed macros should fail quickly; wrong numeric values usually require runtime testing.

Runtime signals should focus on GC 12 hardware or emulation: successful GPU probe, RLC/IMU firmware loading, `RLC_RLCS_BOOTLOAD_STATUS.BOOTLOAD_COMPLETE` reaching completion before timeout, safe-mode entry/exit completing, suspend/resume, GPU reset recovery, MES startup, KFD process and queue creation, SDMA activity, and stable compute/graphics workloads.

Power and diagnostics signals include correct clock-gating and memory-sleep behavior, no unexpected hangs during GFXOFF/deep-sleep transitions, sane RLC GPM/GRBM idle-busy status, no persistent UTCL1/UTCL2 fault bits under normal workloads, working interrupt delivery and clearing for SE/SDMA/UTCL2/PMM/SPM/CP paths, valid SPP/SPM/residency counter behavior, and no firmware mailbox or doorbell handshakes stuck in pending states.

### subset-b-002578: lines 22794-25201

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 22794-25201

## Scope

This chunk is a generated AMD GC 12.0.0 register shift/mask header segment. It contains C preprocessor constants only: register fields are represented by `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros for packing and decoding 32-bit hardware register values. There are no functions, structs, enums, variables, allocation paths, locks, callbacks, persistence code, or executable branches in this range.

The selected lines begin in the middle of the `GFX_ICG_GL2C_CTRL` mask family and then cover `GFX_ICG_GL2C_CTRL1`. The chunk continues through CP/PSP decode, CH power/clock control, GFX IMU, GRBMH, PA, SQ, SX, SPI, and the beginning of TD/TA texture-pipe fields. It ends inside `TA_CNTL_AUX`; the remaining fields for that register and later TPDEC registers are outside this chunk. Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata for the GC 12.0.0 graphics IP, not Ceph filesystem code.

## Purpose

`gc_12_0_0_sh_mask.h` supplies bit layouts for GC 12.0.0 registers. AMDGPU code pairs these macros with matching register addresses from `gc_12_0_0_offset.h` and uses common helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` to compose writes or decode readbacks without duplicating literal bit positions.

This chunk focuses on engine security/debug control, firmware/IMU RAM access, graphics-block busy/status reporting, shader processor controls, shader export/SPI debug state, wavefront counters, trap-screen configuration, and texture-address/texture-data controls:

- GL2C and channel clock-gating override fields for fine-grained clock-control bring-up, debug, and golden-setting programming.
- CP/PSP and GC EA security fields covering indexed debug-memory address/data windows, PSP debug override bits, trusted memory zone control, client security-level maps, GRBM CAM remapping, firewall violation status, and UTC bypass control.
- GFX IMU message, access-control, scratch, RLC RAM, bootloader, instruction/data RAM, core control, and reset-control fields.
- GRBMH fields for read timeouts, interface path disables, aggregate busy/clean status, fine-grained clock-gating targets, soft reset, read-error attribution, invalid pipe, sync, and unit-disable masks.
- PA/GE fields for shader-array disable/rate configuration, geometry-engine busy state, GE/SPI and GE/PA safe-register routing, clipper setup, setup/scan-converter/debug FIFO controls, and NGG-related PA behavior.
- SQ/SQC/LDS fields for shader queue configuration, cache sizing, instruction/data cache behavior, LDS/SQ/SP DSM and error-injection controls, thread trace, arbitration, dynamic VGPR allocation, GL1X status, perf snapshots, interrupt masking, watchpoint registers, indirect register access, and SQ command control.
- SX debug-busy fields for color/export/output buffer internals, request queues, blend/position/index valid queues, and scoreboard state.
- SPI fields for wave IDs, scratch overflow status, debug controls, DSM and EDC counters, debug-busy status, per-stage CU masks, lifetime counters/status, WGP work-pending state, load-balancer counter controls, GDS credits, export/scoreboard buffer sizing, active wavefront counters, trap-screen base/mask/GPR-min registers, and crawler-depth configuration.
- TD/TA fields for texture-data control, status, power control, LDS return credits, scratch, texture-address credits, XNACK clock-gating behavior, and the first `TA_CNTL_AUX` bits.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The interface is the generated macro contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register address symbols for the same names live in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h`.
- AMDGPU consumers use the macros through register helpers and SOC15 MMIO accessors, command-packet register programming, golden-setting tables, debugfs/perf paths, KFD debug/trap setup, reset handling, virtualization paths, and hang diagnostics.

The main macro families in this range are:

- `GFX_ICG_GL2C_CTRL*`, `CHI_CHR_MGCG_OVERRIDE`, `ICG_CHA_CTRL`, and `ICG_CHC_CLK_CTRL`: clock-gating and clock-override fields for GL2C/channel logic.
- `CP_MES_DM_INDEX_*`, `CP_MEC_DM_INDEX_*`, and `CP_GFX_RS64_DM_INDEX_*`: full-width indexed address/data windows for command-processor and RS64 debug-memory access.
- `CPG_PSP_DEBUG`, `CPC_PSP_DEBUG`, `GC_EA_CPWD_SECURE_CTRL`, `GC_EA_CPWD_SDP_SECLEVEL_*`, `GRBM_SEC_CNTL`, `GRBM_CAM_*`, `RLC_REG_SEC_INT_STATUS`, and `RLC_UTC_BYPASS_CNTL`: PSP/security, firewall/violation, client security-level, remapping, and bypass controls.
- `GFX_IMU_*`: IMU mailbox, scratch, access permission, RLC RAM index/address/data, core reset/stall/debug, graphics reset, bootloader address/size, instruction RAM, and data RAM fields.
- `GRBMH_*`: graphics register bus manager hub control/status, interface, fine-grained clock-gating target, soft reset, read-error, clock enable, invalid-pipe, sync, and unit-disable fields.
- `GE_*`, `CC_GC_*`, and `PA_*`: shader-array enablement, graphics-engine busy state, safe-register data paths, setup/clipper/raster/debug controls, and PA FIFO/debug fields.
- `SQ_*`, `SQC_*`, `LDS_CONFIG`, and `SP_CONFIG`: shader queue and cache configuration, DSM/error-injection controls, watch registers, indirect register indexing, GL1X status, perf snapshots, interrupt masking, and command-control macros.
- `SX_DEBUG_BUSY*`: dense one-bit status maps for SX color/export, scoreboard, blend, position, and index internal busy/valid signals.
- `SPI_*`, `SPIS_DEBUG_READ`, and `BCI_DEBUG_READ`: shader processor input/debug state, CU masks for graphics/HP3D/compute queues, wave lifetime counters, load-balancer counters, GDS credits, export buffer sizes, wavefront active counters, trap-screen ranges, and crawler configuration.
- `TD_*` and `TA_*`: texture-data and texture-address control/status/power/scratch/credit fields, ending at the first `TA_CNTL_AUX` shift definitions.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU consumers:

1. Select the GC 12.0.0 register header for the active ASIC generation.
2. Select the matching `reg...` address macro from `gc_12_0_0_offset.h`.
3. Read an existing register value, build an MMIO write value, build a command-packet register write, or decode status/debug output.
4. Use the `__SHIFT`/`__MASK` pair, usually via `REG_SET_FIELD` or `REG_GET_FIELD`, to pack or extract a field.
5. Apply the value in initialization, power/clock setup, secure/PSP access configuration, IMU firmware/RLC RAM handling, reset, graphics pipeline setup, shader/debug/trap setup, perf/debug capture, or hang recovery.

For security and PSP registers, driver and firmware setup code writes privilege, secure-register, client-ID, and bypass fields before protected register access or secure memory traffic is expected. For IMU registers, code programs address/index/data windows and reset/core-control fields around bootloader, instruction RAM, data RAM, and RLC RAM interactions. For status/debug families such as `GRBMH_STATUS`, `SX_DEBUG_BUSY*`, and `SPI_DEBUG_BUSY`, runtime code reads and decodes bitmaps during idle waits, reset diagnosis, hang dumps, or hardware validation. For SQ/SPI/TD/TA configuration registers, programming is part of engine bring-up, shader/debug feature setup, wavefront scheduling, and graphics/compute pipeline behavior.

The header does not describe ordering constraints, polling loops, clear-on-read behavior, sticky-bit clearing, privilege checks, firmware handshakes, or reset sequencing. Those rules live in AMDGPU engine code, firmware contracts, and hardware programming guides.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe hardware register fields whose state is owned by the GPU, firmware, and AMDGPU runtime programming.

Clock-gating override and power-control fields persist as hardware configuration until reprogrammed, reset, or lost during power transitions. Mispacked override fields can leave clocks forced on/off, masking power bugs or causing hangs if a block is gated while active. Security and PSP fields are especially sensitive: `CPG_PSP_DEBUG`, `CPC_PSP_DEBUG`, `GC_EA_CPWD_SECURE_CTRL`, client security maps, GRBM CAM remap fields, and UTC bypass controls can change access policy, attribution, and translation behavior. Full-register writes must preserve reserved bits unless the hardware sequence requires a complete write.

IMU RAM index/address/data fields are transient access windows, but the data they program can affect persistent firmware/RLC behavior until reset or replacement. Core-control and reset fields can stop, reset, or debug the IMU and graphics-related blocks. Bootloader address/size fields must match firmware memory layout and alignment.

GRBMH, PA, SQ, SX, SPI, TD, and TA fields mix persistent configuration with live status. Configuration fields such as SQ cache behavior, LDS and DSM controls, PA clip/raster behavior, SPI CU masks, wave lifetime limits, GDS credits, trap-screen ranges, texture-data controls, and texture-address credits remain active until overwritten. Status and debug fields can be sampled live, can be sticky, or can require clear/acknowledge sequences defined outside this header. Counter/status families can race with hardware activity if sampled without the documented snapshot or idle sequence.

Trap-screen base/mask registers and watch/interrupt fields influence debug and exception handling for waves. Incorrect values can suppress expected traps, trap the wrong address range, or make diagnostics misleading. CU mask and WGP mask fields affect work distribution; bad masks can silently reduce available compute/graphics capacity or target disabled hardware.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.0.0 register set remaining synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h` provides matching register addresses and base indices.
- Common AMDGPU helpers and SOC15 accessors provide field packing/extraction and MMIO access.
- `gfx_v12_0.c`, `gfx_v12_1.c`, IMU code, KFD debug code, reset/hang-dump paths, golden-setting tables, and performance/debug tooling are representative consumers of these register families.

Important integration points include PSP/secure register access setup, IMU boot and RAM programming, RLC interaction, secure/firewall violation diagnostics, clock-gating override programming, GRBM/GRBMH idle waits and reset diagnosis, PA/GE graphics pipeline initialization, SQ/SQC/LDS shader engine setup, KFD and shader trap/watchpoint handling, SPI CU masking and wavefront accounting, wave lifetime tracking, load-balancer/per-WGP counters, GDS credit configuration, SX/SPI/TD/TA debug capture, and texture unit configuration.

The companion offset header has GC 12.0.0 address symbols for registers such as `regCPG_PSP_DEBUG` and `regTD_CNTL`. A matching `gc_12_0_0_default.h` file was not present in the local `asic_reg/gc` directory, so validation for defaults must come from another generated source or AMD's register database if needed.

## Risks And Edge Cases

- Generated-header drift is the primary risk. Wrong shifts or masks compile successfully but program or decode the wrong hardware bits.
- This chunk begins and ends mid-family: `GFX_ICG_GL2C_CTRL` shift/comment context is before the range, and `TA_CNTL_AUX` continues after the range. File-level research must merge adjacent chunks before drawing complete-family conclusions.
- Security and bypass fields can affect isolation and privileged access. `GPA_OVERRIDE`, `UCODE_VF_OVERRIDE`, `SECURE_REG_OVERRIDE`, trusted memory zone, security-level maps, GRBM CAM remap, and UTC bypass fields should be changed only under documented sequences.
- Indexed address/data windows are easy to misuse. CP debug-memory, IMU RLC RAM, instruction RAM, and data RAM windows require correct address alignment, valid bits, and access ordering not encoded in the masks.
- Reset and core-control bits have side effects. `GFX_IMU_CORE_CTRL`, `GFX_IMU_GFX_RESET_CTRL`, `GRBMH_SOFT_RESET`, and related clock/power controls can stop or reset active hardware if written at the wrong time.
- Busy/status bitmaps are dense and similar across registers. Mislabeling `GRBMH_STATUS`, `SX_DEBUG_BUSY*`, or `SPI_DEBUG_BUSY` fields can lead to incorrect hang attribution.
- Repeated CU/WGP mask families are structurally similar but target different graphics, HP3D, and compute paths. Copy/paste mistakes can disable the wrong queue class or shader array.
- DSM/error-injection and debug-clear fields can perturb hardware state. Test-only fields in SQ, PA, SC, PH, SPI, TD, and related blocks should not be enabled by production paths accidentally.
- Counter and lifetime-status fields may require snapshot, reset, or latch handling. The shift/mask header cannot express atomicity, overflow, or clear timing.
- Reserved fields appear in many registers. Read-modify-write callers should preserve reserved bits unless the hardware specification says otherwise.

## Test Signals

Useful validation is a mix of generated-data checks, build coverage, and hardware/runtime diagnostics:

- Kernel build coverage for AMDGPU files that include `gc_12_0_0_sh_mask.h`, especially GFX 12, IMU, KFD debug, reset, hang-dump, power/clock, and perf/debug paths.
- Mechanical comparison against AMD's authoritative GC 12.0.0 register database for every `__SHIFT` and `__MASK` value in this range.
- Cross-check that every register comment in this chunk has a matching `reg...` address macro in `gc_12_0_0_offset.h` with the expected base index.
- Static sanity checks that masks align with shifts, full-width data fields use `0xFFFFFFFFL`, repeated client/CU/WGP/status families remain structurally consistent, and bitmaps do not overlap unless documented.
- Bring-up tests that apply clock-gating and golden-setting programming, then verify idle, suspend/resume, and reset behavior on GC 12.0.0 hardware.
- PSP/security tests that exercise secure register access, VF/VMID violation handling, firewall violation counters, client security-level maps, GRBM CAM remapping, and UTC bypass behavior with expected fault attribution.
- IMU tests that boot firmware, program RLC/I/D RAM windows, exercise core reset/stall/debug paths, and confirm no invalid RAM index/address behavior.
- Graphics and compute workload tests that validate PA/GE/SQ/SPI/TD/TA configuration under draw, dispatch, trap/debug, wave lifetime, CU mask, and texture-heavy workloads.
- Hang/debug dump tests that decode `GRBMH_STATUS`, `SX_DEBUG_BUSY*`, `SPI_DEBUG_BUSY`, `SQG_STATUS`, `TD_STATUS`, wavefront counters, trap-screen state, and error-injection/debug registers coherently.
- Perf/counter tests that reset, select, and read SPI load-balancer, wavefront, lifetime, GDS credit, and debug counters under controlled workload activity.
- Runtime warning signals include unexpected VM/security faults, failed PSP/IMU access, firmware boot failures, GPU reset loops, engines that never become idle, wrong busy-block attribution, missing shader traps, disabled CUs/WGPs, bad wavefront counts, texture unit hangs, or power regressions after clock-gating changes.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002578`. It covers lines 22794-25201 of `gc_12_0_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the partial `GFX_ICG_GL2C_CTRL` and `TA_CNTL_AUX` families and to place these CP/PSP, IMU, GRBMH, PA, SQ, SX, SPI, TD, and TA definitions in the full GC 12.0.0 register map.

### subset-b-002579: lines 25202-27680

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 25202-27680

## Purpose

This chunk is generated AMD GC 12.0.0 graphics-core register bitfield metadata. It contains C preprocessor constants only: each register field is represented by a `__SHIFT` value and a `_MASK` value used to pack or decode 32-bit MMIO register values. There are no executable functions, structs, allocation paths, locks, callbacks, or persistence routines in this slice.

The selected range starts in the tail of the texture-address `TA_CNTL_AUX` definition, continues through texture address status and scratch fields, then covers a large render-backend/depth-buffer block, color-buffer/global-backend topology controls, RMI and UTCL1 controls/status, shader-program register layouts for pixel/geometry/hull stages, SPI arbitration and debug controls, TCP watchpoints, RAS signature registers, and the beginning of the command-buffer depth/stencil render-state register set. The final line is inside `DB_SHADER_CONTROL`; the remaining masks for that register continue after this chunk.

Although this path is under a `ceph-client` source tree, the file is AMD GPU driver hardware metadata. It is coupled to the matching GC 12.0.0 register offset header and to AMDGPU/AMDKFD code using `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, and table-driven golden-register programming.

## Important APIs, Types, And Macros

The public interface in this chunk is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` identifies the low bit of a hardware field.
- `<REGISTER>__<FIELD>_MASK` identifies the bit range for the same field.
- Register comments such as `//DB_DEBUG`, `//SPI_SHADER_PGM_RSRC1_PS`, or `//DB_RENDER_CONTROL` group field macros by hardware register.
- Address-block comments such as `gc_gfx_se_gfx_se_rbdec`, `gc_gfx_se_rmi_gfx_se_rmidec`, `gc_gfx_se_gfx_se_shdec`, `gc_gfx_se_gfx_se_tcpdec`, and `gc_gfx_se_gfx_se_gfxdec0` group the registers by hardware decode block.

Major register families represented here:

- Texture-address tail: remaining `TA_CNTL_AUX` fields include anisotropic filtering, gather/swizzle behavior, deterministic-mode disables, cubemap slice clamp, small-negative truncation, and array round mode. `TA_CNTL2` adds component-storage, request-id, element-size hash, coordinate truncation, unlit-quad elimination, and PRT-plus accumulation controls. `TA_STATUS` provides FIFO non-empty and busy bits for texture-address subunits, and `TA_SCRATCH` exposes a full-width scratch field.
- Depth/render backend debug and timing: `DB_DEBUG`, `DB_DEBUG2`, `DB_DEBUG3`, `DB_DEBUG4`, `DB_DEBUG5`, `DB_DEBUG6`, and `DB_DEBUG7` cover compression disables, forced depth/stencil reads, HiZ/HiS behavior, fast Z/stencil disables, viewport/z-plane optimization, tile/cache/data-forwarding behavior, coherency stalls, VRS interactions, NOZ behavior, panic/test/spare bits, and several workaround-style controls. `DB_CREDIT_LIMIT`, `DB_WATERMARKS`, `DB_FREE_CACHELINES`, `DB_FIFO_DEPTH1..4`, `DB_RING_CONTROL`, `DB_MEM_ARB_WATERMARKS`, `DB_MEM_CONFIG`, `DB_ARB_CONFIG`, and `DB_SUMMARIZER_TIMEOUTS` describe DB buffering, credits, watermarks, SRAM allocation, arbitration, and timeout tuning.
- Backend topology and color-buffer controls: `CC_RB_BACKEND_DISABLE`, `GB_ADDR_CONFIG`, `GB_ADDR_CONFIG_1`, `GB_BACKEND_MAP`, `GB_GPU_ID`, and `GB_ADDR_CONFIG_READ` encode render-backend harvesting and graphics-block topology such as pipe count, compressed fragments, RBs per shader engine, shader-engine count, pipe interleave size, and packetizer count. `CB_HW_CONTROL_4`, `CB_HW_CONTROL_3`, `CB_HW_CONTROL`, `CB_HW_CONTROL_1`, `CB_HW_CONTROL_2`, `CB_HW_MEM_ARBITER_CTL`, `CB_FGCG_SRAM_OVERRIDE`, and `CB_CACHE_EVICT_POINTS` cover CB request throttling, DCC/cache behavior, arbitration, SRAM clock gating override, and cache eviction thresholds.
- SPI and shader program state: `SPI_PQEV_CTRL` and `SPI_EXP_THROTTLE_CTRL` define queue/event and export-throttle controls. The shader-decode block defines checksum, program address, resource, user-data, request-control, meshlet, GS output, and accumulator registers for PS, GS/ES, and HS/LS stages. `SPI_SHADER_PGM_RSRC1_*` and `SPI_SHADER_PGM_RSRC2_*` are especially dense, covering VGPR/SGPR counts, priority, float mode, DX10 clamp/debug mode, LDS size, scratch enable, user SGPR counts, exception enables, shared VGPR count, and similar stage-specific dispatch metadata.
- RMI and UTCL1 memory interface: `RMI_GENERAL_CNTL`, `RMI_GENERAL_CNTL1`, `RMI_GENERAL_STATUS`, `RMI_SUBBLOCK_STATUS0..3`, `RMI_XBAR_CONFIG`, `RMI_PROBE_POP_LOGIC_CNTL`, `RMI_UTC_XNACK_N_MISC_CNTL`, `RMI_DEMUX_CNTL`, `RMI_UTCL1_CNTL1`, `RMI_UTCL1_CNTL2`, formatter controls, scoreboard controls/status, crossbar arbiter controls, clock controls, CID mapping, XNACK debug, spare registers, and `CC_RMI_REDUNDANCY` describe routing, backpressure, UTCL1 behavior, scoreboard state, interface clocking, and redundancy. The separate `UTCL1_CTRL_1`, `UTCL1_HASH_CTRL`, `UTCL1_ALOG`, and `UTCL1_STATUS` registers describe UTCL1 request buffering, hash/client behavior, address logging, and status.
- SPI arbitration/debug and TCP watchpoints: `SPI_ARB_PRIORITY`, `SPI_ARB_CYCLES_0/1`, `SPI_WCL_PIPE_PERCENT_*`, `SPI_USER_ACCUM_VMID_CNTL`, `SPI_GDBG_PER_VMID_CNTL`, `SPI_COMPUTE_QUEUE_RESET`, `SPI_COMPUTE_WF_CTX_SAVE`, and `SPI_SAVE_RESTORE_STATUS` define SPI scheduling weights, wave-context limits, per-VMID debug accumulation, queue reset, and wavefront context-save status. `TCP_WATCH0..3_ADDR_H/L` and `TCP_WATCH0..3_CNTL` define four TCP memory-watch channels with address, mask, mode, and VMID controls.
- RAS signatures: `RAS_SIGNATURE_CONTROL`, `RAS_SIGNATURE_MASK`, and per-block signature registers for SX, DB, PA, SC, SPI, CB, BCI, and GE expose RAS signature collection/inspection points.
- Draw/depth state: `DB_RENDER_CONTROL`, `DB_DEPTH_VIEW`, `DB_DEPTH_VIEW1`, `DB_RENDER_OVERRIDE`, `DB_RENDER_OVERRIDE2`, `DB_DEPTH_SIZE_XY`, `DB_Z_INFO`, `DB_STENCIL_INFO`, depth/stencil read/write base registers, `DB_GL1_INTERFACE_CONTROL`, `DB_MEM_TEMPORAL`, depth bounds, `DB_COUNT_CONTROL`, `DB_VIEWPORT_CONTROL`, `DB_SPI_VRS_CENTER_LOCATION`, and the beginning of `DB_SHADER_CONTROL` describe depth/stencil clear/copy/decompress behavior, view selection, render overrides, surface dimensions, Z/stencil formats and swizzle modes, base addresses, GL1 speculation/compression modes, temporal hints, occlusion/count controls, viewport clamp, VRS sample centers, and shader/depth interaction.

Several definitions are full-width masks, including scratch or address-base fields such as `TA_SCRATCH__SCRATCH_MASK`, `DB_DFD_INDIRECT_DAT__DAT_MASK`, depth/stencil base fields, depth bounds, and RAS signature fields. Full-width masks are packing metadata only; they do not imply the register is safe for arbitrary writes.

## Control Flow

This header has no direct runtime control flow. The operational flow is indirect:

1. GC 12 code includes `gc/gc_12_0_0_sh_mask.h` together with `gc/gc_12_0_0_offset.h`.
2. A call site chooses a register offset, for example `regGB_ADDR_CONFIG`, `regRMI_GENERAL_CNTL`, `regSPI_SHADER_PGM_RSRC1_PS`, `regDB_RENDER_CONTROL`, or `regDB_SHADER_CONTROL`.
3. The call site composes or decodes a register value using field helpers such as `REG_SET_FIELD` or `REG_GET_FIELD`, which rely on the exact `__SHIFT` and `_MASK` names in this file.
4. The value is read from or written to hardware through SOC15 register helpers, debug register accessors, firmware/golden-register tables, queue setup, reset paths, power-management restore paths, or draw/dispatch state programming.

Concrete in-tree consumers for this GC 12 namespace include:

- `amdgpu/gfx_v12_0.c`, which includes this header and reads `regGB_ADDR_CONFIG`; it decodes `GB_ADDR_CONFIG` fields into `adev->gfx.config.gb_addr_config_fields` for packetizers, pipes, compressed fragments, RBs per SE, shader engines, and pipe interleave.
- `amdgpu/imu_v12_0.c`, which programs golden values for registers in this range, including repeated per-index `regRMI_GENERAL_CNTL` writes and `regGB_ADDR_CONFIG`.
- `amdgpu/soc24.c`, which exposes `regGB_ADDR_CONFIG` through the device register read path and returns the cached `adev->gfx.config.gb_addr_config` value when available.
- `amdgpu/mes_v12_0.c`, `amdgpu/sdma_v7_0.c`, and `amdgpu/gfxhub_v12_0.c`, which include the GC 12.0.0 generated register namespace for adjacent queue, SDMA, and VM/cache programming.
- Display code such as `display/amdgpu_dm/amdgpu_dm_plane.c`, which reads `regGB_ADDR_CONFIG` through the same field helpers to derive tiling/display-plane layout information.

## State And Persistence Behavior

The file stores no software state. It describes hardware state that may be software-programmed, hardware-owned, sticky, read-only, write-only, self-clearing, indexed per shader engine, or restored by firmware depending on the register.

The most visible persistent software state tied to this chunk is `adev->gfx.config.gb_addr_config` and its decoded `gb_addr_config_fields`, populated from `GB_ADDR_CONFIG` in GC 12 initialization and reused by SOC24 register reporting and display/tiling paths. Incorrect masks for those fields can persist wrong topology assumptions after initialization.

Other represented state includes DB debug/workaround configuration, DB FIFO and arbitration watermarks, CB hardware controls, RMI routing/status/scoreboard state, UTCL1 address-translation controls/status, shader-program resource descriptors, TCP watchpoint configuration, RAS signature registers, depth/stencil surface state, and draw-time depth/shader controls. Some fields remain programmed until GPU reset, suspend/resume restore, power-gating restore, firmware reinitialization, context-state load, or explicit driver writes. Status, busy, scoreboard, fault, and signature fields are generally hardware-produced observations, while debug, DSM/spare, watchpoint, and override fields can perturb execution when written.

The header does not encode access permissions, reset defaults, broadcast/indexing semantics, reserved-bit requirements, sequencing requirements, or whether a field is latched or self-clearing. Call sites must preserve unrelated bits, use the matching offset header, and follow ASIC programming-guide ordering.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h`. In that file, this chunk's registers map to offsets such as `regTA_CNTL_AUX`, `regTA_CNTL2`, `regDB_DEBUG`, `regDB_DEBUG5`, `regGB_ADDR_CONFIG`, `regGB_ADDR_CONFIG_1`, `regGB_ADDR_CONFIG_READ`, `regRMI_GENERAL_CNTL`, `regRMI_UTCL1_CNTL1`, `regUTCL1_CTRL_1`, `regSPI_SHADER_PGM_RSRC1_PS`, `regSPI_ARB_PRIORITY`, `regTCP_WATCH0_CNTL`, `regRAS_SIGNATURE_CONTROL`, `regDB_RENDER_CONTROL`, `regDB_COUNT_CONTROL`, and `regDB_SHADER_CONTROL`.

Integration points include:

- GC 12 graphics initialization and topology discovery in `gfx_v12_0.c`.
- IMU/RLC golden-register programming in `imu_v12_0.c`.
- SOC24 register-access/debug paths in `soc24.c`, especially indexed register access guarded by `adev->grbm_idx_mutex`.
- MES, SDMA, GFXHUB, KFD, and display code that compiles in the same generated GC 12 namespace and relies on shift/mask compatibility.
- Clear-state and context-state programming for draw/depth registers such as `DB_RENDER_CONTROL`, `DB_COUNT_CONTROL`, and `DB_SHADER_CONTROL`.
- Hardware diagnostics, perf/debug, RAS, TCP watchpoint, and register-dump tooling that decodes status/signature/watch registers from this range.

The chunk has artificial boundaries. It starts after the first `TA_CNTL_AUX` fields and ends before all `DB_SHADER_CONTROL` masks are visible, so adjacent chunks are required before making whole-register or whole-file statements about either boundary register.

## Risks And Edge Cases

- Header/offset mismatch is the primary risk. Using GC 12.0.0 masks with another generation's offset header can compile while silently decoding or programming the wrong bits.
- Dense debug/control registers such as `DB_DEBUG*`, `DB_RENDER_OVERRIDE*`, `CB_HW_CONTROL*`, `RMI_*CNTL*`, and `SPI_SHADER_PGM_RSRC*` contain many adjacent fields. A stale shift or mask can corrupt unrelated behavior without a compiler warning.
- `GB_ADDR_CONFIG`, `GB_ADDR_CONFIG_1`, and `GB_ADDR_CONFIG_READ` are topology-sensitive and feed persistent driver configuration. Wrong decoding can break tiling, render-backend harvesting assumptions, display-plane layout, compressed-fragment handling, or pipe interleave calculations.
- `DB_DEBUG*` and `DB_RENDER_OVERRIDE*` fields can disable compression, fast paths, coherency stalls, z-plane optimizations, or NOZ behavior. Mistakes may appear only as workload-specific hangs, depth/stencil corruption, VRS artifacts, performance cliffs, or power regressions.
- RMI and UTCL1 fields influence memory-interface routing, XNACK behavior, address translation, scoreboard handling, and crossbar arbitration. Incorrect programming can produce stale translations, bad backpressure, memory-ordering faults, or hard-to-reproduce GPU hangs.
- Shader program resource fields are ABI-like hardware descriptors. Incorrect VGPR/SGPR, LDS, scratch, exception, shared-VGPR, or user-SGPR masks can break dispatch, trap/debug behavior, context save/restore, or shader execution only for specific stages.
- TCP watchpoint and SPI debug controls are diagnostic-sensitive. Wrong VMID, mask, mode, or queue-reset fields can miss real faults, trigger false debug events, or disrupt active compute queues.
- RAS signature registers and masks must remain aligned with hardware reliability tooling; misdecoding signatures can hide real error signatures or create false telemetry.
- The header exposes reserved, spare, and full-width fields. Visible masks should not be treated as safe production write masks without ASIC-specific documentation.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware-oriented smoke and regression coverage:

- Build coverage for AMDGPU, MES, SDMA, GFXHUB, KFD, display, and IMU/RLC paths that include `gc_12_0_0_sh_mask.h` with `gc_12_0_0_offset.h`.
- Generated-header checks that each `__SHIFT` has the intended `_MASK`, masks align with shifts, fields do not overlap within a register except documented aliases/full-width fields, and register names match `gc_12_0_0_offset.h`.
- Static comparison against the authoritative GC 12.0.0 register database for this line range, with special attention to repeated shader user-data registers, TCP watch channels, RMI scoreboard/status fields, and `DB_SHADER_CONTROL` continuation across the chunk boundary.
- Topology/init tests confirming `gfx_v12_0.c` decodes `GB_ADDR_CONFIG` into expected `adev->gfx.config` values and that `soc24.c` reports the cached value correctly.
- Golden-register tests for `imu_v12_0.c` values touching `regRMI_GENERAL_CNTL` and `regGB_ADDR_CONFIG`, verifying mask/value pairs preserve non-target fields and match ASIC defaults.
- Graphics tests stressing depth/stencil clears, copies, decompression, HTILE/HiZ/HiS behavior, Z/stencil formats, depth bounds, occlusion counts, VRS center locations, and shader depth/export behavior.
- Suspend/resume, GPU reset, runtime power-management, and SR-IOV smoke tests that cover restoration of DB/CB/RMI/UTCL1/SPI state.
- RAS/debug tests for signature collection, TCP watchpoints, SPI per-VMID debug accumulation, compute queue reset/context-save status, RMI status/scoreboard reads, and UTCL1 address logging.

### subset-b-002580: lines 27681-30173

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 27681-30173

## Scope

This chunk covers a generated AMD GC 12.0.0 shader/register mask header section. It starts at the tail of `DB_SHADER_CONTROL` mask definitions, continues through depth/stencil, rasterizer/scissor, viewport, clip, variable-rate shading, pixel-shader input, scratch-ring, shader-export, SX blend optimization, and color-blend control field definitions, and ends at the `PA_CL_POINT_X_RAD` register marker before that register's fields appear in the next chunk.

The file is a register bitfield map only. It defines C preprocessor constants and has no functions, structs, variables, dynamic storage, or executable control flow. Each register field is represented by the normal AMDGPU generated pair:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

The adjacent `gc_12_0_0_offset.h` header supplies the register addresses. This `*_sh_mask.h` chunk supplies the bit positions and masks used to compose or decode the 32-bit values written to those registers.

## Purpose

The purpose of this range is to encode the ABI between GC 12 graphics hardware and the AMDGPU/KFD driver for render-state programming. The fields here are the low-level layout definitions for state that higher layers normally program through PM4 packets, ring commands, clear-state tables, firmware initialization, or direct MMIO helpers.

The covered state is centered on the graphics pipeline after primitive setup and before/around pixel export:

- Depth-buffer and stencil behavior through `DB_SHADER_CONTROL`, `DB_DEPTH_CONTROL`, `DB_STENCIL_CONTROL`, `DB_EQAA`, alpha-to-mask, stencil ref/op/read/write masks, and memory temporal/speculative-read policy.
- Screen, window, generic, cliprect, and per-viewport scissor rectangles, plus 16 viewport top-left/bottom-right pairs.
- User clip planes, guard-band clip/discard adjustment, per-viewport scale/offset/depth range, and near-clip control.
- Rasterizer routing and steering controls such as `PA_SC_RASTER_CONFIG`, `PA_SC_RASTER_CONFIG_1`, tile steering override, pipe/VMID selection, and screen extent control.
- Variable-rate shading surfaces and overrides through `PA_SC_VRS_*` base, size, info, override, and feedback fields.
- Pixel shader interpolation/input/export formats through `SPI_PS_IN_CONTROL`, `SPI_INTERP_CONTROL_0`, `SPI_SHADER_*_FORMAT`, `SPI_BARYC_*`, `SPI_PS_INPUT_ENA`, `SPI_PS_INPUT_ADDR`, and 32 `SPI_PS_INPUT_CNTL_n` registers.
- Scratch ring base/size through `SPI_TMPRING_SIZE` and `SPI_GFX_SCRATCH_BASE_LO/HI`.
- Shader export and color blend behavior through `SX_PS_DOWNCONVERT*`, `SX_BLEND_OPT_*`, `SX_MRT[0-7]_BLEND_OPT`, and `CB_BLEND[0-7]_CONTROL`.

## Important Macro Families

### Depth, Stencil, and Coverage State

The chunk begins in the middle of `DB_SHADER_CONTROL`, carrying masks for late pixel-shader/depth-buffer behavior such as kill/discard enable, coverage-to-mask, mask export, hierarchical-Z fallback execution, alpha-to-mask disable, depth-before-shader, conservative-Z export, dual-quad disable, ordered pixel shader, pre-shader depth coverage, OREO blend, and intrinsic-rate override. The corresponding shifts are immediately above this chunk, so consumers must see the full generated header rather than treating this line span as a standalone include.

`DB_DEPTH_CONTROL` defines enable bits and compare-function fields for stencil, Z, Z-write, depth bounds, Z function, backface handling, front stencil function, and backface stencil function. In GC 12 this chunk names bits 30 and 31 as reserved fields rather than the older color-write-on-depth-fail/pass names found in some sibling ASIC headers, so cross-generation code must not assume semantic compatibility for those high bits.

`DB_STENCIL_CONTROL` describes front and back stencil fail, Z-pass, and Z-fail operations. `DB_STENCIL_REF`, `DB_STENCIL_OPVAL`, `DB_STENCIL_READ_MASK`, and `DB_STENCIL_WRITE_MASK` provide paired front/back 8-bit values. These values are command-stream state, not kernel-owned persistent policy; the kernel's role is to provide correct masks for command construction and decode.

`DB_EQAA` and `DB_ALPHA_TO_MASK` cover enhanced quality anti-aliasing and alpha-to-coverage details: mask export sample count, alpha-to-mask sample count, high-quality intersections, static anchor associations, overrasterization amount, post-Z overrasterization, alpha-to-mask offsets, and offset rounding.

`SC_MEM_TEMPORAL` and `SC_MEM_SPEC_READ` expose temporal and speculative-read settings for VRS, HiZ, and HiS paths. These fields affect cache/memory behavior around raster/depth surfaces and are sensitive to hardware programming guidance.

### Viewports, Scissors, Clip Rectangles, and Clip Planes

The largest early block is the repeated viewport and scissor geometry layout:

- `PA_SC_VPORT_0_TL` through `PA_SC_VPORT_15_BR` encode 16 viewport top-left and bottom-right integer rectangles with 16-bit X/Y halves.
- `PA_SC_SCREEN_SCISSOR_TL/BR`, `PA_SC_WINDOW_OFFSET`, `PA_SC_WINDOW_SCISSOR_TL/BR`, `PA_SC_GENERIC_SCISSOR_TL/BR`, and `PA_SC_VPORT_SCISSOR_0_TL/BR` through `PA_SC_VPORT_SCISSOR_15_TL/BR` provide screen, window, generic, and per-viewport scissor bounds. Several top-left fields include `WINDOW_OFFSET_DISABLE`, and bottom-right fields include `DX10_DIAMOND_TEST_ENA` depending on the register.
- `PA_SC_CLIPRECT_RULE` and `PA_SC_CLIPRECT_0_TL/BR` through `PA_SC_CLIPRECT_3_TL/BR` define rule bits and four clip rectangles. The corresponding `PA_SC_CLIPRECT_0_EXT` through `PA_SC_CLIPRECT_3_EXT` add extended coordinate bits and discard flags.
- `PA_SC_EDGERULE` provides the table entries used by rasterization edge inclusion rules.
- `PA_SU_HARDWARE_SCREEN_OFFSET` defines signed or packed hardware screen offset fields.

The `PA_CL_UCP_0_X/Y/Z/W` through `PA_CL_UCP_5_X/Y/Z/W` field groups are full 32-bit values for six user clip planes. `PA_CL_PROG_NEAR_CLIP_Z` is another full-width programmed clip value. The later `PA_CL_GB_*_ADJ` and `PA_CL_VPORT_*` groups are also full-width data fields, typically floating-point bit patterns for guard-band and viewport scale/offset state.

### Raster Configuration and Routing

`PA_RATE_CNTL` provides packed sample or shading-rate control fields. `PA_SC_RASTER_CONFIG` contains the detailed tile-pipe, shader-engine, packer, rasterizer, scan converter, and SE map selectors used to route work across graphics pipes and shader engines. `PA_SC_RASTER_CONFIG_1` extends this with extra SE-pair mapping fields. These definitions are tightly coupled to ASIC topology, harvest configuration, and the matching offset/register list.

`PA_SC_SCREEN_EXTENT_CONTROL`, `PA_SC_TILE_STEERING_OVERRIDE`, `CB_CP_PIPEID`, and `CB_CP_VMID` expose additional screen-extent, pipe steering, pipe ID, and VMID fields. Incorrect values here can send raster or color-buffer traffic to the wrong backend resources.

### Variable-Rate Shading and Surface Addresses

The VRS-related groups are:

- `PA_SC_VRS_OVERRIDE_CNTL`, with override mode/rate/combiner fields.
- `PA_SC_VRS_RATE_FEEDBACK_BASE`, `_EXT`, and `_SIZE_XY`, defining feedback surface address and dimensions.
- `PA_SC_VRS_INFO`, exposing or programming rate and mode bits.
- `PA_SC_VRS_RATE_BASE`, `_EXT`, and `_SIZE_XY`, defining the VRS rate image surface address and dimensions.

Address fields are split into low and high/ext registers. Writers must preserve the expected address granularity and combine with the matching offset definitions; these macros only describe bit placement.

### Pixel Shader Input and Export State

`SPI_PS_IN_CONTROL` controls pixel-shader input count, parameter generation, barycentric/POS interpolation details, and related flags. `SPI_INTERP_CONTROL_0` contains point sprite, perspective, sample, center, flat-shade, and custom interpolation control fields. `SPI_SHADER_IDX_FORMAT`, `SPI_SHADER_POS_FORMAT`, `SPI_SHADER_Z_FORMAT`, and `SPI_SHADER_COL_FORMAT` define shader export formats for indices, position exports, Z/stencil/sample-mask style exports, and up to eight color exports.

`SPI_BARYC_CNTL` and `SPI_BARYC_SSAA_CNTL` provide barycentric coordinate policy, including perspective/linear center/centroid/sample control and supersampling controls.

`SPI_PS_INPUT_ENA` and `SPI_PS_INPUT_ADDR` are bitmaps for up to 32 pixel-shader inputs. The 32 `SPI_PS_INPUT_CNTL_n` groups describe each input slot's semantic offset, default value, flat-shade control, cyl-wrap, attractor, primitive-attribute, default flag, and in the first 20 slots additional attribute/per-sample/floating-point control fields. Slots 20-31 have a shorter field set in this generated table. These registers are a key ABI between shader compilation metadata and draw-time command emission.

`SPI_TMPRING_SIZE` and `SPI_GFX_SCRATCH_BASE_LO/HI` describe the temporary/scratch ring configuration used by shader execution. These interact with GPU virtual addresses and per-process or per-queue scratch allocation handled elsewhere in AMDGPU/KFD.

### SX and Color Blend State

`SX_PS_DOWNCONVERT_CONTROL` and `SX_PS_DOWNCONVERT` define per-MRT downconversion controls and formats. `SX_BLEND_OPT_EPSILON` supplies per-MRT epsilon settings, and `SX_BLEND_OPT_CONTROL` supplies per-MRT blend optimization disable/enable and optimization mode fields.

`SX_MRT0_BLEND_OPT` through `SX_MRT7_BLEND_OPT` define repeated source/destination optimization and combiner function fields for color and alpha blend paths. `CB_BLEND0_CONTROL` through `CB_BLEND7_CONTROL` define repeated render-target blend equation state: color source blend, color combiner, color destination blend, alpha source blend, alpha combiner, alpha destination blend, separate-alpha enable, blend enable, and ROP3 disable. These are per-MRT render state fields and are directly tied to color export and color-buffer behavior.

## APIs, Types, and Functions

There are no C APIs, types, or functions in this chunk. The usable interface is the macro naming contract consumed by generic AMDGPU helpers:

- `REG_FIELD_SHIFT(reg, field)` expands to `reg##__##field##__SHIFT`.
- `REG_FIELD_MASK(reg, field)` expands to `reg##__##field##_MASK`.
- `REG_SET_FIELD(orig, reg, field, val)` clears the masked field in a 32-bit word and inserts `val` at the generated shift.
- `REG_GET_FIELD(value, reg, field)` masks and shifts a field out of a 32-bit word.
- SOC15 register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, and field-write helpers combine this field layout with the address macros from the sibling offset header.

Direct include users for the GC 12.0.0 mask header in this source tree include `amdgpu/gfx_v12_0.c`, `amdgpu/soc24.c`, `amdgpu/mes_v12_0.c`, `amdgpu/sdma_v7_0.c`, `amdgpu/gfxhub_v12_0.c`, `amdgpu/imu_v12_0.c`, `amdgpu/amdgpu_amdkfd_gfx_v12.c`, `amdkfd/kfd_mqd_manager_v12.c`, and `amdkfd/kfd_device_queue_manager_v12.c`. The specific render-state macros in this chunk also align with clear-state tables such as `amdgpu/clearstate_gfx12.h`, where many of the same register names appear as initialized context state.

## Control Flow and Data Flow

This header has no runtime control flow. Its compile-time data flow is token concatenation:

1. Higher-level code names a register and field in a helper invocation, for example `REG_SET_FIELD(value, SOME_REGISTER, SOME_FIELD, field_value)`.
2. The helper expands that pair into `SOME_REGISTER__SOME_FIELD__SHIFT` and `SOME_REGISTER__SOME_FIELD_MASK`.
3. The generated constants from this header produce the correct masked 32-bit register value.
4. Separate address macros and MMIO/packet helpers send that value to hardware or decode it from a readback.

For draw/context state, the actual runtime flow is typically userspace or kernel command construction, PM4 packet emission to a ring, GPU command processor consumption, and hardware state update. For initialization state, arrays such as clear-state tables provide default register images. This chunk only supplies the bitfield layout used by those flows.

## State and Persistence Behavior

The macros themselves are compile-time constants and do not persist state. The hardware registers described by the macros hold volatile GPU context and configuration state. Depending on the register class, values may be:

- Draw or pipeline state restored by command streams and context switching.
- Clear-state/default context values loaded when initializing a graphics context.
- Per-queue or per-process shader scratch state.
- Surface-address and size state for VRS feedback/rate images.
- ASIC topology/routing state programmed during graphics initialization.

Persistence is therefore owned by GPU context save/restore, firmware, command processor state, kernel ring setup, and userspace driver command buffers, not by this header. The key persistence risk is that stale or cross-generation masks can silently preserve or corrupt unrelated bits when a field helper reads, clears, and writes a 32-bit register value.

## Dependencies and Integration Points

This chunk depends on the generated register-address headers for GC 12.0.0, especially `gc_12_0_0_offset.h`, and on AMDGPU common helper macros in headers such as `amdgpu.h` and `soc15_common.h`. It also depends semantically on AMD hardware register specifications and on the PM4/register programming model used by graphics, KFD, MES, SDMA, GFXHUB, and IMU code.

Important integration points include:

- Graphics initialization and golden/default register programming in `gfx_v12_0.c` and SOC24 setup code.
- KFD queue and MQD setup where compute/graphics queue state must match the GC 12 field layout.
- Clear-state initialization tables for GC 12 render context defaults.
- Userspace driver command buffers that rely on kernel-shipped register definitions and hardware ABI compatibility.
- Debug, tracing, and register decode paths that use `REG_GET_FIELD` to interpret register dumps.

## Risks and Maintenance Notes

- This range starts after several `DB_SHADER_CONTROL` shift definitions, so chunk-local analysis must remember that the full register definition crosses the chunk boundary.
- Reserved fields in `DB_DEPTH_CONTROL` differ from older sibling headers. Code shared across GC generations should use generation-specific names and avoid writing reserved bits unless hardware documentation explicitly requires it.
- Repeated register families are easy to edit mechanically but dangerous to edit by hand. A one-bit shift error in any `PA_SC_VPORT_*`, `SPI_PS_INPUT_CNTL_n`, `SX_MRTn_BLEND_OPT`, or `CB_BLENDn_CONTROL` entry can affect only one viewport/input/MRT and be hard to diagnose.
- Address high/low split fields for VRS and scratch state must match address alignment and aperture rules outside this header.
- `PA_SC_RASTER_CONFIG` fields are topology-sensitive. Copying values between harvested or differently configured ASICs can misroute raster work.
- `SPI_PS_INPUT_CNTL_n` field availability changes after slot 19 in this chunk; code generators or validators should not assume all 32 slots have identical field sets.
- Because `REG_SET_FIELD` masks the shifted input, out-of-range field values may be truncated rather than rejected at compile time.

## Test Signals

Useful validation signals for this chunk are mostly build-time, register-programming, and GPU-render correctness checks:

- The AMDGPU driver should compile with GC 12.0.0 include users; missing or renamed macros surface as C preprocessor/build failures.
- Static checks can verify each mask is consistent with its shift and field width, repeated families have regular strides, and no masks overlap unexpectedly within one register.
- Register readback tests can program representative fields with `REG_SET_FIELD` and confirm `REG_GET_FIELD` returns the original value for single-bit, multi-bit, and high-bit fields such as blend enable/ROP disable.
- Graphics conformance or piglit/Vulkan/GL tests should cover depth/stencil compare/write behavior, alpha-to-coverage, multisampling/EQAA, viewport/scissor clipping, user clip planes, VRS rate images/feedback, pixel shader interpolation, color export formats, blend equations, MRT enablement, and shader scratch use.
- GPU reset, suspend/resume, and context-switch tests should ensure clear-state and context restore paths reload the volatile registers described by this chunk.

### subset-b-002581: lines 30174-32555

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 30174-32555

## Scope

This chunk is a generated AMD GC 12.0.0 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `__SHIFT` value and a matching `__MASK` value for composing or decoding 32-bit GPU register values. There are no functions, structs, enums, global variables, includes, branches, allocations, locks, callbacks, or persistence logic in this range.

The selected lines begin after the final `CB_BLEND7_CONTROL` field masks, then cover primitive assembly, clipper, setup, scan-converter, binner, variable-rate shading, HiZ/HiS, color-buffer target, color memory-policy, and PA/SC enhancement/debug register fields. The chunk ends after the complete `SC_MEM_SCOPE` field definitions and before the next `gc_gfx_se_gfx_se_pfvf_sqdec` address block starts with `SQ_RUNTIME_CONFIG`.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for the GC 12.0 graphics IP and is not Ceph filesystem code.

## Purpose

`gc_12_0_0_sh_mask.h` supplies bit layouts for GC 12.0.0 registers. Driver code pairs these macros with register addresses from the matching offset header and, where available, defaults from the matching default header. Consumers normally use helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` to avoid open-coded bit shifts and masks.

This slice focuses on the graphics front-end, rasterization, render-target, binner, and scan-converter control surface:

- Clipper and setup state, including point radii/size, user clip planes, viewport transform enables, vertex-output side-band enables, NaN/Inf handling, culling, polygon mode, line stipple, small-primitive filtering, over-rasterization, stereo routing, and primitive-rate or vertex-rate VRS combiners.
- Scan-converter state, including scissor/MSAA mode, walk order, tile coverage, sample iteration, anti-alias sample locations and masks, centroid priority, line rasterization, conservative rasterization, shader-control fields, and sample distance.
- Binner and NGG controls, including bin dimensions, context/persistent states per bin, batch limits, ping-pong bin order, light-volume optimizations, ZPP, wave/deallocation limits, event masks, timeout counters, and binner performance thresholds.
- HiZ/HiS and VRS surface metadata, including surface format, swizzle mode, bases, extents, flush/sync controls, tag limits, eviction policy, debug overrides, and memory scope fields.
- Color-buffer target descriptors for `CB_COLOR0` through `CB_COLOR7`, including base address fragments, view slice ranges, mip level, fragment count, FDCC compression policy, dimensions, swizzle/resource metadata, extended base bits, render-target format/type/swap/rounding fields, and temporal read/write hints.
- PA/SC and PA/PH enhancement registers that expose hardware workarounds, clock-gating controls, out-of-order processing knobs, binner/PBB overrides, FIFO sizing, trap-screen write locks, and debug/performance-control fields.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register-address symbols live in the companion GC 12.0.0 offset header, typically as `mm...` macros.
- AMDGPU callers usually combine these with `REG_SET_FIELD`, `REG_GET_FIELD`, MMIO helpers, indexed-register helpers, or PM4/state-emission paths.

Important register families in this slice include:

- `PA_CL_*`, `PA_SU_*`, and `PA_STEREO_*`: point, clip, viewport-transform, vertex-output, culling, primitive filtering, line, polygon offset, stereo, over-rasterization, and VRS-combiner fields.
- `PA_SC_*`: scan-converter mode, AA config, centroid priority, sample locations, AA masks, binner controls, NGG mode, conservative rasterization, shader control, VRS surface control, HiZ/HiS state, enhancement/debug registers, FIFO sizing, event controls, timeout counters, and performance histogram thresholds.
- `DB_HTILE_SURFACE` and `DB_SRESULTS_COMPARE_STATE0/1`: depth/HTILE surface control and stencil-results comparison fields that interact with PA/SC HiZ/HiS behavior.
- `GE_MAX_OUTPUT_PER_SUBGROUP`, `GE_SE_ENHANCE`, `VGT_REUSE_OFF`, `VGT_DRAW_PAYLOAD_CNTL`, `VGT_GS_MAX_VERT_OUT`, `VGT_GS_INSTANCE_CNT`, and `GE_NGG_SUBGRP_CNTL`: geometry, NGG, draw-payload, reuse, and GS-output controls.
- `CB_TARGET_MASK`, `CB_SHADER_MASK`, `CB_COLOR_CONTROL`, `CB_COLORn_*`, and `CB_MEMn_INFO`: color-output masks, blend/ROP control, render-target descriptors, FDCC compression controls, base extension bits, format/type metadata, and temporal read/write policy for eight color targets.
- `PA_SC_HIZ_*`, `PA_SC_HIS_*`, `PA_SC_VRS_SURFACE_CNTL`, `PA_SC_VRS_SURFACE_CNTL_1`, and `SC_MEM_SCOPE`: hierarchical depth/stencil and VRS surface controls, debug overrides, cache/flush/sync behavior, and memory-scope selectors.

## Control Flow

This header has no runtime control flow. Its behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU consumers:

1. Select the GC 12.0.0 register definitions for the active ASIC.
2. Choose a register address from the matching offset header.
3. Prepare a register value from command-stream state or read an existing register for read-modify-write.
4. Pack or extract fields using the `__SHIFT`/`__MASK` pairs, usually through common AMDGPU field helpers.
5. Emit MMIO writes or PM4 packets as part of draw setup, render-target binding, rasterization setup, binner configuration, reset/resume restore, or diagnostic programming.

At runtime, graphics setup code programs PA/SC/SU/VGT/GE state before draws, then CB and DB-related state controls color and depth/stencil output. Binner, PBB, VRS, HiZ, and HiS settings influence how primitives are tiled, culled, shaded, and compressed. This header does not define packet ordering, cache flush requirements, waits, register access methods, or hardware side effects; those responsibilities stay in the AMDGPU programming sequences and hardware specification.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe GPU register fields whose values live in hardware context state, MMIO-visible registers, or command-stream state until overwritten, restored during context switch, reset during GPU reset, lost during power transitions, or reinitialized on suspend/resume.

Most fields in this chunk are persistent graphics context state: clipper controls, rasterizer modes, sample locations, binner policy, render-target descriptors, VRS/HiZ/HiS surface controls, and PA/SC enhancement bits. Incorrectly restored or stale state can affect later draws even if the current draw does not explicitly touch the same feature.

`CB_COLORn_*` registers are especially stateful. `BASE` and `BASE_EXT` encode GPU-address fragments, `VIEW`/`VIEW2` select slices and mips, `ATTRIB*` define fragment count, dimensions, swizzle mode, resource type, and speculative-read behavior, `FDCC_CONTROL` selects compression behavior, and `INFO` defines format/number type/component swap/rounding. A stale or mispacked color-target field can redirect rendering, corrupt metadata, break blending, or make one MRT slot behave differently from the others.

HiZ/HiS and VRS surface fields also persist across draw sequences. Base, extent, format, swizzle, flush, eviction, sync, tag-limit, and debug override fields must match depth/stencil/VRS metadata allocation and synchronization policy. `SC_MEM_SCOPE` adds memory-scope selectors for VRS rate, VRS feedback, HiZ, and HiS surfaces.

The header does not encode whether individual hardware fields are read-only, write-only, pulse-style, sticky, reset-only, privileged, or safe for read-modify-write. Callers must preserve reserved bits unless a documented full-register value is being emitted, especially for enhancement, debug, cache/sync, and workaround registers.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.0.0 register set staying internally consistent:

- The matching `gc_12_0_0_offset.h` provides register addresses for these field macros.
- The matching `gc_12_0_0_default.h`, when generated for the same register families, provides reset/default values.
- Common AMDGPU register helpers provide the packing, extraction, MMIO, indexed-register, and command-packet mechanisms.
- Graphics IP initialization, ring/PM4 state emission, reset/suspend/resume restore, debugfs or diagnostics, KFD interactions, and userspace command-stream assumptions rely on these bit layouts matching the hardware database.

Integration points include draw payload setup, GS/NGG configuration, primitive culling/filtering, clip/viewport transform, point/line/polygon rasterization, scissor and tile walk order, MSAA sample positions, centroid selection, VRS rate selection and surface feedback, conservative rasterization, binner/PBB policy, depth/stencil HiZ/HiS acceleration, color target binding, FDCC compression, temporal memory policy, and PA/SC hardware-workaround programming.

The `gc_gfx_se_gfx_se_pfvf_padec` address-block marker in the middle of the slice indicates that later registers in the chunk belong to a PA decode area separate from the preceding context-state-style groups. Merge-level research should keep that block boundary because it often maps to different register ranges or access paths in the offset header.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong shift or mask compiles successfully but writes the wrong hardware bits, causing rendering corruption, hangs, missing primitives, bad depth/stencil results, broken VRS, or one-target-only MRT failures.
- The chunk starts mid-family after `CB_BLEND7_CONTROL`; final per-file research must merge the preceding chunk to capture the full blend-control family.
- Repeated `CB_COLOR0` through `CB_COLOR7` layouts invite generator or copy errors. Slot-specific mismatches can affect only one render target and may escape broad smoke tests.
- Address fields such as `BASE_256B` and `BASE_EXT` are not raw byte addresses. Incorrect alignment or unit conversion can program plausible but wrong GPU addresses.
- Compression and metadata fields are high risk: FDCC compression controls, HiZ/HiS base/size/format fields, VRS surface controls, temporal hints, and cache/flush/sync knobs must agree with memory allocation, metadata layout, and cache-management sequences.
- PA/SC enhancement and debug registers expose many workaround, clock-gating, out-of-order, reset, binner, and performance knobs. Full-register writes that do not preserve reserved or ASIC-specific bits can cause subtle performance or correctness regressions.
- MSAA, sample locations, centroid priority, AA masks, VRS rates, conservative rasterization, and exposed/detail sample counts are tightly coupled. Inconsistent programming can produce coverage artifacts that are difficult to diagnose from a single register.
- Event-mask and binner controls can alter batching and synchronization behavior. Treating these as passive state without respecting hardware ordering can cause missed flushes, premature batch breaks, or stale metadata visibility.
- Several fields occupy high bits or full 32-bit masks. Consumers should use unsigned 32-bit arithmetic and helper macros rather than signed shifts or hand-written constants.

## Test Signals

Useful validation is primarily build coverage, generated-data consistency, and hardware/runtime rendering coverage:

- Kernel build coverage for AMDGPU files that include `gc_12_0_0_sh_mask.h`, especially GC 12 graphics initialization, command submission, reset, suspend/resume, and diagnostics.
- Mechanical comparison against AMD's authoritative GC 12.0.0 register database for every `__SHIFT`/`__MASK` pair in this chunk.
- Cross-checks that all registers in this slice have matching address macros in `gc_12_0_0_offset.h` and expected defaults in `gc_12_0_0_default.h` where defaults are generated.
- Static sanity checks that masks align with shifts, repeated `CB_COLORn_*`, `CB_MEMn_INFO`, and AA sample-location layouts remain consistent across slots/pixels, and full-width data registers use `0xFFFFFFFFL`.
- Rendering tests for MRT color output, color masks, blend/ROP interaction, target format/type/component swap, FDCC/compression behavior, fast clears where adjacent registers provide clear state, and suspend/resume or reset restore of render-target state.
- Rasterization tests for clipping, point and line rendering, line stipple, polygon offset, culling, small-primitive filtering, conservative rasterization, MSAA sample positions, centroid interpolation, VRS, stereo/view routing, and viewport/scissor behavior.
- Binner/PBB/NGG tests that exercise bin sizing, batch limits, primitive grouping, event controls, timeout paths, light-volume optimizations, ZPP, and out-of-order PA/SC controls.
- Depth/stencil and metadata tests covering HiZ/HiS enablement, base/extent programming, flush/invalidate/sync behavior, debug override registers, and mixed depth/stencil/VRS workloads.
- Runtime warning signals include GPU hangs around draws or batch transitions, corrupted render targets, incorrect coverage or sample interpolation, broken VRS rates, bad depth/stencil culling, metadata corruption, unexpected performance cliffs from binner/enhancement settings, and regressions isolated to one color target or one MSAA mode.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002581`. It covers lines 30174-32555 of `gc_12_0_0_sh_mask.h`. The final per-file document should merge this with adjacent chunks to complete the preceding `CB_BLEND7_CONTROL` context and continue with the following SQ runtime configuration block.

### subset-b-002582: lines 32556-35081

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 32556-35081

## Scope

This chunk is a generated AMD GC 12.0.0 shift/mask register-header segment. It contains C preprocessor constants only: every hardware register field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a corresponding `<REGISTER>__<FIELD>_MASK` macro. There are no functions, structs, enums, variables, includes, loops, allocations, locks, callbacks, or executable branches in this range.

The selected range begins in the tail of `SC_MEM_SCOPE`, covering `HIZ_SCOPE` and `HIS_SCOPE` shift/mask values after the VRS fields started in the previous lines. It then covers shader-queue, shader-pipe, UTCL1, TCP, SPI resource reservation, graphics user, GL1, SE CAC/DIDT EDC, and the beginning of performance-counter mask definitions. The final selected line is only the `//TCP_PERFCOUNTER0_LO` register comment; its shift/mask definitions are in the following chunk.

Although the source tree path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for AMD GC 12.0.0 graphics IP. It is not Ceph filesystem logic.

## Purpose

`gc_12_0_0_sh_mask.h` gives AMDGPU code the bit layouts for GC 12.0.0 hardware registers. Callers pair these field masks with matching register addresses from the companion GC 12.0.0 offset header and typically use helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` to pack or decode fields without hard-coding raw bit positions.

This chunk focuses on shader engine and shader-array infrastructure:

- `SC_MEM_SCOPE` tail fields define memory-scope controls for hierarchical Z and hierarchical stencil alongside the VRS rate/feedback scope fields that begin just before this chunk.
- `gc_gfx_se_gfx_se_pfvf_sqdec` covers SQ runtime/debug status, shader memory base/config fields, trap-base and trap-memory-address registers, and shader debug toggles.
- `gc_gfx_se_gfx_se_pfonly_spidec` covers SPI/CDBG enablement, graphics-debug wave stall/trap controls, reset-debug disable bits, GDS compute max wave id, SPI/PC arbitration and feature limits, shader resource limits, and per-pipe/per-queue compute wavefront context-save busy status.
- `gc_gfx_se_gfx_se_pfonly_utcl1dec` covers UTCL1 control, invalidation-disable, FIFO sizing, GCRD target/credit safety, and eight identity-mode templates that describe synthesized translation-return attributes.
- `gc_gfx_se_gfx_se_pfonly_tcpdec` covers texture/cache pipe invalidation, busy/status bits, data/cache controls, credit knobs, compression controls, and arbitration.
- `gc_gfx_se_gfx_se_pfonly2_spidec` covers repeated per-CU SPI resource reservations and reservation-enable masks for 16 CUs.
- `gc_gfx_se_gfx_se_gfxudec` covers tessellation/offchip and GE ring sizing, line stipple and screen extents, pre-shader trap-screen controls, SQ thread-trace userdata, SQC cache invalidation, TA buffer-cache base address, DB occlusion counters, SPI configuration/throttle/attribute ring/event/launch-guarantee registers.
- `gc_gfx_se_gfx_se_gl1dec` covers GL1/GL1X arbitration, burst, clock-gating, compression, credit, client delay, compressor override, GL1C/GL1XC controls, status, UTCL0 controls/status/retry, and compression-bypass overrides.
- `gc_gfx_se_gfx_se_pfonly_secacdec` covers shader-engine CAC/LCAC controls, DIDT EDC throttling/status/perf-counter fields, and a large bank of per-block CAC signal weights plus indirect index/data access.
- `gc_gfx_se_gfx_se_perfddec` starts the performance-counter readout map for GE2_SE, GRBMH, PA_SU, PA_SC, SPI, PC, SQ, SQG, SX, TA, and TD counters; the TCP counter family continues after this chunk.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this slice. The exported interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field within a 32-bit register.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask for that field.
- Full-register data or counter fields use `0xFFFFFFFFL`; high address or high counter halves may expose narrower masks such as `0x000000FFL` or `0x7FFFFFFFL`.
- Register-address symbols are expected in the matching GC 12.0.0 offset header under the same register names.
- AMDGPU register helper code, MMIO accessors, PM4 packet builders, context-save/restore logic, debug dumps, reset paths, RAS/power-management code, and performance-monitor logic are the likely direct consumers.

The major macro families in this chunk are:

- `SQ_RUNTIME_CONFIG`, `SQ_DEBUG_STS_GLOBAL`, `SQ_DEBUG_STS_GLOBAL2`, `SH_MEM_BASES`, `SH_MEM_CONFIG`, `SQ_DEBUG`, `SQ_SHADER_TBA_*`, and `SQ_SHADER_TMA_*`: shader queue status, memory addressing/configuration, debug control, and trap handler/trap memory address fields.
- `SPI_CDBG_SYS_*`, `SPI_GDBG_*`, `SPI_RESET_DEBUG`, `SPI_ARB_CNTL_0`, `SPI_FEATURE_CTRL`, `SPI_SHADER_RSRC_LIMIT_CTRL`, `PC_CONFIG_CNTL_*`, and `SPI_COMPUTE_WF_CTX_SAVE_STATUS`: SPI debug, wave stall/trap, reset-debug, arbitration, shader resource limit, primitive control, and context-save status fields.
- `UTCL1_CTRL_0`, `UTCL1_CTRL_2`, `UTCL1_FIFO_SIZING`, `GCRD_*`, and `UTCL1_IDENTITY_MODE0..7`: UTCL1 translation/cache invalidation, credit, identity-mode, return-attribute, fault, PTE TMZ, XNACK, physical-address, IO steer, MTYPE, and dirty-bit fields.
- `TCP_INVALIDATE`, `TCP_STATUS`, `TCP_CNTL`, `TCP_CNTL2`, `TCP_CREDIT`, `TCP_COMPRESSION_CNTL`, and `TCP_ARB`: TCP invalidate trigger, busy/status observation, cache behavior, MGCG/FGCG override, write combining, end-of-wave forcing, data-compression, credit, and arbitration fields.
- `SPI_RESOURCE_RESERVE_CU_0..15` and `SPI_RESOURCE_RESERVE_EN_CU_0..15`: per-CU reserved VGPR/SGPR/LDS/wave/barrier resources and enable/type/queue masks.
- `VGT_TF_RING_SIZE`, `VGT_HS_OFFCHIP_PARAM`, `GE_POS_RING_*`, `GE_PRIM_RING_*`, `PA_*`, `SQ_THREAD_TRACE_USERDATA_*`, `SQC_CACHES`, `TA_CS_BC_BASE_ADDR*`, and `DB_OCCLUSION_COUNT*`: tessellation, geometry-engine rings, raster/pre-shader trap coordinates, thread trace metadata, SQC invalidate/complete, texture address base, and occlusion counter fields.
- `SPI_CONFIG_CNTL*`, `SPI_GS_THROTTLE_CNTL*`, `SPI_ATTRIBUTE_RING_*`, `SPI_SQG_EVENT_CTL`, and `SPI_GRP_LAUNCH_GUARANTEE_*`: SPI priority, export allocation, power-save, context-save wait, throttle, attribute ring, SQG events, and launch-guarantee fields.
- `GL1*` and `GL1X*` plus `GL1C*` and `GL1XC*`: GL1/GL1X arbitration/burst/compression and client/cache behavior, GL1C/GL1XC status, UTCL0 response/fault modes, invalidation VMID/toggle fields, retry counters, in-flight limits, and compression bypass overrides.
- `SE_CAC_*` and `DIDT_EDC_*`: shader-engine current/activity counter controls, low-current activity counter overrides, DIDT EDC enable/reset/throttle/stall-pattern/status/overflow/rolling-power/perf-counter fields, many per-client 16-bit weighting signals, and indirect CAC register access.
- `*_PERFCOUNTER*_LO` and `*_PERFCOUNTER*_HI`: performance counter low/high readout fields for GE2_SE, GRBMH, PA_SU, PA_SC, SPI, PC, SQ, SQG, SX, TA, and TD blocks.

## Control Flow

This header has no runtime control flow. All behavior is compile-time macro substitution.

The implied driver flow is:

1. Select the GC 12.0.0 register headers for the active ASIC.
2. Select a register address from the matching offset header.
3. Read a register, prepare a context-state value, build a PM4 packet, poll status, or decode a debug/performance readback.
4. Use the `__SHIFT` and `__MASK` pair, usually via AMDGPU register helper macros, to pack or extract a field.
5. Apply the resulting value to SQ/SPI/PC/TCP/UTCL1/GL1/CAC/performance-counter setup, diagnostics, reset handling, or context-save/restore.

For programming registers, the control flow is owned by AMDGPU graphics, compute, debug, reset, power, and performance-monitor code. For status and counter registers, callers typically poll, snapshot, or expose decoded values through debugfs, trace, hang-dump, RAS, or performance tooling. This chunk does not encode ordering, synchronization, side effects, valid value ranges, or poll timeouts; those must come from surrounding driver code and the hardware programming guide.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe fields in live GPU hardware registers whose values may be context state, global engine state, volatile status, side-effect triggers, or read-only counters.

SQ/SPI/PC fields are mostly shader-engine and shader-pipe control/debug state. Trap-base/trap-memory address registers are split low/high address fields plus `TRAP_EN`; incorrect composition affects shader trap dispatch. `SH_MEM_BASES` and `SH_MEM_CONFIG` are per-shader addressing and cache behavior state that can participate in context save/restore and VMID isolation. Debug stall and reset-disable fields can change forward progress and reset behavior for active queues.

`SPI_COMPUTE_WF_CTX_SAVE_STATUS` is volatile status: each pipe/queue busy bit reports context-save activity and can change while waves are running. `SPI_RESOURCE_RESERVE_CU_*` and enable registers persist resource-reservation policy until reprogrammed and can reduce visible CU resources or gate specific queue/type classes.

UTCL1, GL1, GL1C, GL1X, and GL1XC fields describe cache, translation, invalidation, credit, retry, fault, compression, and request-tracking state. Some fields are configuration knobs, some are volatile busy/fault/retry status, and some trigger or shape invalidation behavior. Identity-mode registers synthesize translation-return attributes such as snoop, fragment size, permission, XNACK, PTE TMZ, no-PTE, physical address, IO steering, MTYPE, and dirty status; bad settings can bypass normal VM semantics in identity-mode paths.

TCP fields include explicit side effects (`TCP_INVALIDATE__START`), volatile busy/status bits, and cache/compression policy. `TCP_COMPRESSION_CNTL` and GL1 compressor override fields affect data-compression behavior and can interact with memory coherency, cache policy, sparse residency, and performance.

GFXU state covers ring base/size fields, screen extents, trap-screen controls, thread-trace userdata, SQC cache invalidate/complete, TA buffer-cache base address, and DB occlusion counters. Ring and base-address fields persist as graphics context/global engine configuration; counters and status fields change as work executes.

SE CAC and DIDT EDC registers are power/current-management instrumentation and throttling controls. CAC windowing and weight tables affect activity/current estimation. DIDT EDC enable, thresholds, stall patterns, throttle controls, and force-stall fields can intentionally stall SQ/DB/TCP/TD paths; status, overflow, rolling power delta, and perf counter fields are dynamic readbacks.

Performance-counter fields are readout-only or readout-oriented data surfaces from monitored blocks. The low/high pairs must be sampled coherently according to the performance-monitor sequence outside this header. The header only says that each low/high field occupies the full 32-bit register.

Reserved, unused, and spare fields appear throughout the chunk. Their presence as generated macros does not make them safe for arbitrary writes; read-modify-write code should preserve unrelated bits unless the hardware sequence documents a full-register write.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.0.0 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h` supplies matching register address macros.
- Matching generated default headers, where present, supply reset/default values for many of these registers.
- AMDGPU register helper macros provide field packing/extraction and MMIO/PM4 access patterns.
- ASIC-specific AMDGPU graphics, compute, KFD-adjacent, VM, cache, reset, debug, RAS, power-management, and performance-monitor code can include these constants.
- Userspace graphics and compute stacks depend on these values indirectly through kernel command submission, context programming, debug/perf queries, and firmware/kernel ABI behavior.

Important integration surfaces include shader trap setup, SQ debug status dumps, shader memory aperture setup, SPI wavefront/context-save coordination, graphics reset inhibition/debugging, PC/SPI arbitration tuning, per-CU resource reservations, UTCL1 translation and invalidation behavior, TCP invalidation and compression policy, SQC cache invalidation, GL1/GL1X cache and compression behavior, DB occlusion counter readback, thread-trace userdata, attribute-ring programming, launch-guarantee controls, CAC/LCAC and DIDT EDC power throttling, and performance counter sampling.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask still compiles but writes or decodes the wrong hardware bits.
- The selected chunk starts mid-register and ends on a register comment without the matching definitions. Complete file-level analysis must merge adjacent chunks for the full `SC_MEM_SCOPE` and `TCP_PERFCOUNTER0_*` families.
- Many families are repeated and index-sensitive: UTCL1 identity modes `0..7`, SPI resource reservations `0..15`, CU reservation enables `0..15`, occlusion counters `0..3`, and performance counters. Single-index generation mistakes can affect only one lane and be hard to diagnose.
- Side-effect fields such as `TCP_INVALIDATE__START`, `SQC_CACHES__INVALIDATE`, `SQC_CACHES__COMPLETE`, shader debug stalls, reset-disable bits, and DIDT force/throttle controls must not be treated as passive configuration.
- Address split fields such as `SQ_SHADER_TBA_*`, `SQ_SHADER_TMA_*`, `TA_CS_BC_BASE_ADDR*`, and GE ring base fields require correct low/high composition and alignment assumptions from the hardware spec.
- Cache, translation, retry, fault, compression, snoop, atomic, and invalidation fields in UTCL1/GL1/TCP can cause memory ordering bugs, coherency failures, page-fault behavior changes, or silent data corruption if programmed with the wrong policy.
- `SH_MEM_CONFIG`, `SH_MEM_BASES`, and UTCL1 identity-mode fields have VM/security implications because they affect address translation, permission, and trap behavior.
- SPI resource limits and per-CU reservation masks can starve waves, underutilize CUs, or break queue isolation if queue/type masks are wrong.
- DIDT EDC and CAC fields tie performance to power/current estimation. Bad thresholds, weights, or stall patterns can cause excessive throttling, missed protection, unstable clocks, or misleading telemetry.
- Performance-counter low/high readbacks require coherent sampling; this header does not describe latch order or overflow behavior.
- Reserved/spare fields appear with masks. They should be preserved unless a documented sequence requires writing them.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, hardware bring-up, and runtime diagnostics:

- Kernel build coverage for AMDGPU code that includes `gc_12_0_0_sh_mask.h`.
- Mechanical comparison against AMD's authoritative GC 12.0.0 register database for every `__SHIFT` and `__MASK` in lines 32556-35081.
- Cross-checks that each register in this chunk has a matching address symbol in `gc_12_0_0_offset.h` and, where generated, an expected default value in the matching default header.
- Static sanity checks that masks align with shifts, full-width fields use `0xFFFFFFFFL`, high halves have the expected widths, and repeated families keep identical field layouts across indices.
- SQ/SPI debug tests that verify busy/status decode, trap-base programming, wave stall/trap behavior, and compute context-save busy reporting across pipes and queues.
- VM/cache tests that exercise UTCL1 invalidation, identity-mode behavior, GL1/GL1X/GL1C/GL1XC fault/retry/status paths, TCP invalidation, cache compression controls, atomic/snoop behavior, and sparse or faulting memory accesses.
- Graphics workload tests covering tessellation/offchip buffering, GE primitive/position rings, line stipple, screen extents, trap-screen counting, DB occlusion counters, attribute rings, and launch-guarantee behavior.
- SQC/thread-trace diagnostics that confirm `SQC_CACHES` invalidate/complete transitions and thread-trace userdata capture.
- Resource scheduling tests that validate SPI per-CU reservation and enable masks do not strand queues, misroute queue types, or violate resource accounting.
- Power/current-management tests that compare CAC window/weight output and DIDT EDC throttle/status/performance-counter behavior under controlled SQ/DB/TCP/TD workloads.
- Performance-monitor tests that sample GE2_SE, GRBMH, PA_SU, PA_SC, SPI, PC, SQ, SQG, SX, TA, and TD counter low/high pairs and check monotonicity, overflow handling, and block attribution.
- Runtime warning signals include GPU hangs during context save/restore, unexpected reset suppression, incorrect shader trap behavior, VM faults or missing faults, cache incoherency, broken compression/decompression, excessive throttling, impossible busy/status dumps, performance counters stuck at zero, or rendering/compute corruption isolated to GC 12.0.0 paths.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002582`. It covers lines 32556-35081 of `gc_12_0_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the surrounding `SC_MEM_SCOPE` and TCP performance-counter definitions and to place these SQ/SPI/UTCL1/TCP/GL1/CAC/performance-counter masks in the full GC 12.0.0 register map.

### subset-b-002583: lines 35082-37536

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 35082-37536

## Scope

This chunk covers a generated GC 12.0.0 shader/register mask header range. It starts in the middle of the `TCP_PERFCOUNTER0_LO` field definitions and ends in the `ICG_SQ_CLK_CTRL` clock override register, after the `TAG_CLK_OVERRIDE` mask and before the final fields of that register in the following chunk.

The covered range contains only C preprocessor constants. It does not define functions, structs, storage, runtime branches, or executable control flow. The constants are bitfield ABI definitions for AMDGPU GC 12 hardware registers:

- Low/high 32-bit performance counter value registers for TCP, GL1C, GL1XC, CB, DB, RMI, PA_PH, UTCL1, GL1A, and GL1XA blocks.
- Performance counter filter registers for TCP and CB.
- Shader-engine performance counter selection and control for GE2_SE, GRBMH, PA_SU, PA_SC, SPI, PC, SQ, SQG, SX, TA, TD, TCP, GL1C, GL1XC, CB, DB, RMI, PA_PH, UTCL1, GL1A, and GL1XA.
- SQ and SQG performance counter enable/control registers and sample-finish status.
- SQ thread-trace buffer, control, masking, write pointer, halt, poweroff-restore, status, draw/marker, dropped counter, and finish-done debug registers.
- GFX shader-engine power/clock gating controls for SPI, PC, BCI, VGT, GS/NGG, PA, SQ, SQG, ALU, TEX, LDS, and fine-grained SQ clock domains.

## Purpose

The purpose of this header section is to encode field locations for GC 12.0.0 MMIO registers. Each field is represented as a conventional pair:

- `<REGISTER>__<FIELD>__SHIFT`, the field's bit offset.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or compose the field in a 32-bit register value.

The matching `gc_12_0_0_offset.h` file supplies register addresses such as `regSQ_THREAD_TRACE_CTRL`, `regSQ_PERFCOUNTER0_SELECT`, or `regCGTT_SQ_CLK_CTRL`; this file supplies the bit layout for those registers. AMDGPU and KFD code then use the generated names through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15_PREREG`, and `SOC15_REG_OFFSET`.

## Important Macro Families

### Performance Counter Values and Filters

The first part of the chunk provides low/high value masks for multiple block-local counters. Registers such as `TCP_PERFCOUNTER*_LO/HI`, `GL1C_PERFCOUNTER*_LO/HI`, `GL1XC_PERFCOUNTER*_LO/HI`, `CB_PERFCOUNTER*_LO/HI`, `DB_PERFCOUNTER*_LO/HI`, `RMI_PERFCOUNTER*_LO/HI`, `PA_PH_PERFCOUNTER*_LO/HI`, `UTCL1_PERFCOUNTER*_LO/HI`, `GL1A_PERFCOUNTER*_LO/HI`, and `GL1XA_PERFCOUNTER*_LO/HI` expose full-width `PERFCOUNTER_LO` or `PERFCOUNTER_HI` fields with `0xFFFFFFFFL` masks. Consumers combine the low and high halves to read wider hardware performance counter state.

`TCP_PERFCOUNTER_FILTER` and `TCP_PERFCOUNTER_FILTER2` define filters for texture/cache requests: buffer, flat, dimensionality, data format, compression enable, numeric format, software mode, sample count, opcode type, temporal hint, scope, and request mode. `TCP_PERFCOUNTER_FILTER_EN` provides the corresponding per-filter enable bits. This split matters because filter values can be programmed without taking effect unless their enable bits are set.

`CB_PERFCOUNTER_FILTER` is render-backend specific. It filters color-buffer performance counting by operation, format, clear state, MRT, sample count, and fragment count. The enable and selector fields sit next to each other, so mask drift can silently change which render traffic contributes to a counter.

### Shader-Engine Performance Counter Selection

After the `gc_gfx_se_gfx_se_perfsdec` address block marker, the chunk describes event selection for shader-engine-local performance counters.

Most graphics pipeline blocks use a repeated layout:

- `*_PERFCOUNTER0_SELECT` can pack `PERF_SEL`, `PERF_SEL1`, `CNTR_MODE`, `PERF_MODE1`, and `PERF_MODE`.
- `*_PERFCOUNTER0_SELECT1` can add `PERF_SEL2`, `PERF_SEL3`, `PERF_MODE2`, and `PERF_MODE3`.
- Later counters sometimes use a narrower single-event layout with only `PERF_SEL` and `PERF_MODE`.

The covered blocks include GE2_SE, SPI, PC, SX, TA, TD, TCP, GL1C, GL1XC, CB, DB, RMI, PA_PH, GL1A, and GL1XA. Most selectors use 10-bit event fields (`0x000003FFL`), while SQ and SQG use 9-bit `PERF_SEL` fields plus `SPM_MODE` and `PERF_MODE`. UTCL1 uses `PERF_SEL` plus `COUNTER_MODE` fields rather than the common graphics-pipe `CNTR_MODE` naming.

The RMI block also includes `RMI_PERF_COUNTER_CNTL`, which controls transaction/event/TC performance enable selection, event windows, CID, VMID, burst-length threshold, soft reset, and SPM counter selection. That register is more stateful than a simple event selector because it gates how RMI events are attributed and sampled.

`GRBMH_CP_PERFMON_CNTL` and `CP_PERFMON_CNTL_1` connect the shader-engine performance monitor domain to command processor/performance monitor state, with fields for sample enable, perfmon state, SPM perfmon state, and enable mode.

### SQ and SQG Performance Controls

`SQ_PERFCOUNTER0_SELECT` through `SQ_PERFCOUNTER15_SELECT` and `SQG_PERFCOUNTER0_SELECT` through `SQG_PERFCOUNTER7_SELECT` use a compact GC 12 layout: `PERF_SEL`, `SPM_MODE`, and `PERF_MODE`. These fields are central to shader performance profiling because they select events from the shader core and SQG front-end domains and decide how they participate in streaming performance monitoring.

`SQ_PERFCOUNTER_CTRL` and `SQG_PERFCOUNTER_CTRL` include shader-stage enables (`PS_EN`, `CS_EN`, `GS_EN`, `HS_EN`) and per-ME/pipe disable bits. `SQ_PERFCOUNTER_CTRL2` and `SQG_PERFCOUNTER_CTRL2` add `VMID_EN` and `FORCE_EN`. `SQG_PERF_SAMPLE_FINISH` has a `STATUS` bit for sample completion/handshake visibility.

### SQ Thread Trace

The thread-trace section defines the per-SQ trace buffer programming surface:

- `SQ_THREAD_TRACE_BUF0_SIZE`, `BUF0_BASE_LO/HI`, `BUF1_SIZE`, and `BUF1_BASE_LO/HI` describe two trace buffers.
- `SQ_THREAD_TRACE_CTRL` controls mode, high-water/low-water behavior, draw-event capture, register-at-high-water behavior, shader/SPI stalls, interrupt enable, draw/marker synchronization, token behavior, GL1 performance enable, double buffering, prefetch page, util timer, and auto-flush policy.
- `SQ_THREAD_TRACE_MASK` chooses WGP, SIMD, shader-array, wave-type inclusion, and non-detail exclusions.
- `SQ_THREAD_TRACE_TOKEN_MASK` gates token categories such as register detail, instruction tokens, barriers, BOP events, and execution tracing.
- `SQ_THREAD_TRACE_WPTR` exposes buffer ID and write offset.
- `SQ_THREAD_TRACE_HALT` controls entry into poweroff/CGCG and reports readiness.
- `SQ_THREAD_TRACE_STATUS` and `STATUS2` expose busy, finish pending/done, owner VMID, write error, buffer fullness, issue state, lost-packet state, and full-write-buffer state.
- Draw, marker, HP3D draw/marker, dropped counter, and finish-done debug registers expose trace-progress and diagnostic counters.

These registers are integration points for profiling and developer/debug tooling. They are also sensitive to power-state transitions because trace halt and poweroff-restore fields coordinate with clock/power gating.

### GFX Shader-Engine Clock and Power Controls

The final portion, after the `gc_gfx_se_gfx_se_pwrdec` marker, covers clock-gating controls:

- `GFX_ICG_SPI_RA0_CLK_CTRL`, `GFX_ICG_SPI_RA1_CLK_CTRL`, `GFX_ICG_SPI_CS_CTRL`, `GFX_ICG_SPI_PS_CTRL`, `GFX_ICG_SPIS_CTRL`, `CGTX_SPI_DEBUG_CLK_CTRL`, and `GFX_ICG_SPI_CTRL` define SPI-side group overrides, register overrides, off hysteresis, and debug clock controls.
- `GFX_ICG_PC_CLK_CTRL` controls primitive/PC/GL1/LDS/miss-walker/perfmon medium-grain clock-gating overrides, plus on-delay and off-hysteresis.
- `GFX_ICG_BCI_CTRL`, `CGTT_VGT_CLK_CTRL`, `CGTT_GS_NGG_CLK_CTRL`, and `CGTT_PA_CLK_CTRL` expose on-delay, off-hysteresis, performance/debug enables, soft-stall overrides, and block-specific override bits for VGT, tessellation, GS/NGG, PA, SU, CL/VTE, SX interface, and related domains.
- `CGTT_SQ_CLK_CTRL` and `CGTT_SQG_CLK_CTRL` define SQ/SQG on-delay, off-hysteresis, soft-stall overrides, perfmon/thread-trace overrides, core overrides, register overrides, and SQG force-FGCG fields.
- `SQ_ALU_CLK_CTRL`, `SQ_TEX_CLK_CTRL`, and `SQ_LDS_CLK_CTRL` pack per-shader-array `FORCE_WGP_ON` bitmaps for ALU, texture, and LDS domains.
- `SQ_CLK_CTRL` and `ICG_SQ_CLK_CTRL` provide fine-grained SQ clock override bits for SPI/SX messaging, SQC thread trace, wave clocks, LDS, VMEM, SMEM, scalar/SALU/VALU paths, instruction-buffer paths, export, tag, and status domains. This chunk ends before the final `ICG_SQ_CLK_CTRL` masks complete.

## Control Flow and State Behavior

There is no software control flow in this header. The runtime behavior emerges when AMDGPU/KFD code composes MMIO writes or decodes MMIO reads with these masks.

The persistent state represented by this chunk lives in hardware registers:

- Performance counter values and event selectors persist until the profiling setup changes or the hardware block is reset.
- Filter registers constrain which requests or render-backend operations are counted.
- SQ/SQG performance-control and sample-finish bits coordinate sampling state for shader profiling.
- Thread-trace base/size/mask/control registers define trace capture buffers and capture policy, while status and counters report trace progress, errors, dropped data, and ownership.
- Clock-gating control registers alter hardware power/performance behavior by overriding automatic clock gating, forcing WGP domains on, or changing delay/hysteresis thresholds.

Some fields are configuration fields, some are status fields, and some are command-like or handshake fields. For example, trace halt/poweroff fields and sample-finish status require sequencing with hardware state; clock override bits should usually be changed only through the owning power-management or debug path.

## Dependencies and Integration Points

This chunk depends on the generated AMD register header set:

- `gc_12_0_0_offset.h` supplies register offsets for the field names defined here.
- `gc_12_0_0_default.h`, where present for adjacent register families, supplies reset/default values.
- `soc15.h` and AMDGPU register helper macros provide the read/write and field-composition API.

Observed include points in this source tree include:

- `amdgpu/gfx_v12_0.c`, the main GC 12 graphics IP implementation, which includes `gc_12_0_0_offset.h` and this mask header for register setup, RLC/CP bring-up, clock gating, resets, and debug state.
- `amdkfd/kfd_device_queue_manager_v12.c` and `amdkfd/kfd_mqd_manager_v12.c`, which include this header for GC 12 queue/MQD programming.
- `amdgpu/mes_v12_0.c`, `sdma_v7_0.c`, `gfxhub_v12_0.c`, `imu_v12_0.c`, `soc24.c`, and `amdgpu_amdkfd_gfx_v12.c`, which compile against the same GC 12 register definitions.

The specific macros in this chunk are most likely consumed by performance/debug and power-management paths rather than ordinary queue setup. Their natural consumers are GPU performance counter tooling, RLC/SPM setup, shader thread-trace capture, GFX clock-gating control, and diagnostics that read block-local performance counter values.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can program a different hardware field, producing invalid performance data, broken trace capture, clock-gating instability, or GPU hangs.
- Repeated performance counter families are easy to edit incorrectly. Many blocks share similar names and masks, but SQ/SQG, UTCL1, CB, RMI, and some later counters use different layouts.
- Low/high counter reads require correct sequencing in consumers. The header exposes 32-bit halves only; it does not enforce stable 64-bit read ordering or rollover handling.
- Filter value and filter enable fields are separate. Programming `TCP_PERFCOUNTER_FILTER` without `TCP_PERFCOUNTER_FILTER_EN`, or mismatching CB filter enables/selectors, can make profiling silently count the wrong traffic.
- Thread trace can interact with VMID ownership, buffer fullness, dropped packets, interrupts, stalls, CGCG/poweroff, and restore state. Incorrect control sequencing can lose trace packets or stall shader work.
- Clock-gating override fields affect power and timing behavior. Leaving overrides set, forcing WGP domains on, or changing hysteresis/delay fields outside the intended path can regress power, thermal behavior, or performance.
- Cross-generation similarity is not a substitute for compatibility. GC 11 and GC 12 have nearby names but different SQ/SQG selector widths, thread-trace fields, and clock override layouts.
- The chunk starts and ends mid-register-family. The merge lane must stitch it to adjacent chunks for the beginning of `TCP_PERFCOUNTER0_LO` and the remaining `ICG_SQ_CLK_CTRL` fields.

## Test and Validation Signals

Useful validation is mostly build, hardware bring-up, and profiling/debug coverage:

- Build AMDGPU, KFD, MES, SDMA, GFXHUB, IMU, and display configurations that include `gc/gc_12_0_0_sh_mask.h`; this catches missing or renamed macros.
- Run GC 12 graphics bring-up, reset, suspend/resume, and clock-gating tests to catch bad power-control masks and unexpected clock override persistence.
- Validate performance counters across TCP, GL1C/GL1XC, CB, DB, RMI, PA_PH, UTCL1, GL1A/GL1XA, GE2, GRBMH, SPI, PC, SQ/SQG, SX, TA, and TD, including multi-event selectors where available.
- Exercise TCP and CB filtering with known workloads so request-shape, data-format, sample-count, MRT, clear, and fragment filters change counter results as expected.
- Run SQ/SQG SPM sampling and sample-finish tests to verify `SPM_MODE`, `PERF_MODE`, stage enables, VMID filtering, force enable, and disabled ME/pipe fields.
- Capture SQ thread traces through both buffers, verify write pointer/status/owner VMID/error fields, and test high-water/low-water, interrupt, draw/marker sync, dropped-packet, halt, and poweroff-restore behavior.
- Use power-management telemetry to confirm clock-gating override changes do not leave ALU/TEX/LDS WGP domains forced on unexpectedly.

## Unresolved Cross-Chunk References

This chunk begins after `TCP_PERFCOUNTER0_LO` has already started, so the preceding comment and any earlier field context are in the previous chunk. It ends before the last fields of `ICG_SQ_CLK_CTRL`, so the final merged document should combine this analysis with the next chunk to cover that register completely.

### subset-b-002584: lines 37537-40041

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 37537-40041

## Scope

This chunk is a generated AMD GC 12.0.0 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro. There are no functions, structs, enums, variables, allocations, locks, callbacks, includes, or executable branches in this range.

The selected lines start in the tail of `ICG_SQ_CLK_CTRL`, with only the final shader-queue clock-override masks present in this chunk. The main body covers graphics clock-gating and power-related controls for SP, SX, TA, TD, DB, CB, RMI, PH, TCP, LDS, UTCL1, GRBMH, SC, and GL1 blocks; shader-array, render-backend, WGP/RB/SA remapping, and UTCL1 security fields; GC CAC accumulator and lookup-table status registers; then a long `rtavfs_rtavfs_ind_reg_blk` section from `RTAVFS_REG0` through the first fields of `RTAVFS_REG188`. The range ends before the remaining `RTAVFS_REG188` masks and later RTAVFS registers, so adjacent chunk research is required for the complete RTAVFS debug-bus block.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for the GC 12.0.0 graphics IP and is not Ceph filesystem code.

## Purpose

`gc_12_0_0_sh_mask.h` supplies bit layouts for GC 12.0.0 registers. AMDGPU code combines these masks with matching register-address macros from the GC 12.0.0 offset header and commonly accesses fields through helpers such as `REG_SET_FIELD` and `REG_GET_FIELD`. This lets ASIC-specific graphics, power, reset, debug, and performance code program or decode one hardware field without hard-coding raw bit positions.

This chunk focuses on low-level graphics power and topology metadata:

- ICG/CGTT clock-gating overrides for shader processor, shader export, texture/address/decompression, depth buffer, color buffer, RMI, primitive/geometry front-end, texture cache, LDS, UTCL1, GRBMH, scan converter, GL1C/GL1XC, GL1A/GL1XA, and GL1 internal return/source paths.
- Shader-array, WGP, render-backend, and shader-engine remap controls that expose inactive WGPs, disabled shader arrays, disabled RB backends, RMI redundancy repair bits, WGP-to-SA remapping, RB remapping, and SE-to-SA remapping.
- GL1 and GL1X pipe steering fields that select pipe mappings and steering mode.
- A UTCL1 security register with an identity-mode enable bit.
- GC CAC selection/control and full-width accumulator readouts for CP, EA, UTCL2 router/VML2/walker, GE, PMM, SDMA, CHC, RLC, GRBM, and GL2C blocks.
- Clock/power lookup-table fields for EDC/PCC stall-to-release, stall-to-power-break, power-break stall-to-release, and power-break release-to-stall patterns, fixed-pattern performance counters, and hardware LUT update done/error/error-step status.
- RTAVFS register fields for zone start/stop counts, zone enable masks, V/F anchor points, guard-band zones, CPO averaging and clock-divider settings, intercepts, PI controller coefficients, PSM and min/max sensing controls, AVFS/voltage regulator enables, override selectors, FSM counters, CPO start/stop/ripple counters, and target/current frequency count overrides.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this slice. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask within the 32-bit register value.
- Register-address symbols live in the companion GC 12.0.0 offset header, usually as `mm...` symbols with the same register name.
- AMDGPU callers normally combine these definitions with field-pack/extract helpers, MMIO accessors, indexed-register accessors, PM4 packet construction, power-management tables, register dumps, and reset/debug paths.

The main macro families in this chunk are:

- `ICG_SQ_CLK_CTRL`, `ICG_SP_CLK_CTRL`, `GFX_ICG_SX_CLK_CTRL0..4`, `GFX_ICG_TA_CTRL`, `GFX_ICG_TD_CTRL`, `DB_CGTT_CLK_CTRL_0`, `GFX_ICG_CB_CTRL`, `GFX_ICG_RMI_CTRL`, `GFX_ICG_SE_CAC_CLK_CTRL`, `CGTT_PH_CLK_CTRL0..3`, `GFX_ICG_TCP_CTRL`, `ICG_LDS_CLK_CTRL`, `GFX_ICG_UTCL1_CTRL`, and `GFX_ICG_GRBMH_CTRL`: clock-gating, soft-override, stall-override, debug-enable, off-hysteresis, and per-subunit override masks.
- `CGTT_SC_CLK_CTRL0..4`: scan-converter and primitive-binning clock/stall overrides, including VRC/HZC/HSC/HPF, PBB front/batch/raster/gather/output/passmem paths, DB/PKR/PA-SC interfaces, perfmon, dynamic, and register-clock override fields.
- `ICG_GL1C_CLK_CTRL`, `ICG_GL1XC_CLK_CTRL`, `GL1I_GL1R_MGCG_OVERRIDE`, `GL1XI_GL1XR_MGCG_OVERRIDE`, `ICG_GL1A_CTRL`, and `ICG_GL1XA_CTRL`: GL1/GL1X request, VM, UTCL0, GCR, source/return, GRBM, perf, and internal return/source DCLK override bits.
- `GL1_PIPE_STEER`, `GL1X_PIPE_STEER`, `GC_USER_SHADER_ARRAY_CONFIG`, `GRBMH_GC_USER_SA_UNIT_DISABLE`, `GC_USER_SA_UNIT_DISABLE_1`, `GC_USER_RB_BACKEND_DISABLE`, `GC_USER_RMI_REDUNDANCY`, and `GC_USER_SHADER_RATE_CONFIG*`: topology, repair, and shader-rate fields exposed through user or hypervisor-facing register blocks.
- `GRBMH_WGP_SA0_REMAP_CNTL`, `GRBMH_WGP_SA1_REMAP_CNTL`, `GRBMH_RB_SA0_REMAP_CNTL`, `GRBMH_RB_SA1_REMAP_CNTL`, and `GRBMH_GRBM_SA_REMAP_CNTL`: WGP, RB, and shader-array remap controls for harvesting, repair, or virtualization/topology presentation.
- `UTCL1_SECURITY`: UTCL1 identity-mode enable plus reserved high bits.
- `GC_CAC_ID`, `GC_CAC_CNTL`, and the many `GC_CAC_ACC_*` registers: CAC block/signal selection, threshold control, and 32-bit accumulator readback for named GC sub-blocks.
- `EDC_*`, `PCC_*`, `STALL_TO_PWRBRK_*`, `PWRBRK_STALL_TO_RELEASE_*`, and `PWRBRK_RELEASE_TO_STALL_*`: packed `FIRST_PATTERN_*` LUT entries, with 5-bit fields in release-oriented tables and 3-bit fields in power-break stall/release tables.
- `FIXED_PATTERN_PERF_COUNTER_1..10` and `HW_LUT_UPDATE_STATUS_1..2`: full-width counters and hardware LUT update status fields for tables 1-7.
- `RTAVFS_REG0..188` in this range: generated RTAVFS fields for five zones, four V/F points, guard bands, CPO averaging, PSM/min-max/PI controller configuration, voltage-code overrides, FSM timing counters, 64 CPO start/stop/ripple counters, and debug-bus selection.

## Control Flow

This header has no runtime control flow. Its behavior is compile-time macro substitution.

The implied AMDGPU runtime flow is:

1. Select the GC 12.0.0 register headers for the active ASIC.
2. Select a matching register address from the companion offset header or an indexed-register access path.
3. Read an existing register value, prepare a new control value, build a command or firmware table entry, or decode a debug/status dump.
4. Use the `__SHIFT` and `__MASK` pair, commonly through register field helpers, to pack or extract the relevant field.
5. Write or decode the value in graphics clock-gating setup, power-management sequencing, topology/harvesting setup, CAC/performance diagnostics, RTAVFS calibration/control, reset recovery, suspend/resume restore, virtualization, or hang/debug paths.

For clock-gating and topology registers, the driver or firmware typically programs fields during ASIC initialization, power-state transitions, IP block bring-up, debug override, reset recovery, or virtualization partitioning. For CAC and LUT status registers, flows are diagnostic/performance oriented: select a block/signal, configure a threshold or lookup pattern, read accumulators, and check update-completion/error state. For RTAVFS, the implied flow is more state-machine oriented: configure zones, enable CPO/PSM sensing, define PI controller coefficients and guard bands, optionally override voltage/frequency-count values, run or observe AVFS logic, and read counters/status. The header itself does not encode sequencing, polling, locking, register-index selection, firmware ownership, or hardware side-effect rules.

## State And Persistence Behavior

The macros are stateless and persist nothing. They describe GPU registers whose state is owned by hardware, firmware, and AMDGPU runtime code.

Clock-gating and clock-stall override fields are persistent hardware control state while the corresponding IP block is powered. They may be reset to hardware defaults across GPU reset, power gating, BACO/suspend-resume, or IP block reinitialization. Setting soft overrides can deliberately keep clocks ungated for debug or workaround purposes, but can also increase power and hide power-management bugs.

Topology and remap registers represent hardware-presented resource layout: disabled WGPs, shader arrays, render backends, RMI repair selection, GL1/GL1X pipe steering, WGP-to-SA remapping, RB remapping, and SE-to-SA remapping. These values affect how work is routed through graphics resources and may be programmed from fuses, firmware tables, driver discovery, or virtualization policy. Incorrect persistence or restore ordering can expose unavailable resources or route traffic to the wrong physical unit.

`UTCL1_SECURITY__UTCL1_IDENTITY_MODE_ENABLE` is security-relevant configuration state. The header exposes the bit layout only; ownership and allowed transitions are enforced elsewhere by PSP/firmware/driver policy.

GC CAC accumulator registers are readback-style diagnostic/performance state. Accumulator values change with block activity and selected signals. `GC_CAC_ID` and `GC_CAC_CNTL` configure what is observed and how thresholds are applied; accumulator read timing and clearing/latching behavior are not described in this generated header.

Lookup-table and update-status fields persist hardware power/clock transition policy and expose whether hardware LUT updates completed or failed, including small error-step fields. These fields are sensitive to firmware and power-management sequencing; stale done/error bits or mismatched pattern widths can mislead diagnostics.

RTAVFS registers model a large stateful adaptive-voltage/frequency-control subsystem. Zone counts and enable masks define measurement windows, V/F point fields define anchor frequency-count and voltage-code pairs, CPO fields control oscillator measurement, PSM fields control voltage regulator/VDD sensing paths, PI fields control feedback loop behavior, and FSM counters/status expose runtime state. The 64 CPO start/stop/ripple-counter families are volatile measurements. Override fields such as voltage-code override, target/current frequency-count override, and selection bits can bypass normal hardware behavior and therefore should be treated as active controls rather than passive metadata.

Reserved and unused fields appear throughout. Their existence as macros does not make them safe to program arbitrarily; driver code should preserve reserved bits during read-modify-write unless the hardware sequence explicitly requires a full-register value.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.0.0 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h` provides matching register addresses and indexed-register selectors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_default.h`, if present in the same generated family, provides reset/default values for many registers.
- AMDGPU register helper macros provide field packing/extraction and MMIO or indexed-register access mechanisms.
- AMDGPU GFX, RLC, GRBM, KFD/compute-adjacent, power-management, clock-gating, topology/harvesting, reset, virtualization, diagnostics, and debug dump paths can include these constants.
- Firmware/PSP/SMU/RLC interactions are likely for the security, power, RTAVFS, and LUT/CAC families, even though this header only supplies bit definitions.

Integration points include ASIC initialization clock-gating tables, debug paths that force clocks on, power-management or SMU-facing code that configures RTAVFS and LUT patterns, GRBM/topology setup that reflects harvested WGP/RB/SA resources, GL1/GL1X pipe steering, UTCL1 identity/security mode policy, CAC/performance counter collection, and GPU reset/suspend-resume restore code that must reapply or preserve control registers in the expected order.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask compiles cleanly but can write the wrong hardware bits or decode misleading state.
- This chunk starts and ends mid-family. It begins after most `ICG_SQ_CLK_CTRL` shifts/masks and ends before the remaining `RTAVFS_REG188` fields, so adjacent chunks are needed for complete file-level conclusions.
- Many clock-gating fields are active controls. Accidentally setting a soft override or stall override can change power, timing, idle behavior, or debug visibility without producing a local software error.
- Reserved fields are explicitly named in several families, especially `CGTT_SC_CLK_CTRL3`, RTAVFS, and UTCL1 security. These should not be treated as normal programmable bits without hardware guidance.
- Repeated bitfield families are susceptible to single-index mistakes: TA/TD soft overrides, PH/TCP/LDS/UTCL1 overrides, SC PBB paths, WGP/RB remaps, LUT pattern tables, update-status tables, RTAVFS zones, V/F points, and 64 CPO counters all have repeated structures.
- Topology/remap fields can expose or route to harvested, disabled, or remapped physical units. Incorrect masks may cause hangs, incorrect wave scheduling, unavailable render backends, wrong cache steering, or invalid virtualized topology.
- UTCL1 identity mode is security-sensitive. Misprogramming could affect address identity behavior or isolation assumptions; this header gives no policy constraints.
- CAC accumulator fields are full-width readouts whose meaning depends on selected block/signal and timing. Misusing `GC_CAC_ID` or threshold fields can produce plausible but irrelevant performance data.
- LUT pattern fields have different widths across families: EDC/PCC and power-break stall-to-release use 5-bit masks, while stall-to-power-break and power-break release-to-stall use 3-bit masks. Reusing packing logic blindly can corrupt adjacent entries.
- RTAVFS override, PI, PSM, CPO, and FSM fields can affect voltage/frequency behavior. Errors here can cause instability, power regressions, thermal issues, or misleading AVFS telemetry rather than a simple render failure.
- CPO start/stop/ripple counters are volatile measurement state. Treating them as persistent configuration or comparing them without a controlled measurement window can produce false failures.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, hardware diagnostics, and power-management telemetry:

- Kernel build coverage for AMDGPU files that include `gc_12_0_0_sh_mask.h`, especially GC 12.0.0 GFX, GRBM/RLC, clock-gating, power-management, topology, reset, and debug code.
- Mechanical comparison against AMD's authoritative GC 12.0.0 register database to confirm every `__SHIFT` and `__MASK` value in lines 37537-40041.
- Cross-checks that registers in this chunk have matching address macros in `gc_12_0_0_offset.h` and expected defaults in the matching default header where generated.
- Static sanity checks that masks align with shifts, full-width fields use `0xFFFFFFFFL`, repeated families remain structurally consistent across indices, and reserved masks do not overlap named programmable fields.
- Clock-gating tests that toggle debug/soft overrides under controlled conditions and verify idle clocks, power draw, wake latency, and hang-free graphics/compute activity.
- Topology and harvesting tests that confirm disabled WGP/SA/RB masks, remap controls, RMI repair bits, GL1/GL1X pipe steering, and shader-rate fields match discovered hardware and virtualized resource exposure.
- Security and firmware validation for `UTCL1_SECURITY` transitions, including checks that identity mode is only changed by the expected authority and restores correctly after reset/resume.
- CAC/performance diagnostics that select known GC blocks/signals, exercise CP/EA/UTCL2/SDMA/GRBM/GL2C activity, and verify accumulator behavior and threshold handling.
- LUT programming tests that update EDC/PCC/power-break tables, poll `HW_LUT_UPDATE_STATUS_1..2`, and confirm done/error/error-step bits match expected success or injected-failure cases.
- RTAVFS validation that covers zone enable/start/stop settings, V/F anchors, CPO averaging and counters, PI coefficient/anti-windup behavior, PSM min/max/average sensing, voltage-code overrides, target/current frequency-count overrides, and FSM counter progression under controlled workloads.
- Runtime warning signals include higher idle power, unexpected clock residency, GPU hangs during power transitions, invalid harvested-resource exposure, wrong performance counter data, LUT update errors, RTAVFS FSM stalls, voltage/frequency instability, or debug dumps with impossible CPO/ripple-counter state.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002584`. It covers lines 37537-40041 of `gc_12_0_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the preceding `ICG_SQ_CLK_CTRL` family, the trailing `RTAVFS_REG188` debug-bus masks and later RTAVFS registers, and the broader GC 12.0.0 generated register-map context.

### subset-b-002585: lines 40042-40550

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 40042-40550

## Scope

This chunk is the final segment of the generated AMD GC 12.0.0 shift/mask register header. It contains preprocessor constants only. Each hardware field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro. There are no C functions, structs, enums, storage definitions, includes, locks, allocations, callbacks, or executable branches in this range.

The selected lines begin in the middle of `RTAVFS_REG188`, then cover `RTAVFS_REG189` through `RTAVFS_REG194`, the `dbgu_gfx_ports_blk` `PACKER_CONTROL` register, the `gfx_se_sqind` shader-queue indirect register fields for local debug and wave state, and the final `gfx_se_secacind` SE CAC indirect fields. The chunk ends with the file-level `#endif`.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for the GC 12.0.0 graphics IP and is not Ceph filesystem logic.

## Purpose

`gc_12_0_0_sh_mask.h` supplies bit layouts for GC 12.0.0 registers. AMDGPU code combines these masks with addresses from the companion `gc_12_0_0_offset.h` header and with register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, and `RREG32_SOC15`. This lets the driver pack, update, and decode individual hardware fields without embedding raw bit positions throughout engine setup, debug, reset, power, and wave-inspection code.

This specific chunk focuses on late debug and shader-engine metadata:

- RTAVFS control/status fields for debug-bus selection, voltage-code readback, VDD state, loop control, retention save/restore, FSM stop points, scaled/final CPO count reporting, FSM state, and ripple-counter readback.
- A 64-bit debug packer control register with presence, enable, stream ID, and reserved fields.
- Shader queue local status and control fields, including wave occupancy and busy bits for SQ, instruction-side, instruction buffer, arbiter, export, barrier-message, and VM activity.
- Per-wave execution state, including active/valid/idle slots, floating-point mode, scalar prefetch/performance flags, status bits, private wave state, GPR/LDS allocation, instruction-buffer counters, performance snapshot fields, exception flags, trap controls, scratch base, hardware ID, scheduling mode, shader cycle count, DVGPR allocation, PC, TTMP registers, `M0`, and `EXEC`.
- Shader-engine CAC selector/control fields for choosing a CAC block/signal and threshold.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this slice. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask within the register value.
- Address symbols for the same registers are in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h`, commonly as `ix...`, `mm...`, or `reg...` symbols depending on address space.
- AMDGPU callers usually consume these constants through register field helpers, direct MMIO helpers, SQ indirect read helpers, debugfs wave dump code, context save/restore paths, or command-packet construction.

The main macro families in this chunk are:

- `RTAVFS_REG188`: debug-bus enable and selection, using `RTAVFSRTAVFSDBGBUSEN`, `RTAVFSRTAVFSDBGBUSSELREG`, `RTAVFSUSEDBGBUSSELFROMREG`, `RTAVFSRTAVFSDBGSTREAMVALIDSEL`, `RTAVFSRTAVFSDBGSTREAMCLKDIV`, and `RTAVFSRTAVFSDBGSTREAMFSMBITSEL`.
- `RTAVFS_REG189`: AVFS voltage-code and VDD readback fields, including `RTAVFSVOLTCODEFROMPI`, `RTAVFSVOLTCODEFROMBINARYSEARCH`, `RTAVFSVDDREGON`, and `RTAVFSVDDABOVEVDDRET`.
- `RTAVFS_REG190`: AVFS loop and retention controls, including ignore-RLC request, ripple-counter output select, run loop, save/restore CPO weights, and reset retention registers.
- `RTAVFS_REG191`: stop-at-debug controls for AVFS FSM checkpoints such as startup, idle, reset CPO/ripple counters, start CPOs, start ripple counters, ripple counters done, final CPO result ready, voltage code ready, target voltage ready, stop CPOs, and wait for ACK.
- `RTAVFS_REG192` through `RTAVFS_REG194`: AVFS scaled/final CPO counts, FSM state, and 32-bit ripple-counter readback.
- `PACKER_CONTROL`: a 64-bit debug packer register with `PackerPresent`, `PackerEnable`, `StreamID`, and reserved-bit masks. Its mask constants use 64-bit-looking values, including `0xFFFFFFFFFFFFFF00L`.
- `SQ_DEBUG_STS_LOCAL` and `SQ_DEBUG_CTRL_LOCAL`: local SQ busy/wave-level status and a simple 8-bit unused control field.
- `SQ_WAVE_ACTIVE` and `SQ_WAVE_VALID_AND_IDLE`: 20-bit wave-slot bitmaps.
- `SQ_WAVE_MODE`: floating-point round/denorm mode plus `FP16_OVFL`, `SCALAR_PREFETCH_EN`, and `DISABLE_PERF`.
- `SQ_WAVE_STATUS`: per-wave status flags for privilege, trap enable, export readiness, `EXECZ`, `VCCZ`, in-workgroup, trap and trap-barrier state, valid/idle status, skip export, fatal halt, VGPR availability, LDS parameter readiness, GS/export obligations, wave64, DVGPR enable, and WGP takeover.
- `SQ_WAVE_STATE_PRIV`: private scheduler/debug state such as workgroup round-robin, sleep/wakeup, barrier completion, named barrier ID, `SCC`, priority, halt, poison error, conditional debug, scratch enable, performance enable, and thread trace enable.
- `SQ_WAVE_GPR_ALLOC`, `SQ_WAVE_LDS_ALLOC`, `SQ_WAVE_DVGPR_ALLOC_LO`, and `SQ_WAVE_DVGPR_ALLOC_HI`: VGPR/LDS/DVGPR allocation packing.
- `SQ_WAVE_IB_STS`, `SQ_WAVE_IB_STS2`, `SQ_WAVE_IB_DBG1`, and `SQ_WAVE_FLUSH_IB`: outstanding instruction-buffer and memory/export counter fields, forward progress, SPI thread-trace enable, idle/debug counters, and a full-width flush register.
- `SQ_PERF_SNAPSHOT_DATA`, `SQ_PERF_SNAPSHOT_DATA1`, `SQ_PERF_SNAPSHOT_DATA2`, `SQ_PERF_SNAPSHOT_PC_LO`, and `SQ_PERF_SNAPSHOT_PC_HI`: wave performance snapshot validity, issue/no-issue state, PC, wave count, issued/stalled arbiter states, and operation counters.
- `SQ_WAVE_EXCP_FLAG_PRIV`, `SQ_WAVE_EXCP_FLAG_USER`, and `SQ_WAVE_TRAP_CTRL`: privileged and user exception causes plus trap enable controls for ALU exceptions, address watch, wave end, trap-after-instruction, memory violation, context save, illegal instruction, host trap, XNACK error, and first memory-violation source.
- `SQ_WAVE_SCRATCH_BASE_LO` and `SQ_WAVE_SCRATCH_BASE_HI`: full 32-bit scratch base pieces.
- `SQ_WAVE_HW_ID1` and `SQ_WAVE_HW_ID2`: wave identity, SIMD/WGP/SA/SE placement, DP rate, queue/pipe/ME/state/workgroup/VM IDs.
- `SQ_WAVE_SCHED_MODE`, `SQ_SHADER_CYCLES_LO`, `SQ_SHADER_CYCLES_HI`, `SQ_WAVE_PC_LO`, `SQ_WAVE_PC_HI`, `SQ_WAVE_TTMP0` through `SQ_WAVE_TTMP15`, `SQ_WAVE_M0`, `SQ_WAVE_EXEC_LO`, and `SQ_WAVE_EXEC_HI`: scheduler mode, shader cycle counter, program counter, trap temporary registers, `M0`, and execution mask fields.
- `SE_CAC_ID` and `SE_CAC_CNTL`: CAC block/signal selection and 16-bit threshold.

## Control Flow

The header has no runtime control flow. Its behavior is compile-time macro substitution.

The implied AMDGPU runtime flow is:

1. Select the GC 12.0.0 register headers for a matching ASIC.
2. Use the companion offset header to find the address or indirect index for a register.
3. Read a current register value, compose a new value, or collect a debug/status dump.
4. Use the `__SHIFT` and `__MASK` pair, either directly or through field helper macros, to pack or extract the field.
5. Submit the final value through MMIO, SQ indirect access, a command processor packet, debugfs readback, firmware interface, or a context save/restore table.

Concrete integration in this tree appears in `gfx_v12_0_read_wave_data()`: it selects SQ indirect addresses such as `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_PC_LO`, `ixSQ_WAVE_PC_HI`, `ixSQ_WAVE_EXEC_LO`, `ixSQ_WAVE_EXEC_HI`, `ixSQ_WAVE_HW_ID1`, `ixSQ_WAVE_HW_ID2`, `ixSQ_WAVE_GPR_ALLOC`, `ixSQ_WAVE_LDS_ALLOC`, `ixSQ_WAVE_IB_STS`, `ixSQ_WAVE_IB_STS2`, `ixSQ_WAVE_IB_DBG1`, `ixSQ_WAVE_M0`, `ixSQ_WAVE_MODE`, `ixSQ_WAVE_STATE_PRIV`, `ixSQ_WAVE_EXCP_FLAG_PRIV`, `ixSQ_WAVE_EXCP_FLAG_USER`, `ixSQ_WAVE_TRAP_CTRL`, `ixSQ_WAVE_ACTIVE`, `ixSQ_WAVE_VALID_AND_IDLE`, `ixSQ_WAVE_DVGPR_ALLOC_LO`, `ixSQ_WAVE_DVGPR_ALLOC_HI`, and `ixSQ_WAVE_SCHED_MODE`. `amdgpu_debugfs_wave_read()` then exposes this GFX-version-specific wave status stream through debugfs after selecting the target SE/SH/CU/WGP/SIMD/wave.

The RTAVFS, packer, and SE CAC fields do not create control flow in this header. Their control-flow semantics are hardware-defined: writes can enable a debug bus, force AVFS debug stop points, start/stop loops, select counters, or change capture thresholds, while reads can observe volatile hardware state.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe hardware register fields whose values are owned by GPU hardware, firmware, and AMDGPU runtime programming.

RTAVFS fields are power/voltage/frequency state and debug control. Voltage codes, VDD flags, FSM state, scaled CPO counts, final minimum CPO counts, and ripple-counter readback are volatile hardware observations. `RTAVFSRUNLOOP`, `RTAVFSSAVECPOWEIGHTS`, `RTAVFSRESTORECPOWEIGHTS`, and `RTAVFSRESETRETENTIONREGS` are active controls rather than passive state. The stop-at fields in `RTAVFS_REG191` can intentionally halt AVFS sequencing at internal milestones and should be treated as debug or bring-up controls.

`PACKER_CONTROL` configures a debug stream packer. Presence is likely read-only capability, while enable and stream ID affect debug stream routing. Reserved fields occupy most of the 64-bit value and should be preserved unless the authoritative hardware sequence says otherwise.

SQ wave registers describe live per-wave state. Active, valid/idle, status, mode, private state, allocation, outstanding-counter, exception, trap, PC, TTMP, M0, EXEC, cycle, and hardware-ID fields can change while waves execute, trap, halt, context-save, or retire. Reading them through SQ indirect access is a snapshot-like diagnostic operation, not persistent kernel state. The debugfs path protects selection with `adev->grbm_idx_mutex` and resets GRBM selection afterward, but the values remain race-prone with live GPU execution.

Exception and trap fields have both diagnostic and control implications. Privileged exception flags report causes such as address watch, memory violation, save-context, illegal instruction, host trap, wave start/end, performance snapshot, trap-after-instruction, and XNACK error. User exception flags report ALU and graphics/user events such as invalid operation, denorm input, divide by zero, overflow, underflow, inexact, integer divide by zero, buffer out-of-bounds, and LOD clamping. Trap-control bits determine which events can trap.

SE CAC fields configure or read counters in an indirect shader-engine counter block. `CAC_BLOCK_ID`, `CAC_SIGNAL_ID`, and `CAC_THRESHOLD` are small packed fields and likely depend on a block-specific selector protocol outside this header.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.0.0 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h` provides matching addresses and indirect indices, including `ixRTAVFS_REG188` through `ixRTAVFS_REG194`, `ixPACKER_CONTROL`, `ixSQ_DEBUG_STS_LOCAL`, `ixSE_CAC_ID`, `ixSE_CAC_CNTL`, and the SQ wave indirect `ixSQ_WAVE_*` registers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_0.c` includes this header and uses the SQ indirect index macros in the GFX12 wave dump helpers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_debugfs.c` exposes GFX wave state through debugfs and dispatches to the GFX-version-specific `read_wave_data` function.
- Other GC 12.0.0 include users in this tree include `soc24.c`, `sdma_v7_0.c`, `mes_v12_0.c`, `gfxhub_v12_0.c`, `imu_v12_0.c`, and `amdgpu_amdkfd_gfx_v12.c`; they rely on the same generated shift/mask contract for ASIC-specific register access even if not every field in this chunk is referenced directly.
- AMDGPU field helpers and SOC15 MMIO macros are the main consumers for packing/extracting these values.

Integration points are mostly diagnostics, debug, power, and shader-engine inspection:

- AVFS/power-management debug or firmware-facing sequences can use RTAVFS fields to observe voltage/frequency loop internals and retention behavior.
- Debug bus and packer controls feed hardware debug streaming.
- SQ wave readback supports debugfs, hang diagnostics, wave-state dumps, KFD/compute debugging, trap analysis, and low-level scheduler/occupancy inspection.
- Exception and trap masks tie into shader trap handling, memory fault diagnosis, user exception visibility, and context save/restore behavior.
- Cycle counters, performance snapshots, IB counters, and busy bits support performance diagnostics and hang triage.
- SE CAC selector/threshold fields support shader-engine activity or counter-threshold instrumentation.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask compiles cleanly but can decode the wrong wave-state bit or program the wrong control bit.
- This chunk begins mid-register at `RTAVFS_REG188`; the first three shift macros for that register are in the previous chunk. File-level research must merge adjacent chunks before drawing complete conclusions about `RTAVFS_REG188`.
- `PACKER_CONTROL` uses masks wider than 32 bits. Callers must avoid truncating its reserved or stream fields through 32-bit-only helper assumptions when accessing the underlying register is truly 64-bit.
- RTAVFS controls are not ordinary status fields. Misprogramming run-loop, save/restore CPO weights, retention reset, ignore-RLC request, or stop-at bits can perturb voltage/frequency management and cause hangs, incorrect frequency decisions, or misleading power telemetry.
- SQ indirect wave state is volatile. Debugfs or hang-dump readers can observe partial progress, retired waves, or state that changes between consecutive indirect reads. Tests should not assume all fields form an atomic snapshot unless the surrounding hardware sequence freezes execution.
- `SQ_WAVE_STATUS` in GC 12.0.0 differs from older generations. For example, this layout has `IN_WG`, `OREO_CONFLICT`, `NO_VGPRS`, `LDS_PARAM_READY`, `MUST_GS_ALLOC`, `IDLE`, `WAVE64`, `DVGPR_EN`, and `WGP_TAKEOVER`, while older headers use other status names such as `HALT`, `ECC_ERR`, `ALLOW_REPLAY`, or `IN_TG`. Cross-generation debug decoders must use the correct ASIC layout.
- Exception and trap fields are security and correctness sensitive. Enabling or mis-decoding address watch, memory violation, host trap, save-context, XNACK, buffer OOB, or trap-after-instruction bits can confuse trap handlers or hide real faults.
- Allocation fields have compact widths. VGPR base/size, LDS base/size, VGPR shared size, and DVGPR segment fields must be interpreted in hardware units, not raw byte counts, unless a caller explicitly converts units.
- Split fields such as PC low/high, scratch base low/high, shader cycles low/high, and EXEC low/high need correct composition and ordering in debug decoders. A high/low mismatch can point to an impossible PC or execution mask.
- Reserved and `UNUSED` masks document occupied bits, but do not make those bits safe to set. Read-modify-write code should preserve reserved fields unless a documented sequence requires otherwise.
- SE CAC block and signal IDs are selector-dependent. A valid field encoding can still select an unsupported or meaningless signal on a particular ASIC stepping.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, and hardware/runtime diagnostics:

- Kernel build coverage for AMDGPU files that include `gc_12_0_0_sh_mask.h`, especially GFX12, MES, KFD, GFXHUB, IMU, SDMA, and SOC initialization paths.
- Mechanical comparison against AMD's authoritative GC 12.0.0 register database to confirm every `__SHIFT` and `__MASK` value in lines 40042-40550.
- Cross-checks that all registers in this chunk have matching address or indirect-index macros in `gc_12_0_0_offset.h`.
- Static sanity checks that masks align with shifts, full-width data fields use `0xFFFFFFFFL`, `SQ_SHADER_CYCLES_HI` is limited to `0x0FFFFFFF`, 20-bit wave-slot masks stay at `0x000FFFFF`, and the DVGPR segment masks remain structurally consistent across segments 0-7.
- GFX12 debugfs wave-read tests that access `/sys/kernel/debug/dri/.../amdgpu_wave` or equivalent debugfs paths and verify the type-4 wave-data layout can be read without invalid GRBM selection or runtime-power failures.
- Hang-dump or shader-debug tests that decode `SQ_WAVE_STATUS`, PC, EXEC, HW IDs, allocation registers, exception flags, trap controls, and mode/private-state fields on a known workload.
- Trap and exception workloads that trigger representative ALU exceptions, buffer OOB, address-watch, host trap, save-context, wave-start/wave-end, and XNACK paths where hardware and firmware support them.
- Power/AVFS bring-up diagnostics that read RTAVFS voltage code, VDD state, CPO count, FSM state, and ripple-counter fields under controlled clock/voltage conditions.
- Debug-stream tests that validate packer presence/enable/stream-ID behavior without disturbing reserved bits.
- SE CAC tests that select known CAC block/signal IDs and confirm threshold programming or readback follows the hardware specification.
- Runtime warning signals include GFX12 wave dumps with impossible IDs or masks, broken debugfs reads, GPU hangs during wave/trap inspection, inconsistent power/AVFS telemetry, corrupted performance snapshots, or debug stream data loss after packer/control changes.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002585`. It covers lines 40042-40550 of `gc_12_0_0_sh_mask.h`, the tail of the file. The final per-file research should merge it with the previous chunk for the beginning of `RTAVFS_REG188` and with earlier chunks that define the rest of the GC 12.0.0 register map.
