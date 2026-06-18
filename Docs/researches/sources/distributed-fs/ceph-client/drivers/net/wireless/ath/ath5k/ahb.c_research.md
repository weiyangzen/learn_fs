# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/ahb.c

## Purpose

`ahb.c` is the ath5k platform-driver backend for Atheros 5xxx WiSoC devices on ATH25/AHB systems. It maps platform resources, reads board-provided EEPROM/MAC/revision data, enables SoC WLAN bus access and byte swapping, attaches common ath5k hardware, and tears down resources on platform removal.

## Important APIs And Functions

- `ath5k_ahb_read_cachesize()` reports cache-line size in 4-byte words.
- `ath5k_ahb_eeprom_read()` reads EEPROM words from `ar231x_board_config.radio`.
- `ath5k_hw_read_srev()` sets `ah->ah_mac_srev` from board `devid`.
- `ath5k_ahb_eeprom_read_mac()` copies WLAN0/WLAN1 MAC from board config based on platform device ID.
- `ath_ahb_bus_ops` provides bus type `ATH_AHB` and EEPROM/MAC/cache callbacks.
- `ath_ahb_probe()` validates platform data/resource, maps MMIO, gets IRQ, allocates `ieee80211_hw`, initializes `struct ath5k_hw`, enables SoC WLAN access, calls `ath5k_init_ah()`, and stores drvdata.
- `ath_ahb_remove()` disables SoC WLAN access, deinitializes ath5k, unmaps MMIO, and frees `ieee80211_hw`.

## Control Flow

Probe requires `ar231x_board_config` platform data and one memory resource. It maps the resource, obtains IRQ 0, allocates mac80211 hardware storage, and fills `ah->hw`, `ah->dev`, `ah->iobase`, `ah->irq`, and `ah->devid`. For AR2315-or-newer devices it enables WMAC AHB arbitration and global WMAC byte swapping. For older AR5312/231x devices it enables WLAN0 or WLAN1 DMA access and may set `cap_needs_2GHz_ovr` on dual-band boards. Then it calls common `ath5k_init_ah()`.

Remove reverses the SoC enablement, calls `ath5k_deinit_ah()`, unmaps `ah->iobase`, and frees the hardware object.

## State And Persistence Behavior

Board configuration supplies persistent device ID, EEPROM/radio data, flags, and MAC addresses. `struct ath5k_hw` holds mapped MMIO, IRQ, device ID, capability override, and the mac80211 pointer for the device lifetime. SoC register bits persist while bound; remove clears arbitration/DMA enable bits but not the AR2315 byteswap bit.

## Dependencies And Integration Points

The file depends on `<ath25_platform.h>`, Linux platform-device APIs, MMIO mapping, mac80211 allocation, ath common bus ops, register definitions in `reg.h`, and common ath5k attach/deinit.

## Risks

EEPROM bounds checking is subtle because the code advances a `u16 *` into board config and compares against a `void *`-derived end. Global SoC register accesses are hard-coded physical addresses, so this backend is not general-purpose. Bad platform data can produce invalid EEPROM/MAC reads. Resource cleanup must be updated if future probe steps add allocations.

## Test Signals

ATH25 boot should bind `ar231x-wmac` and create an ath5k phy. Validate WLAN0/WLAN1 MAC selection, EEPROM reads, SoC enable bits on bind/unbind, dual-band 2 GHz override behavior, and cleanup for missing platform data/resource, ioremap failure, IRQ failure, allocation failure, and attach failure.
