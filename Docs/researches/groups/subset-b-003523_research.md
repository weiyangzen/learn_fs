# subset-b-003523 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_hwmgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_hwmgr.c

## Purpose
`vega12_hwmgr.c` is the main PowerPlay hardware-manager backend for Vega12 GPUs. It installs the Vega12 `pp_hwmgr_func` vtable, owns the Vega12 private backend state allocated at `hwmgr->backend`, translates kernel PowerPlay callbacks into SMU9 firmware messages, and coordinates dynamic power management, clocks, display constraints, fan control, thermal hooks, BACO integration, media block power gating, sensor reads, and GPU metrics export.

## Important APIs, Types, And Functions
The exported entry point is `vega12_hwmgr_init()`, which assigns `hwmgr->hwmgr_func = &vega12_hwmgr_funcs` and `hwmgr->pptable_func = &vega12_pptable_funcs`. Important lifecycle callbacks are `vega12_hwmgr_backend_init()`, `vega12_hwmgr_backend_fini()`, `vega12_setup_asic_task()`, `vega12_enable_dpm_tasks()`, `vega12_disable_dpm_tasks()`, and `vega12_power_off_asic()`. Clock and DPM controls include `vega12_setup_default_dpm_tables()`, `vega12_apply_clocks_adjust_rules()`, `vega12_force_clock_level()`, `vega12_dpm_force_dpm_level()`, and the min/max upload helpers that send `PPSMC_MSG_SetSoftMinByFreq`, `SetSoftMaxByFreq`, and `SetHardMinByFreq`. Runtime query paths include `vega12_read_sensor()`, `vega12_get_gpu_metrics()`, `vega12_emit_clock_levels()`, `vega12_get_ppfeature_status()`, and `vega12_set_ppfeature_status()`.

## Control Flow
Initialization allocates `struct vega12_hwmgr`, fills registry defaults, sets capability flags, initializes SMU feature descriptors, reads the serial number into `adev->unique_id`, copies thermal/fan defaults, and derives whether the driver controls gfxoff from `PP_GFXOFF_MASK`. DPM enablement first informs SMU about display count, sets the allowed feature mask, uploads the SMC PPTable from parsed PowerPlay data, runs ACG BTC, enables all SMU features, clamps PCIe parameters to platform masks, applies power control, reads clock ranges, builds DPM tables from SMU-reported levels, and populates UMD pstate clocks. Display changes force UCLK high before reconfiguration, upload watermarks when pending, update display count, and set DCEF/deep-sleep display clocks. Shutdown disables all SMU features and clears the loaded-watermark bit.

## State And Persistence
Most state is volatile driver state in `struct vega12_hwmgr`: DPM tables, golden DPM tables, SMU feature flags, VBIOS boot state, cached metrics, watermarks, clock ranges, power-gating booleans, and registry defaults. Persistent inputs come from VBIOS/ATOM data and SMU firmware; this file does not write durable configuration. The SMU metrics cache is refreshed at most every millisecond unless bypassed. A risk exists in `vega12_populate_umdpstate_clocks()`, which indexes `dpm_levels[count]` for peak clocks; if `count` is the number of valid entries, that is an off-by-one read.

## Dependencies And Integration Points
This backend depends heavily on `smum_send_msg_to_smc*`, `smum_smc_table_manager()`, SMU9 driver interfaces, ATOM firmware helpers, `phm_cap_*`, `pp_debug`, thermal helpers from `vega12_thermal.c`, PowerPlay table parsing from `vega12_processpptables.c`, register macros from `vega12_inc.h`, display-manager watermark data, and amdgpu device state. It integrates upward through PowerPlay callback tables and sysfs-facing clock/feature/sensor paths.

## Risks And Test Signals
Primary risks are firmware message sequencing, unit conversions between MHz, kHz, and 10 kHz, unchecked DPM table counts for some clock paths, feature-mask index alignment, and display watermarks. Test signals should include boot/resume/unload on Vega12 hardware, sysfs `pp_dpm_*` and `pp_features` reads/writes, display hotplug and multi-monitor memory-clock behavior, UVD/VCE power-gating transitions, gfxoff toggling, GPU metrics reads, thermal start/stop, and PCIe link reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_hwmgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_hwmgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_hwmgr.h

## Purpose
`vega12_hwmgr.h` defines the private data model for the Vega12 PowerPlay backend. It is the contract between the main hwmgr implementation, thermal code, SMU table handling, and adjacent helpers that need access to Vega12 DPM, feature, thermal, fan, clock, and metrics state.

## Important APIs, Types, And Functions
The key type is `struct vega12_hwmgr`, the object stored in `pp_hwmgr.backend`. Supporting types include `struct smu_features`, `vega12_dpm_level`, `vega12_dpm_state`, `vega12_single_dpm_table`, `vega12_dpm_table`, `vega12_smc_state_table`, `vega12_registry_data`, `vega12_vbios_boot_state`, ODN tables, fan tables, MCLK latency tables, and `vega12_clock_range`. The header exposes one function, `vega12_enable_disable_vce_dpm()`, for media DPM control by other modules.

## Control Flow
This header has no executable flow, but it shapes runtime flow by grouping state into tables used by `vega12_hwmgr.c`: default registry data is written into `registry_data`; SMU features are populated in `smu_features[]`; DPM setup fills the nested `vega12_dpm_table`; display and watermark paths use `display_timing`, `clk_range[]`, and `smc_state_table.water_marks_table`; metrics reads update `metrics_table` and `gpu_metrics_table`.

## State And Persistence
The structures represent volatile kernel memory. They mirror firmware state and parsed VBIOS inputs but are not durable themselves. Important mutable flags include `uvd_power_gated`, `vce_power_gated`, `gfxoff_controlled_by_driver`, `water_marks_bitmap`, SMU feature `supported/enabled/allowed`, and cached `metrics_time`. Constants define DPM array sizes, UMD pstate indices, voltage-control modes, thermal output modes, and default averaging coefficients.

## Dependencies And Integration Points
It includes generic hwmgr definitions, SMU9 Vega12 driver interfaces, and ATOM firmware control types. Its definitions must stay in sync with SMU firmware table layouts such as `PPTable_t`, `Watermarks_t`, `SmuMetrics_t`, and `OverDriveTable_t`, plus higher-level PowerPlay structures such as ODN and fan-control records.

## Risks And Test Signals
The main risks are structure drift against firmware interfaces, fixed array size assumptions (`MAX_REGULAR_DPM_NUMBER`, `PPCLK_COUNT`), duplicate default macro names, and misspelled pseudo-count macros that could be copied into future code. Test signals are compile coverage across all users, SMU table upload success, correct feature-name mapping, and sanitizer or debug checking around DPM table indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_hwmgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_inc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_inc.h

## Purpose
`vega12_inc.h` is an include aggregator for Vega12 register definitions. It lets hwmgr and thermal code use generated SOC15 register offsets, defaults, masks, and shifts for thermal, MP, GC, and NBIO blocks through one Vega12-specific header.

## Important APIs, Types, And Functions
The file declares no functions or types of its own. Its important content is the inclusion of `asic_reg/thm/thm_9_0_*`, `asic_reg/mp/mp_9_0_*`, `asic_reg/gc/gc_9_2_1_*`, and `asic_reg/nbio/nbio_6_1_*` headers.

## Control Flow
There is no runtime control flow. Compile-time inclusion enables macros used by calls such as `RREG32_SOC15(THM, ...)`, `WREG32_SOC15(THM, ...)`, PCIe register reads, and field manipulation in thermal and hwmgr code.

## State And Persistence
No state is stored. The file exposes hardware register constants that control access to persistent hardware state at runtime from other compilation units.

## Dependencies And Integration Points
This header depends on generated ASIC register headers being present and matching the target Vega12/IP versions. It integrates into `vega12_hwmgr.c` for PCIe and feature code and `vega12_thermal.c` for thermal status and interrupt registers.

## Risks And Test Signals
The risk is incorrect IP-version binding: wrong register masks or offsets can silently corrupt hardware programming. Test signals are clean compilation, successful thermal interrupt programming, accurate temperature reads, and valid PCIe link-width/speed reporting on target hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_inc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_pptable.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_pptable.h

## Purpose
`vega12_pptable.h` defines the packed ATOM BIOS Vega12 PowerPlay table layout consumed by `vega12_processpptables.c`. It bridges VBIOS table data to the driver's `phm_ppt_v3_information` and SMU `PPTable_t`.

## Important APIs, Types, And Functions
Important constants identify thermal controllers, platform capability bits, and the expected table revision. `enum ATOM_VEGA12_ODSETTING_ID` indexes OD setting min/max arrays. `enum ATOM_VEGA12_PPCLOCK_ID` indexes clock min/max arrays. `ATOM_Vega12_POWERPLAYTABLE` contains the common table header, platform fields, power limits, software shutdown temperature, power-saving clocks, OD settings, and embedded `PPTable_t smcPPTable`.

## Control Flow
The file has no executable control flow. Runtime consumers cast ATOM data to `ATOM_Vega12_POWERPLAYTABLE`, validate the header revision and size, copy indexed arrays, and duplicate `smcPPTable` for later SMU upload.

## State And Persistence
This structure describes persistent VBIOS data. Driver code copies selected values into volatile `hwmgr->pptable`, `platform_descriptor`, `thermal_controller`, and eventually `vega12_hwmgr.smc_state_table.pp_table`.

## Dependencies And Integration Points
It depends on ATOM common table types and SMU Vega12 `PPTable_t`. It integrates with ATOM firmware table lookup, PowerPlay capability setup, thermal limit computation, overdrive limits, and SMU table upload.

## Risks And Test Signals
The main risks are packed layout drift, endian handling mistakes, invalid VBIOS table revisions, and array-index mismatches between OD/clock enums and firmware tables. Test signals include successful PPTable validation, sensible OD limits in sysfs, correct software shutdown temperature, and SMU accepting the uploaded PPTable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_pptable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_processpptables.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_processpptables.c

## Purpose
`vega12_processpptables.c` parses and materializes the Vega12 ATOM PowerPlay table. It allocates `hwmgr->pptable`, validates the VBIOS PPTable, applies platform capability bits, copies power/clock/OD limits, duplicates the embedded SMU `PPTable_t`, augments it with SMC DPM information from firmware control helpers, and exposes the `vega12_pptable_funcs` callback table.

## Important APIs, Types, And Functions
The public API is `const struct pp_table_func vega12_pptable_funcs` with `.pptable_init = vega12_pp_tables_initialize` and `.pptable_fini = vega12_pp_tables_uninitialize`. Internal functions include `get_powerplay_table()`, `check_powerplay_tables()`, `set_platform_caps()`, `init_powerplay_table_information()`, and `append_vbios_pptable()`. `append_vbios_pptable()` copies I2C, VR telemetry, voltage step, phase shedding, GPIO, LED, and spread-spectrum parameters into the SMU PPTable.

## Control Flow
Initialization allocates `struct phm_ppt_v3_information`, locates the `powerplayinfo` ATOM table or reuses `hwmgr->soft_pp_table`, validates revision/size, sets `PHM_PlatformCaps_*` from VBIOS platform caps, initializes thermal and overdrive metadata, copies indexed limits, `kmemdup()`s the embedded `smcPPTable`, and appends extra VBIOS SMC DPM fields. Finalization frees every allocated array/table pointer and then frees `hwmgr->pptable`.

## State And Persistence
The source VBIOS table is persistent firmware data. The parser caches its address and size in `hwmgr->soft_pp_table` and `soft_pp_table_size`; allocated parsed state lives in `hwmgr->pptable`. The SMU PPTable copy is later uploaded by `vega12_init_smc_table()`.

## Dependencies And Integration Points
Dependencies include ATOM firmware lookup, `pp_atomfwctrl_get_smc_dpm_information()`, `phm_copy_*_limits_array()`, `phm_cap_*`, Linux memory allocation, and `vega12_pptable.h`. Integration is direct with `vega12_hwmgr_init()` through `hwmgr->pptable_func`.

## Risks And Test Signals
Risks include leaks on partial initialization failure, trusting table sizes after minimal validation, duplicated assignment of `Vr2_I2C_address`, endian correctness, and platform caps not matching hardware behavior. Test signals include PPTable init/fini leak checks, boot with/without `soft_pp_table`, malformed VBIOS rejection, OD limit visibility, thermal-controller capability, BACO/BAMACO capability propagation, and SMU PPTable upload success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_processpptables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_processpptables.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_processpptables.h

## Purpose
`vega12_processpptables.h` declares the Vega12 PowerPlay table callback object and defines BIOS I2C line identifiers used when interpreting table or firmware-control data.

## Important APIs, Types, And Functions
`enum Vega12_I2CLineID` maps logical DDC/SCL/SDA/VGA lines to firmware IDs. The `Vega12_I2C_*` macros map those lines to numeric pin/data/clock identifiers. The header exports `extern const struct pp_table_func vega12_pptable_funcs`.

## Control Flow
No executable control flow is present. The callback object declared here is assigned by `vega12_hwmgr_init()` so generic PowerPlay code can call Vega12-specific PPTable init/fini.

## State And Persistence
No runtime state is stored here. The constants represent stable firmware/hardware identifiers that influence parsed SMU PPTable contents.

## Dependencies And Integration Points
The header depends on `hwmgr.h` for `struct pp_table_func`. It integrates `vega12_processpptables.c` with the main hwmgr and any code needing Vega12 I2C line IDs.

## Risks And Test Signals
Risks are mostly mapping errors: incorrect I2C IDs can break external sensors, VR telemetry, or liquid-cooling sensor communication. Test signals include PPTable parser compilation, sensor presence in SMU PPTable, and boards with VR/liquid/PLX I2C devices reporting correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_processpptables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_thermal.c

## Purpose
`vega12_thermal.c` implements Vega12 thermal and fan-control callbacks used by the hwmgr vtable. It reads edge temperature, configures thermal interrupt thresholds, starts/stops alerts, reports fan RPM support, reads current RPM through SMU, programs fan target temperature, and starts/stops SMU-managed fan control.

## Important APIs, Types, And Functions
Public functions are `vega12_thermal_get_temperature()`, `vega12_thermal_stop_thermal_controller()`, `vega12_fan_ctrl_get_fan_speed_info()`, `vega12_fan_ctrl_get_fan_speed_rpm()`, `vega12_fan_ctrl_reset_fan_speed_to_default()`, `vega12_fan_ctrl_stop_smc_fan_control()`, `vega12_thermal_disable_alert()`, `vega12_fan_ctrl_start_smc_fan_control()`, and `vega12_start_thermal_controller()`. Internal helpers include `vega12_thermal_set_temperature_range()`, `vega12_thermal_enable_alert()`, and `vega12_thermal_setup_fan_table()`.

## Control Flow
Starting the thermal controller validates the supplied range, clamps low/high thresholds against valid alert bounds and software shutdown temperature, programs `THM_THERMAL_INT_CTRL`, enables thermal interrupt clear bits, sends `PPSMC_MSG_SetFanTemperatureTarget` using `FanTargetTemperature` from the active SMU PPTable, and starts SMC fan control if the microcode fan-control platform cap is set. Stopping disables alerts. RPM reads send `PPSMC_MSG_GetCurrentRpm`.

## State And Persistence
The module modifies hardware registers and SMU runtime state but keeps little local state. It reads `hwmgr->pptable` for software shutdown temperature and `hwmgr->backend` for SMU PPTable fan target and SMU feature support. The fan feature enable/disable internals are compiled out, so start/stop currently succeed without toggling `GNLD_FAN_CONTROL` directly.

## Dependencies And Integration Points
Dependencies include Vega12 register definitions, SOC15 register access macros, SMU messages, PowerPlay thermal units, `vega12_hwmgr` state, and platform caps. It is called through `vega12_hwmgr_funcs` for thermal start/stop, fan speed info/RPM, fan reset, and CTF alert disable.

## Risks And Test Signals
Risks include hardware register programming mistakes, threshold unit conversion errors, compiled-out fan feature toggling causing misleading auto/manual state, and depending on initialized PPTable/backend state. Test signals include thermal controller start/stop on boot and suspend/resume, interrupt threshold behavior, sysfs fan RPM reads, fan target temperature programming, and sensor temperature consistency with SMU metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_thermal.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_thermal.h

## Purpose
`vega12_thermal.h` is the public header for Vega12 thermal and fan-control helpers. It defines temperature limits, fan mode constants, a multi-sensor temperature container, and the thermal/fan functions consumed by the Vega12 hwmgr.

## Important APIs, Types, And Functions
`struct vega12_temperature` contains edge, hotspot, HBM, VR, liquid, and PLX temperature fields. Constants define alert masks, minimum/maximum readings, valid alert thresholds, and static PWM mode IDs. The header declares thermal temperature, alert, controller, and fan RPM/control functions implemented in `vega12_thermal.c`.

## Control Flow
There is no executable flow. The declarations are wired into `vega12_hwmgr_funcs` and used by `vega12_hwmgr.c` sensor, fan-control mode, thermal-start, and thermal-stop paths.

## State And Persistence
No state is stored in the header. The declared APIs act on `struct pp_hwmgr`, whose backend and PPTable state carry thermal limits and fan target configuration.

## Dependencies And Integration Points
It depends on `hwmgr.h` for `struct pp_hwmgr`, `struct PP_TemperatureRange`, and fan speed info types. It integrates the thermal compilation unit with the hwmgr backend and generic PowerPlay callbacks.

## Risks And Test Signals
Risks are stale declarations when implementation behavior changes and unused structures/constants drifting away from SMU metric fields. Test signals are clean compilation of all hwmgr users and runtime coverage of every exported thermal/fan callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_thermal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_baco.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_baco.c

## Purpose
`vega20_baco.c` implements BACO/BAMACO support helpers for Vega20-class hardware. It detects platform support, reports BACO state from registers, enters/exits BACO through SMU messages, cleans BIOS scratch registers after exit, handles an RAS-aware enter parameter, and exposes a VDCI flush workaround.

## Important APIs, Types, And Functions
Public APIs are `vega20_get_bamaco_support()`, `vega20_baco_get_state()`, `vega20_baco_set_state()`, and `vega20_baco_apply_vdci_flush_workaround()`. `clean_baco_tbl` is a small `soc15_baco_cmd_entry` table that writes zeroes to `NBIF` BIOS scratch registers 6 and 7 after BACO exit.

## Control Flow
Support detection first requires `PHM_PlatformCaps_BACO`, then checks a raw register bit at `0x17569` and `RCC_BIF_STRAP0__STRAP_PX_CAPABLE_MASK`. State reads check `BACO_CNTL__BACO_MODE_MASK`. Setting state is idempotent: if already in the requested state it returns success. Entering BACO sets `THM_BACO_CNTL` bit 31 and sends `PPSMC_MSG_EnterBaco` with parameter 0 when RAS is absent/disabled; with RAS enabled it sends parameter 1 without the THM write. Exiting sends `PPSMC_MSG_ExitBaco` and programs `clean_baco_tbl`. The workaround sets the PPTable driver address and sends `PPSMC_MSG_BacoWorkAroundFlushVDCI`.

## State And Persistence
State is held in hardware/SMU registers, not local memory. The function reads `adev->ras_enabled` and RAS context to choose the enter path. Exiting BACO explicitly clears scratch registers, preventing stale firmware/BIOS state from persisting across transitions.

## Dependencies And Integration Points
Dependencies include SOC15 register access, Vega20 register definitions, Vega20 SMU messages, common BACO command programming, amdgpu RAS context, and `vega20_set_pptable_driver_address()`. The functions are exported through the header for use by Vega20 hwmgr callbacks.

## Risks And Test Signals
Risks include use of a magic raw register address for support detection, inverted/fragile return handling around `soc15_baco_program_registers()`, RAS-specific sequencing differences, and platform-cap mismatch. Test signals include BACO enter/exit cycles, runtime suspend/resume, RAS-enabled and RAS-disabled boards, scratch register cleanup validation, BAMACO capability reporting, and VDCI workaround execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_baco.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_baco.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_baco.h

## Purpose
`vega20_baco.h` declares the Vega20 BACO helper interface used by the power-management backend. It exposes support detection, state query, state transition, and VDCI workaround functions.

## Important APIs, Types, And Functions
The declared functions are `vega20_get_bamaco_support()`, `vega20_baco_get_state()`, `vega20_baco_set_state()`, and `vega20_baco_apply_vdci_flush_workaround()`. The header imports `hwmgr.h` for `struct pp_hwmgr` and `common_baco.h` for `enum BACO_STATE` and common BACO definitions.

## Control Flow
No runtime flow is present in the header. It allows the hwmgr implementation to call into the BACO implementation without embedding register programming details in the broader power-management code.

## State And Persistence
No state is stored. The declared operations manipulate SMU and hardware BACO state through the implementation file.

## Dependencies And Integration Points
The header is the integration boundary between Vega20 hwmgr code and common BACO state definitions. It must remain consistent with the implementation's return semantics and BACO state enum.

## Risks And Test Signals
Risks are limited to declaration drift and incorrect inclusion of common BACO types. Test signals are compile coverage for all call sites and runtime verification that callback wiring can enter, exit, and query BACO state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_baco.h -->
