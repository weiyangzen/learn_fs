# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun4i-pll3.c

## Purpose
This legacy provider registers the sun4i A10 PLL3 video clock as a gate plus divider composite.

## Important APIs, Types, And Functions
The key function is `sun4i_a10_pll3_setup()` declared for `allwinner,sun4i-a10-pll3-clk`. It uses gate bit 31 and a 7-bit divider at shift 0.

## Control Flow
Early init maps the PLL register, creates divider and gate components, reads the output name and parent, registers a composite clock with `CLK_SET_RATE_PARENT`, and adds a simple OF provider.

## State And Persistence
State is the PLL3 gate and divider fields. There is no cleanup/persistence outside the registered clock.

## Dependencies And Integration Points
It depends on CCF composite helpers, OF mapping, and a spinlock. It integrates with legacy display/video clock consumers that need PLL3-derived rates.

## Risks
Video PLL rates are display-sensitive; wrong divider width or parent propagation can break pixel clocks. Early provider allocation failure paths must avoid using unmapped registers.

## Test Signals
Test by checking PLL3 rates in clk-summary and validating display modes that depend on PLL3.
