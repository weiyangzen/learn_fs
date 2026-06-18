<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu14_driver_if_v14_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu14_driver_if_v14_0.h

## Purpose
Defines the SMU 14.0 power-play table and driver/shared-memory ABI for AMDGPU SW SMU. It is the full v14.0 PMFW driver interface: feature bits, DPM level counts, throttler and dstate masks, voltage/fuse/AVFS descriptors, PP table layout, board layout, driver config, metrics, watermark, I2C, ECC, overdrive, activity-monitor, table IDs, and firmware-to-driver interrupt context IDs.

## Important APIs, Types, And Constants
The ABI version is `PPTABLE_VERSION 0x1B`; changing `SkuTable_t` or `BoardTable_t` requires bumping it. Clock topology is exposed through `PPCLK_e` plus DPM array sizes such as 16 GFXCLK levels, 8 SOC/FCLK/display levels, 6 UCLK levels, and 3 PCIe link levels. Feature control uses 64 `FEATURE_*_BIT` positions and masks such as `ALLOWED_FEATURE_CTRL_DEFAULT` and `ALLOWED_FEATURE_CTRL_SCPM`. Major exported tables are `PPTable_t`, `PFE_Settings_t`, `SkuTable_t`, `CustomSkuTable_t`, `BoardTable_t`, `OverDriveTable_t`, `OverDriveLimits_t`, `DriverSmuConfigExternal_t`, `DriverInfoTable_t`, `SmuMetricsExternal_t`, `WatermarksExternal_t`, `SwI2cRequestExternal_t`, `EccInfoTable_t`, `AvfsDebugTableExternal_t`, and `DpmActivityMonitorCoeffIntExternal_t`.

## Control Flow
There are no functions, but the constants define firmware command flow. The host writes table contents into driver DRAM, points PMFW at that memory through PPSMC address messages, and transfers by `TABLE_*` IDs. Firmware consumes PP/board/driver config tables to initialize DPM, voltage, fan, power, GFXOFF/DCS, BACO, I2C, and AVFS behavior, then publishes telemetry through the SMU metrics table and asynchronous IH interrupt context IDs.

## State And Persistence
Most fields are persistent firmware policy state loaded from VBIOS or driver-supplied tables: SKU limits, board GPIO/I2C wiring, SVI3 regulator settings, DPM frequency tables, AVFS fuse overrides, overdrive limits, fan settings, and workload masks. Runtime state is exported in metrics counters, temperatures, voltages/currents, fan PWM/RPM, throttling percentages, energy accumulators, D3hot counters, ECC info, and table-transfer status codes. Padding and `MmHubPadding` fields are part of the binary ABI and must stay stable.

## Dependencies And Integration
This header is included by ASIC-specific SMU code and paired with v14 PPSMC message headers. It depends on fixed-width integer types supplied by the include chain and on firmware, VBIOS, DAL/display, RLC, MMHUB, power-management, overdrive, and I2C tooling agreeing on byte layout and enum values. Table IDs integrate directly with `SMC_MSG_TransferTableDram2Smu` and `SMC_MSG_TransferTableSmu2Dram`.

## Risks And Test Signals
The main risk is silent ABI drift: array size, enum order, packing, or padding changes can corrupt firmware interpretation. Feature bit mismatches can enable/disable the wrong power domain, and bad voltage/fan/thermal limits can cause throttling or safety issues. Test signals include driver-if version checks, table transfer return codes, SMU metrics sanity, overdrive validation errors, fan/thermal interrupt contexts, BACO/AC/DC IH events, I2C command success, and GPU suspend/resume/D3hot coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu14_driver_if_v14_0.h -->
