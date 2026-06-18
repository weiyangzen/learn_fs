# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_processpptables.c

## Purpose

This file loads the Vega10 PowerPlay table from ATOMBIOS or a cached soft table, validates it, converts packed BIOS subtables into runtime `phm_ppt_v2_information`, initializes platform capabilities and thermal metadata, exposes BIOS power-state entries, and provides a BACO-capability refresh helper.

## Important APIs, Types, and Functions

The exported `vega10_pptable_funcs` supplies `.pptable_init` and `.pptable_fini` hooks. `vega10_get_number_of_powerplay_table_entries` returns BIOS state count, `vega10_get_powerplay_table_entry` maps one ATOM state through a caller callback, and `vega10_baco_set_cap` refreshes `PHM_PlatformCaps_BACO`.

Key static functions are `get_powerplay_table`, `check_powerplay_tables`, `set_platform_caps`, `init_thermal_controller`, `init_over_drive_limits`, `init_powerplay_extended_tables`, `init_dpm_2_parameters`, and conversion helpers for MM, SOC/GFX/MEM/DCEF/PIX/PHY/DISP clocks, PCIe, hard limits, voltage lookups, valid clock arrays, TDP/PowerTune, and I2C line IDs.

## Control Flow, State, and Persistence

Initialization allocates `hwmgr->pptable`, fetches or caches the BIOS table in `hwmgr->soft_pp_table`, validates revision and state presence, sets platform caps from `ulPlatformCaps`, imports thermal/fan settings, clamps the overdrive engine clock to `VEGA10_ENGINECLOCK_HARDMAX` unless ACG is enabled, builds dependency and lookup tables with `kzalloc_flex`, copies hard limits into `hwmgr->dyn_state`, and initializes DPM2 voltage-mode and TDP overdrive fields. Uninitialization frees most allocated tables and nulls their pointers.

Power-state entry lookup reuses the cached table, validates the state array, computes classification flags from `usClassification` and `usClassification2`, calls the supplied callback with the ATOM state and root table, then patches boot state through `hwmgr->hwmgr_func` when applicable.

## Dependencies and Integration Points

The parser depends on `ppatomfwctrl`, ATOM firmware table access, `vega10_pptable.h`, Linux allocation helpers, `phm_cap_set/unset`, `pp_hwmgr` table hooks, and AMDGPU PCI IDs for a DCEFCLK workaround. Its outputs feed Vega10 DPM setup, fan control, PowerTune default copying, power containment, display clock decisions, overdrive limits, and BACO support.

## Risks and Test Signals

Most subtable pointers are formed by offset arithmetic with limited table-size checks, so malformed BIOS data can lead to out-of-bounds reads. The state entry check uses `entry_index <= ucNumEntries`, which permits an out-of-range zero-based index. `get_vddc_lookup_table` allocates for `max_levels` but sets count from BIOS entries without clamping. Fini does not visibly free every optional table initialized in `init_powerplay_extended_tables` in this source version, such as SOC/DCEF/PIX/PHY/DISP/PCIe/valid SOC/DCEF arrays, which should be checked against the wider tree. Tests should inject synthetic tables for each revision, zero-entry failures, absent optional offsets, pioneer DCEFCLK workaround, ACG overdrive behavior, PCIe truncation, and cleanup after partial initialization failure.
