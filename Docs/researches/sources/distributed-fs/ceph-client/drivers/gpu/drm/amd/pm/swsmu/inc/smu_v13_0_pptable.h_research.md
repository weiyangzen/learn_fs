<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v13_0_pptable.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v13_0_pptable.h

## Purpose

`smu_v13_0_pptable.h` is the base packed PowerPlay table layout for SMU13 platforms that use the older, SMU11-like OD/power-saving schema. It defines VBIOS metadata, platform caps, thermal-controller type, power limits, power-saving clock ranges, OverDrive bounds, and optionally the embedded PMFW `PPTable_t`.

## Important APIs, Types, and Functions

It exports `SMU_13_0_TABLE_FORMAT_REVISION`, platform-cap bits, thermal-controller constants, OD/power-saving-clock versions, OD capability/feature/setting enums, PP clock IDs, `smu_13_0_overdrive_table`, `smu_13_0_power_saving_clock_table`, and packed `smu_13_0_powerplay_table`. `SMU_13_0_PARTIAL_PPTABLE` can omit `PPTable_t smc_pptable` for partial parsing.

## Control Flow

There is no local control flow. `smu13/aldebaran_ppt.c` includes it, parses the VBIOS powerplay table, copies or references the embedded PMFW table, and exposes the driver-facing constraints through common SMU helpers.

## State and Persistence Behavior

The parsed table persists under `smu_table_context` as board policy: platform caps, shutdown temperature, OD ranges, power-saving clocks, and PMFW table data. Firmware receives the embedded `PPTable_t` through table upload.

## Dependencies

It depends on `atom_common_table_header`, `PPTable_t`, and 1-byte packing. The layout mirrors firmware/BIOS expectations and must not be treated as a normal extensible C struct.

## Integration Points

Aldebaran SMU13 code uses this contract for PPTable setup, OverDrive and power-saving clock reporting, BACO/MACO/platform-cap checks, and PMFW table upload.

## Risks and Edge Cases

This base schema lacks newer OD features present in SMU13.0.0/13.0.7. Consumers must use the header matching the ASIC and VBIOS format. OD count fields require bounds checks, and table revision/format mismatches should not be silently accepted.

## Test Signals

Build Aldebaran PM code, parse real VBIOS tables, verify OD/power-saving-clock output, validate thermal/power limits, and confirm PMFW accepts the uploaded table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v13_0_pptable.h -->
