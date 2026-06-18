# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn42/dcn42_clk_mgr.h

## Purpose
This header declares the DCN 4.2 clock-manager object and public helper surface used by clock-manager selection, SMU table handling, watermark notification, low-power transitions, and FPGA/prod clock update paths.

## Important APIs, Types, And Functions
`DCN42_CLKIP_REFCLK` defines the 48 MHz reference used by CLKIP counter conversion. `struct clk_mgr_dcn42` embeds `clk_mgr_internal` and owns a `dcn42_smu_watermark_set`. `struct dcn42_ss_info_table` contains spread-spectrum lookup information. Public functions include `dcn42_init_clocks`, `dcn42_update_clocks`, `dcn42_clk_mgr_construct`, `dcn42_clk_mgr_destroy`, `dcn42_init_single_clock`, `dcn42_convert_wck_ratio`, `dcn42_build_watermark_ranges`, `dcn42_notify_wm_ranges`, `dcn42_set_low_power_state`, `dcn42_get_max_clock_khz`, `dcn42_get_smu_clocks`, and `dcn42_update_clocks_fpga`.

## Control Flow And Integration
`clk_mgr.c` constructs this manager for DCN 4.2 ASICs. The implementation installs either production or FPGA function tables. External code can query SMU presence, maximum clocks, active display state, and dentist DISPCLK. The header also exposes DPP/DTB DTO update helpers, allowing related code to coordinate DTO programming with clock changes.

## State And Persistence
The object carries base clock-manager state plus SMU watermark memory state. The global `dcn42_ss_info_table` is declared extern and used for spread-spectrum lookup. SMU DPM table transfer uses `struct dcn42_smu_dpm_clks`, forward-declared here to avoid including the full SMU table header in all consumers.

## Dependencies
It depends on `clk_mgr_internal.h` and Display Core types such as `dc`, `dc_state`, `clk_bw_params`, `clk_type`, and `dccg`. It is tightly paired with `dcn42_clk_mgr.c` and `dcn42_smu.h`.

## Risks
The header declares `dcn42_has_active_display` twice, a minor maintenance smell. The broad helper surface exposes internals that could be called out of intended ordering. Since watermark state includes a physical address, constructor/destructor and notify paths must agree on ownership.

## Test Signals
Build tests catch duplicate or mismatched prototypes. Runtime tests should exercise constructor selection, production versus FPGA function tables, helper calls from clock update paths, and destroy behavior after watermark notification.
