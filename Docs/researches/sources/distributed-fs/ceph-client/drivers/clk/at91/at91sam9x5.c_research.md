# sources/distributed-fs/ceph-client/drivers/clk/at91/at91sam9x5.c

Purpose: shared PMC setup for the AT91SAM9x5 family variants (`9g15`, `9g25`, `9g35`, `9x25`, `9x35`). Variant-specific `CLK_OF_DECLARE` wrappers pass extra peripheral tables and LCD clock presence into `at91sam9x5_pmc_setup()`.

Important APIs and data: common tables describe master limits with div3 prescaler, PLLA ranges, the PCR layout, shared system clocks, shared peripherals, and per-variant extras such as MACB, LCDC, CAN, ISI, and USART3. `at91sam9x5_pmc_setup()` is the central builder.

Control flow: setup resolves slow/main parents, maps the PMC, allocates `pmc_data`, registers `main_rc_osc`, bypassable `main_osc`, SAM9x5 `mainck`, PLLA, `plladivck`, UTMI, master pres/div, USB, SMD clock, two programmable clocks, system clocks, optional `lcdck`, shared PCR peripherals, extra variant peripherals, and the OF provider.

State and persistence: `pmc_data` exports core/system/peripheral/PCK handles. Critical `ddrck` keeps DDR enabled. Peripheral dividers are PCR-backed and can auto-divide according to declared range. No variant state is stored after setup beyond registered clocks.

Dependencies and integration: integrates SMD and USB helper providers and uses `pmc_pcr_lock`. The static variant wrappers expose distinct DT compatible strings without duplicating clock construction.

Risks: sentinel-driven `extra_pcks` requires `.id == 0` termination; family variants rely on correct boolean `has_lcdck`; setup failure does not unwind registered clocks. Test signals include each compatible binding producing expected clocks in clk_summary, SMD/USB rates, LCDC availability only on LCD variants, and CAN/MACB clocks only on matching variants.
