# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_0_sh_mask.h lines 13009-13922

## Scope

This chunk covers a generated AMD SDMA 4.4.0 shift/mask header region for `SDMA4_RLC*` queue registers. The range starts in the tail of the `SDMA4_RLC3_IB_CNTL` field definitions and continues through the complete `SDMA4_RLC4`, `SDMA4_RLC5`, `SDMA4_RLC6`, and `SDMA4_RLC7` register-field groups, ending just before the header guard's final `#endif`.

The chunk contains 703 preprocessor `#define` entries. It defines constants only: there are no C functions, structs, enums, variables, allocations, locking paths, or executable branches in the selected lines.

## Purpose

The purpose of this header section is to provide the bit-level ABI between SDMA 4.4.0 hardware and AMDGPU code that reads or writes SDMA RLC queue registers. Each hardware field is represented by the generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or compose that field.

These macros are intended to be paired with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_0_offset.h`, which supplies the matching `regSDMA4_RLC*_*` register addresses. Runtime consumers include the SDMA 4.4 support code that includes this header, especially `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_4.c`, and the broader AMDGPU register helper machinery around `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, and SOC15 offset handling.

## Register Families

### RLC3 Tail

The first lines continue an `SDMA4_RLC3_IB_CNTL` definition started before the chunk. Within this chunk the visible fields are:

- `CMD_VMID`, plus masks for `IB_ENABLE`, `IB_SWAP_ENABLE`, `SWITCH_INSIDE_IB`, and `CMD_VMID`.
- Indirect-buffer pointer/address/size fields: `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO`, `IB_BASE_HI`, `IB_SIZE`, and `IB_SUB_REMAIN`.
- Queue status and scheduling fields: `SKIP_CNTL`, `CONTEXT_STATUS`, `PREEMPT`, and `MINOR_PTR_UPDATE`.
- Doorbell and pointer polling fields: `DOORBELL`, `STATUS`, `DOORBELL_LOG`, `DOORBELL_OFFSET`, `RB_WPTR_POLL_ADDR_HI`, and `RB_WPTR_POLL_ADDR_LO`.
- Context-save and diagnostic fields: `CSA_ADDR_LO`, `CSA_ADDR_HI`, `DUMMY_REG`, `WATERMARK`, `RB_AQL_CNTL`, `MIDCMD_DATA0` through `MIDCMD_DATA10`, and `MIDCMD_CNTL`.

Because the line range begins after the first `SDMA4_RLC3_IB_CNTL` shift definitions, `IB_ENABLE__SHIFT`, `IB_SWAP_ENABLE__SHIFT`, and `SWITCH_INSIDE_IB__SHIFT` for RLC3 live in the preceding chunk even though their masks are present here.

### RLC4 Through RLC7 Queues

The rest of the range repeats the same queue register layout for `SDMA4_RLC4`, `SDMA4_RLC5`, `SDMA4_RLC6`, and `SDMA4_RLC7`. Each complete queue group exposes:

- Ring-buffer control and addressing: `RB_CNTL`, `RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, `RB_WPTR_HI`, `RB_RPTR_ADDR_HI`, and `RB_RPTR_ADDR_LO`.
- Write-pointer polling: `RB_WPTR_POLL_CNTL`, `RB_WPTR_POLL_ADDR_HI`, and `RB_WPTR_POLL_ADDR_LO`.
- Indirect-buffer dispatch: `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO`, `IB_BASE_HI`, `IB_SIZE`, and `IB_SUB_REMAIN`.
- Queue status, preemption, and context state: `SKIP_CNTL`, `CONTEXT_STATUS`, `PREEMPT`, `CSA_ADDR_LO`, `CSA_ADDR_HI`, and `MINOR_PTR_UPDATE`.
- Doorbell handling: `DOORBELL`, `STATUS`, `DOORBELL_LOG`, and `DOORBELL_OFFSET`.
- Flow-control and command snapshot fields: `WATERMARK`, `RB_AQL_CNTL`, `DUMMY_REG`, `MIDCMD_DATA0` through `MIDCMD_DATA10`, and `MIDCMD_CNTL`.

The repeated layout makes these RLC queues register-compatible. Driver code can often use a base register plus a queue stride, while the generated macros preserve queue-specific symbolic names for compile-time field composition.

## Important Fields

`RB_CNTL` is the primary ring-buffer configuration register. Its fields include `RB_ENABLE`, `RB_SIZE`, `RB_SWAP_ENABLE`, `RPTR_WRITEBACK_ENABLE`, `RPTR_WRITEBACK_SWAP_ENABLE`, `RPTR_WRITEBACK_TIMER`, `RB_PRIV`, and `RB_VMID`. Incorrect values here can prevent queue execution, corrupt pointer writeback, or run a queue under the wrong VMID/privilege context.

`RB_BASE` and `RB_BASE_HI` describe the ring buffer GPU address. The low-address register is full-width in this mask header, while the high register masks only 24 bits. Pointer registers (`RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, `RB_WPTR_HI`) are full-width offsets, and the writeback address low registers mask address bits with 4-byte alignment.

`RB_WPTR_POLL_CNTL` controls hardware polling of the write pointer. The relevant fields are `ENABLE`, `SWAP_ENABLE`, `F32_POLL_ENABLE`, `FREQUENCY`, and `IDLE_POLL_COUNT`. The companion poll address registers provide the memory location being polled.

`IB_CNTL` enables indirect-buffer execution and describes command interpretation with `IB_ENABLE`, `IB_SWAP_ENABLE`, `SWITCH_INSIDE_IB`, and `CMD_VMID`. `IB_BASE_LO` is 32-byte aligned, `IB_RPTR` and `IB_OFFSET` use bit-2 alignment, and `IB_SIZE`/`IB_SUB_REMAIN` expose 20-bit size counters.

`CONTEXT_STATUS` is the main queue state observation register. It includes `SELECTED`, `IDLE`, `EXPIRED`, `EXCEPTION`, `CTXSW_ABLE`, `CTXSW_READY`, `PREEMPTED`, and `PREEMPT_DISABLE`. These bits are useful for bring-up, queue reset, preemption, and post-hang diagnostics.

`DOORBELL` and `DOORBELL_OFFSET` define whether MMIO/doorbell writes are enabled for the queue and where the queue listens in the doorbell aperture. `DOORBELL_LOG` captures backend error state and logged doorbell data. `STATUS` exposes write-pointer update failure and pending indicators.

`WATERMARK` carries read and write outstanding thresholds. `RB_AQL_CNTL` enables AQL packet mode and configures packet size/step. `MIDCMD_DATA*` and `MIDCMD_CNTL` capture or restore mid-command state with `DATA_VALID`, `COPY_MODE`, `SPLIT_STATE`, and `ALLOW_PREEMPT`, which is relevant to preemption and command replay.

## APIs, Types, and Functions

This chunk does not define callable APIs or C types. Its practical API surface is the generated macro naming convention consumed by AMDGPU register helpers:

- `REG_SET_FIELD(value, REGISTER, FIELD, field_value)` expects `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`.
- `REG_GET_FIELD(value, REGISTER, FIELD)` expects the same mask/shift pair.
- `SOC15_REG_FIELD`, RAS field tables, and generated register metadata use the same `REGISTER__FIELD_*` convention.
- `RREG32`/`WREG32` and SOC15-specific wrappers perform the actual MMIO access once a matching register offset is selected.

The companion offset header provides register addresses such as `regSDMA4_RLC4_RB_CNTL`, `regSDMA4_RLC5_DOORBELL`, and `regSDMA4_RLC7_MIDCMD_CNTL`. This mask header provides only field extraction/composition constants for the values read from or written to those addresses.

## Control Flow

There is no local control flow in the chunk. The effective runtime flow happens in driver code that includes the header:

1. Select an SDMA instance and queue register offset from the offset header or a helper that applies an instance base offset.
2. Read the current register value when preserving unrelated fields is required.
3. Use `REG_SET_FIELD` or direct mask/shift operations to compose new field values.
4. Write the composed value with an MMIO helper.
5. Poll status fields such as `CONTEXT_STATUS`, `STATUS`, or pointer registers when waiting for idle, queue stop, pointer writeback, or reset completion.

For this repository snapshot, `amdgpu/sdma_v4_4.c` includes `sdma_4_4_0_sh_mask.h` and uses the same generated-mask style for SDMA 4.4 RAS counter fields. Queue setup code for nearby SDMA generations, such as `sdma_v4_4_2.c`, demonstrates the normal pattern: configure ring buffer size/address, pointer writeback, write-pointer polling, doorbells, then set `RB_ENABLE` and `IB_ENABLE`.

## State and Persistence

The macros themselves are compile-time constants and hold no process or kernel state. The hardware registers they describe are volatile device state:

- Ring and indirect-buffer base addresses persist in hardware until reset, suspend, power gating, or explicit reprogramming.
- Read/write pointers and IB offsets change as SDMA consumes queue work.
- Doorbell capture/log/status fields reflect runtime doorbell activity and errors.
- Context-status and mid-command fields reflect queue scheduling/preemption state and may be meaningful during hang recovery or context save/restore.
- RLC context-save addresses (`CSA_ADDR_LO`/`CSA_ADDR_HI`) point hardware at memory used for queue context state.

On suspend/resume, reset, GPU recovery, or XCP/partition transitions, driver code must reestablish the relevant register state from `struct amdgpu_ring`, firmware-derived topology, doorbell assignments, and memory manager allocations. The header is part of that persistent hardware contract but does not persist anything by itself.

## Dependencies and Integration Points

This chunk depends on generated ASIC register conventions shared across AMDGPU:

- `sdma_4_4_0_offset.h` for `regSDMA4_RLC*_*` register addresses.
- `soc15.h` and AMDGPU MMIO helpers for translating logical register names into mapped MMIO offsets.
- `amdgpu_ring` state for ring base address, read/write pointer backing memory, doorbell index, and queue size.
- Doorbell management in AMDGPU/KFD paths, because `DOORBELL` and `DOORBELL_OFFSET` must match the doorbell aperture assignment visible to user queues or kernel queues.
- VMID and context-switching code, because `RB_VMID`, `CMD_VMID`, `CSA_ADDR*`, `PREEMPT`, and `CONTEXT_STATUS` encode queue ownership and preemption behavior.
- SDMA firmware and microcode behavior, which consumes these register values and updates status/pointer fields.

There is also a KFD-facing integration point in `amdgpu_amdkfd_arcturus.c`, which computes SDMA RLC register spacing from `mmSDMA4_RLC0_RB_CNTL` in the related `sdma4_4_2_2` register set. That pattern reinforces that RLC queue registers are laid out as repeated queue blocks.

## Risks

The main risk is register-definition drift. If a mask or shift does not match the SDMA 4.4.0 hardware specification, the driver may silently program the wrong bits. For this chunk, high-impact examples include `RB_ENABLE`, `IB_ENABLE`, `DOORBELL__ENABLE`, `RB_VMID`, `CMD_VMID`, `RB_BASE_HI`, `RB_RPTR_ADDR_LO__ADDR`, and `MIDCMD_CNTL`.

Alignment-sensitive fields are another risk. Several address/offset fields intentionally mask low bits: `IB_BASE_LO` starts at bit 5, `IB_RPTR`/`IB_OFFSET` start at bit 2, doorbell offsets are 4-byte aligned, and pointer writeback addresses mask low bits. Driver code that shifts or pre-aligns values incorrectly can point hardware at the wrong memory.

The RLC3 portion is split across chunk boundaries. Research or generated checks that treat this chunk as an independent complete register group must account for the missing RLC3 `IB_CNTL` shift lines that precede line 13009.

Queue-specific repetition can hide copy/paste or generation errors. RLC4-RLC7 should be structurally identical for most fields, so a single divergent mask may only affect one queue and appear as an intermittent multi-queue scheduling or KFD workload issue.

Doorbell and VMID fields are security-sensitive in virtualized or multi-process GPU workloads. A wrong doorbell offset or VMID can cause work submission to target the wrong queue or address space.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, register-level, and hardware-integration signals:

- The kernel tree compiles with `sdma_4_4_0_sh_mask.h` included by `amdgpu/sdma_v4_4.c`; missing or renamed masks should fail builds where corresponding `REG_SET_FIELD`, `REG_GET_FIELD`, or `SOC15_REG_FIELD` uses exist.
- Generated-header consistency checks can compare every `SDMA4_RLC4` through `SDMA4_RLC7` register group for identical field names, shifts, and masks where the hardware layout is expected to repeat.
- Offset/mask pairing checks can verify that every register comment in this chunk has a matching `regSDMA4_RLC*_*` definition in `sdma_4_4_0_offset.h`.
- Runtime queue bring-up should show successful SDMA ring tests and IB tests, with ring pointers advancing and no `WPTR_UPDATE_FAIL_COUNT` growth.
- Doorbell tests should confirm that enabling `DOORBELL__ENABLE` and programming `DOORBELL_OFFSET` causes write-pointer updates to reach the expected queue.
- Hang recovery and reset tests should observe sensible `CONTEXT_STATUS` transitions, successful `PREEMPT` behavior where supported, and restored ring/IB state after resume.
- RAS and diagnostics should still compile and report SDMA instance state correctly, because the SDMA 4.4 code includes this generated mask header alongside the offset header.
