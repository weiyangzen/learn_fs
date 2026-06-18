# sources/distributed-fs/ceph-client/drivers/clk/at91/at91sam9n12.c

Purpose: AT91SAM9N12 PMC clock-tree setup for `"atmel,at91sam9n12-pmc"`. It models a main RC/main crystal mux, PLLA, PLLB-backed USB, master clock, programmable clocks, system clocks, and PCR-based peripherals.

Important APIs and data: `at91sam9n12_pmc_setup()` is the setup entry. It defines master characteristics with `have_div3_pres`, PLLA high-frequency ranges, PLLB 30-100 MHz output, `at91sam9n12_pcr_layout`, system clocks including critical `ddrck`, and the peripheral ID/name table.

Control flow: the function resolves `slow_clk` and `main_xtal`, maps the PMC, allocates arrays sized by `PMC_PLLBCK + 1`, system count, 31 peripherals, and two PCKs. It registers `main_rc_osc`, optional-bypass `main_osc`, SAM9x5-style `mainck`, PLLA plus `plladivck`, PLLB, master pres/div, SAM9N12 USB from `pllbck`, two programmable clocks, system clocks, and PCR peripherals.

State and persistence: `pmc_data` stores exported core, system, peripheral, and programmable handles. The PCR peripheral provider persists per-clock divider/status state and writes PCR on enable/restore. `ddrck` is critical to preserve bootloader DDR enablement.

Dependencies and integration: shares the global `pmc_pcr_lock`; uses `at91sam9x5_master_layout`, legacy PLL registration, SAM9N12 USB ops, and OF provider lookup through `of_clk_hw_pmc_get`.

Risks: the setup assumes PLLB can satisfy USB consumers; missing `clock-names` aborts without diagnostics; no cleanup unregisters earlier clocks after later failure. Test signals include USB clock rate, master clock under `/sys/kernel/debug/clk/clk_summary`, peripheral gates toggling through drivers, and DDR continuing through unused-clock disable.
