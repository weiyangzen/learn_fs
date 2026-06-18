# sources/distributed-fs/ceph-client/drivers/clk/at91/at91sam9rl.c

Purpose: early PMC setup for AT91SAM9RL via `"atmel,at91sam9rl-pmc"`. It is a smaller legacy tree with main clock, PLLA, UTMI, master clock, two programmable clocks, two system PCKs, and basic peripheral gates.

Important APIs and data: `at91sam9rl_pmc_setup()` consumes static `sam9rl_mck_characteristics`, two PLLA output bands, `at91sam9rl_systemck`, and `at91sam9rl_periphck`. It registers clocks through the common helpers declared in `pmc.h`.

Control flow: setup fetches `slow_clk` and `main_xtal`, maps the PMC regmap, allocates `pmc_data`, registers an RM9200-style `mainck` directly from the crystal parent, PLLA, UTMI, master pres/div using `at91rm9200_master_layout`, two programmable clocks, system PCK gates, peripheral gates, and the OF provider.

State and persistence: persistent kernel state is only the clock graph and `pmc_data`. Hardware persistence and suspend context are handled by provider ops such as master, PLL, UTMI, programmable, and system where available. There is no local backup state in this file.

Dependencies and integration: depends on legacy AT91 PMC register layout, `at91rm9200_programmable_layout`, `at91_clk_register_peripheral()`, and the global clock provider contract using two phandle arguments.

Risks: PLLA range selection is narrow and table-driven; wrong DT parents can yield impossible master/UTMI rates. Registration failure frees only `pmc_data`. Test signals: PCK0/PCK1 readiness, USB/UTMI lock, peripheral driver clock enables, and clocksource operation if timer peripherals depend on the registered gates.
