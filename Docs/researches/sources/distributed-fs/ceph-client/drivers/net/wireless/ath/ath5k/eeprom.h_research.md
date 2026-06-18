# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/eeprom.h

## Purpose
`eeprom.h` is the EEPROM layout contract for ath5k. It defines offsets, version constants, bitfield extractors, calibration dimensions, RF/regulatory modes, EEPROM read helper macros, and all storage types used by `eeprom.c` and later PHY/TX-power code. It is not just a header for declarations; it encodes the packed on-device data format and the in-memory normalized representation.

## Important Types and Constants
Important offset families include `AR5K_EEPROM_INFO()`, version markers from `AR5K_EEPROM_VERSION_3_0` through `5_3`, `AR5K_EEPROM_MODES_11A/B/G()`, `AR5K_EEPROM_GROUPS_START()`, target power offsets, CTL offsets, RFKill fields, PCIe SERDES marker, and misc-word extractors such as `AR5K_EEPROM_EEMAP()`, `AR5K_EEPROM_TARGET_PWRSTART()`, and `AR5K_EEPROM_CAL_DATA_START()`. `AR5K_EEPROM_OFF()` centralizes old/new offset switching.

Core data types are `struct ath5k_chan_pcal_info_rf5111`, `_rf5112`, `_rf2413`, `struct ath5k_pdgain_info`, `struct ath5k_chan_pcal_info`, `struct ath5k_rate_pcal_info`, `struct ath5k_edge_power`, and `struct ath5k_eeprom_info`. The normalized calibration model stores frequency piers, min/max power, a union of raw RF-specific data, then allocated `pd_curves` for interpolation. `struct ath5k_eeprom_info` aggregates header fields, RF calibration settings, power calibration arrays for 11a/11b/11g, per-rate target powers, CTL edges, noise floor settings, and spur mitigation tables.

## State, Dependencies, and Integration
The `AR5K_EEPROM_READ()` macro depends on an `ah` variable in scope and calls `ath5k_hw_nvram_read()`, returning `-EIO` from the caller on failure. This makes the header tightly coupled to parser functions and their error model. The constants are consumed by EEPROM parsing, PHY setup, regulatory code, RFKill/GPIO setup, spur mitigation, TX power table generation, and capability discovery.

## Risks and Test Signals
Risks come from layout constants being de facto hardware ABI: changing masks, array sizes, version gates, or offset arithmetic can corrupt all downstream calibration. The macro-based read helper hides control flow and requires compatible caller signatures. Test signals include compile coverage of all parsers, attach tests on cards with each EEPROM version/EEMAP, bounds checking of pier/CTL/spur arrays, and comparison of parsed `ath5k_eeprom_info` fields against known-good dumps.
