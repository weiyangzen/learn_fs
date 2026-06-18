<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9330_1p2_initvals.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9330_1p2_initvals.h

Purpose: Provides the AR9331/AR9330 1.2 revision-specific initialization tables. It is a smaller delta-style data header that reuses many 1.1 tables through macros while replacing the 1.2 TX gain, radio core, baseband core/postamble, and normal RX gain data.

Important APIs/types/functions: The file defines no functions or types. It exports `ar9331_modes_high_ob_db_tx_gain_1p2`, `ar9331_1p2_radio_core`, `ar9331_1p2_baseband_core`, `ar9331_1p2_baseband_postamble`, and `ar9331_common_rx_gain_1p2`. Macro aliases map high-power, low-ob/db, and lowest-ob/db TX gain names to the same 1.2 high-ob/db table; map the Japan FIR, 25 MHz and 40 MHz crystal tables, SoC pre/postamble, MAC core/postamble, and no-XLNA RX gain table back to the 1.1 definitions.

Control flow: `ar9003_hw_init_mode_regs()` selects this header under `AR_SREV_9330_12(ah)`. The selected arrays populate the same `struct ath_hw` INI slots as the 1.1 path, but many symbols resolve through preprocessor aliases to the 1.1 data. During channel programming, `ar9003_hw_process_ini()` writes the 1.2 baseband/radio/RX/TX tables and any aliased 1.1 tables in the normal AR9003 split sequence. Runtime TX gain modes 0, 1, 2, and 3 all resolve to 1.2 high-ob/db data through the aliases except where the mode function directly names the high-ob/db symbol.

State and persistence behavior: The file is immutable data. Its effect persists only as hardware register values after the ath9k init path writes them. The macro aliases are resolved at compile time, so there is no runtime distinction between an aliased 1.2 symbol and its 1.1 source table once the `ar5416IniArray` pointer is stored in `struct ath_hw`.

Dependencies: Depends on `ar9330_1p1_initvals.h` and `ar9003_2p2_initvals.h` being included in a context where the aliased source symbols exist before use. It also depends on the ath9k INI infrastructure in `calib.h`, `hw.h`, `ar9003_hw.c`, `ar9003_phy.c`, and `hw.c`.

Integration points: The 1.2 branch in `ar9003_hw.c` installs these arrays for AR9330 1.2 devices, selects the 25 MHz or 40 MHz crystal alias via `ah->is_clk_25mhz`, and lets RX/TX gain apply helpers swap tables based on EEPROM/config gain indexes. The normal RX gain table has 128 register/value rows; the radio/baseband tables carry the revision-specific RF and PHY setup.

Risks: Because this revision intentionally reuses many 1.1 tables, a local change in the 1.1 header can silently affect AR9330 1.2 behavior through aliases. The TX gain aliases collapse multiple gain modes to one table; changing only one visible name can create a false assumption that modes differ. As with all initvals, incorrect register literals or modal columns can cause hardware bring-up regressions that are only visible on real AR9330 1.2 boards.

Test signals: Build should validate that all aliased 1.1 symbols are available. Runtime validation should cover AR9330 1.2 reset/probe, 25 MHz and 40 MHz board variants, 2 GHz HT20/HT40 channels, TX gain mode selection despite shared aliases, RX gain mode 0 and no-XLNA mode 1, and 2484 MHz Japan CCK programming through the inherited table. Compare RF performance against the 1.1 path to catch accidental alias breakage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9330_1p2_initvals.h -->
