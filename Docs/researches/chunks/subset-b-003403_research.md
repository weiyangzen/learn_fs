# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma7/sdma7_4_2_2_sh_mask.h lines 2570-2956

## Scope

This chunk is the tail of the generated SDMA7 4.2.2 shift/mask header. It covers the end of the `SDMA7_RLC5_MIDCMD_CNTL` field definitions, the full `SDMA7_RLC6_*` and `SDMA7_RLC7_*` register field maps, and the closing include guard for `_sdma7_4_2_2_SH_MASK_HEADER`.

The file is a hardware register description header, not runtime logic. It provides C preprocessor constants used by AMDGPU SDMA programming code to compose and decode register values. The sibling address header `sdma7_4_2_2_offset.h` supplies matching `mmSDMA7_RLC6_*` and `mmSDMA7_RLC7_*` register offsets and base indices.

## Purpose

The macros define bit positions and masks for SDMA RLC queue contexts 6 and 7. Each context describes one SDMA run-list controller queue: ring-buffer setup, indirect-buffer execution, doorbell signaling, write-pointer polling, context-switch/preemption status, context-save area addresses, AQL controls, and mid-command capture state.

Important repeated pattern:

- `*_SHIFT` constants give the low bit for a hardware field.
- `*_MASK` constants give the 32-bit field mask after shifting.
- RLC6 and RLC7 have the same field layout; their register names differ only by queue/context index.
- The chunk begins with `RLC5_MIDCMD_CNTL`, completing the RLC5 mid-command block started in the preceding chunk.

## Register Groups

### RLC5 mid-command tail

`SDMA7_RLC5_MIDCMD_CNTL` exposes:

- `DATA_VALID` at bit 0, indicating whether captured mid-command data registers are meaningful.
- `COPY_MODE` at bit 1.
- `SPLIT_STATE` in bits 4-7.
- `ALLOW_PREEMPT` at bit 8.

These fields pair with the earlier `SDMA7_RLC5_MIDCMD_DATA0..8` registers. They are relevant for preemption or context save/restore paths that need to resume a command split across scheduling events.

### RLC6 queue context

The RLC6 block defines a complete SDMA queue context:

- Ring-buffer control and pointers: `RLC6_RB_CNTL`, `RLC6_RB_BASE`, `RLC6_RB_BASE_HI`, `RLC6_RB_RPTR`, `RLC6_RB_RPTR_HI`, `RLC6_RB_WPTR`, and `RLC6_RB_WPTR_HI`.
- Write-pointer polling and read-pointer writeback: `RLC6_RB_WPTR_POLL_CNTL`, `RLC6_RB_WPTR_POLL_ADDR_HI/LO`, and `RLC6_RB_RPTR_ADDR_HI/LO`.
- Indirect-buffer execution: `RLC6_IB_CNTL`, `RLC6_IB_RPTR`, `RLC6_IB_OFFSET`, `RLC6_IB_BASE_LO/HI`, `RLC6_IB_SIZE`, and `RLC6_IB_SUB_REMAIN`.
- Scheduling and context state: `RLC6_SKIP_CNTL`, `RLC6_CONTEXT_STATUS`, `RLC6_PREEMPT`, and `RLC6_MINOR_PTR_UPDATE`.
- Doorbell path: `RLC6_DOORBELL`, `RLC6_DOORBELL_LOG`, and `RLC6_DOORBELL_OFFSET`.
- Context-save and scratch state: `RLC6_CSA_ADDR_LO/HI`, `RLC6_DUMMY_REG`, `RLC6_MIDCMD_DATA0..8`, and `RLC6_MIDCMD_CNTL`.
- Outstanding request and packet mode controls: `RLC6_WATERMARK` and `RLC6_RB_AQL_CNTL`.

Key fields include `RB_ENABLE`, `RB_SIZE`, `RB_SWAP_ENABLE`, read-pointer writeback enable/swap/timer, `RB_PRIV`, and `RB_VMID` in `RLC6_RB_CNTL`; `IB_ENABLE`, `IB_SWAP_ENABLE`, `SWITCH_INSIDE_IB`, and `CMD_VMID` in `RLC6_IB_CNTL`; `SELECTED`, `IDLE`, `EXPIRED`, `EXCEPTION`, `CTXSW_ABLE`, `CTXSW_READY`, `PREEMPTED`, and `PREEMPT_DISABLE` in `RLC6_CONTEXT_STATUS`; and `ENABLE`/`CAPTURED` in `RLC6_DOORBELL`.

### RLC7 queue context

The RLC7 block mirrors RLC6 with the same field names and masks under the `SDMA7_RLC7_*` prefix. The repeated groups cover ring-buffer base/pointers, write-pointer polling, indirect-buffer state, context status, doorbell state, watermark limits, doorbell offset, CSA addresses, preempt command bit, AQL control, minor pointer update, and mid-command data/control.

Because the bit layout is identical to RLC6, driver code can use common queue-programming logic with per-context register offsets. The only distinction is the hardware register address selected by the matching `mmSDMA7_RLC7_*` symbols in the offset header.

## APIs, Types, and Functions

This chunk defines no functions, structs, enums, or callable APIs. Its externally visible interface is the set of preprocessor symbols. Consumers typically combine these masks with register access helpers and field-preparation macros elsewhere in AMDGPU, for example by shifting values into the low bit named by `__SHIFT` and constraining them with `__MASK`.

The constants are hardware ABI definitions. Renaming or changing a value is equivalent to changing the driver's interpretation of SDMA7 registers.

## Control Flow

There is no direct control flow in this header. Runtime control flow appears in consumers that:

1. Program queue registers before enabling an SDMA RLC queue.
2. Update or poll write/read pointers through memory-backed addresses.
3. Ring a doorbell or poll doorbell capture/log state.
4. Read context status to decide whether a queue is idle, selected, preempted, exceptioned, or ready for context switch.
5. Save or restore mid-command and CSA state during preemption or suspend/resume flows.

The ordering of register writes matters in those consumers even though it is not represented here. In particular, base addresses and pointer writeback addresses should be valid before `RB_ENABLE` or doorbell enable bits are set.

## State and Persistence

The state represented by these macros lives in SDMA hardware registers and, for pointer writeback/polling, in GPU-visible memory programmed through address registers:

- Ring-buffer base, RPTR/WPTR offsets, IB base/size, CSA addresses, and poll/writeback addresses persist as hardware context state while the engine and queue remain initialized.
- `CONTEXT_STATUS`, `STATUS`, and `DOORBELL_LOG` expose transient hardware state such as pending pointer updates, failed updates, backend doorbell errors, exceptions, and preemption progress.
- `MIDCMD_DATA0..8` plus `MIDCMD_CNTL` represent resume/capture state for commands interrupted mid-execution.
- The header itself contains no persistence mechanism; it is compile-time metadata for encoding persistent hardware state correctly.

## Dependencies and Integration Points

Primary dependencies:

- Paired register address definitions in `drivers/gpu/drm/amd/include/asic_reg/sdma7/sdma7_4_2_2_offset.h`.
- AMDGPU register I/O helpers that write/read `mmSDMA7_RLC6_*` and `mmSDMA7_RLC7_*` offsets.
- SDMA queue setup, KFD/compute queue, context switching, preemption, doorbell, and suspend/resume code paths that need exact field masks.
- Hardware documentation or generated register database for SDMA7 4.2.2.

Integration is by include-time symbol availability. The masks are usually paired with same-named offset macros; for example `SDMA7_RLC6_RB_CNTL__RB_ENABLE_MASK` applies to `mmSDMA7_RLC6_RB_CNTL`, while `SDMA7_RLC7_DOORBELL_OFFSET__OFFSET_MASK` applies to `mmSDMA7_RLC7_DOORBELL_OFFSET`.

## Risks and Edge Cases

- Address alignment is encoded in masks: several low address bits are not writable, such as `RB_RPTR_ADDR_LO__ADDR_MASK` and `DOORBELL_OFFSET__OFFSET_MASK` beginning at bit 2, and `IB_BASE_LO__ADDR_MASK` beginning at bit 5. Consumers must not pass unaligned addresses and assume the hardware preserves low bits.
- `RB_BASE_HI__ADDR_MASK` is only `0x00FFFFFF`, unlike full-width high-address fields elsewhere. Incorrectly treating it as 32 bits can produce invalid queue base addresses.
- VMID fields are narrow (`RB_VMID` and `CMD_VMID` are 4-bit masks). Values outside the mask would be truncated if assembled naively.
- `CONTEXT_STATUS__EXCEPTION_MASK` spans bits 4-6. It should be decoded as a field, not as a single boolean bit.
- RLC6 and RLC7 are intentionally duplicated. Mechanical edits to one context but not the other would create asymmetric behavior in otherwise identical queues.
- Doorbell enable/captured bits live high in `DOORBELL` (`0x10000000` and `0x40000000`). Consumers must avoid confusing these control bits with doorbell offset fields, which live in `DOORBELL_OFFSET`.
- Mid-command data registers are full 32-bit payload slots, but `MIDCMD_CNTL__DATA_VALID` gates whether their contents should be trusted.

## Test Signals

Useful validation signals for code that consumes this chunk:

- Build coverage: AMDGPU builds fail if expected symbols are missing or renamed.
- Register programming traces should show RLC6/RLC7 ring base, size, VMID, writeback, poll, and doorbell registers receiving values masked to the documented field widths.
- Queue bring-up tests should confirm `RB_ENABLE` and doorbell enable paths work for queues 6 and 7.
- Preemption/context-switch tests should observe `CTXSW_READY`, `PREEMPTED`, `PREEMPT_DISABLE`, `IB_PREEMPT`, and mid-command valid/split state transitions without hangs.
- Suspend/resume or GPU reset tests should restore CSA, RB, IB, and pointer state for RLC6/RLC7 queues.
- Negative/error tests or debug telemetry should flag `WPTR_UPDATE_FAIL_COUNT`, `WPTR_UPDATE_PENDING`, `DOORBELL_LOG__BE_ERROR`, and `CONTEXT_STATUS__EXCEPTION` if pointer or doorbell programming is wrong.
