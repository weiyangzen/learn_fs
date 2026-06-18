# sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/aquantia.h

## Purpose
Provides shared register definitions, data structures, firmware fingerprint helpers, SGMII statistics descriptors, private state, and cross-module prototypes for the Aquantia PHY driver.

## Important APIs, Types, and Functions
Important register groups include VEND1 global control/reset, mailbox interfaces, firmware ID, per-speed global configuration, LED provisioning/drive registers, thermal registers, interrupt masks/status, reserved firmware status, and C22EXT SGMII stats. Key types are `aqr107_hw_stat`, `aqr_global_syscfg`, `enum aqr_rate_adaptation`, and `struct aqr107_priv`. The header declares `aqr_hwmon_probe`, `aqr_firmware_load`, Aquantia LED callbacks, `aqr_phy_led_active_low_set`, `aqr_phy_led_polarity_set`, and `aqr_wait_reset_complete`.

## Control Flow and State
The header has no direct runtime flow except the HWMON stub selected by `IS_REACHABLE(CONFIG_HWMON)`. It defines persistent driver state: accumulated SGMII stats, a 64-bit firmware fingerprint, saved LED polarity bitmaps, a global-configuration readiness flag, and per-speed host-interface/rate-adaptation mappings.

## Dependencies and Integration Points
Includes `linux/device.h` and `linux/phy.h` and is shared by `aquantia_main.c`, `aquantia_firmware.c`, `aquantia_hwmon.c`, and `aquantia_leds.c`. It encodes hardware ABI fields used by phylib, ethtool stats, LED class integration, HWMON, firmware loading, and interface-mode selection.

## Risks and Test Signals
Risks are incorrect masks or register addresses affecting multiple modules, HWMON stub divergence, firmware fingerprint mistakes changing interface translation, and private state layout assumptions across modules. Test signals include compile coverage with and without HWMON, LED polarity persistence after reset, SGMII stat reads, firmware fingerprint logs, and register dumps against datasheet values.
