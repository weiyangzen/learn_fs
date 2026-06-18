# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0/sdma0_4_2_2_sh_mask.h lines 1-2559

## Scope

This chunk covers the opening 2,559 lines of the AMDGPU generated SDMA0 4.2.2 shift/mask header. It contains the license/header guard and bitfield definitions for the `sdma0_sdma0dec` address block through the beginning of the `SDMA0_RLC5_*` queue context register set. The file is declarative: it exposes C preprocessor constants used by AMDGPU and AMDKFD code to compose, mask, and decode SDMA MMIO register values. It defines no functions, storage, or executable control flow.

## Purpose

The header maps SDMA0 hardware register fields to two macro forms per field:

- `REGISTER__FIELD__SHIFT`, the bit offset for a field.
- `REGISTER__FIELD_MASK`, the bit mask for extracting or clearing the field.

These constants are consumed by register helper macros such as `REG_SET_FIELD()`, direct shifts, and direct mask operations around `RREG32*()`/`WREG32*()` MMIO accessors. In this chunk, the definitions describe:

- Microcode upload and VM context registers: `SDMA0_UCODE_ADDR`, `SDMA0_UCODE_DATA`, `SDMA0_VM_CNTL`, `SDMA0_VM_CTX_LO/HI`, `SDMA0_VM_CTX_CNTL`.
- SR-IOV/virtualization state: `SDMA0_ACTIVE_FCN_ID`, `SDMA0_VIRT_RESET_REQ`, `SDMA0_VF_ENABLE`, and GPU IOV violation logs.
- Context/public register type bitmaps: `SDMA0_CONTEXT_REG_TYPE0..3` and `SDMA0_PUB_REG_TYPE0..3`, which classify which register slots belong to save/restore or access groups.
- Global SDMA controls: MMHUB unit ID, power/clock controls, main `SDMA0_CNTL`, chicken bits, GB address config, read burst, F32 control, freeze/preemption, phase quantum, power-gating FSM, EDC/ECC, atomics, performance counters, credit control, ULV status, and dummy registers.
- UTCL1/MMU-facing controls and diagnostics: watermarks, read/write FIFO status, invalidation, XNACK address/VMID logging, timeout, and page policy fields.
- Queue-context register templates for `GFX`, `PAGE`, and `RLC0` through the start of `RLC5`: ring buffer, indirect buffer, write pointer polling, doorbells, context status, watermarks, context save area addresses, preemption, AQL, minor pointer update, and mid-command save/restore registers.

## Important Definitions

The most important public interface is the macro namespace itself. Consumers combine these constants with register offsets from companion offset headers, for example `mmSDMA0_GFX_RB_CNTL`, `mmSDMA0_PAGE_RB_CNTL`, `mmSDMA0_RLC0_RB_CNTL`, and `regSDMA0_UTCL1_*`.

Notable groups in this chunk:

- `SDMA0_CNTL` defines operational toggles: trap enable, UTCL1 enable, semaphore interrupt enable, byte-swap controls, mid-command preemption/world-switch, automatic context switching, context-empty/frozen/IB-preempt interrupts.
- `SDMA0_STATUS_REG`, `SDMA0_STATUS1_REG`, `SDMA0_STATUS2_REG`, and `SDMA0_STATUS3_REG` expose engine, ring, indirect-buffer, copy-engine, memory-client, semaphore, interrupt, exception, and command-op status bits.
- `SDMA0_PHASE0_QUANTUM`, `SDMA0_PHASE1_QUANTUM`, and `SDMA0_PHASE2_QUANTUM` provide `UNIT`, `VALUE`, and `PREFER` fields used to program SDMA context-switch scheduling quantum.
- `SDMA0_UTCL1_*` definitions cover page-fault/XNACK handling and cache/page policy: `REDO_ENABLE`, `REDO_DELAY`, request watermarks, FIFO empty/full bits, `PAGE_FAULT`, `PAGE_NULL`, invalidation VMID vectors, read/write XNACK address/VMID/vector logs, and XNACK timeout limits.
- `SDMA0_GFX_*` and `SDMA0_PAGE_*` define the two ordinary SDMA queues. Each has RB enable/size/swap/VMID fields, RB base and read/write pointers, IB enable/base/size/offset fields, doorbell enable/offset/log fields, context status, CSA addresses, AQL controls, and mid-command data/control registers.
- `SDMA0_RLC0_*` through `SDMA0_RLC5_*` are compute/HWS queue-context variants with the same field shape as `GFX`/`PAGE`. The chunk fully covers `RLC0` through `RLC4` and reaches `RLC5_CSA_ADDR_LO` at line 2558; remaining `RLC5` fields continue after this chunk.

## Control Flow

There is no runtime control flow in this header. Runtime behavior appears in consumers:

- SDMA initialization reads a register, updates one field with `REG_SET_FIELD(value, SDMA0_GFX_RB_CNTL, RB_ENABLE, ...)`, and writes it back to enable or disable the GFX ring and IB.
- Page queue stop/start code uses the matching `SDMA0_PAGE_RB_CNTL` and `SDMA0_PAGE_IB_CNTL` fields.
- Context-switch setup computes a phase quantum using `SDMA0_PHASE0_QUANTUM__VALUE_MASK`, `VALUE__SHIFT`, `UNIT_MASK`, and `UNIT__SHIFT`, then writes the same encoded value to phase 0/1/2 registers.
- AMDKFD SDMA queue load/destroy paths disable an `RLC0` queue, poll `SDMA0_RLC0_CONTEXT_STATUS__IDLE_MASK`, program doorbell, read/write pointers, base addresses, writeback addresses, and then re-enable `SDMA0_RLC0_RB_CNTL__RB_ENABLE`.

Thus the actual sequencing is owned by SDMA IP block drivers and KFD queue-management code; this header supplies the bit encodings those sequences depend on.

## State and Persistence

The macros have no state of their own. They describe hardware state held in SDMA MMIO registers and in GPU-visible queue structures:

- RB/IB base, read pointer, write pointer, writeback address, CSA address, and doorbell offset fields persist in hardware until rewritten or reset.
- `CONTEXT_STATUS`, `STATUS*`, UTCL1 FIFO, XNACK, error-log, EDC, performance-counter, and IOV violation bits expose live hardware state or latched diagnostic state.
- `MIDCMD_DATA0..8` and `MIDCMD_CNTL` represent hardware save/restore state for preempted or split mid-command execution.
- `PUB_DUMMY_REG*`, `F32_COUNTER`, `PERFCOUNTER*_RESULT`, and EDC counters are read/write or counter-style registers whose values may survive long enough for debugging, accounting, or firmware coordination, but their lifetime is still tied to the SDMA block and reset/power behavior.

The header must match the ASIC register specification exactly; an incorrect mask or shift would persist wrong values in hardware registers rather than in software data structures.

## Dependencies

This chunk depends implicitly on AMDGPU's generated register ecosystem:

- Offset headers provide the register addresses (`mmSDMA0_*` or `regSDMA0_*`); this file only provides bit layouts.
- MMIO helpers (`RREG32`, `WREG32`, `RREG32_SDMA`, `WREG32_SDMA`, `RREG32_SOC15_IP`, `WREG32_SOC15_IP`) perform the actual register access.
- Bitfield helper macros (`REG_SET_FIELD`, and local direct mask/shift expressions) assume the `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` naming convention used here.
- Firmware and hardware contracts define valid field values; this header generally does not encode enumerations or semantic ranges beyond bit width.

The source file is under `drivers/gpu/drm/amd/include/asic_reg/sdma0`, so it is source-tree-aligned with AMD SDMA0 register definitions rather than Ceph filesystem logic despite living inside the `ceph-client` source snapshot.

## Integration Points

Main in-tree integration points include:

- `drivers/gpu/drm/amd/amdgpu/sdma_v4_0.c`, which uses these fields for SDMA 4.x engine enable/disable, ring setup, context-switch quantum, UTCL1 timeout programming, golden register values, and diagnostics.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_*`, especially Arcturus and gfx v8/v10/v10.3 KFD glue, which computes SDMA RLC queue offsets from `mmSDMA0_RLC1_RB_CNTL - mmSDMA0_RLC0_RB_CNTL` and programs the per-queue `RLC0` register template at a per-engine/per-queue offset.
- `drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_*`, which stores queue context register values in MQDs using shifts such as `SDMA0_RLC0_RB_CNTL__RB_SIZE__SHIFT`, `RB_VMID__SHIFT`, and `RPTR_WRITEBACK_TIMER__SHIFT`.
- Debug/dump paths that enumerate contiguous register ranges from `RLC0_RB_CNTL` through doorbell/status/CSA/mid-command blocks and decode state with the masks in this header.
- SR-IOV and virtualization paths that inspect or program VF IDs, virtual reset requests, VF enable, and GPU IOV violation fields.

## Risks

- Because this file is generated hardware ABI surface, hand edits are high risk. A one-bit mismatch can enable the wrong SDMA feature, corrupt RB/IB addresses, break doorbells, or make queue idle polling unreliable.
- Many register templates are intentionally repetitive. Copy/paste or generation errors between `GFX`, `PAGE`, and `RLCn` groups are hard to catch by inspection but can affect only one queue class.
- Address fields have alignment-sensitive low-bit shifts, such as `RB_RPTR_ADDR_LO__ADDR__SHIFT` at bit 2 and IB base low address at bit 5. Callers must preserve the documented alignment; writing unaligned GPU addresses will truncate low bits.
- Some fields are status or write-one/control style rather than ordinary configuration. Misusing masks from this header in read-modify-write paths can accidentally clear latched diagnostics, trigger resets, alter power states, or hide faults.
- The `RLCn` queue offset pattern assumes the offset header lays queues out uniformly. KFD code uses `RLC0` masks for later queues via address offsets; layout drift in future ASICs would need corresponding generated headers and consumer updates.
- This chunk ends in the middle of the `RLC5` context group, so any final per-file analysis must reconcile continuation fields from the next chunk before describing the full `RLC5` register set.

## Test Signals

Useful validation signals for changes around this header are mostly compile-time and hardware/runtime:

- Kernel build coverage for AMDGPU/AMDKFD users verifies that all generated macro names referenced by C files still exist.
- SDMA ring bring-up should show GFX and PAGE queues enabling successfully, with RB/IB pointers advancing and fence/trap packets completing.
- KFD SDMA queue tests should load, dump, destroy, and reload RLC queues without `SDMA RLC not idle` timeouts.
- Suspend/resume and GPU reset tests should preserve or correctly restore ring base, pointer, doorbell, CSA, and mid-command state.
- VM fault/XNACK tests and page-fault stress should exercise `UTCL1_*` status, timeout, invalidation, and XNACK log fields without interrupt storms.
- SR-IOV validation should check VF enable/reset behavior and GPU IOV violation logs.
- Power-management tests should cover SDMA clock/power gating, ULV status, and context-switch quantum programming.
