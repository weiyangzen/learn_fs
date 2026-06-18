# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma3/sdma3_4_2_2_sh_mask.h lines 2570-2956

## Purpose

This chunk is the terminal range of the generated AMD SDMA3 4.2.2 shift/mask header. It defines preprocessor constants for SDMA3 RLC queue-context bitfields: the end of the RLC5 mid-command control block, the complete RLC6 queue block, and the complete RLC7 queue block. The range contains 300 `#define` entries: 150 `__SHIFT` macros and 150 `_MASK` macros. It has no executable C logic, structs, functions, enums, or storage; its API is the generated macro namespace consumed by AMDGPU and KFD register programming paths.

The covered queue blocks describe live SDMA queue state: ring-buffer enablement and sizing, ring base/read/write pointers, write-pointer polling, read-pointer writeback, indirect-buffer execution state, context status, doorbell routing, diagnostic status/logs, watermarks, context-save-area addresses, preemption state, AQL packet interpretation, minor pointer update gating, and mid-command save/restore state.

## Important Macros And Register Fields

- `SDMA3_RLC5_MIDCMD_CNTL` completes the RLC5 mid-command block with `DATA_VALID`, `COPY_MODE`, `SPLIT_STATE`, and `ALLOW_PREEMPT`.
- `SDMA3_RLC6_*` defines a full per-queue RLC context: `RB_CNTL`, `RB_BASE(_HI)`, `RB_RPTR(_HI)`, `RB_WPTR(_HI)`, `RB_WPTR_POLL_CNTL`, `RB_RPTR_ADDR_{HI,LO}`, `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_{LO,HI}`, `IB_SIZE`, `SKIP_CNTL`, `CONTEXT_STATUS`, `DOORBELL`, `STATUS`, `DOORBELL_LOG`, `WATERMARK`, `DOORBELL_OFFSET`, `CSA_ADDR_{LO,HI}`, `IB_SUB_REMAIN`, `PREEMPT`, `DUMMY_REG`, `RB_WPTR_POLL_ADDR_{HI,LO}`, `RB_AQL_CNTL`, `MINOR_PTR_UPDATE`, `MIDCMD_DATA0` through `MIDCMD_DATA8`, and `MIDCMD_CNTL`.
- `SDMA3_RLC7_*` repeats the same full schema for queue 7.
- `RB_CNTL` fields encode `RB_ENABLE`, ring size, endian/swap behavior, read-pointer writeback enable/swap/timer, privileged ring mode, and VMID.
- Pointer and address registers are split across low/high words. Low address masks enforce alignment: read-pointer writeback and poll addresses use bit 2 alignment, IB base low uses bit 5 alignment, and CSA low uses bit 2 alignment.
- `RB_WPTR_POLL_CNTL` exposes hardware polling knobs: `ENABLE`, `SWAP_ENABLE`, `F32_POLL_ENABLE`, polling `FREQUENCY`, and `IDLE_POLL_COUNT`.
- `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_*`, `IB_SIZE`, and `IB_SUB_REMAIN` describe indirect-buffer execution state for a queue.
- `CONTEXT_STATUS` reports `SELECTED`, `IDLE`, `EXPIRED`, `EXCEPTION`, `CTXSW_ABLE`, `CTXSW_READY`, `PREEMPTED`, and `PREEMPT_DISABLE`.
- `DOORBELL`, `DOORBELL_OFFSET`, and `DOORBELL_LOG` describe queue notification enablement, captured state, backend errors, and captured doorbell payload.
- `STATUS` exposes write-pointer update failure count and pending state. `WATERMARK` describes read and write outstanding request limits or counters.
- `RB_AQL_CNTL` fields (`AQL_ENABLE`, `AQL_PACKET_SIZE`, `PACKET_STEP`) describe AQL packet layout for KFD/HSA-style SDMA queues.
- `MIDCMD_DATA*` and `MIDCMD_CNTL` are context save/restore and preemption-related registers for preserving a partially executed SDMA command.

## Control Flow And Usage Model

This header has no branches, loops, or functions. Runtime behavior appears in callers that combine these masks with the companion offset header `sdma3_4_2_2_offset.h` and AMDGPU MMIO helpers.

The direct include sites in this tree are `amdgpu/sdma_v4_0.c` and `amdgpu/amdgpu_amdkfd_arcturus.c`. `sdma_v4_0.c` programs SDMA rings and golden settings through `RREG32_SDMA`, `WREG32_SDMA`, `SOC15_REG_GOLDEN_VALUE`, and `REG_SET_FIELD`; the golden settings explicitly include RLC6/RLC7 writeback-address and write-pointer-poll registers. `amdgpu_amdkfd_arcturus.c` implements KFD SDMA queue load, dump, occupancy, and destroy using the RLC0 register names plus computed queue offsets. That queue-relative pattern means the RLC6/RLC7 field layout must stay schema-compatible with RLC0 even when driver code does not name `SDMA3_RLC6_*` or `SDMA3_RLC7_*` directly.

For KFD-style queue restore, the effective sequence is: compute the SDMA engine and queue register offset, clear `RB_ENABLE`, poll `CONTEXT_STATUS.IDLE`, program doorbell state, program RPTR/WPTR and base/writeback addresses, use `MINOR_PTR_UPDATE` while updating pointers, then set `RB_ENABLE`. Dump paths iterate contiguous register windows from `RB_CNTL` through `DOORBELL`, from `STATUS` through `CSA_ADDR_HI`, from `IB_SUB_REMAIN` through `MINOR_PTR_UPDATE`, and from `MIDCMD_DATA0` through `MIDCMD_CNTL`.

## State And Persistence Behavior

The macros describe hardware register fields, not persistent software data. The state is volatile MMIO state owned by the SDMA engine and can be changed by driver writes, firmware/microcode, context switches, queue preemption, device reset, or power-management transitions.

Queue configuration and execution state lives in the `RB_*`, `IB_*`, `DOORBELL*`, `RB_AQL_CNTL`, and VMID/privilege fields. Context continuity is represented by `CSA_ADDR_*`, `IB_SUB_REMAIN`, `MIDCMD_DATA*`, and `MIDCMD_CNTL`. Diagnostic state is represented by `CONTEXT_STATUS`, `STATUS`, `DOORBELL_LOG`, and `WATERMARK`; those fields should be treated as hardware snapshots that may race with active queue execution.

MQD/HQD management in KFD persists selected queue values in software structures and restores them into these registers, but the header itself does not store anything. `MINOR_PTR_UPDATE` is a synchronization aid during pointer updates, especially for 64-bit pointer pairs where consuming a partially updated value would corrupt queue progress.

## Dependencies And Integration Points

- The companion address header `sdma3_4_2_2_offset.h` provides matching `mmSDMA3_RLC5_*`, `mmSDMA3_RLC6_*`, and `mmSDMA3_RLC7_*` register offsets. In that header, RLC6 starts at `mmSDMA3_RLC6_RB_CNTL` offset `0x0340` and RLC7 starts at `mmSDMA3_RLC7_RB_CNTL` offset `0x0398`.
- The broader SDMA 4.2.2 family includes matching `sdma0` through `sdma7` headers. Arcturus KFD code selects the engine base with `SOC15_REG_OFFSET(SDMA3, 0, mmSDMA3_RLC0_RB_CNTL)` and then applies queue spacing, so SDMA3 must match the common RLC queue layout.
- AMDGPU register helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` depend on the exact `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` naming convention used here.
- Doorbell integration depends on AMDGPU doorbell allocation and KFD user queues; incorrect `DOORBELL_OFFSET` or `ENABLE` values disconnect host submissions from the hardware queue.
- SDMA firmware/microcode and hardware context-switch logic consume the mid-command, preempt, IB, and CSA fields. These masks must match the ASIC register database, not merely the software naming pattern.

## Risks And Edge Cases

- Any wrong shift or mask silently targets the wrong hardware bits. Likely symptoms include SDMA queue hangs, missed doorbells, invalid VMID/privilege state, pointer corruption, failed preemption, or stuck non-idle queues.
- Address low-word masks encode alignment. Unaligned ring bases, writeback addresses, polling addresses, IB bases, or CSA addresses lose low bits and may redirect hardware memory accesses.
- RLC queue blocks are repetitive, making copy/paste or generation drift hard to spot. RLC6 and RLC7 should remain field-compatible with RLC0-RLC5 unless the hardware spec explicitly says otherwise.
- `CONTEXT_STATUS` and `STATUS` fields are live hardware state. Polling code needs timeouts, and diagnostic code should expect transient values.
- `RB_WPTR_POLL_CNTL` values affect dispatch latency, polling traffic, and SR-IOV behavior. Incorrect `F32_POLL_ENABLE`, frequency, or idle count can cause slow queue pickup or excessive polling.
- `MIDCMD_DATA*`, `MIDCMD_CNTL.DATA_VALID`, `SPLIT_STATE`, and `ALLOW_PREEMPT` are sensitive for mid-command preemption. Clearing or decoding them incorrectly can prevent a queue from resuming a split command.
- This is generated hardware-description material. Manual edits should be avoided unless regenerated from or checked against authoritative AMD register data.

## Test Signals

- Build coverage: `amdgpu/sdma_v4_0.c` and `amdgpu/amdgpu_amdkfd_arcturus.c` should compile with this header and the companion offset header included.
- Static header checks: every complete RLC6/RLC7 register field in this chunk should have paired `__SHIFT` and `_MASK` definitions, with no divergence from the equivalent RLC0-RLC5 field schema.
- Queue lifecycle tests: KFD SDMA queues on SDMA3 queue IDs 6 and 7 should load, become idle when disabled, restore ring pointers/base addresses/doorbells, and re-enable without timeout.
- Doorbell tests: host doorbell writes should advance queue WPTR state, avoid `DOORBELL_LOG.BE_ERROR`, and not leave `STATUS.WPTR_UPDATE_PENDING` stuck.
- Pointer/writeback tests: RPTR writeback should update the programmed memory address, and pointer restore should not regress when `MINOR_PTR_UPDATE` is toggled around low/high pointer writes.
- Preemption/context-switch tests: interrupted SDMA work should preserve `MIDCMD_DATA*`, `MIDCMD_CNTL.DATA_VALID`, `SPLIT_STATE`, and `IB_SUB_REMAIN` across suspend/resume or queue preemption.
- AQL tests: KFD/HSA SDMA AQL queues should validate `AQL_PACKET_SIZE` and `PACKET_STEP` programming for queues mapped to this RLC layout.

## Chunk Boundary Notes

This document covers only lines 2570-2956 of `sdma3_4_2_2_sh_mask.h`. The range begins after the RLC5 mid-command data registers, so it only contains `SDMA3_RLC5_MIDCMD_CNTL` for RLC5. It ends at the file's closing `#endif`, so RLC6 and RLC7 are complete within this chunk. Whole-file research should merge this with earlier chunks that cover SDMA3 global fields, GFX/PAGE queues, and RLC0-RLC5.
