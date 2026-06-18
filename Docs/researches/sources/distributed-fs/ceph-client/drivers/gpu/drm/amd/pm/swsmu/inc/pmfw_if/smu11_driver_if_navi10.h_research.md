<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu11_driver_if_navi10.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu11_driver_if_navi10.h

## Purpose
This header defines the Navi10/Navi1x SMU11 driver interface ABI. It provides PPTable layout, feature and throttler bits, DPM clock counts, I2C command layouts, power/thermal/voltage enums, OOB monitor data, metrics variants for NV10/NV12, watermarks, overdrive, AVFS/debug/activity monitor tables, table transfer IDs, and UCLK switch constants used by Navi10-family SMU backends.

## Important APIs, Types, and Functions
- Version and sizing: `PPTABLE_NV10_SMU_VERSION`, `NUM_*_DPM_LEVELS`, link levels, max-level macros, Gemini mode constants, `NUM_FEATURES`.
- Feature bits include DPM clocks/link/DCEF, memory voltage scaling, deep sleep, ULV, FW D-state, GFXOFF, BACO, VCN/JPEG/USB power gating, RSMU CG, PPT/TDC/EDC/APCC/GTHR/ACDC/VRHOT/FW CTF/fan/thermal, RM, LED, spread spectrum, OOB, Vmin, MMHUB/ATHUB power gating, and APCC DFLL.
- Tables and structures: packed `PPTable_t`, `DriverSmuConfig_t`, `OverDriveTable_t`, `SmuMetrics_legacy_t`, `SmuMetrics_t`, `SmuMetrics_NV12_legacy_t`, `SmuMetrics_NV12_t`, `SmuMetrics_NV1X_t`, `Watermarks_t`, AVFS debug/fuse override tables, `DpmActivityMonitorCoeffInt_t`, `RlcPaceFlopsPerByteOverride_t`, and `OutOfBandMonitor_t`.
- Table IDs: PPTable, watermarks, AVFS, PSM debug, fuse override, PM status log, SMU metrics, driver config, activity monitor coeff, overdrive, I2C commands, and pace.

## Control Flow
The header is declarative, but it drives Navi10 backend control flow. During initialization the backend builds or patches `PPTable_t`, transfers it to PMFW, and later transfers watermarks, overdrive, AVFS, I2C, activity monitor, and pace tables as requested by generic SMU operations. Runtime metrics reads select the correct member of `SmuMetrics_NV1X_t` depending on ASIC or firmware generation. Display paths consume `Watermarks_t`; OD sysfs paths consume `OverDriveTable_t`; fan/power/thermal paths read limits and control fields from PPTable and metrics.

## State and Persistence Behavior
`PPTable_t` is persistent PMFW configuration for feature enablement, AC/DC power limits, TDC, thermal limits, FW D-state mask, ULV, voltage control, DPM frequency tables, UCLK divisors, PCIe link DPM, fan curves, AVFS curves, board telemetry, GPIOs, spread spectrum, board power, and MMHUB padding. Metrics structures are transient snapshots. Watermarks persist until reloaded for display clock ranges. Overdrive table values represent user-adjustable state. Table IDs persist as ABI values used as arguments to PMFW table transfer messages.

## Dependencies and Integration Points
- Used by Navi10 PPT implementation selected for MP1 11.0.0, 11.0.5, and 11.0.9.
- Integrates with generic SMU feature maps, clock maps, workload maps, table transfer, display watermarks, OD editing, fan control, metrics, sensors, BACO/GFXOFF, and DPM operations.
- Firmware, VBIOS PPTable data, and Linux structure definitions must agree on layout, units, array counts, and table IDs.

## Risks
- This is a dense firmware ABI. Changing `PPTable_t`, metrics variants, watermarks, or table IDs without a matching PMFW interface update can break boot-time DPM setup or runtime PM features.
- Navi10 feature bit positions differ from Arcturus and later ASICs; maps must remain per-ASIC.
- Multiple metrics variants make size and generation selection important. Reading an NV12 metrics buffer as legacy NV10 will misdecode energy, PCIe, and pre/post deep-sleep fields.
- Units and fixed point formats vary: MHz, Celsius, mV Q2, Q4.4, Q16, Q8.24, Q12.12, and 10 KHz units coexist.
- OOB monitor and I2C structures expose board-management data; command counts, addresses, and padding must be validated before transfer.

## Test Signals
- Compile Navi10 backend and compare structure sizes/offsets against the PMFW header used to build firmware.
- Boot Navi10/Navi12 hardware and verify PPTable transfer, watermarks upload, OD table reads/edits, GFXOFF/BACO behavior, fan controls, and metrics reporting.
- Exercise display mode changes to validate watermark rows for SOCCLK/DCEFCLK and UCLK ranges.
- Validate metrics variant selection by checking PCIe rate/width, energy accumulator, VCN activity, and pre/post deep-sleep averages on supported ASICs.
- Negative tests should catch accidental feature bit renumbering, table ID changes, and malformed I2C command counts above `MAX_SW_I2C_COMMANDS`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu11_driver_if_navi10.h -->
