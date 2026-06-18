# sources/distributed-fs/ceph-client/drivers/clk/at91/sam9x60.c

Purpose: monolithic PMC setup for Microchip SAM9X60 using newer fractional/divider PLL providers, PCR peripherals, generated clocks, USB clock, programmable clocks, and master clock limits.

Important APIs and data: `sam9x60_pmc_setup()` is selected by `"microchip,sam9x60-pmc"`. Static data defines PLLA/UPLL characteristics and layouts, master layout at offset `0x28`, direct programmable layout, PCR layout at `0x88`, system clocks, peripheral clocks, and GCK tables with max-rate ranges.

Control flow: setup resolves `td_slck`, `md_slck`, and `main_xtal`, maps the PMC, allocates `pmc_data`, registers RC/main oscillators, main mux, PLLA frac/div as critical CPU clocks, UPLL frac/div as UTMI core, master pres/div, USB clock with three parents, two programmable clocks, system clocks, PCR peripherals, generated clocks, and the provider.

State and persistence: critical PLLA/div and DDR/MPDDR-related clocks prevent disabling CPU and memory domains. Fractional/divider PLL providers cache programming and restore active state; PCR generated/peripheral providers cache enable and divider state.

Dependencies and integration: depends on `clk-sam9x60-pll.c`, `clk-generated.c`, `clk-peripheral.c`, `clk-usb.c`, and `pmc_pcr_lock`. The setup is early because some clocks are clocksource dependencies.

Risks: parent arrays are reused across programmable and generated setup; all GCKs use linear parent IDs without mux table, so layout masks must match hardware encoding. Test signals include CPU/master rate, UPLL-derived USB clock, GCK max-rate enforcement for SDMMC/LCD/I2S/ClassD, and critical clocks surviving unused-clock cleanup.
