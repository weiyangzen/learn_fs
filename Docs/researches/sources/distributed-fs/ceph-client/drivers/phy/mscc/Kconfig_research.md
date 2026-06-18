# sources/distributed-fs/ceph-client/drivers/phy/mscc/Kconfig

Purpose: This Kconfig fragment exposes the Microsemi/Microchip Ocelot SerDes PHY driver.

Important APIs/types/functions: It defines tristate symbol `PHY_OCELOT_SERDES`, selects `GENERIC_PHY`, and depends on `OF` and `MFD_SYSCON`. The help text identifies support for SerDes muxing on Microsemi Ocelot.

Control flow: Kernel configuration resolves whether the Ocelot SerDes provider can be compiled. When enabled, the directory Makefile builds `phy-ocelot-serdes.o`.

State and persistence: The file has no runtime state. Its persistent effect is through `.config`, which controls object inclusion and module availability.

Dependencies and integration points: The dependencies reflect the driver design: OF is used for provider/consumer phandles, and syscon/regmap access is used to program the shared HSIO block.

Risks: Missing dependency updates can cause compile/link errors if the source driver adds subsystem calls. Overly broad dependencies may allow building for platforms where required `soc/mscc/ocelot_hsio.h` support is not meaningful, though `COMPILE_TEST` is not explicitly advertised here.

Test signals: Config builds should show `CONFIG_PHY_OCELOT_SERDES` compiling cleanly as built-in and module. Runtime binding requires a device-tree node compatible with `mscc,vsc7514-serdes`.
