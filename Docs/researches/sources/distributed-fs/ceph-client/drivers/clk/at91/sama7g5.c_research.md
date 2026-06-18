<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/sama7g5.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/sama7g5.c

Purpose: This file provides the early PMC clock-tree definition for Microchip SAMA7G5. It registers the SoC's main clock, fractional/divider PLLs, MCK0-MCK4, UTMI, programmable clocks, system clocks, peripheral clocks, and generated clocks.

Important APIs, types, and functions: The entry point is `sama7g5_pmc_setup()`, registered by `CLK_OF_DECLARE(..., "microchip,sama7g5-pmc", ...)`. The file defines PLL ID/component/type enums, fractional and divider PLL layouts, PLL characteristics, `sama7g5_plls[][]`, `sama7g5_mckx[]`, `sama7g5_systemck[]`, `sama7g5_periphck[]`, `sama7g5_gck[]`, and register-layout metadata for MCK0, programmable clocks, and PCR. It delegates clock implementations to AT91/SAM9x60 helpers including `sam9x60_clk_register_frac_pll()`, `sam9x60_clk_register_div_pll()`, `at91_clk_register_master_div()`, `at91_clk_sama7g5_register_master()`, `at91_clk_sama7g5_register_utmi()`, `at91_clk_register_programmable()`, `at91_clk_register_system()`, `at91_clk_register_sam9x5_peripheral()`, and `at91_clk_register_generated()`.

Control flow: Setup resolves the three required external parents (`td_slck`, `md_slck`, `main_xtal`), obtains the PMC regmap, allocates `pmc_data`, registers the main RC oscillator, main oscillator, and main clock, then walks the PLL descriptor matrix to register each fractional PLL and its divider outputs. It creates CPU `mck0`, then builds and registers MCK1-MCK4 from slow/main and PLL parents. It registers UTMI, eight programmable clocks, system clocks backed by programmable clock hardware, peripheral clocks tied to MCK parents, and generated clocks with dynamically allocated mux tables.

State and persistence behavior: Registered hardware pointers are stored both in static descriptor entries and in `pmc_data` arrays. Hardware persists in PMC register state; temporary mux tables must remain allocated after registration and are only freed on error. Locks split register serialization by PLL, MCK0, MCKx, and PCR domains. Critical clock flags protect CPU, DDR, system, and other always-on paths.

Dependencies and integration points: The file depends on the common AT91 PMC implementation, syscon regmap, DT parent clocks, and `dt-bindings/clock/at91.h`. Consumers include camera, Ethernet, SDMMC, audio, CAN, timer, QSPI, PWM, USB, and generated-clock users in board DTs.

Risks and test signals: Risks include wrong generated-clock parent mux values, missing parent hardware before registration, memory lifetime mistakes in dynamic mux tables, and rate-change side effects on shared PLLs. Tests should cover early boot, timer stability, `clk_summary` inspection, peripheral probe success, generated-clock rate requests, and any CPU/DDR-related frequency changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/sama7g5.c -->
