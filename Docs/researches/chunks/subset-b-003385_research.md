# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_2_sh_mask.h lines 2569-2948

## Scope

This chunk is the tail of the generated AMD SDMA1 4.2 shift/mask header. It starts with the final mask lines for `SDMA1_RLC5_MIDCMD_CNTL`, then defines the complete bitfield geometry for SDMA1 RLC context queues 6 and 7, and ends with the file's closing include-guard `#endif`.

The file is C preprocessor metadata only. It contains no functions, structs, enums, static storage, allocation, locking, branches, loops, MMIO calls, or direct control flow. Its public surface is the generated `*_SHIFT` and `*_MASK` macro namespace used by AMDGPU register helpers and register programming code.

Although the repository path is under a `ceph-client` source mirror, this chunk documents AMD GPU SDMA hardware register fields. It does not implement distributed filesystem behavior.

## Purpose

`sdma1_4_2_sh_mask.h` supplies symbolic bit positions and masks for fields inside SDMA1 4.2 registers. It is paired with SDMA1 4.2 offset headers such as `sdma1_4_2_offset.h` and nearby revision headers, which provide the register addresses. Consumers combine the address macros with these shift/mask macros through AMDGPU helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()` or through hand-built read/modify/write sequences.

The covered range describes queue-context register fields for the high RLC contexts on SDMA engine 1:

- The boundary lines finish `SDMA1_RLC5_MIDCMD_CNTL`, with masks for `DATA_VALID`, `COPY_MODE`, `SPLIT_STATE`, and `ALLOW_PREEMPT`.
- `SDMA1_RLC6_*` defines the full RLC6 queue-context bit layout.
- `SDMA1_RLC7_*` defines the full RLC7 queue-context bit layout.

RLC6 and RLC7 are structurally identical in this header. They expose ring-buffer configuration, read/write pointer handling, write-pointer polling, read-pointer writeback, indirect-buffer execution state, context status, doorbell state, queue status, watermarks, context-save addresses, preemption control, AQL controls, minor-pointer update, and mid-command snapshot/control fields.

## Important Macro Families

The exported macros follow a strict generated naming convention:

- `SDMA1_RLC[6|7]_RB_CNTL__*` describes ring-buffer control fields. It includes `RB_ENABLE`, `RB_SIZE`, `RB_SWAP_ENABLE`, read-pointer writeback enable/swap/timer fields, `RB_PRIV`, and `RB_VMID`.
- `SDMA1_RLC[6|7]_RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, and `RB_WPTR_HI` are full-width or high-address/offset fields for ring storage and queue pointers.
- `SDMA1_RLC[6|7]_RB_WPTR_POLL_CNTL` describes polling enable, swap enable, 32-bit polling mode, polling frequency, and idle poll count.
- `SDMA1_RLC[6|7]_RB_RPTR_ADDR_HI/LO` and `RB_WPTR_POLL_ADDR_HI/LO` describe GPU/CPU-visible memory addresses used for read-pointer writeback and write-pointer polling. The low address fields are 4-byte aligned through `ADDR__SHIFT = 0x2` and `ADDR_MASK = 0xFFFFFFFC`; `RB_RPTR_ADDR_LO` also exposes `RPTR_WB_IDLE`.
- `SDMA1_RLC[6|7]_IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO`, `IB_BASE_HI`, `IB_SIZE`, and `IB_SUB_REMAIN` describe indirect-buffer enablement, address, progress, and remaining-size state.
- `SDMA1_RLC[6|7]_CONTEXT_STATUS` exposes scheduler/context-switch state: selected, idle, expired, exception code bits, context-switch ability/readiness, preempted state, and preempt-disable state.
- `SDMA1_RLC[6|7]_DOORBELL`, `DOORBELL_LOG`, and `DOORBELL_OFFSET` define doorbell enable/captured status, logged data/error, and the aligned doorbell aperture offset.
- `SDMA1_RLC[6|7]_STATUS` reports write-pointer update failure count and pending update state.
- `SDMA1_RLC[6|7]_WATERMARK` packs read and write outstanding-watermark fields.
- `SDMA1_RLC[6|7]_CSA_ADDR_LO/HI` defines context-save area address fields.
- `SDMA1_RLC[6|7]_PREEMPT` exposes the `IB_PREEMPT` command bit.
- `SDMA1_RLC[6|7]_RB_AQL_CNTL` defines AQL enablement, packet size, and packet step fields for AQL/HSA-style queues.
- `SDMA1_RLC[6|7]_MIDCMD_DATA0` through `MIDCMD_DATA8` are full 32-bit mid-command data words, with `MIDCMD_CNTL` indicating validity, copy mode, split state, and whether preemption is allowed.

There are no callable APIs or C types in this chunk. The macros themselves are the interface.

## Control Flow and Data Flow

The header has no local runtime control flow. The effective flow occurs in AMDGPU SDMA consumers:

1. SDMA code selects an SDMA1 RLC6 or RLC7 register address from a matching offset header, such as `mmSDMA1_RLC6_RB_WPTR_POLL_CNTL` or `mmSDMA1_RLC7_RB_RPTR_ADDR_LO`.
2. Driver code reads, writes, or read/modify/writes the register through SOC15/AMDGPU MMIO helpers.
3. Field helper macros use the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` definitions from this chunk to isolate or compose specific fields.
4. Hardware interprets the value as queue-context state for ring execution, pointer polling/writeback, doorbell notification, indirect-buffer processing, context switching, preemption, AQL packet handling, or mid-command resume.

The surrounding AMDGPU SDMA initialization code includes this shift/mask header in `amdgpu/sdma_v4_0.c`. The same RLC6/RLC7 register names appear in golden-setting tables, where `mmSDMA1_RLC6_RB_RPTR_ADDR_LO`, `mmSDMA1_RLC6_RB_WPTR_POLL_CNTL`, `mmSDMA1_RLC7_RB_RPTR_ADDR_LO`, and `mmSDMA1_RLC7_RB_WPTR_POLL_CNTL` receive masked initialization values. SDMA v5 code has analogous golden settings for the same queue-context concepts in later generated headers, so these field layouts are part of a recurring AMDGPU SDMA register contract.

## State and Persistence Behavior

This header stores no software state and persists nothing to disk. It describes hardware-owned register state:

- Ring state persists queue enablement, queue size, base addresses, read/write pointers, privilege and VMID selection, byte-swap behavior, and read-pointer writeback policy until reset or reprogramming.
- Polling state persists whether hardware polls a write-pointer memory location, how frequently it polls, how it swaps data, and how it behaves while idle.
- Doorbell state persists enablement, offset selection, captured-doorbell indication, and logged doorbell data/error status.
- Indirect-buffer state persists IB enablement, base, size, read pointer, current offset, and remaining sub-IB size while work executes.
- Context and scheduling state is live hardware status: selected, idle, expired, exception bits, context-switch readiness, preempted, and preempt-disabled conditions.
- Context-save and mid-command state persists addresses and snapshot words used by preemption/context-switch machinery to resume partially executed commands.
- AQL state persists whether AQL mode is active and how packets are sized and stepped.
- Watermark and status fields reflect live outstanding read/write pressure and write-pointer update failures or pending updates.

Persistence duration is controlled by the SDMA engine's reset, power-management, context-switch, and firmware rules. The header does not encode access types, reset values, sticky bits, write-one-to-clear behavior, or sequencing requirements.

## Dependencies and Integration Points

Direct dependencies are generated-header conventions and the AMDGPU register-access layer:

- Matching SDMA1 4.2 offset headers provide concrete `mmSDMA1_RLC6_*` and `mmSDMA1_RLC7_*` register addresses. In `sdma1_4_2_offset.h`, RLC6 starts at `mmSDMA1_RLC6_RB_CNTL = 0x0380` and RLC7 starts at `mmSDMA1_RLC7_RB_CNTL = 0x03e0`; in `sdma1_4_2_2_offset.h`, the same field layout maps onto a slightly different address schedule.
- AMDGPU helper macros depend on the exact `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming scheme.
- `amdgpu/sdma_v4_0.c` includes this header and uses the related address macros in golden-setting arrays for SDMA1 RLC6/RLC7 pointer writeback and write-pointer polling setup.
- Register default headers for adjacent IP versions provide reset/default values, but this shift/mask header supplies only field geometry.

The registers described here integrate with SDMA queue setup, GPU scheduler queue context management, VMID/privilege selection, doorbell routing, memory-backed pointer writeback/polling, indirect-buffer dispatch, preemption/context save/restore, AQL queue operation, register dumps, diagnostics, and hardware bring-up validation.

## Risks and Edge Cases

- The chunk begins in the middle of the RLC5 mid-command control register. Any whole-file analysis must merge with the previous chunk before making complete RLC5 statements.
- The macros are untyped constants. A stale or incorrect mask can compile cleanly while causing writes to the wrong hardware bits.
- RLC6 and RLC7 layouts are nearly identical, making copy/paste or generator errors hard to spot. A wrong RLC index can silently target a different queue context.
- Address fields are split across low/high registers and often require alignment. Low address fields with `ADDR__SHIFT = 0x2` must not be populated with unaligned addresses.
- Ring, polling, read-pointer writeback, and doorbell fields connect the SDMA engine to memory and doorbell apertures. Bad programming can make hardware fetch stale queues, write back to the wrong memory, or wake the wrong context.
- `CONTEXT_STATUS`, `STATUS`, `DOORBELL_LOG`, `WATERMARK`, `IB_SUB_REMAIN`, and `MIDCMD_*` are live hardware-observed or hardware-updated state. Tests and diagnostics should not assume stable values without quiescing or polling rules.
- Preemption and mid-command fields are scheduler-sensitive. Writing them outside the expected preemption/context-switch sequence can corrupt resume state or leave queues stalled.
- VMID and privilege fields in `RB_CNTL` affect memory translation and isolation. Incorrect values can produce GPUVM faults or route work under the wrong address space.
- This field layout is SDMA1 4.2-specific. Nearby generations such as SDMA 4.2.2 and GC 10.x have related but not always identical generated headers; mixing masks and offsets across IP versions is unsafe.

## Test and Validation Signals

Useful validation is mainly generated-header and hardware integration coverage:

- Compile AMDGPU SDMA v4.0 paths that include `sdma1/sdma1_4_2_sh_mask.h` with the matching offset header; unresolved or renamed macros should fail at build time.
- Static generation checks should confirm every RLC6/RLC7 field has a matching `_SHIFT` and `_MASK` pair and that full-width fields use `0xFFFFFFFFL`.
- Cross-check this chunk against the authoritative SDMA1 4.2 register database, especially packed fields in `RB_CNTL`, `RB_WPTR_POLL_CNTL`, `CONTEXT_STATUS`, `DOORBELL`, `STATUS`, `WATERMARK`, `RB_AQL_CNTL`, and `MIDCMD_CNTL`.
- Validate consistency with offset headers: RLC6/RLC7 register names in the offset header should all have field definitions here, and the RLC6/RLC7 context stride should match hardware documentation.
- Boot/probe on matching SDMA 4.2 hardware should apply golden settings for RLC6/RLC7 pointer writeback and write-pointer polling without hangs or register-write faults.
- Queue submission tests should verify ring pointer movement, read-pointer writeback, write-pointer polling, and doorbell notification for high RLC contexts if those queues are exposed by the ASIC/driver configuration.
- Preemption/context-switch tests should exercise `PREEMPT`, `CONTEXT_STATUS`, `CSA_ADDR_*`, `IB_SUB_REMAIN`, and `MIDCMD_*` state before and after forced SDMA IB preemption.
- Register dump decoders should use these masks to decode live RLC6/RLC7 state and compare decoded values against expected queue configuration, VMID, doorbell offset, AQL mode, and idle/preempt status.

## Chunk Boundary Notes

This is the final chunk of `sdma1_4_2_sh_mask.h`. Merge/reconciliation should combine the first few lines with the prior RLC5 chunk, then treat RLC6 and RLC7 as complete context-register field blocks and retain the closing include-guard note.
