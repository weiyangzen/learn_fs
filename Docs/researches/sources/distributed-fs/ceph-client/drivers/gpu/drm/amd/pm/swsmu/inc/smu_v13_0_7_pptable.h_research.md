<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v13_0_7_pptable.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v13_0_7_pptable.h

## Purpose

`smu_v13_0_7_pptable.h` defines the packed PowerPlay table layout for SMU13.0.7/Plum Bonito-style platforms. It describes VBIOS metadata, platform caps, thermal controller, power limits, OverDrive 8.3 capabilities/settings, fan curve and power-mode settings, per-zone GFX voltage offset controls, and embedded PMFW `PPTable_t`.

## Important APIs, Types, and Functions

Exports include `SMU_13_0_7_TABLE_FORMAT_REVISION`, platform-cap bits, thermal-controller IDs, OD/power-saving-clock versions, OD capability and feature enums, OD setting enums including fan curve points and per-zone voltage-offset points, power-mode setting enums, PP clock IDs, `smu_13_0_7_overdrive_table`, and packed `smu_13_0_7_powerplay_table`.

## Control Flow

No executable flow exists. `smu13/smu_v13_0_7_ppt.c` parses VBIOS bytes with this layout, uses OD bounds for sysfs, and transfers the embedded PMFW table to firmware.

## State and Persistence Behavior

Parsed table instances persist as driver policy for platform caps, OD bounds, power modes, fan settings, shutdown temperature, and PMFW SKU data. The header itself has no state.

## Dependencies

It requires `atom_common_table_header` and `PPTable_t`; struct packing and reserve sizes are binary ABI. The `padding` fields are intentional layout stabilizers.

## Integration Points

Direct integration is the SMU13.0.7 PPT implementation. It feeds AMDGPU OverDrive, power-limit, fan, thermal, BACO/MACO, and PMFW table-upload paths.

## Risks and Edge Cases

The table has many fixed-size OD arrays; counts must not exceed maxima. Per-zone voltage offsets and fan curve settings require strict unit and range handling. Any field insertion before `smc_pptable` changes PMFW table offset. Revision mismatches must be rejected or handled explicitly.

## Test Signals

Build SMU13.0.0 PM, parse known Plum Bonito VBIOS tables, validate OD sysfs ranges, fan curve/power mode behavior, per-zone voltage offset limits, and successful PMFW PPTable upload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v13_0_7_pptable.h -->
