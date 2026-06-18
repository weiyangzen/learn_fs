# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn42/dcn42_smu.h

## Purpose
This header defines the DCN 4.2 PMFW interface subset used by the display clock manager, including DPM and watermark table layouts plus SMU wrapper prototypes.

## Important APIs, Types, And Functions
`PMFW_DRIVER_IF_VERSION` is `7`. The file defines clock table sizes, `DSPCLK_e`, `DisplayClockTable_t`, `WatermarkRowGeneric_t`, `Watermarks_t`, `WCK_RATIO_e`, `MemPstateTable_t`, and `DpmClocks_t_dcn42`. `DpmClocks_t_dcn42` contains DCFCLK, DISPCLK, DPPCLK, SOCCLK, VCN, VPE, FCLK frequency/voltage, SOC voltage, memory p-state table, enabled level counts, and min/max GFX clocks. `struct dcn42_smu_dpm_clks` couples a DPM table pointer with a GPU address.

Function prototypes expose PMFW version query, clock setters, display idle optimization, PHY refclk powerdown, PME workaround, DRAM address setup, DPM and watermark transfer, Z-state control, DTB control, and DPREF/DTB queries.

## Control Flow And Integration
`dcn42_clk_mgr.c` allocates a `DpmClocks_t_dcn42` buffer, transfers it from SMU through the declared address and transfer functions, and maps it into bandwidth parameters. Watermark notification builds `struct dcn42_watermarks` and transfers it through the same address protocol. Runtime updates call the declared setters for clock and power policy changes.

## State And Persistence
The structures model shared firmware state. `DpmClocks_t_dcn42` is a point-in-time snapshot from PMFW. `dcn42_watermarks` is written by the driver and consumed by firmware. `display_idle_optimization` encodes display-off and S0i2 readiness state.

## Dependencies
It includes `os_types.h` and relies on Display Core users to supply `clk_mgr_internal` and `dcn_zstate_support_state`. It is an ABI boundary with PMFW and must remain layout-compatible.

## Risks
The header contains some copied/commented artifacts and sparse comments around throttler status, suggesting the interface may still be evolving. `DpmClocks_t_dcn42` parsing assumes firmware level counts are trustworthy except where implementation clamps memory p-states. Incorrect WCK ratio values fall back to 1:1 in the clock manager, which can mask firmware data issues.

## Test Signals
Validate `PMFW_DRIVER_IF_VERSION`, table sizes, DPM level counts, memory p-state order and WCK ratios, watermark row encoding, and that DPREF/DTB query functions return sensible nonzero values on supported hardware.
