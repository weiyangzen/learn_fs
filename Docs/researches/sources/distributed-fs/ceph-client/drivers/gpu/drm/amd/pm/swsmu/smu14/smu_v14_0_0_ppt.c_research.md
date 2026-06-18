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
