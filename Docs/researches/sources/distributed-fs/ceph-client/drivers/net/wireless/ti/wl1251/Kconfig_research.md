# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/Kconfig

Purpose: Defines kernel configuration options for the TI wl1251 core driver and its SPI/SDIO bus frontends.

Important APIs, types, and functions: `WL1251` is a tristate requiring `MAC80211` and selecting `FW_LOADER` and `CRC7`. `WL1251_SPI` depends on `WL1251 && SPI_MASTER`. `WL1251_SDIO` depends on `WL1251 && MMC`.

Control flow: The core module must be enabled before a bus-specific module can be selected. Help text identifies module names `wl1251`, `wl1251_spi`, and `wl1251_sdio`.

State and persistence: Build configuration only.

Dependencies and integration points: Integrates with mac80211, firmware loading, CRC7 support, SPI, MMC/SDIO, and the wl1251 Makefile.

Risks: Bus modules are selectable only when the core is enabled; distro configs must include the correct frontend for hardware discovery. Firmware availability remains runtime dependent.

Test signals: Kconfig dependency checks and module build/load tests for SPI and SDIO variants.
