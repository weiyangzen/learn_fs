# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/eeprom.h

## Purpose

`eeprom.h` declares the packed on-device AR9170 EEPROM layout and EEPROM-derived constants used for band support, regulatory data, calibration tables, target powers, conformance limits, MAC address, chain masks, subsystem ID, and LED mode fields.

## Important APIs, Types, and Functions

Key constants include `AR9170_EEPROM_START`, chain and spur counts, calibration pier counts, target-power counts, CTL counts, and LED mode bitfields. `struct ar9170_eeprom_modal` holds per-band modal radio parameters such as antenna control, gains, attenuation, margins, IQ calibration, XPA timing, noise thresholds, and spur channels. Calibration structures include `ar9170_calibration_data_per_freq`, legacy and HT target-power structs, `ar9170_calctl_edges`, and `ar9170_calctl_data`. The top-level `struct ar9170_eeprom` is the packed binary layout read directly from device registers in `main.c`.

## Control Flow

The file provides no executable code. `main.c` reads the EEPROM from `AR9170_EEPROM_START` into `ar->eeprom`, then parses operating flags, regulatory domain, MAC address, and chain masks. `phy.c` consumes modal headers, calibration piers, target powers, and CTL edges when programming PHY/RF state for a channel.

## State and Persistence Behavior

The structures model persistent device calibration and identity state stored in nonvolatile EEPROM. Runtime code treats the data as authoritative but copies it into RAM in `ar->eeprom`; derived runtime fields include supported bands, permanent MAC address, survey allocation size, power tables, heavy-clip settings, and regulatory configuration.

## Dependencies and Integration Points

The layout uses Linux endian types and `__packed` to match firmware/hardware storage exactly. It integrates with `main.c` EEPROM reads, ath regulatory setup, `phy.c` calibration interpolation, MAC transmit-power programming, and debug includes that need the same shared definitions.

## Risks and Edge Cases

Any layout drift breaks binary compatibility with existing devices. Endianness conversion is required for multibyte fields. Calibration arrays use sentinel values such as `0xff`; missing or malformed EEPROM data can make channel setup fail or produce unsafe power limits. Chain mask mismatches are handled in `main.c` but can alter advertised HT transmit parameters.

## Test Signals

Validate `sizeof(struct ar9170_eeprom)` remains word aligned and compatible with `carl9170_read_eeprom()` chunking. Test devices with 2 GHz only, 5 GHz only, dual-band, different chain masks, and missing/sentinel calibration piers. Confirm regulatory domains, permanent MAC address, and per-channel target-power interpolation match known EEPROM dumps.
