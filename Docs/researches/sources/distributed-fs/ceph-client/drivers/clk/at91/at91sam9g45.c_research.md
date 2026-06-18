# sources/distributed-fs/ceph-client/drivers/clk/at91/at91sam9g45.c

Purpose: early common-clock setup for the AT91SAM9G45 PMC, selected by `CLK_OF_DECLARE(..., "atmel,at91sam9g45-pmc", ...)`. It builds the SoC clock tree and publishes it through `of_clk_add_hw_provider(np, of_clk_hw_pmc_get, at91sam9g45_pmc)`.

Important APIs and data: `at91sam9g45_pmc_setup()` is the only entry point. Static tables describe master-clock limits/divisors, PLLA output windows plus `out`/`icpll` programming, system clocks such as critical `ddrck`, and peripheral IDs. It uses provider helpers from `pmc.h`: main oscillator, RM9200 main clock, legacy PLL, PLLA divider, UTMI, master pres/div, USB, programmable, system, and basic peripheral clocks.

Control flow: it resolves `slow_clk` and `main_xtal`, maps the PMC regmap, allocates `pmc_data`, honors `atmel,osc-bypass`, registers the core clocks in dependency order, fills `chws`, `pchws`, `shws`, and `phws`, then registers the provider. Any registration failure jumps to `err_free`.

State and persistence: persistent state is the allocated `pmc_data` arrays and registered `clk_hw` objects. Runtime hardware state is owned by helper providers through PMC registers. `ddrck` is marked `CLK_IS_CRITICAL` because DDR is bootloader-enabled and must not be disabled by unused-clock cleanup.

Dependencies and integration: depends on DT `clock-names`, `dt-bindings/clock/at91.h`, syscon/regmap, and AT91 common-clock helpers. The TCB clocksource note explains why this is an early OF declaration rather than a platform driver.

Risks: missing parent names silently abort setup; failed mid-tree registration leaks already registered clocks because only `pmc_data` is freed; incorrect PLL ranges or peripheral IDs can over/under-clock hardware. Test signals include boot logs for invalid `clk_get`, `/sys/kernel/debug/clk/clk_summary`, USB/UTMI enumeration, DDR stability, and timer availability during early boot.
