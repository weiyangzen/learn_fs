# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx6ul.c

## Purpose
`clk-imx6ul.c` registers the i.MX6UL and i.MX6ULL clock tree. It covers ANATOP PLL/PFD roots, CA7 step clocking, bus clocks, USDHC, NAND/GPMI/BCH/ENFC, LCDIF/SIM or EPDC, SAI/SPDIF/ESAI audio, dual ENET references selected through IOMUXC GPR, QSPI, CAN, UART, and low-speed peripheral gates. One `fsl,imx6ul-ccm` OF declaration serves both UL and ULL, with runtime compatibility checks for variant-only blocks.

## Important APIs, Types, And Functions
Provider state is `hws` plus `clk_hw_data`. `clk_on_imx6ul()` and `clk_on_imx6ull()` branch registration for SIM/CAAM versus EPDC/ESAI/DCP/AIPSTZ3 differences. Parent arrays define PLL bypasses, CA7 secondary/step, AXI, PERIPH/PERIPH2, USDHC, BCH/GPMI, EIM, SPDIF, SAI, LCDIF/SIM/EPDC, LDB, QSPI, ENFC, CAN, ECSPI, UART, PERCLK, CSI, and CLKO muxes. ENET reference selection is implemented with `imx_clk_gpr_mux()` using `IMX6UL_GPR1_ENET*_` bit tables and optional pad fixed clocks from OF.

## Control Flow
`imx6ul_clocks_init()` allocates the onecell table, obtains fixed and external display clocks, maps `fsl,imx6ul-anatop`, registers PLL bypass sources, PLLs, bypass muxes, roots, USB PHY dummy gates, PFDs, ENET reference dividers/gates, post dividers, and fixed factors. It maps CCM and registers variant-aware selectors: SIM muxes for i.MX6UL or EPDC/ESAI muxes for i.MX6ULL. It then registers dividers, busy bus dividers, and CCGR gates, with conditional CAAM versus DCP/ENET placement and EPDC versus ENET/SIM gates. After masking MMDC handshake, it registers ENET GPR muxes, validates the table, publishes the provider, performs a safe AHB/PERIPH parent transition to get AXI to 264 MHz while keeping AHB within 133 MHz, sets ENET/CSI rates, enables AIPSTZ3 on ULL and USB PHY gates when needed, assigns CAN/SIM or EPDC/ENFC parents, selects internal ENET references, and registers UART clocks.

## State And Persistence
State is limited to the allocated provider table, shared gate refcounts for ASRC/audio/SAI/ESAI groups, and live ANATOP/CCM/IOMUXC-GPR register state. No filesystem persistence exists. Critical clock flags keep AIPS, MMDC, AXI, and ROM infrastructure alive. Variant branches leave some IDs meaningful only on the compatible SoC.

## Dependencies And Integration Points
The driver depends on `dt-bindings/clock/imx6ul-clock.h`, CCF, OF fixed clocks, `imx_mmdc_mask_handshake()`, `imx_clk_gpr_mux()`, IOMUXC GPR definitions from `imx6q-iomuxc-gpr.h`, optional USB PHY support, and UART registration. Primary consumers are ENET MACs/PTP, LCDIF, EPDC on ULL, SIM on UL, GPMI NAND, USDHC, SAI/SPDIF/ESAI audio, CAN, QSPI, UART, ECSPI, I2C, PWM, ADC, timers, watchdogs, and security/DMA blocks.

## Risks
Variant branching is a major risk: a clock ID registered only for UL or ULL must not be used by the other DT. ENET reference selection crosses CCM and IOMUXC GPR state, so wrong table masks can drive pads incorrectly. The safe AHB transition is required because AHB must stay at or below 133 MHz; reordering those parent/rate writes can overclock the bus. Some gates intentionally share register bits for serial/ipg pairs; incorrect use of non-shared gates would break refcounting.

## Test Signals
Expected signals are no missing-clock warnings for the active compatible, AXI at the intended 264 MHz path with AHB restored to 132 MHz, PERCLK sourced from OSC, ENET1/2 references at 50 MHz and selected through GPR muxes, CSI at 24 MHz, working CAN from PLL3 80 MHz, SIM clocks on UL or EPDC/ESAI clocks on ULL, NAND/GPMI operation, USB PHY dummy gate enablement when configured, and stable UART console registration.
