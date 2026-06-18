# sources/distributed-fs/ceph-client/drivers/phy/socionext/phy-uniphier-usb2.c

Purpose: UniPhier USB2 PHY provider for USB2 controller-integrated PHYs, with child-node-per-port PHY creation and syscon register programming.

Important APIs, types, and functions: `struct uniphier_u2phy_soc_data` contains two register/value pairs per port. `uniphier_u2phy_init()` writes port configuration registers. `uniphier_u2phy_power_on/off()` manage optional VBUS. `uniphier_u2phy_xlate()` matches a consumer phandle node to a linked-list PHY instance.

Control flow: probe reads SoC data table, counts sentinel-terminated entries, obtains parent syscon regmap, iterates child nodes, allocates a `priv`, obtains optional `vbus`, creates a PHY bound to the child node, reads the child `reg` as data index, links instances, and registers custom xlate. Init writes `config0` and `config1` when data is present; power only toggles VBUS.

State and persistence: each child PHY has its own `priv`, optional data pointer, optional VBUS, and `next` pointer. Hardware state persists in parent syscon USBPHY control/PLL registers.

Dependencies and integration points: generic PHY, syscon parent node, child DT nodes with `reg`, optional regulator, Pro4 and LD11 compatible data tables.

Risks: `dev_set_drvdata(dev, priv)` stores the last allocated `priv`, but the linked list head is `next`; because `priv` remains the most recent node this works, but a no-child DT leaves null provider state. Optional VBUS is fetched from the parent device rather than child, so per-port supplies are not modeled. Out-of-range `reg` only warns and leaves the PHY unconfigured.

Test signals: DT with multiple child PHYs, phandle resolution by child node, VBUS enable/disable observation, syscon register write validation for Pro4/LD11, and warning coverage for invalid `reg` values.
