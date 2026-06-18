<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn21/rn_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn21/rn_clk_mgr.c

## Purpose

`rn_clk_mgr.c` implements the Renoir/DCN2.1 clock manager. It handles VBIOS-SMU clock messages, display low-power entry/exit, DPP DTO updates using actual DPP clock returns, DPM-table-derived bandwidth parameters, memory watermark range notification, boot clock snapshots, and link-rate PHYCLK requests.

## Important APIs, Types, And Functions

The public constructor is `rn_clk_mgr_construct()`. Main callbacks are `rn_update_clocks()`, `rn_init_clocks()`, `rn_enable_pme_wa()`, `rn_notify_wm_ranges()`, `rn_notify_link_rate_change()`, `rn_set_low_power_state()`, and `rn_are_clock_states_equal()`. Important helpers include `rn_get_active_display_cnt_wa()`, `rn_update_clocks_update_dpp_dto()`, `get_vco_frequency_from_reg()`, clock register dump helpers, `build_watermark_ranges()`, `find_socclk_for_voltage()`, `find_dcfclk_for_voltage()`, and `rn_clk_mgr_helper_populate_bw_params()`.

## Control Flow

Construction installs `dcn21_funcs`, sets SMU/DCCG/DFS defaults, obtains SMU version and periodic retraining status, clears the minimum DISPCLK workaround for SMU 55.51.0 or newer, reads VCO from CLK PLL registers, chooses DDR4/LPDDR4 watermark tables by memory type, Green Sardine revision, single-rank/asymmetric config, and retraining state, snapshots boot clock registers, sets DPREFCLK, and optionally replaces hard-coded bandwidth params with SMU DPM table data.

Clock update first handles power state: when safe to lower and no active display is detected, it sends display count 0; otherwise it restores mission mode. It updates hard-min DCFCLK, deep-sleep DCFCLK, clamps DPPCLK to at least 100 MHz, avoids zero DISP/DPP clocks, programs DISPCLK through SMU, and sequences DPP DTO around SMU DPPCLK requests. It uses actual DPPCLK returned by SMU as the DCCG reference.

## State And Persistence Behavior

State persists in `clk_mgr_base->clks`, `pwr_state`, `smu_ver`, `periodic_retraining_disabled`, `rn_bw_params`, selected watermark table, boot clock snapshot, DCCG DTOs, current PHYCLK request table, and PMFW watermark range state. No disk state is written.

## Dependencies And Integration Points

It depends on Renoir MP/CLK registers, `rn_clk_mgr_vbios_smu`, DCE DPREF helpers, DCN20 DPP DTO patterns, DCN20 FPU watermark table generation, PP/SMU DPM table callbacks, integrated BIOS memory info, DMCU PSR, and link encoder state.

## Risks

Active display counting intentionally mixes stream signals and DIG enable state and contains an HDMI display-off workaround; miscounts can prevent low-power entry or cause wake problems. DPM table parsing assumes voltage-level correspondence across FCLK/DCFCLK/SOCCLK arrays. Watermark table selection depends on memory type, retraining support, and ASIC revision. SMU version gates can leave older firmware without hard-min DCFCLK messages.

## Test Signals

Renoir/Green Sardine boot, LPDDR4 and DDR4 systems, display-off/on with HDMI and DP, low-power state entry, SMU DPM table reads, watermark range programming, p-state/retraining workloads, DPPCLK clamp cases, PSR wait-loop updates, and PHYCLK changes on link-rate switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn21/rn_clk_mgr.c -->
