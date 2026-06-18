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
