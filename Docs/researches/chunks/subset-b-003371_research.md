# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_2_sh_mask.h lines 2530-3300

## Purpose

This chunk is the tail of the generated SDMA 4.4.2 shift/mask header. It defines C preprocessor constants for bit shifts and masks used to program SDMA RLC queue registers, specifically the end of `SDMA_RLC4_RB_CNTL`, the full RLC5 and RLC6 register-field sets, and the full RLC7 set through `SDMA_RLC7_MIDCMD_CNTL`, followed by the header guard close.

The values are hardware ABI data rather than executable logic. Driver code combines these masks with matching register offsets from `sdma_4_4_2_offset.h` and helper macros such as `REG_SET_FIELD()` / `REG_GET_FIELD()` to configure and inspect SDMA queues without hard-coding bit positions at each call site.

## Important Definitions

The chunk repeats the same register-field pattern for RLC queue instances 4 through 7:

- Ring buffer control and pointer state:
  `SDMA_RLCx_RB_CNTL`, `RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, `RB_WPTR_HI`.
  The control fields include `RB_ENABLE`, `RB_SIZE`, byte-swap enable, read-pointer writeback enable/swap/timer, `RB_PRIV`, and `RB_VMID`.
- Write-pointer polling and read-pointer writeback:
  `RB_WPTR_POLL_CNTL`, `RB_WPTR_POLL_ADDR_HI`, `RB_WPTR_POLL_ADDR_LO`, `RB_RPTR_ADDR_HI`, and `RB_RPTR_ADDR_LO`.
  These encode enable bits, polling frequency, idle poll count, alignment-constrained addresses, and `RPTR_WB_IDLE`.
- Indirect buffer execution:
  `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO`, `IB_BASE_HI`, `IB_SIZE`, and `IB_SUB_REMAIN`.
  Important fields include `IB_ENABLE`, `IB_SWAP_ENABLE`, `SWITCH_INSIDE_IB`, command VMID, privilege, aligned IB base, and remaining IB size.
- Queue scheduling/status:
  `SKIP_CNTL`, `CONTEXT_STATUS`, `PREEMPT`, `MINOR_PTR_UPDATE`, and `DUMMY_REG`.
  `CONTEXT_STATUS` exposes `SELECTED`, `IDLE`, `EXPIRED`, `EXCEPTION`, `CTXSW_ABLE`, `CTXSW_READY`, `PREEMPTED`, and `PREEMPT_DISABLE`.
- Doorbells and diagnostics:
  `DOORBELL`, `STATUS`, `DOORBELL_LOG`, `WATERMARK`, and `DOORBELL_OFFSET`.
  These cover doorbell enable/captured state, write-pointer update failure/pending state, logged backend error/data, outstanding read/write watermarks, and the queue doorbell aperture offset.
- AQL and mid-command state:
  `RB_AQL_CNTL`, `MIDCMD_DATA0` through `MIDCMD_DATA10`, and `MIDCMD_CNTL`.
  These fields describe AQL packet sizing/step and a saved or inspected in-flight command payload with `DATA_VALID`, `COPY_MODE`, `SPLIT_STATE`, and `ALLOW_PREEMPT`.

The masks are consistent across RLC5, RLC6, and RLC7, and match the earlier RLC0-RLC4 pattern in the same header. Line 2530 starts after the first several `SDMA_RLC4_RB_CNTL` shift/mask definitions, so the chunk contains only the final `RB_PRIV` and `RB_VMID` masks for that register before continuing with the rest of RLC4.

## Control Flow

There is no runtime control flow in this header. The operational flow appears in consumers:

1. SDMA/KFD code includes `sdma_4_4_2_offset.h` and this mask header.
2. It computes an SDMA engine or RLC queue register address using the offset constants.
3. It reads or writes the register with `RREG32()` / `WREG32()` or SDMA instance wrappers.
4. It uses the shift/mask constants through field helpers, or directly tests masks, to enable queues, poll idle state, configure doorbells, dump state, or restore MQD contents.

`amdgpu_amdkfd_gc_9_4_3.c` demonstrates the intended RLC queue model. It computes a per-queue RLC base from `regSDMA_RLC0_RB_CNTL` and the stride to `regSDMA_RLC1_RB_CNTL`, then addresses any queue by adding `queue_id * stride`. That means the repeated RLC4-RLC7 definitions in this chunk must remain layout-compatible with RLC0/RLC1 because queue code can address later queues using the same register layout and field semantics.

## State and Persistence Behavior

The constants describe hardware state, not stored software state. The relevant persistent or recoverable state lives in SDMA hardware registers and MQD snapshots:

- Ring base, read/write pointers, writeback addresses, doorbell offset, and `RB_CNTL` persist in hardware while the queue is active.
- KFD queue load writes an MQD's SDMA RLC fields into the hardware queue registers, disables `RB_ENABLE` while waiting for `CONTEXT_STATUS.IDLE`, programs doorbell/pointers/base/writeback addresses, then enables the ring.
- Queue destroy disables the ring, waits for `CONTEXT_STATUS.IDLE`, disables the doorbell, and records the current read pointer back into the MQD-like software structure.
- Queue dump reads contiguous RLC register ranges, including the mid-command data/control area described in this chunk, so user/debug tooling can inspect live or suspended SDMA queue state.

The header itself has no allocation, locking, I/O, or persistence code. Correctness depends on the constants matching the hardware register layout exactly.

## Dependencies and Integration Points

- Paired offset header: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_2_offset.h` provides `regSDMA_RLC4_*` through `regSDMA_RLC7_*` addresses that correspond to these field masks.
- Main SDMA implementation: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_4_2.c` includes this header and the offset header for SDMA 4.4.2/4.4.4/4.4.5 register programming and register dumps.
- KFD GC 9.4.3 integration: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gc_9_4_3.c` includes the same headers and uses RLC register offsets/masks to load, destroy, inspect, and report SDMA HQD state.
- Common AMDGPU register helpers: `REG_SET_FIELD()` and `REG_GET_FIELD()` depend on the naming convention `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`. Any rename or inconsistent field name breaks these macro expansions.
- Hardware-visible ABI: firmware, kernel SDMA setup, KFD MQD handling, doorbell routing, and debug register dumps all assume these definitions match SDMA 4.4.2 silicon.

## Risks

- A single incorrect mask or shift can silently program the wrong bit in a memory-mapped hardware register, causing queue hangs, missed doorbells, invalid VMID/privilege selection, broken writeback, or failed preemption.
- The chunk is repetitive and generated-style; manual edits are high risk because RLC4-RLC7 must remain stride-compatible and field-compatible with RLC0-RLC3.
- Alignment masks such as `*_ADDR_MASK` encode hardware alignment requirements. Incorrect low-bit masks can point hardware at invalid ring, IB, writeback, or doorbell memory.
- `CONTEXT_STATUS` masks are used in timeout loops. Wrong `IDLE` or `SELECTED` values can create false readiness, timeout failures, or incorrect active-doorbell reporting.
- Doorbell masks and offsets are security-sensitive in multi-process/KFD use because they control how user queues signal hardware.
- This file is included in kernel C translation units; malformed macro names, missing `L` suffixes where expected, or guard damage can cause broad build failures in AMDGPU code.

## Test Signals

- Kernel build coverage for AMDGPU with SDMA 4.4.2/GC 9.4.3 enabled validates macro names and include integration.
- Static compile checks around `REG_SET_FIELD()` / `REG_GET_FIELD()` users catch missing or renamed field macros.
- Runtime SDMA ring tests should confirm queue initialization, ring pointer movement, writeback, doorbell signaling, and IB execution.
- KFD SDMA queue tests should cover HQD load/destroy/dump, doorbell offset reporting, MQD restoration, and multi-queue operation using queue ids that map beyond RLC0/RLC1.
- GPU reset, suspend/resume, and preemption tests are useful signals because this chunk includes context status, preempt, and mid-command state fields.
- Debug register dump comparison against expected SDMA 4.4.2 register layouts can catch offset/mask drift for RLC4-RLC7.
