# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/vega12/smu9_driver_if.h

## Purpose

`vega12/smu9_driver_if.h` is the Vega12-specific SMU9 driver interface. It supersedes the base SMU9 layout with interface version `0x10`, larger graphics DPM capacity, explicit feature masks, new DPM descriptor/equation formats, metrics and overdrive tables, driver configuration, and activity monitor coefficients.

## Important APIs, types, and constants

The file defines DPM array sizes for GFX, VCLK, DCLK, ECLK, MP0, UCLK, SOCCLK, DCEFCLK, DISPCLK, PIXCLK, PHYCLK, and PCIe link. Graphics DPM has 16 levels, while several display/video domains have eight levels.

`FEATURE_*_BIT` and `FEATURE_*_MASK` enumerate 32 firmware features including DPM domains, ULV, deep sleep, PPT/TDC/thermal, regulator hot, fan control, GFX EDC, GFXOFF, CG, and ACG. `DPM_OVERRIDE_*` masks describe policy links between voltage/frequency domains and GFXOFF clock switching. VR mapping, PSI selection, throttler status, workload bits, and table-transfer status constants define additional firmware ABI fields.

`PPCLK_e` names clock domains. `QuadraticInt_t`, `LinearInt_t`, and `DroopInt_t` encode firmware equations. `DpmDescriptor_t` describes voltage mode, discrete-level snapping, conversion to AVFS clock, and static-spread/AVFS curves per clock domain.

`PPTable_t` is the central packed Vega12 power table. It includes AC/DC socket power limits, TDC limits, thermal limits, FIT/PPM limits, ULV offsets, min/max voltages, DPM descriptors, frequency tables for all clock domains, DC-mode maximums, MP0 levels, graphics CKS/ACG settings, UCLK/PCIe link settings, TDPM settings, fan controls, AVFS/BTC/ageing equations, I2C sensor addresses, voltage step limits, VR mappings, telemetry calibration, GPIO/LED pins, spread-spectrum settings, VR2 address, board reserved words, and firmware padding.

Additional tables include `DriverSmuConfig_t` for LPF taus, `OverDriveTable_t` for overdrive clocks/fan/temperature limits, `SmuMetrics_t` for current clocks, averages, activity, voltage offsets, power, temperatures, throttler status, and link level, `Watermarks_t`, `AvfsDebugTable_t`, `AvfsFuseOverride_t`, and `DpmActivityMonitorCoeffInt_t`.

`TABLE_*` IDs cover PP table, watermarks, AVFS, AVFS debug, AVFS fuse override, PM status log, SMU metrics, driver config, activity monitor coefficients, and overdrive.

## Control flow

The header provides no code. Runtime flow is table-oriented: the driver builds a specific table, writes the driver DRAM address to firmware, and transfers the selected table ID. Query paths transfer SMU-owned metrics or debug tables back to DRAM. Feature enable/disable messages use the feature masks and Vega12 message IDs from `vega12_ppsmc.h`.

## State and persistence behavior

Most structures describe SMU-resident policy or telemetry. `PPTable_t`, `DriverSmuConfig_t`, `Watermarks_t`, `OverDriveTable_t`, and activity coefficients are driver-authored policy tables. `SmuMetrics_t` and AVFS debug tables are firmware-authored runtime telemetry. Data persists in firmware memory until reuploaded, overwritten by firmware, or reset.

The packed layout and reserved fields are persistent ABI. `FeaturesToRun[2]` and table IDs also persist as the firmware interpretation boundary between host policy and SMU behavior.

## Dependencies and integration points

The file integrates with Vega12 SMU manager code, `vega12_ppsmc.h` messages, PowerPlay profile/overdrive/thermal paths, display watermark programming, AVFS tooling, and metrics queries. It depends on fixed-width integer definitions from the including environment and the firmware's exact interpretation of packed structures.

## Risks

Compared with the base SMU9 interface, this file has more clock domains and more cross-domain policy. Array-size, table-ID, or feature-mask mistakes can produce wrong clock bounds, broken video/display DPM, incorrect GFXOFF behavior, or missing thermal throttling. `FeaturesToRun[2]` suggests 64-bit feature plumbing, but only 32 feature bits are defined here, so high-word behavior must match firmware expectations.

Equation and voltage fields use compact integer formats without local validation. Mis-scaled AVFS/BTC/ageing coefficients or telemetry offsets can cause unstable voltage selection. Because metrics and policy tables share transfer infrastructure, callers must not confuse read-only telemetry IDs with driver-authored upload IDs.

## Test signals

Validation should cover Vega12 interface-version negotiation, PP table upload, feature enable/disable masks, metrics table transfer, watermarks, overdrive table upload, activity monitor coefficient transfer, fan and thermal behavior, GFXOFF/ACG behavior, and all display/video clock domains. Offset/size checks against firmware headers are especially important.
