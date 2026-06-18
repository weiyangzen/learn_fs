# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn42/dcn42_clk_mgr.c

## Purpose
This file implements the DCN 4.2 clock manager. It initializes clock state, reads SMU DPM tables, programs display and bandwidth clocks through PMFW, updates DPP DTOs, handles low-power display idle policy, manages watermark ranges, exposes FPGA and production function tables, and constructs/destroys the DCN 4.2 clock-manager object.

## Important APIs, Types, And Functions
Major functions include `dcn42_update_clocks`, `dcn42_init_clocks`, `dcn42_get_smu_clocks`, `dcn42_get_dpm_table_from_smu`, `dcn42_notify_wm_ranges`, `dcn42_build_watermark_ranges`, `dcn42_update_clocks_update_dpp_dto`, `dcn42_update_clocks_update_dtb_dto`, `dcn42_get_clock_freq_from_clkip`, `dcn42_dump_clk_registers`, `dcn42_set_low_power_state`, `dcn42_update_clocks_fpga`, `dcn42_get_max_clock_khz`, and `dcn42_clk_mgr_construct`.

## Control Flow And Integration
Construction sets register tables, DCCG, SMU presence/version, default DPREF/DTB clocks, BIOS-derived memory parameters, and SMU-derived DPM tables. Initialization resets live clock state, configures DP DTO source clock based on spread spectrum, dumps boot clocks, and tracks whether DTBCLK is enabled.

Runtime `dcn42_update_clocks` first handles Z-state and DTB enable/disable based on `safe_to_lower`, active display detection, and low-power transition state. It then updates DCFCLK and deep-sleep DCFCLK, clamps debug minimums, programs DISPCLK with the DCN 3.5 OTG workaround, manages DPPCLK lowering/raising order relative to DPP DTOs, optionally updates DTB DTO state, and notifies DMCUB with the latest clocks.

SMU clock-table retrieval allocates a GART buffer, transfers `DpmClocks_t_dcn42` from PMFW, logs levels, populates the bandwidth clock table, reverses memory p-state order into ascending table entries, sets WCK ratios, and installs a fixed DTBCLK level.

## State And Persistence
The live clock state is stored in `clk_mgr_base->clks`; bandwidth limits are stored in the static `dcn42_bw_params` object. Watermark notification allocates a GART table, sends it to SMU, and frees it immediately after transfer. Firmware-side persistent state includes clock hardmins, DTB enablement, display idle optimization bits, watermark table contents, and Z-state policy. FPGA mode mutates clock values locally and pushes them through `dm_set_dcn_clocks`.

## Dependencies
The file depends on DCCG, DCE/DCN clock helpers, DCN 4.2 and CLK 15 register headers, `dcn42_smu.c`, DMUB command infrastructure, link service, BIOS integrated info, and DC debug/config flags. It also reuses `dcn35_disable_otg_wa`, showing cross-generation workaround dependency.

## Risks
The production path uses a static `dcn42_bw_params`, which is simple but sensitive to multi-device assumptions. `dcn42_notify_wm_ranges` skips if `WM_A` is already valid, so stale watermark state can suppress resend. DTB DTO update is a no-op for DCN 4.2, but state still tracks DTB enable and reference clock. The constructor calls `dcn42_get_smu_clocks` both inside integrated-info handling and again after setting `bw_params`, so repeated transfers should be harmless but are worth monitoring. Low-power exit is currently empty.

## Test Signals
Validate SMU table parsing, active display detection, low-power idle optimization, DPP DTO cleanup for inactive pipes, DMCUB clock notification, watermark transfer acceptance, DTB enable behavior on hardware with and without DTB, and FPGA clock update behavior. Hardware readback via CLKIP counters is a key diagnostic signal.
