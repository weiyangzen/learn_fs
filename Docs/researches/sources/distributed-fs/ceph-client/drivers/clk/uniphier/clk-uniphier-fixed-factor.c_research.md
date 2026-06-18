# sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-fixed-factor.c

Purpose: UniPhier helper for registering table-described fixed-factor clocks.

Important APIs/types/functions: `uniphier_clk_register_fixed_factor()` allocates a `clk_fixed_factor`, sets standard `clk_fixed_factor_ops`, optional parent, multiplier, and divisor, then registers via `devm_clk_hw_register()`.

Control flow: called by the core dispatcher for `UNIPHIER_CLK_TYPE_FIXED_FACTOR`. If the data has a parent name, the clock sets `CLK_SET_RATE_PARENT`; otherwise it is parentless. On allocation or registration failure it returns `ERR_PTR`.

State and persistence: device-managed `clk_fixed_factor` stores mult/div and CCF state. There is no MMIO.

Dependencies/integration: consumes `uniphier_clk_fixed_factor_data` from SoC data macros such as `UNIPHIER_CLK_FACTOR` and divider convenience macros.

Risks: data must not provide zero divisors. Parentless fixed factors are allowed by code but must make sense in the clock tree.

Test signals: rates for PLL-derived factor clocks, parentless entries, and compile coverage of all SoC tables using `UNIPHIER_CLK_FACTOR`.
