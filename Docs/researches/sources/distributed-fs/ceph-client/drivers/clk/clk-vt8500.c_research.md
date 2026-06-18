# sources/distributed-fs/ceph-client/drivers/clk/clk-vt8500.c

## Purpose
`clk-vt8500.c` provides early OF-declared clock registration for VIA/Wondermedia SoC clock controllers. It supports memory-mapped PMC-backed gated clocks, divisor clocks, combined gated-divisor clocks, and several PLL encoding families (`VT8500`, `WM8650`, `WM8750`, and `WM8850`). The driver is intended for platform clock setup during boot rather than as a normal platform device.

## Important APIs, Types, And Functions
`struct clk_device` models a device clock with optional divisor and enable registers, enable bit, divisor mask, and shared lock. `struct clk_pll` models a PLL register plus PLL type. `vtwm_set_pmc_base()` maps the PMC either from the `via,vt8500-pmc` node or the legacy physical base `0xD8130000`. Device clock operations are `vt8500_dclk_enable()`, `vt8500_dclk_disable()`, `vt8500_dclk_is_enabled()`, `vt8500_dclk_recalc_rate()`, `vt8500_dclk_determine_rate()`, and `vt8500_dclk_set_rate()`.

PLL support is split into bit-calculation helpers for each hardware family: `vt8500_find_pll_bits()`, `wm8650_find_pll_bits()`, `wm8750_find_pll_bits()`, `wm8850_find_pll_bits()`, and `wm8750_get_filter()`. CCF-facing PLL operations are `vtwm_pll_set_rate()`, `vtwm_pll_determine_rate()`, and `vtwm_pll_recalc_rate()`. OF init functions are registered through `CLK_OF_DECLARE()` for `via,vt8500-device-clock`, `via,vt8500-pll-clock`, `wm,wm8650-pll-clock`, `wm,wm8750-pll-clock`, and `wm,wm8850-pll-clock`.

## Control Flow
For a device clock node, `vtwm_device_clk_init()` ensures the PMC base is mapped, allocates a `clk_device`, reads optional `enable-reg`/`enable-bit` and `divisor-reg`/`divisor-mask` properties, selects the correct operation set based on whether the clock is gated, divided, or both, registers the clock, adds an OF provider, and registers a clkdev lookup. For rate changes, the divisor path computes a ceiling divisor, handles SDMMC's special bit-5 `/64` predivider encoding when the divisor mask is `0x3f`, waits for PMC busy bits before and after writing, and serializes register updates with a global spinlock.

For PLL nodes, `vtwm_pll_clk_init()` maps the register offset from `reg`, assigns the PLL type from the compatible wrapper, registers a PLL clock with one parent, adds an OF provider, and registers clkdev lookup. PLL `determine_rate` and `set_rate` dispatch to type-specific search functions and then encode the chosen multiplier/divisor/filter fields into the memory-mapped register while waiting for PMC busy state.

## State And Persistence
Persistent state is the memory-mapped PMC register contents controlling clock gates, device divisors, and PLL multiplier/divider fields. In-memory state consists of allocated `clk_device` and `clk_pll` structures retained for the life of the system, the global `pmc_base`, and the shared spinlock. There is no remove path because `CLK_OF_DECLARE` clocks are boot-time infrastructure. Register writes are immediately persistent in hardware, guarded by busy polling but not mirrored through regmap or a suspend cache.

## Dependencies And Integration Points
The driver integrates with early device-tree clock initialization, `of_iomap()`, `ioremap()`, CCF `clk_hw_register()`, `of_clk_add_hw_provider()`, and legacy clkdev lookups. It depends on board DTS nodes to provide PMC offsets, parent clocks, optional output names, and compatible strings selecting the correct PLL formula. Consumers use the registered OF clock providers and clkdev aliases.

## Risks
Busy waiting on `pmc_base` can spin forever if hardware never clears `VT8500_PMC_BUSY_MASK`. Some error paths after allocation or missing properties return without freeing already allocated state. PLL search loops are brute force for WM8750/WM8850 and intentionally choose the closest lower-or-equal rate, which can surprise consumers expecting exact rates. In `vtwm_pll_determine_rate()`, failures assign the negative errno into `req->rate` and still return 0, which is an unusual CCF contract. The SDMMC divisor encoding is inferred from mask value `0x3f`, so another clock with the same mask but different semantics would be misdetected. The fallback legacy PMC base can map hardware even without a proper DT PMC node.

## Test Signals
Tests should verify OF-declared clocks register from representative DTS nodes for gated-only, divisor-only, and gated-divisor clocks. Rate tests should cover zero-rate no-ops, divisor rounding, divisor overflow rejection, SDMMC `/64` encoding, and PMC busy wait sequencing. PLL tests should exercise all four compatibles, exact and inexact rate requests, out-of-range rejection, and recalc from known register encodings. Boot logs and `clk_summary` should confirm expected parentage, output names, enable states, and clkdev aliases.
