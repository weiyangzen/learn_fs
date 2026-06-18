# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma4/sdma4_4_2_2_sh_mask.h lines 2570-2956

## Scope

This chunk is the final section of the generated AMD SDMA4 4.2.2 shift/mask header. It starts at `SDMA4_RLC5_MIDCMD_CNTL`, then defines the complete bitfield layout for SDMA4 RLC queue contexts 6 and 7, and ends with the closing include guard.

The file is C preprocessor metadata only. It contains no functions, structs, enums, allocation, locking, branches, loops, MMIO calls, or direct runtime control flow. Its exported surface is a dense namespace of `*_SHIFT` and `*_MASK` macros that AMDGPU code combines with matching offset headers and register helpers.

Although the repository path is under a `ceph-client` source mirror, this chunk documents AMD GPU SDMA hardware registers. It does not implement distributed filesystem behavior.

## Purpose

`sdma4_4_2_2_sh_mask.h` supplies symbolic bit positions and masks for fields inside SDMA4 4.2.2 registers. It is paired with `sdma4_4_2_2_offset.h`, which provides the register addresses. Consumers use the address macros plus these field macros through helpers such as `REG_SET_FIELD()`, `REG_GET_FIELD()`, `SOC15_REG_OFFSET()`, `RREG32()`, and `WREG32()`.

The covered range describes high RLC queue-context registers for SDMA engine 4:

- `SDMA4_RLC5_MIDCMD_CNTL` appears at the chunk boundary and exposes the mid-command control bits `DATA_VALID`, `COPY_MODE`, `SPLIT_STATE`, and `ALLOW_PREEMPT`.
- `SDMA4_RLC6_*` defines the full RLC6 queue-context bit layout.
- `SDMA4_RLC7_*` defines the full RLC7 queue-context bit layout.

RLC6 and RLC7 are structurally identical in this header. They describe ring-buffer configuration, read/write pointer registers, write-pointer polling, read-pointer writeback, indirect-buffer state, context status, doorbell state, queue status, watermarks, context-save addresses, preemption, AQL mode, minor-pointer update, and mid-command snapshot/control fields.

## Important Macro Families

The exported macros follow the generated `SDMA4_RLC[6|7]_<REGISTER>__<FIELD>_{SHIFT,MASK}` convention:

- `RB_CNTL` defines queue enablement and identity fields: `RB_ENABLE`, `RB_SIZE`, `RB_SWAP_ENABLE`, `RPTR_WRITEBACK_ENABLE`, `RPTR_WRITEBACK_SWAP_ENABLE`, `RPTR_WRITEBACK_TIMER`, `RB_PRIV`, and `RB_VMID`.
- `RB_BASE` and `RB_BASE_HI` describe the split ring-buffer base address. The low word is full width and the high word is masked to `0x00FFFFFF`.
- `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, and `RB_WPTR_HI` describe 64-bit read/write pointer offsets split across low/high registers.
- `RB_WPTR_POLL_CNTL` controls hardware polling of a memory-backed write pointer through `ENABLE`, `SWAP_ENABLE`, `F32_POLL_ENABLE`, `FREQUENCY`, and `IDLE_POLL_COUNT`.
- `RB_RPTR_ADDR_HI/LO` describes the memory location used for read-pointer writeback. The low register has `RPTR_WB_IDLE` at bit 0 and a 4-byte-aligned `ADDR` field at bits 31:2.
- `RB_WPTR_POLL_ADDR_HI/LO` describes the memory location hardware polls for write-pointer updates, with the low address field also aligned to bits 31:2.
- `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO`, `IB_BASE_HI`, `IB_SIZE`, and `IB_SUB_REMAIN` describe indirect-buffer enablement, address, progress, size, and remaining sub-IB state.
- `CONTEXT_STATUS` exposes scheduler/context-switch state: `SELECTED`, `IDLE`, `EXPIRED`, packed `EXCEPTION`, `CTXSW_ABLE`, `CTXSW_READY`, `PREEMPTED`, and `PREEMPT_DISABLE`.
- `DOORBELL`, `DOORBELL_LOG`, and `DOORBELL_OFFSET` describe doorbell enable/captured state, logged data or bus-error state, and the aligned doorbell aperture offset.
- `STATUS` reports write-pointer update failure count and whether a write-pointer update is pending.
- `WATERMARK` packs read and write outstanding-watermark fields.
- `CSA_ADDR_LO/HI` describes the context-save area address used by context-switch/preemption machinery.
- `PREEMPT` exposes the `IB_PREEMPT` control bit.
- `DUMMY_REG` is a full-width scratch or placeholder register field.
- `RB_AQL_CNTL` defines AQL queue enablement, packet size, and packet step fields.
- `MINOR_PTR_UPDATE` exposes an `ENABLE` bit used around pointer update sequencing.
- `MIDCMD_DATA0` through `MIDCMD_DATA8` are full 32-bit mid-command snapshot data words, and `MIDCMD_CNTL` marks validity, copy mode, split state, and preemption allowance.

There are no callable APIs or C types in this chunk. The macros themselves are the interface.

## Control Flow and Data Flow

The header has no local runtime control flow. The effective data flow happens when AMDGPU and AMDKFD code program SDMA queue registers:

1. Driver code chooses an SDMA RLC register address from `sdma4_4_2_2_offset.h`, for example `mmSDMA4_RLC6_RB_CNTL` or `mmSDMA4_RLC7_RB_WPTR_POLL_CNTL`.
2. Code composes or decodes register values with the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros from this header.
3. SOC15/MMIO helpers read or write the selected register.
4. Hardware interprets the fields as queue state for ring execution, pointer polling/writeback, doorbell notification, indirect-buffer execution, context switching, preemption, AQL packet handling, and mid-command resume.

Two integration paths include this exact SDMA4 4.2.2 header pair:

- `amdgpu/sdma_v4_0.c` includes `sdma4/sdma4_4_2_2_offset.h` and `sdma4/sdma4_4_2_2_sh_mask.h` along with the other SDMA engines. Its golden-setting tables program related RLC fields such as `RB_RPTR_ADDR_LO` and `RB_WPTR_POLL_CNTL` for RLC queues on SDMA engines.
- `amdgpu/amdgpu_amdkfd_arcturus.c` includes the same header pair and computes an RLC register base from `engine_id` and `queue_id`. The KFD path uses the RLC register stride to load, dump, and destroy SDMA HQD/MQD state; RLC6 and RLC7 are reached by the same queue-indexed address math even though many field helper calls use the RLC0 macro names because the per-queue bit layouts are intentionally repeated.

## State and Persistence Behavior

This header stores no software state and persists nothing to disk. It describes hardware-owned register state:

- Ring-buffer state persists enablement, size, base address, read/write pointers, byte-swap behavior, read-pointer writeback policy, privilege, and VMID until the SDMA context is reset or reprogrammed.
- Polling state persists whether the engine polls a write-pointer memory address, how it swaps data, how often it polls, and how it behaves while idle.
- Doorbell state persists enablement, doorbell offset, captured-doorbell indication, and logged doorbell data or bus-error status.
- Indirect-buffer state persists IB enablement, base address, size, current read pointer, current offset, command VMID, and remaining sub-IB size while work executes.
- Context status, queue status, and watermarks are live hardware state reflecting selection, idleness, expiration, exception conditions, context-switch readiness, preemption state, pointer-update activity, and outstanding read/write pressure.
- Context-save and mid-command registers hold preemption/context-switch resume state, including context-save area address and mid-command snapshot words.
- AQL state persists whether AQL mode is active and how AQL packets are sized and stepped.
- `MINOR_PTR_UPDATE` is a transient sequencing control used when updating pointer fields.

The header does not encode reset values, access permissions, sticky-bit behavior, write-one-to-clear semantics, ordering requirements, or firmware ownership rules. Those constraints come from the hardware register database and the driver sequences that use these masks.

## Dependencies and Integration Points

Direct dependencies and integration contracts include:

- The matching offset header `sdma4_4_2_2_offset.h`. In that file, RLC6 starts at `mmSDMA4_RLC6_RB_CNTL = 0x0340` and RLC7 starts at `mmSDMA4_RLC7_RB_CNTL = 0x0398`, both with base index 1.
- Generated AMD register naming conventions. Helpers such as `REG_SET_FIELD(value, SDMA4_RLC6_RB_CNTL, RB_ENABLE, 1)` depend on exact `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` names.
- SOC15 register access and offset calculation through `SOC15_REG_OFFSET()`, `RREG32()`, `WREG32()`, and SDMA-specific wrappers in `sdma_v4_0.c`.
- AMDKFD Arcturus SDMA queue management. `get_sdma_rlc_reg_offset()` computes engine and queue offsets, and queue load/dump/destroy paths touch the same categories of RLC registers covered here.
- Memory-backed queue data: ring base, read/write pointers, read-pointer writeback address, write-pointer poll address, context-save area, and doorbell offset all connect these bitfields to GPU-visible memory and doorbell apertures.
- Firmware and scheduler behavior: context status, preemption, CSA, IB, and mid-command fields are meaningful only within SDMA firmware/hardware context-switch rules.

The same high-level field layout appears in adjacent engine headers (`sdma0` through `sdma7`) and newer multi-instance `sdma_4_4_0` headers, but names and offset namespaces differ. The 4.2.2 header uses `mmSDMA4_*` offsets in the engine-specific directory; later multi-instance headers use `regSDMA4_*` forms.

## Risks and Edge Cases

- This chunk begins at the RLC5 mid-command control register. Whole-file reconciliation should merge the RLC5 discussion with the preceding chunk before treating RLC5 as complete.
- The macros are untyped integer constants. A wrong mask or shift compiles cleanly but can program the wrong hardware bits.
- RLC6 and RLC7 are nearly identical to each other and to lower RLC queue contexts. Copy/paste or generator mistakes are easy to miss, and using the wrong queue offset can silently target a different queue context.
- Offsets and masks must come from the same IP-version header set. Mixing `sdma4_4_2_2_sh_mask.h` with unrelated SDMA4 or `sdma_4_4_0` offsets risks writes to the wrong register or wrong bit positions.
- Split address fields require correct low/high composition and alignment. `RB_RPTR_ADDR_LO`, `RB_WPTR_POLL_ADDR_LO`, `CSA_ADDR_LO`, and `DOORBELL_OFFSET` use low bits as reserved/control space rather than address payload.
- `IB_BASE_LO` starts at bit 5, so IB base programming must respect a stronger alignment than the 4-byte ring pointer address fields.
- `RB_CNTL` contains `RB_PRIV` and `RB_VMID`. Incorrect values can route work under the wrong privilege or GPUVM address space and can produce isolation failures or GPUVM faults.
- Pointer writeback, pointer polling, and doorbell fields connect hardware execution to memory and notification paths. Bad addresses or stale queue pointers can stall queues, corrupt memory, or wake the wrong queue.
- `CONTEXT_STATUS`, `STATUS`, `DOORBELL_LOG`, `WATERMARK`, `IB_SUB_REMAIN`, and `MIDCMD_*` are live hardware-updated fields. Debug code and tests should avoid assuming stable values unless the queue is idle or the driver follows documented polling rules.
- `PREEMPT`, `CSA_ADDR_*`, and `MIDCMD_*` are scheduler-sensitive. Writing them outside expected context-switch or preemption sequences can corrupt resume state or leave a queue wedged.

## Test and Validation Signals

Useful validation is mostly generated-header consistency plus hardware integration coverage:

- Build AMDGPU paths that include `sdma4/sdma4_4_2_2_sh_mask.h`, especially `sdma_v4_0.c` and `amdgpu_amdkfd_arcturus.c`; missing or renamed macros should fail at compile time.
- Static generation checks should verify every field in this chunk has a matching `_SHIFT` and `_MASK` pair and that full-width fields use `0xFFFFFFFFL`.
- Cross-check the masks against the authoritative SDMA4 4.2.2 register database, especially packed fields in `RB_CNTL`, `RB_WPTR_POLL_CNTL`, `CONTEXT_STATUS`, `DOORBELL`, `STATUS`, `WATERMARK`, `RB_AQL_CNTL`, and `MIDCMD_CNTL`.
- Check offset/header consistency: every RLC6/RLC7 register in `sdma4_4_2_2_offset.h` should have the corresponding field definitions here, and the RLC6-to-RLC7 stride should match the queue-index arithmetic used by AMDKFD.
- Boot/probe on Arcturus-class hardware should apply SDMA golden settings without SDMA register access faults or queue hangs.
- KFD SDMA queue load/dump/destroy tests should exercise high queue IDs that resolve to RLC6 and RLC7, verifying idle polling, doorbell setup, ring base/pointers, pointer writeback, and write-pointer polling.
- Queue submission tests should confirm ring pointer movement, read-pointer writeback memory updates, doorbell notification, IB execution, and VMID/privilege behavior for queues backed by these register contexts.
- Preemption/context-switch testing should observe `CONTEXT_STATUS`, `PREEMPT`, `CSA_ADDR_*`, `IB_SUB_REMAIN`, and `MIDCMD_*` before and after forced SDMA IB preemption.
- Register dump decoders should use these masks to decode live RLC6/RLC7 values and compare them with expected MQD/HQD configuration.

## Chunk Boundary Notes

This is the final chunk of `sdma4_4_2_2_sh_mask.h`. Merge/reconciliation should combine the initial `SDMA4_RLC5_MIDCMD_CNTL` block with the previous RLC5 chunk, treat RLC6 and RLC7 as complete context-register field blocks, and retain the closing include-guard note.
