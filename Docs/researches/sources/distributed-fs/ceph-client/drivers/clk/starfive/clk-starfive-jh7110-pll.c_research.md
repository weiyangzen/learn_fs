# sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110-pll.c

## Purpose
This built-in driver registers the programmable PLL outputs for JH7110 PLL0, PLL1, and PLL2 using syscon/regmap registers. It supports a fixed set of legal preset frequencies.

## Important APIs, Types, And Functions
`struct jh7110_pll_preset` holds frequency, fractional value, fbdiv, prediv, postdiv1, and integer/fraction mode. `struct jh7110_pll_info` describes each PLL's offsets, masks, and shifts. `jh7110_pll_recalc_rate()`, `jh7110_pll_determine_rate()`, and `jh7110_pll_set_rate()` implement `jh7110_pll_ops`. `jh7110_pll_probe()` obtains the parent syscon regmap, registers three `clk_hw`s, and adds a custom OF provider.

## Control Flow
Rate recalculation reads all relevant fields, interprets integer mode when both DACPD and DSMPD are set, fraction mode when both are clear, and computes `parent * (fbdiv + frac / 2^24) / prediv / 2^postdiv1`. Determine-rate chooses the highest preset not exceeding the request, but only when the parent is the expected 24 MHz oscillator. Set-rate requires an exact preset frequency and writes mode, prediv, fbdiv, optional frac, and postdiv fields.

## State And Persistence
PLL configuration persists in syscon registers shared with the broader system controller. The driver keeps only static metadata and `regmap` access state. Debugfs can expose decoded register fields per PLL.

## Dependencies And Integration Points
It depends on `dt-bindings/clock/starfive,jh7110-crg.h`, an OF parent syscon node, and a 24 MHz input clock. The SYS clock driver consumes these PLL outputs by firmware name when available.

## Risks
Only preset rates are supported; arbitrary clock framework requests fail. Parent rates other than 24 MHz make determine-rate fall back to current hardware rate and make set-rate invalid. There is no explicit PLL lock wait after programming in this file. Division by zero is possible if hardware reports prediv zero, though valid presets avoid it.

## Test Signals
Validate each preset rate, rejected non-preset rates, debugfs decoded fields, SYS CPU-root notifier behavior during PLL0 changes, and boot operation when SYS uses these PLL outputs instead of fixed-factor fallbacks.
