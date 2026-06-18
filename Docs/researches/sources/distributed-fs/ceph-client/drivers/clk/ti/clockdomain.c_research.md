# sources/distributed-fs/ceph-client/drivers/clk/ti/clockdomain.c

Purpose: bridges TI clock framework clocks to OMAP clockdomains. It looks up clockdomain names, stores pointers in `clk_hw_omap`, exposes enable/disable helpers for clocks that do not use default gate ops, and supports DT `ti,clockdomain` nodes.

Important APIs/types/functions: `omap2_clkops_enable_clkdm()`, `omap2_clkops_disable_clkdm()`, `omap2_init_clk_clkdm()`, and `ti_dt_clockdomains_setup()`. `of_ti_clockdomain_setup()` applies one clockdomain name to all parent clocks of a `ti,clockdomain` node.

Control flow: during clock registration, `.init = omap2_init_clk_clkdm` resolves `clkdm_name` through `ti_clk_ll_ops->clkdm_lookup()`. Runtime enable/disable helpers increment/decrement clockdomain use counts. DT setup walks matching nodes after clock registration and retrofits `clkdm_name` onto listed OMAP clocks.

State and persistence: clockdomain pointer and name live in each `clk_hw_omap`. Actual use counts are maintained by platform clockdomain code behind low-level callbacks.

Dependencies/integration: depends on `ti_clk_ll_ops` clockdomain callbacks and on `omap2_clk_is_hw_omap()` to reject basic CCF clocks. Used by gate, interface, DPLL, and clkctrl operations.

Risks: missing clockdomain names are nonfatal but can leave power-domain control incomplete. DT clockdomain setup warns and skips basic clocks, so mixed lists need review. Feature flag `TI_CLK_DISABLE_CLKDM_CONTROL` changes runtime semantics.

Test signals: verify clockdomain lookup logs, enable/disable clocks while checking clockdomain use counts, parse DT `ti,clockdomain` nodes, and test platforms with framework clockdomain control disabled.
