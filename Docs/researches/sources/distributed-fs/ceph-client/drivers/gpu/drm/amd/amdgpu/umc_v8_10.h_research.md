# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v8_10.h

## Purpose

This header defines UMC v8.10 topology, total-channel calculation, ECC counter constants, normalized-address column handling, swizzle-mode mapping macros, and public RAS/channel-table declarations.

## Important APIs, Types, and Functions

Important constants are `UMC_V8_10_CHANNEL_INSTANCE_NUM`, `UMC_V8_10_UMC_INSTANCE_NUM`, `UMC_V8_10_TOTAL_CHANNEL_NUM`, `UMC_V8_10_PER_CHANNEL_OFFSET`, `UMC_V8_10_CE_CNT_INIT`, `UMC_V8_10_NA_COL_2BITS_POWER_OF_2_NUM`, and `UMC_V8_10_NA_C5_BIT`. Swizzle helpers include `SWIZZLE_MODE_TMP_ADDR`, `SWIZZLE_MODE_ADDR_HI`, `SWIZZLE_MODE_ADDR_MID`, `SWIZZLE_MODE_ADDR_LOW`, and `SWIZZLE_MODE_ADDR_LSB`.

## Control Flow

There is no runtime flow. The swizzle macros are composed by `umc_v8_10.c` to map normalized addresses to physical addresses.

## State and Persistence Behavior

No state is stored. `UMC_V8_10_TOTAL_CHANNEL_NUM` reads runtime `adev->gmc` topology, including half-use masks, when expanded.

## Dependencies and Integration Points

It includes SOC15 and AMDGPU headers and exports `umc_v8_10_ras`, `umc_v8_10_channel_idx_tbl`, and `umc_v8_10_channel_idx_tbl_ext0` for generation setup.

## Risks

There is a typo in `UUMC_V8_10_CE_INT_THRESHOLD`; it is internally used by `UMC_V8_10_CE_CNT_INIT`, so compile succeeds, but the name is inconsistent. Swizzle macros assume valid `col_bit` values and can produce bad shifts if called without prior validation.

## Test Signals

Compile coverage, correct total-channel counts under `m_half_use`, valid swizzle PA results, and successful binding of the v8.10 RAS object are the main signals.
