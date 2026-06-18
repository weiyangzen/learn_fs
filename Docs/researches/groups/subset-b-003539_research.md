# subset-b-003539 research

Grouped research for AMDGPU SWSMU SMU13/SMU14 power-management platform-table sources. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.c

## Purpose
Implements the SMU13.0.7 discrete-GPU PowerPlay table backend for AMDGPU SWSMU. It maps generic SMU messages, clocks, features, tables, power sources, and workload profiles to SMU13.0.7 firmware IDs, loads and validates the platform power table, initializes SMC/DPM/metrics/overdrive state, exposes sysfs-visible clocks, sensors, thermal limits, power limits, power profiles, fan controls, reset hooks, BACO/GPO/WBRF hooks, and installs the `pptable_funcs` used by the common SMU layer.

## Important APIs, Types, And Functions
- Static mapping tables include `smu_v13_0_7_message_map`, `smu_v13_0_7_clk_map`, `smu_v13_0_7_feature_mask_map`, `smu_v13_0_7_table_map`, `smu_v13_0_7_pwr_src_map`, `smu_v13_0_7_workload_map`, and `smu_v13_0_7_throttler_map`.
- PowerPlay setup is split across `smu_v13_0_7_setup_pptable`, `smu_v13_0_7_get_pptable_from_pmfw`, `smu_v13_0_7_store_powerplay_table`, `smu_v13_0_7_append_powerplay_table`, and `smu_v13_0_7_check_powerplay_table`.
- Runtime table/DPM setup uses `smu_v13_0_7_tables_init`, `smu_v13_0_7_allocate_dpm_context`, `smu_v13_0_7_init_smc_tables`, and `smu_v13_0_7_set_default_dpm_table`.
- Telemetry is handled by `smu_v13_0_7_get_smu_metrics_data`, `smu_v13_0_7_read_sensor`, `smu_v13_0_7_get_gpu_metrics`, and `smu_v13_0_7_get_throttler_status`.
- User tuning paths include `smu_v13_0_7_emit_clk_levels`, `smu_v13_0_7_force_clk_levels`, `smu_v13_0_7_od_edit_dpm_table`, `smu_v13_0_7_set_default_od_settings`, `smu_v13_0_7_restore_user_od_settings`, `smu_v13_0_7_get_power_limit`, `smu_v13_0_7_set_power_limit`, `smu_v13_0_7_get_power_profile_mode`, and `smu_v13_0_7_set_power_profile_mode`.
- `smu_v13_0_7_ppt_funcs` is the exported integration contract; `smu_v13_0_7_set_ppt_funcs` installs it and initializes the debug-capable message mailbox.

## Control Flow
During device bring-up, `smu_v13_0_7_set_ppt_funcs` assigns all mapping arrays and the driver interface version, then `smu_v13_0_7_setup_pptable` fetches the combo PPTABLE from PMFW, copies its SMC PPTABLE into `driver_pptable`, optionally appends board data from the ATOM `smc_dpm_info` table when SCPM is not active, and records platform capabilities such as hardware DC control, BACO/MACO, thermal controller type, and overdrive enablement. SMC table initialization allocates VRAM-backed firmware tables for PPTABLE, watermarks, metrics, I2C, overdrive, PM status logging, activity monitor coefficients, combo PPTABLE, and Wi-Fi band data, then allocates software metrics/watermark buffers and a GPU metrics driver cache.

At runtime, DPM tables are populated from firmware for enabled clocks or from boot values when a feature is disabled. Metrics reads update the SMU metrics table and convert firmware units into pp sensors and GPU metrics structs. Clock-level sysfs output selects the correct DPM table, marks current levels, prints PCIE levels, or prints supported overdrive ranges. Clock forcing translates bitmasks into soft min/max frequency messages. Overdrive edits validate each input against PPTABLE min/max limits, update an external overdrive table, and only upload to firmware on commit or restore. Power-limit writes use the base SetPptLimit path up to the firmware message limit and use the overdrive PPT percentage field for higher limits when overdrive is enabled.

## State And Persistence
Persistent firmware-visible state lives in SMU tables in VRAM and PMFW state: allowed feature masks, DPM limits, power limit, overdrive table, power profile activity coefficients, DF C-state, BACO/GPO state, and WBRF exclusion ranges. Driver state includes `smu_table` pointers for power-play, driver PPTABLE, combo PPTABLE, watermarks, metrics, boot/user/current overdrive tables, DPM context, current power limit, custom profile parameters, user overdrive flag, pstate table, and SMU message-control registers. Resume paths preserve user overdrive values in `user_overdrive_table` and restore them after a boot table refresh. Mode1 reset sets `adev->no_hw_access` with a memory barrier after sending the debug mailbox reset.

## Dependencies And Integration Points
The file depends on AMDGPU core device state, ATOM BIOS helpers, SMU common helpers, SMU13.0 common functions, generated SMU13.0.7 firmware interface headers, ASIC register definitions, RAS status checks, PCIe helpers, and the SWSMU `pptable_funcs` dispatch table. Integration points include sysfs pp_dpm and OD interfaces, hwmon/power sensors, GPU metrics IOCTL/sysfs plumbing, VCN/JPEG power gating, thermal alert registration in shared SMU13 code, BACO runtime power management, MGPU fan boost, WBRF coexistence, and firmware mailbox messages.

## Risks And Edge Cases
The PPTABLE path assumes the combo table layout matches `struct smu_13_0_7_powerplay_table`; mismatched firmware data can corrupt limits or board data. Overdrive commit intentionally ignores `FeatureCtrlMask` when caching user data, so changes to the table layout around the voltage-offset field are risky. Power-limit handling has a two-path boundary at `MsgLimits.Power`; incorrect current-limit tracking can leave an overdrive PPT override active. Metrics contain pre/post deep-sleep values and firmware-version-dependent energy behavior, so stale or unit-mismatched metrics can mislead userspace. PCIE override logic mutates the cached PCIE table while enforcing host caps. Mode1 reset disables hardware access globally and depends on callers honoring `no_hw_access`.

## Test Signals
Useful signals include successful combo PPTABLE retrieval, correct ATOM board table append when SCPM is off, DPM table fallback to boot clocks when features are disabled, sysfs clock lists showing current levels, OD edits rejecting out-of-range values, OD restore preserving user values across suspend/resume, power limit transitions below and above the message limit, metrics fields matching SMU telemetry units, PCIE parameter overrides respecting link caps, WBRF support gating on firmware version, and mode1 reset setting `no_hw_access` only after a successful debug message.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.h

## Purpose
Declares the SMU13.0.7 PPT backend entry point used by the AMDGPU SWSMU dispatcher.

## Important APIs, Types, And Functions
- The only public symbol is `smu_v13_0_7_set_ppt_funcs(struct smu_context *smu)`.
- The include guard `__SMU_V13_0_7_PPT_H__` prevents duplicate declarations.

## Control Flow
SMU device-selection code includes this header and calls `smu_v13_0_7_set_ppt_funcs` when the probed MP1/SMU IP version corresponds to SMU13.0.7. The implementation then installs the PPT function table, firmware mapping arrays, driver interface version, and mailbox setup.

## State And Persistence
The header owns no state. Its declared function mutates the caller-provided `struct smu_context` when invoked by platform setup.

## Dependencies And Integration Points
The declaration requires `struct smu_context` to be visible from surrounding SWSMU headers. It connects SMU13.0.7-specific code to common AMDGPU SMU initialization.

## Risks And Edge Cases
Prototype drift between this header and `smu_v13_0_7_ppt.c` would break platform setup at build time. Selecting this entry point for the wrong IP revision would install message and table mappings that do not match firmware.

## Test Signals
Build coverage should confirm the declaration matches the implementation. Runtime probe should show `smu->ppt_funcs`, mapping tables, and `smc_driver_if_version` populated after this entry point is called.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/yellow_carp_ppt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/yellow_carp_ppt.c

## Purpose
Implements the SMU13 Yellow Carp APU PPT backend. It maps Yellow Carp firmware messages, features, and tables, initializes APU SMC tables, controls VCN/JPEG/GFXOFF/reset behavior, reads APU metrics and sensors, manages display watermarks, exposes DPM and OD sysfs clock views, and installs a Yellow Carp `pptable_funcs` table.

## Important APIs, Types, And Functions
- Mapping and feature contracts are `yellow_carp_message_map`, `yellow_carp_feature_mask_map`, `yellow_carp_table_map`, and `yellow_carp_dpm_features`.
- Table lifetime is handled by `yellow_carp_init_smc_tables` and `yellow_carp_fini_smc_tables`.
- Power and media controls include `yellow_carp_system_features_control`, `yellow_carp_dpm_set_vcn_enable`, `yellow_carp_dpm_set_jpeg_enable`, `yellow_carp_post_smu_init`, `yellow_carp_mode2_reset`, and common SMU13 GFXOFF helpers.
- Telemetry and watermarks use `yellow_carp_get_smu_metrics_data`, `yellow_carp_read_sensor`, `yellow_carp_set_watermarks_table`, `yellow_carp_get_gpu_metrics`, and `yellow_carp_get_gfxoff_status`.
- DPM and tuning helpers include `yellow_carp_set_default_dpm_tables`, `yellow_carp_get_dpm_ultimate_freq`, `yellow_carp_set_soft_freq_limited_range`, `yellow_carp_emit_clk_levels`, `yellow_carp_force_clk_levels`, `yellow_carp_od_edit_dpm_table`, `yellow_carp_set_performance_level`, and `yellow_carp_set_fine_grain_gfx_freq_parameters`.

## Control Flow
`yellow_carp_set_ppt_funcs` marks the SMU as an APU, installs feature/table/message maps, sets the Yellow Carp driver interface version, and initializes common SMU13 message control. Initialization allocates VRAM-backed watermarks, DPM clocks, and metrics tables plus software buffers and a GPU metrics v2.1 cache. Runtime feature shutdown sends `PrepareMp1ForUnload` only outside S0ix. Post-init explicitly enables GFXOFF before later allow/disallow control. Media power gating sends VCN/JPEG up/down messages, while mode2 reset sends `GfxDeviceDriverReset` with reset mode 2.

DPM data is read from the `DpmClocks_t` table. If a DPM feature is disabled, ultimate frequency queries fall back to VBIOS boot clocks. GFXCLK exposes fine-grain min/max through `gfx_default_hard_min_freq`, `gfx_default_soft_max_freq`, and the actual user-selected values. Performance-level changes compute target ranges for SCLK, FCLK, SOCCLK, VCLK, and DCLK and send the matching hard-min or soft-max SMU messages. Watermark programming copies display-provided reader/writer ranges into the firmware table and uploads it once per watermark load.

## State And Persistence
Driver state includes `clocks_table`, `metrics_table`, `watermarks_table`, the GPU metrics cache, `watermarks_bitmap`, fine-grain GFX min/max fields, the current forced DPM level, and `smu->is_apu`. Firmware-visible state includes watermarks, soft/hard clock limits, VCN/JPEG power state, GFXOFF state, and reset state. No disk state is stored.

## Dependencies And Integration Points
The file depends on AMDGPU core, `smu_v13_0` common helpers, Yellow Carp generated firmware interface headers, SMU common table/message helpers, SOC15 register access for GFXOFF status, display watermark input, VCN/JPEG harvest state through common device structures, and the SWSMU `pptable_funcs` table. Userspace observes the code through sensors, GPU metrics, OD clock sysfs, forced performance levels, and media power-management behavior.

## Risks And Edge Cases
Metrics units differ by field: some values are divided by 100, some converted to fixed-point power, and GPU metrics v2.1 stores several raw firmware fields. SmartShift share calculation divides by STAPM limits and must guard zero limits. DPM-level ordering for memory/FCLK reverses indexes for display, and disabled DPM paths return boot frequencies scaled from 10 kHz to MHz. OD edits are only allowed in manual DPM mode and only cover GFX min/max. Watermarks are uploaded only once after `WATERMARKS_LOADED`, so later range changes require bitmap management elsewhere. The code assumes IP versions 13.0.1/13.0.3/13.0.8 for UMD pstate defaults.

## Test Signals
Signals include successful allocation/freeing of all SMC software tables, GFXOFF enable during post-init, no unload message during S0ix, VCN/JPEG up/down messages, mode2 reset message, DPM tables populated from firmware, fallback boot clocks when features are disabled, GFX fine-grain OD range validation in manual mode, watermark upload and bitmap transitions, GFXOFF status register decoding, and GPU metrics v2.1 fields matching firmware metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/yellow_carp_ppt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/yellow_carp_ppt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/yellow_carp_ppt.h

## Purpose
Declares the Yellow Carp SMU13 PPT backend setup function.

## Important APIs, Types, And Functions
- The header exports `yellow_carp_set_ppt_funcs(struct smu_context *smu)`.
- The include guard is `__YELLOW_CARP_PPT_H__`.

## Control Flow
The platform selection code calls `yellow_carp_set_ppt_funcs` for Yellow Carp-class APUs. The implementation installs APU-specific `pptable_funcs`, message mappings, feature mappings, table mappings, and driver interface version.

## State And Persistence
The header itself stores no state. Its entry point mutates `struct smu_context`, including `ppt_funcs`, `feature_map`, `table_map`, `is_apu`, and message-control setup.

## Dependencies And Integration Points
It depends on the SWSMU context type from common headers and links Yellow Carp platform selection to the implementation in `yellow_carp_ppt.c`.

## Risks And Edge Cases
Calling this setup function for the wrong firmware family would install Yellow Carp message IDs against incompatible PMFW. Header/implementation mismatch would fail compilation or platform setup.

## Test Signals
Build should compile callers and implementation with the same prototype. Runtime probe should show `is_apu` set and Yellow Carp mappings installed for the correct IP revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/yellow_carp_ppt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu14/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu14/Makefile

## Purpose
Adds SMU14 manager objects to the AMDGPU powerplay build.

## Important APIs, Types, And Functions
- `SMU14_MGR` lists the SMU14 object files: `smu_v14_0.o`, `smu_v14_0_0_ppt.o`, and `smu_v14_0_2_ppt.o`.
- `AMD_SWSMU_SMU14MGR` prefixes those objects with `$(AMD_SWSMU_PATH)/smu14/`.
- `AMD_POWERPLAY_FILES += $(AMD_SWSMU_SMU14MGR)` contributes them to the parent AMDGPU powerplay object list.

## Control Flow
When the parent powerplay makefiles include this file, the SMU14 object list is expanded into source-tree-relative object paths and appended to the global AMD powerplay build variable. Kbuild then compiles and links the SMU14 common layer and PPT backends into the AMDGPU driver when the surrounding configuration enables AMDGPU powerplay support.

## State And Persistence
The file has no runtime state. Its persistent effect is build graph membership for SMU14 sources.

## Dependencies And Integration Points
It depends on the parent make environment defining `AMD_SWSMU_PATH` and `AMD_POWERPLAY_FILES`. It integrates SMU14 sources with the larger AMDGPU SWSMU build and must stay aligned with files present in the `smu14` directory.

## Risks And Edge Cases
Removing an object here drops the corresponding platform backend from the driver even if the source remains. Adding a missing object causes build failure. The listed SMU14.0.2 backend is outside this work item but is part of the same build group, so dependency changes in common SMU14 code can affect it.

## Test Signals
Kbuild should compile all listed objects without missing-file errors. Link output should include SMU14 common and PPT setup symbols used by AMDGPU IP-version selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu14/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu14/smu_v14_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu14/smu_v14_0.c

## Purpose
Provides the shared SMU14 support layer used by SMU14 PPT backends. It handles SMU firmware loading, PPTABLE selection, common SMC table allocation, power context allocation, VBIOS boot value parsing, driver/tool/memory-pool table address notification, allowed feature masks, GFXOFF and system feature control, display-change notification, power limit access, thermal/MP1 interrupt plumbing, DPM table queries, clock limit messages, performance-level ranges, media power gating, deep-sleep and ULV features, BACO/BAMACO transitions, IMU GFX power-up, common OD editing, and thermal alert enablement.

## Important APIs, Types, And Functions
- Firmware/PPTABLE path: `smu_v14_0_init_microcode`, `smu_v14_0_load_microcode`, `smu_v14_0_fini_microcode`, `smu_v14_0_init_pptable_microcode`, `smu_v14_0_get_pptable_from_firmware`, and `smu_v14_0_setup_pptable`.
- Table and power lifetime: `smu_v14_0_init_smc_tables`, `smu_v14_0_fini_smc_tables`, `smu_v14_0_init_power`, and `smu_v14_0_fini_power`.
- Firmware communication helpers include `smu_v14_0_check_fw_status`, `smu_v14_0_notify_memory_pool_location`, `smu_v14_0_set_driver_table_location`, `smu_v14_0_set_tool_table_location`, `smu_v14_0_set_allowed_mask`, and `smu_v14_0_system_features_control`.
- DPM and performance helpers include `smu_v14_0_get_dpm_ultimate_freq`, `smu_v14_0_set_soft_freq_limited_range`, `smu_v14_0_set_hard_freq_limited_range`, `smu_v14_0_set_single_dpm_table`, and `smu_v14_0_set_performance_level`.
- Interrupt and thermal helpers include `smu_v14_0_register_irq_handler`, `smu_v14_0_enable_thermal_alert`, `smu_v14_0_disable_thermal_alert`, `smu_v14_0_set_irq_state`, and `smu_v14_0_irq_process`.
- BACO/media/control helpers include `smu_v14_0_set_vcn_enable`, `smu_v14_0_set_jpeg_enable`, `smu_v14_0_run_btc`, `smu_v14_0_gpo_control`, `smu_v14_0_deep_sleep_control`, `smu_v14_0_gfx_ulv_control`, `smu_v14_0_baco_enter`, `smu_v14_0_baco_exit`, and `smu_v14_0_set_gfx_power_up_by_imu`.

## Control Flow
Firmware initialization skips SR-IOV VFs, derives the firmware prefix from MP1 IP version, optionally requests kicker firmware, records the SMC firmware version, and registers the firmware with PSP loading when appropriate. Direct loading writes firmware words to MP1 SRAM, toggles MP1 reset, and polls firmware interrupt-enable flags. PPTABLE setup chooses a driver-provided firmware PPTABLE by `pptable_id` or VBIOS PPTABLE for SR-IOV/no-id cases; SCPM plus PSP loading can also register a PPTABLE firmware blob for PSP.

SMC table initialization allocates common driver PPTABLE, max sustainable clocks, optional overdrive tables, and combo PPTABLE memory. Boot values are parsed from ATOM firmware-info and SMU-info table revisions. Runtime helpers notify PMFW of VRAM table addresses, feature masks, GFXOFF permissions, display UCLK fast-switch needs, and power-source/power-limit changes. IRQ registration wires THM high/low events and MP1 SMU-to-host interrupts into the AMDGPU IRQ core; processing schedules software CTF work or adjusts thermal thresholds for fan abnormal/recovery events. DPM helpers query firmware for min/max/count/indexed frequencies, set soft/hard limits, and construct forced performance profiles across GFX, memory, SOC, VCN, and FCLK.

## State And Persistence
State includes requested firmware in `adev->pm.fw`, PSP firmware accounting, `smu->pptable_firmware`, VBIOS boot values, allocated SMC table buffers, overdrive buffers, combo PPTABLE, power context, DPM contexts, current power limit, `pstate_table` current ranges, IRQ source registration, thermal range, BACO state, and `smu_baco` platform capability. Firmware-visible persistent state includes SMU code in MP1/PSP, selected PPTABLE, feature masks, DRAM table addresses, GFXOFF permission, DPM min/max limits, power limits, VCN/JPEG power state, deep-sleep feature toggles, ULV, BACO state, and thermal interrupt thresholds.

## Dependencies And Integration Points
The file depends on Linux firmware loading, AMDGPU firmware/PSP infrastructure, ATOM BIOS helpers, SMU common mailbox/table helpers, SOC15 MMIO access, THM/MP1 register definitions, AMDGPU IRQ core, VCN/JPEG harvest configuration, runtime power management, and SWSMU PPT backends that call these shared functions. Userspace sees its effects through power limits, performance levels, media engines, thermal events, BACO runtime suspend, and metrics populated by backend files.

## Risks And Edge Cases
Firmware header version parsing is strict for driver PPTABLE extraction; unsupported versions fail setup. Direct firmware load loops skip the first and last dwords and poll `usec_timeout`, so firmware layout assumptions matter. Table allocation sizes depend on backend `SMU_TABLE_INIT` ordering before common allocation. IRQ code has separate APU vs dGPU MP1 registers, and one parameter is misspelled `tyep` but unused. DPM range setters round soft max values and use encoded clock IDs; wrong mapping arrays in a backend will send valid messages for the wrong clock. BACO exit clears VBIOS scratch registers for reinit, which is sensitive to runtime PM sequencing.

## Test Signals
Signals include firmware request names for SMU14.0.2/14.0.3 and kicker firmware, successful PSP firmware accounting, MP1 interrupt-enable polling success, PPTABLE selection by override/id/VBIOS, correct boot clocks from ATOM revisions, balanced SMC/power allocation cleanup, DRAM address messages with high/low halves, allowed mask high then low messages, GFXOFF gating by IP version and feature mask, thermal IRQ enable/disable and fan abnormal threshold adjustment, DPM min/max/index queries, forced performance levels updating pstate current ranges, VCN/JPEG skipping harvested instances, and BACO state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu14/smu_v14_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu14/smu_v14_0_0_ppt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu14/smu_v14_0_0_ppt.c

## Purpose
Implements the SMU14.0.0/14.0.1/14.0.4/14.0.5 APU PPT backend. It maps SMU14.0.0 firmware messages, features, and table IDs, initializes APU metrics/DPM/watermark tables, exposes sensors and GPU metrics v3.0, manages VCN/VPE/ISP/UMSCH/MALL controls, handles APU DPM table differences between SMU14.0.0 and SMU14.0.1, implements fine-grain GFX OD, and installs the SMU14.0.0 PPT function table.

## Important APIs, Types, And Functions
- Platform mappings are `smu_v14_0_0_message_map`, `smu_v14_0_0_feature_mask_map`, `smu_v14_0_0_table_map`, and `smu_v14_0_0_dpm_features`.
- Table and feature setup uses `smu_v14_0_0_init_smc_tables`, `smu_v14_0_0_fini_smc_tables`, `smu_v14_0_0_system_features_control`, and `smu_v14_0_0_is_dpm_running`.
- Telemetry paths are `smu_v14_0_0_get_smu_metrics_data`, `smu_v14_0_0_read_sensor`, and `smu_v14_0_0_get_gpu_metrics`.
- DPM helpers include version-specific `smu_v14_0_1_get_dpm_freq_by_index`, `smu_v14_0_0_get_dpm_freq_by_index`, `smu_v14_0_1_get_dpm_ultimate_freq`, `smu_v14_0_0_get_dpm_ultimate_freq`, `smu_v14_0_0_emit_clk_levels`, `smu_v14_0_0_set_soft_freq_limited_range`, `smu_v14_0_0_force_clk_levels`, and `smu_v14_0_common_set_performance_level`.
- Media and platform controls include `smu_v14_0_0_set_vpe_enable`, `smu_v14_0_0_set_isp_enable`, `smu_v14_0_0_set_umsch_mm_enable`, `smu_v14_0_common_get_dpm_table`, `smu_v14_0_common_set_mall_enable`, and `smu_v14_0_0_restore_user_od_settings`.
- `smu_v14_0_0_set_ppt_funcs` installs the ops table and selects the driver interface version by MP1 IP version.

## Control Flow
PPT setup marks the context as APU, installs mapping tables and `smu_v14_0_0_ppt_funcs`, chooses driver interface version `0x7` for SMU14.0.0/14.0.4/14.0.5 or `0x6` for SMU14.0.1, then initializes a mailbox using MP1 C2PMSG 66/82/90. SMC table initialization allocates watermarks, DPM clocks large enough for either `DpmClocks_t` or `DpmClocks_t_v14_0_1`, SMU metrics, and a GPU metrics v3.0 cache.

Metrics reads refresh `SMU_TABLE_SMU_METRICS`, convert selected members for pp sensors, and populate a v3.0 metrics structure with temperatures, IPU/core activity, memory/IPU traffic, power, clocks, throttle residencies, and boot-time counter. Watermark setup copies display reader/writer ranges into DCFCLK/SOCCLK rows and uploads once. DPM helpers branch on MP1 IP 14.0.1 for dual-VCN clock arrays and memory/FCLK layout, otherwise use the SMU14.0.0 table. Performance-level changes query ultimate/profile frequencies for SCLK, FCLK, SOCCLK, VCLK/DCLK, and VCLK1/DCLK1 where present, then sends the backend-specific hard-min/soft-max messages.

## State And Persistence
Driver state includes metrics, clocks, watermarks, GPU metrics cache, watermarks bitmap, APU flag, message-control register configuration, default and actual GFX min/max frequencies, user OD flag, and cached DPM tables. Firmware-visible state includes watermarks, DPM frequency limits, VCN/JPEG power through shared SMU14 helpers, VPE/ISP/UMSCH power state, MALL power-gating controller/state on SMU14.0.1, GFX IMU power-up, and mode2 reset state.

## Dependencies And Integration Points
The file depends on generated SMU14.0.0 firmware interface headers, common SMU14 helpers in `smu_v14_0.c`, SMU common table/message helpers, AMDGPU IP-version detection, display watermark data, VCN/JPEG/VPE/ISP/UMSCH users, and the SWSMU `pptable_funcs` dispatcher. Userspace integration includes pp sensors, GPU metrics v3.0, OD clock sysfs, forced performance levels, and DPM clock table consumers.

## Risks And Edge Cases
The backend handles multiple IP revisions with two DPM table layouts; wrong IP detection can index the wrong clock arrays. Several wrapper helpers ignore return values from version-specific subcalls and return zero, so failures can be masked in common DPM queries. VCLK1/DCLK1 are intentionally ignored on non-14.0.1 paths. Metrics units depend on firmware version for GFX activity and use fixed-point socket power conversion for pp sensors while GPU metrics store raw fields. `smu_v14_0_0_set_soft_freq_limited_range` returns the last message result and can send only min for ISP clocks. MALL control is only initialized for 14.0.1.

## Test Signals
Signals include correct driver interface version per IP revision, successful mailbox register setup, allocation of the larger DPM clocks buffer, metrics v3.0 field population, sensor reads for power/temperature/SmartShift shares, watermark upload once per bitmap state, DPM index/count/min/max for both 14.0.0 and 14.0.1 table layouts, VCLK1/DCLK1 only on 14.0.1, fine-grain GFX defaults initialized from the selected table type, OD restore sending hard-min and soft-max GFX messages, VPE/ISP/UMSCH power messages, and MALL messages only on 14.0.1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu14/smu_v14_0_0_ppt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu14/smu_v14_0_0_ppt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu14/smu_v14_0_0_ppt.h

## Purpose
Declares the setup entry point for the SMU14.0.0-family PPT backend.

## Important APIs, Types, And Functions
- The sole exported declaration is `smu_v14_0_0_set_ppt_funcs(struct smu_context *smu)`.
- The include guard is `__SMU_V14_0_0_PPT_H__`.

## Control Flow
AMDGPU SMU IP-version selection includes this header and invokes `smu_v14_0_0_set_ppt_funcs` for supported SMU14.0.0-family APUs. The implementation installs the backend function table, firmware mappings, table mappings, APU flag, driver interface version, and mailbox registers.

## State And Persistence
The header has no state. The declared function mutates `struct smu_context` and indirectly controls later firmware-visible state through the installed callbacks.

## Dependencies And Integration Points
It depends on the SWSMU context definition and integrates the SMU14.0.0 PPT implementation with common AMDGPU SMU initialization.

## Risks And Edge Cases
A wrong platform selector would install SMU14.0.0 message mappings against incompatible PMFW. Prototype drift would break build-time integration.

## Test Signals
Build should validate the prototype against callers and implementation. Runtime probe should confirm `ppt_funcs`, `feature_map`, `table_map`, `is_apu`, and the selected SMU14 driver interface version are set after this function runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu14/smu_v14_0_0_ppt.h -->
