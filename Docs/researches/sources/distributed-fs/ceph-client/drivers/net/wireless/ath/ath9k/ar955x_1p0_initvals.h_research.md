# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar955x_1p0_initvals.h

Purpose: Supplies AR955x 1.0 SoC WLAN initialization tables for AR9003-family MAC, baseband, radio, SOC, RX gain bounds, TX gain, and fast-clock programming. `ar9003_hw.c` installs these tables for `AR_SREV_9550()` devices.

Important APIs and data: Defines `ar955x_1p0_radio_postamble`, `ar955x_1p0_baseband_postamble`, `ar955x_1p0_radio_core`, `ar955x_1p0_modes_xpa_tx_gain_table`, `ar955x_1p0_mac_core`, `ar955x_1p0_baseband_core`, `ar955x_1p0_soc_preamble`, `ar955x_1p0_common_wo_xlna_rx_gain_bounds`, `ar955x_1p0_mac_postamble`, `ar955x_1p0_common_rx_gain_bounds`, `ar955x_1p0_modes_no_xpa_tx_gain_table`, and `ar955x_1p0_modes_fast_clock`. Macro aliases reuse AR9300 2.2 SOC postamble, common RX gain tables, no-XLNA RX gain tables, and Japan 2484 MHz CCK FIR coefficients.

Control flow: The file is declarative. The AR9550 initialization branch assigns these arrays into `ah->iniMac`, `ah->iniBB`, `ah->iniRadio`, `ah->iniSOC`, `ah->iniModesRxGain`, `ah->ini_modes_rx_gain_bounds`, `ah->iniModesTxGain`, and `ah->iniModesFastClock`. Gain override helpers later switch between XPA and no-XPA TX tables and between common and no-XLNA RX tables based on hardware configuration.

State and persistence: The arrays are read-only driver data. They become active by being referenced from `struct ath_hw` and then written into device registers during hardware reset/channel setup. No filesystem or NVRAM persistence is handled here.

Dependencies and integration points: Integrated with AR9003 init sequencing, EEPROM/board data that determines XPA and XLNA behavior, fast-clock mode programming, and shared AR9300 tables. AR955x tables are also reused by QCA953x/QCA956x headers through macro aliases for SOC and gain-bound data.

Risks: AR955x is an SoC target, so bad init values can affect integrated radio/MAC operation before higher-level mac80211 symptoms are obvious. The TX gain arrays use nine columns, unlike narrower QCA953x/QCA956x tables, so consumers must use the correct array metadata. Shared aliases mean edits may affect descendant chip headers. RX gain bounds must remain synchronized with the selected RX gain table.

Test signals: Validate AR9550 reset, scan, association, 20/40 MHz operation, fast-clock behavior, XPA/no-XPA boards, external-LNA and no-XLNA receive paths, throughput under calibration load, and no regressions in QCA953x/QCA956x table selection that aliases AR955x definitions.
