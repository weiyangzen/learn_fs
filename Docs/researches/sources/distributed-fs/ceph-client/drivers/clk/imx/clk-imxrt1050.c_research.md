# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imxrt1050.c

## Purpose
Registers the i.MX RT1050 CCM/ANATOP clock tree, including PLLs, PFD outputs, bypass muxes, system bus dividers, peripheral muxes, and a small set of peripheral gates.

## Important APIs, Types, And Functions
`imxrt1050_clocks_probe()` is the single platform probe. It fills a `clk_hw_onecell_data` indexed by `imxrt1050-clock.h`. It uses `imx_clk_hw_pllv3()`, `imx_clk_hw_pfd()`, mux/divider/gate helpers, fixed-factor helpers, and `of_clk_add_hw_provider()`.

## Control Flow
Probe allocates the clock array, obtains the oscillator, maps `fsl,imxrt-anatop`, registers PLL reference muxes, PLLv3 instances, bypass muxes, video dividers, PLL3 fixed 80 MHz, PLL2/PLL3 PFDs, then maps CCM and registers core/bus/peripheral selectors and gates. Failure unregisters all created clocks.

## State And Persistence Behavior
State is the ANATOP/CCM register contents and the provider's `clk_hw` array. There is no suspend state in this file. The driver is devm-backed except for clock unregister cleanup on probe errors.

## Dependencies And Integration Points
Depends on `imxrt1050-clock.h`, OF compatible `fsl,imxrt1050-ccm`, ANATOP compatible `fsl,imxrt-anatop`, and common i.MX PLL/PFD helpers. Consumers include USDHC, LPUART, LCDIF, DMA, DMAMUX, SEMC, AHB/IPG/peripheral bus users.

## Risks
Some parent entries are placeholders such as `"todo"` or dummy inputs, so DT/rate changes need caution. PLL/PFD register offsets must match RT1050 ANATOP, which differs from larger i.MX8 SoCs. Missing critical flags on SEMC/bus paths could destabilize memory access.

## Test Signals
Boot RT1050, verify clock provider registration, UART console, USDHC, LCDIF pixel path, DMA/DMAMUX, SEMC/bus rates, PFD rates in `clk_summary`, and assigned-clock rate changes.
