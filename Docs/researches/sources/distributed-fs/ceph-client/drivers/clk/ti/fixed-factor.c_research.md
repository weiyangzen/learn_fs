# sources/distributed-fs/ceph-client/drivers/clk/ti/fixed-factor.c

Purpose: TI-specific DT wrapper for fixed-factor clocks. It reads TI property names and registers a standard CCF fixed-factor clock with alias and optional autoidle setup.

Important APIs/types/functions: `of_ti_fixed_factor_clk_setup()` for `ti,fixed-factor-clock`. It uses `clk_register_fixed_factor()`, `ti_dt_clk_name()`, `ti_clk_add_alias()`, and `of_ti_clk_autoidle_setup()`.

Control flow: setup requires `ti,clock-div` and `ti,clock-mult`, optionally sets `CLK_SET_RATE_PARENT`, obtains the first parent name, registers the fixed-factor clock, adds an OF provider, configures autoidle, and creates a clkdev alias.

State and persistence: no private state beyond the CCF fixed-factor clock and optional autoidle side effects.

Dependencies/integration: depends on DT properties, one parent clock, CCF fixed-factor ops, and TI alias/autoidle helpers.

Risks: missing div/mult properties abort registration. The code does not validate zero divisors directly; behavior depends on CCF fixed-factor validation. Parent absence still passes a NULL parent name.

Test signals: DT nodes with valid and missing mult/div, set-rate-parent propagation, provider lookup, and alias lookup by output name.
