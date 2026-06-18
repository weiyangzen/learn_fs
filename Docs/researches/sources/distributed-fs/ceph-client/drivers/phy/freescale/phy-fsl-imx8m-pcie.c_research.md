# sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-imx8m-pcie.c

## Purpose
This driver exposes the i.MX8M PCIe PHY as a Generic PHY for i.MX8MM and i.MX8MP. It configures reference-clock pad mode, AUX and power GPR bits, optional de-emphasis tuning, resets, and PLL readiness.

## Important APIs, types, and functions
`struct imx8_pcie_phy` stores MMIO base, reference clock, PHY handle, IOMUXC GPR regmap, reset controls, DT properties, and variant data. `imx8_pcie_phy_init()` enables the ref clock, `imx8_pcie_phy_power_on()` sequences register programming and reset release, `imx8_pcie_phy_power_off()` asserts resets, and `imx8_pcie_phy_exit()` disables the clock.

## Control flow
Probe reads `fsl,refclk-pad-mode`, optional de-emphasis properties, and `fsl,clkreq-unsupported`, obtains clock `ref`, looks up variant-specific IOMUXC GPR, gets reset `pciephy`, gets `perst` only on i.MX8MP, maps MMIO, creates one PHY, and registers a provider. Power-on asserts reset, applies de-emphasis on i.MX8MM, configures pad input/output/internal PLL, updates GPR AUX/power/SSC/refclk bits, releases resets, asserts common reset through GPR, and polls for `ANA_PLL_DONE`.

## State and persistence behavior
DT-derived pad mode, tuning, and CLKREQ behavior persist in driver state. Hardware state persists in PHY MMIO and IOMUXC GPR registers. Clock enable is paired with init/exit, not power-on/off. On i.MX8MM, PERST is not acquired, so reset helpers must tolerate NULL.

## Dependencies and integration points
The driver depends on Generic PHY, clocks, reset controls, syscon lookup, i.MX IOMUXC GPR definitions, and dt-bindings for i.MX8 PCIe refclk pad modes.

## Risks and test signals
Missing `fsl,refclk-pad-mode` defaults to zero. Several reset-control calls and register writes are not checked. PLL polling compares the full register value to `ANA_PLL_DONE`, which is fragile if other bits are set. Test all pad modes, both variants, de-emphasis settings, CLKREQ unsupported handling, PLL timeout injection, repeated lifecycle cycles, and PCIe enumeration after warm boot.
