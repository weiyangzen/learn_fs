# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-pll.c

Purpose: legacy AT91 PLL provider for PLLA/PLLB registers at `CKGR_PLLAR + id * 4`. It computes divider/multiplier pairs within input/output constraints and programs optional output/current-control fields.

Important APIs and data: `at91_clk_register_pll()` registers the clock. Layout constants describe RM9200, SAM9G45, SAM9G20 PLLB, and SAMA5D3 bit layouts. `struct clk_pll` stores id, div, mul, output range index, layout, characteristics, regmap, and PM state.

Control flow: prepare reads current PLL register, skips if already ready with matching div/mul, programs ICPR/out/count/mul/div, then waits for lock. Determine-rate calls `clk_pll_get_best_div_mul()` to scan valid dividers, choose closest multiplier, and verify output range. set-rate only updates cached div/mul/range; hardware changes occur when prepared.

State and persistence: cached div/mul/range are initialized from hardware and later set by rate changes. Save stores parent rate, calculated rate, and status; restore checks that firmware retained register values and warns if not.

Dependencies and integration: older SoC setup and DT compat paths use this provider. It depends on `clk_pll_characteristics`, `clk_pll_layout`, regmap, and PMC status lock bits.

Risks: lock wait is unbounded; restore passes `PLL_REG(id)` into a ready helper that expects an id, so warnings may be unreliable; arithmetic uses integer division and may select close but not exact rates. Test signals include PLL lock bits, chosen div/mul/out fields, invalid rate rejection, and restore warnings after backup suspend.
