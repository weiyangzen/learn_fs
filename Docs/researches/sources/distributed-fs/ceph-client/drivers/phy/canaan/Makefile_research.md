# sources/distributed-fs/ceph-client/drivers/phy/canaan/Makefile

## Purpose
Maps `CONFIG_PHY_CANAAN_USB` to `phy-k230-usb.o`.

## Control flow and state
Kbuild includes the object when the symbol is built-in or modular. There is no runtime state.

## Integration, risks, and test signals
The file integrates the Canaan PHY driver into the kernel PHY build. Risk is limited to symbol or filename drift. Verify object inclusion for `CONFIG_PHY_CANAAN_USB=y` and module output for `m`.
