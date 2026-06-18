# sources/distributed-fs/ceph-client/drivers/clk/clk-axm5516.c

## Purpose
Provides the LSI Axxia AXM5516 clock controller, registering PLL, divider, and mux clocks backed by a shared MMIO regmap and exposing them through DT binding indexes.

## Important APIs, Types, And Functions
Common type `axxia_clk` embeds `clk_hw` and regmap. Specialized types are `axxia_pllclk`, `axxia_divclk`, and `axxia_clkmux`. Important callbacks are `axxia_pllclk_recalc`, `axxia_divclk_recalc_rate`, and `axxia_clkmux_get_parent`. Static objects define all PLLs, dividers, muxes, and `axmclk_clocks`. Provider/probe functions are `of_clk_axmclk_get`, `axmclk_probe`, `axmclk_init`, and `axmclk_exit`.

## Control Flow
The core initcall registers a platform driver. Probe maps the resource, creates a regmap, assigns that regmap to each static clock object, registers each `clk_hw`, and adds an OF provider. Recalc callbacks read control registers to compute PLL or divider rates; mux callback reads parent selector fields.

## State And Persistence
Clock objects are static globals; probe fills their regmap pointer. Hardware registers persist PLL dividers, postdividers, reference dividers, clock dividers, and mux selections. The provider returns clocks by binding enum index.

## Dependencies And Integration Points
Depends on `dt-bindings/clock/lsi,axm5516-clks.h`, platform resources, regmap MMIO, CCF, and OF provider APIs. Parent clocks such as `clk_ref0`, `clk_ref1`, and `clk_ref2` must be provided elsewhere.

## Risks And Edge Cases
The driver is read-only for rates and mux parents; it cannot change rates or parents. Static clock objects complicate multiple-instance support. Integer arithmetic calculates `(parent / divisors) * fbdiv`, which may lose precision. Provider lookup assumes every binding index maps to a non-null static object.

## Test Signals
Probe registration count, provider bounds checking, PLL rate formulas, divider one-plus field behavior, mux parent indexes, required external reference clocks, and single-instance assumptions should be covered.
