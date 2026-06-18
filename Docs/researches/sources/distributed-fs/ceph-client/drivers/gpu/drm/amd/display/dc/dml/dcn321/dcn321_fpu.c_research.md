# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn321/dcn321_fpu.c

## Purpose
This DCN3.21 FPU file defines the ASIC IP parameters and SoC bounding box used by DML, then updates that bounding box from runtime clock tables, BIOS data, debug overrides, and display-core configuration. It is responsible for producing usable voltage/clock states for DML and DML2 on DCN321 hardware.

## Important APIs, Types, And Functions
Global `dcn3_21_ip` describes hardware limits such as DPP/OTG/DSC counts, ROB/DET/config return buffer sizes, chunk sizes, line buffer size, writeback limits, cursor buffers, DCC support, DP2 outputs, and DML workarounds. Global `dcn3_21_soc` seeds latency, bandwidth percentage, channel, bus width, spread-spectrum, MALL, and default clock-limit data. Helpers include `get_optimal_ntuple()`, `calculate_net_bw_in_kbytes_sec()`, sorted-table insertion/removal/swap helpers, `sort_entries_with_same_bw()`, `remove_inconsistent_entries()`, `override_max_clk_values()`, `build_synthetic_soc_states()`, and `dcn321_get_optimal_dcfclk_fclk_for_uclk()`. The public entry point is `dcn321_update_bw_bounding_box_fpu()`.

## Control Flow And State
`dcn321_update_bw_bounding_box_fpu()` asserts FPU availability, applies `dc->config`, debug, `dc->bb_overrides`, BIOS SoC info, VRAM channel information, DSC and prefetch workarounds, PLL/refclk data, and then builds clock states. In legacy mode it constructs DCFCLK/UCLK states from PMFW tables and STA targets; otherwise `build_synthetic_soc_states()` creates sorted points of interest from DCFCLK targets, max DCFCLK, UCLK DPMs, and FCLK DPMs, removes unsupported/duplicate/inconsistent entries, rounds clocks to DPMs, and indexes states. It then calls `dml_init_instance()` for `dc->dml` and the current state's DML, and copies clock/latency overrides into `dc->dml2_options`.

## State And Persistence Behavior
The file mutates global `dcn3_21_ip` and `dcn3_21_soc` in place, plus `dc->dml`, `dc->current_state->bw_ctx.dml`, and `dc->dml2_options.bbox_overrides`. These are runtime driver state updates, not persistent storage, but because the globals are mutable, repeated calls accumulate the latest override values.

## Dependencies And Integration Points
Includes clock manager/resource headers, DCN32/DCN321 resource headers, and `display_mode_vba_util_32.h`. It depends on BIOS callbacks (`get_soc_bb_info`), VRAM info, `clk_bw_params`, `dc->debug`, `dc->bb_overrides`, `dc->clk_mgr`, and `dcn32_calc_num_avail_chans_for_mall()`. It initializes DML as `DML_PROJECT_DCN32`, reusing the DCN32 DML function table.

## Risks
Clock-table synthesis mixes MHz, MT/s, percentages, and channel widths, so unit errors are high impact. Several loops iterate backward with unsigned state counts and assume nonzero entries. The mutable global bounding box can leak override assumptions across contexts if not refreshed carefully. Legacy and synthetic paths can produce different state counts, and the `num_states > MAX_NUM_DPM_LVL` path asserts and returns early. Incorrect BIOS channel data changes MALL allocation and bandwidth limits.

## Test Signals
Useful checks include DML state count and monotonicity, clock-limit dumps after BIOS/debug override, successful `dml_init_instance()` with `DML_PROJECT_DCN32`, DML2 override table contents, and display validation across DC/AC clock tables. Edge tests should cover single-entry PMFW tables, missing FCLK/DPPCLK/PHYCLK data, DC-mode overwrite disabled/enabled, BIOS latency overrides, nondefault VRAM channel width/count, and legacy vs synthetic SoC bounding-box paths.
