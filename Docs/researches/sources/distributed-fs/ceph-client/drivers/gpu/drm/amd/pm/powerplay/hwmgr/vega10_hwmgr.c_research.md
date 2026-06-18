# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_hwmgr.c

## Purpose
This is the Vega10 implementation of the legacy AMD PowerPlay hardware-manager backend. It converts VBIOS PowerPlay tables, Atom firmware data, display requirements, OverDrive edits, thermal/fan policy, and user/sysfs requests into SMU9 firmware tables and SMC messages. It registers a `pp_hwmgr_func` callback table through `vega10_hwmgr_init()` so the common PowerPlay layer can initialize DPM, switch power states, read sensors, control clocks/fans, handle display changes, power-gate media blocks, manage BACO, and shut down MP1.

## Important APIs, Types, and Functions
- `vega10_hwmgr_init()`: public init hook. It assigns `hwmgr->hwmgr_func = &vega10_hwmgr_funcs`, assigns `vega10_pptable_funcs`, and enables BACO capability for passthrough devices.
- `vega10_hwmgr_backend_init()` / `vega10_hwmgr_backend_fini()`: allocate and free `struct vega10_hwmgr`, derive voltage control modes, set platform capabilities, initialize SMU feature metadata, patch dependency tables, seed OverDrive and fan defaults, and cache memory-channel information.
- `vega10_enable_dpm_tasks()` / `vega10_disable_dpm_tasks()`: main lifecycle gates for DPM, voltage tables, SMC PPTable upload, thermal/VR hot/deep-sleep/ULV/DIDT/power-containment/ACG features, and their shutdown order.
- `vega10_init_smc_table()`: constructs software DPM tables, fills `PPTable_t`, uploads it via `smum_smc_table_manager(..., PPTABLE, false)`, uploads AVFS fuse overrides, and enables AVFS/ACG.
- `vega10_set_power_state_tasks()`: applies a requested power state by updating DPM tables when necessary, generating boot/max DPM limits, uploading the PPTable, and toggling AVFS around OD or custom-table changes.
- `vega10_read_sensor()`: services PowerPlay sensor queries for clocks, load, temperatures, UVD/VCE power state, package power, VDDGFX, and enabled SMU features.
- `vega10_emit_clock_levels()`, `vega10_force_clock_level()`, and `vega10_dpm_force_dpm_level()`: implement sysfs-style clock reporting and forced DPM policies.
- `vega10_odn_edit_dpm_table()`: validates and applies OverDrive Next clock/voltage edits, restore, and commit commands.
- `vega10_set_power_profile_mode()` / `vega10_get_power_profile_mode()`: expose workload/profile tuning and custom GFX DPM parameters.

## Control Flow
Initialization starts in `vega10_hwmgr_init()`, which only installs function tables and optionally sets BACO capability. The common PowerPlay layer later calls `.backend_init`, which allocates backend state, selects SVID2/GPIO voltage control based on Atom firmware, initializes registry defaults, derives platform caps, queries SMU version and serial number, populates SMU feature support flags, completes voltage dependency tables, and caches default limits.

When dynamic state management is enabled, `vega10_enable_dpm_tasks()` configures telemetry, constructs voltage tables, initializes and uploads the SMU PPTable, then enables thermal protection, VR hot, deep sleep, DPM features, DIDT, power containment, power-control levels, and ULV. The PPTable construction path builds DPM tables from VBIOS dependencies, duplicates last valid entries to fill firmware fixed-size arrays, derives PLL dividers through Atom firmware helpers, programs boot voltages and deep-sleep DCEF clocks, fills AVFS/GPIO parameters, and uploads through the SMU table manager.

Power-state changes flow through `vega10_apply_state_adjust_rules()` and `vega10_set_power_state_tasks()`. The adjust phase clamps clocks for DC, stable pstate, display minimums, and multi-display memory-switching restrictions. The set phase finds whether requested clocks require DPM table edits, repopulates SCLK/MCLK/SOCCLK portions when flagged, calculates low/high enabled DPM indexes, uploads soft min/max indexes to SMC, uploads the PPTable, and updates AVFS state.

Display changes call `vega10_notify_smc_display_config_after_ps_adjustment()` and `vega10_display_configuration_changed_task()`. Those paths toggle UCLK fast switching, request DCEF/display clock voltage, set deep-sleep DCEF limits, upload watermark tables once present, and notify the SMC of display count.

Shutdown uses `vega10_power_off_asic()` and `.dynamic_state_management_disable` to disable thermal, power containment, DIDT, AVFS, DPM, deep sleep, ULV, ACG, and PCC limiting, then clears the loaded watermark bit.

## State and Persistence Behavior
Persistent per-device software state is in `hwmgr->backend`, cast to `struct vega10_hwmgr`. It stores live DPM tables, golden default DPM tables, registry feature knobs, voltage tables, leakage data, SMU feature support/enabled flags, boot state, watermarks, OD tables, custom profile data, media power-gating booleans, display timing cache, and flags such as `need_update_dpm_table`.

Hardware/firmware state is persisted through SMU messages and table uploads: soft min/max clock indexes, enabled feature masks, workload mask, PPTable/WMTABLE/AVFS fuse tables, BACO state, telemetry config, power containment, and display clock requests. Some backend fields mirror firmware state, especially `smu_features[].enabled`, DPM soft limits, `water_marks_bitmap`, `uvd_power_gated`, and `vce_power_gated`. Those mirrors are important but can become stale if SMU calls fail after local mutation.

No disk persistence occurs. All settings are runtime driver state rebuilt from VBIOS, Atom firmware, module feature masks, and user requests.

## Dependencies and Integration Points
- Common PowerPlay: `hwmgr.h`, `hardwaremanager.h`, `amd_powerplay.h`, `pp_overdriver.h`, `pp_thermal.h`, `ppinterrupt.h`.
- Atom firmware and VBIOS parsing: `ppatomfwctrl.h`, `atomfirmware.h`, `vega10_processpptables.h`, `vega10_pptable.h`.
- SMU9: `smu9.h`, `smu9_driver_if.h`, `vega10_smumgr.h`, `vega10_ppsmc.h`, `smum_send_msg_to_smc*()`, `smum_smc_table_manager()`.
- Vega10 companion modules: `vega10_powertune.h`, `vega10_thermal.h`, `vega10_baco.h`.
- SOC/register access: `vega10_inc.h`, `soc15_common.h`, SMUIO offsets/masks, PCIe helpers, and `RREG32_SOC15`/`RREG32_PCIE`.
- Display manager integration occurs through display config data and watermark callbacks; media integration occurs through UVD/VCE DPM and power-gating callbacks.

## Risks
- The file contains many hardware-table array fills with firmware-defined maximums. Off-by-one errors or unvalidated VBIOS counts can corrupt fixed-size PPTable fields; assertions check many but not all assumptions.
- Local SMU feature `enabled` mirrors are sometimes updated before or around firmware calls. A failed SMC transaction can leave software state inconsistent with firmware state.
- `need_update_dpm_table` is a shared bitfield driving OD, SOCCLK, SCLK, MCLK, and AVFS behavior. Missing a bit or failing to clear the right bits can leave stale DPM data or disable AVFS longer than intended.
- Some logic is ASIC- or mode-specific, such as `pp_one_vf` peak limits, passthrough BACO capability, ACG firmware major version checks, and PCC limiting for specific chip/subvendor combinations.
- Display and memory-clock constraints are tightly coupled. Multi-monitor, VR, frame-lock, and latency policy changes can affect UCLK switching and flicker/power behavior.
- Several paths return generic `-EINVAL` or continue after `PP_ASSERT` diagnostics, so failures may be hard to diagnose without SMC/register tracing.

## Test Signals
- Build coverage with Vega10 PowerPlay enabled is required for the callback table and all companion headers.
- Boot/init tests should verify backend allocation, SMU version/serial reads, voltage control detection, PPTable upload, and DPM feature enablement.
- Runtime tests should cover AC/DC switching, stable pstate, forced DPM levels, manual clock masks, OD edit/commit/restore, power profiles, sensor reads, thermal/fan control, and UVD/VCE power gating.
- Display tests should cover no display, single display, unsynchronized multi-display, watermark upload, DCEF/deep-sleep clock requests, and memory-switching latency constraints.
- Suspend/resume, GPU reset, passthrough, and BACO in/out tests should check that DPM disable/enable ordering and watermarks recover correctly.
