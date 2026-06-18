## sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54spi_eeprom.h

Purpose: this header embeds a static Prism54 SPI EEPROM/PDA image as `p54spi_eeprom[]`. It is not executable logic; it is calibration and identity data used by the p54 SPI path when a device lacks a usable external EEPROM image.

Important data: the byte array starts with an `eeprom_pda_wrap`-style magic header, a placeholder MAC address, interface list data, hardware platform component ID, country list/default country, antenna gain, RSSI approximation, PA calibration curves, ZIF TX IQ calibration entries for 2.4 GHz channels, and a `PDR_END` marker. Comments identify PDA records such as `PDR_MAC_ADDRESS`, `PDR_INTERFACE_LIST`, `PDR_COUNTRY_LIST`, `PDR_PRISM_PA_CAL_CURVE_DATA_CUSTOM`, and `PDR_PRISM_ZIF_TX_IQ_CALIBRATION`.

Control flow and state: there are no functions, locks, or runtime state transitions in this file. Persistence behavior is the static in-kernel copy of factory-like EEPROM data; downstream parser code treats this byte stream as if it were read from device EEPROM.

Dependencies and integration: it is protected by `P54SPI_EEPROM_H` and depends on p54 EEPROM/PDA parsers elsewhere to interpret record lengths and IDs correctly. Regulatory and RF calibration behavior depends on consumers preserving the byte ordering and record boundaries.

Risks: the embedded MAC is explicitly bogus, so callers must replace or tolerate it. The large calibration table is brittle: accidental byte edits, truncation, endian assumptions, or record length mismatches can silently damage RF behavior. Test signals are compile inclusion, successful p54 EEPROM parse, expected country/channel registration, and functional TX power/RSSI behavior on SPI Prism54 hardware.
