<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v14_0_2_pptable.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v14_0_2_pptable.h

## Purpose

`smu_v14_0_2_pptable.h` defines the packed PowerPlay table layout for SMU14.0.2/14.0.3-era platforms. It is richer than earlier layouts: it records PMFW PPTable/SKU/board/custom SKU offsets and sizes, source of the table, platform caps including LED/mobile OD, two-tier basic/advanced OD bounds, custom OD data, and embedded PMFW `PPTable_t`/`CustomSkuTable_t` payloads.

## Important APIs, Types, and Functions

Exports include table format revisions, platform-cap bits, thermal-controller constants, OD/custom OD versions, OD software feature capability/feature/setting enums, power-mode setting enums, `smu_14_0_2_overdrive_table_id`, `smu_14_0_2_overdrive_table`, `smu_14_0_3_pptable_source`, packed `smu_14_0_2_powerplay_table`, custom OD enums, `smu_14_0_2_custom_overdrive_table`, and `smu_14_0_3_custom_powerplay_table`.

## Control Flow

There is no executable code. `smu14/smu_v14_0_2_ppt.c` parses the layout, uses offset/size fields to locate PMFW SKU/board/custom tables, exposes OD and custom OD ranges, and uploads firmware-facing table data.

## State and Persistence Behavior

Parsed instances persist in driver table context as board policy and firmware payload. Offset fields identify substructures inside the PMFW table; custom table data persists as user/firmware policy until replaced or reset.

## Dependencies

It depends on `atom_common_table_header`, `PPTable_t`, and `CustomSkuTable_t` from the SMU14 PMFW driver interface. Packing and the comment requiring PMFW table 32-byte alignment are part of the ABI.

## Integration Points

Direct consumer is the SMU14.0.2 PPT implementation. It integrates with IFWI/driver-hardcoded/registry PPTable sourcing, AMDGPU OverDrive, power-mode policy, custom SKU handling, and PMFW table transfer.

## Risks and Edge Cases

The table has many absolute offsets and sizes; parsers must validate bounds before dereferencing. The comment says `table_size` offset and PMFW alignment must remain stable. Basic/advanced OD arrays have separate bounds and caps, so sysfs must select the right tier. The OverDrive version is marked TODO/TBD, which increases compatibility risk with firmware and PPGen.

## Test Signals

Build SMU14.0.2 PM, parse IFWI and registry/hardcoded PPTable sources, validate subtable offset bounds, verify OD basic/advanced range reporting, test custom power-mode data, and confirm PMFW accepts uploaded table bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v14_0_2_pptable.h -->
