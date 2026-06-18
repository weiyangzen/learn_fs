# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/Kconfig

Purpose: Configuration menu for the ST-Ericsson CW1100/CW1200 mac80211 driver family.

Important APIs and types: Defines `CW1200` as the shared core tristate depending on `MAC80211` and `CFG80211`. Under `if CW1200`, it defines `CW1200_WLAN_SDIO` depending on `MMC` and `CW1200_WLAN_SPI` depending on `SPI`.

Control flow: Users first enable the common core, then choose one or both bus front-ends. Help text documents that SDIO defaults target Sagrad SG901-1091/1098 style platform data and that other designs need board/platform-data glue.

State and persistence: Kconfig selections persist in `.config` and drive Kbuild module generation.

Dependencies and integration: Integrates with cfg80211/mac80211 and either MMC SDIO or SPI subsystems. It controls objects declared in the CW1200 Makefile.

Risks: The driver is platform-data oriented; modern device-tree-only systems may need board-specific glue not represented by these options. Enabling the core without a bus module builds common code but cannot bind hardware.

Test signals: Build matrix should cover `CW1200=m` with SDIO, SPI, both, and neither bus front-end, plus dependency rejection when MMC/SPI or mac80211/cfg80211 are disabled.
