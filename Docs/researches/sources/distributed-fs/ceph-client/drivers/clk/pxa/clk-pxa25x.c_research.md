# sources/distributed-fs/ceph-client/drivers/clk/pxa/clk-pxa25x.c

Purpose: Implements PXA25x clock topology, frequency reporting, CKEN peripheral clocks, PLL/core clocks, dummy legacy aliases, and DT early provider registration.

Important APIs, types, and functions: `pxa25x_get_clk_frequency_khz()` reports core/run/CPLL/memory rates. `clk_pxa25x_memory_get_rate()`, `clk_pxa25x_run_get_rate()`, `clk_pxa25x_cpll_get_rate()`, and `clk_pxa25x_core_get_parent()` decode CCCR/CLKCFG state. `clk_pxa25x_cpll_set_rate()` applies supported `pxa25x_freqs` entries through `pxa2xx_cpll_change()`. `pxa25x_clocks_init()` registers base, dummy, and CKEN clocks.

Control flow: Init stores the clock register base, registers fixed oscillators and peripheral PLL fixed factors, registers CPLL/run/core/memory clocks, registers dummy clkdev aliases for legacy devices, then registers CKEN gates. DT init ioremaps the fixed clock register address and publishes the common one-cell provider.

State and persistence: Static `clk_regs` holds MMIO base. CPLL and core state persists in CCCR/CLKCFG; memory refresh state is in SMEMC MDREFR. CKEN gate bits persist in CKEN.

Dependencies and integration points: Depends on PXA common helpers, PXA SMEMC row-count helpers, `clk-pxa2xx.h` register definitions, legacy clkdev device IDs, and DT binding IDs.

Risks: Only four frequency table entries are supported. `clk_pxa25x_memory_get_rate()` divides by M multiplier from CCCR; invalid encodings could divide by zero. DT init uses a hard-coded physical register address. Dummy clocks preserve legacy API behavior but can mask missing real pin clock control.

Test signals: `pxa25x_get_clk_frequency_khz(1)` should print expected run/turbo/memory rates. Test CPLL changes across supported table entries and validate MDREFR DRI updates. CKEN bits should match peripherals such as MMC, I2C, UARTs, USB, SSP, LCD, and MEMC.
