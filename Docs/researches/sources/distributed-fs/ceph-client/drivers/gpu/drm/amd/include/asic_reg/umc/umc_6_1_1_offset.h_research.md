# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_1_1_offset.h

## Purpose
This generated header defines the UMC 6.1.1 register offsets needed by AMDGPU RAS handling for ECC error counter selection, ECC count reads, and MCA status/address collection on non-Arcturus UMC 6.1 ASICs.

## Important APIs, Types, and Functions
The public offsets are `mmUMCCH0_0_EccErrCntSel`, `mmUMCCH0_0_EccErrCnt`, `mmMCA_UMC_UMC0_MCUMC_STATUST0`, and `mmMCA_UMC_UMC0_MCUMC_ADDRT0`, all with `_BASE_IDX 0`. There are no functions or types.

## Control Flow
There is no internal flow. In `amdgpu/umc_v6_1.c`, code chooses these offsets when `adev->asic_type != CHIP_ARCTURUS`. It then adds per-UMC and per-channel offsets from `get_umc_6_reg_offset()`. Counter initialization selects lower and upper chips, configures APIC-based ECC interrupt behavior, and writes an initial counter value. Query flow reads counts and MCA status. Address flow reads `MCUMC_ADDRT0` when an uncorrectable ECC error is valid.

## State and Persistence Behavior
The header has no state. The named registers hold persistent hardware state: ECC counter selection, ECC counter values, MCA status latches, and MCA error address latches. The RAS code temporarily disables UMC index mode around accesses and clears status after recording an address.

## Dependencies and Integration Points
It pairs with `umc_6_1_1_sh_mask.h` and is included by `amdgpu/umc_v6_1.c`. Integration depends on RSMU index-mode control, `SOC15_REG_OFFSET`, PCIe register accessors, `adev->umc.channel_offs`, and `amdgpu_umc_fill_error_record()`.

## Risks
The file is part of an ASIC split: Arcturus uses the `umc_6_1_2_offset.h` `_ARCT` variant instead. Choosing the wrong offset family or base index can silently read the wrong register aperture. Counter and MCA status registers are used across many UMC instances and channels, so offset errors scale across the whole memory topology.

## Test Signals
Build `amdgpu/umc_v6_1.c`. Runtime validation should cover non-Arcturus UMC 6.1 hardware, checking counter initialization, lower/higher chip selection, CE/UE counting, MCA status clearing, and translated retired-page addresses.
