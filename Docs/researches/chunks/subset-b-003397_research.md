# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma5/sdma5_4_2_2_sh_mask.h lines 2570-2956

## Scope

This chunk is the tail of the generated AMD SDMA5 4.2.2 shift/mask header. It starts at the complete `SDMA5_RLC5_MIDCMD_CNTL` field definitions, then covers the complete bitfield layout for SDMA5 RLC queue contexts 6 and 7, and ends with the closing include guard.

The file is C preprocessor register metadata only. It defines `*_SHIFT` and `*_MASK` constants for hardware register fields; it contains no functions, structs, enums, allocation, locking, branches, loops, MMIO access, or local persistence. The effective users are AMDGPU register helpers and queue-management code that combine these masks with the matching SDMA5 4.2.2 offset header.

Although this repository path is under a `ceph-client` source mirror, this chunk documents AMD GPU SDMA hardware registers. It does not implement distributed filesystem behavior.

## Purpose

`sdma5_4_2_2_sh_mask.h` supplies symbolic bit positions and masks for the SDMA engine 5 register block in the 4.2.2 IP revision. Its companion `sdma5_4_2_2_offset.h` supplies the concrete MMIO register addresses. Together they let driver code write readable register programming expressions instead of open-coded bit constants.

The covered range describes high RLC queue-context registers:

- `SDMA5_RLC5_MIDCMD_CNTL` defines control bits for a mid-command snapshot: `DATA_VALID`, `COPY_MODE`, `SPLIT_STATE`, and `ALLOW_PREEMPT`.
- `SDMA5_RLC6_*` defines the complete RLC6 context field layout.
- `SDMA5_RLC7_*` defines the complete RLC7 context field layout.

RLC6 and RLC7 are structurally identical in this chunk. They expose ring-buffer setup, read/write pointer state, pointer polling/writeback, indirect-buffer execution, context status, doorbell routing, live queue status, outstanding-operation watermarks, context-save-area addresses, preemption control, AQL packet controls, minor pointer update, and mid-command snapshot registers.

## Important Macro Families

The exported names follow the generated AMD register convention `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`.

- `SDMA5_RLC[6|7]_RB_CNTL__*` defines ring-buffer control fields: `RB_ENABLE`, `RB_SIZE`, `RB_SWAP_ENABLE`, `RPTR_WRITEBACK_ENABLE`, `RPTR_WRITEBACK_SWAP_ENABLE`, `RPTR_WRITEBACK_TIMER`, `RB_PRIV`, and `RB_VMID`.
- `RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, and `RB_WPTR_HI` describe the ring base address and producer/consumer pointer fields. Most are full 32-bit fields; `RB_BASE_HI` is masked to 24 bits.
- `RB_WPTR_POLL_CNTL` defines write-pointer polling behavior: enable, swap, 32-bit polling mode, polling frequency, and idle poll count.
- `RB_RPTR_ADDR_HI/LO` and `RB_WPTR_POLL_ADDR_HI/LO` define memory addresses used for read-pointer writeback and write-pointer polling. Low address fields are 4-byte aligned with `ADDR__SHIFT = 0x2` and `ADDR_MASK = 0xFFFFFFFC`; `RB_RPTR_ADDR_LO` also exposes `RPTR_WB_IDLE`.
- `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO`, `IB_BASE_HI`, `IB_SIZE`, and `IB_SUB_REMAIN` describe indirect-buffer enablement, addressing, progress, and remaining size.
- `CONTEXT_STATUS` exposes scheduler/context-switch state: selected, idle, expired, exception bits, context-switch ability/readiness, preempted, and preempt-disable.
- `DOORBELL`, `DOORBELL_LOG`, and `DOORBELL_OFFSET` describe doorbell enable/capture state, logged doorbell data or bus-error state, and the aligned doorbell offset.
- `STATUS` reports write-pointer update failure count and pending update state.
- `WATERMARK` packs read and write outstanding-operation watermark fields.
- `CSA_ADDR_LO/HI` defines the context-save-area address used by queue save/restore and preemption flows.
- `PREEMPT` exposes the `IB_PREEMPT` command bit.
- `RB_AQL_CNTL` defines AQL queue enablement, packet size, and packet step fields.
- `MINOR_PTR_UPDATE` gates minor pointer update behavior while queue pointers are being written.
- `MIDCMD_DATA0` through `MIDCMD_DATA8` are full 32-bit mid-command snapshot words. `MIDCMD_CNTL` marks those words valid and describes copy mode, split state, and preemption allowance.

There are no callable APIs or C types in this chunk. The macros themselves are the public interface.

## Control Flow and Data Flow

This header has no runtime control flow. The effective flow happens in AMDGPU consumers:

1. Driver code selects an SDMA5 RLC register address from `sdma5_4_2_2_offset.h`, for example `mmSDMA5_RLC6_RB_CNTL`, `mmSDMA5_RLC6_RB_WPTR_POLL_CNTL`, `mmSDMA5_RLC7_CONTEXT_STATUS`, or `mmSDMA5_RLC7_MIDCMD_CNTL`.
2. Code reads or writes the register through SOC15/AMDGPU MMIO helpers.
3. Helpers such as `REG_SET_FIELD()` or direct bit tests use this header's `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants to compose or decode fields.
4. Hardware interprets the final register value as queue state for ring execution, memory-backed pointer writeback/polling, doorbell notification, indirect-buffer dispatch, context switching, preemption, AQL processing, or mid-command resume.

The `amdgpu/amdgpu_amdkfd_arcturus.c` integration includes `sdma5/sdma5_4_2_2_offset.h` and this mask header as part of the Arcturus eight-SDMA-engine register set. Its SDMA MQD load/dump/destroy helpers calculate an engine-specific RLC register base from `engine_id`, then program queue registers by adding an RLC queue stride. That code often uses the SDMA0 RLC0 names as canonical field geometry, relying on identical layouts across SDMA engines and RLC queue instances; this SDMA5 header supplies the engine-specific names needed when code or tooling references SDMA5 directly.

`amdgpu/sdma_v4_0.c` also includes the SDMA5 4.2.2 offset and mask headers. Its golden-register settings show the relevant hardware behavior for high RLC contexts by initializing the analogous RLC6/RLC7 read-pointer writeback low-address and write-pointer polling-control registers on SDMA instances. Those settings are a strong integration signal for the `RB_RPTR_ADDR_LO` and `RB_WPTR_POLL_CNTL` field layouts described here.

## State and Persistence Behavior

The header stores no software state and persists nothing to disk. It describes hardware register state whose lifetime is controlled by SDMA reset, power management, firmware, and queue scheduling rules.

- Ring configuration persists enablement, ring size, base address, read/write pointers, byte-swap mode, read-pointer writeback policy, privilege, and VMID until the queue is reprogrammed or reset.
- Pointer polling and writeback state persists the memory addresses and polling policy that let hardware observe producer updates and publish consumer progress.
- Doorbell state persists enablement, selected doorbell offset, captured-doorbell indication, and logged doorbell data or bus-error status.
- Indirect-buffer fields track the current IB base, size, read pointer, current offset, and remaining sub-IB bytes while work executes.
- Context status, queue status, watermarks, and doorbell logs are live hardware-observed state. They can change while the SDMA engine is running.
- CSA and mid-command fields persist context-save and partially executed command data used by preemption and context-switch machinery.
- AQL fields persist whether the RLC queue consumes AQL packets and how packet size/step are interpreted.
- `MINOR_PTR_UPDATE` and `PREEMPT` are control fields used during pointer update and preemption sequences rather than durable software state.

The mask header does not encode reset values, access permissions, volatile/sticky behavior, write-one-to-clear semantics, or required sequencing. Those rules must come from the hardware specification and driver programming sequences.

## Dependencies and Integration Points

Direct dependencies and integration points are:

- The matching offset header `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma5/sdma5_4_2_2_offset.h`. In that file, RLC6 starts at `mmSDMA5_RLC6_RB_CNTL = 0x0340`, the RLC6 mid-command block ends at `mmSDMA5_RLC6_MIDCMD_CNTL = 0x0389`, RLC7 starts at `mmSDMA5_RLC7_RB_CNTL = 0x0398`, and the RLC7 mid-command block ends at `mmSDMA5_RLC7_MIDCMD_CNTL = 0x03e1`.
- AMDGPU register helper conventions, especially `REG_SET_FIELD()` and bit tests against `*_MASK` constants.
- SOC15 register addressing and MMIO helpers used by AMDGPU SDMA and KFD paths.
- `amdgpu/amdgpu_amdkfd_arcturus.c`, which includes all SDMA0 through SDMA7 4.2.2 generated headers and computes per-engine/per-queue RLC register offsets for SDMA MQD load, dump, occupancy, and destroy operations.
- `amdgpu/sdma_v4_0.c`, which includes the SDMA5 4.2.2 headers and contains golden-setting tables for SDMA RLC pointer writeback and write-pointer polling behavior.
- The KFD MQD representation `struct v9_sdma_mqd`, whose saved queue fields correspond to RLC register values such as `RB_CNTL`, `DOORBELL`, `RB_RPTR`, `RB_WPTR`, `RB_BASE`, and read-pointer writeback addresses.

The registers described here integrate with SDMA queue creation/destruction, HSA/KFD queue scheduling, GPUVM VMID selection, doorbell routing, memory-backed pointer synchronization, indirect-buffer execution, context save/restore, preemption, register dumping, diagnostics, and ASIC bring-up validation.

## Risks and Edge Cases

- The chunk begins at RLC5 mid-command control, after the RLC5 mid-command data words defined in the previous chunk. Whole-file reconciliation should merge this boundary before making complete RLC5 claims.
- These are untyped integer macros. A wrong mask or shift compiles cleanly but can program the wrong hardware bits.
- RLC6 and RLC7 are nearly identical. Generator or copy/paste mistakes are easy to miss, and using the wrong queue index can silently target a different hardware queue.
- Masks must be paired with the matching SDMA5 4.2.2 offsets. Mixing masks from another SDMA engine or IP revision is unsafe even when names look similar.
- Split address fields require correct low/high construction and alignment. Low address fields with `ADDR__SHIFT = 0x2` must not receive unaligned addresses.
- `RB_CNTL__RB_VMID` and `RB_CNTL__RB_PRIV` affect address translation and privilege. Incorrect values can produce GPUVM faults or run work in the wrong address space.
- Doorbell and pointer-poll/writeback fields connect hardware to memory and doorbell apertures. Bad values can make SDMA fetch stale work, write progress into the wrong memory, or wake the wrong queue.
- Live status fields such as `CONTEXT_STATUS`, `STATUS`, `DOORBELL_LOG`, `WATERMARK`, `IB_SUB_REMAIN`, and `MIDCMD_*` should not be treated as stable unless the queue is idle or the caller follows the required polling sequence.
- Preemption and mid-command state are scheduler-sensitive. Writing `PREEMPT`, `CSA_ADDR_*`, or `MIDCMD_*` outside the expected save/restore flow can corrupt resume state or leave queues stalled.
- The header does not describe reset/default values. Tests that infer defaults from masks alone are incomplete.

## Test and Validation Signals

Useful validation is mostly compile-time, generator, and hardware-integration coverage:

- Build AMDGPU paths that include `sdma5/sdma5_4_2_2_sh_mask.h` with the matching offset header; renamed or missing generated macros should fail compilation.
- Static generation checks should confirm every RLC6/RLC7 register field has a matching `_SHIFT` and `_MASK` pair, full-width fields use `0xFFFFFFFFL`, and aligned low-address fields preserve the expected low-bit masks.
- Cross-check the packed fields against the authoritative SDMA5 4.2.2 register database, especially `RB_CNTL`, `RB_WPTR_POLL_CNTL`, `CONTEXT_STATUS`, `DOORBELL`, `STATUS`, `DOORBELL_LOG`, `WATERMARK`, `RB_AQL_CNTL`, and `MIDCMD_CNTL`.
- Validate the companion offset header contains all RLC6/RLC7 register names covered here and that the RLC queue stride matches the driver logic in `get_sdma_rlc_reg_offset()`.
- Boot/probe on matching Arcturus-class hardware should apply SDMA RLC golden settings and initialize pointer writeback/polling registers without hangs or MMIO faults.
- KFD SDMA queue tests should verify MQD load/destroy behavior for high RLC queue IDs, including `RB_ENABLE`, `CONTEXT_STATUS__IDLE`, doorbell enable/offset, read-pointer writeback, write-pointer polling, and saved read-pointer state.
- Queue submission tests should observe ring pointer movement, read-pointer writeback updates, and doorbell-triggered progress on SDMA5 queues if those queues are exposed by the ASIC configuration.
- Preemption and context-switch tests should exercise `PREEMPT`, `CSA_ADDR_*`, `IB_SUB_REMAIN`, `CONTEXT_STATUS`, and `MIDCMD_*` state before and after forced SDMA IB preemption.
- Register dump and decoder tooling should use these masks to decode live RLC6/RLC7 values and compare them against expected queue configuration, VMID, privilege, AQL mode, doorbell offset, and idle/preempt status.

## Chunk Boundary Notes

This is the final chunk of `sdma5_4_2_2_sh_mask.h`. Merge/reconciliation should join the opening RLC5 `MIDCMD_CNTL` lines with the prior RLC5 block, then treat RLC6 and RLC7 as complete high-RLC queue-context field blocks and preserve the closing include-guard note.
