# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/eeprom.h

## Purpose
Defines MT7601U EEPROM/efuse offsets, bitfields, calibration data structures, and signed six-bit conversion helpers.

## Important APIs, Types, And Functions
Defines `MT7601U_EEPROM_SIZE`, max EEPROM version, default TX power, `enum mt76_eeprom_field`, NIC config bit masks, TX power by-rate offset macro, `enum mt7601u_eeprom_access_modes`, `struct power_per_rate`, `struct mt7601u_rate_power`, `struct reg_channel_bounds`, `struct mt7601u_eeprom_params`, and helpers `s6_validate()`, `s6_to_int()`, and `int_to_s6()`.

## Control Flow
No runtime flow except inline signed-six-bit validation/conversion used by EEPROM parsing and PHY power programming.

## State And Persistence
The structures define persistent parsed EEPROM state attached to `dev->ee`, including power tables, regulatory channel bounds, TSSI calibration, RSSI offsets, LNA gain, and frequency offset.

## Dependencies And Integration Points
Consumed by `eeprom.c`, debugfs, and PHY calibration code. Depends on bitfield macros and `struct mt7601u_dev` forward declaration.

## Risks
Offsets are hardware ABI; wrong values corrupt calibration. `s6_validate()` warns on out-of-range values but masks them, so caller validation remains important.

## Test Signals
Parsed debugfs EEPROM output matches raw efuse contents and signed power conversions behave for boundary values -32 and +31.
