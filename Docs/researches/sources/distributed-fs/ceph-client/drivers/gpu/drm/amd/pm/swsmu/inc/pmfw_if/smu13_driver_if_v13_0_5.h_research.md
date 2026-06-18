<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_v13_0_5.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_v13_0_5.h

## Purpose
This is a minimal SMU13.0.5 APU firmware interface header. It defines just enough ABI for watermarks, DPM clock discovery, compact metrics reporting, throttler status, and table IDs used by `smu_v13_0_5_ppt.c`.

## Important APIs, Types, and Functions
The version macro is `SMU13_0_5_DRIVER_IF_VERSION`. Exported types are `WatermarkRowGeneric_t`, `Watermarks_t`, `DfPstateTable_t`, `SmuMetrics_t`, and `DpmClocks_t`. DPM level counts are four per clock/voltage family, making the table smaller than v13.0.4 and Yellow Carp. `SmuMetrics_t` reports current GFX/SOC/VCN/DCLK/memory clocks, GFX/UVD activity, two voltage/current/power rails, GFX/SOC temperature, throttler status, and socket power. Table IDs run from BIOS and watermarks through custom DPM, DPM clocks, modern standby, and metrics.

## Control Flow
There is no executable flow. `smu13/smu_v13_0_5_ppt.c` allocates `DpmClocks_t` and `SmuMetrics_t`, fetches DPM clocks from firmware, and uses the compact metrics payload for sensor and activity reporting. The common SMU13 table transfer path uses the `TABLE_*` values to select the firmware slot.

## State and Persistence Behavior
DPM clocks are cached capability state from firmware. Watermarks are policy state transferred for display and memory pstate coordination. Metrics are transient snapshots. The header intentionally lacks PPTable, OverDrive, I2C, ECC, AVFS, and PMF limit contracts found in larger discrete or APU variants.

## Dependencies and Integration Points
The header is included by `smu_v13_0_5_ppt.c` and `smu_v13_0_5_pmfw.h`. It integrates with generic SMU table management, APU hwmon reporting, display watermark handling, DPM clock enumeration, workload-independent throttler status, and modern standby log table selection.

## Risks
Because this header is deliberately small, code shared with richer SMU13 variants must not assume OverDrive, I2C, ECC, PMF, or extended metrics fields exist. The reduced DPM level counts can truncate copied logic from v13.0.4/Yellow Carp if not guarded. Power units are milliwatts in the metrics comments, unlike some other headers that use watts for similarly named fields.

## Test Signals
Build `smu_v13_0_5_ppt.c`, verify `SMU_TABLE_DPMCLOCKS` and `SMU_TABLE_SMU_METRICS` sizes, read DPM clock levels from firmware, compare basic clock/activity/power/temperature reporting to hardware, and exercise display watermark transfer and modern standby table selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_v13_0_5.h -->
