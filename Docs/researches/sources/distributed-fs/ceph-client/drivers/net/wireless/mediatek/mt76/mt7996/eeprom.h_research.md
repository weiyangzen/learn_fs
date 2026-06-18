# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/eeprom.h

## Purpose
This header defines MT7996 EEPROM offsets, bitfields, band-selection enums, and channel-group helpers used by EEPROM parsing and power lookup.

## Important APIs, Types, And Functions
`enum mt7996_eeprom_field` names chip ID, version, MAC addresses, Wi-Fi config, rate-delta, and target-power offsets. Macros define TX/RX path, stream number, FEM PA/LNA config, and rate delta enable/sign/mask fields. `enum mt7996_eeprom_band` maps EEPROM band selectors. Inline helpers `mt7996_get_channel_group_5g()` and `mt7996_get_channel_group_6g()` map channel numbers to EEPROM target-power groups.

## Control Flow
There is no runtime flow beyond the inline channel group helpers. EEPROM code uses the offsets and masks to parse byte arrays and index target-power tables.

## State And Persistence
The constants describe persistent EEPROM layout and calibration/capability data. Channel group helpers determine which persistent target-power byte applies to a runtime channel.

## Dependencies And Integration Points
It includes `mt7996.h` for device context and kernel bit helpers. It is consumed by `eeprom.c` and power/regulatory code that needs target-power grouping.

## Risks
Offsets and masks are hardware/firmware ABI. Incorrect values can break chip validation, MAC address loading, chain capability, FEM validation, or TX power. Channel grouping must match the calibration table layout for 5 GHz and 6 GHz.

## Test Signals
EEPROM parsing across all bands, correct MAC address offsets, expected path/NSS capabilities, target-power lookup by 5/6 GHz channels, and fallback validation against default binaries validate this header.
