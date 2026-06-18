# sources/distributed-fs/ceph-client/drivers/clk/at91/sama5d2.c

Purpose: SAMA5D2 PMC setup for main/PLL/master clocks, audio PLLs, UTMI trim, H32MX, USB, programmable clocks, system clocks, two classes of peripherals, generated clocks, and optional I2S mux outputs.

Important APIs and data: `sama5d2_pmc_setup()` is selected by `"atmel,sama5d2-pmc"`. Static tables define master limits, PLLA range, PCR layout, system clocks, normal and H32MX-parented peripherals, generated clocks with audio PLL changeable parent IDs, and direct programmable layout.

Control flow: setup resolves slow/main parents, maps PMC, allocates `pmc_data`, registers RC/main/mainck, PLLA and `plladivck`, audio FRAC/PAD/PMC outputs, optional SFR regmap, UTMI, master pres/div, H32MX, USB, three programmable clocks, system clocks, normal peripherals, 32-bit peripherals parented by H32MX, generated clocks, optional I2S mux clocks via SFR, and provider.

State and persistence: `ddrck` and `mpddr_clk` are critical. SFR regmap is optional for I2S mux but used by UTMI trim when present. Provider-level PM state covers main/master/peripheral/generated/USB/UTMI clocks; audio PLL lacks explicit save/restore.

Dependencies and integration: pulls together most providers in this subset. Generated clocks for I2S and ClassD can change parent audio PLL rate through `chg_pid = 5`, matching the sixth parent `"audiopll_pmcck"`.

Risks: without SFR, I2S mux clocks are skipped and UTMI supports only trims not requiring SFR; periph32 ranges rely on H32MX cap; audio PLL sharing can lock rates around first enabled consumer. Test signals include audio clocks, I2S mux availability, UTMI trim behavior at non-12 MHz main clocks, H32MX below 90 MHz, and GCK range enforcement.
