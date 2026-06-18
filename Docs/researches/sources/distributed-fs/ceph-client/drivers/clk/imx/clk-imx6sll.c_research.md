# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx6sll.c

## Purpose
`clk-imx6sll.c` is the i.MX6SLL CCM/ANATOP provider. It describes a SoloLite-Lite style clock tree with PLL bypasses, PLL/PFD roots, AXI/AHB/MMDC bus clocks, display and e-paper pixel paths, SSI/SPDIF/external-audio shared gates, USB PHY dummy gates, and common low-speed peripheral gates. It registers the provider with `CLK_OF_DECLARE_DRIVER(imx6sll, "fsl,imx6sll-ccm", ...)`.

## Important APIs, Types, And Functions
The file is mostly declarative clock topology around `static struct clk_hw **hws` and `static struct clk_hw_onecell_data *clk_hw_data`. It uses parent-name arrays for PLL bypasses, bus roots, USDHC, SSI, SPDIF, LDB DI, LCDIF, EPDC, ECSPI, UART, and PERCLK selectors. `imx6sll_clocks_init()` is the only function: it allocates the onecell structure, obtains external fixed clocks (`ckil`, `osc`, `ipp_di0`, `ipp_di1`), maps `fsl,imx6sll-anatop`, clears PLL bypass bits via `xPLL_CLR()`, registers ANATOP clocks, maps CCM, registers CCM muxes/dividers/busy dividers/gates, masks MMDC handshake, publishes the provider, registers UART clocks, and adjusts bus rates.

## Control Flow
Initialization first disables PLL bypass by writing clear registers for PLL1/2/3/4/5/6/7. PLL constructors in this file use bypass-source parents for PLL inputs, then separate bypass muxes and post gates/fixed factors expose usable roots. Optional USB PHY gates are only created and marked critical when `CONFIG_USB_MXS_PHY` is enabled. After PFD and post-divider setup, CCM muxes define bus and peripheral parent choices, then dividers and busy dividers derive per-domain rates. CCGR sections create gates for AIPSTZ, DCP, UARTs, GPIOs, ECSPI, timers, I2C, OCOTP, CSI, LCDIF, PXP, EPDC, watchdogs, MMDC, OCRAM, ROM, SDMA, SPBA, audio, and USDHC. Final policy lowers AHB to 99 MHz, switches PERIPH through a safe intermediate path to PLL2 bus, then raises AHB to 132 MHz.

## State And Persistence
State lives in the allocated provider table, shared gate counters for audio/SSI groups, and live ANATOP/CCM registers. There is no external persistence. Critical gates for memory, OCRAM, ROM, AIPS, and MMDC IPG/fast paths prevent essential infrastructure from being disabled by unused-clock cleanup.

## Dependencies And Integration Points
The driver depends on `dt-bindings/clock/imx6sll-clock.h`, standard CCF and i.MX-specific helpers, OF fixed-clock names, `imx_mmdc_mask_handshake()`, and UART clock registration. It feeds consumers for LCDIF, EPDC, LDB DI, PXP, CSI, USDHC, ECSPI, UART, I2C, GPIO, timers, watchdogs, SPBA, SSI/SPDIF/external audio, USB, and memory infrastructure.

## Risks
The PLL bypass clear sequence is hardware-sensitive and differs from drivers that use `clk_set_parent()` for bypass muxes. Several gates share one CCGR bit and depend on shared counters, so incorrect grouping can under- or over-gate audio clocks. `IMX6SLL_CLK_LDB_DI1_DIV_SEL` appears to use the same bit offset as DI0 in this source; if not intentional, display clock selection would be suspect. As with other i.MX drivers, `WARN_ON(!base)` does not abort after failed MMIO mapping.

## Test Signals
Expected test signals are clean provider registration, no missing-clock warnings, AHB settling at 132 MHz after the safe parent transition, working LCDIF and EPDC pixel clocks including LDB-derived alternatives, stable USDHC/UART/I2C/ECSPI operation, USB PHY clocks when enabled, and audio paths proving shared SSI/SPDIF/external-audio gates do not disable each other.
