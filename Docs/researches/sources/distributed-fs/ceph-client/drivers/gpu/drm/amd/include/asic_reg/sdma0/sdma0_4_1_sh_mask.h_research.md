# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0/sdma0_4_1_sh_mask.h

## Purpose

This header is the SDMA0 4.1 register-field mask and shift map for the AMD GPU driver copy of the Ceph client source tree. It is a generated-style C preprocessor contract for the `sdma0_sdma0dec` address block: every exported symbol names a register field and provides either the bit shift (`__SHIFT`) or bit mask (`_MASK`) needed to compose, update, or decode 32-bit SDMA0 MMIO register values.

The file has no executable logic, functions, structs, or enums. Its purpose is ABI-like: driver code includes this header alongside the matching register offset headers and uses the constants to program SDMA firmware upload, virtual memory context registers, public SDMA controls, UTCL1 fault/XNACK state, power and clock controls, GFX queue registers, and the RLC0/RLC1 SDMA queue register sets.

## Important APIs, Types, and Macros

- Include guard: `_sdma0_4_1_SH_MASK_HEADER` prevents duplicate macro definitions within a translation unit.
- Exported field constants: 1,416 total field macros, split into 708 `__SHIFT` constants and 708 `_MASK` constants.
- Naming pattern: `REGISTER__FIELD__SHIFT` gives the low-bit position for a field, while `REGISTER__FIELD_MASK` gives the already-positioned bit mask. These are intended for helpers such as `REG_SET_FIELD`, manual `value << SHIFT`, and mask tests.
- Public and discovery/control groups:
  - `SDMA0_UCODE_ADDR`, `SDMA0_UCODE_DATA`, `SDMA0_UCODE_CHECKSUM`, and `SDMA0_F32_CNTL` describe microcode address/data/checksum and F32 halt/step controls.
  - `SDMA0_PUB_REG_TYPE0` through `SDMA0_PUB_REG_TYPE3` map public register grouping/type bitmaps.
  - `SDMA0_CONTEXT_REG_TYPE0` through `SDMA0_CONTEXT_REG_TYPE3` map context-save/restore grouping for GFX context registers.
- VM and virtualization groups:
  - `SDMA0_VM_CNTL`, `SDMA0_VM_CTX_LO`, `SDMA0_VM_CTX_HI`, `SDMA0_VM_CTX_CNTL`, `SDMA0_ACTIVE_FCN_ID`, and `SDMA0_VIRT_RESET_REQ` expose VM command, context address, privilege/VMID, VF/PF, and virtual reset fields.
  - `SDMA0_GPU_IOV_VIOLATION_LOG` captures GPU IOV violation status, address, operation type, VF/VFID, and initiator.
- Engine control and status groups:
  - `SDMA0_CNTL` covers trap, UTC L1, semaphore wait interrupt, data/fence byte-swap, mid-command preempt/world-switch, auto context switch, context-empty, frozen, and IB preempt interrupt bits.
  - `SDMA0_STATUS_REG`, `SDMA0_STATUS1_REG`, `SDMA0_STATUS2_REG`, and `SDMA0_STATUS3_REG` expose idle, ring-buffer, IB, MC, SRBM, semaphore, interrupt, command-op, exception, and copy-engine status bits.
  - `SDMA0_FREEZE`, `SDMA0_PHASE0_QUANTUM`, `SDMA0_PHASE1_QUANTUM`, and `SDMA0_RELAX_ORDERING_LUT` describe preemption/freeze, scheduling quantum, and ordering behavior by packet category.
- Power, clock, and reliability groups:
  - `SDMA0_POWER_CNTL`, `SDMA_POWER_GATING`, `SDMA_PGFSM_CONFIG`, `SDMA_PGFSM_WRITE`, `SDMA_PGFSM_READ`, `SDMA0_POWER_CNTL_IDLE`, `SDMA0_CLK_CTRL`, and `SDMA0_ULV_CNTL` expose power gating, FSM, memory power, idle delay, clock override, and ultra-low-voltage status/control fields.
  - `SDMA0_EDC_CONFIG`, `SDMA0_EDC_COUNTER`, and `SDMA0_EDC_COUNTER_CLEAR` expose error detection/correction configuration and counters.
  - `SDMA0_PERFMON_CNTL`, `SDMA0_PERFCOUNTER0_RESULT`, `SDMA0_PERFCOUNTER1_RESULT`, and `SDMA0_PERFCOUNTER_TAG_DELAY_RANGE` expose SDMA performance monitoring fields.
- Addressing and memory-system groups:
  - `SDMA0_GB_ADDR_CONFIG` and `SDMA0_GB_ADDR_CONFIG_READ` expose pipe, pipe-interleave, bank-interleave, bank count, and shader-engine count fields.
  - `SDMA0_MMHUB_CNTL`, `SDMA0_MMHUB_TRUSTLVL`, `SDMA0_PHYSICAL_ADDR_LO`, `SDMA0_PHYSICAL_ADDR_HI`, and `SDMA0_CRD_CNTL` describe MMHUB unit/trust and physical address/credit fields.
  - `SDMA0_UTCL1_CNTL`, `SDMA0_UTCL1_WATERMK`, `SDMA0_UTCL1_RD_STATUS`, `SDMA0_UTCL1_WR_STATUS`, `SDMA0_UTCL1_INV0` through `INV2`, `SDMA0_UTCL1_RD_XNACK0/1`, `SDMA0_UTCL1_WR_XNACK0/1`, `SDMA0_UTCL1_TIMEOUT`, and `SDMA0_UTCL1_PAGE` cover UTCL1 retry, watermarks, page faults/null pages, invalidation, XNACK address/VMID/vector, timeout, and page request attributes.
- Queue and context register groups:
  - `SDMA0_GFX_*` describes the primary GFX SDMA queue: ring buffer control/base/read pointer/write pointer, writeback/polling addresses, IB control/base/size, skip count, context status/control, doorbell, watermark, CSA address, preempt, AQL, minor pointer update, and mid-command save data.
  - `SDMA0_RLC0_*` and `SDMA0_RLC1_*` repeat the same queue/context vocabulary for two RLC SDMA queues.

## Control Flow

There is no runtime control flow inside this header. Control flow enters indirectly when C files include it and then use the constants during SDMA initialization, queue setup, suspend/resume, interrupt control, fault reporting, or diagnostics.

The usual consuming pattern is:

1. Read a 32-bit SDMA register with an MMIO helper.
2. Clear bits with a `_MASK` constant, set bits with either `_MASK` or `value << __SHIFT`, or use register helper macros that pair register and field names with this header's definitions.
3. Write the updated value back through an SDMA/SOC15 MMIO helper.
4. Poll a status register field, such as an idle or context-status mask, until hardware reaches the expected state.

Examples visible elsewhere in the AMD driver tree include ring-buffer enable/disable through `SDMA0_GFX_RB_CNTL__RB_ENABLE_MASK`, trap/context-empty interrupt toggles through `SDMA0_CNTL__*` bits, KFD MQD construction through `SDMA0_RLC0_RB_CNTL__RB_SIZE__SHIFT` and related fields, and SDMA idle checks through `SDMA0_STATUS_REG__IDLE_MASK`.

## State and Persistence Behavior

The file itself stores no mutable state and performs no persistence. The constants describe hardware state that persists in SDMA0 registers until changed by the driver, firmware, GPU reset, power-gating transition, or hardware event.

State represented by this map includes:

- SDMA firmware programming state (`UCODE_ADDR`, `UCODE_DATA`, checksum, F32 halt/step).
- Queue state for GFX/RLC queues: ring buffer base, high address, read/write pointers, pointer writeback, write-pointer polling, IB base/offset/size, context status, doorbell capture, AQL mode, and preemption state.
- VM and UTCL1 state: VM command/context fields, retry control, invalidation vectors, XNACK fault address/VMID/vector, page-fault/null-page bits, and read/write FIFO status.
- Power and clock state: power-gating enable/request/status, clock override bits, memory power override and delays, idle delays, and ULV interrupt/status bits.
- Error and observability state: EDC counters, IOV violation logs, error logs, performance counter configuration/results, and status registers.

Because many fields are status, latch, or control bits owned jointly by firmware and hardware, consumers must preserve unrelated bits with read-modify-write sequences unless the hardware programming guide explicitly allows full-register writes.

## Dependencies

- This header depends only on the C preprocessor and standard integer literal syntax; it includes no other files.
- It is intended to be included with matching SDMA0 4.1 register offset headers in the same generated `asic_reg` hierarchy, so callers can combine `mm/regSDMA0_*` offsets with these field masks/shifts.
- Consumers depend on common AMDGPU register helpers such as MMIO read/write wrappers and field helpers (`REG_SET_FIELD`, mask tests, and SOC15 SDMA offset helpers). Those helpers are not defined here.
- It has sibling architecture/version headers such as `sdma0_4_0_sh_mask.h`, `sdma0_4_2_sh_mask.h`, and matching `sdma1` headers. Version skew matters: fields with identical names may differ across ASIC generations, and some later SDMA versions add or rename fields.

## Integration Points

- `amdgpu` SDMA engine code uses this style of header during SDMA ring initialization, halt/resume, timeout programming, trap/context-empty interrupt handling, idle polling, clock/power gating, golden-register setup, and diagnostics.
- `amdkfd` MQD and queue-management paths use RLC/GFX queue field shifts and masks to build memory queue descriptors and to enable/disable SDMA queues while waiting for context-idle status.
- SOC15 register-offset layers pair these masks with per-ASIC MMIO offsets and per-instance SDMA index calculations.
- Debug and fault-reporting paths can decode UTCL1 read/write status, XNACK registers, IOV violation logs, EDC counters, and SDMA status registers with these masks.
- Power-management paths depend on the `SDMA0_POWER_CNTL`, `SDMA_POWER_GATING`, `SDMA_PGFSM_*`, `SDMA0_CLK_CTRL`, and `SDMA0_ULV_CNTL` fields to avoid corrupting hardware state during clock gating, memory power transitions, and suspend/resume.

## Risks and Edge Cases

- Hardware contract risk: an incorrect mask or shift silently programs the wrong hardware bits. Failures may present as SDMA queue hangs, invalid DMA, VM faults, missed interrupts, broken preemption, power-management instability, or GPU reset.
- Version skew risk: this is specifically the SDMA0 4.1 map. Accidentally including a 4.0/4.2 or SDMA1 header for an SDMA0 4.1 code path can compile successfully while targeting the wrong field layout.
- Field-width risk: callers that shift values manually must bound values to the field width. For example queue size, VMID, address-low alignment, timeout, watermarks, and quantum fields have finite masks; overflow will corrupt adjacent fields unless masked before insertion.
- Reserved-bit risk: several group/type and control registers include `RESERVED` masks. Read-modify-write is safer than literal full-register writes when reserved fields must be preserved.
- Address-alignment risk: many address fields start at bit 2, bit 5, or bit 12. Callers must pass aligned GPU addresses and must split low/high address parts according to the mask definitions.
- Status/latch risk: status and violation/fault registers can be sticky or hardware-updated. Polling or clearing logic must follow the relevant hardware semantics; the header does not encode read-clear/write-one-clear behavior.
- Multi-queue risk: `GFX`, `RLC0`, and `RLC1` sections are structurally similar. Copy/paste mistakes between queue families can route values to the wrong queue descriptor or status check.

## Test Signals

- Build signal: AMDGPU/KFD translation units that include SDMA0 4.1 headers compile without undefined register-field symbols and without macro redefinition conflicts.
- Static consistency signal: for every field, `MASK >> SHIFT` should produce a contiguous unshifted field width; full-width value fields should use shift `0` and mask `0xFFFFFFFFL` where expected.
- Header-pair signal: code paths targeting SDMA0 4.1 include the matching offset and mask headers for the same ASIC generation and SDMA instance.
- Runtime initialization signal: SDMA rings enable successfully, write/read pointers advance, IB execution works, and `SDMA0_STATUS_REG__IDLE_MASK` transitions as expected during idle waits.
- KFD queue signal: MQD-created SDMA queues use the RLC/GFX ring-control fields without hangs, and context idle/preemption status bits behave during queue teardown.
- Fault-diagnostic signal: UTCL1 fault/XNACK/status decoding reports coherent VMID, address, vector, page fault/null-page, and FIFO states under induced or observed VM faults.
- Power-management signal: suspend/resume, power gating, clock override, and ULV paths do not leave SDMA frozen, non-idle, or unable to process ring commands.
- Regression signal: compare generated masks/shifts against the authoritative AMD register database or adjacent upstream kernel header for SDMA0 4.1 when updating this file.
