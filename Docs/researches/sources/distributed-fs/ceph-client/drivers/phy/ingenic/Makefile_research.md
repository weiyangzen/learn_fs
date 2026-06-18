# sources/distributed-fs/ceph-client/drivers/phy/ingenic/Makefile

## Purpose
Kbuild mapping for the Ingenic USB PHY driver.

## Important APIs, types, and functions
Maps `CONFIG_PHY_INGENIC_USB` to `phy-ingenic-usb.o`.

## Control flow
Kbuild compiles the object when the config is enabled.

## State and persistence
No runtime state; build state only.

## Dependencies and integration points
Depends on adjacent Kconfig symbol and source filename.

## Risks and test signals
Risk is object-symbol mismatch. Test with `CONFIG_PHY_INGENIC_USB=m/y`.
