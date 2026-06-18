# sources/distributed-fs/ceph-client/drivers/phy/mscc/Makefile

Purpose: This Makefile connects the Ocelot SerDes Kconfig symbol to its single driver object.

Important APIs/types/functions: It contains `obj-$(CONFIG_PHY_OCELOT_SERDES) := phy-ocelot-serdes.o`.

Control flow: Kbuild includes or modularizes `phy-ocelot-serdes.o` according to `CONFIG_PHY_OCELOT_SERDES`.

State and persistence: There is no runtime state. The only persistent input is the kernel configuration.

Dependencies and integration points: It integrates with the `drivers/phy/mscc` directory and the Kconfig symbol of the same directory. The `:=` assignment is sufficient because the symbol maps to one object.

Risks: Object renames or additional companion objects require updating this file. A stale Makefile would produce config symbols that appear enabled but do not build the intended driver.

Test signals: `make drivers/phy/mscc/` or a full kernel build with `CONFIG_PHY_OCELOT_SERDES=m/y` should produce the expected module/object.
