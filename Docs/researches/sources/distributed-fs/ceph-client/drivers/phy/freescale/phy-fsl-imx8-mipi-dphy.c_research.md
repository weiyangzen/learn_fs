# sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-imx8-mipi-dphy.c

## Purpose
This driver exposes the NXP/Mixel i.MX8 MIPI D-PHY, with LVDS support on i.MX8QXP combo hardware. It converts Generic PHY MIPI D-PHY and LVDS options into PLL dividers, high-speed timing registers, LVDS syscon programming, and SCU firmware controls.

## Important APIs, types, and functions
`struct mixel_dphy_priv` stores current configuration, DPHY/LVDS regmaps, ref clock, device data, SCU IPC handle, slave flag, and alias id. `mixel_dphy_config_from_opts()` validates MIPI rates and computes CM/CN/CO and HS timing fields. `mixel_dphy_configure_mipi_dphy()` writes MIPI timing and PLL registers. `mixel_dphy_configure_lvds_phy()` programs LVDS pads, MODE8, divider, and ref-clock rate. `mixel_dphy_set_mode()`, `mixel_dphy_power_on()`, and `mixel_dphy_power_off()` implement Generic PHY sequencing.

## Control flow
Probe maps the DPHY register region, initializes regmap, gets `phy_ref`, and for combo hardware gets `fsl,syscon`, alias id, and SCU IPC. Consumers set mode, validate options, configure, initialize, and power on. MIPI configure computes and stores timing state, writes calibration/test values, and sets PLL parameters. LVDS configure sets pad state, slave mode, VCO divider, and reference clock rate.

## State and persistence behavior
`priv->cfg` stores the last MIPI timing/PLL configuration. `priv->is_slave` stores LVDS slave role and affects lock polling. Hardware power state is active-low through `DPHY_PD_PLL` and `DPHY_PD_DPHY`; exit clears divider registers. Combo mode can persist in SCU firmware controls.

## Dependencies and integration points
The driver depends on Generic PHY, Generic MIPI D-PHY and LVDS configure options, regmap-mmio, clocks, syscon, and i.MX SCU firmware IPC. Compatible data distinguishes i.MX8MQ MIPI-only from i.MX8QXP combo behavior.

## Risks and test signals
Ratio calculation and boundary rates need testing, and a zero ref clock is not explicitly rejected before ratio calculation. Combo mode depends on correct alias ids and SCU controls. `clk_set_rate()` return is ignored in LVDS configuration. Test MIPI rate boundaries, PLL lock timeouts, LVDS clock limits, master/slave LVDS, SCU failures, mode rejection, and consumer-driven resume behavior.
