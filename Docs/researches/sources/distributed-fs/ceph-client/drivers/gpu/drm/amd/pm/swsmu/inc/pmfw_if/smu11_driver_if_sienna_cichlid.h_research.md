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
