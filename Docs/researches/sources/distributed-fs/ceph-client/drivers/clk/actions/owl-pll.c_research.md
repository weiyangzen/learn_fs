# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-pll.c

Purpose: this file implements OWL PLL clocks, including fixed-rate PLLs, multiplier-based PLLs, and PLLs with explicit value/rate tables.

Important functions: `owl_pll_calculate_mul()` rounds a requested rate by base frequency and clamps it to min/max multiplier. `_get_table_rate()` and `_get_pll_table()` translate table values and choose the closest not-above table rate. `owl_pll_determine_rate()` returns a table rate, fixed base frequency, or base-frequency multiplied result. `owl_pll_recalc_rate()` reads the register and calculates current output. `owl_pll_is_enabled()`, `owl_pll_enable()`, and `owl_pll_disable()` control the enable bit. `owl_pll_set_rate()` writes multiplier/table value and delays for PLL lock.

Control flow/state: hardware registers store enable bits and multiplier/table fields. `udelay(pll_hw->delay)` models post-programming stabilization.

Risks and tests: in `owl_pll_set_rate()`, `reg &= ~mul_mask(pll_hw)` does not shift the mask before clearing, while values are written at `shift`; shifted fields may leave old bits behind. Fixed-frequency PLLs are represented by `width == 0`. Test signals include PLL table selection, recalc after set-rate, enable state, and hardware bring-up for audio/display/EDP PLLs.
