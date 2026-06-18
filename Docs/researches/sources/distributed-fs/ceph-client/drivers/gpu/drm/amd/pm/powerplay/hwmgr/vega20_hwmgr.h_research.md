# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_hwmgr.h

## Purpose
`vega20_hwmgr.h` defines the private data model, feature IDs, DPM tables, registry defaults, overdrive structures, and constants used by the Vega20 PowerPlay hardware manager. It is the state contract shared by `vega20_hwmgr.c`, thermal code, powertune code, and PPTable processing.

## Important APIs, Types, and Functions
The central type is `struct vega20_hwmgr`, which embeds current and golden DPM tables, registry data, VBIOS boot state, voltage metadata, thermal/power-gating flags, OverdriveN/Overdrive8 state, SMU feature descriptors, SMC table storage, metrics caches, PCIe overrides, and workload/profile flags. `struct smu_features` tracks whether each firmware feature is supported, enabled, allowed, and how it maps to SMU bit IDs and bitmaps. DPM modeling uses `struct vega20_dpm_level`, `struct vega20_dpm_state`, `struct vega20_single_dpm_table`, `struct vega20_pcie_table`, and `struct vega20_dpm_table`.

The header also defines `GNLD_*` feature indices, OD8 feature and setting IDs, `struct vega20_smc_state_table` for PPTable/watermark/metrics/overdrive firmware tables, `struct vega20_registry_data` for driver policy switches, and fixed UMD pstate indices.

## Control Flow
There is no executable control flow, but the layout drives initialization in `vega20_hwmgr.c`: registry defaults are populated, SMU feature IDs are assigned according to the `GNLD_*` enum, DPM tables are filled from SMU queries or boot clocks, and OD8 capability/range information is copied from parsed PPTable structures into `od8_settings`.

## State and Persistence
All state declared here is in-memory driver state. It is allocated during backend init and freed during backend fini. The "golden" DPM table is a saved copy of the default firmware-discovered table used to compute overdrive percentages and restore bounds; it is not a persistent user profile store.

## Dependencies and Integration Points
The header depends on `hwmgr.h`, `smu11_driver_if.h`, and `ppatomfwctrl.h` for PowerPlay core types, SMU table types (`PPTable_t`, `Watermarks_t`, `SmuMetrics_t`, `OverDriveTable_t`, etc.), and Atom firmware voltage table types. It is included by Vega20 hwmgr, powertune, and thermal code to interpret `hwmgr->backend`.

## Risks
This header is ABI-sensitive inside the driver: enum order is used when composing feature masks and printing PP feature names. Array sizes and fixed pstate indices must remain consistent with firmware-reported DPM levels. Duplicate macro names also appear in generic headers, so changes can create subtle compile conflicts.

## Test Signals
Compile coverage is the first signal. Runtime signals include correct SMU feature bitmask reporting, valid DPM table counts, overdrive range reporting, and no out-of-bounds access when firmware reports minimum clock-level counts.
