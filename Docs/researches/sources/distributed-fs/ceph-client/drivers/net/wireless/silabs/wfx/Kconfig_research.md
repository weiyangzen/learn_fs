# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/Kconfig

Purpose: Defines the WFx driver Kconfig symbol for Silicon Labs WF200-family 802.11 chips.

Important APIs and types: `config WFX` is a tristate requiring `MAC80211`, either SPI or MMC support, and `MMC || !MMC` to prevent built-in WFx when MMC is modular. Help text notes SPI/SDIO bus support and Device Tree requirement for SDIO because reliable SDIO vendor IDs are not available.

Control flow and integration: The symbol controls compilation of the aggregate `wfx.o` object and conditional inclusion of SPI/SDIO bus objects. It also controls module availability for both bus drivers registered by `main.c`.

State and persistence: Persistent state is the `.config` choice `n/m/y`, which determines driver registration and module production.

Dependencies: Depends on mac80211 and bus subsystems. SPI and MMC dependencies map to `bus_spi.c` and `bus_sdio.c`.

Risks and test signals: Risks include invalid built-in/modular combinations with MMC, missing bus support, and user confusion when SDIO devices are not declared in Device Tree. Test build matrices for `WFX=m/y`, `SPI=y/m/n`, and `MMC=y/m/n`.

Test signals: Source read size: 13 lines, 506 bytes.
