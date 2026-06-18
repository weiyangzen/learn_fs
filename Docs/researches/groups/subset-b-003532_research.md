# Research: subset-b-003532

Grouped source research for subset B work item `subset-b-003532`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu11_driver_if_sienna_cichlid.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu11_driver_if_sienna_cichlid.h

## Purpose
This header is the SMU11 PMFW driver interface contract for Sienna Cichlid and related Beige Goby boards. It defines the binary table layouts, feature bits, table IDs, clock domain indexes, thermal/throttler indexes, I2C command ABI, overdrive table, metrics table variants, ECC table, watermarks, AVFS debug/fuse data, and activity monitor coefficients exchanged between the AMDGPU SMU driver and firmware.

## Important APIs, Types, and Functions
The public ABI starts with `SMU11_DRIVER_IF_VERSION` and `PPTABLE_Sienna_Cichlid_SMU_VERSION`, followed by DPM level counts for GFX, SOC, UCLK, FCLK, display clocks, PCIe link, XGMI, and fan curve points. The main exported structures are packed `PPTable_t`, `PPTable_beige_goby_t`, `DriverSmuConfig_t`, `OverDriveTable_t`, `SmuMetrics_t` through `SmuMetrics_V4_t`, `SmuMetricsExternal_t`, `WatermarksExternal_t`, `AvfsDebugTableExternal_t`, `AvfsFuseOverrideExternal_t`, `DpmActivityMonitorCoeffIntExternal_t`, `RlcPaceFlopsPerByteOverrideExternal_t`, `SwI2cRequestExternal_t`, and `EccInfoTable_t`.

The table ID macros map PMFW transfer slots: `TABLE_PPTABLE`, `TABLE_WATERMARKS`, `TABLE_AVFS_PSM_DEBUG`, `TABLE_AVFS_FUSE_OVERRIDE`, `TABLE_PMSTATUSLOG`, `TABLE_SMU_METRICS`, `TABLE_DRIVER_SMU_CONFIG`, `TABLE_ACTIVITY_MONITOR_COEFF`, `TABLE_OVERDRIVE`, `TABLE_I2C_COMMANDS`, `TABLE_PACE`, and `TABLE_ECCINFO`. Important enums include `PPCLK_e`, `TEMP_e`, `TDC_THROTTLER_e`, `PPT_THROTTLER_e`, `FEATURE_PWR_DOMAIN_e`, `FanMode_e`, `D3HOTSequence_e`, `DpmDescriptor_t`, I2C controller enums, VR mapping/PSI bitfields, and workload bits.

## Control Flow
The file has no executable control flow. It drives runtime flow through table allocation and transfer in `smu11/sienna_cichlid_ppt.c`: the driver initializes SMU table slots using these sizes, loads the power-play table from VBIOS, chooses the Beige Goby layout for matching ASIC variants, sends and receives tables with `smu_cmn_update_table()`, decodes `SmuMetrics*` for sensors and throttling, applies `OverDriveTable_t` changes, issues software I2C command tables, and fetches `EccInfoTable_t` for RAS error reporting. The union inside `SmuMetricsExternal_t` lets the consumer select a metrics layout based on firmware support and ASIC behavior.

## State and Persistence Behavior
The header stores no state itself, but most structures describe persistent firmware-owned state. `PPTable_t` and `PPTable_beige_goby_t` encode SKU and board policy that PMFW uses across DPM, thermal, fan, ULV, BACO, XGMI, AVFS, VR, and memory behavior. Overdrive tables persist in the driver's boot/user/current copies and are transferred to firmware when user tuning changes. Metrics and ECC tables are firmware snapshots. I2C requests are transient command packets. Padding and `MmHubPadding` fields are part of the ABI and must remain stable.

## Dependencies and Integration Points
This header is included by `smu11/sienna_cichlid_ppt.c` and paired with SMU11 PPSMC message definitions and generic SMU table infrastructure in `amdgpu_smu.h` and `smu_cmn`. It integrates with VBIOS PPTable parsing, hwmon/sysfs sensor exposure, OverDrive interfaces, RAS UMC handling, BACO/D3HOT accounting, DC watermarks, RLC pace/GPO logic, software I2C support, PCIe link reporting, and XGMI training. Consumers depend on exact struct packing, table numbers, enum order, units, and array dimensions.

## Risks
The central risk is ABI drift: changing any field, order, size, table ID, or enum value without updating firmware and version checks can corrupt PMFW table interpretation. Power, voltage, thermal, fan, and CTF fields are safety relevant; invalid values can cause unstable clocks, overheating, excessive current, or spurious throttling. Metrics variants are easy to decode with the wrong layout. The two PPTable layouts share many fields but differ in reserved space and a few names, so copy assumptions between Sienna Cichlid and Beige Goby can break offsets. Software I2C command length and stop/restart flags must be bounded to avoid malformed PMFW bus transactions.

## Test Signals
Useful signals include successful AMDGPU build for Sienna Cichlid, SMU table initialization sizes matching firmware expectations, boot without PMFW table transfer failures, valid `hwmon` clocks/temperatures/power/fan readings, OverDrive changes surviving the driver table path, stable DC watermark programming, working software I2C reads, correct ECC record collection on RAS-capable boards, and no regressions in BACO/D3HOT counters, PCIe link state, XGMI levels, or thermal throttling status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu11_driver_if_sienna_cichlid.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_aldebaran.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_aldebaran.h

## Purpose
This header defines the SMU13 PMFW interface for the Aldebaran compute GPU family. It focuses on high-performance discrete GPU policy: DPM for GFX/VCN/SOC/UCLK/FCLK/LCLK/XGMI, HBM and VR thermal limits, APCC, XGMI training, I2C VR telemetry, ECC/RAS tables, AVFS debug data, and SMU metrics.

## Important APIs, Types, and Functions
The ABI version macro is `SMU13_DRIVER_IF_VERSION_ALDE`. Major structures include packed `PPTable_t`, `DriverSmuConfig_t`, `SmuMetrics_t`, `AvfsDebugTable_t`, `SwI2cRequestExternal_t`, `EccInfo_t`, `EccInfo_V2_t`, and `EccInfoTable_t`. The power table defines `FeaturesToRun`, PPT/TDC/HBM limits, voltage maxima, `DpmDescriptor_t`, DID/FID clock tables, startup PLL and SVI values, guardband/AVFS parameters, XGMI DPM levels, GFX/SOC Vmin settings, telemetry calibration, spread spectrum, I2C controller config, XGMI current, and EDC power limit.

The table IDs are `TABLE_PPTABLE`, `TABLE_AVFS_PSM_DEBUG`, `TABLE_AVFS_FUSE_OVERRIDE`, `TABLE_PMSTATUSLOG`, `TABLE_SMU_METRICS`, `TABLE_DRIVER_SMU_CONFIG`, `TABLE_I2C_COMMANDS`, and `TABLE_ECCINFO`. Throttler bits distinguish PPT, GFX/SOC/HBM TDC, GPU/memory/VR temperatures, and APCC.

## Control Flow
The header has no executable flow. `smu13/aldebaran_ppt.c` initializes table slots with these sizes, transfers I2C command packets, reads metrics to expose clocks, activity, temperatures, power, energy and serial number, and requests ECC information for RAS handling. The union inside `EccInfoTable_t` lets the same table slot represent the original ECC layout or the V2 layout with a correctable-error address.

## State and Persistence Behavior
The PPTable is persistent board/SKU policy consumed by PMFW after boot and resume. Driver SMU config controls telemetry averaging. SMU metrics are sampled firmware state, with energy and timestamp counters useful for deltas. ECC entries are latched hardware/RAS state copied through PMFW, including MCA status/address and CE counts across `ALDEBARAN_UMC_CHANNEL_NUM` channels. I2C command tables are transient requests.

## Dependencies and Integration Points
This header integrates with `aldebaran_ppt.c`, SMU13 table transfer helpers, XGMI topology/training, AMDGPU RAS UMC code, VR/I2C telemetry, hwmon sensors, APCC and DPM control, and firmware PMSTATUS/AVFS debug facilities. It relies on exact packing for the large `PPTable_t` and on firmware agreeing which ECC table layout is active.

## Risks
Using the wrong ECC layout can drop `mca_ceumc_addr` or misalign all following channel records. Incorrect HBM, TDC, EDC, or VR thermal limits can affect compute GPU safety and reliability. XGMI link speed/width values are firmware contracts and a bad table can break multi-GPU fabrics. The duplicated I2C enable defines and compact controller protocol set make it easy to assume support for protocols that Aldebaran firmware does not implement.

## Test Signals
Build `aldebaran_ppt.c`, boot Aldebaran hardware with successful PPTable/metrics/ECC table transfer, validate XGMI DPM and link training, compare HBM and VR thermal readings to hardware monitors, exercise I2C VR telemetry, inspect energy/timestamp deltas, inject or observe RAS CE/UE paths, and verify APCC/PPT/TDC throttling status matches firmware events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_aldebaran.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_v13_0_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_v13_0_0.h

## Purpose
This header is the full SMU13.0.0 discrete GPU driver/firmware ABI. It defines feature masks, PPTable versioning, split SKU and board tables, OverDrive and limits tables, driver info, metrics, watermarks, AVFS debug data, activity monitor coefficients, ECC, I2C request tables, workload bits, transfer statuses, table IDs, and SMU interrupt context IDs.

## Important APIs, Types, and Functions
Version contracts are `SMU13_0_0_DRIVER_IF_VERSION` and `PPTABLE_VERSION`. The major data contracts are `SkuTable_t`, `BoardTable_t`, packed `PPTable_t`, `OverDriveTable_t`, `OverDriveLimits_t`, `BootValues_t`, `MsgLimits_t`, `DriverReportedClocks_t`, `DriverSmuConfigExternal_t`, `DriverInfoTable_t`, `SmuMetricsExternal_t`, `WatermarksExternal_t`, `AvfsDebugTableExternal_t`, `DpmActivityMonitorCoeffIntExternal_t`, `SwI2cRequestExternal_t`, and `EccInfoTable_t`.

The header provides 64 feature bits, allowed feature masks for default and SCPM operation, debug overrides, VR/SVI/PSI mapping, thermal/throttler indexes, D3HOT sequence indexes, AVFS fuse enums, memory vendor indexes, OverDrive feature bits, DPM clock enums, power-source enums, table transfer status values, table IDs including `TABLE_COMBO_PPTABLE`, `TABLE_DRIVER_INFO`, `TABLE_ECCINFO`, and `TABLE_WIFIBAND`, plus IH interrupt context IDs for BACO, AC/DC, audio, thermal throttling, and fan abnormal/recovery events.

## Control Flow
There is no internal control flow. `smu13/smu_v13_0_0_ppt.c` uses these types to initialize SMU table sizes, parse PPTable data from VBIOS, transfer combo/power tables to firmware, decode `SmuMetricsExternal_t`, implement throttle-status mapping from `ThrottlingPercentage`, support OverDrive limit validation and updates, send I2C commands, populate driver info, and fetch ECC information for RAS. Generic SMU13 code consumes the interrupt context IDs for PMFW-to-driver notifications.

## State and Persistence Behavior
`SkuTable_t` and `BoardTable_t` are persistent firmware policy: features, power/current/temperature limits, DPM frequencies, voltage/AVFS tables, GFXOFF/DCS/GPO behavior, fan controls, memory and VR settings, spread spectrum, BACO delays, and board GPIOs. OverDrive tables persist in driver-managed boot/current/user copies and are transferred when tuning changes. Metrics are periodically updated firmware snapshots. Driver info and watermarks are cached policy tables. ECC info mirrors RAS state across 24 UMC channels.

## Dependencies and Integration Points
The header is included by `smu_v13_0_0_ppt.c` and depends on SMU13 PPSMC message headers, VBIOS PPTable layout, common SMU table transfer, AMDGPU OverDrive sysfs, hwmon, DC watermarks, RAS UMC paths, I2C VR/thermal devices, workload policy, and PMFW interrupt handling in `smu_v13_0.c`. Field units and enum order are part of the firmware ABI.

## Risks
This is a broad safety-critical ABI. Bad table IDs or struct size drift can make PMFW read a different payload than the driver wrote. Power, TDC, CTF, fan, VR, AVFS, and voltage fields can affect hardware safety. `SkuTable_t` and `BoardTable_t` are packed together, so padding changes alter many offsets. The OverDrive limits/table pair must stay synchronized or user tuning can bypass intended bounds. Memory vendor ordering affects spread-spectrum and temperature-limit policy. Metrics spare counts and external padding protect MMHUB access and should not be repurposed casually.

## Test Signals
Build `smu_v13_0_0_ppt.c`, verify PMFW interface version compatibility, boot with successful PPTable/metrics/driver-info/overdrive table initialization, compare reported clocks, PCIe, fan, temperature, power, and throttling values against hardware, exercise OverDrive validation paths, validate DC watermark programming, run BACO and AC/DC transitions, test software I2C, and confirm ECC/RAS records on supported boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_v13_0_0.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_v13_0_6.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_v13_0_6.h

## Purpose
This header defines the SMU13.0.6 PMFW-side ABI fragments used for software I2C, error-code classification, AVFS debug tables, thermal interrupt notifications, throttler masks, clock IDs, UCLK DPM mode selection, and ClearMcaOnRead control. It is narrower than the full discrete GPU PPTable headers and leaves active table IDs to the consuming PPT implementation.

## Important APIs, Types, and Functions
The version is `SMU13_0_6_DRIVER_IF_VERSION`. Important types include I2C enums and `SwI2cRequestExternal_t`, `ERR_CODE_e`, `GC_ERROR_CODE_e`, `PPCLK_e`, `UCLK_DPM_MODE_e`, `AvfsDebugTableAid_t`, and `AvfsDebugTableXcd_t`. Error enums map MMHUB, VCN, JPEG, SDMA, SOC, GC, and shared MP5 error categories. I2C speed enums explicitly mark older 50 KHz, high-speed 1 MHz, and 2.3 MHz modes as unsupported. Interrupt and throttler constants include `IH_INTERRUPT_ID_TO_DRIVER`, `IH_INTERRUPT_CONTEXT_ID_THERMAL_THROTTLING`, `THROTTLER_PROCHOT_BIT`, PPT, socket/VR/HBM thermal bits, and `ClearMcaOnRead_UE_FLAG_MASK` / `ClearMcaOnRead_CE_POLL_MASK`.

## Control Flow
The header has no internal control flow. `smu13/smu_v13_0_6_ppt.c` includes it, defines local table mappings, initializes `SMU_TABLE_I2C_COMMANDS`, sends ClearMcaOnRead messages using the masks, handles thermal-throttling interrupt context IDs, and uses the software I2C request structures for firmware-mediated bus access. Error-code enums provide typed values for firmware RAS/error events rather than in-header behavior.

## State and Persistence Behavior
I2C request structures are transient command buffers. ClearMcaOnRead masks affect firmware behavior for clearing uncorrectable flags and correctable-error polling on read, so the resulting behavior persists in firmware policy until changed or reset. AVFS debug tables are snapshots per AID or XCD. Error code enums describe latched hardware/firmware events consumed by RAS or interrupt paths.

## Dependencies and Integration Points
Integration points are `smu_v13_0_6_ppt.c`, `smu_v13_0_6_ppsmc.h`, generic SMU message/table infrastructure, RAS/MCA clearing, thermal interrupt handling, software I2C support, and debug/AVFS table readers. The active table IDs are not taken from this header because its `TABLE_*` section is commented out in the source.

## Risks
The commented table definitions are a trap for maintainers; consumers must use the active local mapping in `smu_v13_0_6_ppt.c`. Unsupported I2C enum entries preserve numeric positions and should not be used as valid speeds. ClearMcaOnRead behavior is version-sensitive in the consumer and can affect RAS visibility if enabled or disabled on unsupported firmware. Error code values have intentional gaps and shared SOC codes, so compacting or renumbering them would break firmware event decoding.

## Test Signals
Build `smu_v13_0_6_ppt.c`, validate software I2C transfers, confirm thermal interrupt handling reaches the driver on over-temperature events, exercise ClearMcaOnRead only on firmware versions that advertise support, verify RAS logs preserve expected error-code names and MCA clearing behavior, and inspect AVFS debug snapshots for correct AID/XCD dimensions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_v13_0_6.h -->

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
