# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_0_sh_mask.h

## Purpose
This generated header defines field masks and shifts for a minimal UMC 6.0 register set: ECC read/write enable, DRAM-ready status, and ECC disabled capability. It allows callers to interpret or set these hardware bits using AMD register helper macros.

## Important APIs, Types, and Functions
The interface is macro-only. `UMCCH0_0_EccCtrl__RdEccEn` and `UMCCH0_0_EccCtrl__WrEccEn` describe ECC enablement bits. `UMCCH0_0_UMC_CONFIG__DramReady` describes the high status bit indicating DRAM readiness. `UMCCH0_0_UmcLocalCap__EccDis` describes whether ECC is disabled or unavailable in the local capability register. There are no functions or types.

## Control Flow
The header has no control flow. It is included by `amdgpu/gmc_v9_0.c`, where UMC state contributes to graphics memory controller initialization and capability decisions. Callers typically read a register, apply `REG_GET_FIELD` or a mask/shift expression, and branch on ECC availability, ECC enablement, or DRAM readiness.

## State and Persistence Behavior
No state is stored by the header. The fields describe hardware state. `RdEccEn` and `WrEccEn` may be programmed by firmware or driver setup. `DramReady` is a hardware status bit reflecting memory initialization. `EccDis` is capability state and should generally be treated as read-only unless hardware documentation says otherwise.

## Dependencies and Integration Points
It pairs with `umc_6_0_offset.h` for register addresses and `umc_6_0_default.h` for default values. It integrates with AMDGPU GMC and RAS decisions through register helper conventions. The macros use the channel-0 register prefix even when equivalent fields apply to other channels through companion offsets.

## Risks
Using channel-0 field names against other channel offsets is conventional in generated AMD headers, but it requires the field layouts to be identical. Incorrect ECC enable interpretation can lead to false RAS capability reporting. Treating `DramReady` as writable, or clearing enable bits while memory is active, would be hazardous.

## Test Signals
Compile-test `gmc_v9_0.c` and related AMDGPU configurations. Runtime checks should compare reported ECC capability with VBIOS/firmware tables, confirm DRAM-ready before memory-dependent operations, and verify ECC enable bits on hardware with and without ECC support.
