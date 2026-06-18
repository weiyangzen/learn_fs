# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma5/sdma5_4_2_2_offset.h

## Purpose

This generated AMDGPU register header defines the SDMA5 instance register offsets for the SDMA 5.4.2.2 register block. It is a pure preprocessor map: each `mmSDMA5_*` macro names a 32-bit MMIO register offset relative to the SDMA5 hardware IP base, and each matching `mmSDMA5_*_BASE_IDX` macro selects the register base segment index used by SOC15 addressing helpers. The file is protected by `_sdma5_4_2_2_OFFSET_HEADER` and contains no executable C functions, structs, or storage.

The declared address block is `sdma5_sdma5dec` with a documented base address of `0x7b000`. In driver code, these raw offsets are combined with runtime IP base data from `adev->reg_offset[SDMA5_HWIP]` through SOC15 helpers, so the values here are one layer of the hardware address contract rather than standalone CPU virtual addresses.

## Important API Surface

The exported API is the macro namespace itself:

- Global SDMA5 engine registers begin at `0x0000`, including firmware upload/checksum (`mmSDMA5_UCODE_ADDR`, `mmSDMA5_UCODE_DATA`, `mmSDMA5_UCODE_CHECKSUM`), VM context selection (`mmSDMA5_VM_CNTL`, `mmSDMA5_VM_CTX_LO`, `mmSDMA5_VM_CTX_HI`, `mmSDMA5_VM_CTX_CNTL`), virtualization controls (`mmSDMA5_ACTIVE_FCN_ID`, `mmSDMA5_VIRT_RESET_REQ`, `mmSDMA5_VF_ENABLE`, `mmSDMA5_GPU_IOV_VIOLATION_LOG`, `mmSDMA5_GPU_IOV_VIOLATION_LOG2`), power/clock/control registers (`mmSDMA5_POWER_CNTL`, `mmSDMA5_POWER_CNTL_IDLE`, `mmSDMA5_CLK_CTRL`, `mmSDMA5_CNTL`, `mmSDMA5_FREEZE`), status and error registers (`mmSDMA5_STATUS_REG`, `mmSDMA5_STATUS1_REG`, `mmSDMA5_STATUS2_REG`, `mmSDMA5_STATUS3_REG`, `mmSDMA5_ERROR_LOG`), EDC/RAS counters (`mmSDMA5_EDC_CONFIG`, `mmSDMA5_EDC_COUNTER`, `mmSDMA5_EDC_COUNTER_CLEAR`), UTCL1 translation/cache status and invalidation registers (`mmSDMA5_UTCL1_*`), performance counters (`mmSDMA5_PERFMON_CNTL`, `mmSDMA5_PERFCOUNTER0_RESULT`, `mmSDMA5_PERFCOUNTER1_RESULT`, `mmSDMA5_PERFCOUNTER_TAG_DELAY_RANGE`), and memory/GB configuration (`mmSDMA5_GB_ADDR_CONFIG`, `mmSDMA5_GB_ADDR_CONFIG_READ`, `mmSDMA5_MMHUB_CNTL`).
- Queue/context register groups expose repeated ring buffer, indirect buffer, doorbell, context-save, preemption, watermark, AQL, minor pointer, and mid-command registers.
- The non-RLC queues are `GFX` from `0x0080` through `0x00c9` and `PAGE` from `0x00d8` through `0x0121`.
- The compute/RLC queue groups `RLC0` through `RLC7` each expose the same 42 logical offsets. `RLC0_RB_CNTL` starts at `0x0130`; each subsequent RLC queue starts `0x58` dwords later, ending with `RLC7_MIDCMD_CNTL` at `0x03e1`.
- The file contains 507 `mmSDMA5_*` register-offset macros and a corresponding `*_BASE_IDX` macro for each offset. All base index values in this file are `1`.

There are no C types or functions here. Bit-level field names, shifts, and masks are deliberately split into the companion `sdma5_4_2_2_sh_mask.h`; consumers must include both files when they need to write fields instead of whole registers.

## Control Flow

This header has no runtime control flow. Its control effect is compile-time substitution into AMDGPU register access paths:

- `SOC15_REG_OFFSET(SDMA5, 0, mmSDMA5_...)` expands an SDMA5 offset into an absolute register index using IP discovery/base tables.
- `SOC15_REG_GOLDEN_VALUE(SDMA5, 0, mmSDMA5_..., mask, value)` uses these offsets to build golden-register initialization tables.
- Direct MMIO helpers such as `RREG32()` and `WREG32()` receive offsets derived from these macros and then perform hardware reads/writes.

The most visible integration path is `amdgpu_amdkfd_arcturus.c`, where `get_sdma_rlc_reg_offset()` handles SDMA engine selection. For engine 5 it computes an SDMA5 RLC base with `SOC15_REG_OFFSET(SDMA5, 0, mmSDMA5_RLC0_RB_CNTL) - mmSDMA5_RLC0_RB_CNTL`, then queue-specific code adds the generic RLC register offsets used by KFD SDMA queue load/dump operations. `sdma_v4_0.c` also maps instance 5 through `sdma_v4_0_get_reg_offset()`, returning `adev->reg_offset[SDMA5_HWIP][0][1] + offset`.

## State and Persistence Behavior

The file itself holds no mutable state and performs no persistence. The constants address stateful hardware registers whose contents persist according to GPU reset, power, firmware, and queue lifecycle rules:

- Ring buffer registers hold queue base addresses and read/write pointers.
- Indirect-buffer registers hold IB base, size, offset, and read-pointer state.
- Doorbell and polling registers tie software queue submissions to hardware wakeups.
- Context, CSA, preempt, and mid-command registers carry queue execution state used during scheduling, preemption, and reset recovery.
- EDC, error, status, and performance registers expose hardware-observed state and counters.

Because these offsets are compiled into the kernel module, changing them changes which hardware state AMDGPU reads or writes. A wrong value can silently target an unrelated register while still compiling cleanly.

## Dependencies

Direct dependencies are minimal:

- Standard C preprocessor support for include guards and `#define`.
- The AMDGPU SOC15 register-addressing model, especially `SDMA5_HWIP`, `SOC15_REG_OFFSET`, `SOC15_REG_GOLDEN_VALUE`, `RREG32`, and `WREG32`.
- Runtime base-offset tables in `struct amdgpu_device`, populated from the ASIC/IP offset headers such as `arct_ip_offset.h`.
- Companion generated register field definitions in `sdma5_4_2_2_sh_mask.h`.
- Sibling SDMA instance headers (`sdma0` through `sdma7`) that keep the same layout with instance-specific prefixes.

The source uses the MIT-style AMD license block and appears generated from hardware register descriptions rather than hand-maintained logic.

## Integration Points

Primary integration points in this tree are:

- `drivers/gpu/drm/amd/amdgpu/sdma_v4_0.c`: includes the SDMA5 offset and mask headers, uses `mmSDMA5_CHICKEN_BITS`, `mmSDMA5_GB_ADDR_CONFIG`, `mmSDMA5_GB_ADDR_CONFIG_READ`, and `mmSDMA5_UTCL1_TIMEOUT` in Arcturus golden-register tables, and maps SDMA instance 5 to `adev->reg_offset[SDMA5_HWIP][0][1] + offset`.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_arcturus.c`: includes all SDMA 4.2.2 instance headers and uses `mmSDMA5_RLC0_RB_CNTL` when computing the base for SDMA5 RLC queue registers for KFD/HSA queue management.
- `drivers/gpu/drm/amd/include/arct_ip_offset.h`: provides the SDMA5 hardware IP base segments used at runtime by SOC15 register offset resolution.
- `drivers/gpu/drm/amd/include/asic_reg/sdma5/sdma5_4_2_2_sh_mask.h`: supplies field masks and shifts for the registers whose offsets are declared here.

The repeated queue layout also supports generic queue code that uses SDMA0 offsets as a canonical intra-block layout after computing an instance-specific base. That makes layout consistency between SDMA0 and SDMA5 headers an integration requirement.

## Risks and Edge Cases

- Offset drift versus hardware specification is the main risk. The compiler cannot detect a register offset that still has the right type and name but addresses the wrong dword.
- The `*_BASE_IDX` value is uniformly `1`; consumers that choose base segment `0` for SDMA5 would address the wrong aperture on ASICs whose SDMA5 base lives in segment 1.
- RLC queue code assumes equal spacing between RLC queues. In this header the stride from `RLC0_RB_CNTL` to `RLC1_RB_CNTL` is `0x58`, repeated through `RLC7`; a future generated layout change would require matching changes in generic queue-offset arithmetic.
- The SDMA5 namespace is instance-specific. Accidentally mixing `mmSDMA5_*` offsets with `SDMA0_HWIP` bases, or `mmSDMA0_*` offsets with an SDMA5 base when layouts diverge, can produce hard-to-debug MMIO corruption.
- Public, context, virtualization, and RAS register offsets are security and reliability sensitive because KFD, SR-IOV, reset, and error-handling paths may rely on them during fault recovery.
- Since this is generated code, manual local edits risk being overwritten or desynchronizing from sibling SDMA instance headers and the companion mask header.

## Test Signals

Useful validation signals for this file are mostly integration and hardware-facing:

- Build coverage for AMDGPU with Arcturus/Aldebaran SDMA support catches missing or renamed macros.
- Static checks can compare the RLC queue stride across `RLC0` through `RLC7`, verify each offset has a matching `_BASE_IDX`, and compare SDMA5 layout against sibling SDMA instance headers expected to share the 4.2.2 layout.
- Driver init logs and golden-register programming on Arcturus-class GPUs should show successful SDMA initialization without MMIO access faults.
- KFD SDMA queue tests should be able to create, load, suspend, resume, and destroy SDMA queues on engine 5 without timeout in context-idle polling.
- Ring submission tests should observe advancing RB/IB pointers and doorbell behavior for SDMA5 queues.
- RAS/error injection or diagnostic reads should report plausible `EDC_COUNTER`, `STATUS*`, `ERROR_LOG`, and UTCL1 status values rather than all-zero, all-one, or bus-error patterns.
- Suspend/resume and GPU reset tests are important because queue context, CSA, preemption, and mid-command registers are read or restored around recovery paths.
