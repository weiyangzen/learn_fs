# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ahb.c

## Purpose

This file is the platform/AHB bus frontend for ath9k on OF-described Qualcomm/Atheros SoCs with integrated Wi-Fi MACs. It maps MMIO resources, obtains IRQs, allocates the mac80211 hardware object, registers the interrupt handler, and calls shared ath9k initialization with AHB-specific bus operations.

## Important APIs and functions

- `ath9k_of_match_table[]` maps compatible strings such as `qca,ar9130-wifi`, `qca,ar9330-wifi`, `qca,ar9340-wifi`, and qca9530/9550/9560 variants to ath9k device IDs.
- `ath_ahb_read_cachesize()` reports L1 cache line size in 4-byte words for bus tuning.
- `ath_ahb_eeprom_read()` always fails and logs that EEPROM data must be supplied externally.
- `ath_ahb_bus_ops` supplies `ATH_AHB`, cache-size read, and EEPROM read callbacks to shared hardware code.
- `ath_ahb_probe()` is the platform probe path; `ath_ahb_remove()` is cleanup; `ath_ahb_init()` and `ath_ahb_exit()` register and unregister the `platform_driver`.

## Control flow

Probe maps the first platform resource with `devm_platform_ioremap_resource()`, obtains IRQ 0, fills channel-context ops, allocates `struct ieee80211_hw` with private `struct ath_softc`, binds the platform device to the hw object, initializes softc fields, requests a shared IRQ using `ath_isr`, retrieves the device ID from OF match data, and calls `ath9k_init_device()`. On success it logs the hardware name, MMIO pointer, and IRQ. Error paths free the IRQ and ieee80211 hardware object in reverse order. Remove deinitializes the device, frees IRQ, and frees the hw object.

## State and persistence behavior

Runtime state is stored in `struct ath_softc` under the allocated `ieee80211_hw`. `sc->mem`, `sc->irq`, `sc->dev`, and `sc->hw` bind platform resources to shared ath9k code. There is no persistent state; calibration/EEPROM state must come from external platform data or other firmware mechanisms because direct EEPROM read is intentionally unsupported here.

## Dependencies and integration points

The file depends on Linux platform driver, OF match data, MMIO resource management, IRQ registration, mac80211 allocation, and shared ath9k APIs from `ath9k.h`. It integrates with Kconfig through `CONFIG_ATH9K_AHB` and with the main module via `ath_ahb_init()`/`ath_ahb_exit()`.

## Risks

AHB devices require correct device-tree compatible strings, resource layout, IRQ, and external calibration data. A missing or wrong match data device ID leads to incorrect hardware initialization. Since IRQ is requested before `ath9k_init_device()`, failures must reliably free the IRQ; the code does. External EEPROM provisioning is a platform integration risk, not handled locally.

## Test signals

Boot an OF platform with each compatible, verify probe logs the expected hardware name, test missing MMIO/IRQ failures, confirm interrupt handling and remove cleanup, validate external calibration provisioning, and run mac80211 association/traffic tests on AHB SoCs.
