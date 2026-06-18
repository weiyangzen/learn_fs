<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_yellow_carp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_yellow_carp.h

## Purpose
This header defines the Yellow Carp SMU13 APU driver/firmware interface. It provides table layouts for display watermarks, custom DPM settings, DPM clock discovery, SMU metrics, workload bits, and table IDs, similar to v13.0.4 but with a shorter metrics layout and no PMF infrastructure table payload structure.

## Important APIs, Types, and Functions
The ABI version is `SMU13_YELLOW_CARP_DRIVER_IF_VERSION`. Important types are `FloatInIntFormat_t`, `DisplayClockTable_t`, `WatermarkRowGeneric_t`, `Watermarks_t`, `DpmActivityMonitorCoeffExt_t`, `CustomDpmSettings_t`, `DfPstateTable_t`, `DpmClocks_t`, and `SmuMetrics_t`. `DpmClocks_t` includes DCF, display, DPP, SOC, VCN, DCLK, SOC voltage, DF pstate data with WCK ratio, enabled-level counts, and min/max GFX clock. `SmuMetrics_t` reports clock, activity, rail power, per-core/L3 telemetry, GFX/SOC temperatures, throttler status, socket/STAPM/APU/dGPU power, TDC/EDC values, infrastructure frequency limits, skin temperature, and device state.

## Control Flow
The file has no executable flow. `smu13/yellow_carp_ppt.c` includes it, initializes DPM clock and metrics table slots, fetches clock tables from firmware, decodes metrics for sensor reporting and SmartShift power percentage calculations, and transfers watermarks or custom DPM policy through common SMU table helpers.

## State and Persistence Behavior
DPM clocks are firmware-provided capability state cached in `smu_table->clocks_table`. Watermarks and custom DPM coefficients are policy data transferred to firmware. Metrics are transient snapshots. Table IDs define persistent protocol slots, including `TABLE_INFRASTRUCTURE_LIMITS` as a reserved/known table number even though this header does not define a companion `PmfInfo_t` like v13.0.4.

## Dependencies and Integration Points
Integration points include `yellow_carp_ppt.c`, `smu_v13_0_1_pmfw.h`, generic SMU transfer code, APU hwmon and SmartShift reporting, display/DAL watermark handling, workload selection, DPM clock enumeration, and firmware modern-standby logs. Its table and metrics layout must stay aligned with Yellow Carp firmware rather than other SMU13 APU variants.

## Risks
Yellow Carp resembles v13.0.4 but lacks the filtered/average tail and `PmfInfo_t`; shared code must not read beyond `SmuMetrics_t`. `TABLE_INFRASTRUCTURE_LIMITS` exists as an ID, but assuming the v13.0.4 payload can corrupt table transfers. WCK ratio and DF pstate interpretation are important for memory clock reporting. Mixed units across power fields can cause visible sensor errors.

## Test Signals
Build `yellow_carp_ppt.c`, validate DPM clock and metrics table sizes, compare clocks/activity/power/temperature/STAPM readings to firmware tools or hardware expectations, exercise SmartShift percentage calculations, test display watermark transitions, and verify table ID compatibility with Yellow Carp PMFW.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_yellow_carp.h -->
