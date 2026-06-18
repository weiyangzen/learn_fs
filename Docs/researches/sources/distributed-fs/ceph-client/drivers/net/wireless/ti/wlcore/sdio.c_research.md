# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/sdio.c

## Purpose
`sdio.c` is the SDIO bus glue for wlcore devices. It translates wlcore raw read/write/power/block-size operations to Linux MMC/SDIO calls, parses device tree data, and creates a child platform device (`wl12xx` or `wl18xx`) that the common core driver probes.

## Important APIs, Types, and Functions
`struct wl12xx_sdio_glue` stores the SDIO device and child platform device. `sdio_ops` implements `struct wl1271_if_operations` with `wl12xx_sdio_raw_read()`, `wl12xx_sdio_raw_write()`, `wl12xx_sdio_set_power()`, and `wl1271_sdio_set_block_size()`. Raw access uses CMD52 (`sdio_f0_readb/writeb`) for `HW_ACCESS_ELP_CTRL_REG` and CMD53 (`sdio_readsb/writesb` or `sdio_memcpy_fromio/toio`) for regular fixed/incrementing transfers. `wl1271_probe()` validates SDIO function 2, sets quirks, parses OF compatible data and IRQs, detects wl18xx by SDIO revision 3.00, and registers the platform child. Suspend sets `MMC_PM_KEEP_POWER` when WoWLAN is enabled and supported.

## Control Flow
The SDIO driver matches TI SDIO IDs, probes only function 0x02, prepares platform data containing `if_ops` and family metadata, maps IRQ/wakeirq from OF, and allocates a child platform device named according to detected chip family. The child receives IRQ resources and platform data, then common wlcore probe handles firmware and mac80211 registration. Remove unregisters the child and balances runtime PM.

## State and Persistence Behavior
State is per-device glue allocated with devm. Power state is delegated to MMC runtime PM and SDIO function enable/disable. `pwr_in_suspend` is stored in platform data based on host `MMC_PM_KEEP_POWER`. The module-level `dump` parameter controls hex dumps of SDIO transfers.

## Dependencies and Integration Points
Dependencies include Linux SDIO/MMC APIs, OF IRQ parsing, runtime PM, platform devices, `wlcore.h`, `wl12xx_80211.h`, and `io.h`. The file integrates with the common core exclusively through platform data and `wl1271_if_operations`.

## Risks and Test Signals
Risks include wrong function-number matching, failed IRQ parsing, SDIO revision misclassification, PM imbalance around `pm_runtime_put_noidle()`/remove, failure to keep power for WoWLAN, and transfer-mode differences for fixed vs incrementing addresses. Test signals include SDIO probe/remove, register reads/writes including ELP CMD52, firmware boot after `mmc_hw_reset()`, block size setup, suspend with and without host keep-power support, and optional transfer dumps.
