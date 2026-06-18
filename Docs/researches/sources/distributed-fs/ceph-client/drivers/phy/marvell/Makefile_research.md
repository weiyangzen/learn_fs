# sources/distributed-fs/ceph-client/drivers/phy/marvell/Makefile

## Purpose
Kbuild object mapping for Marvell PHY drivers.

## Important APIs, types, and functions
Relevant mappings are `CONFIG_ARMADA375_USBCLUSTER_PHY += phy-armada375-usb2.o` and `CONFIG_PHY_MVEBU_A38X_COMPHY += phy-armada38x-comphy.o`, alongside other Marvell PHY objects.

## Control flow
Kbuild includes each object according to config state.

## State and persistence
No runtime state; build state only.

## Dependencies and integration points
Relies on adjacent Marvell Kconfig symbols and source filenames.

## Risks and test signals
Risk is symbol/object drift. Test enabled builds for Armada375 and Armada38x symbols.
