# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma2/sdma2_4_2_2_sh_mask.h lines 2570-2956

## Scope

This chunk is the final section of the generated AMD SDMA2 4.2.2 shift/mask header. It begins at the tail of `SDMA2_RLC5_MIDCMD_*`, covers the complete field geometry for SDMA2 RLC queue contexts 6 and 7, and ends with the file's closing include guard.

The file is C preprocessor metadata only. It defines `*_SHIFT` and `*_MASK` constants for hardware register fields. It contains no functions, structs, enums, storage, allocation, locking, branches, loops, or direct MMIO accesses. The macros become useful when paired with the matching offset header, `sdma2_4_2_2_offset.h`, and AMDGPU register helpers such as `REG_SET_FIELD()`, `REG_GET_FIELD()`, `RREG32()`, `WREG32()`, and `SOC15_REG_OFFSET()`.

Although the repository path is under a `ceph-client` source mirror, this chunk documents AMD GPU SDMA register programming state. It is not distributed filesystem logic.

## Purpose

`sdma2_4_2_2_sh_mask.h` supplies symbolic bit positions and masks for SDMA engine 2 on the Arcturus-era SDMA 4.2.2 register layout. The covered range describes high-numbered RLC queue contexts:

- The first lines finish `SDMA2_RLC5_MIDCMD_CNTL`, exposing `DATA_VALID`, `COPY_MODE`, `SPLIT_STATE`, and `ALLOW_PREEMPT`.
- `SDMA2_RLC6_*` defines the full register-field layout for RLC queue 6.
- `SDMA2_RLC7_*` defines the full register-field layout for RLC queue 7.

RLC6 and RLC7 are structurally identical in this header. Each queue context exposes ring-buffer setup, read/write pointer state, write-pointer polling, read-pointer writeback, indirect-buffer execution state, queue status, doorbell state, memory watermarks, context-save addresses, preemption control, AQL packet controls, minor-pointer update, and mid-command snapshot/control words.

## Important Macro Families

The chunk exports these macro groups:

- `SDMA2_RLC[6|7]_RB_CNTL__*`: ring-buffer enablement and attributes. Fields include `RB_ENABLE`, `RB_SIZE`, `RB_SWAP_ENABLE`, `RPTR_WRITEBACK_ENABLE`, `RPTR_WRITEBACK_SWAP_ENABLE`, `RPTR_WRITEBACK_TIMER`, `RB_PRIV`, and `RB_VMID`.
- `SDMA2_RLC[6|7]_RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, and `RB_WPTR_HI`: ring base-address and producer/consumer pointer fields. The low base is full 32-bit and the high base carries a 24-bit address field.
- `SDMA2_RLC[6|7]_RB_WPTR_POLL_CNTL__*`: write-pointer polling configuration. It defines polling enable, swap enable, 32-bit polling mode, polling frequency, and idle poll count.
- `SDMA2_RLC[6|7]_RB_RPTR_ADDR_HI/LO` and `RB_WPTR_POLL_ADDR_HI/LO`: memory addresses for read-pointer writeback and write-pointer polling. Low address fields are 4-byte aligned with `ADDR__SHIFT = 0x2` and `ADDR_MASK = 0xFFFFFFFC`; `RB_RPTR_ADDR_LO` also contains `RPTR_WB_IDLE`.
- `SDMA2_RLC[6|7]_IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO`, `IB_BASE_HI`, `IB_SIZE`, and `IB_SUB_REMAIN`: indirect-buffer enablement, VMID selection for commands, base address, current pointer/offset, total size, and remaining sub-IB size.
- `SDMA2_RLC[6|7]_CONTEXT_STATUS__*`: hardware scheduling and context-switch status. Fields cover selected, idle, expired, exception bits, context-switch ability/readiness, preempted, and preempt-disable state.
- `SDMA2_RLC[6|7]_DOORBELL`, `DOORBELL_LOG`, and `DOORBELL_OFFSET`: doorbell enable/captured state, logged backend error/data, and the aligned doorbell aperture offset.
- `SDMA2_RLC[6|7]_STATUS__*`: write-pointer update failure count and pending-update state.
- `SDMA2_RLC[6|7]_WATERMARK__*`: read and write outstanding-watermark fields.
- `SDMA2_RLC[6|7]_CSA_ADDR_LO/HI`: context-save area address fields, with the low address aligned on bit 2.
- `SDMA2_RLC[6|7]_PREEMPT__IB_PREEMPT`: command bit used to request IB preemption.
- `SDMA2_RLC[6|7]_DUMMY_REG`: a full-width scratch/dummy field.
- `SDMA2_RLC[6|7]_RB_AQL_CNTL__*`: AQL/HSA queue controls for AQL enablement, packet size, and packet step.
- `SDMA2_RLC[6|7]_MINOR_PTR_UPDATE__ENABLE`: latch/control bit around minor pointer updates.
- `SDMA2_RLC[6|7]_MIDCMD_DATA0` through `MIDCMD_DATA8` and `MIDCMD_CNTL`: mid-command snapshot data and control fields for validity, copy mode, split state, and preemption allowance.

There are no callable APIs or C types in this chunk. The macro namespace is the public interface.

## Control Flow and Data Flow

This header has no local runtime control flow. Runtime behavior appears when AMDGPU code combines these masks with register addresses and MMIO accessors:

1. Code selects the SDMA engine and queue context. For Arcturus KFD SDMA queue management, `amdgpu_amdkfd_arcturus.c` includes `sdma2/sdma2_4_2_2_offset.h` and `sdma2/sdma2_4_2_2_sh_mask.h` alongside SDMA0 through SDMA7 headers.
2. `get_sdma_rlc_reg_offset()` computes a per-engine base and queue offset from `mmSDMA[0-7]_RLC0_RB_CNTL` plus a queue stride derived from `mmSDMA0_RLC1_RB_CNTL - mmSDMA0_RLC0_RB_CNTL`. For engine 2, this uses `SOC15_REG_OFFSET(SDMA2, 0, mmSDMA2_RLC0_RB_CNTL) - mmSDMA2_RLC0_RB_CNTL`.
3. Queue load, dump, occupancy, and destroy paths use RLC0 register names plus the computed queue offset. For queue ids 6 and 7 on SDMA engine 2, that addressing lands on the RLC6/RLC7 registers whose fields are described by this chunk.
4. Register helpers compose or test fields using the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` names. For example, queue load clears and later sets `RB_ENABLE`, waits for `CONTEXT_STATUS.IDLE`, programs doorbell offset/enable, writes ring pointers and base addresses, and toggles `MINOR_PTR_UPDATE` around write-pointer updates.
5. Hardware consumes the programmed register state to fetch ring commands, poll or write back pointers, process doorbells, execute IBs, save/resume context state, report queue status, and honor preemption/AQL controls.

The SDMA v4.0 initialization code also includes this header. Its SDMA 4.2 golden-setting tables program related high RLC queue registers for pointer-writeback idle state and write-pointer polling. In `sdma_v4_0.c`, SDMA0/SDMA1 golden settings include RLC6/RLC7 `RB_RPTR_ADDR_LO` and `RB_WPTR_POLL_CNTL` entries; the same field contract applies to the SDMA2 4.2.2 generated namespace when the Arcturus multi-SDMA engine path addresses engine 2.

## State and Persistence Behavior

The header stores no software state and persists nothing on disk. It describes hardware register state whose lifetime is controlled by SDMA engine reset, queue programming, context switching, power management, firmware behavior, and driver teardown.

Register-state categories in this chunk include:

- Ring state: enablement, queue size, base addresses, read/write pointers, byte-swap behavior, privilege, VMID, and read-pointer writeback settings.
- Pointer-memory state: memory addresses used by hardware for read-pointer writeback and write-pointer polling, including idle indication and polling cadence.
- Doorbell state: doorbell enablement, captured indication, offset, logged data, and backend-error indication.
- IB state: indirect-buffer enablement, base, size, current read pointer, current offset, command VMID, and remaining sub-IB size.
- Scheduler/context state: selected, idle, expired, exception bits, context-switch readiness, preempted, and preempt-disabled status.
- Context-save/preemption state: context-save area address, IB preempt request, mid-command data words, and mid-command control flags used to recover or continue interrupted work.
- AQL state: AQL enablement, packet size, and packet step.
- Live status/counters: write-pointer update failures, pending updates, and read/write outstanding-watermark values.

The header does not specify reset values, read/write permissions, sticky-bit behavior, write-one-to-clear semantics, or ordering rules. Those requirements come from the hardware register specification and the driver sequences that use the fields.

## Dependencies and Integration Points

Primary dependencies and integration points are:

- `sdma2_4_2_2_offset.h`: provides the concrete register addresses that match these masks. In the matching offset header, RLC6 starts at `mmSDMA2_RLC6_RB_CNTL = 0x0340` and RLC7 starts at `mmSDMA2_RLC7_RB_CNTL = 0x0398`, with the related status, context-save, preemption, polling, AQL, and mid-command registers laid out afterward.
- AMDGPU SOC15 register helpers: `SOC15_REG_OFFSET()` maps logical IP block/register names to MMIO addresses, while `RREG32()` and `WREG32()` perform 32-bit MMIO reads and writes.
- AMDGPU field helpers: `REG_SET_FIELD()` and related macros depend on the exact generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming convention.
- `amdgpu/amdgpu_amdkfd_arcturus.c`: includes this SDMA2 4.2.2 mask header and uses matching offset headers for KFD SDMA queue load, dump, occupancy, and destroy operations across SDMA engines and RLC queue ids.
- `amdgpu/sdma_v4_0.c`: includes the header in SDMA v4 bring-up code and uses related RLC queue register names in golden settings for pointer writeback and write-pointer polling.
- MQD state structures such as `struct v9_sdma_mqd`: queue load/destroy paths move software-saved queue state into and out of the hardware RLC registers whose fields are described here.
- Hardware doorbell, GPUVM/VMID, KFD queue scheduling, AQL/HSA queueing, and preemption/context-save mechanisms.

The RLC6/RLC7 layouts are part of a repeated generated pattern across SDMA engines 0 through 7. Engine-specific headers keep the same field concepts under distinct `SDMA<n>_` prefixes so callers do not mix IP blocks accidentally.

## Risks and Edge Cases

- The chunk starts inside `SDMA2_RLC5_MIDCMD_CNTL`; a whole-file report must merge this boundary with the preceding chunk before making complete RLC5 claims.
- These macros are untyped constants. A stale mask, wrong shift, or wrong IP-version header can compile cleanly but program the wrong hardware bits.
- RLC6 and RLC7 are almost identical. Generator, copy/paste, or merge errors are easy to miss unless checked against the authoritative register database and matching offset header.
- Queue addressing in Arcturus KFD is stride-based from RLC0. If the assumed RLC stride or offset-header layout drifts, queue id 6 or 7 can target the wrong context register block even though field masks still compile.
- Low address fields are alignment-sensitive. `ADDR__SHIFT = 0x2` and masks such as `0xFFFFFFFC` mean unaligned ring pointer writeback, write-pointer polling, CSA, IB, or doorbell offsets will lose low bits.
- `RB_CNTL.RB_VMID` and `RB_PRIV` affect address translation and privilege. Bad values can route SDMA work through the wrong VMID or trigger GPUVM faults/isolation failures.
- Doorbell offset and enable fields connect user/kernel queue signaling to hardware. Misprogramming can wake the wrong queue, miss queue updates, or leave stale captured/logged doorbell state.
- Pointer polling and writeback fields connect hardware to memory. Wrong addresses or swap settings can corrupt memory or make hardware consume stale producer pointers.
- `CONTEXT_STATUS`, `STATUS`, `WATERMARK`, `IB_SUB_REMAIN`, `DOORBELL_LOG`, and `MIDCMD_*` are live hardware-updated state. Diagnostics must account for races unless the queue is quiesced or the driver has explicit polling rules.
- Preemption and mid-command state are scheduler-sensitive. Writing `PREEMPT` or `MIDCMD_CNTL` outside the expected context-switch sequence can leave work partially saved, corrupt resume state, or stall the queue.
- The field layout is SDMA2 4.2.2-specific. Similar SDMA 4.2, SDMA 4.4, and GC-generated headers contain related but not necessarily identical address maps or mid-command data counts; mixing masks and offsets across generations is unsafe.

## Test and Validation Signals

Useful validation signals are mostly build-time, generated-header consistency, and hardware integration tests:

- Build AMDGPU/KFD code paths that include `sdma2/sdma2_4_2_2_sh_mask.h` with the matching offset header. Missing or renamed macros should fail at compile time.
- Static generation checks should verify every field in this chunk has a paired `_SHIFT` and `_MASK`, full-width fields use `0xFFFFFFFFL`, low aligned address fields mask off the low two or five bits as expected, and RLC6/RLC7 definitions remain structurally identical where the hardware requires it.
- Cross-check against `sdma2_4_2_2_offset.h`: every RLC6/RLC7 register in the offset header should have field definitions here, and the RLC6/RLC7 address ranges should preserve the queue-context stride used by KFD queue-offset calculations.
- Compare packed fields against the authoritative AMD register database, especially `RB_CNTL`, `RB_WPTR_POLL_CNTL`, `IB_CNTL`, `CONTEXT_STATUS`, `DOORBELL`, `STATUS`, `WATERMARK`, `RB_AQL_CNTL`, and `MIDCMD_CNTL`.
- On matching Arcturus/SDMA 4.2.2 hardware, KFD SDMA queue load should clear `RB_ENABLE`, observe `CONTEXT_STATUS.IDLE`, program doorbell, ring pointer, ring base, and read-pointer writeback registers, then set `RB_ENABLE` without timeout.
- Queue submission tests should verify ring write-pointer movement, read-pointer writeback, write-pointer polling, and doorbell notification for SDMA engine 2 high RLC queues when exposed by the driver configuration.
- Queue destroy tests should verify `RB_ENABLE` clearing, idle polling, doorbell disablement, and persistence of read-pointer values back into the MQD.
- Register dump tests should decode RLC6/RLC7 state using these masks and compare decoded values against expected queue configuration, VMID, privilege, doorbell offset, AQL mode, and idle/preempt status.
- Preemption/context-switch tests should exercise `PREEMPT`, `CONTEXT_STATUS`, `CSA_ADDR_*`, `IB_SUB_REMAIN`, and `MIDCMD_*` state around forced SDMA IB preemption and resume.

## Chunk Boundary Notes

This is the final chunk of `sdma2_4_2_2_sh_mask.h`. Merge/reconciliation should attach the initial RLC5 mid-command control lines to the previous RLC5 chunk, treat RLC6 and RLC7 as complete queue-context field blocks, and retain the closing include-guard note.
