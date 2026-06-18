# sources/distributed-fs/ceph-client/drivers/net/ieee802154/Kconfig

Purpose: Defines the kernel configuration menu for IEEE 802.15.4 low-rate wireless personal area network drivers. It groups fake, SPI, USB, and simulator transceiver drivers under `IEEE802154_DRIVERS` and encodes their bus and stack dependencies.

Important APIs, types, and symbols: `menuconfig IEEE802154_DRIVERS` depends on `NETDEVICES && IEEE802154` and defaults to `y` while adding no code by itself. Driver symbols include `IEEE802154_FAKELB`, `IEEE802154_AT86RF230`, `IEEE802154_MRF24J40`, `IEEE802154_CC2520`, `IEEE802154_ATUSB`, `IEEE802154_ADF7242`, `IEEE802154_CA8210`, `IEEE802154_CA8210_DEBUGFS`, `IEEE802154_MCR20A`, and `IEEE802154_HWSIM`. Several SPI drivers select or depend on `REGMAP_SPI`; USB and debugfs options depend on `USB` and `DEBUG_FS`.

Control flow: Kconfig evaluation determines which object files the companion Makefile includes. Enabling the parent menu makes child choices visible; selecting a child as built-in or module controls whether the related driver is linked into the kernel image or built as a loadable module.

State and persistence behavior: The only persistent state is kernel build configuration in `.config` and generated autoconf headers. Runtime driver state is not present here.

Dependencies and integration points: The symbols integrate with the network device subsystem, `IEEE802154`, `MAC802154`, SPI, USB, common clock support, debugfs, regmap, and the Makefile in the same directory. Help text documents module names expected by users and packaging.

Risks and edge cases: Incorrect dependencies can create build failures or expose drivers without required bus/mac802154 support. `IEEE802154_DRIVERS` defaults to `y`, so new child defaults should be conservative. Debugfs must remain gated by both the CA8210 driver and `DEBUG_FS`.

Test signals: Run Kconfig builds for allnoconfig/menuconfig visibility, each driver as `m`, combinations without SPI/USB/MAC802154, and randconfig coverage to catch missing selects or unmet dependencies.
