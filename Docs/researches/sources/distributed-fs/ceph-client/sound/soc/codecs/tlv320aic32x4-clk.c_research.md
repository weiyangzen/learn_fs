# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic32x4-clk.c

## Purpose
Implements the Common Clock Framework clock tree used by the TLV320AIC32x4 family codec core. It exposes the codec PLL, codec input mux, ADC/DAC dividers, and bit-clock divider as `clk_hw` providers backed by codec registers.

## Important APIs, Types, and Functions
`struct clk_aic32x4` binds a CCF clock to a device, regmap, and divider register. `struct clk_aic32x4_pll_muldiv` stores PLL P/R/J/D settings, and `struct aic32x4_clkdesc` describes each exported clock. Important callbacks include `clk_aic32x4_pll_prepare()`, `clk_aic32x4_pll_calc_muldiv()`, `clk_aic32x4_pll_set_rate()`, `clk_aic32x4_div_set_rate()`, `clk_aic32x4_bdiv_set_parent()`, `aic32x4_register_clk()`, and exported `aic32x4_register_clocks()`.

## Control Flow
`aic32x4_register_clocks()` rewrites the PLL and codec-clkin parent arrays so the board-provided MCLK name is parent 0, then registers `pll`, `codec_clkin`, `ndac`, `mdac`, `nadc`, `madc`, and `bdiv`. PLL rate setting computes P/R/J/D from requested output and parent rate, writes PLLPR/PLLJ/PLLD registers, then sleeps 10 ms for lock. Divider clocks round up parent/rate to a 1-128 divisor, program the low seven bits of their register, and use the high enable bit for prepare/unprepare. The bit-clock divider extends the divider ops with a mux in `AIC32X4_IFACE3`.

## State and Persistence
State is stored in codec registers through regmap and in devm-managed clock objects. CCF parent/rate decisions persist as register bits until reset or regcache restore by the codec core. No private runtime cache is kept beyond the clock object register address.

## Dependencies and Integration Points
Depends on `linux/clk-provider.h`, clkdev lookup registration, regmap, and register definitions from `tlv320aic32x4.h`. The main codec driver calls `aic32x4_register_clocks()` during probe, then uses these clocks from `hw_params()` and bias transitions.

## Risks
Several regmap reads in `get_parent()` ignore failures and may return stale stack data if hardware access fails. `aic32x4_register_clk()` does not check `clk_hw_register_clkdev()` or `devm_clk_register()` results in the caller loop, so partial clock registration is not surfaced. Divider math uses rounded-up divisors and rates, which can produce close but not exact audio clocks. PLL parent names are assigned from compound literals stored into a static descriptor array, relying on their static storage duration in file scope expressions.

## Test Signals
Exercise PLL parent selection, rate requests near P/R/J/D limits, divider values 1 and 128, invalid too-high PLL input, `bdiv` parent switching, probe with a non-default MCLK name, and codec `hw_params()` paths that consume all exported clock IDs.
