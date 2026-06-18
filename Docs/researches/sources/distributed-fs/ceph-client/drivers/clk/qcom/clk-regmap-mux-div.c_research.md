# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-mux-div.c

## Purpose
Implements a combined regmap-backed mux and half-integer divider for Qualcomm RCG-like registers. It chooses a parent and divider together, updates CFG, triggers CMD update, and provides CCF rate/parent/recalc operations.

## Important APIs, Types, And Functions
Exports `clk_regmap_mux_div_ops` and `mux_div_set_src_div()`. Internal helpers include `mux_div_get_src_div()`, `is_better_rate()`, `mux_div_determine_rate()`, `__mux_div_set_rate_and_parent()`, `mux_div_get_parent()`, `mux_div_set_parent()`, `mux_div_set_rate()`, `mux_div_set_rate_and_parent()`, and `mux_div_recalc_rate()`.

## Control Flow
`mux_div_set_src_div()` writes source and HID divider fields into CFG and sets CMD update, polling up to 500 us for hardware to clear it. Determine-rate iterates parents and divider values, asks parents to round candidate rates, computes actual rate as `parent * 2 / div`, and selects the best rate at or above the request when possible. Set-rate and set-rate-and-parent recompute best source/divider and cache the chosen raw values after a successful hardware update. Recalc reads current source/divider and resolves the matching parent.

## State And Persistence
Hardware CFG/CMD fields persist the selected parent source and divider. Software caches `md->src` and `md->div` for subsequent parent-only or rate-only changes. Pending dirty configuration is detected and logged in get paths.

## Dependencies And Integration Points
Depends on regmap, CCF parent APIs, delays, and descriptor definitions in `clk-regmap-mux-div.h`. It is used by drivers that need a compact mux/divider not covered by full RCG2 descriptors.

## Risks And Edge Cases
The `src` parameter to `__mux_div_set_rate_and_parent()` is not used directly because the helper searches all parents; callers expecting forced parent selection may be surprised. If CMD dirty remains set, get operations log an error but continue with default output values. Bad parent maps make recalc and get-parent fall back to zero or return wrong rates.

## Test Signals
Best-rate selection across all parents/dividers, CMD update timeout, dirty CFG handling, parent map misses, cached src/div updates, and recalc from hardware fields are important tests.
