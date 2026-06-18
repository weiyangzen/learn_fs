# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/eeprom.h

## Purpose
MT7603 EEPROM field map and bit definitions used by EEPROM loading, MCU calibration upload, txpower setup, and antenna detection.

## Important APIs, Types, And Functions
- `enum mt7603_eeprom_field` defines offsets for chip ID, version, MAC address, NIC config, RSSI offsets, Wi-Fi RF settings, 2 GHz/5 GHz power groups, rate power deltas, ELAN fields, temperature compensation, crystal calibration, and CP/FT version.
- `MT_TX_POWER_GROUP_SIZE_5G` and `MT_TX_POWER_GROUPS_5G` document 5 GHz power array geometry.
- `enum mt7603_eeprom_source` names PROM, efuse, and flash sources.
- `MT_EE_NIC_CONF_0_RX_PATH` and `MT_EE_NIC_CONF_0_TX_PATH` extract path counts from NIC config byte.

## Control Flow
Header-only constants are consumed by `eeprom.c`, `mcu.c`, and `init.c` to index the EEPROM byte array. There is no runtime flow in this file.

## State And Persistence
No state. It describes persistent EEPROM layout that is loaded into `dev->mt76.eeprom.data`.

## Dependencies And Integration Points
Includes `mt7603.h` for common chip definitions and bit macros. Its offsets must match firmware expectations for `MCU_EXT_CMD_EFUSE_BUFFER_MODE` and `MCU_EXT_CMD_SET_TX_POWER_CTRL`.

## Risks
Incorrect offsets corrupt calibration, MAC address, antenna mask, txpower, and firmware setup. Some fields are byte arrays while others are little-endian words, so callers must use the right accessor.

## Test Signals
Validate EEPROM dumps against known board data, firmware calibration success, expected antenna mask, target txpower, RSSI offsets, and no regression in MT7628/MT7688 variant detection.
