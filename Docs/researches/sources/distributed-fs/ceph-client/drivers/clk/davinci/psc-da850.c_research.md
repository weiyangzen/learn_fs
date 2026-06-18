# sources/distributed-fs/ceph-client/drivers/clk/davinci/psc-da850.c

Purpose: supplies DA850 PSC0/PSC1 LPSC clock tables, clkdev aliases, parent-clock dependencies, and init data for the generic DaVinci PSC driver.

Important APIs/types/functions: `da850_psc0_info` and `da850_psc1_info` define LPSC module IDs, power domains, names, parents, clkdev aliases, and flags. `LPSC_CLKDEV*()` arrays map legacy consumers such as MMC, UART, USB, EMAC, LCDC, SATA, GPIO, and DSP. Exports `da850_psc0_init_data`, `da850_psc1_init_data`, `of_da850_psc0_init_data`, and `of_da850_psc1_init_data`.

Control flow: PSC0 init registers 16 possible module slots; PSC1 init registers 32. Platform paths call `davinci_psc_register_clocks()` to also install clkdev aliases. OF paths call `of_davinci_psc_clk_init()` to publish onecell clock and genpd providers.

State and persistence: the file has static descriptor state only. Hardware enable/reset state is managed by `psc.c` based on these descriptors.

Dependencies and integration points: depends on PLL names (`pll0_sysclk*`), CFGCHIP async clocks (`async1`, `async3`), legacy platform device names, and PSC generic structures in `psc.h`.

Risks: missing or wrong parent clocks cause PSC probe deferral/failure. `LPSC_ALWAYS_ENABLED` is critical for DMA, interrupt controller, ARM, DDR, and transfer controller clocks; misclassification could break boot or suspend. Sparse module IDs require the `num_clks` bounds to exceed the highest LPSC ID.

Test signals: DA850 boot should show all always-enabled clocks on, legacy clkdev consumers should resolve, DT consumers should acquire clocks by onecell index, and DSP local reset should work for the `LPSC_LOCAL_RESET` entry.
