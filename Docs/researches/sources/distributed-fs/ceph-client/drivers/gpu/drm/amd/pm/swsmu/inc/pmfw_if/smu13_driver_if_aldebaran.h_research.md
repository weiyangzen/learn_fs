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
