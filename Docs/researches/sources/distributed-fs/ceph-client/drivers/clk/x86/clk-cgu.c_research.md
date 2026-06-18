<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-cgu.c -->
# sources/distributed-fs/ceph-client/drivers/clk/x86/clk-cgu.c

## Purpose

`clk-cgu.c` provides generic LGM CGU branch-clock helpers for fixed clocks, muxes, dividers, fixed factors, gates, and dual dividers.

## Important APIs, Types, And Functions

It implements registration helpers for each `enum lgm_clk_type`, CCF ops for mux parent get/set, divider recalc/determine/set/enable, gate enable/disable/status, and dual-divider recalc/determine/set/enable. `lgm_clk_register_branches()` walks `lgm_clk_branch` tables. `lgm_clk_register_ddiv()` walks `lgm_clk_ddiv_data` tables. Special flags include `CLOCK_FLAG_VAL_INIT`, `MUX_CLK_SW`, `GATE_CLK_HW`, and `DIV_CLK_NO_MASK`.

## Control Flow

SoC probe registers PLLs, then branch clocks, then dual-divider clocks. Branch registration switches on type. Gate entries without `GATE_CLK_HW` intentionally publish `NULL` provider slots so external power management can own the gate.

## State And Persistence Behavior

Register-backed state persists in CGU regmap. Software-only muxes store their parent selection in `mux->reg` when `MUX_CLK_SW` is set. Devm state holds per-clock metadata.

## Dependencies And Integration Points

It depends on Linux CCF helpers, divider/mux APIs, regmap operations from `clk-cgu.h`, and LGM table data.

## Risks And Test Signals

Risks include `min_t()` in dynamic reconfig style patterns not assigning capped values elsewhere, NULL provider slots surprising consumers, dual-divider inability to represent primes above 8, and no locking around most regmap field updates. Test parent selection, rate rounding for divider tables, gate ownership policy, and ddiv 2.5 predivide behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-cgu.c -->
