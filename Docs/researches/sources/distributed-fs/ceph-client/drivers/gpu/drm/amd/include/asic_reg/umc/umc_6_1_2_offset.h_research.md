# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_1_2_offset.h

## Purpose
This generated header defines Arcturus-specific UMC 6.1.2 register offsets for ECC counter selection, ECC count, MCA status, and MCA address registers. It mirrors the UMC 6.1.1 register set but uses `_ARCT` macro names and base index 1.

## Important APIs, Types, and Functions
The exported symbols are `mmUMCCH0_0_EccErrCntSel_ARCT`, `mmUMCCH0_0_EccErrCnt_ARCT`, `mmMCA_UMC_UMC0_MCUMC_STATUST0_ARCT`, and `mmMCA_UMC_UMC0_MCUMC_ADDRT0_ARCT`, each with `_BASE_IDX 1`. There are no functions or types.

## Control Flow
The header is selected in `amdgpu/umc_v6_1.c` when `adev->asic_type == CHIP_ARCTURUS`. The caller uses these offsets for counter clearing, counter initialization, CE/UE count queries, and UE address queries. Field manipulation still uses the UMC 6.1.1 field names because the C file includes only the 6.1.1 sh/mask header.

## State and Persistence Behavior
The header has no software state. It names Arcturus UMC registers whose values persist in hardware until driver, firmware, reset, or RAS clearing changes them. Arcturus paths also temporarily disallow DF C-state during RAS queries so register access and address collection remain stable.

## Dependencies and Integration Points
It integrates with `amdgpu/umc_v6_1.c`, Arcturus ASIC detection, RSMU UMC index-mode handling, DF C-state control via `amdgpu_dpm_set_df_cstate()`, SOC15 register offset infrastructure, and PCIe MMIO accessors. It pairs conceptually with `umc_6_1_2_sh_mask.h`, although the current C integration uses 6.1.1 field macro names.

## Risks
Base index 1 is the main difference from 6.1.1. A mismatch would target the wrong generated register base for Arcturus. Because field masks are assumed compatible with 6.1.1 names, any future 6.1.2 field layout change would require updating `umc_v6_1.c` includes and field names, not just this offset file.

## Test Signals
Run UMC RAS tests on Arcturus. Check that the Arcturus branch accesses `_ARCT` offsets, disables and restores DF C-state around queries, handles UMC index mode correctly, initializes both chip counters, and records valid UE addresses before clearing MCA status.
