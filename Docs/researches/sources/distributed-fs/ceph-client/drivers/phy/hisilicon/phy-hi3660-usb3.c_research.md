# sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-hi3660-usb3.c

## Purpose
HiSilicon HI3660 USB3 PHY provider. It programs peripheral CRG, PCTRL, and USB OTG BC syscon registers to bring the USB3/USB2 PHY out of reset, select clocks, fake VBUS valid, and apply an eye diagram parameter.

## Important APIs, types, and functions
- `struct hi3660_priv` stores device, three regmaps, and `eye_diagram_param`.
- `hi3660_phy_init()` disables refclk isolation, enables TCXO, asserts/deasserts resets, enables PHY refs, exits IDDQ, fakes VBUS, and writes `USBOTG3_CTRL4`.
- `hi3660_phy_exit()` asserts PHY POR and disables TCXO.
- Probe obtains `hisilicon,pericrg-syscon`, `hisilicon,pctrl-syscon`, parent `usb3-otg-bc` regmap, optional `hisilicon,eye-diagram-param`, and registers one PHY.

## Control flow
After probe, generic PHY consumers call init/exit. Init is strictly sequential; any regmap failure logs and aborts. Delays are fixed for IDDQ exit, reset deassertion, and VBUS validity.

## State and persistence
Runtime state is only the cached eye parameter and syscon register state. No persistent storage or dynamic power-management state is stored.

## Dependencies and integration points
Uses generic PHY, OF, platform driver, `MFD_SYSCON`, and regmap. Integrates with DT via `hisilicon,hi3660-usb-phy` and syscon phandles.

## Risks and test signals
Risks include parent node assumptions for `syscon_node_to_regmap(dev->parent->of_node)`, incomplete cleanup after partial init failure, and fixed timing margins. Test with missing phandles, default/custom eye parameter, USB enumeration, and repeated init/exit cycles.
