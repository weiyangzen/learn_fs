# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_chip.c

## Purpose
Implements the ZD1211/ZD1211B chip abstraction above USB register commands and below mac80211/RF-specific drivers. It initializes the MAC/BBP register blocks, reads EEPROM policy and calibration data, serializes register access, manages RF callbacks, configures channel/rates/beacon/LED state, and exposes chip lifecycle helpers to `zd_mac.c`.

## Important APIs, Types, And Functions
Public entry points include `zd_chip_init()`, `zd_chip_clear()`, `zd_chip_init_hw()`, `zd_chip_read_mac_addr_fw()`, `zd_ioread16/32()`, `zd_iowrite16/32()`, `zd_ioread32v()`, `zd_iowrite32a()`, `zd_chip_set_channel()`, `zd_read_regdomain()`, `zd_write_mac_addr()`, `zd_write_bssid()`, `zd_chip_switch_radio_on/off()`, `zd_chip_enable_int()`, `zd_chip_disable_int()`, `zd_chip_enable_rxtx()`, `zd_chip_disable_rxtx()`, `zd_chip_enable_hwint()`, `zd_chip_disable_hwint()`, `zd_chip_set_basic_rates()`, `zd_chip_control_leds()`, `zd_set_beacon_interval()`, `zd_rx_rate()`, `zd_chip_set_multicast_hash()`, and `zd_chip_get_tsf()`. Internal helpers convert 32-bit register IO into 16-bit USB requests, read EEPROM POD/calibration fields, lock/unlock PHY registers, reset ZD1211/ZD1211B PHY tables, initialize HMAC registers, and apply optional EEPROM-driven RF/BBP patches.

## Control Flow
`zd_chip_init()` zeroes the composite state and initializes USB and RF subobjects. Hardware bring-up in `zd_chip_init_hw()` runs under `chip->mutex`: marks `CR_AFTER_PNP`, discovers firmware register base, disables GPI and hardware interrupts, reads POD flags and RF type, writes BBP/HMAC defaults, calls `zd_rf_init_hw()`, records firmware version, reads calibration/integration tables, and prints a device ID. Runtime channel changes lock PHY registers, invoke the RF driver's `set_channel`, update per-channel power/integration/OFDM calibration when the RF wants it, patch CCK gain and 6M band-edge settings, then unlock PHY registers. RX/TX and interrupt methods delegate to the USB layer while preserving the chip mutex contract.

## State And Persistence
Persistent state lives in `struct zd_chip`: `zd_usb`, `zd_rf`, `mutex`, firmware register base, EEPROM-derived power calibration arrays for 14 channels, OFDM calibration tables, link LED selection, PA type, and patch capability bits. Register writes persist in device firmware/hardware until reset. The code deliberately keeps all USB register access serialized by `chip->mutex`; many locked helpers assert that contract in debug builds.

## Dependencies And Integration Points
Depends on `zd_usb` register/RF write primitives, `zd_rf` RF callbacks, `zd_mac` rate and PLCP definitions, Linux mutexes, mac80211 interface type constants, and device logging. It integrates upward with mac80211 operations through `zd_mac.c` and downward with firmware over USB vendor requests and interrupt endpoints.

## Risks
Register ordering is fragile, especially PHY lock/unlock, ZD_CR204 before ZD_CR203, and beacon timing register invariants. `read_values()` packs EEPROM words into byte tables with legacy indexing; off-by-one or guard errors affect transmit power. Channel 1/11 band-edge comments note regulatory-domain assumptions. Several APIs return zeroed/default behavior after hardware IO errors, such as TSF read returning 0. Any caller bypassing `chip->mutex` can race USB command buffers or RF state.

## Test Signals
Probe should log firmware version and full chip/RF identity. Exercise ZD1211 and ZD1211B devices, each supported RF type, channels 1/11/14, interface start/stop, beacon interval changes, multicast filter updates, LED association/scanning transitions, suspend/reset restore, and failed USB IO paths. DEBUG builds should not trip `ZD_ASSERT(mutex_is_locked(&chip->mutex))`.
