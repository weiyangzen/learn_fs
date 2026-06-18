# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn35/dcn35_smu.h

## Purpose
This header defines the DCN 3.5 PMFW driver interface subset consumed by the display clock manager. It supplies table layouts, DPM level constants, watermark structures, display idle optimization encoding, and prototypes for the SMU mailbox wrapper.

## Important APIs, Types, And Functions
The file defines `PMFW_DRIVER_IF_VERSION 4`, `DSPCLK_e`, `DisplayClockTable_t`, `WatermarkRowGeneric_t`, `Watermarks_t`, `DpmClocks_t_dcn35`, and `DpmClocks_t_dcn351`. DCN 3.5.1 splits VCN clock arrays into VCN0 and VCN1 fields, while DCN 3.5 has single VCN arrays. `MemPstateTable_t` describes UCLK, memory clock, voltage, and WCK ratio. `struct dcn35_smu_dpm_clks` and `struct dcn351_smu_dpm_clks` pair table pointers with GPU addresses.

The function prototypes cover SMU versioning, clock programming, table transfer, display idle optimization, PHY reference clock powerdown, PME workaround, Z-state policy, DTB/DPREF queries, IPS low-power handling, and DPIA host router bandwidth notification.

## Control Flow And Integration
Clock-manager constructors allocate GPU memory for DPM and watermark tables, use the DRAM address setters declared here, and request SMU table transfers using `TABLE_DPMCLOCKS` or `TABLE_WATERMARKS`. Runtime clock updates call the per-clock setters and low-power helpers. The header is shared by the C wrapper and by DCN 3.5 clock-manager implementation code.

## State And Persistence
The structures describe firmware-owned or shared-memory state. `WatermarkRowGeneric_t` persists until overwritten in SMU table memory. `DpmClocks_t_*` is a snapshot transferred from SMU into driver memory. `display_idle_optimization` encodes PMFW policy bits for display idle handling.

## Dependencies
It depends on `os_types.h` and Display Core's `clk_mgr_internal` and `dcn_zstate_support_state` declarations through users. It must remain binary-compatible with PMFW, so field ordering, sizes, and table constants are dependency boundaries.

## Risks
The file embeds a PMFW interface copy. Any mismatch with firmware table version, array counts, or structure packing can corrupt clock table parsing or watermark transfer. The TODO near `display_idle_optimization` says the type was taken from another ASIC and may be incorrect, which is a direct firmware-contract risk.

## Test Signals
Validation should compare SMU-reported DPM tables against expected ASIC data, verify DCN 3.5 versus DCN 3.5.1 table parsing, and confirm that watermark rows sent through shared memory are accepted by firmware.
