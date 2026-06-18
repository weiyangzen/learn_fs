<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c

## Purpose

`dcn20_clk_mgr.c` is the shared Navi/DCN2 clock-manager implementation. It converts bandwidth results into SMU hard-min/voltage requests, DENTIST DISPCLK/DPPCLK divider programming, DPP DTO updates, p-state handshakes, PHYCLK link-rate requests, and clock-state query helpers.

## Important APIs, Types, And Functions

Public/shared functions include `dentist_get_did_from_divider()`, `dcn20_update_clocks_update_dpp_dto()`, `dcn20_update_clocks_update_dentist()`, `dcn2_update_clocks()`, `dcn2_update_clocks_fpga()`, `dcn2_init_clocks()`, `dcn2_read_clocks_from_hw_dentist()`, `dcn2_get_clock()`, and `dcn20_clk_mgr_construct()`. Local callbacks include `dcn2_enable_pme_wa()`, `dcn2_are_clock_states_equal()`, and `dcn2_notify_link_rate_change()`. Register metadata is provided by `clk_mgr_regs`, `clk_mgr_shift`, and `clk_mgr_mask`.

## Control Flow

Construction installs DCN2 callbacks, register tables, SMU/DCCG pointers, spread-spectrum defaults, computes dentist VCO from `CLK3_CLK_PLL_REQ`, derives DPREFCLK from DFS slice 2, disables DFS bypass for dGPU, and reads spread-spectrum info. `dcn2_update_clocks()` handles resume/forced reset by reading current DENTIST dividers, updates display count through NV SMU, applies forced minimum DCFCLK, sends hard-min requests for DCFCLK, deep-sleep DCFCLK, SOCCLK, UCLK, and display voltage, updates p-state handshake support, and sequences DPP DTO versus DENTIST changes based on whether DPPCLK is being lowered.

The DENTIST helper calculates weighted dividers from VCO/current clocks, works around transitions to/from divider 127 by adding or dropping OTG pixels, then writes DISPCLK and DPPCLK dividers and waits for change-done bits. DPP DTO updates use per-pipe bandwidth DPP clocks and avoid lowering DTOs unless safe.

## State And Persistence Behavior

Clock state persists in `clk_mgr_base->clks`, DCCG `ref_dppclk` and `pipe_dppclk_khz`, SMU hard-min/voltage state, DENTIST hardware dividers, display count, PSR wait-loop settings, and `cur_phyclk_req_table`. No disk state is used.

## Dependencies And Integration Points

The file integrates with `dccg`, DCE DPREF helpers, PP/SMU NV callbacks, stream encoder FIFO calibration, DMCU PSR, link-service PHY rate changes, DC debug/config flags, and resource pool bandwidth bounding. Later DCN versions reuse its DENTIST and DTO helpers.

## Risks

Clock lowering order is safety-critical. Incorrect DENTIST divider conversion or missing divider-127 workaround can corrupt output. p-state support updates depend on `safe_to_lower` and active plane count. Optional SMU callbacks mean some voltage/display-count requests may be skipped. FPGA and forced-clock modes intentionally bypass parts of normal programming and need separate coverage.

## Test Signals

Mode sets with DPPCLK raise/lower, divider-127 transitions, active-display count changes, p-state supported/unsupported transitions, link-rate PHYCLK changes, suspend/resume, forced clock modes, FPGA builds, PSR wait-loop updates, and SMU hard-min trace validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c -->
