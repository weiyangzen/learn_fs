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
