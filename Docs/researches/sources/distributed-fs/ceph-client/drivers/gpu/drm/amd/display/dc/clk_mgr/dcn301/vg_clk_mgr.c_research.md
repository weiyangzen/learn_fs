<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn301/vg_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn301/vg_clk_mgr.c

## Purpose

`vg_clk_mgr.c` implements the Van Gogh/DCN3.0.1 clock manager. It manages SMU-backed display/DPP/DCF clocks, display idle low-power state, framebuffer-backed DPM and watermark tables, BIOS/SMU-derived bandwidth parameters, and Van Gogh-specific watermark selection.

## Important APIs, Types, And Functions

Public functions are `vg_clk_mgr_construct()` and `vg_clk_mgr_destroy()`. Main callbacks are `vg_update_clocks()`, `vg_init_clocks()`, `vg_enable_pme_wa()`, `vg_notify_wm_ranges()`, and `vg_are_clock_states_equal()`. Important helpers include `vg_get_active_display_cnt_wa()`, VCO and clock-register dump helpers, `vg_build_watermark_ranges()`, `find_max_clk_value()`, `find_dcfclk_for_voltage()`, `vg_clk_mgr_helper_populate_bw_params()`, and `vg_get_dpm_table_from_smu()`.

## Control Flow

Construction initializes nested `clk_mgr_vgh`/`clk_mgr_internal` state, allocates framebuffer memory for watermarks and DPM clocks with dummy fallbacks, queries SMU version, reads dentist VCO, chooses DDR4 or LPDDR5 watermark table from BIOS memory type, snapshots boot clocks, sets DPREFCLK/spread-spectrum state, transfers DPM clocks from SMU into GPU memory, and populates bandwidth params from BIOS plus SMU table. It frees the temporary DPM table before returning.

Clock updates handle low-power display idle by sending `display_idle_optimization` when safe to lower and no active display remains, update hard-min DCFCLK and deep-sleep DCFCLK unless disabled by debug, clamp DPPCLK to 100 MHz, set DISPCLK, and sequence DPP DTOs relative to SMU DPPCLK changes. Watermark notification builds `struct watermarks`, sets its MC address, and transfers it to SMU.

## State And Persistence Behavior

Persistent state includes `clk_mgr_vgh.smu_wm_set`, selected `vg_bw_params`, SMU version/presence, boot clock snapshot, power state, DCCG DTOs, PMFW clock constraints, and watermark table contents. `vg_clk_mgr_destroy()` frees allocated watermark framebuffer memory.

## Dependencies And Integration Points

It depends on DCN20 DTO helpers, DCN20 FPU watermark table adjustment, Van Gogh register headers, `dcn301_smu`, BIOS integrated info, framebuffer memory allocation helpers, DCCG, DC debug flags, and external DDR4/LPDDR5 watermark tables.

## Risks

Dummy fallback tables let construction continue when GPU memory allocation fails, but SMU transfers are then skipped because MC address is zero. DPM table parsing assumes nonzero reverse-filled DF pstates and voltage lookup consistency. The low-power active-display workaround can miscount. The DPPCLK clamp lacks the Renoir guard for zero, so a zero request becomes 100 MHz.

## Test Signals

Van Gogh boot with SMU present/absent, framebuffer allocation failure fallback, DPM table transfer, DDR4 versus LPDDR5 watermark selection, display idle entry/exit, DPPCLK lowering/raising, DCFCLK debug disable, watermark upload, and destroy-time framebuffer free checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn301/vg_clk_mgr.c -->
