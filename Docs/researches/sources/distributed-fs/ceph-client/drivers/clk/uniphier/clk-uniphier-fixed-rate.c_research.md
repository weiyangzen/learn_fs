# sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-fixed-rate.c

Purpose: UniPhier helper for registering table-described fixed-rate clocks.

Important APIs/types/functions: `uniphier_clk_register_fixed_rate()` allocates `clk_fixed_rate`, sets `clk_fixed_rate_ops`, assigns `fixed_rate`, and registers device-managed CCF hw.

Control flow: called by core dispatcher for `UNIPHIER_CLK_TYPE_FIXED_RATE`. It creates a parentless clock with no flags and returns `ERR_PTR` on allocation or registration failure.

State and persistence: fixed rate value and CCF state persist as device-managed data. No hardware registers are touched.

Dependencies/integration: depends on SoC data using fixed-rate type and CCF fixed-rate ops.

Risks: fixed-rate data must match board/SoC reference clocks; incorrect values skew all descendants. There are no runtime validation hooks.

Test signals: clock summary rates for fixed-rate entries and consumers using those clocks as roots.
