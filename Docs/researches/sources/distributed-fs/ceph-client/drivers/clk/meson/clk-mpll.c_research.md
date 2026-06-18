# sources/distributed-fs/ceph-client/drivers/clk/meson/clk-mpll.c

## Purpose
`clk-mpll.c` implements Meson MPLL clocks. MPLLs are PLL-derived outputs with fractional scaling, modeled as `parent_rate / (N2 + SDM/16384)`. They provide audio and fixed-rate derived clocks with optional spread-spectrum and initialization register programming.

## Important APIs, Types, And Functions
The exported ops are `meson_clk_mpll_ops` and `meson_clk_mpll_ro_ops`. `rate_from_params()` converts SDM/N2 fields to a rate. `params_from_rate()` computes SDM/N2 for a requested rate, respecting `CLK_MESON_MPLL_ROUND_CLOSEST`. `mpll_recalc_rate()`, `mpll_determine_rate()`, and `mpll_set_rate()` implement common clock callbacks. `mpll_init()` runs optional init sequences, enables fractional SDM, optionally sets spread spectrum, and sets a misc bit when provided.

## Control Flow
Initialization first calls `clk_regmap_init()`, then optionally writes the init register sequence. It always enables the SDM fractional part and conditionally programs spread-spectrum and misc fields. Determine-rate computes bounded N2/SDM parameters and returns the achievable rate. Set-rate writes SDM first and then N2.

## State, Persistence, And Dependencies
Persistent state is the MPLL register fields described by `struct meson_clk_mpll_data`: `sdm`, `sdm_en`, `n2`, `ssen`, `misc`, optional init regs, and flags. Dependencies include `clk-regmap.h`, `clk-mpll.h`, `parm.h`, `regmap_multi_reg_write()`, Linux common clock helpers, `do_div()`, and module namespace exports.

## Integration Points
SoC clock files instantiate MPLL divider nodes for audio and fixed-frequency trees, commonly with init sequences. Read-only ops expose firmware-owned MPLLs while still allowing recalc/determine. The helper relies on parent PLL rates supplied by the surrounding clock tree.

## Risks And Edge Cases
`N2_MIN` and `N2_MAX` clamp impossible rates; callers may receive a rounded/clamped rate rather than the request. `rate_from_params()` rejects `n2 < 4` and recalc reports zero on invalid hardware state. Spread-spectrum and misc fields are optional via `MESON_PARM_APPLICABLE()`, so SoC descriptors must use null parameters correctly. Init sequences alter hardware immediately on registration.

## Test Signals
Tests should cover rate-to-parameter conversion at min/max N2, round-up versus round-closest behavior, recalc from raw SDM/N2 values, init register writes, SDM enablement, spread-spectrum flag behavior, and read-only consumers.
