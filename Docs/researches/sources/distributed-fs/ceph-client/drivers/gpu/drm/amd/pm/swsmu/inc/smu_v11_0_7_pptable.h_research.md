<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v11_0_7_pptable.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v11_0_7_pptable.h

## Purpose

`smu_v11_0_7_pptable.h` defines the packed VBIOS PowerPlay table layout for SMU 11.0.7/Sienna Cichlid style boards. It describes driver-side table metadata, platform capabilities, thermal-controller IDs, power-saving clock bounds, OverDrive capabilities/settings, optimized power mode data, and the embedded PMFW `PPTable_t`.

## Important APIs, Types, and Functions

The file exports `SMU_11_0_7_TABLE_FORMAT_REVISION`, platform-cap bits for PowerPlay/SBIOS power source/hardware DC/BACO/MACO/shadow pstate, thermal controller IDs, OverDrive and power-saving-clock versions, OD capability and feature enums, OD setting enums, power-mode setting enums, and PP clock IDs. Key structures are `smu_11_0_7_overdrive_table`, `smu_11_0_7_power_saving_clock_table`, and packed `smu_11_0_7_powerplay_table` ending in `PPTable_t smc_pptable`.

## Control Flow

There is no code flow. Sienna Cichlid PPT code includes the header, parses a VBIOS table into this layout, copies or references the embedded PMFW table, and exposes OD/power-saving constraints to sysfs and common SMU helpers.

## State and Persistence Behavior

The header stores no state. Parsed instances persist in `smu_table_context` as VBIOS-derived board policy: platform caps, shutdown temperature, OD bounds, fan curve points, power modes, and PMFW SKU data. Firmware receives the embedded PMFW table through SMU table upload.

## Dependencies

It requires `atom_common_table_header` and `PPTable_t` from the SMU11 driver interface. Packing is part of the binary ABI; field order, reserve sizes, and array maxima are not arbitrary.

## Integration Points

Direct include is `smu11/sienna_cichlid_ppt.c`. It integrates with AMDGPU PPTable parsing, OverDrive sysfs, fan policy, BACO/MACO platform-cap checks, power-saving clock reporting, and PMFW table transfer.

## Risks and Edge Cases

Changing enum order or struct packing breaks VBIOS parsing. Some OD enum names use the base `SMU_11_0` prefix for auto fan acoustic limit, so consumers must use the exact identifiers. `feature_count` and `setting_count` must be validated against fixed array sizes. Firmware/BIOS table revision mismatches should fail cleanly.

## Test Signals

Build Sienna Cichlid PM code, parse known VBIOS PowerPlay tables, verify OD range/sysfs output, check fan curve and power-mode controls, and confirm PMFW accepts the embedded `PPTable_t`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v11_0_7_pptable.h -->
