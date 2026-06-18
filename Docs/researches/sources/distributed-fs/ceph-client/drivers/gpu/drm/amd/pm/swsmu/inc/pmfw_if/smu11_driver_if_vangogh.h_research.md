<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu11_driver_if_vangogh.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu11_driver_if_vangogh.h

## Purpose
This header defines the SMU firmware interface used by the Van Gogh APU power-management driver. It is a compact APU-oriented ABI for display watermarks, custom DPM activity monitor tuning, DPM clock tables, metrics snapshots, workload bits, table IDs, and ISP tile power-gating masks.

## Important APIs, Types, and Functions
The interface exposes `SMU13_DRIVER_IF_VERSION` despite living under an SMU11 Van Gogh file name, which makes the exact macro name part of the local ABI. Core types include `FloatInIntFormat_t`, `DisplayClockTable_t`, `WatermarkRowGeneric_t`, `Watermarks_t`, `DpmActivityMonitorCoeffExt_t`, `CustomDpmSettings_t`, `df_pstate_t`, `vcn_clk_t`, `DpmClocks_t`, `SmuMetrics_legacy_t`, `SmuMetricsTable_t`, and `SmuMetrics_t`. Important macros define DCFCLK, DISPCLK, DPP/PHY, SOC, ISP, VCN, FCLK, and voltage level counts; throttler status bits; workload bits; table IDs from `TABLE_BIOS_IF` to `TABLE_SMU_METRICS`; and ISP tile selection/status masks.

## Control Flow
There is no internal control flow. `smu11/vangogh_ppt.c` allocates metrics and clocks tables using these structures, transfers `TABLE_DPMCLOCKS` and `TABLE_SMU_METRICS`, and branches on the metrics fields to report current clocks, activity, power, temperatures, throttling, C0 residency, and per-core telemetry. Watermark and custom DPM tables are consumed by display and driver policy paths through firmware table transfers.

## State and Persistence Behavior
The header has no mutable state. `DpmClocks_t` represents firmware-populated available clock and voltage levels and persists in the driver's SMU table cache. `Watermarks_t` and `CustomDpmSettings_t` are policy tables transferred to firmware. `SmuMetrics_t` contains sampled current and average telemetry with explicit sample start/stop times. The legacy metrics layout exists for compatibility with older firmware table formats.

## Dependencies and Integration Points
Integration points are `smu11/vangogh_ppt.c`, `smu_v11_5_pmfw.h`, common SMU table transfer code, display watermark programming, APU sensor reporting, workload selection, and ISP tile power-control messages. The metrics table also supports third-party tooling expectations through per-core, L3, and APU-specific fields.

## Risks
The version macro name is easy to misuse because it says `SMU13` in an SMU11 header. Metrics compatibility is another risk: decoding a legacy table as the newer current/average table will misread temperatures, core arrays, or throttling status. Table number drift can make firmware accept a transfer as the wrong table. ISP tile masks encode two-bit status fields and must not be confused with one-bit tile selection masks.

## Test Signals
Build `vangogh_ppt.c`, verify table allocation sizes, and boot on Van Gogh hardware with valid DPM clock table transfer. Runtime signals include correct `hwmon` clock/power/temperature readings, reasonable C0 residency and per-core telemetry, display watermark stability during pstate changes and memory retraining, workload switching, and ISP tile power status matching firmware responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu11_driver_if_vangogh.h -->
