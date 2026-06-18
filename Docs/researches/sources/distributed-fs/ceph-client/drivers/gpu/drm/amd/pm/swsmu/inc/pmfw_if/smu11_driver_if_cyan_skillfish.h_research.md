<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu11_driver_if_cyan_skillfish.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu11_driver_if_cyan_skillfish.h

## Purpose
This compact header defines the Cyan Skillfish MP1/SMU11 driver interface version, firmware table IDs, and SMU metrics layout. It is the ABI used by the Cyan Skillfish backend to identify firmware tables and decode current/average telemetry for CPU, GFX, SOC IP clocks, power rails, socket power, temperatures, and throttling status.

## Important APIs, Types, and Functions
- Interface version: `MP1_DRIVER_IF_VERSION 0x8`.
- Table IDs: `TABLE_BIOS_IF`, `TABLE_WATERMARKS`, `TABLE_PMSTATUSLOG`, `TABLE_DPMCLOCKS`, `TABLE_MOMENTARY_PM`, `TABLE_SMU_METRICS`, and `TABLE_COUNT`.
- `SmuMetricsTable_t`: per-sample telemetry containing six CPU cores, two L3 entries, GFX/SOC/VCLK/DCLK/Memclk, voltage/current/power rails, socket power, SOC/edge temperatures, throttler status, and spare padding.
- `SmuMetrics_t`: wraps current and average metrics tables plus sample start/stop timestamps and `Accnt`.

## Control Flow
There is no code flow in this header. The Cyan Skillfish SMU backend requests `TABLE_SMU_METRICS` from PMFW, interprets the returned buffer as `SmuMetrics_t`, and maps fields into generic AMDGPU metrics/sysfs outputs. The table ID constants are also used when generic table-transfer helpers pass PMFW table identifiers.

## State and Persistence Behavior
The header stores no driver state. `SmuMetrics_t` describes firmware-produced telemetry snapshots; `Current` and `Average` are two views of the same field set. Table IDs are persistent ABI constants and include several backward-compatible entries declared but not actively used by the driver.

## Dependencies and Integration Points
- Used by Cyan Skillfish PPT/SMU code selected from `smu_set_funcs` for MP1 11.0.8.
- Integrates with generic `get_gpu_metrics`, `get_pm_metrics`, sensor reads, and table-transfer logic.
- Depends on PMFW and BIOS using the same table numbering and metrics layout.

## Risks
- Metrics arrays are fixed at six CPU cores and two L3 entries; code using this table must not assume a larger topology.
- Temperatures use centi-Celsius in several fields while other SMU headers often use Celsius or millidegrees Celsius in driver-facing APIs.
- Backward-compatible but unused table IDs should not be removed or renumbered because firmware may still expose them.
- No explicit packing pragma is used; ABI validation should confirm compiler layout matches PMFW expectations.

## Test Signals
- Compile Cyan Skillfish backend and verify the selected table IDs match backend mappings.
- Read SMU metrics and confirm current/average CPU, GFX, SOC, clock, rail, socket power, and temperature values are sane.
- Check unit conversion for centi-Celsius and mW/mV/mA fields when exposed through generic metrics.
- Regression tests should compare `sizeof(SmuMetricsTable_t)` and `sizeof(SmuMetrics_t)` against PMFW expectations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu11_driver_if_cyan_skillfish.h -->
