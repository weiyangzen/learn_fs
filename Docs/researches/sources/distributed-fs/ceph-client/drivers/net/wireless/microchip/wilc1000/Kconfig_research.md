# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/Kconfig

Purpose: Defines WILC1000 core and bus-specific configuration symbols for SDIO, SPI, and optional SDIO out-of-band interrupt support.

Important APIs and entries: `config WILC1000` is the hidden/shared tristate core selected by bus drivers. `WILC1000_SDIO` depends on `CFG80211`, `INET`, and `MMC`, selects `WILC1000`, and describes SDIO operation. `WILC1000_SPI` depends on `CFG80211`, `INET`, and `SPI`, selects `WILC1000`, `CRC7`, and `CRC_ITU_T`. `WILC1000_HW_OOB_INTR` is a bool depending on SDIO.

Control flow: Users select an SDIO or SPI bus transport, which selects the shared core module. Bus symbols drive compilation of `sdio.o` or `spi.o`; the core symbol drives common cfg80211/netdev/HIF/wlan objects.

State and persistence: Configuration choices persist in `.config` and determine module availability, bus registration, and optional interrupt handling.

Dependencies and integration points: Integrated by the Microchip vendor Kconfig and the WILC1000 Makefile. Runtime code assumes cfg80211 and IP networking support, while bus modules rely on MMC or SPI subsystems.

Risks: The help text says Atmel WILC1000 and Wi-Fi-only 802.11n; WILC3000 firmware support appears in netdev code, so configuration wording may not fully describe all chip ids handled by core code. Missing CRC selections would break SPI protocol helpers.

Test signals: Kconfig dependency resolution for SDIO/SPI, allmodconfig/randconfig coverage, and builds with OOB interrupt enabled validate this file.
