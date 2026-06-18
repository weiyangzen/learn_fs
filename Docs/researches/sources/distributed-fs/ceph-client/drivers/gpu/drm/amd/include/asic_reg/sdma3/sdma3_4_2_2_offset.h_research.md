# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma3/sdma3_4_2_2_offset.h

## Purpose

`sdma3_4_2_2_offset.h` is a generated AMDGPU register-offset header for SDMA engine instance 3, hardware block `sdma3_sdma3dec`, with documented block base address `0x79000`. It exports C preprocessor constants named `mmSDMA3_*` plus matching `mmSDMA3_*_BASE_IDX` constants. Driver code uses these symbolic offsets to address the SDMA3 command processor, ring buffers, indirect buffers, page queue, RLC queues, virtualization controls, power controls, status registers, UTCL1 translation/cache registers, and diagnostic/performance registers.

This file contains no executable logic. Its value is as a hardware ABI map: the numeric offsets must match the SDMA 4.2.2 register layout for the SDMA3 instance. Consumers combine these offsets with SOC15 register-base tables or precomputed per-instance register bases before issuing MMIO reads/writes.

## Exported API Surface

The exported API is entirely macro based:

- Include guard: `_sdma3_4_2_2_OFFSET_HEADER`.
- Register offsets: `#define mmSDMA3_<REGISTER> 0x...`.
- Base-index selectors: `#define mmSDMA3_<REGISTER>_BASE_IDX 1`.

Important register families:

- Microcode and VM setup: `mmSDMA3_UCODE_ADDR`, `mmSDMA3_UCODE_DATA`, `mmSDMA3_UCODE_CHECKSUM`, `mmSDMA3_VM_CNTL`, `mmSDMA3_VM_CTX_LO`, `mmSDMA3_VM_CTX_HI`, `mmSDMA3_VM_CTX_CNTL`, `mmSDMA3_MMHUB_CNTL`.
- SR-IOV/virtualization controls: `mmSDMA3_ACTIVE_FCN_ID`, `mmSDMA3_VIRT_RESET_REQ`, `mmSDMA3_VF_ENABLE`, `mmSDMA3_GPU_IOV_VIOLATION_LOG`, `mmSDMA3_GPU_IOV_VIOLATION_LOG2`.
- Public/context register type bitmaps: `mmSDMA3_CONTEXT_REG_TYPE0` through `TYPE3`, and `mmSDMA3_PUB_REG_TYPE0` through `TYPE3`.
- Global control/status: `mmSDMA3_POWER_CNTL`, `mmSDMA3_POWER_CNTL_IDLE`, `mmSDMA3_CLK_CTRL`, `mmSDMA3_CNTL`, `mmSDMA3_STATUS_REG`, `mmSDMA3_STATUS1_REG`, `mmSDMA3_STATUS2_REG`, `mmSDMA3_STATUS3_REG`, `mmSDMA3_FREEZE`, `mmSDMA3_ERROR_LOG`, `mmSDMA3_VERSION`, `mmSDMA3_ID`.
- Memory/cache/translation controls: `mmSDMA3_GB_ADDR_CONFIG`, `mmSDMA3_GB_ADDR_CONFIG_READ`, `mmSDMA3_RD_BURST_CNTL`, `mmSDMA3_HBM_PAGE_CONFIG`, `mmSDMA3_UTCL1_CNTL`, `mmSDMA3_UTCL1_WATERMK`, `mmSDMA3_UTCL1_RD_STATUS`, `mmSDMA3_UTCL1_WR_STATUS`, `mmSDMA3_UTCL1_INV0` through `INV2`, `mmSDMA3_UTCL1_*_XNACK*`, `mmSDMA3_UTCL1_TIMEOUT`, `mmSDMA3_UTCL1_PAGE`.
- Atomic and ordering controls: `mmSDMA3_ATOMIC_CNTL`, `mmSDMA3_ATOMIC_PREOP_LO`, `mmSDMA3_ATOMIC_PREOP_HI`, `mmSDMA3_RELAX_ORDERING_LUT`.
- Diagnostics/performance/RAS-adjacent registers: `mmSDMA3_EDC_CONFIG`, `mmSDMA3_EDC_COUNTER`, `mmSDMA3_EDC_COUNTER_CLEAR`, `mmSDMA3_PERFMON_CNTL`, `mmSDMA3_PERFCOUNTER0_RESULT`, `mmSDMA3_PERFCOUNTER1_RESULT`, `mmSDMA3_PERFCOUNTER_TAG_DELAY_RANGE`, `mmSDMA3_F32_CNTL`, `mmSDMA3_F32_COUNTER`, `mmSDMA3_CRD_CNTL`, `mmSDMA3_ULV_CNTL`.
- GFX queue window: `mmSDMA3_GFX_RB_*`, `mmSDMA3_GFX_IB_*`, `mmSDMA3_GFX_DOORBELL*`, `mmSDMA3_GFX_STATUS`, `mmSDMA3_GFX_CSA_ADDR_*`, `mmSDMA3_GFX_PREEMPT`, `mmSDMA3_GFX_MIDCMD_DATA0` through `DATA8`, and `mmSDMA3_GFX_MIDCMD_CNTL`.
- PAGE queue window: the same ring, IB, doorbell, status, CSA, preempt, AQL, minor pointer, and mid-command shape under `mmSDMA3_PAGE_*`.
- RLC queue windows: eight repeated queue windows `mmSDMA3_RLC0_*` through `mmSDMA3_RLC7_*`. Each RLC queue exposes ring control/base/read/write pointer registers, write-pointer polling registers, IB registers, skip/context/doorbell/status registers, CSA address registers, preempt/dummy/AQL/minor pointer registers, and mid-command data/control registers.

The RLC register windows are regular: `RLC0_RB_CNTL` starts at `0x0130`, `RLC1_RB_CNTL` at `0x0188`, and each subsequent RLC queue advances by `0x58`. This fixed stride is relied on by queue-management code that computes per-queue offsets instead of switching over every register name.

## Control Flow

There is no runtime control flow in this header. At compile time, including C files receive integer constants. Runtime flow appears in consumers:

- `amdgpu/sdma_v4_0.c` includes this header next to the SDMA0, SDMA1, and SDMA2-7 offset/mask headers. Its `sdma_v4_0_get_reg_offset()` maps SDMA instance 3 to `adev->reg_offset[SDMA3_HWIP][0][1] + offset`; this matches the `_BASE_IDX 1` values in this header.
- `WREG32_SDMA(instance, offset, value)` and `RREG32_SDMA(instance, offset)` in `sdma_v4_0.c` pass offsets through `sdma_v4_0_get_reg_offset()` before MMIO access. Generic SDMA v4 code usually passes SDMA0-relative register names while selecting the instance dynamically, but golden settings and multi-engine support also include the SDMA3-specific symbols from this header.
- `amdgpu/amdgpu_amdkfd_arcturus.c` includes this header for Arcturus KFD queue management. Its `get_sdma_rlc_reg_offset()` handles `engine_id == 3` with `SOC15_REG_OFFSET(SDMA3, 0, mmSDMA3_RLC0_RB_CNTL) - mmSDMA3_RLC0_RB_CNTL`, then adds `queue_id * (mmSDMA0_RLC1_RB_CNTL - mmSDMA0_RLC0_RB_CNTL)` to locate a specific RLC queue window. That logic depends on SDMA3 RLC offsets matching the common SDMA queue stride.

## State and Persistence Behavior

The header itself has no storage, no mutable state, no static data, and no persistence behavior. State changes occur only when consumers use these offsets for hardware register access.

The mapped hardware registers represent volatile device state:

- Firmware load/programming state through `UCODE_ADDR`, `UCODE_DATA`, and `UCODE_CHECKSUM`.
- Ring and indirect-buffer state through `*_RB_BASE`, `*_RB_RPTR`, `*_RB_WPTR`, `*_IB_BASE_*`, `*_IB_SIZE`, and related control registers.
- Doorbell state through `*_DOORBELL`, `*_DOORBELL_OFFSET`, and `*_DOORBELL_LOG`.
- Context save/restore and queue scheduling state through context type registers, CSA address registers, `*_CONTEXT_STATUS`, `*_PREEMPT`, `*_AQL_CNTL`, `*_MINOR_PTR_UPDATE`, and mid-command registers.
- Error, status, EDC, and performance state through `STATUS*`, `ERROR_LOG`, `EDC_*`, and `PERF*` registers.

Persistence is hardware/driver controlled. Register contents may reset across GPU reset, suspend/resume, firmware reload, queue teardown, or ASIC power-gating events. Driver state is reconstructed by higher-level AMDGPU/KFD code using these addresses; this header only names the addresses.

## Dependencies

Direct dependencies are minimal:

- C preprocessor support for include guards and `#define`.
- The generated companion field header `sdma3_4_2_2_sh_mask.h`, which defines bit shifts and masks for fields in the registers named here.
- SOC15 AMDGPU register addressing infrastructure, including `SOC15_REG_OFFSET`, `SOC15_REG_ENTRY`, `SOC15_REG_GOLDEN_VALUE`, `RREG32`, `WREG32`, and `adev->reg_offset`.
- Sibling generated SDMA headers for instances 0-7, because common SDMA v4 code frequently calculates offsets by instance and assumes matching layouts/strides across engines.

No standard-library, kernel helper, or local type is declared by this file.

## Integration Points

Key integration points in this source tree are:

- `drivers/gpu/drm/amd/amdgpu/sdma_v4_0.c`: includes the header for SDMA v4 initialization, golden register settings, firmware loading, ring setup, queue pointer access, power management, RAS/EDC reads, and hang/status diagnostics. For instance 3, `sdma_v4_0_get_reg_offset()` adds the supplied offset to the SDMA3 hardware base indexed through `[0][1]`.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_arcturus.c`: includes the header for KFD SDMA queue load, dump, occupancy, and destroy paths on Arcturus. The SDMA3 RLC0 offset is used to derive an engine-specific base, while common RLC0-relative offsets are added to reach individual queue registers.
- `sdma3_4_2_2_sh_mask.h`: supplies field masks such as register `*_RB_ENABLE`, `*_IDLE`, context bitmap fields, and other bit definitions required to safely modify values at the offsets declared here.
- Generated GC register headers such as `gc_10_3_0_offset.h` can also define SDMA3 names with different offsets/base indexes for a different address namespace. Include ordering and ASIC selection must ensure code uses the register map matching the targeted GPU generation.

## Risks and Failure Modes

- Wrong offset values can cause writes to the wrong MMIO register, which can break firmware loading, ring initialization, queue scheduling, doorbell handling, power management, or GPU reset recovery.
- `_BASE_IDX` mismatches are high risk. This file consistently uses base index `1`; consumers such as `sdma_v4_0_get_reg_offset()` select SDMA3 via `adev->reg_offset[SDMA3_HWIP][0][1]`. A mismatch would shift all accesses into the wrong register segment.
- RLC queue stride assumptions are implicit. KFD code derives `RLCn` windows by adding a stride computed from RLC0/RLC1 offsets. If the generated RLC offsets ever stop being regular, queue load/dump/destroy paths would address incorrect queue state.
- Cross-instance copy/paste errors are plausible because SDMA0-7 headers are nearly identical except for instance prefix, base address/index, and some generation-specific offsets. The suspicious pattern in `sdma_v4_0.c` golden settings where an SDMA3 row uses `mmSDMA2_UTCL1_TIMEOUT` illustrates why generated offset headers and consumers need compile-time and runtime validation.
- These constants are tightly bound to ASIC generation. Reusing this header for a different SDMA generation or GC namespace can silently program wrong registers even though the code compiles.
- This header provides offsets only, not field masks. Using raw values without the companion `_sh_mask.h` masks can clobber reserved bits or unrelated fields.

## Test and Validation Signals

Useful signals for validating this header and its consumers:

- Build coverage for AMDGPU with Arcturus/SDMA v4.2.2 support enabled. Missing or renamed macros should fail compilation in `sdma_v4_0.c` or `amdgpu_amdkfd_arcturus.c`.
- Static consistency checks between this file and `sdma3_4_2_2_sh_mask.h`: every offset macro used as a register should have corresponding field definitions where fields are expected, and no field header should refer to non-existent registers.
- Register-map consistency checks across SDMA instances 2-7: common queues should preserve the same relative layout and `0x58` RLC queue stride.
- Runtime boot/probe logs on matching hardware should show successful SDMA firmware load, valid SDMA status reads, and no MMIO faults or timeout loops in SDMA init.
- Ring tests should exercise GFX and PAGE queue setup: writes to `RB_BASE`, `RB_RPTR/WPTR`, `RB_WPTR_POLL_ADDR`, `DOORBELL`, and `IB_CNTL` should result in command completion.
- KFD queue tests on Arcturus should exercise `kgd_arcturus_hqd_sdma_load()`, dump, occupancy, and destroy paths for `engine_id == 3` and multiple `queue_id` values. Failures would likely appear as queue idle timeouts, non-advancing write/read pointers, or incorrect HQD dumps.
- RAS/EDC diagnostic tests should read `EDC_COUNTER`, clear counters through `EDC_COUNTER_CLEAR`, and confirm expected interrupt/error-reporting behavior.
- Suspend/resume, GPU reset, and SR-IOV/VF scenarios should validate that SDMA3 registers are restored and that virtualization-related registers do not report unexpected violations.
