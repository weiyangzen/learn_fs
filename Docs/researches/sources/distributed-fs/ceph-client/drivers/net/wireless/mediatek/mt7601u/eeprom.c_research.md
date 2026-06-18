# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/eeprom.c

## Purpose
Reads MT7601U efuse/EEPROM calibration data and converts it into driver calibration, regulatory, MAC address, power, RSSI, frequency-offset, and TSSI state.

## Important APIs, Types, And Functions
`mt7601u_eeprom_init()` is the exported initializer. Internal helpers read efuse blocks, validate physical usage-map size, detect TSSI support, set chip capabilities, compute per-channel power, choose country channel bounds, calculate RF frequency offset compensation, validate RSSI offsets, program per-rate TX power registers, and initialize TSSI slope/offset data.

## Control Flow
Initialization first checks the efuse usage map to reject devices that require an unsupported default EEPROM file. It allocates `dev->ee`, reads 256 bytes in 16-byte efuse blocks, warns on newer EEPROM versions, installs MAC address, parses capabilities and power tables, writes TX power configuration registers, and frees the temporary EEPROM buffer.

## State And Persistence
Persistent parsed state is stored in `dev->ee`: TSSI enable/data, RF frequency offset, RSSI offsets, reference temperature, LNA gain, per-channel power, per-rate power table, original CCK BW20 powers, and regulatory channel range. It also writes MAC address registers and TX power configuration hardware registers.

## Dependencies And Integration Points
Depends on MTD/OF headers only indirectly here, register access/polling, EEPROM field definitions in `eeprom.h`, MAC address setup in `mac.c`, and PHY calibration code that later consumes `dev->ee`.

## Risks
Invalid or all-0xff fields require fallback defaults; mishandling signed six-bit power values can over/under-program TX power. Region parsing has vendor quirks and a TODO for region 33/channel 14. Devices needing an external default EEPROM are explicitly unsupported.

## Test Signals
Probe logs EEPROM version/region, valid MAC address selection, correct 1-14 channel exposure by region, sane per-channel/per-rate power in debugfs, TSSI-enabled calibration on matching devices, and graceful failure on unusable efuse maps.
