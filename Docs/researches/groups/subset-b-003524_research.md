# Research: subset-b-003524

Grouped research for Vega20 AMDGPU PowerPlay hardware manager sources and adjacent public headers. Each section preserves the source path for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_hwmgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_hwmgr.c

## Purpose
`vega20_hwmgr.c` is the Vega20 implementation of the legacy AMD PowerPlay hardware-manager backend. It binds `struct pp_hwmgr` to Vega20-specific SMU11 firmware operations for dynamic power management, clock/voltage limits, display clock requests, overdrive, power profiles, power gating, thermal/fan hooks, BACO, I2C arbitration, XGMI/DF state control, and GPU metrics. `vega20_hwmgr_init()` installs `vega20_hwmgr_funcs` and `vega20_pptable_funcs`, making this file the integration surface between generic PowerPlay code and Vega20 firmware/register programming.

## Important APIs, Types, and Functions
The file is organized around `struct vega20_hwmgr` from `vega20_hwmgr.h`, reached through `hwmgr->backend`. Backend lifetime is handled by `vega20_hwmgr_backend_init()` and `vega20_hwmgr_backend_fini()`. Initialization sets registry defaults, platform caps, SMU feature IDs and bitmaps, serial number, boot clock metadata, DPM tables, sustainable clock limits, overdrive defaults, and the default PPT power limit. `vega20_enable_dpm_tasks()` is the core bring-up sequence: set display count to zero, upload allowed feature masks, initialize/upload the SMC PPTable, run BTC/AFLL calibration, enable SMU features, override PCIe parameters, notify display state, send FCLK:GFXCLK ratio, initialize power-gating state, build DPM tables, initialize power limits and OD8 settings, and publish UMD pstate clocks.

Clock control is split into DPM table discovery (`vega20_setup_single_dpm_table()`, `vega20_setup_default_dpm_tables()`), min/max uploads (`vega20_upload_dpm_min_level()`, `vega20_upload_dpm_max_level()`), forced levels (`vega20_force_dpm_highest()`, `vega20_force_dpm_lowest()`, `vega20_unforce_dpm_levels()`, `vega20_force_clock_level()`), and sysfs emission (`vega20_emit_clock_levels()`). Display integration uses `vega20_pre_display_configuration_changed_task()`, `vega20_display_configuration_changed_task()`, `vega20_notify_smc_display_config_after_ps_adjustment()`, `vega20_display_clock_voltage_request()`, and `vega20_set_watermarks_for_clocks_ranges()`.

Overdrive8 is implemented through `vega20_od8_set_feature_capabilities()`, `vega20_od8_initialize_default_settings()`, `vega20_od8_set_settings()`, `vega20_get_sclk_od()`, `vega20_set_sclk_od()`, `vega20_get_mclk_od()`, `vega20_set_mclk_od()`, and `vega20_odn_edit_dpm_table()`. The file also exposes PP feature toggling (`vega20_get_ppfeature_status()`, `vega20_set_ppfeature_status()`), power profile reporting and programming (`vega20_get_power_profile_mode()`, `vega20_set_power_profile_mode()`), sensors (`vega20_read_sensor()`), metrics (`vega20_get_gpu_metrics()`), power gating (`vega20_power_gate_uvd()`, `vega20_power_gate_vce()`), MP1 state preparation, SMU I2C bus access, DF C-state, XGMI pstate, and power-off handling.

## Control Flow
The normal lifecycle begins when the common PowerPlay layer calls `vega20_hwmgr_init()`, then backend init allocates and populates `struct vega20_hwmgr`. PPTable initialization is delegated to `vega20_processpptables.c`; later `vega20_enable_dpm_tasks()` copies the parsed PPTable into the SMC table, uploads it with `smum_smc_table_manager(... TABLE_PPTABLE, false)`, and enables firmware features. Most runtime operations follow the same pattern: compute a local DPM/OD/display state, send one or more `PPSMC_MSG_*` commands through `smum_send_msg_to_smc[_with_parameter]()`, and update the cached `vega20_hwmgr` fields only after the firmware operation succeeds.

Display changes are two phase. Before reconfiguration, the driver raises UCLK and FCLK to high levels to keep display memory service stable. After reconfiguration, pending watermark tables are uploaded once and the new display count is sent to SMU. The clock-adjust path recomputes soft/hard min/max values for GFXCLK, UCLK, FCLK, UVD/VCE clocks, SOCCLK, and display clocks based on UMD pstate, forced profile, display latency, multi-monitor state, and DAL hard-min requests.

## State and Persistence
Persistent runtime state is in `hwmgr->backend`, `hwmgr->platform_descriptor`, `hwmgr->pptable`, and selected `hwmgr` public fields such as `power_limit`, `default_power_limit`, `power_profile_mode`, and UMD pstate clocks. `struct vega20_hwmgr` caches SMU feature support/enabled/allowed bits, active DPM tables plus golden copies, VBIOS boot clocks, SMU PPTable/watermark/OD/metrics tables, overdrive flags, fan/power-gating state, PCIe overrides, workload mask, and a one-millisecond metrics cache keyed by `metrics_time`. State is not persisted across driver reload; it is reconstructed from VBIOS tables, SMU firmware queries, and defaults.

## Dependencies and Integration Points
This implementation depends on SMU11 table layouts and message IDs from `smu11_driver_if.h` and `vega20_ppsmc.h`, PPTable parsing from `vega20_processpptables.c`, register offsets/masks from `vega20_inc.h` and SoC-specific include paths, thermal/fan helpers from `vega20_thermal.c`, power-limit helpers from `vega20_powertune.c`, BACO helpers from `vega20_baco.h`, and generic PowerPlay interfaces from `hwmgr.h`, `hardwaremanager.h`, `amd_powerplay.h`, `kgd_pp_interface.h`, and display-manager PP interfaces. It also calls AtomBIOS helpers (`pp_atomfwctrl_get_vbios_bootup_values()`), amdgpu core power-gating helpers, PCIe register accessors, and sysfs emit helpers.

## Risks
Firmware ABI coupling is the primary risk: message IDs, table IDs, PPTable version, and SMU version checks must match the loaded firmware. Clock units vary between 10 kHz, 100 kHz, MHz, and kHz; many paths multiply or divide by 100, 1000, or 10, so unit mistakes can overconstrain clocks. Several arrays assume firmware-reported DPM counts fit `MAX_REGULAR_DPM_NUMBER`, `NUM_LINK_LEVELS`, or OD8 setting counts. The OD8 code validates many ranges but still relies on PPTable capabilities and exported firmware tables being coherent. Display clock and memory hard-min logic is sensitive to multi-monitor and latency inputs. Sensor and metrics paths depend on cache freshness and firmware table export success. Direct register reads/writes for fan and PCIe state require the expected SOC15 block mappings.

## Test Signals
Useful signals include successful driver load with Vega20 hardware, `dmesg` free of PP_ASSERT failures during DPM enable, correct `pp_dpm_*` clock-level sysfs output with current-level markers, `pp_features` get/set round trips, overdrive edits rejected outside OD ranges and accepted within ranges, stable display hotplug/multi-monitor transitions without underflow, fan PWM/RPM manual and auto transitions, UVD/VCE power-gating state changes during media workloads, `gpu_metrics` and hwmon sensor values updating, PCIe DPM levels not exceeding platform capability, and suspend/resume or BACO reset paths reinitializing state cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_hwmgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_hwmgr.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_hwmgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_inc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_inc.h

## Purpose
`vega20_inc.h` is a thin register include aggregator for Vega20 PowerPlay code. It pulls in SOC15 offset and mask definitions for thermal (`thm_11_0_2`), MP (`mp_9_0`), and NBIO (`nbio_7_4`) blocks.

## Important APIs, Types, and Functions
The file exports no functions or types of its own. Its important API is the set of included register constants and field masks consumed by `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, and `REG_GET_FIELD` users in hwmgr and thermal code.

## Control Flow
There is no control flow. Inclusion makes register names such as thermal fan-control registers and NBIO/MP masks available to implementation files.

## State and Persistence
No state is defined. It only names hardware register addresses and bitfields through included generated headers.

## Dependencies and Integration Points
It integrates generated ASIC register headers with Vega20-specific PM files, particularly fan control, temperature reads, interrupt setup, and low-level power-management register access.

## Risks
Incorrect include selection would make the driver program the wrong SOC15 block layout. Because these are compile-time constants, errors generally surface as build failures or runtime hardware misprogramming rather than local validation failures.

## Test Signals
Build success verifies names exist. Runtime fan/thermal/PCIe register behavior on Vega20 hardware validates that the selected offset/mask headers match the ASIC revision.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_inc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_powertune.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_powertune.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_powertune.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_powertune.h

## Purpose
`vega20_powertune.h` declares the public Vega20 PowerTune helpers used by the hardware-manager implementation and generic callback wiring.

## Important APIs, Types, and Functions
It declares `vega20_set_power_limit()`, `vega20_power_control_set_level()`, and `vega20_validate_power_level_request()`. These are implemented in `vega20_powertune.c` and operate on `struct pp_hwmgr`.

## Control Flow
The header has no control flow. It permits `vega20_hwmgr.c` to call PowerTune setup during DPM enable and to expose power-limit programming through `pp_hwmgr_func`.

## State and Persistence
No state is declared. The functions operate on `hwmgr->backend`, platform descriptor fields, and SMU runtime state.

## Dependencies and Integration Points
The declarations rely on `struct pp_hwmgr` being visible to includers. The implementation requires SMU message helpers and Vega20 feature-state definitions.

## Risks
Because this header only declares a narrow interface, most risk is signature drift with the implementation or generic hwmgr callback expectations.

## Test Signals
Build success validates declaration/definition consistency. Runtime power-limit and power-control sysfs behavior validates the API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_powertune.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_pptable.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_pptable.h

## Purpose
`vega20_pptable.h` defines the packed AtomBIOS PowerPlay table format for Vega20. It bridges VBIOS-provided board policy data to the driver's parsed `phm_ppt_v3_information` and SMU `PPTable_t`.

## Important APIs, Types, and Functions
The key type is `ATOM_Vega20_POWERPLAYTABLE`, a packed structure containing the Atom common header, table revision and size, platform caps, thermal controller type, power limits, software shutdown temperature, power-saving clock table, OverDrive8 table, reserve fields, and embedded `PPTable_t smcPPTable`. Supporting types define OD8 feature/setting identifiers, `ATOM_VEGA20_OVERDRIVE8_RECORD`, `ATOM_VEGA20_POWER_SAVING_CLOCK_RECORD`, and PP clock identifiers.

## Control Flow
There is no executable control flow. `vega20_processpptables.c` reads these structures, validates revisions, copies OD8 arrays and power-saving clock ranges, extracts board power limits, and duplicates the embedded `smcPPTable` for later upload by `vega20_hwmgr.c`.

## State and Persistence
The structures describe persistent VBIOS data, but this header only defines its in-memory representation. Parsed copies live in `hwmgr->pptable` and `data->smc_state_table.pp_table`.

## Dependencies and Integration Points
It depends on AtomBIOS scalar typedefs (`UCHAR`, `USHORT`, `ULONG`) and `smu11_driver_if.h`'s `PPTable_t` through includers. It is tightly coupled to the firmware-supported `PPTABLE_V20_SMU_VERSION` checked by the parser.

## Risks
Packed layout must match VBIOS exactly. Revision/count mismatches can cause rejected PPTable initialization or misinterpreted OD ranges. OD8 enum ordering is mirrored by the hwmgr OD8 setting code, so drift between Atom table IDs and driver setting IDs is risky.

## Test Signals
Boot logs should not report unsupported PPTable format or version mismatch. OD8 sysfs ranges, thermal limits, fan maximum RPM, and power-saving clock limits should reflect board VBIOS values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_pptable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_processpptables.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_processpptables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_processpptables.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_processpptables.h

## Purpose
`vega20_processpptables.h` declares the Vega20 PPTable function table used by the hwmgr initializer.

## Important APIs, Types, and Functions
It includes `hwmgr.h` and exports `extern const struct pp_table_func vega20_pptable_funcs;`. The function table provides `.pptable_init` and `.pptable_fini` implemented in `vega20_processpptables.c`.

## Control Flow
No direct control flow exists. `vega20_hwmgr_init()` assigns `hwmgr->pptable_func = &vega20_pptable_funcs`, allowing generic PowerPlay lifecycle code to invoke the Vega20 PPTable parser.

## State and Persistence
No state is declared. The referenced function table manages `hwmgr->pptable` when invoked.

## Dependencies and Integration Points
It depends on the generic `struct pp_table_func` declaration from `hwmgr.h`. It is the compile-time link between the hwmgr backend and PPTable parser.

## Risks
The only material risk is declaration/definition mismatch or failing to include this header where `vega20_hwmgr_init()` assigns the function table.

## Test Signals
Build success and successful PowerPlay table initialization on Vega20 hardware validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_processpptables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_thermal.c

## Purpose
`vega20_thermal.c` implements Vega20 fan control and thermal alert helpers used by the hwmgr function table. It can switch between SMU microcode fan control and manual register-driven PWM/RPM modes, read hotspot temperature, program thermal interrupt thresholds, and send the fan target temperature to SMU.

## Important APIs, Types, and Functions
SMU fan-control feature toggles are `vega20_fan_ctrl_start_smc_fan_control()`, `vega20_fan_ctrl_stop_smc_fan_control()`, and their private enable/disable helpers. Manual fan access includes `vega20_fan_ctrl_get_fan_speed_pwm()`, `vega20_fan_ctrl_set_fan_speed_pwm()`, `vega20_fan_ctrl_get_fan_speed_rpm()`, `vega20_fan_ctrl_set_fan_speed_rpm()`, and `vega20_fan_ctrl_get_fan_speed_info()`. Temperature and alert handling includes `vega20_thermal_get_temperature()`, `vega20_thermal_disable_alert()`, `vega20_thermal_stop_thermal_controller()`, and `vega20_start_thermal_controller()`.

## Control Flow
Manual PWM/RPM setters first stop SMU fan control when microcode fan control is enabled, compute register units, write THM fan-control registers, and set static mode. Thermal startup validates a temperature range, programs high/low interrupt thresholds clamped by the PPTable software shutdown temperature, enables thermal interrupt clear bits, and sends `PPSMC_MSG_SetFanTemperatureTarget` using the uploaded SMU PPTable fan target.

## State and Persistence
The file mutates `data->smu_features[GNLD_FAN_CONTROL].enabled` when enabling or disabling firmware fan control. It reads the thermal controller and PPTable state from `hwmgr` and `hwmgr->pptable`. Manual fan settings are persisted only in hardware registers until changed, reset, or SMU control resumes.

## Dependencies and Integration Points
It depends on `vega20_hwmgr.h` for backend feature state, `vega20_smumgr.h` and `vega20_ppsmc.h` for SMU commands, `vega20_inc.h`/SOC15 macros for THM register access, and `pp_debug.h` for assertion/log macros. The hwmgr function table exposes these routines for generic thermal/fan operations.

## Risks
Fan control crosses firmware and direct-register domains; failing to stop SMU control before manual writes can cause contention. RPM conversion can overflow without the explicit `speed > UINT_MAX/8` check. PWM conversion depends on `FMAX_DUTY100` being nonzero. Thermal threshold clamping depends on valid PPTable shutdown temperature. Comments reference older ASIC families, so maintainers must trust register names over comments.

## Test Signals
Runtime tests should verify readable RPM/PWM, manual PWM and RPM writes changing fan behavior, auto mode re-enabling SMU control, hotspot temperature reading plausible values, thermal alert programming not failing at startup, and no SMU fan-control feature errors in logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_thermal.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_thermal.h

## Purpose
`vega20_thermal.h` declares Vega20 thermal and fan-control helpers and shared constants for the hwmgr thermal callback wiring.

## Important APIs, Types, and Functions
It defines `struct vega20_temperature` with edge, hotspot, HBM, VR, liquid, and PLX temperature fields, alert masks, minimum/maximum temperature ranges, and fan static-mode constants. It declares temperature read, fan speed info/get/set for PWM and RPM, SMU fan-control start/stop, thermal alert disable, thermal controller start, and thermal controller stop functions.

## Control Flow
The header has no executable control flow. `vega20_hwmgr.c` installs the declared routines in `pp_hwmgr_func`, while `vega20_thermal.c` implements them.

## State and Persistence
No state is stored here. The declared functions mutate SMU feature state and THM registers through `struct pp_hwmgr`.

## Dependencies and Integration Points
It includes `hwmgr.h` for `struct pp_hwmgr`, `struct phm_fan_speed_info`, and `struct PP_TemperatureRange`. It is included by both the thermal implementation and hwmgr backend.

## Risks
The declared `struct vega20_temperature` is broader than the current implementation's direct temperature reads, so callers should not assume every field is populated by these APIs. Constants must match hardware register mode encodings.

## Test Signals
Build linkage plus fan/thermal sysfs and hwmon behavior validate this header's interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_thermal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/amd_powerplay.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/amd_powerplay.h

## Purpose
`amd_powerplay.h` is a lightweight umbrella header for AMD PowerPlay code. It centralizes common kernel, amdgpu, CGS, display-manager PP, and KGD PP interface includes.

## Important APIs, Types, and Functions
This header declares no new functions or data structures. Its exported surface is the transitive availability of `seq_file`, Linux integer/error types, `amd_shared.h`, `cgs_common.h`, `dm_pp_interface.h`, `kgd_pp_interface.h`, and `amdgpu.h`.

## Control Flow
There is no control flow. Including it gives implementation files access to common PowerPlay-facing interfaces and amdgpu device types.

## State and Persistence
No state is defined.

## Dependencies and Integration Points
It is used by files such as `vega20_hwmgr.c` that need broad PowerPlay and amdgpu type visibility. It sits near the top of the include graph for this legacy PM stack.

## Risks
Umbrella headers can hide true dependencies and increase compile coupling. Any change to included headers may affect many PowerPlay translation units.

## Test Signals
Compile success across PowerPlay users validates that included interface dependencies remain sufficient and non-conflicting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/amd_powerplay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/cz_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/cz_ppsmc.h

## Purpose
`cz_ppsmc.h` defines Carrizo/Stoney-era PowerPlay SMC protocol constants: fan-control modes, DPM array IDs, return codes, message IDs, and feature masks. It provides the numeric firmware command ABI for older ASIC/APU SMU communication.

## Important APIs, Types, and Functions
The header defines `PPSMC_Result_*` return values and `PPSMC_isERROR()`, a large set of `PPSMC_MSG_*` command IDs for feature enablement, clock limits, power gating, DRAM/logging setup, display/watermark control, and legacy jobs, plus feature masks such as `NB_DPM_MASK`, `VDDGFX_MASK`, `VCE_DPM_MASK`, `ACP_DPM_MASK`, `UVD_DPM_MASK`, and `SCLK_DPM_MASK`. It also defines fan-control and DPM-array enums.

## Control Flow
There is no executable flow. Other source files use these constants when composing commands for the SMC messaging layer.

## State and Persistence
No state is declared. The constants describe firmware-visible state transitions and commands.

## Dependencies and Integration Points
The file uses packed layout guards for firmware/shared-code compatibility and is part of the PowerPlay include set used by ASIC-specific SMU managers. Although the researched Vega20 hwmgr uses `vega20_ppsmc.h`, this header is relevant to the same generic SMC message infrastructure for older hardware paths.

## Risks
Numeric message IDs are firmware ABI. Renumbering or reusing IDs incorrectly would send wrong commands. Some names overlap with other ASIC-specific `*_ppsmc.h` headers, so include ordering and ASIC-specific compilation boundaries matter.

## Test Signals
Build coverage in Carrizo/Stoney PM code and runtime SMC command success on those ASICs are the practical tests. Failures would appear as unknown command, failed SMC result, or broken DPM/power-gating behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/cz_ppsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/fiji_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/fiji_ppsmc.h

## Purpose
`fiji_ppsmc.h` defines Fiji-era PowerPlay SMC protocol constants. It maps software state flags, thermal types, system flags, DPM state flags, return codes, SMC message IDs, event status bits, and the `PPSMC_Msg` typedef used by Fiji PM code.

## Important APIs, Types, and Functions
Important definitions include software state flags for DC/UVD/VCE, thermal-protect constants, GPIO/system flags, DPM2 flags, display watermark levels, hardware performance state flags, Gemini mode constants, `PPSMC_Result_*` values, and a large list of `PPSMC_MSG_*` IDs covering DPM control, power gating, CAC, voltage/thermal control, logging, BACO, I2C, AVFS, telemetry, and PSM commands. `typedef uint16_t PPSMC_Msg;` identifies command values passed to the SMC layer.

## Control Flow
The header has no executable control flow. ASIC-specific PM implementations use these macros to select firmware actions.

## State and Persistence
No runtime state is stored. The macros describe firmware commands and bit meanings that operate on firmware-managed state.

## Dependencies and Integration Points
It is a packed firmware ABI header for Fiji PowerPlay components. It integrates with generic SMC send helpers and ASIC-specific managers that need stable numeric command identifiers.

## Risks
The header contains many overlapping command names also present in other ASIC headers, but with potentially different numeric values. Incorrectly mixing Fiji and non-Fiji protocol constants is a high-risk firmware ABI bug. Comments note some temporary or legacy commands, so stale command support must be checked against firmware.

## Test Signals
Fiji hardware DPM, fan, thermal, BACO, voltage, and logging operations should complete without `UnknownCmd` or failed SMC responses. Compile boundaries should prevent conflicting message definitions from being used in the wrong ASIC path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/fiji_ppsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/hardwaremanager.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/hardwaremanager.h

## Purpose
`hardwaremanager.h` defines common PowerPlay hardware-manager abstractions used by ASIC-specific backends such as Vega20. It provides platform capability bits, performance/clock descriptor types, fan-speed capability metadata, capability helpers, and generic `phm_*` function declarations that dispatch through `struct pp_hwmgr`.

## Important APIs, Types, and Functions
Important types include `struct phm_fan_speed_info`, `enum phm_platform_caps`, `struct pp_hw_descriptor`, `enum PHM_PerformanceLevelDesignation`, `struct PHM_PerformanceLevel`, `enum PP_PCIEGen`, `struct PP_Clocks`, `struct pp_clock_info`, `struct phm_platform_descriptor`, `struct phm_clocks`, `struct phm_odn_performance_level`, and `struct phm_odn_clock_levels`. Inline helpers `phm_cap_set()`, `phm_cap_unset()`, `phm_cap_enabled()`, and macro `PP_CAP(c)` are heavily used by ASIC backends to gate features.

The declared `phm_*` functions cover ASIC setup, dynamic state management, power-state application, clock adjustment, DPM forcing, display configuration changes, thermal start/stop, DAL clock queries, clock-by-type queries, display clock voltage requests, max high clocks, and SMC firmware CTF disable.

## Control Flow
The header defines dispatch-layer contracts but not implementations. ASIC code fills callback tables, while generic PHM functions call through those callbacks to execute backend-specific logic. Capability bits set during PPTable and backend init determine later branches such as microcode fan control, PowerControl, OD8 AC/DC support, UMD pstate, BACO, and display-clock behavior.

## State and Persistence
`struct phm_platform_descriptor` is the main generic state container described here. It stores platform caps, VBIOS interrupt ID, overdrive and clock step information, hardware performance counts, TDP and voltage adjustment fields, and related limits. ASIC backends populate it during init; it persists for the lifetime of the `pp_hwmgr`.

## Dependencies and Integration Points
This header sits between generic PowerPlay code and ASIC hwmgr implementations. Vega20 uses its caps helpers throughout initialization, PowerTune, fan control, display handling, and OD setup. It also depends on shared enums/types from DM and KGD PP interfaces through includers.

## Risks
Capability enum order is ABI-like within the driver because caps are stored as bit positions in an integer array. Adding or reordering entries can break persisted assumptions inside a build. `PP_CAP(c)` assumes a local variable named `hwmgr`, which is convenient but can obscure dependencies and fail in contexts without that name. Duplicate DPM update macros also exist in Vega20 headers, creating possible maintenance drift.

## Test Signals
Compile coverage plus runtime feature gating is key: platform caps printed or inferred from behavior should match VBIOS/driver policy, generic PHM calls should dispatch to Vega20 callbacks, and fan/thermal/DPM/OD/display features should appear only when the corresponding caps are set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/hardwaremanager.h -->
