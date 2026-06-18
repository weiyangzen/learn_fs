# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs-pll.c

Purpose: Generic PLL calculator for MIPI CCS, SMIA, and SMIA++ camera sensors. It computes video-timing and operational PLL front/back branch dividers, pixel rates, and CSI bus rates from sensor limits and requested bus/link parameters.

Important APIs/types/functions: Exported API is `ccs_pll_calculate()`. Helper groups include divider normalization (`clk_div_even()`, `clk_div_even_up()`, `is_one_or_even()`), validation (`bounds_check()`, `check_fr_bounds()`, `check_bk_bounds()`, `check_ext_bounds()`), debug printing (`print_pll()`, `print_pll_flags()`), VT divisor search (`ccs_pll_find_vt_sys_div()`, `__ccs_pll_calculate_vt_tree()`, `ccs_pll_calculate_vt_tree()`, `ccs_pll_calculate_vt()`), and OP branch search (`ccs_pll_calculate_op()`).

Control flow: `ccs_pll_calculate()` normalizes lane counts for non-lane-speed mode, chooses OP limit/state pointers depending on dual-PLL/no-OP-clock flags, validates required inputs, rejects non-integer OP pixel divisors unless flexible division is allowed, computes SDR OP system clock from link frequency and bus type, derives CSI pixel rate, computes OP pre-PLL divider bounds, reduces the desired clock ratio with `gcd()`, and iterates valid pre-PLL divisors. Each candidate computes OP PLL multiplier/sys/pix divisors, validates OP bounds, computes or later separately computes VT clocks, checks FIFO derating/overrating constraints, and exits on the first valid configuration. Dual-PLL mode then runs a separate VT-tree calculation.

State/persistence: Stateless calculation helper. It mutates caller-provided `struct ccs_pll` output fields and logs debug data; it does not touch sensor hardware.

Dependencies/integration: Uses Linux `gcd`, `lcm`, device logging, integer division helpers, and `ccs-pll.h`. Sensor drivers provide `struct ccs_pll_limits` and input bus configuration, then program returned fields into sensor registers.

Risks: The algorithm is integer-heavy and many frequency products are 32-bit, so unusual high-frequency limits can overflow. It returns the first valid search result, not necessarily a globally optimal clock tree. Flexible OP pixel division, DDR flags, C-PHY constants, FIFO derating/overrating, and dual PLL branching create a broad matrix where regressions are easy. Bounds debug strings include a few naming inconsistencies but do not affect calculation.

Test signals: Known-good CCS/SMIA sensor tables should verify exact output branches and pixel rates for D-PHY, C-PHY, dual PLL, no OP clocks, DDR flags, flexible divisors, and FIFO derating/overrating. Fuzz or property tests should assert output fields stay within all declared limits and return `-EINVAL` for zero required inputs or impossible divisors.
