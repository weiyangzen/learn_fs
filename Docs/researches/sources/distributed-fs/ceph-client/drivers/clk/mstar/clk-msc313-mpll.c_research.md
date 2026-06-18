# sources/distributed-fs/ceph-client/drivers/clk/mstar/clk-msc313-mpll.c

Purpose: MStar MSC313 MPLL driver that reports one programmable MPLL rate and fixed-factor divided outputs.

Important APIs/functions: `msc313_mpll_recalc_rate` reads regmap fields for input, loop, and output divisors. `msc313_mpll_probe` sets up MMIO regmap, regmap fields, registers the MPLL clock, creates fixed-factor divider outputs, and publishes a onecell provider.

Control flow: probe maps resource, creates a 16-bit stride-4 regmap, allocates field handles, allocates `clk_hw_onecell_data`, registers the root MPLL, then registers output clocks named `<mpll>_div_N` for dividers 2,3,4,5,6,7,10.

State and persistence: root rate is hardware-backed by config registers; divider outputs are software fixed factors. Allocations are devm-managed.

Dependencies and integration: requires `REGMAP_MMIO`, CCF, platform driver matching `mstar,msc313-mpll`, and OF onecell consumers.

Risks: `clk_data` allocation uses `ARRAY_SIZE(output_dividers)` but `num` is `NUMOUTPUTS`, which is one larger, suggesting a possible under-allocation for `hws[0..NUMOUTPUTS-1]`. The output divider field value is used directly instead of mapped through `output_dividers`, so hardware encoding assumptions matter.

Test signals: KASAN boot for allocation bounds, rate readback tests, onecell indexes for all outputs, and compile testing with regmap-mmio.
