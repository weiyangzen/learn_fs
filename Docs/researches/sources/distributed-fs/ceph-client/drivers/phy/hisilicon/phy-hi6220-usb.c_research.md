# sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-hi6220-usb.c

## Purpose
HI6220 USB PHY provider. It controls a peripheral syscon block to reset USB OTG/PICOPHY logic, select host/PHY behavior, fake VBUS, program an eye pattern, and enter SIDDQ on exit.

## Important APIs, types, and functions
- `struct hi6220_priv` stores syscon regmap and device.
- `hi6220_phy_init()` toggles reset enable/disable bits for USBOTG bus, PICOPHY POR, USBOTG, and 32K reset.
- `hi6220_phy_setup()` handles on/off register programming.
- `hi6220_phy_start()` and `hi6220_phy_exit()` wrap setup as PHY ops.

## Control flow
Probe gets `hisilicon,peripheral-syscon`, runs reset initialization once, creates a generic PHY, and registers simple xlate. PHY init enables ACA/res select, fakes VBUS, selects OTG PHY, clears SIDDQ/OGDISABLE, and writes `EYE_PATTERN_PARA`. Exit sets SIDDQ.

## State and persistence
Runtime state is the syscon register values; no persisted data. The driver stores only the regmap pointer.

## Dependencies and integration points
Generic PHY, platform driver, OF, `MFD_SYSCON`, and regmap. Integrated by DT compatible `hisilicon,hi6220-usb-phy`.

## Risks and test signals
Risks include ignoring return values in initial reset helper, sparse rollback, and fixed eye pattern. Test boot probe, init/exit error injection, USB OTG host/device behavior, and register programming against reference manual values.
