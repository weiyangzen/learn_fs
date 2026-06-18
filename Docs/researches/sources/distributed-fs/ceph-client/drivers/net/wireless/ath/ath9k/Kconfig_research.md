# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/Kconfig

## Purpose

This Kconfig file defines build-time configuration for the ath9k family: core PCI/AHB mac80211 devices, USB HTC devices, shared hardware/common libraries, debugfs, bluetooth coexistence, DFS certification hooks, dynamic ACK, WOW, rfkill, channel contexts, PC-OEM support, EEPROM-less PCI loader, hardware RNG, and spectral scan support.

## Important options

- `ATH9K_HW` and `ATH9K_COMMON` are hidden tristate helper modules selected by `ATH9K` and `ATH9K_HTC`.
- `ATH9K` is the main mac80211 Atheros 802.11n driver and depends on `MAC80211` and `HAS_DMA`; it selects LEDs where available and selects the shared helper modules.
- `ATH9K_PCI` and `ATH9K_AHB` enable bus frontends for PCI/PCIe and OF-backed SoC AHB devices.
- `ATH9K_HTC` enables USB HTC devices such as AR9271 and selects shared ath9k hardware/common code.
- `ATH9K_DEBUGFS`, `ATH9K_HTC_DEBUGFS`, `ATH9K_STATION_STATISTICS`, `ATH9K_DFS_DEBUGFS`, and `ATH9K_COMMON_SPECTRAL` expose debug and spectral functionality.
- Certification/risk-sensitive options include `ATH9K_TX99` and `ATH9K_DFS_CERTIFIED`, both guarded by `CFG80211_CERTIFICATION_ONUS`.

## Control flow and integration

The file controls which objects in `Makefile` are built. User-visible options choose bus support and optional functionality; hidden helper symbols allow the Makefile to build shared modules only when a frontend needs them. Several options depend on kernel subsystems such as PCI, USB, OF, PM, RFKILL, DEBUG_FS, MAC80211_DEBUGFS, RELAY, and HW_RANDOM.

## State and persistence behavior

There is no runtime state here. Kernel `.config` selections persist across builds and determine available code paths, modules, and exported features. Defaults are conservative for testing/certification features and permissive for common hardware support such as PCI and rfkill.

## Dependencies and risks

Incorrect dependencies can produce link failures or expose code without required kernel subsystems. Regulatory-sensitive options are intentionally not default because enabling TX99 or DFS initiation on uncertified platforms can violate certification assumptions. Debugfs and station statistics increase visibility but also code size and runtime surface. `ATH9K_PCI_NO_EEPROM` is separated because it supports special EEPROM-less platforms and should not be enabled accidentally.

## Test signals

Run Kconfig dependency tests through `oldconfig`/`allmodconfig`, verify object inclusion through `make M=...`, test matrix builds for PCI-only, AHB-only, HTC-only, debugfs, WOW, HWRNG, BT coexistence, and spectral combinations, and confirm certification-gated options remain disabled unless explicitly selected with `CFG80211_CERTIFICATION_ONUS`.
