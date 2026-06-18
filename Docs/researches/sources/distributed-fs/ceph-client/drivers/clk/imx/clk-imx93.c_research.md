# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx93.c

## Purpose
Registers the i.MX93/i.MX91 CCM clock tree. It describes fixed system PLL PFD outputs, fractional GPPLLs, composite root clocks, CCGR gates, shared gates, and A55 CPU clock integration.

## Important APIs, Types, And Functions
`root_array[]` describes root composites with ID, name, offset, selector group, flags, and optional platform mask. `ccgr_array[]` describes gate clocks with parent, offset, flags, optional shared counter, and platform mask. `imx93_clocks_probe()` allocates onecell data, maps ANATOP and CCM, registers fixed/PFD/PLL clocks, iterates both arrays, creates the A55 selector and CPU clock, publishes the provider, and registers UART clocks.

## Control Flow
Probe selects platform mask from match data (`PLAT_IMX93` or `PLAT_IMX91`), initializes external clocks, registers fixed system PFD rates, maps `fsl,imx93-anatop`, creates ARM/audio/video PLLs, maps CCM, then conditionally registers root and CCGR entries whose masks match. Errors unregister the whole clock array.

## State And Persistence Behavior
State includes the `clk_hw` graph, hardware CCM/ANATOP registers, and shared gate counters for SAI, MU-B, PDM, and SPDIF gate pairs. The module parameter `mcore_booted` is declared for compatibility with broader i.MX clock code.

## Dependencies And Integration Points
Depends on `imx93-clock.h`, common clock framework, i.MX composite/gate/GPPLL helpers, OF platform probing, and platform compatibles `fsl,imx93-ccm` and `fsl,imx91-ccm`.

## Risks
Platform masks are important because i.MX91 and i.MX93 share offsets with different clock IDs. Shared CCGR gates must keep counts synchronized. Critical roots for A55/M33/NIC/HSIO/sys counter must not be disabled or low-power paths can fail.

## Test Signals
Boot i.MX93 and i.MX91 DTs, inspect platform-specific clocks, validate A55 CPU clock, UART/I2C/SPI/USDHC/SAI/PDM/SPDIF/media/USB/ENET consumers, and run suspend/resume/CPU idle tests that depend on critical gates.
