# sources/distributed-fs/ceph-client/drivers/phy/lantiq/Makefile

## Purpose
Kbuild mapping for Lantiq PHY drivers.

## Important APIs, types, and functions
Maps `CONFIG_PHY_LANTIQ_RCU_USB2` to `phy-lantiq-rcu-usb2.o` and `CONFIG_PHY_LANTIQ_VRX200_PCIE` to `phy-lantiq-vrx200-pcie.o`.

## Control flow
Kbuild compiles objects according to config symbols.

## State and persistence
No runtime state; build state only.

## Dependencies and integration points
Tied to adjacent Kconfig and source filenames.

## Risks and test signals
Risk is stale mapping. Test both symbols enabled as modules/built-in.
