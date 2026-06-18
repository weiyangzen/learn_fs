# sources/distributed-fs/ceph-client/include/linux/mmc/card.h

## Purpose
`mmc/card.h` defines the MMC core's card-facing state. It models parsed CID/CSD/EXT_CSD/SCR/SSR data, SD switch and extension capabilities, UHS-II card configuration, SDIO common/function data, physical partitions, quirks, and the main `struct mmc_card` device object.

## Important APIs, Types, And Functions
Key types are `struct mmc_cid`, `struct mmc_csd`, `struct mmc_ext_csd`, `struct sd_scr`, `struct sd_ssr`, `struct sd_switch_caps`, `struct sd_ext_reg`, `struct sd_uhs2_config`, `struct sdio_cccr`, `struct sdio_cis`, `struct mmc_part`, and `struct mmc_card`. Helper macros identify card types (`mmc_card_mmc()`, `mmc_card_sd()`, `mmc_card_sdio()`, `mmc_card_sd_combo()`), and inline helpers expose 4 KiB sector and async IRQ support. The only external function declared here is `mmc_card_is_blockaddr()`.

## Control Flow And State
The header itself has no active control flow; it defines persistent card state populated during card detection and mode negotiation. `struct mmc_card` binds a `struct device` to a host, OCR/RCA/type/state, raw and parsed register snapshots, erase/trim/cache/HPI/CQE capabilities, SDIO functions and tuples, selected bus speed/drive strength, debugfs root, eMMC physical partition descriptors, and a completion workqueue. Quirk bits alter later block, SDIO, erase, cache, tuning, and power-off behavior.

## Dependencies And Integration Points
Dependencies include the device model and module device tables. Integration points include MMC block, SD, SDIO, CQE, debugfs, eMMC partition handling, card detection, mode switching, power management, and host capabilities from `host.h`.

## Risks And Test Signals
Risks include mis-parsed register fields, unit conversion errors for sectors/bytes/timeouts, stale raw-vs-parsed capability state, quirk bit regressions, SDIO function count overflow, and wrong partition access flags. Test signals include card enumeration across MMC/SD/SDIO/combo media, EXT_CSD parsing tests, erase/trim/cache/HPI/CQE behavior tests, debugfs inspection, partition exposure tests, and known-bad-card quirk coverage.
