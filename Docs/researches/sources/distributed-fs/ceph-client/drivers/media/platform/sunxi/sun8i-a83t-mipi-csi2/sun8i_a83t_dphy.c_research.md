# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/sun8i_a83t_dphy.c

Purpose: registers and implements the integrated A83T MIPI D-PHY as a generic PHY provider backed by the CSI-2 controller's regmap.

Important APIs and functions: exported internal function is `sun8i_a83t_dphy_register`. PHY ops are `sun8i_a83t_dphy_configure`, `sun8i_a83t_dphy_power_on`, and `sun8i_a83t_dphy_power_off`.

Control flow: registration creates a devm-managed PHY, stores the CSI-2 device as PHY drvdata, and registers a simple OF PHY provider. Configure validates MIPI D-PHY options. Power-on writes reset/shutdown bits in the D-PHY control register and analog resistor/sink settings. Power-off clears the D-PHY control register.

State and persistence: the PHY object is devm-managed and tied to the controller device. Hardware state is limited to D-PHY control and analog registers and is changed on PHY power transitions.

Dependencies and integration points: depends on generic PHY APIs, MIPI D-PHY validation helpers, and shared regmap/register definitions from the A83T CSI-2 driver. It is consumed by the controller stream path through `csi2_dev->dphy`.

Risks: configure only validates generic timing and does not program timing-specific registers; power-on uses fixed analog values. The power-off function clears control but leaves analog register state untouched. There is no explicit reset op.

Test signals: PHY provider lookup by device tree, `phy_configure` validation with sensor pixel-rate-derived timings, power-on/off register traces, and stream bring-up on A83T hardware.
