# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/eeprom.h

## Purpose
This header defines Prism54 EEPROM/PDA record layouts, calibration database formats, PDR record codes, country flag fields, and synth/frontend capability bits consumed by `eeprom.c` and scan setup.

## Important APIs, Types, and Functions
- `struct pda_entry` and `struct eeprom_pda_wrap` model the EEPROM/PDA container.
- Calibration structs include IQ autocal, channel output limits, longbow output points, PA curve samples, RSSI calibration entries, country records, antenna gains, and custom database wrappers.
- PDR constants identify MAC address, country, interface list, hardware component ID, RSSI, output-power, curve, and custom records.
- Country flags encode real/pseudo certification, band, indoor/outdoor, and index bits.
- Synth flags describe frontend type, IQ calibration mode, FAA switch, disabled bands, RX/TX diversity, and ASM.

## Control Flow
The header has no executable logic. It supplies packed layouts and constants for the EEPROM parser and firmware scan command builders.

## State and Persistence Behavior
The structs are binary views over EEPROM data and are not owned state by themselves. Callers copy/normalize selected records into `p54_common` heap allocations.

## Dependencies and Integration Points
It depends on Linux endian types and is included by p54 EEPROM and firmware I/O code. The definitions map directly to firmware/PDA records and must stay consistent with the device EEPROM format.

## Risks and Edge Cases
All structs are packed ABI formats. Mis-sizing, wrong endian conversion, or incorrect PDR values would corrupt calibration interpretation. Several custom PDR codes are driver-specific modifications and need careful validation before trust.

## Test Signals
Known-good EEPROM images parsing successfully, expected synth type reporting, channel table generation, and CRC validation are the main signals that the definitions match hardware data.
