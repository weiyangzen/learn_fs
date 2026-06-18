# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-rcg.c

## Purpose
Implements first-generation Qualcomm root clock generator (RCG) ops. It supports parent muxing, pre-dividers, M/N:D counters, dynamic double-buffered RCGs, bypass clocks, pixel and escape clock special cases, and an LCC glitch-free mux behavior.

## Important APIs, Types, And Functions
Exports `clk_rcg_ops`, `clk_rcg_floor_ops`, `clk_rcg_bypass_ops`, `clk_rcg_bypass2_ops`, `clk_rcg_pixel_ops`, `clk_rcg_esc_ops`, `clk_rcg_lcc_ops`, and `clk_dyn_rcg_ops`. Core helpers translate fields between registers and descriptors: `ns_to_src()`, `src_to_ns()`, `md_to_m()`, `ns_to_pre_div()`, `mn_to_md()`, `ns_m_to_n()`, `mn_to_ns()`, `mn_to_reg()`, `configure_bank()`, `calc_rate()`, `__clk_rcg_set_rate()`, and dynamic RCG set-rate/parent helpers.

## Control Flow
Parent reads decode source select fields from NS registers; parent writes update source select fields. Rate recalc reads pre-divider, M/N, and mode fields and computes `parent / pre_div * m / n` when M/N is enabled. Determine-rate selects a frequency table entry and parent, optionally asking the parent to change rate. Set-rate programs M/N under reset, updates NS and optional enable-register mode bits, writes pre-divider and source, and releases reset. Dynamic RCGs program the inactive bank when enabled and flip the mux-select bit for glitch-free switching.

## State And Persistence
Hardware state resides in NS, MD, bank, and enable registers. Dynamic RCGs have two banks of NS/MD/pre-divider/source fields, with the active bank encoded by `mux_sel_bit`. Software descriptors persist register addresses, field widths, parent maps, and frequency tables.

## Dependencies And Integration Points
Depends on regmap, CCF, qcom parent/frequency helpers in `common.h`, and definitions from `clk-rcg.h`. SoC CC drivers instantiate these for older hardware generations; downstream branch gates usually consume RCG outputs.

## Risks And Edge Cases
M/N programming must assert and release reset in the correct register, which varies by descriptor. Dynamic RCGs require accurate bank descriptions or the wrong bank can be modified while live. Bypass2 and pixel/escape ops infer current parent from hardware, so invalid source fields return errors or default to parent zero. LCC clocks deliberately switch to XO while programming to avoid a stuck glitch-free mux.

## Test Signals
Recalc against known NS/MD values, set-rate with table and floor variants, dynamic bank switching while enabled and disabled, bypass and bypass2 parent behavior, pixel fraction selection, escape divider boundaries, and LCC enable/disable mux switching are useful signals.
