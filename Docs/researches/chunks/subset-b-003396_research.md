# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma5/sdma5_4_2_2_sh_mask.h lines 1-2569

## Purpose

This chunk is the first 2569 lines of the generated AMD SDMA5 4.2.2 shift/mask header. It defines C preprocessor constants for SDMA5 register bit positions and masks under the `sdma5_sdma5dec` address block. The file is data, not executable code: there are no functions, structs, or control branches. Its purpose is to publish the ASIC register-field contract that AMDGPU and KFD code use with register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, and `SOC15_REG_GOLDEN_VALUE`.

The covered range includes the public SDMA5 registers, context/public register type bitmaps, MMHUB and virtualization fields, power and clock controls, status and error-reporting fields, UTCL1/XNACK/invalidation controls, performance counters, GPU IOV violation logs, complete GFX and PAGE queue-context schemas, complete RLC0 through RLC4 queue-context schemas, and most of the RLC5 queue-context schema. The chunk ends at `SDMA5_RLC5_MIDCMD_DATA8__DATA8_MASK`; `SDMA5_RLC5_MIDCMD_CNTL` starts on the next source line and is outside this work item.

## Important Macros And Register Fields

- Header guard: `_sdma5_4_2_2_SH_MASK_HEADER`.
- Public microcode and VM registers: `SDMA5_UCODE_ADDR`, `SDMA5_UCODE_DATA`, `SDMA5_VM_CNTL`, `SDMA5_VM_CTX_LO/HI`, `SDMA5_VM_CTX_CNTL`, `SDMA5_ACTIVE_FCN_ID`, `SDMA5_VIRT_RESET_REQ`, and `SDMA5_VF_ENABLE`.
- Context/public register type maps: `SDMA5_CONTEXT_REG_TYPE0` through `TYPE3` and `SDMA5_PUB_REG_TYPE0` through `TYPE3` are bitmaps that identify which SDMA context/public registers belong to each type class.
- Engine controls: `SDMA5_POWER_CNTL`, `SDMA5_CLK_CTRL`, `SDMA5_CNTL`, `SDMA5_CHICKEN_BITS`, `SDMA5_CHICKEN_BITS_2`, `SDMA5_GB_ADDR_CONFIG`, and `SDMA5_GB_ADDR_CONFIG_READ`.
- Status and diagnostics: `SDMA5_STATUS_REG`, `SDMA5_STATUS1_REG`, `SDMA5_STATUS2_REG`, `SDMA5_STATUS3_REG`, `SDMA5_ERROR_LOG`, `SDMA5_EDC_CONFIG`, `SDMA5_EDC_COUNTER`, `SDMA5_EDC_COUNTER_CLEAR`, `SDMA5_GPU_IOV_VIOLATION_LOG`, and `SDMA5_GPU_IOV_VIOLATION_LOG2`.
- Scheduling/preemption controls: `SDMA5_FREEZE`, `SDMA5_F32_CNTL`, `SDMA5_PHASE0_QUANTUM`, `SDMA5_PHASE1_QUANTUM`, `SDMA5_PHASE2_QUANTUM`, `SDMA5_UNBREAKABLE`, and per-context `*_PREEMPT`, `*_CONTEXT_STATUS`, and `*_MIDCMD_DATA*` fields.
- UTCL1 and address translation fields: `SDMA5_UTCL1_CNTL`, `SDMA5_UTCL1_WATERMK`, `SDMA5_UTCL1_RD_STATUS`, `SDMA5_UTCL1_WR_STATUS`, `SDMA5_UTCL1_INV0/1/2`, `SDMA5_UTCL1_RD_XNACK0/1`, `SDMA5_UTCL1_WR_XNACK0/1`, `SDMA5_UTCL1_TIMEOUT`, and `SDMA5_UTCL1_PAGE`.
- Ring/IB queue fields repeated across `GFX`, `PAGE`, and `RLC0` through `RLC5`: `RB_CNTL`, `RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, `RB_WPTR_HI`, `RB_WPTR_POLL_CNTL`, `RB_RPTR_ADDR_HI/LO`, `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO/HI`, `IB_SIZE`, `SKIP_CNTL`, `CONTEXT_STATUS`, `DOORBELL`, `STATUS`, `DOORBELL_LOG`, `WATERMARK`, `DOORBELL_OFFSET`, `CSA_ADDR_LO/HI`, `IB_SUB_REMAIN`, `PREEMPT`, `DUMMY_REG`, `RB_WPTR_POLL_ADDR_HI/LO`, `RB_AQL_CNTL`, `MINOR_PTR_UPDATE`, and `MIDCMD_DATA0` through `MIDCMD_DATA8`.
- The RLC5 block is partial in this chunk: it covers `RLC5_RB_CNTL` through `RLC5_MIDCMD_DATA8`; the associated `RLC5_MIDCMD_CNTL` field masks are outside lines 1-2569.

## Control Flow And Usage Model

The header has no runtime control flow. Its behavior is realized in callers that include this header together with `sdma5_4_2_2_offset.h` and use the generated names to compose MMIO values.

The typical runtime pattern is:

1. A caller identifies an SDMA engine and queue, then calculates a register offset from the companion `mmSDMA5_*` address macros.
2. The caller writes control registers using values assembled with `REG_SET_FIELD` and these `REG__FIELD__SHIFT`/`REG__FIELD_MASK` definitions.
3. The caller polls status fields such as `CONTEXT_STATUS.IDLE`, `STATUS.WPTR_UPDATE_PENDING`, or broader engine idle bits in `STATUS_REG`.
4. Context save, restore, dump, and preemption paths read or write contiguous queue-context ranges including ring pointers, doorbell state, CSA addresses, and mid-command data.

`amdgpu_amdkfd_arcturus.c` includes this SDMA5 header and its companion offset header. Its SDMA queue helper computes the SDMA5 engine base using `SOC15_REG_OFFSET(SDMA5, 0, mmSDMA5_RLC0_RB_CNTL) - mmSDMA5_RLC0_RB_CNTL`. The same file then manages SDMA queues through a generic RLC0-plus-offset addressing pattern, so the field schema in `SDMA5_RLC0_*` through `SDMA5_RLC5_*` must remain compatible with the corresponding offset layout even when the code uses RLC0 field names for multiple queues.

`sdma_v4_0.c` includes this header family for Arcturus/Aldebaran SDMA setup. In the golden settings table, SDMA5 participates in programming `mmSDMA5_CHICKEN_BITS`, `mmSDMA5_GB_ADDR_CONFIG`, `mmSDMA5_GB_ADDR_CONFIG_READ`, and `mmSDMA5_UTCL1_TIMEOUT`, tying this generated mask data to early engine configuration and known-good hardware workarounds.

## State And Persistence Behavior

The macros do not store state themselves. They describe volatile hardware state and configuration fields:

- Ring-buffer state is represented by base addresses, read/write pointers, read-pointer writeback addresses, pointer polling controls, VMID/privilege fields, and enable bits.
- IB state is represented by `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO/HI`, `IB_SIZE`, and `IB_SUB_REMAIN`.
- Doorbell state is represented by enable/captured bits, doorbell offsets, doorbell log data, and write-pointer update status.
- Preemption and context switching depend on `CONTEXT_STATUS`, `PREEMPT`, `CSA_ADDR_LO/HI`, `MINOR_PTR_UPDATE`, `MIDCMD_DATA0..8`, and, just outside this chunk for RLC5, `MIDCMD_CNTL`.
- Translation and memory-system state is exposed through UTCL1 invalidation, XNACK, timeout, page, watermark, and physical-address fields.
- Error and diagnostic state is exposed through EDC counters, status registers, GPU IOV violation logs, ULV status, performance counters, and dummy/scratch-style registers.

Persistence-like behavior is external to this header. Driver-managed MQD/HQD structures and hardware context-save areas preserve queue configuration across suspend, reset, preemption, or process eviction. The bit definitions here must match the hardware save/restore image; otherwise a restored queue can resume with corrupted pointers, stale doorbell state, wrong VMID, or invalid mid-command state.

## Dependencies And Integration Points

- Companion addresses: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma5/sdma5_4_2_2_offset.h` supplies the `mmSDMA5_*` register numbers that pair with these masks.
- AMDGPU register helpers depend on the exact generated naming convention: `REG_SET_FIELD(x, SDMA5_RLC5_RB_CNTL, RB_ENABLE, v)` expects `SDMA5_RLC5_RB_CNTL__RB_ENABLE_MASK` and `SDMA5_RLC5_RB_CNTL__RB_ENABLE__SHIFT`.
- `amdgpu_amdkfd_arcturus.c` includes the SDMA5 offset and mask headers for Arcturus KFD queue load/dump/is-occupied paths and for engine/queue offset computation.
- `sdma_v4_0.c` includes this header family for SDMA golden settings and ASIC initialization, including the SDMA5 `UTCL1_TIMEOUT` programming path.
- The same layout is mirrored across SDMA0 through SDMA7 4.2.2 headers. Cross-engine consistency matters because the KFD code selects an engine but often reuses RLC0 register names plus computed offsets.
- SDMA firmware and microcode consume the programmed queue and context fields; incorrect bit definitions can violate firmware-visible ABI expectations even if the C code compiles.

## Risks And Edge Cases

- Incorrect masks or shifts can silently program the wrong hardware bits. Likely symptoms include SDMA queue hangs, missing doorbells, failed preemption, invalid VMID/privilege selection, lost write-pointer updates, or data corruption.
- Many address fields intentionally mask low alignment bits: for example `RB_RPTR_ADDR_LO`, `IB_BASE_LO`, `CSA_ADDR_LO`, and `RB_WPTR_POLL_ADDR_LO`. Unaligned software addresses will be truncated by field construction.
- The queue-context blocks are highly repetitive. Copy/paste or generator errors between `GFX`, `PAGE`, and `RLC0` through `RLC5` can evade compile-time detection because the macro names still exist.
- The assigned chunk ends inside the RLC5 mid-command group. A consumer of this research should not infer that `RLC5_MIDCMD_CNTL` is covered here; it starts after line 2569.
- Status fields such as idle, pending, exception, XNACK, and violation bits are volatile hardware observations. Treating them as stable software state can race with the engine.
- Power, clock, ULV, relaxed-ordering, UTCL1 timeout, and chicken-bit fields affect low-level engine timing. Bad values may produce intermittent failures that only appear under load, virtualization, page faults, or power-state transitions.
- Generated register headers should generally be regenerated from AMD's authoritative register database rather than manually edited; local edits risk divergence from the companion offset headers and from other SDMA engine headers.

## Test Signals

- Compile coverage: AMDGPU/KFD builds should include `amdgpu_amdkfd_arcturus.c` and `sdma_v4_0.c` without missing `SDMA5_*` mask or shift definitions.
- Golden setting validation: Arcturus/Aldebaran initialization should write SDMA5 `CHICKEN_BITS`, `GB_ADDR_CONFIG`, `GB_ADDR_CONFIG_READ`, and `UTCL1_TIMEOUT` with expected masked values and no register programming warnings.
- SDMA queue restore tests: queue load should clear `RB_ENABLE`, observe `CONTEXT_STATUS.IDLE`, program doorbell and ring pointer state, toggle `MINOR_PTR_UPDATE`, then re-enable the ring without timeout.
- Doorbell tests: SDMA submissions should advance write pointers, avoid `DOORBELL_LOG.BE_ERROR`, and keep `STATUS.WPTR_UPDATE_PENDING` and `WPTR_UPDATE_FAIL_COUNT` bounded.
- Preemption/context-switch tests: interrupted SDMA work should preserve CSA addresses, `IB_SUB_REMAIN`, and `MIDCMD_DATA0..8` content across save/restore, with `MIDCMD_CNTL` checked by the following chunk.
- VM fault/XNACK tests: UTCL1 invalidation and XNACK status fields should decode correctly when page faults, VM holes, retry limits, or invalidate requests are exercised.
- Virtualization tests: VF/PF fields in `ACTIVE_FCN_ID`, `VIRT_RESET_REQ`, `VF_ENABLE`, and GPU IOV violation logs should identify the expected VFID and write/read operation on SR-IOV capable hardware.
- Register dump diagnostics: KFD SDMA dumps should traverse the RLC context ranges and decode values consistently with this header and the companion SDMA5 offset header.
