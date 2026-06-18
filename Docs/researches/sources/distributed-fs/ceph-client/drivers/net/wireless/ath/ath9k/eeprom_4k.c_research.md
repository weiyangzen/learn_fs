# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/eeprom_4k.c

Purpose: Implements EEPROM operations for 4K single-chain 2 GHz AR9285/AR9271-style devices, including EEPROM loading, validation, debug dumping, board register programming, PDADC table setup, and per-rate TX power programming.

Important APIs and functions: The exported ops table is `eep_4k_ops`. Internal callbacks include `ath9k_hw_4k_fill_eeprom()`, `ath9k_hw_4k_check_eeprom()`, `ath9k_hw_4k_get_eeprom()`, `ath9k_hw_4k_set_board_values()`, `ath9k_hw_4k_set_txpower()`, and `ath9k_hw_4k_get_spur_channel()`. Important helpers are `ath9k_hw_set_4k_power_cal_table()`, `ath9k_hw_set_4k_power_per_rate_table()`, and `ath9k_hw_4k_set_gain()`.

Control flow: Fill reads the 4K layout from offset 64, using USB register reads on USB devices. Check swaps fields if needed, validates checksum and major/minor version, and converts endian-sensitive modal fields. Board programming writes antenna switch, IQ correction, gain, antenna diversity, RF timing, CCA, PA timing, output/driver bias, and optional baseband desired-scale registers. TX power programming builds target power arrays, applies CTL/regulatory limits, programs PDADC tables, updates `regulatory->max_power_level`, and writes OFDM/CCK/HT rate power registers unless in test mode.

State and persistence: Persistent data lives in `ah->eeprom.map4k`. Runtime state includes PHY registers, `regulatory->max_power_level`, LED/antenna diversity related PHY state, and optional TPC register state. EEPROM content is only read and endian-normalized in memory.

Dependencies and integration points: Depends on common EEPROM helpers, AR9002 PHY register macros, silicon revision checks for AR9271 and AR9285 behavior, USB bus detection, mac80211 channel flags, and regulatory CTL values. Selected by `ath9k_hw_eeprom_init()` for AR9285/AR9271.

Risks: This layout supports only one chain, but the code still writes mirrored gain fields in places; chain mask assumptions need care. Version-dependent modal bitfields affect output bias and antenna diversity. PDADC arrays are static and register writes are buffered, so reset/channel configuration must be serialized.

Test signals: Probe AR9285 and AR9271 USB/non-USB devices, validate checksum and endian swap paths, test antenna diversity and diversity-combining, compare 2 GHz CCK/OFDM/HT20/HT40 power tables, verify TPC enable/disable paths, and confirm spur and MAC/regdomain debugfs dumps.
