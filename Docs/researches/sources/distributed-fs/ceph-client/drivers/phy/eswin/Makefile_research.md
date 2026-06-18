# sources/distributed-fs/ceph-client/drivers/phy/eswin/Makefile

## Purpose
Maps `CONFIG_PHY_EIC7700_SATA` to `phy-eic7700-sata.o`.

## Control flow and state
Kbuild includes the object for built-in or modular configurations. There is no runtime state.

## Integration, risks, and test signals
The file integrates the ESWIN SATA PHY driver into the PHY build. Risk is limited to symbol or filename drift. Verify object inclusion for `CONFIG_PHY_EIC7700_SATA=y` and module output for `m`.
