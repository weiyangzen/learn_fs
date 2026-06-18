# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/Kconfig

## Purpose
Defines build-time options for the common TI wlcore module and its SPI/SDIO transport modules.

## Important APIs, types, and functions
- `config WLCORE` is the common mac80211-based TI WLAN core and selects `FW_LOADER`.
- `config WLCORE_SPI` depends on `WLCORE`, `SPI_MASTER`, and `OF`, and selects `CRC7`.
- `config WLCORE_SDIO` depends on `WLCORE` and `MMC`.

## Control flow
No runtime flow. Kconfig controls which common and transport modules are built.

## State and persistence behavior
No runtime state. Values persist in the kernel build configuration.

## Dependencies and integration points
Chip-family modules such as wl18xx select or depend on `WLCORE`. Transport modules provide bus-specific access under the common wlcore abstraction.

## Risks and test signals
Dependency mistakes cause broken build combinations or missing firmware loader/transport support. Test builtin/module/disabled combinations for wlcore, SPI, SDIO, OF, MMC, and mac80211.
