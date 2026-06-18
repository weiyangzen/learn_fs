# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/Makefile

## Purpose
Defines object composition for the common wlcore module and its SPI/SDIO transport modules.

## Important APIs, types, and functions
- `wlcore-objs` includes common main, command, I/O, event, TX/RX, power-save, ACX, boot, init, debugfs, scan, sysfs, and vendor command objects.
- `wlcore_spi-objs` and `wlcore_sdio-objs` build transport implementations.
- Testmode support is conditionally added when `CONFIG_NL80211_TESTMODE` is enabled.

## Control flow
No runtime flow. kbuild combines objects according to Kconfig symbols.

## State and persistence behavior
No runtime state. Build outputs depend on configuration.

## Dependencies and integration points
Integrates the common wlcore implementation used by wl12xx/wl18xx lower drivers and bus modules.

## Risks and test signals
Object-list drift can cause unresolved symbols or missing runtime features. Build tests should cover wlcore, wlcore_spi, wlcore_sdio, and NL80211 testmode configurations.
