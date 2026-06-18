<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn31/dcn31_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn31/dcn31_clk_mgr.c

## Purpose

`dcn31_clk_mgr.c` implements the DCN3.1/Yellow Carp clock manager. It handles SMU-backed clock updates, Z-state and DTBCLK control, display idle optimization, DMCUB clock notification, DPM-table-derived bandwidth params, DDR5/LPDDR5 watermark programming, and SMU shared-memory allocation.

## Important APIs, Types, And Functions

Public functions are `dcn31_update_clocks()`, `dcn31_init_clocks()`, `dcn31_are_clock_states_equal()`, `dcn31_get_dtb_ref_freq_khz()`, `dcn31_clk_mgr_construct()`, and `dcn31_clk_mgr_destroy()`. Helpers include `dcn31_get_active_display_cnt_wa()`, `dcn31_disable_otg_wa()`, `get_vco_frequency_from_reg()`, `dcn31_build_watermark_ranges()`, `dcn31_notify_wm_ranges()`, `dcn31_get_dpm_table_from_smu()`, `find_clk_for_voltage()`, `dcn31_clk_mgr_helper_populate_bw_params()`, and `dcn31_set_low_power_state()`.

## Control Flow

Construction initializes nested manager state, allocates framebuffer watermark and DPM tables with dummy fallbacks, queries SMU version, reads dentist VCO, chooses DDR5/LPDDR5 watermark table by BIOS memory type, sets DPREF/ref DTB clock defaults, installs bandwidth params, and if debug `pstate_enabled` is true, transfers DPM clocks from SMU, logs them, and populates bandwidth params with FCLK/MemClk/voltage/WCK ratio/DCFCLK/SOCCLK/dispclk/dppclk data.

Clock update first manages Z-state support and periodic detection, DTBCLK enable/disable, and display idle optimization based on `safe_to_lower`. It sends DCFCLK and deep-sleep DCFCLK requests, clamps DPPCLK to 100 MHz, temporarily disables OTGs for DPMS-off or virtual streams around DISPCLK changes, sequences DPP DTOs and DPPCLK, then sends a `DMUB_CMD__CLK_MGR_NOTIFY_CLOCKS` command to DMCUB with the latest clock values.

## State And Persistence Behavior

Persistent state includes SMU watermark memory/address, selected watermark table, DPM-derived `dcn31_bw_params`, power state, Z-state support, DTBCLK enable/reference, SMU version/presence, clock values, DCCG DTOs, DMCUB-notified clock state, and PMFW constraints. Destroy frees allocated watermark memory.

## Dependencies And Integration Points

It depends on DCN20 DPP DTO helpers, DCN31 SMU helpers, DCE DPREF helper, DMCUB command service, link service, Yellow Carp/MP/CLK registers, BIOS integrated info, and framebuffer allocation helpers.

## Risks

Z-state and DTBCLK sequencing depends on `safe_to_lower`; wrong ordering can affect idle residency or timing. The OTG workaround touches active timing generators and sync context for DPMS-off/virtual streams, so incorrect pipe selection can blank the wrong output. DPM parsing relies on voltage fallback logic and WCK ratio mapping. If `pstate_enabled` is false, bandwidth params remain mostly static defaults.

## Test Signals

Yellow Carp boot with DDR5 and LPDDR5, pstate-enabled/disabled debug modes, Z8/Z10 transitions, DTBCLK users, display idle entry/exit, DPMS-off and virtual-stream DISPCLK changes, DMCUB clock notification verification, watermark upload, DPM table logging, WCK ratio handling, and destroy memory cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn31/dcn31_clk_mgr.c -->
