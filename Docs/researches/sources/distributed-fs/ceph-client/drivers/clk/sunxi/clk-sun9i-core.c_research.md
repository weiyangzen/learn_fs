# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun9i-core.c

Provides factor-clock definitions for Allwinner A80 core clocks: PLL4, GT bus, AHB0/1/2, APB0, and APB1. Each is registered through the shared Sunxi factors framework.

`sun9i_a80_get_pll4_factors()` normalizes PLL4 to 6/12/24 MHz steps and selects `n`, `m`, and `p`. `sun9i_a80_get_gt_factors()` implements a simple divide-by-1..4 path. `sun9i_a80_get_ahb_factors()` selects a power-of-two `p` divider. `sun9i_a80_get_apb1_factors()` attempts an `m,p` divider for APB1. Each clock has a `clk_factors_config`, `factors_data`, spinlock, setup function, and `CLK_OF_DECLARE()` compatible.

Each clock's mux/factor/enable state persists in its mapped register. The GT bus clock is registered as critical through `sunxi_factors_register_critical()` so it remains enabled. It depends on `clk-factors.h`, `order_base_2()`, OF early registration, and A80 DT compatibles such as `allwinner,sun9i-a80-pll4-clk` and `allwinner,sun9i-a80-apb1-clk`.

Factor math is the primary risk because invalid `m/p/n` values directly corrupt bus rates. The APB1 helper's `req->m = (req->parent_rate >> req->p) - 1` is worth targeted review because it appears to omit division by the requested divisor and can exceed the five-bit field. Test signals include rate-rounding for low/high boundaries, boot-critical bus stability, and CCF summaries matching the A80 manual.
