# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_processpptables.c

## Purpose
`vega20_processpptables.c` initializes and tears down parsed Vega20 PowerPlay table state. It retrieves the AtomBIOS PowerPlay table, validates the table and embedded SMU PPTable version, translates platform caps, copies OD8 and power-saving clock limit arrays, augments the SMU PPTable with `smc_dpm_info` VBIOS fields, and exposes this through `vega20_pptable_funcs`.

## Important APIs, Types, and Functions
`get_powerplay_table()` obtains `powerplayinfo` through `smu_atom_get_data_table()` unless `hwmgr->soft_pp_table` is already set. `check_powerplay_tables()` validates format revision, structure size, and `smcPPTable.Version`. `set_platform_caps()` maps Atom platform capability bits into `PHM_PlatformCaps_*`. `copy_overdrive_feature_capabilities_array()` and generic PHM array-copy helpers allocate parsed OD/range arrays. `append_vbios_pptable()` copies voltage step, VR mapping, telemetry, spread-spectrum, GPIO, LED, and I2C-controller data from `atom_smc_dpm_info_v4_4` into `PPTable_t`. `init_powerplay_table_information()` fills `phm_ppt_v3_information`, sets thermal/fan caps, copies board power limits, enables power control when supported, duplicates the embedded SMU PPTable, appends VBIOS data, and overrides fan target temperature to 105. `vega20_pp_tables_initialize()` and `vega20_pp_tables_uninitialize()` are installed in `const struct pp_table_func vega20_pptable_funcs`.

## Control Flow
The generic PowerPlay table path calls `pptable_init`, which allocates `hwmgr->pptable`, retrieves VBIOS data, validates it, applies platform caps, and initializes parsed table information. Later, `vega20_hwmgr.c` copies `pptable_information->smc_pptable` into its SMU table and uploads it. On teardown, the uninitialize function frees each allocated array, the copied SMU PPTable, and `hwmgr->pptable`.

## State and Persistence
This file owns allocation and cleanup for `struct phm_ppt_v3_information`. It also caches the raw soft PP table pointer and size in `hwmgr` when the table is obtained from AtomBIOS. Parsed state persists for the driver lifetime and is consumed by hwmgr initialization, OD8, thermal limits, fan information, and power-limit reporting.

## Dependencies and Integration Points
It depends on AtomBIOS table lookup, `smu11_driver_if.h` table layouts, `vega20_pptable.h` packed table definitions, platform cap helpers from `hardwaremanager.h`, and allocation helpers/macros from the PowerPlay stack. It feeds `vega20_hwmgr.c`, `vega20_thermal.c`, and PowerTune policy through `hwmgr->pptable`.

## Risks
The code assumes OD capability/settings arrays exist when revision is 1; allocation failures in helper calls are not always immediately checked in the caller. It force-overrides `FanTargetTemperature` to 105, which may hide VBIOS-provided board tuning. `append_vbios_pptable()` copies many fields one by one, making it sensitive to Atom structure changes. Cleanup assumes `hwmgr->pptable` was fully allocated; partial init failure paths must avoid leaks or null dereferences.

## Test Signals
Successful PPTable init without `Unsupported PPTable format`, `Invalid PowerPlay Table`, or version mismatch logs is required. OD8 range output, platform caps such as BACO/BAMACO/PowerControl, fan max RPM, thermal shutdown threshold, and SMU PPTable upload success validate this parser.
