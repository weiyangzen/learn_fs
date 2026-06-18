# sources/distributed-fs/ceph-client/drivers/clk/clk-moxart.c

Purpose: early OF clock driver for MOXA ART SoC PLL and APB clocks, represented as fixed-factor clocks derived from boot-time register strap values.

Important APIs, types, and functions: `moxart_of_pll_clk_init()` reads PLL multiplier from offset `0x30`, registers a fixed-factor clock, creates a clkdev alias, and adds a simple OF provider. `moxart_of_apb_clk_init()` reads APB divider selector from offset `0x0c`, maps it through `div_idx`, doubles it, and registers the APB fixed-factor clock.

Control flow: each `CLK_OF_DECLARE` callback reads optional `clock-output-names`, gets parent name, maps the node, reads the relevant field, unmaps the node, checks that the parent clock can be obtained, registers the fixed-factor clock, registers clkdev, and adds the provider.

State and persistence: no mutable software state is retained except registered clock objects. Hardware register values are sampled once at boot and modeled as fixed factors.

Dependencies and integration points: depends on OF early clock init, MMIO mapping, common fixed-factor registration, clkdev, and parent clocks described in DT.

Risks and test signals: `of_clk_get()` references are not released with `clk_put()`. If fixed-factor registration fails after mapping has been unmapped there is no allocated private state to clean, but parent references still matter. APB selector values above 4 silently fall back to index 0. Test signals are boot clock rates from strap registers, provider lookup, and clkdev alias availability.
