# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/Kconfig

## Purpose
This Kconfig file defines build options for the Prism54 softmac family: common code plus USB, PCI, SPI, optional SPI fallback EEPROM, and LED support.

## Important APIs, Types, and Functions
- `P54_COMMON` is a tristate depending on `MAC80211` and selecting `FW_LOADER` and `CRC_CCITT`.
- `P54_USB` depends on `P54_COMMON && USB` and selects `CRC32`.
- `P54_PCI` depends on `P54_COMMON && PCI`.
- `P54_SPI` depends on `P54_COMMON && SPI_MASTER`.
- `P54_SPI_DEFAULT_EEPROM` optionally embeds a generic SPI EEPROM blob.
- `P54_LEDS` depends on p54, mac80211 LED support, and compatible `LEDS_CLASS`, defaulting to `y`.

## Control Flow
Configuration choices determine which transport modules are built. The common module is required by every frontend, while frontends pull in their bus-specific probe/runtime code.

## State and Persistence Behavior
The file persists selections in the kernel config only. Runtime consequences include firmware loader availability, CRC support for EEPROM parsing, optional embedded EEPROM data, and LED class registration.

## Dependencies and Integration Points
It integrates with mac80211, USB, PCI, SPI master, firmware loader, CRC, and LED class subsystems. It is sourced from the vendor-level Intersil Kconfig.

## Risks and Edge Cases
Selecting SPI fallback EEPROM embeds generic calibration/country/interface values and is explicitly a fallback; incorrect use can produce suboptimal or regulatory-sensitive behavior. LED dependency expression must stay aligned with built-in/module combinations.

## Test Signals
Kconfig parsing, expected symbol visibility, and successful builds for common-only plus each transport combination are the main signals.
