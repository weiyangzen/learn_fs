<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/sama5d4.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/sama5d4.c

Purpose: This file initializes the SAMA5D4 PMC clock tree at early boot. It is similar to SAMA5D3 but adds an `h32mxck` branch for 32-bit peripheral clocks and splits peripherals into those clocked from `masterck_div` and those clocked from `h32mxck`.

Important APIs, types, and functions: `sama5d4_pmc_setup()` is the only functional entry point and is registered with `CLK_OF_DECLARE(..., "atmel,sama5d4-pmc", ...)`. Static data includes `mck_characteristics`, `plla_characteristics`, `sama5d4_pcr_layout`, `sama5d4_systemck[]`, `sama5d4_periph32ck[]`, and `sama5d4_periphck[]`. The code uses AT91 common helpers such as `at91_clk_register_main_rc_osc()`, `at91_clk_register_main_osc()`, `at91_clk_register_sam9x5_main()`, `at91_clk_register_pll()`, `at91_clk_register_plldiv()`, `at91_clk_register_utmi()`, `at91_clk_register_master_pres()`, `at91_clk_register_master_div()`, `at91_clk_register_h32mx()`, `at91sam9x5_clk_register_usb()`, `at91sam9x5_clk_register_smd()`, `at91_clk_register_programmable()`, `at91_clk_register_system()`, and `at91_clk_register_sam9x5_peripheral()`.

Control flow: The setup requires `slow_clk` and `main_xtal`, maps the PMC regmap, allocates `pmc_data`, registers main oscillators and PLLA, creates the master clock, derives `h32mxck`, registers USB/SMD and three programmable clocks, then iterates through system, normal peripheral, and 32-bit peripheral tables. Failures free `pmc_data` and abort before provider registration.

State and persistence behavior: Clock hardware state is represented by registered `clk_hw` objects stored in the `pmc_data` export arrays. Register state persists in the PMC and PCR registers. `mck_lock` protects master-clock updates and `pmc_pcr_lock` protects PCR programming. `ddrck` and `mpddr_clk` are critical to keep bootloader-enabled DDR clocks active.

Dependencies and integration points: The file depends on syscon regmap conversion of the PMC node, AT91 shared PMC implementations in `pmc.h`, and the AT91 clock binding IDs. It exports clocks through `of_clk_hw_pmc_get()` for DT consumers.

Risks and test signals: The key risks are wrong split between `masterck_div` and `h32mxck` peripherals, incorrect IDs in the static tables, and PLL/master limits that do not match silicon. Boot tests should verify DDR stability, early console, USB, MMC, timer operation, and that `clk_summary` shows expected parents for the 32-bit peripheral set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/sama5d4.c -->
