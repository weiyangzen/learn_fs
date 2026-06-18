# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9580_1p0_initvals.h

Purpose: Supplies AR9580 1.0 initialization data for radio, baseband, MAC, RX gain, DFS/Japan channel support, and a broad set of TX gain modes. These tables are selected for `AR_SREV_9580()` hardware in AR9003 setup.

Important APIs and data: Defines `ar9580_1p0_radio_core`, `ar9580_1p0_radio_postamble`, `ar9580_1p0_baseband_core`, `ar9580_1p0_low_ob_db_tx_gain_table`, `ar9580_1p0_high_power_tx_gain_table`, `ar9580_1p0_lowest_ob_db_tx_gain_table`, `ar9580_1p0_mac_core`, `ar9580_1p0_mixed_ob_db_tx_gain_table`, `ar9580_1p0_type6_tx_gain_table`, `ar9580_1p0_rx_gain_table`, `ar9580_1p0_baseband_postamble`, and `ar9580_1p0_baseband_postamble_dfs_channel`. Macro aliases reuse AR9300 2.2 SOC, MAC postamble, no-XLNA RX gain, type5/high-OB/DB TX gain, fast-clock, and Japan CCK FIR data.

Control flow: The AR9580 branch installs the local MAC/baseband/radio/SOC/RX/TX tables, then assigns fast-clock, Japan CCK FIR, and DFS tables. TX gain helper modes select among lowest, high-OB/DB, low-OB/DB, high-power, mixed, type5, and type6 tables according to the EEPROM/configured gain index. RX gain mode 1 switches to the aliased no-XLNA table.

State and persistence: The arrays are static read-only data. They affect runtime through `struct ath_hw` INI descriptors and the resulting device register writes. No persistent storage is modified.

Dependencies and integration points: Integrated with AR9003 hardware attach, EEPROM gain-index interpretation, DFS channel handling, fast-clock programming, Japan channel support, and common AR9300 tables. AR9580 has more TX gain variants than several neighboring chips, making it a key consumer of the gain-mode dispatch table.

Risks: Gain-mode dispatch must remain aligned with available AR9580 tables; selecting the wrong table can violate power limits or reduce performance. DFS postamble values are regulatory-sensitive. Shared aliases mean AR9300 table changes can affect AR9580 behavior. Modal array widths must match the INI programming helper expectations.

Test signals: Validate AR9580 reset and association, run TX power/EVM checks for all supported gain modes, test DFS channels and radar-capable channel changes, verify Japan 2484 MHz behavior where applicable, exercise no-XLNA RX mode, and watch for calibration, ANI, or stuck beacon regressions under traffic.
