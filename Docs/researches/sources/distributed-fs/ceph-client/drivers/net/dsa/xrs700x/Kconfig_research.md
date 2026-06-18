# sources/distributed-fs/ceph-client/drivers/net/dsa/xrs700x/Kconfig

Purpose: this Kconfig fragment declares build options for Arrow SpeedChips XRS7003/XRS7004 DSA support and its transport frontends.

Important APIs, types, and functions: `NET_DSA_XRS700X` is the hidden core tristate selected by transport drivers; it depends on `NET_DSA`, selects `NET_DSA_TAG_XRS700X`, and selects `REGMAP`. `NET_DSA_XRS700X_I2C` is the user-visible I2C transport option, depends on `NET_DSA && I2C`, selects the core, and selects `REGMAP_I2C`. `NET_DSA_XRS700X_MDIO` is the user-visible MDIO transport option, depends on `NET_DSA`, and selects the core.

Control flow: users choose a transport; Kconfig pulls in the shared core and the required tagging/regmap infrastructure. The Makefile then builds `xrs700x.o` for the core and the selected transport object.

State and persistence: Kconfig persists only build-time selection state. Runtime state is in the C files.

Dependencies and integration points: this integrates the driver with DSA, the XRS700x tagger, regmap, I2C, and the MDIO frontend listed in the Makefile but outside this work item.

Risks: the core symbol is not user-selectable, so missing transport selection yields no driver. MDIO does not explicitly select a named regmap bus helper here, so its source must provide or depend on the needed regmap support. Incorrect selects can produce link failures or a DSA driver without its tag protocol.

Test signals: `olddefconfig`/`menuconfig` coverage for I2C-only, MDIO-only, both transports, and disabled DSA; module dependency checks showing the tagger and regmap objects are built; and runtime probe with each selected transport.
