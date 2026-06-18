# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/Makefile

Purpose: Defines Kbuild object composition for WILC1000 common core and SDIO/SPI bus modules.

Important APIs and entries: `obj-$(CONFIG_WILC1000) += wilc1000.o`; `wilc1000-objs` contains `cfg80211.o`, `netdev.o`, `mon.o`, `hif.o`, `wlan_cfg.o`, and `wlan.o`. `CONFIG_WILC1000_SDIO` builds `wilc1000-sdio.o` from `sdio.o`; `CONFIG_WILC1000_SPI` builds `wilc1000-spi.o` from `spi.o`.

Control flow: Kbuild links common objects into one core module/object and bus-specific shims separately. Bus modules use exported core symbols such as cfg80211 init and netdev interface creation.

State and persistence: No runtime state. Build composition is determined by `.config`.

Dependencies and integration points: Coordinates with Kconfig symbols and source files not all in this subset (`wlan.c`, `wlan_cfg.c`, `sdio.c`, `spi.c`). Module firmware declarations live in `netdev.c`.

Risks: Common object ordering generally does not matter, but missing `mon.o` or `hif.o` would break cfg80211 monitor/P2P or host-interface symbols. Bus-specific modules depend on core symbols being exported where needed.

Test signals: Modular and built-in builds for core plus SDIO/SPI combinations, modpost symbol checks, and clean link of `wilc1000.o` validate this file.
