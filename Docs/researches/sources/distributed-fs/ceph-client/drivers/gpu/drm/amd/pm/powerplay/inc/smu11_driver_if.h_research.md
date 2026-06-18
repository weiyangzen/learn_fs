# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu11_driver_if.h

## Purpose

`smu11_driver_if.h` is the large SMU11 driver/firmware ABI header for PPTable v2.0-era discrete GPUs. It defines clock-level counts, feature and throttler bits, workload bits, I2C/VR telemetry descriptors, DPM descriptors, the packed `PPTable_t`, metrics and watermark tables, AVFS debug/override tables, overdrive settings, activity monitor coefficients, table IDs, and ECC/debug bit fields.

## Important APIs, Types, And Functions

Important constants include DPM level counts for GFXCLK, VCLK, DCLK, ECLK, MP0CLK, SOCCLK, UCLK, FCLK, DCEFCLK, DISPCLK, PIXCLK, PHYCLK, PCIe link, and XGMI. Feature bits cover DPM, ULV, PPT/TDC/thermal, deep sleep, AC/DC, VR hot, firmware CTF, LED, fan, GFX EDC, GFXOFF, clock gating, XGMI, and ECC. Core types include I2C controller enums/configuration, polynomial helper types, `PPCLK_e`, `POWER_SOURCE_e`, `VOLTAGE_MODE_e`, `AVFS_VOLTAGE_TYPE_e`, `DpmDescriptor_t`, `PPTable_t`, `DriverSmuConfig_t`, `OverDriveTable_t`, `SmuMetrics_t`, `Watermarks_t`, `AvfsDebugTable_t`, `AvfsFuseOverride_t`, and `DpmActivityMonitorCoeffInt_t`.

`PPTable_t` is the main board and policy table: limits, thermal thresholds, voltage ranges, load lines, clock frequency tables, DC max clocks, PCIe/XGMI settings, TDPM, fan policy, AVFS curves, BTC/aging data, debug overrides, VR mappings, telemetry calibration, GPIOs, LED pins, spread spectrum, I2C controllers, and reserved/padding areas.

## Control Flow And Data Flow

There is no executable code. The driver parses or constructs PPTable data, uploads it through SMU table-transfer messages, reads `SmuMetrics_t` for telemetry, updates watermarks from display requirements, applies overdrive edits, and optionally transfers AVFS/debug/activity-monitor tables. Firmware consumes the fields to make DPM, voltage, fan, thermal, XGMI, and throttling decisions.

## State And Persistence Behavior

The structures define persistent firmware table state. `PPTable_t` configures long-lived board policy until replaced or firmware reset. `SmuMetrics_t` is a firmware-updated snapshot table. `OverDriveTable_t`, watermarks, AVFS overrides, and activity coefficients persist in SMU memory once transferred. Padding and reserved fields are ABI-significant.

## Dependencies And Integration Points

The header depends on fixed-width types and packed layout. It integrates with SMU v11 hwmgr/smu code, PPTable parsing, fan control, thermal and throttling handling, overdrive sysfs, XGMI, ECC reporting, display watermarks, I2C telemetry sensors, AVFS/BTC calibration, metrics reporting, and table-transfer code.

## Risks And Edge Cases

The version note says structure changes require an interface-version update elsewhere, so silent ABI edits are dangerous. Some masks correctly use `1ULL` for bits above 31, while many lower masks use `1`; callers should use 64-bit feature containers. Packed layout, floats in `AvfsDebugTable_t`, and reserved padding make compatibility sensitive. Units vary widely across clocks, voltage, current, temperature, RPM, PWM, GPIO polarity, and fixed-point coefficients.

## Test Signals

Validation needs compile-time size/offset checks, SMU11 firmware version compatibility, PPTable upload and readback, metrics sanity under load, fan and thermal throttling tests, overdrive edits, watermark updates during display changes, XGMI state transitions, ECC mask handling, I2C telemetry reads, and AVFS override/debug table transfers.
