# Research: subset-b-003537

This grouped report covers AMDGPU SMU v13 power-management source files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13`. Each file section is wrapped with the exact reconciliation markers required by the research cron.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/aldebaran_ppt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/aldebaran_ppt.h

## Purpose
`aldebaran_ppt.h` is the public header for the Aldebaran SMU13 power-play table implementation. It does not implement behavior directly; it defines the local DPM and PCIe table shapes consumed by the Aldebaran PPT C implementation and exposes `aldebaran_set_ppt_funcs(struct smu_context *smu)` so the SMU framework can install Aldebaran-specific function tables.

## Important APIs, Types, And Constants
The exported API is `aldebaran_set_ppt_funcs`, which is expected to set `smu->ppt_funcs` and related maps for Aldebaran. The header also defines UMD pstate selector constants for `GFXCLK`, `SOCCLK`, and `MCLK`, plus `MAX_DPM_NUMBER` and `ALDEBARAN_MAX_PCIE_CONF`.

The core data types are:

- `struct aldebaran_dpm_level`: enabled flag plus a frequency/value and secondary parameter.
- `struct aldebaran_dpm_state`: soft and hard min/max levels.
- `struct aldebaran_single_dpm_table`: count, current DPM state, and up to 16 levels.
- `struct aldebaran_pcie_table`: up to two PCIe gen/lane/lclk configurations.
- `struct aldebaran_dpm_table`: aggregate tables for SOC, GFX, memory, media, fabric, and PCIe domains.

## Control Flow And Integration
The header participates in the SMU PPT selection path: an ASIC probe path includes this header, calls `aldebaran_set_ppt_funcs`, and the implementation then uses these Aldebaran table structs while satisfying the generic `pptable_funcs` contract from `amdgpu_smu.h`. The table shape mirrors the generic SMU DPM model but remains Aldebaran-specific, so callers should treat these as implementation details rather than cross-ASIC ABI.

## State And Persistence
All structures are in-memory driver state. They model PMFW-reported or driver-derived DPM levels and PCIe capabilities; they do not persist to disk. Persistence across suspend/resume depends on the owning PPT implementation reinitializing or restoring the SMU context.

## Dependencies
The header depends on common kernel integer types and `struct smu_context` being visible to including code. It is coupled to AMDGPU SMU concepts: DPM clocks, PCIe link settings, UMD pstates, and the PPT function registration pattern.

## Risks
The fixed array sizes are a correctness boundary. If firmware exposes more than `MAX_DPM_NUMBER` DPM levels or more than `ALDEBARAN_MAX_PCIE_CONF` PCIe configurations, the implementation must clamp or reject data before storing it. Any change to these structs must stay synchronized with the Aldebaran implementation and avoid assuming generic `smu_dpm_table` layout equivalence.

## Test Signals
Useful signals are successful Aldebaran probe, populated DPM sysfs clock levels, valid PCIe level output, suspend/resume without losing DPM state, and absence of out-of-bounds writes when firmware reports edge-case table counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/aldebaran_ppt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0.c

## Purpose
`smu_v13_0.c` is the shared SMU v13 backend used by multiple AMDGPU ASIC-specific PPT implementations. It provides common firmware loading, PPT selection, table allocation/freeing, boot value extraction, SMU mailbox setup, DPM queries and soft limits, fan control, thermal/MP1 interrupt handling, BACO and reset helpers, PCIe parameter override, WBRF exclusion upload, and small shared control helpers.

## Important APIs And Functions
Firmware and PPT setup are handled by `smu_v13_0_init_microcode`, `smu_v13_0_fini_microcode`, `smu_v13_0_load_microcode`, `smu_v13_0_init_pptable_microcode`, `smu_v13_0_setup_pptable`, and `smu_v13_0_get_pptable_from_firmware`. The code chooses firmware names from the MP1 IP version, handles kicker firmware, registers firmware with PSP loading, and selects a PPT from VBIOS or PMFW firmware depending on SR-IOV, driver override, emulation mode, and `pp_table_id`.

SMU state allocation is split across `smu_v13_0_init_smc_tables`, `smu_v13_0_fini_smc_tables`, `smu_v13_0_init_power`, and `smu_v13_0_fini_power`. Boot values come from ATOM firmware and SMU info tables via `smu_v13_0_get_vbios_bootup_values`.

DPM and clocks are served by `smu_v13_0_get_dpm_ultimate_freq`, `smu_v13_0_set_soft_freq_limited_range`, `smu_v13_0_set_performance_level`, `smu_v13_0_get_boot_freq_by_index`, `smu_v13_0_get_dpm_freq_by_index`, and `smu_v13_0_set_single_dpm_table`. These functions use ASIC clock mappings, PMFW messages, and fallback boot clocks when DPM is disabled.

Thermal and interrupt handling are centered on `smu_v13_0_register_irq_handler`, `smu_v13_0_enable_thermal_alert`, `smu_v13_0_disable_thermal_alert`, `smu_v13_0_set_irq_state`, `smu_v13_0_irq_process`, and `smu_v13_0_interrupt_work`. Fan control uses `smu_v13_0_get_fan_control_mode`, `smu_v13_0_set_fan_control_mode`, `smu_v13_0_set_fan_speed_pwm`, and `smu_v13_0_set_fan_speed_rpm`.

Power, reset, and platform helpers include `smu_v13_0_get_current_power_limit`, `smu_v13_0_set_power_limit`, `smu_v13_0_gfx_off_control`, `smu_v13_0_deep_sleep_control`, `smu_v13_0_gfx_ulv_control`, `smu_v13_0_baco_enter`, `smu_v13_0_baco_exit`, `smu_v13_0_mode1_reset`, `smu_v13_0_set_gfx_power_up_by_imu`, and `smu_v13_0_update_pcie_parameters`.

## Control Flow
The common bring-up flow is: request SMU firmware unless running as SR-IOV VF, optionally register firmware with PSP, read VBIOS boot values, initialize SMU table storage, select a power-play table, program driver/tool/memory-pool DRAM addresses to PMFW, set allowed feature masks, then allow ASIC-specific PPT code to populate DPM tables and expose sysfs/hwmon controls.

Most runtime operations translate generic SMU requests into ASIC-specific indices via `smu_cmn_to_asic_specific_index`, pack the index and value into a PMFW argument, and call `smu_cmn_send_smc_msg_with_param`. The performance-level path computes target ranges from DPM tables or `smu->pstate_table`, applies ASIC-specific exceptions such as SMU 13.0.2 unsupported domains, then updates both PMFW soft limits and the cached current pstate ranges.

IRQ control configures THM and MP1 interrupt registers. The IRQ process path reacts to thermal high/low events, SMUIO critical-temperature faults with orderly poweroff, AC/DC changes, throttling notifications, and fan abnormal/recovery context IDs that rewrite soft CTF thresholds.

## State And Persistence
The file owns allocations under `smu->smu_table`, `smu->smu_dpm`, and `smu->smu_power`, plus transient cached fields such as max sustainable clocks, overdrive tables, metrics table pointers, DPM contexts, current power limit, BACO state, pstate current ranges, and WBRF table content. These are runtime kernel structures and are freed by `smu_v13_0_fini_smc_tables` or `smu_v13_0_fini_power`. User DPM and custom levels are not durable here; resume paths must restore them through ASIC-specific PPT functions.

Firmware blobs live in `adev->pm.fw` and are released by `smu_v13_0_fini_microcode`. PPT memory may point into VBIOS/firmware data or into `smu->pptable_firmware.data` for SCPM-provided tables. BACO state is cached in `smu->smu_baco.state` and must match PMFW transitions.

## Dependencies And Integration Points
The file integrates with Linux firmware loading, ATOM BIOS parsing, PSP firmware loading, AMDGPU IRQ registration, SOC15 register access, SMU common messaging (`smu_cmn_*`), RAS/throttling notification, runpm/BACO, VCN/JPEG power control, display notification, PCIe link capability management, and WBRF Wi-Fi exclusion tables.

It depends on ASIC-specific mappings installed by PPT files. If a message, clock, power source, workload, or table mapping is missing, the common helper returns `-EINVAL`, `-ENOTSUPP`, or silently skips unsupported functionality depending on the call site.

## Risks
The highest-risk areas are firmware/PPT selection, register programming, and interrupt handling. Incorrect PPT source selection can bind incompatible PMFW tables. DPM table code assumes PMFW-reported counts fit the target table arrays. Thermal interrupt code can trigger system shutdown on CTF, so source IDs and thresholds must be exact. Fan RPM math must avoid divide-by-zero and overflow; the implementation checks zero and `UINT_MAX / 8`. BACO and reset paths alter hardware access state and scratch registers, so ordering and delays matter. WBRF conversion from Hz to MHz must preserve exclusion coverage with floor/ceil rounding.

## Test Signals
Validation should cover boot on each supported MP1 v13 ASIC, firmware load and unload logs, VBIOS and driver PPT paths, SR-IOV VF no-firmware path, DPM sysfs clock levels, performance level transitions, power-limit set/get, fan PWM/RPM controls, thermal alert enable/disable, AC/DC interrupt reenable, BACO enter/exit, mode1 reset recovery, PCIe capability clamping, and WBRF add/remove updates with `WifiBandEntryNum` both nonzero and zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c

## Purpose
`smu_v13_0_0_ppt.c` is the ASIC-specific SMU v13.0.0/v13.0.10 PPT implementation for discrete GPUs. It binds generic SMU operations to v13.0.0 PMFW message IDs, table IDs, clock IDs, feature bits, workload bits, and power-source encodings. It also implements the product-specific behaviors not present in the shared v13 core: combo PPT retrieval, OD table editing, GPU metrics v1.3 formatting, software I2C over SMU, power profiles, WBRF support gating, ECC table access, and debug-mailbox reset behavior.

## Important APIs, Tables, And Functions
The externally visible API is `smu_v13_0_0_set_ppt_funcs(struct smu_context *smu)`. It installs `smu_v13_0_0_ppt_funcs`, mapping arrays, `SMU13_0_0_DRIVER_IF_VERSION`, and message control registers. It also disables GFXOFF on displayless SMU 13.0.10 devices.

Static mapping arrays are central: `smu_v13_0_0_message_map`, `smu_v13_0_0_clk_map`, `smu_v13_0_0_feature_mask_map`, `smu_v13_0_0_table_map`, `smu_v13_0_0_pwr_src_map`, `smu_v13_0_0_workload_map`, and `smu_v13_0_0_throttler_map`.

Table setup flows through `smu_v13_0_0_tables_init`, `smu_v13_0_0_allocate_dpm_context`, `smu_v13_0_0_init_smc_tables`, `smu_v13_0_0_get_pptable_from_pmfw`, `smu_v13_0_0_setup_pptable`, `smu_v13_0_0_store_powerplay_table`, `smu_v13_0_0_append_powerplay_table`, and `smu_v13_0_0_check_powerplay_table`.

Runtime behavior includes `smu_v13_0_0_set_default_dpm_table`, `smu_v13_0_0_get_smu_metrics_data`, `smu_v13_0_0_read_sensor`, `smu_v13_0_0_emit_clk_levels`, `smu_v13_0_0_force_clk_levels`, `smu_v13_0_0_get_gpu_metrics`, `smu_v13_0_0_get_power_limit`, `smu_v13_0_0_set_power_limit`, `smu_v13_0_0_get_power_profile_mode`, and `smu_v13_0_0_set_power_profile_mode`.

Overdrive support is implemented by `smu_v13_0_0_get_od_setting_limits`, `smu_v13_0_0_is_od_feature_supported`, `smu_v13_0_0_get_overdrive_table`, `smu_v13_0_0_upload_overdrive_table`, `smu_v13_0_0_set_default_od_settings`, `smu_v13_0_0_restore_user_od_settings`, `smu_v13_0_0_od_restore_table_single`, and `smu_v13_0_0_od_edit_dpm_table`.

## Control Flow
During initialization, the generic SMU layer calls the installed `init_smc_tables`, which allocates VRAM-backed PMFW tables plus kernel-side metrics, watermarks, ECC, OD, and DPM contexts. The PPT setup path pulls the combo PPT from PMFW, copies its SMC table into `driver_pptable`, optionally appends board data from ATOM `smc_dpm_info` when SCPM is not active, then derives BACO/MACO, hardware DC, OD enablement, thermal controller, `smu->od_settings`, and no-fan flags.

DPM table population queries PMFW for supported levels when each feature is enabled, otherwise falls back to boot clocks. For GFXCLK it clamps the visible max to the driver-reported game clock when present. Clock-level emission handles regular clock domains, PCIe levels from metrics plus cached PCIe table, and OD sysfs views. Forced levels compute min/max indices from a bitmask, account for fine-grained tables, and call the shared soft-frequency limiter.

OD edits validate feature support and min/max bounds from the PPT OD limit structs, mutate the cached `OverDriveTableExternal_t`, set the PMFW `FeatureCtrlMask` for the current transaction, and upload only on restore/commit. User OD persistence across suspend is implemented by preserving selected user fields when boot OD tables are refreshed.

Software I2C builds a `SwI2cRequest_t` command sequence from Linux `i2c_msg` arrays, inserts restart/stop flags, submits it through `SMU_TABLE_I2C_COMMANDS`, then copies read bytes from the driver table response. The file registers several adapters and assigns FRU/RAS EEPROM buses.

## State And Persistence
The file persists runtime state in `smu->smu_table` allocations: `driver_pptable`, combo PPT, metrics cache, watermarks, ECC table, overdrive tables, and DPM context. It stores user OD in `user_overdrive_table` and tracks whether user OD differs from boot defaults via `smu->user_dpm_profile.user_od`. Custom power profile coefficients are allocated in `smu->custom_profile_params` and are cleared when leaving custom profile mode. Unique IDs are copied from metrics into `adev->unique_id`.

## Dependencies And Integration Points
This file depends on PMFW interface headers `smu13_driver_if_v13_0_0.h`, `smu_v13_0_0_pptable.h`, and `smu_v13_0_0_ppsmc.h`, shared helpers from `smu_v13_0.c` and `smu_cmn`, ATOM BIOS board tables, Linux I2C, AMDGPU RAS, VCN/JPEG power management, thermal IRQs, BACO/runpm, WBRF, and sysfs/hwmon sensor readers.

The `pptable_funcs` table is the integration contract. Most entries delegate common operations to `smu_v13_0.c`, while v13.0.0-specific entries override PPT setup, DPM defaults, OD, metrics, I2C, reset, ECC, PCIe parsing, and power profiles.

## Risks
OD editing is a major risk area because it writes PMFW control tables and must keep `FeatureCtrlMask` transactional rather than cached. Incorrect bounds from PPT limits could permit invalid clocks, voltage offsets, fan curves, or PPT percentages. The I2C path has command-count and combined-message constraints; requests near `MAX_SW_I2C_COMMANDS` need adapter quirks to prevent overflow. Firmware-version gates for GFXOFF, compute profile optimization, ECC table support, WBRF, and RAS reset parameters must remain accurate for each IP version. Metrics fields have firmware-version quirks, especially energy accumulator validity. Mode1 reset disables MMIO access and uses a memory barrier, so callers must tolerate no hardware access during the wait.

## Test Signals
Test signals include successful probe on SMU 13.0.0 and 13.0.10, combo PPT retrieval, DPM sysfs levels for GFX/UCLK/SOC/FCLK/media/DCEF, OD sysfs read/edit/commit/restore, suspend/resume preserving OD, GPU metrics v1.3 content, fan PWM/RPM reading and setting, power profile display and custom profile programming, SMU-backed I2C FRU/RAS EEPROM access, ECC info exposure on supported firmware, mode1/mode2 reset behavior, WBRF support by firmware version, and PCIe level clamping from the SkuTable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.h

## Purpose
`smu_v13_0_0_ppt.h` is the minimal public header for the SMU v13.0.0 PPT implementation. It declares the function that binds the v13.0.0 ASIC implementation into the generic SMU framework.

## Important API
The only API is `smu_v13_0_0_set_ppt_funcs(struct smu_context *smu)`. Callers use it during ASIC initialization so the `smu_context` receives the v13.0.0 `pptable_funcs`, mapping tables, driver interface version, and message-control setup.

## Control Flow And Integration
This header is included by dispatch code and by the implementation file. The caller does not manipulate v13.0.0 internals directly; it calls the registration function, after which generic SMU code invokes behavior through `smu->ppt_funcs`.

## State And Persistence
The header itself owns no state. The declared function mutates `struct smu_context` by assigning function pointers and mapping-table pointers, but that behavior is implemented in `smu_v13_0_0_ppt.c`.

## Dependencies
The declaration depends on `struct smu_context` being declared by included AMDGPU SMU headers. It is part of the AMDGPU power-management layering contract, not a standalone module.

## Risks
The main risk is interface drift. If the implementation changes its exported registration function name or expected initialization side effects, this header and the ASIC selection code must be updated together. Because this header exposes no feature flags or table shapes, downstream code should not infer supported behavior from this file alone.

## Test Signals
Build coverage is the key signal: all translation units including this header should compile, and devices that select SMU v13.0.0 should reach a populated `smu->ppt_funcs` table and complete SMU initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_12_ppt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_12_ppt.c

## Purpose
`smu_v13_0_12_ppt.c` supplies SMU v13.0.12 data-center oriented extensions used by the broader SMU v13.0.6/v13.0.12 stack. It defines v13.0.12 feature and message mappings, initializes extra driver/system metric caches, synthesizes a driver PPT from static PMFW metrics, exposes rich GPU/XCP/system/baseboard temperature metrics, and implements RAS EEPROM SMU callbacks for bad-page metadata.

## Important APIs And Functions
The file exports mapping tables `smu_v13_0_12_feature_mask_map` and `smu_v13_0_12_message_map`, plus functions consumed by the v13.0.6-style PPT layer: `smu_v13_0_12_tables_init`, `smu_v13_0_12_tables_fini`, `smu_v13_0_12_get_max_metrics_size`, `smu_v13_0_12_get_system_metrics_size`, `smu_v13_0_12_setup_driver_pptable`, `smu_v13_0_12_is_dpm_running`, `smu_v13_0_12_get_smu_metrics_data`, `smu_v13_0_12_get_system_power`, `smu_v13_0_12_get_npm_data`, `smu_v13_0_12_get_xcp_metrics`, and `smu_v13_0_12_get_gpu_metrics`.

Temperature integration is exposed through `smu_v13_0_12_temp_funcs`, which points at `smu_v13_0_12_is_temp_metrics_supported` and `smu_v13_0_12_get_temp_metrics`.

RAS integration is exposed through `smu_v13_0_12_ras_smu_drv`, backed by `smu_v13_0_12_eeprom_smu_funcs` callbacks for table version, bad-page count, MCA address, timestamp, IPID, and erase operations.

## Control Flow
Table initialization creates a cached `SMU_TABLE_PMFW_SYSTEM_METRICS` buffer and driver tables for baseboard and GPU board temperature metrics. Driver PPT setup is lazy: if the local `PPTable_t` is not initialized, the code fetches static metrics, asks PMFW for metrics version, converts Q10 values into integer limits/frequency tables, records SOC/AID/XCD public serial numbers as AMDGPU UIDs, copies FRU product strings, captures optional board voltage, PLDM, node-power, and fast-PPT fields based on capability checks, initializes XGMI max speed/width, and marks the PPT initialized.

Runtime metrics paths convert PMFW Q10 metrics into kernel-facing integers. `smu_v13_0_12_get_smu_metrics_data` reports first-instance clocks, activity, power, and max temperatures. `smu_v13_0_12_get_system_metrics_table` refreshes the system metrics cache by requesting PMFW export, invalidating HDP, copying from the shared driver table, and updating cache time. System power and NPM readers gate on capabilities before reading system metrics.

GPU metrics aggregation handles multi-instance data: per-XCC GFX clocks/busy counters, per-VCN/JPEG media busy, XGMI link metrics, PCIe counters, HBM/AID/XCD temperatures when capability and active UMC masks allow, throttle residencies, socket energy, and firmware timestamps. XCP metrics filter the same PMFW metrics by partition instance masks.

RAS helpers are thin PMFW message wrappers. Bad-page count retries until EEPROM readiness or timeout when PMFW returns `-EBUSY`; MCA address and IPID are read as low/high 32-bit halves.

## State And Persistence
State is cached in SMU table caches, driver metric tables, `smu_table->tables[SMU_TABLE_SMU_METRICS].version`, `smu_table->driver_pptable`, `dpm_context->board_volt`, `adev->uid_info`, `adev->fru_info`, and firmware PLDM version. The RAS callbacks access persistent PMFW/RAS EEPROM data indirectly, but this file itself only sends mailbox messages and copies returned values.

## Dependencies And Integration Points
The file depends heavily on `smu_v13_0_6_ppt.h` helpers and capability checks, v13.0.12 PMFW headers, XGMI instance mapping, FRU EEPROM structures, RAS EEPROM infrastructure, AMDGPU XCP partition APIs, UMC active masks, PCIe helpers, and shared SMU table-cache/copy helpers. It is an extension module rather than a complete standalone `pptable_funcs` provider.

## Risks
The main risks are metrics schema/version drift and array/index assumptions. Many loops map hardware instance masks through `GET_INST`; invalid masks or unexpected PMFW array sizes can misreport metrics. HBM stack extraction assumes two UMC bits per stack and validates the pair mask. System metrics caching must not serve stale values past its interval for telemetry-sensitive consumers. RAS operations must handle EEPROM busy timeouts and reconstruct 64-bit fields correctly. Capability gates are important because several fields are only valid on firmware that advertises support.

## Test Signals
Strong signals include static metrics/PPT initialization on v13.0.12 hardware, correct UID and FRU population, XGMI max speed/width reporting, GPU metrics with multi-XCC and multi-VCN data, XCP metrics partition filtering, system power and node power sensors only appearing when supported, baseboard/GPU board temperature metric labels, RAS EEPROM bad-page count/address/IPID/timestamp operations, and behavior when PMFW returns `-EIO` for enabled masks or `-EBUSY` for EEPROM readiness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_12_ppt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_4_ppt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_4_ppt.c

## Purpose
`smu_v13_0_4_ppt.c` is the SMU v13.0.4/v13.0.11 APU-oriented PPT implementation. It installs a compact PPT function table for integrated devices, maps v13.0.4 PMFW messages/features/tables, manages DPM clocks and watermarks, reports GPU metrics v2.1, handles SmartShift-like APU/dGPU share sensors, and implements APU-specific performance-level and mode2 reset behavior.

## Important APIs, Maps, And Functions
The external registration API is `smu_v13_0_4_set_ppt_funcs(struct smu_context *smu)`. It sets `smu->ppt_funcs`, feature and table maps, driver interface version, `smu->is_apu = true`, and selects message-control register base indices based on the MP1 IP version.

Mapping tables include `smu_v13_0_4_message_map`, `smu_v13_0_4_feature_mask_map`, and `smu_v13_0_4_table_map`. The DPM feature set is defined by `smu_v13_0_4_dpm_features`.

Lifecycle functions are `smu_v13_0_4_init_smc_tables`, `smu_v13_0_4_fini_smc_tables`, `smu_v13_0_4_is_dpm_running`, and `smu_v13_0_4_system_features_control`. Metrics and sensors are implemented by `smu_v13_0_4_get_gpu_metrics`, `smu_v13_0_4_get_smu_metrics_data`, `smu_v13_0_4_get_current_clk_freq`, and `smu_v13_0_4_read_sensor`.

Clock and performance operations include `smu_v13_0_4_get_dpm_freq_by_index`, `smu_v13_0_4_get_dpm_level_count`, `smu_v13_0_4_emit_clk_levels`, `smu_v13_0_4_clk_dpm_is_enabled`, `smu_v13_0_4_get_dpm_ultimate_freq`, `smu_v13_0_4_set_soft_freq_limited_range`, `smu_v13_0_4_force_clk_levels`, `smu_v13_0_4_get_dpm_profile_freq`, `smu_v13_0_4_set_performance_level`, and `smu_v13_0_4_set_fine_grain_gfx_freq_parameters`.

## Control Flow
Initialization allocates VRAM-backed watermarks, DPM clocks, and metrics tables, plus kernel-side `clocks_table`, `metrics_table`, `watermarks_table`, and a GPU metrics driver table. Unlike v13.0.0, this file does not parse a large discrete-GPU PPT locally; it relies on shared `smu_v13_0_set_default_dpm_tables` to fetch `SMU_TABLE_DPMCLOCKS`.

System feature disable is conservative for low-power state transitions. When disabling outside S0ix and entering S4, it first sends a GFX device-driver reset workaround, then sends `PrepareMp1ForUnload`.

Clock queries use a mix of metrics table fields and direct PMFW messages. GFXCLK and FCLK current frequencies are requested by message; SOC/VCLK/DCLK/UCLK values come from metrics. DPM levels come from `DpmClocks_t`, with FCLK/MCLK indexed in reverse order for display. Performance-level changes compute target min/max pairs across SCLK, FCLK, SOCCLK, VCLK, and DCLK, then send hard-min/soft-max PMFW messages. VCLK values are shifted into the packed VCN argument format.

Watermark programming copies DC-provided reader/writer ranges into `Watermarks_t`, marks `WATERMARKS_EXIST`, and writes the table once if not already loaded.

## State And Persistence
Runtime state lives in allocated SMU table buffers and caches: `clocks_table`, `metrics_table`, `watermarks_table`, GPU metrics driver table, `watermarks_bitmap`, and GFX default/actual hard-min/soft-max fields. The implementation records fine-grained GFX limits from `DpmClocks_t` and uses those values for OD-like SCLK display and performance-level transitions. State is runtime-only and is torn down in `smu_v13_0_4_fini_smc_tables`.

## Dependencies And Integration Points
The file integrates with shared SMU v13 helpers for firmware status, boot values, VCN/JPEG power, driver table location, GFXOFF, generic OD editing, GFX IMU power-up, and default DPM table fetch. It depends on v13.0.4 PMFW interface headers, DC watermarks, AMDGPU metrics/hwmon consumers, and SMU common table/message helpers.

## Risks
Clock-domain mapping is the main risk. Some domains use feature gates that differ from discrete GPUs, and VCLK/DCLK min/max messages share VCN packed arguments. `smu_v13_0_4_get_dpm_level_count` leaves unsupported counts untouched, so callers must restrict clock types. Metrics scaling divides several fields by 100 or 1000; unit drift in PMFW would break sensors. Watermarks are only written once after `WATERMARKS_LOADED`, so updates after initial load need careful bitmap handling. The S4 reset workaround must remain aligned with PMFW/RLC behavior.

## Test Signals
Useful signals are APU probe with `smu->is_apu`, DPM table load, GPU metrics v2.1 output with core/L3 data, hwmon sensors for load/power/temp/voltage/SmartShift shares, DC watermark programming, GFXOFF allow/disallow, VCN/JPEG power toggles, performance-level changes across low/high/auto/profile modes, mode2 reset, and correct mailbox register setup on both IP 13.0.4 and non-13.0.4 users of this PPT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_4_ppt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_4_ppt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_4_ppt.h

## Purpose
`smu_v13_0_4_ppt.h` is the public header for the SMU v13.0.4 PPT implementation. It exposes the v13.0.4 registration function used by ASIC initialization code.

## Important API
The header declares `smu_v13_0_4_set_ppt_funcs(struct smu_context *smu)`. The implementation assigns the APU-specific `pptable_funcs`, feature and table maps, driver interface version, APU flag, and mailbox mapping.

## Control Flow And Integration
The header is a small dispatch boundary. Generic AMDGPU power-management code includes it, calls the registration function for the matching MP1 IP version, and then interacts with the implementation through `smu->ppt_funcs`.

## State And Persistence
The header owns no state. State mutation happens inside `smu_v13_0_4_set_ppt_funcs`, which updates the supplied `smu_context`; runtime allocations are handled by the implementation's `init_smc_tables` and `fini_smc_tables`.

## Dependencies
The declaration depends on `struct smu_context` from the AMDGPU SMU framework. It is coupled to the v13.0.4 implementation file and the ASIC selection logic.

## Risks
The main risk is registration mismatch: if an ASIC selects this header but the implementation's maps or mailbox setup are not appropriate for that IP, all later generic SMU calls can send wrong PMFW messages. The header does not provide compile-time protection against those semantic mismatches.

## Test Signals
Build coverage and boot coverage are the key signals. A v13.0.4/v13.0.11 device should call this function, set `smu->is_apu`, install non-null PPT functions, and complete SMU DPM initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_4_ppt.h -->
