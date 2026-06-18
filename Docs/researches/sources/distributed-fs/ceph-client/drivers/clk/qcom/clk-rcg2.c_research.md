# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-rcg2.c

## Purpose
Implements second-generation Qualcomm CMD_RCGR root clock generator ops. It handles parent selection, half-integer dividers, M/N:D counters, frequency-table and generated-rate selection, duty-cycle control, display/byte/GPU special clocks, shared parked RCGs, DFS-enabled serial-engine RCGs, and DisplayPort ratios.

## Important APIs, Types, And Functions
Exports `clk_rcg2_ops`, `clk_rcg2_gp_ops`, `clk_rcg2_floor_ops`, `clk_rcg2_fm_ops`, `clk_rcg2_mux_closest_ops`, `clk_edp_pixel_ops`, `clk_byte_ops`, `clk_byte2_ops`, `clk_pixel_ops`, `clk_gfx3d_ops`, `clk_rcg2_shared_ops`, `clk_rcg2_shared_floor_ops`, `clk_rcg2_shared_no_init_park_ops`, `qcom_cc_register_rcg_dfs()`, and `clk_dp_ops`. Key helpers include `update_config()`, `calc_rate()`, `_freq_tbl_determine_rate()`, `_freq_tbl_fm_determine_rate()`, `clk_rcg2_calc_mnd()`, `__clk_rcg2_configure_parent()`, `__clk_rcg2_configure_mnd()`, `clk_rcg2_configure()`, shared force-enable helpers, DFS table population, and DP/pixel fraction helpers.

## Control Flow
Normal RCG2 rate changes select a table entry, encode parent source, HID divider, M/N/D values, mode bits, and optional hardware-clock-control into CFG/M/N/D registers, then set CMD_UPDATE and poll until hardware clears it. GP ops synthesize M/N/HID values from parent and requested rates. Floor ops pick a floor table entry, FM ops choose among multiple equivalent configurations, and duty-cycle ops rewrite D while M/N mode is active. Display, byte, pixel, and DP ops derive fractional tables or rational approximations from the current parent. GFX3D rate changes ping-pong between PLL parents. Shared RCG ops park disabled clocks on a safe source and cache the intended CFG until re-enable.

## State And Persistence
Persistent hardware state includes CMD status/update bits, CFG source/divider/mode fields, M/N/D registers, shared force-enable bit, DFS perf-level tables, and display-specific fraction programming. Software state includes static descriptors plus `parked_cfg`, dynamically allocated DFS `freq_tbl`, and GFX3D helper parent arrays.

## Dependencies And Integration Points
Depends on regmap, CCF, rational approximation, GCD/math helpers, qcom parent/frequency helpers, and `clk-rcg.h`. It is a central utility for modern Qualcomm CC drivers and works with downstream branches, power domains, display PHYs, serial engines, and GPU clock trees.

## Risks And Edge Cases
`update_config()` timeouts indicate hardware did not accept new configuration. M/N and HID widths cap generated rates, and `clk_rcg2_calc_mnd()` may reduce scale or clamp to fit. Shared RCG parking is designed to avoid wedged GDSCs; wrong safe source indices can still wedge hardware. DFS table allocation is lazy and can fail. Display fraction tables accept only supported parent/rate combinations. GFX3D requires one fixed and two variable PLL parents or returns an error.

## Test Signals
Normal, floor, FM, and GP set-rate paths; duty-cycle set/get; update timeout injection; shared parking while disabled and re-enable restore; DFS registration and perf-level recalc; byte/pixel/eDP/DP rates; and GFX3D PLL ping-pong transitions are high-value tests.
