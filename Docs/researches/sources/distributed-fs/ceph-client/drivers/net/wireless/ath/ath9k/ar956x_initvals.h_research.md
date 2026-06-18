# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar956x_initvals.h

Purpose: Defines QCA956x/QCA9561 SoC init tables for AR9003-family baseband, radio, RX gain, TX gain, XLNA, DFS, Japan-channel, and fast-clock support. `ar9003_hw.c` installs these for `AR_SREV_9561()`.

Important APIs and data: Local arrays include `qca956x_1p0_baseband_core`, `qca956x_1p0_baseband_postamble`, `qca956x_1p0_radio_core`, `qca956x_1p0_radio_postamble`, `qca956x_1p0_baseband_core_txfir_coeff_japan_2484`, `qca956x_1p0_modes_no_xpa_tx_gain_table`, `qca956x_1p0_modes_xpa_tx_gain_table`, `qca956x_1p0_modes_no_xpa_low_ob_db_tx_gain_table`, `qca956x_1p0_modes_no_xpa_green_tx_gain_table`, `qca956x_1p0_common_rx_gain_table`, and `qca956x_1p0_xlna_only`. Macro aliases reuse AR955x MAC/SOC/gain-bound definitions, AR9331 MAC postamble, AR9300 no-XLNA RX gain and DFS tables, and AR9462 fast-clock tables.

Control flow: The AR9561 init branch assigns MAC, baseband, radio, SOC, no-XLNA RX gain, RX gain bounds, default no-XPA TX gain, DFS, Japan CCK FIR, and fast-clock tables. TX gain helper modes can replace the default with XPA, low-OB/DB, or green TX gain tables. RX gain mode 0 can select `qca956x_1p0_common_rx_gain_table` plus `qca956x_1p0_xlna_only`, while mode 1 uses the no-XLNA alias.

State and persistence: The header contributes immutable register tables only. Runtime effects are hardware register programming and `struct ath_hw` INI pointer selection during resets and channel changes.

Dependencies and integration points: Integrated with AR9003 reset, DFS-channel setup, Japan 2484 MHz channel support, EEPROM gain decisions, QCA9561 SoC revision detection, and shared AR9300/AR9331/AR9462/AR955x tables. The XLNA-only table is an integration point for boards with external LNA-specific receive-chain behavior.

Risks: Many definitions are cross-chip aliases, so validating QCA956x changes requires checking AR955x, AR9331, AR9300, and AR9462 assumptions. TX gain tables use three columns rather than the wider AR955x/AR9580 format, so incorrect table metadata can program wrong modal values. DFS and Japan-channel table mistakes can cause regulatory or interoperability failures. XLNA selection is board-specific and can degrade sensitivity if applied incorrectly.

Test signals: Boot QCA9561 boards with no-XPA and XPA front ends, test scan/association/throughput, verify DFS-channel register programming, test channel 14/Japan CCK behavior when supported, exercise RX gain mode switching including XLNA-only path, and check calibration/noise-floor stability after reset.
