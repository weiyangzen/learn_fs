<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-cgu-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/x86/clk-cgu-pll.c

## Purpose

`clk-cgu-pll.c` implements PLL CCF operations for the LGM Clock Generation Unit.

## Important APIs, Types, And Functions

`lgm_pll_calc_rate()` computes `(parent * mult + parent * frac / 2^24) / div`. `lgm_pll_recalc_rate()` reads multiplier, divider, and fractional fields from CGU registers; LJPLLs apply an additional divide-by-four. `lgm_pll_enable()` sets the enable bit and polls for it; `lgm_pll_disable()` clears it. `lgm_clk_register_plls()` registers each `lgm_pll_clk_data` entry and stores it by ID.

## Control Flow

LGM probe calls `lgm_clk_register_plls()` before branch and ddiv registration. Each PLL entry allocates devm state, binds regmap and metadata, registers CCF hardware, and fills the onecell array.

## State And Persistence Behavior

PLL configuration and enable state persist in CGU registers. Driver state is devm-managed and contains only metadata and regmap pointer.

## Dependencies And Integration Points

It depends on CCF, regmap polling, OF/device helpers, and `clk-cgu.h` register access helpers. `clk-lgm.c` supplies the PLL inventory.

## Risks And Test Signals

Risks include divide fields reading as zero, short 100 us polling timeout, and LJPLL-specific divider assumptions. Test recalc against known register values, enable/disable status, and all LGM PLL IDs in `clk_summary`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-cgu-pll.c -->
