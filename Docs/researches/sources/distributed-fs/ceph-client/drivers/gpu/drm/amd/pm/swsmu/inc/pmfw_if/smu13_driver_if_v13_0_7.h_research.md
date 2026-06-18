<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_v13_0_7.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_v13_0_7.h

## Purpose
This header is the SMU13.0.7 discrete GPU firmware interface. It is closely related to v13.0.0 but has its own interface and PPTable versions, memory vendor ordering, advanced OverDrive limits, metrics padding, AVFS debug table size, and feature set. It defines the binary ABI for PPTable, board table, OverDrive, metrics, driver info, watermarks, I2C, ECC, activity monitor coefficients, workload bits, transfer statuses, table IDs, and PMFW interrupt contexts.

## Important APIs, Types, and Functions
The version macros are `SMU13_0_7_DRIVER_IF_VERSION` and `PPTABLE_VERSION`. Major structures are `SkuTable_t`, `BoardTable_t`, packed `PPTable_t`, `OverDriveTable_t`, `OverDriveLimits_t`, `BootValues_t`, `MsgLimits_t`, `DriverReportedClocks_t`, `DriverSmuConfigExternal_t`, `DriverInfoTable_t`, `SmuMetricsExternal_t`, `WatermarksExternal_t`, `AvfsDebugTableExternal_t`, `DpmActivityMonitorCoeffIntExternal_t`, `SwI2cRequestExternal_t`, and `EccInfoTable_t`. The ABI also defines feature bits, allowed feature masks, debug overrides, VR/SVI/PSI data, thermal and throttler indexes, D3HOT sequence counters, AVFS fuse enumerations, OverDrive feature bits and `PP_OD_POWER_FEATURE_e`, memory vendors, and table IDs through `TABLE_WIFIBAND`.

## Control Flow
There is no runtime flow in the header. `smu13/smu_v13_0_7_ppt.c` sizes and transfers the tables, decodes `SmuMetricsExternal_t`, calculates throttler status from `ThrottlingPercentage`, manages OverDrive limits including advanced maxima, updates I2C command tables, populates driver info, and handles ECC table access. Generic SMU13 interrupt handling consumes the IH context IDs for BACO, AC/DC, audio, thermal throttling, and fan abnormal/recovery events.

## State and Persistence Behavior
`SkuTable_t` and `BoardTable_t` define persistent PMFW policy for feature enablement, power/current/temperature limits, DPM frequencies, voltage/AVFS behavior, GFXOFF/DCS/GPO, fan policy, memory and VR configuration, spread spectrum, BACO delays, and board GPIOs. OverDrive tables hold user-tunable state with min/basic/advanced limits. Metrics are mutable firmware telemetry snapshots. ECC and I2C tables are firmware exchange buffers, while watermarks and driver-info tables are cached policy/capability data.

## Dependencies and Integration Points
This header is included by `smu_v13_0_7_ppt.c` and depends on SMU13 PPSMC definitions, common SMU table transfer, VBIOS PPTable parsing, OverDrive sysfs, hwmon, DC watermarks, RAS UMC, software I2C, PMFW interrupts in `smu_v13_0.c`, workload policy, and firmware version matching. It is source-compatible in shape with v13.0.0 in many areas, but not ABI-identical.

## Risks
Copying assumptions from v13.0.0 is risky: PPTable version, spare sizes, advanced OverDrive limits, AVFS debug array size, memory vendor order, and some fuse fields differ. A mismatched `SmuMetricsExternal_t` spare count changes table size. Safety-sensitive risks mirror v13.0.0: bad voltage, fan, CTF, TDC, PPT, AVFS, or VR data can destabilize hardware. OverDrive advanced limits require careful validation so user tuning cannot exceed firmware-supported ranges.

## Test Signals
Build `smu_v13_0_7_ppt.c`, validate table sizes and PMFW interface version, boot with successful PPTable/metrics/overdrive/driver-info transfers, compare hwmon clocks/power/temperatures/fan/PCIe readings, exercise basic and advanced OverDrive bounds, verify fan abnormal and recovery interrupts, test BACO and AC/DC events, validate DC watermarks, and confirm ECC and I2C paths on supported boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_v13_0_7.h -->
