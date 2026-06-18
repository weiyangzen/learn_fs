# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma4/sdma4_4_2_2_offset.h

## Purpose

`sdma4_4_2_2_offset.h` is a generated AMDGPU ASIC register offset header for the SDMA4 block in the SDMA 4.2.2 register family. It has no executable code; it defines preprocessor constants that name memory-mapped SDMA4 registers and their SOC15 base-index selectors. The block comment identifies the address block as `sdma4_sdma4dec` with a hardware base address of `0x7a000`, while the actual driver-facing register addresses are formed by combining these relative offsets with per-ASIC IP base tables such as `SDMA4_BASE`.

The file exposes 507 logical SDMA4 register offsets, each paired with a `_BASE_IDX` macro, for 1,014 `mmSDMA4_*` definitions total. The offsets run from `mmSDMA4_UCODE_ADDR` at `0x0000` through `mmSDMA4_RLC7_MIDCMD_CNTL` at `0x03e1`. Every `_BASE_IDX` in this file is `1`, so consumers expect the SDMA4 register window used by this ASIC generation to be selected from base segment index 1 unless a helper deliberately uses another segment.

## Important APIs, Types, and Macro Families

This header exports macros rather than C APIs or types. The important API surface is the register naming contract consumed by SOC15 register helpers.

- Core SDMA engine control registers include `mmSDMA4_UCODE_ADDR`, `mmSDMA4_UCODE_DATA`, `mmSDMA4_VM_CNTL`, `mmSDMA4_MMHUB_CNTL`, `mmSDMA4_POWER_CNTL`, `mmSDMA4_CLK_CTRL`, `mmSDMA4_CNTL`, `mmSDMA4_CHICKEN_BITS`, `mmSDMA4_GB_ADDR_CONFIG`, `mmSDMA4_RD_BURST_CNTL`, and `mmSDMA4_UTCL1_*`.
- Status, diagnostics, and reliability registers include `mmSDMA4_STATUS_REG`, `mmSDMA4_STATUS1_REG`, `mmSDMA4_STATUS2_REG`, `mmSDMA4_STATUS3_REG`, `mmSDMA4_UCODE_CHECKSUM`, `mmSDMA4_EDC_CONFIG`, `mmSDMA4_EDC_COUNTER`, `mmSDMA4_EDC_COUNTER_CLEAR`, `mmSDMA4_ERROR_LOG`, `mmSDMA4_GPU_IOV_VIOLATION_LOG`, and performance counter registers.
- Queue and command processor register groups are repeated for `GFX`, `PAGE`, and `RLC0` through `RLC7`. Each group has ring-buffer control/base/read-pointer/write-pointer registers, indirect-buffer registers, doorbell registers, status/context registers, preemption registers, AQL controls, minor pointer update controls, and mid-command capture registers.
- The companion `sdma4_4_2_2_sh_mask.h` supplies bit shift and mask definitions for the same register names. This offset file only names register addresses; field layout must come from the sh/mask header.
- The `_BASE_IDX` macros are part of the SOC15 register-access ABI. Macros such as `SOC15_REG_OFFSET`, `SOC15_REG_GOLDEN_VALUE`, `SOC15_REG_ENTRY`, `RREG32`, and `WREG32` combine a hardware IP block, instance, base index, and register offset to reach the final MMIO address.

## Control Flow

There is no runtime control flow in this header. Its values affect driver control flow indirectly when SDMA code resolves and accesses MMIO registers.

The main access path is:

1. ASIC-specific initialization, such as `arct_reg_base_init()` and `aldebaran_reg_base_init()`, stores `SDMA4_BASE.instance[i]` into `adev->reg_offset[SDMA4_HWIP][i]`.
2. SDMA v4 code includes this header in `amdgpu/sdma_v4_0.c` and uses `mmSDMA4_*` constants in golden register tables and register-offset helpers.
3. For SDMA instance 4, `sdma_v4_0_get_reg_offset()` returns `adev->reg_offset[SDMA4_HWIP][0][1] + offset`, matching this header's base-index-1 convention.
4. Register helpers then perform actual reads and writes using computed addresses.

The KFD Arcturus path includes this header in `amdgpu/amdgpu_amdkfd_arcturus.c`. `get_sdma_rlc_reg_offset()` computes the base for engine 4 as `SOC15_REG_OFFSET(SDMA4, 0, mmSDMA4_RLC0_RB_CNTL) - mmSDMA4_RLC0_RB_CNTL`, then derives per-queue RLC offsets by adding `queue_id * (mmSDMA0_RLC1_RB_CNTL - mmSDMA0_RLC0_RB_CNTL)`. That computation relies on the SDMA4 RLC queue layout matching the other SDMA engines.

## State and Persistence Behavior

The header itself stores no state and persists nothing. It describes hardware state surfaces: firmware upload ports, VM context registers, ring buffer pointers, indirect buffer pointers, doorbell state, queue context status, performance counters, error counters, and virtualization-related status. State persistence happens in hardware registers, firmware-controlled SDMA queues, and driver-owned memory such as MQDs and ring buffers.

Several macro groups identify state that survives across command submission boundaries until reset, reprogramming, or hardware update:

- Ring buffer state is represented by `*_RB_BASE`, `*_RB_BASE_HI`, `*_RB_RPTR`, `*_RB_RPTR_HI`, `*_RB_WPTR`, `*_RB_WPTR_HI`, and `*_RB_RPTR_ADDR_*`.
- Indirect buffer execution state is represented by `*_IB_CNTL`, `*_IB_RPTR`, `*_IB_OFFSET`, `*_IB_BASE_LO`, `*_IB_BASE_HI`, `*_IB_SIZE`, and `*_IB_SUB_REMAIN`.
- Doorbell and polling state is represented by `*_DOORBELL`, `*_DOORBELL_LOG`, `*_DOORBELL_OFFSET`, `*_RB_WPTR_POLL_CNTL`, and `*_RB_WPTR_POLL_ADDR_*`.
- Reliability and observability state is represented by `EDC`, `STATUS`, `ERROR_LOG`, `PERFCOUNTER`, `GPU_IOV_VIOLATION_LOG`, and UTCL1 status registers.

Because these are MMIO addresses, any offset error can mutate persistent hardware state outside normal C type checking.

## Dependencies

This header depends on the AMDGPU SOC15 register access model:

- `SDMA4_HWIP` from the AMDGPU hardware IP enumeration indexes the device's `reg_offset` table.
- `SDMA4_BASE` from ASIC IP offset headers such as `arct_ip_offset.h` and `aldebaran_ip_offset.h` supplies per-instance base segments.
- `soc15.h` and related SOC15 helpers use `mmSDMA4_*` and `_BASE_IDX` macros to compute final register addresses.
- `sdma4_4_2_2_sh_mask.h` provides field-level masks for safe read-modify-write operations against the offsets in this file.
- Peer headers for `sdma0` through `sdma7` define equivalent layouts for other SDMA engines. Several integration paths assume these layouts remain isomorphic.

## Integration Points

Direct observed consumers include:

- `amdgpu/sdma_v4_0.c`, which includes this header and uses `mmSDMA4_CHICKEN_BITS`, `mmSDMA4_GB_ADDR_CONFIG`, `mmSDMA4_GB_ADDR_CONFIG_READ`, and `mmSDMA4_UTCL1_TIMEOUT` in Arcturus and Aldebaran golden settings. It also resolves SDMA instance 4 via `adev->reg_offset[SDMA4_HWIP][0][1] + offset`.
- `amdgpu/amdgpu_amdkfd_arcturus.c`, which includes this header for KFD SDMA queue programming on Arcturus. Engine 4 base computation uses `mmSDMA4_RLC0_RB_CNTL`.
- `amdgpu/arct_reg_init.c` and `amdgpu/aldebaran_reg_init.c`, which populate `adev->reg_offset[SDMA4_HWIP]` from `SDMA4_BASE`.
- `amdgpu/amdgpu_dev_coredump.c`, which labels `SDMA4_HWIP` as `SDMA4` for dump output, making correct register naming important for diagnostics.

At the subsystem level, the header bridges generated hardware register specifications to SDMA firmware loading, queue setup, KFD compute queue management, golden register programming, reset/recovery diagnostics, and RAS/performance observability.

## Risks

- Offset drift is high impact. A wrong `mmSDMA4_*` value can cause the driver to program the wrong MMIO register, potentially corrupting queue state, disabling a block, breaking doorbells, or masking hardware errors.
- Base-index mismatch is subtle. This file's `_BASE_IDX` values are all `1`, and `sdma_v4_0_get_reg_offset()` uses segment `[1]` for SDMA instances 2 through 7. A consumer using segment `[0]` for SDMA4 with these offsets may address the wrong register aperture.
- Cross-engine layout assumptions are embedded in KFD. `get_sdma_rlc_reg_offset()` calculates SDMA4's engine base with `mmSDMA4_RLC0_RB_CNTL` but computes queue stride using SDMA0 constants. That is valid only if all SDMA 4.2.2 engine RLC queue blocks have identical spacing.
- Generated header edits are risky. Manual changes can desynchronize offsets from the companion sh/mask header, ASIC IP base tables, and firmware expectations.
- Queue group repetition increases copy/paste risk. `GFX`, `PAGE`, and eight `RLC` blocks have near-identical register sets with different offsets; missing one queue or misnumbering a queue can create failures that only appear under multi-queue KFD workloads.
- The file has no compile-time range checks. Macro use compiles even if a register is not valid for a specific ASIC stepping; validation must come from matching the generated register package to the ASIC version.

## Test Signals

Useful validation signals for this header are integration and hardware-facing rather than unit-level:

- Build coverage for AMDGPU with Arcturus/Aldebaran SDMA paths enabled catches missing or renamed macros in `sdma_v4_0.c` and `amdgpu_amdkfd_arcturus.c`.
- Golden register programming should complete without MMIO faults or timeout warnings on ASICs that expose SDMA4.
- SDMA firmware loading and checksum/status registers should report sane values after initialization, especially around `UCODE`, `STATUS*`, `CNTL`, and `POWER/CLK` registers.
- KFD SDMA queue creation, load, preemption, and teardown on engine 4 should succeed, with doorbell writes advancing RLC queue write/read pointers.
- GPU reset and coredump paths should identify SDMA4 and capture meaningful status/error registers rather than zeros or unrelated block data.
- RAS and error-injection testing should show SDMA EDC/error counters changing at the expected offsets and clearing through the expected clear register.
- Multi-engine SDMA tests should compare SDMA4 behavior against SDMA0-SDMA7 peers, since this file is part of a repeated register layout family.
