# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0/sdma0_4_2_sh_mask.h lines 2561-2992

## Purpose

This chunk is the tail of the generated AMD SDMA0 4.2 shift/mask header. It defines bitfield positions and masks for SDMA0 RLC queue-context registers, covering the end of RLC5 and the complete RLC6 and RLC7 blocks. The macros are not executable logic; they are the hardware contract used by AMDGPU/KFD code to compose, decode, dump, and restore SDMA queue registers through `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, and `WREG32`.

The covered register groups model per-queue SDMA state: ring-buffer base/read/write pointers, write-pointer polling, indirect-buffer state, context status, doorbell state, watermarks, context-save-area addresses, preemption state, AQL queue layout, minor pointer update control, and mid-command save/restore registers. RLC6 and RLC7 have the same field schema as the preceding RLC queues, letting driver code select a queue by adding a per-queue register offset to the RLC0 register numbers while still using the RLC0 masks for common fields.

## Important Macros And Register Fields

- `SDMA0_RLC5_*` in this slice starts at `DUMMY_REG`, then covers write-pointer poll addresses, AQL control, minor pointer update, `MIDCMD_DATA0` through `MIDCMD_DATA8`, and `MIDCMD_CNTL`.
- `SDMA0_RLC6_*` defines the full per-queue block: `RB_CNTL`, ring base/RPTR/WPTR registers, `RB_WPTR_POLL_CNTL`, writeback pointer address registers, `IB_*` registers, `SKIP_CNTL`, `CONTEXT_STATUS`, `DOORBELL`, `STATUS`, `DOORBELL_LOG`, `WATERMARK`, `DOORBELL_OFFSET`, `CSA_ADDR_*`, `IB_SUB_REMAIN`, `PREEMPT`, `DUMMY_REG`, polling address registers, `RB_AQL_CNTL`, `MINOR_PTR_UPDATE`, and mid-command data/control registers.
- `SDMA0_RLC7_*` repeats the same full per-queue schema for queue 7.
- `RB_CNTL` fields enable the ring and encode ring size, endian/swap behavior, read-pointer writeback, writeback timer, privileged mode, and VMID.
- Pointer/address fields are split into low/high 32-bit registers. Low address fields commonly start at bit 2 or bit 5 and mask alignment bits, for example `RB_RPTR_ADDR_LO__ADDR_MASK`, `CSA_ADDR_LO__ADDR_MASK`, and `IB_BASE_LO__ADDR_MASK`.
- `RB_WPTR_POLL_CNTL` controls firmware/hardware polling of a memory write pointer with `ENABLE`, `SWAP_ENABLE`, `F32_POLL_ENABLE`, `FREQUENCY`, and `IDLE_POLL_COUNT`.
- `CONTEXT_STATUS` exposes selected, idle, expired, exception, context-switch, preempted, and preempt-disable states.
- `DOORBELL` and `DOORBELL_OFFSET` encode whether doorbells are enabled/captured and where the queue doorbell is mapped.
- `STATUS` tracks write-pointer update failures and pending updates.
- `DOORBELL_LOG` records backend doorbell errors and the captured doorbell data.
- `WATERMARK` limits or reports read/write outstanding request levels.
- `PREEMPT` exposes `IB_PREEMPT`; `MIDCMD_CNTL` exposes `DATA_VALID`, `COPY_MODE`, `SPLIT_STATE`, and `ALLOW_PREEMPT`.
- `RB_AQL_CNTL` fields (`AQL_ENABLE`, `AQL_PACKET_SIZE`, `PACKET_STEP`) describe AQL packet interpretation for queues used by HSA/KFD style dispatch.

## Control Flow And Usage Model

This header has no branches or functions. The effective control flow happens in callers that combine these masks with the companion address header `sdma0_4_2_offset.h` and the MMIO helpers. The pattern in KFD SDMA code is:

1. Resolve a physical SDMA engine and queue to an RLC register offset.
2. Read or write `mmSDMA0_RLC0_* + sdma_rlc_reg_offset` rather than hardcoding each RLCn address.
3. Use the generated masks to set or test individual fields. For example, KFD restores an SDMA queue by clearing `RB_ENABLE`, polling `CONTEXT_STATUS.IDLE`, programming doorbell and ring pointers, temporarily enabling `MINOR_PTR_UPDATE`, and then setting `RB_ENABLE`.
4. Dump paths iterate contiguous register ranges, including `MIDCMD_DATA0` through `MIDCMD_CNTL`, to capture queue state for diagnostics or context save/restore.

Although this chunk names RLC5, RLC6, and RLC7 explicitly, the runtime code often uses the RLC0 register identifiers plus a computed offset. Therefore consistency between each RLCn mask block and the RLC0 mask block is important even when the RLCn symbols are not referenced directly.

## State And Persistence Behavior

The macros describe volatile hardware state, not persistent software state. Persistence-like behavior exists only through hardware context save/restore and driver-managed MQD state:

- Ring base, read/write pointers, writeback addresses, VMID, doorbell offset, and AQL controls determine the live queue execution state.
- `CSA_ADDR_LO/HI`, `IB_SUB_REMAIN`, `MIDCMD_DATA*`, and `MIDCMD_CNTL` support context save/restore and mid-command preemption, allowing a queue to resume after a world switch or preemption point.
- `MINOR_PTR_UPDATE` gates controlled pointer writes during restore, reducing the chance that partially updated 64-bit pointers are consumed by hardware.
- Status and log registers are diagnostic snapshots. They must be interpreted as hardware-latched or volatile values and should not be treated as stable configuration.

## Dependencies And Integration Points

- Depends on the companion offset headers, especially `sdma0_4_2_offset.h`, for the actual `mmSDMA0_RLC5_*`, `mmSDMA0_RLC6_*`, and `mmSDMA0_RLC7_*` register addresses.
- Integrates with AMDGPU register helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD`, which rely on the exact `REG__FIELD__SHIFT` and `REG__FIELD_MASK` naming convention.
- Integrates with KFD SDMA HQD/MQD management. The nearby driver pattern in `amdgpu_amdkfd_arcturus.c` uses analogous SDMA RLC masks to restore queues, test occupancy, and dump registers.
- Integrates with SDMA firmware and GPU microcode expectations. The driver-visible queue fields here must match the ASIC's SDMA0 4.2 register layout.
- Cross-version comparison with `sdma0_4_2_2_*` and older `sdma0_4_1_*` headers is relevant when adding ASIC support or backporting queue-management code because queue spacing and mid-command register addresses can differ even when field meanings are similar.

## Risks And Edge Cases

- Incorrect masks or shifts can silently program the wrong hardware bits, causing queue hangs, invalid VMID/privilege selection, missed doorbells, corrupted pointers, or failed preemption.
- Address low-word masks encode alignment requirements. Supplying unaligned ring, writeback, polling, IB, or CSA addresses will lose low bits and can redirect hardware accesses.
- RLC block repetition invites copy/paste errors. RLC5, RLC6, and RLC7 should remain schema-compatible with each other and with RLC0 unless the hardware specification explicitly differs.
- `RB_WPTR_POLL_CNTL` frequency and idle poll fields affect latency and power. Bad values can create slow dispatch pickup or excessive polling.
- `CONTEXT_STATUS` exception and preemption bits are status fields; using them as durable state can race with hardware updates.
- `MIDCMD_DATA*` and `MIDCMD_CNTL` are sensitive during preemption/world-switch flows. Clearing `DATA_VALID` or mismatching `SPLIT_STATE` can break command resumption.
- This file is generated hardware-description material. Manual edits risk diverging from AMD's register database and should be avoided unless regenerating or correcting from authoritative ASIC data.

## Test Signals

- Build coverage: the AMDGPU/KFD code that includes `sdma0_4_2_sh_mask.h` must compile cleanly, proving all referenced field macros still match the expected naming pattern.
- Queue restore/resume tests: SDMA queues should disable, reach `CONTEXT_STATUS.IDLE`, restore pointers and doorbell state, and re-enable without `WPTR_UPDATE_FAIL_COUNT` growth.
- Doorbell tests: queue submissions through doorbells should update WPTR state, avoid `DOORBELL_LOG.BE_ERROR`, and leave `STATUS.WPTR_UPDATE_PENDING` bounded.
- Preemption/context-switch tests: workloads interrupted mid-SDMA command should preserve `MIDCMD_DATA*`, `MIDCMD_CNTL.DATA_VALID`, `SPLIT_STATE`, and `ALLOW_PREEMPT` semantics across suspend/resume.
- AQL queue tests: KFD/HSA dispatch through SDMA-backed AQL queues should validate `AQL_PACKET_SIZE` and `PACKET_STEP` programming.
- Register dump diagnostics: dump output should include the contiguous ranges through `MINOR_PTR_UPDATE` and `MIDCMD_CNTL`, with values that decode according to these masks.
