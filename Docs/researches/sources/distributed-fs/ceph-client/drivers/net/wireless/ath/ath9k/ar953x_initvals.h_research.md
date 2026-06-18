# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar953x_initvals.h

Purpose: Provides QCA953x AR9003-family hardware initialization arrays for MAC, baseband, radio, RX gain, TX gain, and modal/postamble programming. These tables are selected by `ar9003_hw.c` for `AR_SREV_9531()` hardware during reset and channel bring-up.

Important APIs and data: The file exports static `u32` init arrays such as `qca953x_1p0_mac_core`, `qca953x_1p0_baseband_core`, `qca953x_1p0_baseband_postamble`, `qca953x_1p0_radio_core`, `qca953x_1p0_radio_postamble`, revision-specific TX gain tables for 1.0, 1.1, and 2.0 silicon, and 2.0-specific baseband/RX gain tables. Macro aliases reuse shared AR9300/AR955x tables for MAC postamble, SOC pre/postamble, common RX gain, no-XLNA gain, fast clock, and RX gain bounds.

Control flow: The header has no executable flow. Its arrays are consumed through `INIT_INI_ARRAY()` in `ar9003_hw_attach_ops()` and the AR9003 TX/RX gain selection helpers. The main hardware initialization branch chooses 1.0/1.1 versus 2.0 baseband and RX tables using `AR_SREV_9531_20()`, and chooses TX gain tables according to `AR_SREV_9531_10()`, `AR_SREV_9531_11()`, or `AR_SREV_9531_20()`. Later gain-mode overrides can replace `ah->iniModesTxGain` and `ah->iniModesRxGain` when EEPROM/configured gain indices request alternate tables.

State and persistence: The file owns immutable compile-time register data only. Runtime state is the `struct ath_hw` INI array pointers populated from these tables; hardware register state persists until the next reset, channel reprogramming, or power transition.

Dependencies and integration points: Depends on the common ath9k initval convention: two-column arrays for register/value programming and five-column arrays for modal values across operating modes. It integrates with `ar9003_hw.c`, `hw.c` reset/programming paths, EEPROM-derived TX/RX gain selection, regulatory/channel setup, and shared tables from `ar9003_2p2_initvals.h` and `ar955x_1p0_initvals.h`.

Risks: Register values are silicon-revision and board-design sensitive. Incorrect table selection for QCA9531 1.0, 1.1, or 2.0 can break RF bring-up, calibration, sensitivity, or TX power. Macro aliases hide dependencies on AR9300/AR955x data, so changing a shared table affects QCA953x. Column-count mismatches would corrupt modal programming. TX gain table selection is especially risky because XPA/no-XPA and low-power variants must match board front-end hardware.

Test signals: Boot QCA9531 1.0/1.1/2.0 boards, verify hardware reset completes, scan/associate on 2.4 GHz, exercise EEPROM TX gain indices, compare RSSI/noise floor with and without external LNA, run throughput and power measurements, test regulatory channel changes, and watch ath9k debug output for calibration, PLL, or stuck beacon/reset loops.
