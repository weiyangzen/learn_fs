<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_eeprom.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_eeprom.h

Purpose: shared mt76x02 EEPROM map and conversion helpers. It names offsets for chip ID, MAC, NIC configuration, RX gain, TX power, TSSI, temperature compensation, and usage-map fields.

Important APIs/types/functions: `enum mt76x02_eeprom_field`, `enum mt76x02_eeprom_modes`, `enum mt76x02_board_type`, `mt76x02_eeprom_get()`, `mt76x02_field_valid()`, sign-extension helpers, and `mt76x02_rate_power_val()`.

Control flow: declarative header; inline helpers validate odd/out-of-range offsets, decode little-endian words, and turn signed/optional EEPROM nibbles/bytes into calibrated signed values.

State and persistence: no mutable state. It defines the interpretation of persistent EEPROM/eFUSE bytes consumed by init and PHY power code.

Dependencies/integration: included by mt76x02 EEPROM helpers and mt76x2 EEPROM code; depends on unaligned access through callers and on `struct mt76x02_dev`.

Risks: offset aliases such as XTAL trim sharing addresses, signed-value polarity, optional enable-bit handling, and bounds checks returning `-1` as an int. Test signals include EEPROM fixture parsing, invalid/0xff fields, power table conversion, and channel/band capability derivation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_eeprom.h -->
