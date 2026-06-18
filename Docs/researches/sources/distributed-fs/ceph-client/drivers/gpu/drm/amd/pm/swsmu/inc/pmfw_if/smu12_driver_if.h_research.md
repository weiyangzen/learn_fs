<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu12_driver_if.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu12_driver_if.h

## Purpose
This header is the SMU12 Renoir-era APU driver/firmware interface. It defines the table layouts for display watermarks, custom DPM tuning, DPM clock discovery, and SMU metrics, along with clock IDs, workload bits, table IDs, and throttler status mapping.

## Important APIs, Types, and Functions
The ABI version is `SMU12_DRIVER_IF_VERSION`. Important types are `FloatInIntFormat_t`, `DisplayClockTable_t`, `WatermarkRowGeneric_t`, `Watermarks_t`, `DpmActivityMonitorCoeffExt_t`, `CustomDpmSettings_t`, `DpmClock_t`, `DpmClocks_t`, `CLOCK_IDs_e`, and `SmuMetrics_t`. `DpmClocks_t` gives enabled levels for DCFCLK, SOCCLK, FCLK, memory clock, VCLK, and DCLK. `SmuMetrics_t` provides clock-frequency arrays, average GFX/SOC/VCN/FCLK activity, voltage/current/power rails, fan PWM, socket power, CPU core and L3 telemetry, thermal data, SmartShift/STAPM limits, dGPU/APU power, and TDC/EDC values.

## Control Flow
The file has no code flow. `smu12/renoir_ppt.c` includes it to size `SMU_TABLE_DPMCLOCKS` and `SMU_TABLE_SMU_METRICS`, pull clock tables from firmware, decode metrics for `hwmon` and power profile reporting, and use throttler bits when mapping firmware status into driver-visible throttle reasons. Display code uses the watermark rows for SOC/DCF clock and memory ranges.

## State and Persistence Behavior
State lives in firmware and the driver's cached table buffers. DPM clocks are persistent capability/policy data until reset, resume, or firmware reload. Watermark and custom DPM settings are policy payloads. Metrics are sampled telemetry that changes as firmware updates the table. Table IDs define the persistent protocol slots used by `SMC_MSG_TransferTable*`.

## Dependencies and Integration Points
The header integrates with `renoir_ppt.c`, SMU12 PMFW message headers, common SMU table allocation and transfer helpers, display watermark/DAL paths, APU hwmon sensors, SmartShift/power-limit reporting, and workload selection. It depends on consumers preserving exact enum order for `CLOCK_IDs_e` and `TABLE_*` values.

## Risks
`CurrentSocketPower` is documented in watts while several power arrays are milliwatts, so unit confusion can create bad user-visible readings. Clock ID order controls metrics array decoding and must match firmware. Incorrect DPM count constants can truncate or overread firmware tables. Thermal and electrical throttler bit positions need to stay aligned with firmware or throttle diagnostics become misleading.

## Test Signals
Build `renoir_ppt.c`, confirm table transfer success for DPM clocks and metrics, inspect `hwmon` power/current/voltage/temperature units, validate display pstate transitions and memory retraining watermarks, exercise workload masks, and compare throttler status against induced SPL/FPPT/SPPT, thermal, TDC, PROCHOT, and EDC events where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu12_driver_if.h -->
