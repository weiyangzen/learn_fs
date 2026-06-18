# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0/sdma0_4_2_2_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003375`: lines 1-2559, `Docs/researches/chunks/subset-b-003375_research.md`
- `subset-b-003376`: lines 2560-3002, `Docs/researches/chunks/subset-b-003376_research.md`

## Chunk Research

### subset-b-003375: lines 1-2559

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

### subset-b-003376: lines 2560-3002

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0/sdma0_4_2_2_sh_mask.h lines 2560-3002

## Scope

This chunk covers the final 443 lines of the generated AMD SDMA0 4.2.2 shift/mask header. It starts at the `SDMA0_RLC5_CSA_ADDR_LO__ADDR_MASK` line, so the `RLC5_CSA_ADDR_LO` register group begins in the previous chunk. It then completes the tail of the `SDMA0_RLC5_*` queue-context field definitions, defines the full `SDMA0_RLC6_*` and `SDMA0_RLC7_*` RLC queue-context field sets, and closes the header include guard with `#endif`.

The range contains preprocessor constants only: 339 `#define` statements, 169 `__SHIFT` macros, 170 `_MASK` macros, and register-name comments. There are no functions, types, enums, variables, direct MMIO accesses, branches, loops, allocations, locks, or persistence code. The content is declarative register bitfield geometry for SDMA0 RLC queues 5 through 7 on the 4.2.2 SDMA block used by Arcturus-era AMDGPU/KFD code.

Although the repository path is under a `ceph-client` mirror, this header is AMD GPU register metadata. It does not implement Ceph or distributed-filesystem behavior.

## Purpose

`sdma0_4_2_2_sh_mask.h` supplies symbolic bit positions and masks for SDMA0 register fields. Driver code combines these definitions with the companion offset header `sdma0_4_2_2_offset.h` and AMDGPU helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32`, and `WREG32`.

This chunk focuses on high-numbered RLC SDMA queue contexts:

- The tail of `SDMA0_RLC5`, covering context-save-area, indirect-buffer remainder, preemption, write-pointer polling address, AQL, minor pointer update, and mid-command state fields.
- Complete `SDMA0_RLC6` and `SDMA0_RLC7` queue register layouts, including ring buffer controls, ring base/read/write pointers, write-pointer polling, read-pointer writeback, indirect-buffer controls and addresses, context status, doorbell control/log/offset, watermarks, context-save-area addresses, preemption, AQL packet mode, minor pointer updates, and mid-command save/restore state.

The generated macro naming convention is the public interface:

- `SDMA0_RLCn_REGISTER__FIELD__SHIFT` gives the least-significant bit position of a field.
- `SDMA0_RLCn_REGISTER__FIELD_MASK` gives the field mask inside the 32-bit register value.

The macros do not encode register offsets, reset values, read/write permissions, write-one-to-clear behavior, reserved-bit policy, ownership, or programming order. Those semantics come from the matching offset/default headers, calling code, firmware contracts, and ASIC documentation.

## Important Macro Families

### Ring Buffer State

For `RLC6` and `RLC7`, and for the already-started `RLC5` tail where applicable, the queue ring definitions describe the persistent hardware queue pointers and ring configuration:

- `RB_CNTL` fields define `RB_ENABLE`, encoded `RB_SIZE`, byte swap behavior, read-pointer writeback enable/swap/timer, queue privilege, and `RB_VMID`.
- `RB_BASE` and `RB_BASE_HI` hold the ring buffer base address split into low/high words.
- `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, and `RB_WPTR_HI` expose 64-bit read/write pointer offsets split across registers.
- `RB_WPTR_POLL_CNTL` controls hardware write-pointer polling, including enable, swap, F32 polling mode, frequency, and idle poll count.
- `RB_RPTR_ADDR_HI` and `RB_RPTR_ADDR_LO` provide the read-pointer writeback address; the low word also has `RPTR_WB_IDLE`.
- `RB_WPTR_POLL_ADDR_HI` and `RB_WPTR_POLL_ADDR_LO` provide the memory address used when the engine polls a write pointer instead of relying only on doorbells.

The low address fields consistently mask alignment bits: ring pointer writeback and write-pointer-poll low addresses use `ADDR__SHIFT` 2 with `0xFFFFFFFC`, while IB base low fields use `ADDR__SHIFT` 5 with `0xFFFFFFE0`. Queue programming must preserve those alignment expectations.

### Indirect Buffer, Skip, And Context Status

Each full queue block includes:

- `IB_CNTL` fields for `IB_ENABLE`, `IB_SWAP_ENABLE`, `SWITCH_INSIDE_IB`, and `CMD_VMID`.
- `IB_RPTR` and `IB_OFFSET` fields with offset shift 2 and mask `0x003FFFFC`.
- `IB_BASE_LO`, `IB_BASE_HI`, and `IB_SIZE` fields for the active indirect-buffer address and size.
- `SKIP_CNTL__SKIP_COUNT` for skipped command accounting.
- `IB_SUB_REMAIN__SIZE` for the remaining sub-IB size.

The `CONTEXT_STATUS` fields expose scheduler-visible queue state: `SELECTED`, `IDLE`, `EXPIRED`, `EXCEPTION`, `CTXSW_ABLE`, `CTXSW_READY`, `PREEMPTED`, and `PREEMPT_DISABLE`. KFD queue load and destroy paths use the equivalent `RLC0` idle mask after disabling a queue and waiting for the hardware context to drain; because Arcturus computes queue windows by stride, the same register layout applies to `RLC5`, `RLC6`, and `RLC7`.

### Doorbells, Watermarks, CSA, And Preemption

Doorbell and context-management fields include:

- `DOORBELL__ENABLE` at bit 28 and `DOORBELL__CAPTURED` at bit 30.
- `DOORBELL_OFFSET__OFFSET` shifted by 2 with mask `0x0FFFFFFC`.
- `DOORBELL_LOG__BE_ERROR` plus the captured doorbell `DATA` field.
- `STATUS__WPTR_UPDATE_FAIL_COUNT` and `STATUS__WPTR_UPDATE_PENDING`.
- `WATERMARK__RD_OUTSTANDING` and `WATERMARK__WR_OUTSTANDING` for read/write outstanding request limits or status.
- `CSA_ADDR_LO` and `CSA_ADDR_HI` for context-save-area address state.
- `PREEMPT__IB_PREEMPT` for requesting or reflecting indirect-buffer preemption.

These fields are liveness-sensitive: queue wakeup, idle detection, preemption, and context save/restore all rely on the doorbell, status, CSA, and preempt bit positions matching the hardware layout.

### AQL, Minor Pointer Update, And Mid-Command State

The AQL and mid-command field families are repeated for `RLC5`, `RLC6`, and `RLC7`:

- `RB_AQL_CNTL` has `AQL_ENABLE`, `AQL_PACKET_SIZE`, and `PACKET_STEP`.
- `MINOR_PTR_UPDATE__ENABLE` gates minor pointer update behavior.
- `MIDCMD_DATA0` through `MIDCMD_DATA8` are full-width data payload registers.
- `MIDCMD_CNTL` has `DATA_VALID`, `COPY_MODE`, `SPLIT_STATE`, and `ALLOW_PREEMPT`.

These macros support mid-command preemption and restore flows. The header only names the saved-data registers and control bits; correctness depends on firmware/driver code preserving the right payload and respecting hardware-defined valid/copy/split-state semantics.

## Control Flow

This header has no local runtime control flow. Runtime control flow is in consumers that include it. The relevant in-tree consumer is `amdgpu_amdkfd_arcturus.c`, which includes `sdma0/sdma0_4_2_2_offset.h` and this shift/mask header, plus equivalent headers for SDMA1 through SDMA7.

The Arcturus KFD SDMA flow is:

1. Compute an SDMA engine base from `SOC15_REG_OFFSET(SDMAx, 0, mmSDMAx_RLC0_RB_CNTL)`.
2. Compute the selected queue register window with `queue_id * (mmSDMA0_RLC1_RB_CNTL - mmSDMA0_RLC0_RB_CNTL)`.
3. Disable `RB_ENABLE`, poll `CONTEXT_STATUS.IDLE`, and time out if the queue does not drain.
4. Program doorbell offset/enable, read/write pointers, minor pointer update, ring base, and read-pointer writeback address.
5. Re-enable `RB_ENABLE`.
6. Dump or destroy queues by reading the same repeated register ranges and preserving/restoring MQD pointer state.

Although the code typically references `RLC0` offsets and masks, queue selection is by computed stride. The `RLC5`, `RLC6`, and `RLC7` definitions in this chunk document the same per-queue hardware schema for the high queue windows and must stay consistent with the generated offsets.

## State And Persistence Behavior

The file itself owns no software state and persists nothing. It names hardware-visible state for live SDMA0 RLC queue contexts. That state persists only according to the SDMA hardware reset and power domains and is reinitialized by driver, firmware, or KFD queue-management paths after queue creation, teardown, GPU reset, suspend/resume, power-gating loss, or SR-IOV/PF intervention.

Represented queue state includes:

- Ring configuration and pointers: enable, size, VMID, privilege, base address, read pointer, write pointer, read-pointer writeback address, write-pointer polling address, polling cadence, and swap mode.
- IB execution state: enable, base, size, read pointer, offset, command VMID, skip count, sub-IB remaining size, and switch-inside-IB behavior.
- Scheduler and recovery state: selected/idle/expired/exception/context-switch/preempted bits, preempt disable, `IB_PREEMPT`, and mid-command valid/split/preempt control state.
- Doorbell state: enable, captured state, offset, log data, backend error reporting, write-pointer update pending/fail counts.
- Context and AQL state: CSA address, AQL enable/packet sizing/step, minor pointer update enable, and full-width mid-command data words.

Callers must not infer write permissions or clear semantics from masks alone. Status fields may be sticky, W1C, read-only, or firmware-owned depending on the register and mode; this generated header does not carry that metadata.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor, but semantic correctness depends on synchronized generated register data:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0/sdma0_4_2_2_offset.h` supplies the matching `mmSDMA0_RLC5_*`, `mmSDMA0_RLC6_*`, and `mmSDMA0_RLC7_*` offsets. The chunk aligns with offset windows `RLC5` at `0x02e8..0x0331`, `RLC6` at `0x0340..0x0389`, and `RLC7` at `0x0398..0x03e1`.
- Equivalent generated headers for `sdma1` through `sdma7` provide the same per-engine schema for Arcturus' multiple SDMA engines.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_arcturus.c` includes this header and uses the shared RLC queue layout to load, dump, query, and destroy KFD SDMA queues through MMIO.
- KFD MQD structures such as `struct v9_sdma_mqd` carry fields that are written into these queue registers: ring control/base/pointers, doorbell offset, read-pointer writeback address, dummy register state, and related queue context values.
- Doorbell allocation/range code in KFD and NBIO determines which doorbell offsets are valid for user queues; the `DOORBELL_OFFSET` and `DOORBELL` masks here are the SDMA-side queue endpoint of that integration.

The final per-file analysis should treat this file as one member of the Arcturus SDMA0 register-header set, not as a standalone driver module.

## Risks And Edge Cases

- The chunk starts with a boundary fragment: only `SDMA0_RLC5_CSA_ADDR_LO__ADDR_MASK` is present for that register in this slice. The matching comment and shift definition are in the previous chunk, so merge-time checks must not report that as a local generation error.
- A single wrong shift or mask can compile cleanly but program the wrong hardware field. This is most dangerous for `RB_ENABLE`, `RB_VMID`, `RB_SIZE`, doorbell offset/enable, pointer writeback addresses, and preemption/mid-command controls.
- Queue blocks are highly repetitive. Copy or generator drift between `RLC5`, `RLC6`, `RLC7`, and lower queue windows can create queue-id-specific failures that only appear when high-numbered SDMA queues are allocated.
- Address masks encode alignment. Misusing unshifted byte addresses for `RB_RPTR_ADDR_LO`, `RB_WPTR_POLL_ADDR_LO`, `CSA_ADDR_LO`, or `IB_BASE_LO` can point hardware at the wrong memory.
- Doorbell offset mistakes can alias queues or prevent wakeups. A bad `DOORBELL_OFFSET` field can make user submissions invisible or route writes to another queue's doorbell.
- Context-status and preemption fields are recovery-sensitive. Incorrect `IDLE`, `PREEMPTED`, `PREEMPT_DISABLE`, `IB_PREEMPT`, `MIDCMD_CNTL`, or `MIDCMD_DATA*` definitions can break queue destroy, timeout handling, or mid-command restore.
- Status and log registers may have side effects not represented here. Generic read-modify-write against status/log bits can lose diagnostics or clear hardware state unintentionally if the caller ignores the hardware access rules.
- Firmware, PSP, PF, or reset code may own some queue state in specific modes. KFD queue programming must respect ownership, reset sequencing, and SR-IOV constraints outside this header.

## Test Signals

Useful validation is mostly generated-data and hardware-integration oriented:

- Preprocess or build AMDGPU/KFD code paths that include `sdma0_4_2_2_offset.h` and `sdma0_4_2_2_sh_mask.h`, especially `amdgpu_amdkfd_arcturus.c`.
- Static generation checks that every complete register group in this chunk has matching `__SHIFT` and `_MASK` definitions, with an explicit boundary exception for `SDMA0_RLC5_CSA_ADDR_LO`.
- Cross-check every `SDMA0_RLC5_*`, `SDMA0_RLC6_*`, and `SDMA0_RLC7_*` field group against `sdma0_4_2_2_offset.h` for a matching `mmSDMA0_RLCn_*` offset and base index.
- Compare the repeated RLC queue blocks against lower-numbered `RLC0` through `RLC4` and against the sibling SDMA engine headers, allowing only intentional instance and queue-number prefixes.
- Runtime KFD SDMA tests on Arcturus-class hardware: queue create/load, ring submission, doorbell wakeup, read-pointer writeback, write-pointer polling, queue idle detection, and queue destroy for high queue IDs.
- Stress tests for multiple SDMA engines and high-numbered queues to catch stride or queue-window mistakes.
- Reset, suspend/resume, GPU recovery, and preemption tests that verify ring pointers, CSA addresses, doorbell state, context status, and mid-command data are restored or cleared correctly.
- Diagnostic dump tests using `kgd_arcturus_hqd_sdma_dump` to confirm that the dumped register ranges remain aligned with the generated RLC window layout.

## Chunk Notes For Merge

This document intentionally covers only lines 2560-3002 of `sdma0_4_2_2_sh_mask.h`. Earlier chunks must cover the start of `SDMA0_RLC5_CSA_ADDR_LO` and the rest of SDMA0 global/lower-queue definitions. This is the final chunk of the file and includes the closing include guard. The merged per-file report should describe the whole header as generated SDMA0 4.2.2 bitfield metadata consumed by Arcturus AMDGPU/KFD SDMA queue-management paths.
