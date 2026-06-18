# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/eeprom_9287.c

Purpose: Implements EEPROM operations for AR9287 two-chain 2 GHz devices, with support for normal closed-loop PDADC programming and open-loop power control calibration.

Important APIs and functions: The exported ops table is `eep_ar9287_ops`. Major callbacks are `ath9k_hw_ar9287_fill_eeprom()`, `ath9k_hw_ar9287_check_eeprom()`, `ath9k_hw_ar9287_get_eeprom()`, `ath9k_hw_ar9287_set_board_values()`, and `ath9k_hw_ar9287_set_txpower()`. Helper functions include `ar9287_eeprom_get_tx_gain_index()`, `ar9287_eeprom_olpc_set_pdadcs()`, `ath9k_hw_set_ar9287_power_cal_table()`, and `ath9k_hw_set_ar9287_power_per_rate_table()`.

Control flow: Fill reads from `AR9287_EEP_START_LOC` for regular devices or `AR9287_HTC_EEP_START_LOC` for USB. Check handles byte swapping, checksum, modal field conversion, and version validation. `get_eeprom()` exposes revision-gated temperature slope and open-loop fields. Calibration setup either computes PDADC gain boundaries from calibration piers or programs open-loop reference power registers per chain. TX power setup clamps target powers by CTL edge and scaled chain power, writes OFDM/CCK/HT rate registers, applies HT40 PDADC increment only for closed-loop mode, and enables/disables TPC.

State and persistence: Persistent calibration is `ah->eeprom.map9287`. Runtime state includes `ah->initPDADC` for open-loop mode, PHY analog/BB registers, PDADC tables, and regulatory max power. No EEPROM writes occur.

Dependencies and integration points: Depends on common EEPROM math, AR9002 PHY fields, USB HTC EEPROM loading, AR9287 revision macros, regulatory CTL tables, and `ath9k_hw_update_regulatory_maxpower()`. It is selected by `ath9k_hw_eeprom_init()` for AR9287 silicon.

Risks: Open-loop and closed-loop paths share data unions but interpret calibration rows differently. Power table offset adjustment shifts PDADC arrays and can underflow if EEPROM values are inconsistent. Chain-specific direct register addresses in OLPC code are less self-documenting than macro-based writes.

Test signals: Validate regular and HTC USB EEPROM offsets, minor version 1/2/3 feature gates, two-chain mask combinations, open-loop power control enabled and disabled, HT20/HT40 rate power programming, temperature slope queries, and board RF bias programming for both chains.
