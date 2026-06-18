# sources/distributed-fs/ceph-client/drivers/clk/meson/c3-pll.c

## Purpose
`c3-pll.c` describes the Amlogic C3 PLL clock controller. It exposes fixed PLL-derived outputs, GP0 PLL, HIFI PLL, and MCLK PLL paths, plus two MCLK output chains. The driver registers the `amlogic,c3-pll-clkc` provider and maps C3 PLL dt-binding IDs to clock hardware.

## Important APIs, Types, And Functions
The source uses `struct clk_regmap`, `struct clk_fixed_factor`, `struct clk_div_table`, `struct pll_mult_range`, and `struct reg_sequence`. PLL DCO nodes use `meson_clk_pll_ops`; output dividers use `clk_regmap_divider_ops`; fixed PLL dividers use fixed-factor clocks and read-only gates; MCLK selectors and gates use generic regmap mux/gate ops. `c3_pll_hw_clks[]` is the dt-binding ID map, `c3_pll_clkc_data` is the common registration payload, and `c3_pll_clkc_driver` probes through `meson_clkc_mmio_probe()`.

## Control Flow
Probe is generic: map the MMIO resource, create a regmap, register every clock in the C3 PLL array, and add an OF provider. Runtime PLL enable, disable, recalc, determine-rate, and set-rate behavior is delegated to `clk-pll.c`. GP0 and HIFI PLLs have initialization register sequences and multiplier ranges; MCLK PLL has an init sequence, an OD divider, a special one-based/allow-zero post divider, and MCLK0/MCLK1 mux/divider/gate chains.

## State, Persistence, And Dependencies
Persistent hardware state is in ANACTRL registers such as `ANACTRL_FIXPLL_CTRL4`, `ANACTRL_GP0PLL_CTRL*`, `ANACTRL_HIFIPLL_CTRL*`, and `ANACTRL_MPLL_CTRL*`. Linux state is the registered `clk_hw` graph. Dependencies include `clk-regmap.h`, `clk-pll.h`, `meson-clkc-utils.h`, platform probing, fixed-factor clock ops, and `dt-bindings/clock/amlogic,c3-pll-clkc.h`.

## Integration Points
Other C3 clock controllers and device-tree consumers refer to parent names such as `fix`, `top`, `mclk`, `fdiv2`, `fdiv2p5`, `fdiv3`, `fdiv4`, `fdiv5`, `fdiv7`, `gp0`, and `hifi`. The output table makes PLL-generated clocks available to peripheral controllers and audio/MCLK users. The implementation relies on the common Meson PLL helper for lock polling and rate programming.

## Risks And Edge Cases
PLL init sequences are tightly coupled to silicon programming manuals; wrong constants can prevent lock or produce unstable rates. OD tables intentionally limit supported encodings below the raw bitfield maximum. Rate changes inherit `clk-pll.c` behavior, including temporary disable/re-enable and fallback attempts if the PLL does not lock.

## Test Signals
Build coverage with C3 PLL enabled, probe of `amlogic,c3-pll-clkc`, `clk_summary` inspection of fixed and programmable PLL outputs, rate-set tests for GP0/HIFI/MCLK PLLs, lock-failure logging checks, and audio MCLK consumer tests are high-value. Device-tree tests should confirm all named parent clocks are provided and every `CLKID_*` entry matches the binding header.
