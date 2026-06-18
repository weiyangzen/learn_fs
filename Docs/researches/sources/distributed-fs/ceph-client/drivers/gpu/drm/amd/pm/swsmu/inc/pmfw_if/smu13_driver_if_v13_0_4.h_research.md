<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_v13_0_4.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_v13_0_4.h

## Purpose
This header defines the SMU13.0.4 APU firmware interface. It covers display watermarks, custom DPM coefficients, DPM clock discovery with DF pstate and WCK ratio, SMU metrics with APU/PMF-oriented telemetry, infrastructure limits, ISP tile masks, workload bits, and table IDs.

## Important APIs, Types, and Functions
The ABI version is `SMU13_0_4_DRIVER_IF_VERSION`. Major types are `FloatInIntFormat_t`, `WatermarkRowGeneric_t`, `Watermarks_t`, `DpmActivityMonitorCoeffExt_t`, `CustomDpmSettings_t`, `DfPstateTable_t`, `DpmClocks_t`, `SmuMetrics_t`, and `PmfInfo_t`. The metrics table includes clocks, GFX/UVD activity, rail voltage/current/power, per-core and L3 telemetry, GFX/SOC temperatures, throttler status, socket/STAPM/APU/dGPU power, TDC/EDC values, infrastructure frequency limits, skin/device/filtered temperature fields, averaged clocks/activity/DRAM bandwidth, average socket/core power, C0 residency, and `MetricsCounter`.

## Control Flow
The header has no control flow. `smu13/smu_v13_0_4_ppt.c` allocates DPM clocks and metrics tables, requests clock tables from firmware, decodes `SmuMetrics_t` for sensors and power-limit reporting, and uses the table IDs to transfer watermarks, custom DPM data, DPM clocks, modern standby logs, metrics, and infrastructure limits. ISP tile masks support firmware messages that power or query ISP blocks.

## State and Persistence Behavior
`DpmClocks_t` is firmware-discovered capability state cached by the driver. `Watermarks_t` and `CustomDpmSettings_t` are policy tables. `SmuMetrics_t` is mutable telemetry updated by firmware, and `PmfInfo_t` is platform-management limit information for STAPM and PPT ranges. ISP tile masks represent command arguments or status decoding rather than stored driver state.

## Dependencies and Integration Points
Integration points include `smu_v13_0_4_ppt.c`, `smu_v13_0_4_pmfw.h`, SMU table transfer helpers, APU hwmon reporting, PMF infrastructure-limit consumers, display watermark/DAL flows, DPM clock enumeration, workload policy, and ISP tile power management. Firmware must agree on DPM counts and table slot numbers.

## Risks
`TABLE_INFRASTRUCTURE_LIMITS` is an extra table compared with smaller APU headers and must stay aligned with PMF use. Metrics fields mix milliwatts, watts, MHz, centi-Celsius, bandwidth counters, and percentages. `MetricsCounter` semantics are firmware-specific and can be misinterpreted as time. WCK ratio in DF pstate entries is part of memory clock interpretation; ignoring it can report or select wrong memory behavior.

## Test Signals
Build `smu_v13_0_4_ppt.c`, validate DPM clock table transfer and enabled-level counts, inspect PMF infrastructure limits, compare sensor units for STAPM/APU/dGPU/socket power, exercise display pstate and memory retraining watermarks, verify averaged metrics update over time, and test ISP tile mask commands where hardware exposes those blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_v13_0_4.h -->
