# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_powertune.c

## Purpose
`vega20_powertune.c` implements the Vega20 PowerTune power-limit helper functions used by the hwmgr function table. Its scope is intentionally small: validate requested TDP adjustment, send PPT limits to SMU, and translate platform TDP adjustment polarity into an overdrive percentage.

## Important APIs, Types, and Functions
`vega20_set_power_limit()` checks whether the `GNLD_PPT` SMU feature is enabled and sends `PPSMC_MSG_SetPptLimit` with the requested limit. `vega20_validate_power_level_request()` rejects percentage adjustments greater than `hwmgr->platform_descriptor.TDPLimit`. `vega20_power_control_set_level()` checks `PHM_PlatformCaps_PowerContainment`, derives a signed percentage from `TDPAdjustment` and `TDPAdjustmentPolarity`, and calls the private `vega20_set_overdrive_target_percentage()` wrapper around `PPSMC_MSG_OverDriveSetPercentage`.

## Control Flow
The main hwmgr bring-up path calls `vega20_power_control_set_level()` after DPM tables and sustainable clocks are initialized. User-facing power-limit changes call `vega20_set_power_limit()` through the hwmgr callback table.

## State and Persistence
This file does not own state. It reads `hwmgr->backend` for SMU feature state and reads `platform_descriptor` fields for limits and requested adjustments. Firmware stores the effective runtime PPT/overdrive settings until reset or reprogramming.

## Dependencies and Integration Points
It depends on `vega20_hwmgr.h` for `GNLD_PPT`, `vega20_smumgr.h` for SMU message helpers, and `vega20_ppsmc.h` for message IDs. It is wired into `vega20_hwmgr_funcs` as `.set_power_limit` and called during DPM enable.

## Risks
The validation helper ignores `tdp_absolute_value_adjustment`, so callers expecting absolute-value validation need additional checks elsewhere. Signed percentage conversion is cast to `uint32_t` for the SMU message, so firmware must interpret the value as expected. If `GNLD_PPT` feature state is stale, a power-limit request may silently do nothing.

## Test Signals
Check that power-limit sysfs writes produce expected SMU PPT changes, invalid percentage adjustments are rejected, and DPM enable logs do not report `OverDriveSetPercentage` failures when PowerContainment is enabled.
