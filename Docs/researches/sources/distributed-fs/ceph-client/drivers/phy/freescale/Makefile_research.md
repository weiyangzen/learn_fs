# sources/distributed-fs/ceph-client/drivers/phy/freescale/Makefile

## Purpose
Maps Freescale/NXP PHY Kconfig symbols to source objects.

## Important rules
For this work item, `CONFIG_PHY_MIXEL_MIPI_DPHY` builds `phy-fsl-imx8-mipi-dphy.o`, and `CONFIG_PHY_FSL_IMX8M_PCIE` builds `phy-fsl-imx8m-pcie.o`.

## Control flow and state
Kbuild includes each object according to its config symbol. There is no runtime state.

## Integration, risks, and test signals
The file integrates the Freescale PHY source files into the kernel PHY build. Risk is limited to symbol or filename drift. Verify object inclusion for `y` and module output for `m`.
