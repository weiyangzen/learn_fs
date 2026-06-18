# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/eeprom.c

## Purpose
This file parses Prism54 EEPROM/PDA data, builds mac80211 band/channel tables, extracts calibration/output-power/RSSI data, applies regulatory hints, and reads EEPROM slices through firmware when needed.

## Important APIs, Types, and Functions
- `p54_parse_eeprom()` is the main parser and is exported.
- `p54_read_eeprom()` downloads EEPROM in firmware-sized blocks then parses it.
- `p54_generate_channel_lists()` merges IQ autocal, output limits, and PA curve records into usable channels.
- `p54_generate_band()` allocates `ieee80211_supported_band` data and fills surveys.
- `p54_convert_rev0()`, `p54_convert_rev1()`, `p54_convert_output_limits()`, and `p54_convert_db()` normalize EEPROM database formats into `p54_cal_database`.
- `p54_parse_rssical()` and `p54_rssi_find()` provide RSSI-to-dBm calibration lookup.
- Static rate arrays define 2.4 GHz and 5 GHz legacy rates.

## Control Flow
The parser starts after the PDA wrapper header, walks variable-length `pda_entry` records, bounds-checks each entry against the supplied EEPROM buffer, handles known PDR codes, updates a running CRC, and stops at `PDR_END` only if checksum matches. It extracts MAC address, power limits, PA curves, IQ calibration, country, interface/synth info, hardware version, RSSI calibration, and custom database wrappers. After a valid terminator, it verifies required data exists, derives `rxhw`, generates channel/band tables, initializes Xbow synth if needed, exposes 2/5 GHz bands according to synth disable bits, records diversity support, generates a random MAC if EEPROM address is invalid, and reports hardware identity.

## State and Persistence Behavior
Parsed state is stored in `struct p54_common`: `iq_autocal`, `output_limit`, `curve_data`, `rssi_db`, `survey`, `band_table`, `rxhw`, diversity masks, permanent MAC address, and current RSSI default. On parse failure, allocated calibration/survey structures are freed and pointers reset. `p54_read_eeprom()` uses transient heap storage for the full EEPROM image.

## Dependencies and Integration Points
It depends on Linux firmware, mac80211/cfg80211 channel and regulatory APIs, CRC-CCITT, sorting helpers, Ethernet address helpers, and p54 firmware I/O via `p54_download_eeprom()`. It integrates with p54 PCI/USB/SPI setup, common registration, scan/channel-change logic, and RSSI reporting.

## Risks and Edge Cases
EEPROM data is untrusted hardware/firmware input. Important risks are malformed lengths, unsupported PA curve revisions, missing required records, checksum failure, incomplete per-channel calibration, invalid MAC addresses, and custom wrapper shape mismatches. Some frequency band boundaries are marked FIXME and are legacy-specific. A subtle loop in `p54_update_channel_param()` starts from `list->entries`, so correctness depends on zeroed allocation and max-entry bounds.

## Test Signals
Signals include successful parse of known device EEPROMs, generated bands matching expected channels/power limits, regulatory hints for pseudo-country entries, correct fallback to default RSSI calibration, and failure on corrupted CRC/lengths. Runtime scan success validates that calibration databases line up with selected channels.
