<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v11_0_pptable.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v11_0_pptable.h

## Purpose

`smu_v11_0_pptable.h` is the base packed PowerPlay table layout for early SMU11 boards such as Navi10/Arcturus users of the common SMU11 PPTable contract. It combines VBIOS metadata, platform capabilities, board power limits, power-saving clocks, OverDrive limits, and optionally the PMFW `PPTable_t`.

## Important APIs, Types, and Functions

It defines `SMU_11_0_TABLE_FORMAT_REVISION`, platform-cap bits, `SMU_11_0_PP_THERMALCONTROLLER_NONE`, OverDrive and power-saving-clock versions, OD capability/feature/setting enums, PP clock IDs, and maxima for OD features/settings and PP clocks. Structures are `smu_11_0_overdrive_table`, `smu_11_0_power_saving_clock_table`, and packed `smu_11_0_powerplay_table`. The `SMU_11_0_PARTIAL_PPTABLE` guard can omit the embedded PMFW table for partial parsing.

## Control Flow

No executable flow is present. Platform setup routines call common SMU11 PPTable parsing, cast the result to this layout, copy `smc_pptable` into `driver_pptable`, append supplemental atom BIOS DPM data where needed, and then upload the PMFW table.

## State and Persistence Behavior

The parsed table becomes persistent driver policy for the GPU lifetime: power limits, software shutdown temperature, platform caps, thermal controller type, OD bounds, and power-saving clock ranges. The header itself stores no state.

## Dependencies

It depends on the ATOM common table header and a visible `PPTable_t` definition unless partial mode is enabled. Exact `#pragma pack(push, 1)` layout is required for VBIOS binary compatibility.

## Integration Points

Direct includes include `smu11/navi10_ppt.c` and `smu11/arcturus_ppt.c`. Arcturus uses it to copy `powerplay_table->smc_pptable`, check BACO/MACO/fan support, read `software_shutdown_temp`, and derive thermal/power limits.

## Risks and Edge Cases

The same base layout is reused by multiple ASIC paths; platform-specific assumptions must stay in platform code. Wrong table revision or reserve sizing can offset `smc_pptable`. OD feature arrays are fixed size and must be bounded by counts. A missing `PPTable_t` definition will break non-partial builds.

## Test Signals

Build Navi10 and Arcturus PM, parse real VBIOS tables, validate thermal/power/fan caps, verify OD range reporting, and confirm table upload to PMFW succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v11_0_pptable.h -->
