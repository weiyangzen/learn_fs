# Research: subset-b-004767

Grouped source research for AR9003 ath9k initval headers. Each section is source-tree aligned and intended for deterministic splitting into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9330_1p1_initvals.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9330_1p1_initvals.h

Purpose: Provides the AR9331/AR9330 1.1 silicon revision initialization tables used by ath9k's AR9003 hardware path. The file is a guarded data header, not an implementation unit: it exposes `static const u32` register/value matrices and two alias macros so `ar9003_hw.c` can seed the `struct ath_hw` INI arrays for MAC, baseband, radio, SoC, crystal, RX gain, TX gain, and Japan 2484 MHz CCK FIR handling.

Important APIs/types/functions: There are no functions or exported C types in this file. The important data symbols are `ar9331_1p1_mac_core`, `ar9331_1p1_mac_postamble`, `ar9331_1p1_baseband_core`, `ar9331_1p1_baseband_postamble`, `ar9331_1p1_radio_core`, `ar9331_1p1_soc_preamble`, `ar9331_1p1_soc_postamble`, `ar9331_1p1_xtal_25M`, `ar9331_1p1_xtal_40M`, `ar9331_common_rx_gain_1p1`, `ar9331_common_wo_xlna_rx_gain_1p1`, and the TX gain tables `ar9331_modes_lowest_ob_db_tx_gain_1p1`, `ar9331_modes_high_ob_db_tx_gain_1p1`, and `ar9331_modes_low_ob_db_tx_gain_1p1`. The macros map `ar9331_1p1_baseband_core_txfir_coeff_japan_2484` to the shared AR9300 2.2 table and map high-power TX gain to the lowest-ob/db table.

Control flow: This header is pulled into `ar9003_hw.c`, where `ar9003_hw_init_mode_regs()` selects it under `AR_SREV_9330_11(ah)` and installs its arrays with `INIT_INI_ARRAY`. Later, `ar9003_hw_process_ini()` programs the selected arrays in split order: SoC, MAC, baseband, radio, RX gain, TX gain, optional fast-clock/additional clocks, and Japan CCK FIR. The modal five-column tables are consumed with a `modesIndex` derived from 5 GHz/2 GHz and HT20/HT40 channel state; two-column tables are forced to column 1 by `ar9003_hw_prog_ini()` when the selected modal column is out of range. `ar9003_tx_gain_table_apply()` can replace the default TX table with the high or low ob/db variants based on the runtime TX gain index, and `ar9003_rx_gain_table_apply()` can switch between normal and no-XLNA RX gain tables.

State and persistence behavior: The header owns no mutable state and performs no persistence. Its arrays become runtime pointers in `struct ath_hw` fields such as `iniMac`, `iniBB`, `iniRadio`, `iniSOC`, `iniModesRxGain`, `iniModesTxGain`, `iniAdditional`, and `iniCckfirJapan2484`. Persistence is hardware-facing only: once `REG_WRITE_ARRAY()` and `ar9003_hw_prog_ini()` write the tables, the register state remains in the device until reset, channel reprogramming, sleep transitions, or another INI sequence changes it.

Dependencies: Depends on inclusion after ath9k definitions that provide `u32`, `ARRAY_SIZE`, `struct ar5416IniArray`, and `INIT_INI_ARRAY`. It also depends on shared AR9300 2.2 init symbols for the Japan CCK FIR alias. Integration is entirely through `ar9003_hw.c`, `ar9003_phy.c`, and `hw.c` helpers that flatten the static arrays into register writes.

Integration points: The 1.1 revision branch uses these tables when probing or resetting AR9330/AR9331 devices. The crystal tables are selected by `ah->is_clk_25mhz`; the gain tables are selected by EEPROM/config-derived TX/RX gain indexes; and the Japan FIR table is only programmed when the channel is 2484 MHz. The table dimensions matter because `INIT_INI_ARRAY` records rows and columns directly from the C array shape.

Risks: This file encodes a hardware ABI as raw register constants. A wrong address, value, row order, or column count can break bring-up, calibration, channel changes, regulatory behavior, receive sensitivity, transmit power, or sleep/clock stability without producing compile-time errors. The modal-table layout is especially fragile: the first column is a register address and subsequent columns correspond to mode indexes used by `ar9003_hw_process_ini()`. The 1.1 high-power alias means callers requesting mode 3 receive the lowest-ob/db table, which is intentional but easy to misread as a missing high-power table.

Test signals: Build coverage should compile `ar9003_hw.c` with this header included and catch missing aliases. Runtime signals are successful AR9330 1.1 probe/reset, register programming without `WARN_ON` or failed reset, operation on both 25 MHz and 40 MHz crystal boards, 2 GHz HT20/HT40 association and traffic, RX gain index 0 and 1 behavior, TX gain modes 0 through 3 where supported, and channel 2484 CCK operation. RF validation should watch calibration stability, noise floor, rate control, EVM/TX power, and receive sensitivity after table edits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9330_1p1_initvals.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9340_initvals.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9340_initvals.h

Purpose: Supplies AR9340 1.0 initialization data for ath9k's AR9003-family hardware path. It covers MAC, baseband, radio, SoC preamble, 40 MHz reference-clock radio adjustments, multiple TX gain profiles, and aliases to shared AR9300 2.2 postamble, fast clock, RX gain, Japan FIR, and DFS channel tables.

Important APIs/types/functions: No functions or types are defined. Key data symbols include `ar9340_1p0_mac_core`, `ar9340_1p0_baseband_core`, `ar9340_1p0_baseband_postamble`, `ar9340_1p0_radio_core`, `ar9340_1p0_radio_postamble`, `ar9340_1p0_radio_core_40M`, `ar9340_1p0_soc_preamble`, `ar9340Modes_lowest_ob_db_tx_gain_table_1p0`, `ar9340Modes_high_power_tx_gain_table_1p0`, `ar9340Modes_high_ob_db_tx_gain_table_1p0`, `ar9340Modes_low_ob_db_tx_gain_table_1p0`, `ar9340Modes_mixed_ob_db_tx_gain_table_1p0`, `ar9340Modes_low_ob_db_and_spur_tx_gain_table_1p0`, and `ar9340_cus227_tx_gain_table_1p0`. Macros alias the MAC postamble, SoC postamble, fast-clock table, RX gain and no-XLNA RX gain tables, Japan CCK FIR table, and DFS postamble table to shared AR9300 2.2 data.

Control flow: `ar9003_hw_init_mode_regs()` selects these tables when `AR_SREV_9340(ah)` is true. It installs core/post split arrays for MAC, baseband, radio, and SoC, selects the no-XLNA RX gain table by default, chooses high-ob/db TX gain by default, installs fast clock, Japan FIR, and DFS tables, and installs `ar9340_1p0_radio_core_40M` as `iniAdditional` when the board is not using a 25 MHz clock. `ar9003_tx_gain_table_apply()` can later select TX gain modes 0 through 7 for AR9340, including mixed, low-ob/db-spur, and CUS227 profiles. `ar9003_rx_gain_table_apply()` can select shared normal or no-XLNA RX gain profiles.

State and persistence behavior: The header has no runtime state. Its static arrays become `struct ath_hw` INI pointers and are written into device registers by `ar9003_hw_process_ini()`, `REG_WRITE_ARRAY()`, and `ar9003_hw_prog_ini()`. Hardware state persists until reset, sleep/channel reprogramming, or a later table write.

Dependencies: Depends on the shared AR9300 2.2 init header for aliased MAC/SoC postambles, fast-clock settings, RX gain tables, Japan FIR, and DFS channel values. It also depends on ath9k channel-mode indexing where modal tables use register plus 5 GHz HT20, 5 GHz HT40, 2 GHz HT40, and 2 GHz HT20 value columns.

Integration points: The file feeds AR9340-specific branches in initial mode setup, TX gain mode selection, RX gain mode selection, fast-clock programming for 5 GHz channels, DFS channel handling, and optional radio-core changes for 40 MHz clock designs. The `ar9340_cus227_tx_gain_table_1p0` table is only reached through TX gain mode 7, making it a board/customer-specific integration path.

Risks: AR9340 has a broad TX gain surface in this file; selecting the wrong gain mode can alter regulatory power, spur behavior, or board-specific calibration. The shared aliases mean edits in AR9300 2.2 tables can affect AR9340 even though this header looks self-contained. The conditional 40 MHz clock table is a small but critical path; incorrect values can create clock-dependent failures that do not reproduce on 25 MHz boards.

Test signals: Build should verify all shared aliases resolve. Runtime validation should include AR9340 probe/reset, 25 MHz and 40 MHz reference boards, 2 GHz and 5 GHz HT20/HT40 channels, fast-clock channels, DFS channel setup, TX gain modes 0 through 7 where board data selects them, RX gain mode 0 versus 1, and Japan channel 2484. RF lab checks should watch spur masks, per-chain transmit power, receive sensitivity, calibration completion, and stability across channel changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9340_initvals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9462_2p0_initvals.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9462_2p0_initvals.h

Purpose: Provides AR9462 2.0 initialization data, including dual-band modal tables, PCIe low-power settings, system-to-antenna radio postamble values, normal/mixed/5G-XLNA RX gain handling, and multiple TX gain profiles. This is a full data source for the first AR9462 2.x branch used by ath9k.

Important APIs/types/functions: There are no functions or types. Major symbols are `ar9462_2p0_mac_core`, `ar9462_2p0_baseband_core`, `ar9462_2p0_baseband_postamble`, `ar9462_2p0_radio_core`, `ar9462_2p0_radio_postamble`, `ar9462_2p0_radio_postamble_sys2ant`, `ar9462_2p0_soc_preamble`, `ar9462_2p0_soc_postamble`, `ar9462_2p0_modes_fast_clock`, `ar9462_2p0_pciephy_clkreq_disable_L1`, `ar9462_2p0_common_rx_gain`, `ar9462_2p0_common_mixed_rx_gain`, `ar9462_2p0_baseband_core_mix_rxgain`, `ar9462_2p0_baseband_postamble_mix_rxgain`, `ar9462_2p0_baseband_postamble_5g_xlna`, `ar9462_2p0_modes_low_ob_db_tx_gain`, `ar9462_2p0_modes_high_ob_db_tx_gain`, and `ar9462_2p0_modes_mix_ob_db_tx_gain`. Macros alias the MAC postamble to the AR9331 1.1 table, no-XLNA RX gain to the AR9300 2.2 table, 5G-XLNA-only RX gain to the mixed RX table, and Japan FIR to the AR9300 2.2 table.

Control flow: `ar9003_hw_init_mode_regs()` selects this file for `AR_SREV_9462_20(ah)`. It installs MAC, baseband, radio, system-to-antenna, SoC, RX gain, PCIe SerDes, fast-clock, and Japan FIR arrays. PCIe low-power arrays are only installed when `ah->config.pll_pwrsave` requests the D3 or D0 transition settings. `ar9003_tx_gain_table_apply()` selects low, high, or mixed ob/db TX profiles for AR9462 2.0. `ar9003_rx_gain_table_apply()` can select normal, no-XLNA, mixed LNA, or 5G-XLNA-only behavior; mixed and XLNA modes also install extra baseband core/postamble or XLNA postamble arrays that `ar9003_hw_process_ini()` writes only on AR9462 2.0-or-later hardware.

State and persistence behavior: Static arrays are immutable, but they configure a large amount of runtime hardware state when copied into `struct ath_hw` INI slots. PCIe SerDes tables affect sleep and wake transitions when PLL power-save flags are enabled. Mixed/XLNA RX tables affect additional `ath_hw` slots (`ini_modes_rxgain_bb_core`, `ini_modes_rxgain_bb_postamble`, and `ini_modes_rxgain_xlna`) beyond the common `iniModesRxGain` path.

Dependencies: Depends on shared AR9331 and AR9300 2.2 tables for aliased postamble, no-XLNA, and Japan FIR behavior. It integrates with revision checks and gain-index helpers in `ar9003_hw.c`, programming helpers in `ar9003_phy.c`, and PCIe power-save handling in the AR9003 hardware code. Modal table width must match the AR9003 mode-index contract.

Integration points: AR9462 2.0 is integrated more deeply than the AR9330/AR9340 headers because it has extra radio-post-system-to-antenna writes, PCIe SerDes power-save arrays, fast-clock settings, and multi-step RX gain overrides. These arrays are used during reset/channel programming and during sleep/awake SerDes programming through `ar9003_hw_configpcipowersave()`.

Risks: The RX gain path has coupled tables: selecting mixed LNA without the matching baseband core/postamble and XLNA postamble writes can produce subtle sensitivity or 5 GHz failures. The 5G-XLNA-only alias to the mixed table is intentional but easy to misinterpret. PCIe low-power settings are gated by flags, so regressions may only appear in suspend/resume, D0/D3, or L1 clock-request scenarios. Modal columns and row ordering are hardware-sensitive across both bands.

Test signals: Compile coverage should catch missing shared aliases. Runtime validation should include AR9462 2.0 probe/reset, 2 GHz and 5 GHz HT20/HT40 channels, fast-clock channels, TX gain modes 0, 1, and 4, RX gain modes 0 through 3 including mixed LNA and 5G-XLNA-only paths, PCIe PLL power-save D0 and D3 transitions, system-to-antenna radio postamble programming, Japan 2484 CCK behavior, and suspend/resume stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9462_2p0_initvals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9462_2p1_initvals.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9462_2p1_initvals.h

Purpose: Provides the AR9462 2.1 revision delta tables. It reuses most AR9462 2.0 initialization data through macros and replaces only the MAC core, baseband postamble, and SoC preamble arrays needed for the later revision.

Important APIs/types/functions: This file defines no functions or types. Its direct data exports are `ar9462_2p1_mac_core`, `ar9462_2p1_baseband_postamble`, and `ar9462_2p1_soc_preamble`. Macro aliases map the 2.1 names for MAC postamble, baseband core, radio core/postamble, SoC postamble, radio system-to-antenna postamble, normal/mixed/no-XLNA/5G-XLNA RX gain tables, mixed RX gain auxiliary baseband tables, low/high/mixed TX gain tables, fast-clock table, Japan FIR, and PCIe clock-request table to their AR9462 2.0 equivalents.

Control flow: `ar9003_hw_init_mode_regs()` selects this header when `AR_SREV_9462_21(ah)` is true. The flow mirrors AR9462 2.0 but resolves many selected symbols to 2.0 arrays at compile time. Runtime TX gain modes 0, 1, and 4 and RX gain modes 0 through 3 use the same helper paths as 2.0, with aliases supplying the table bodies. The 2.1-specific `ar9462_2p1_baseband_postamble` and `ar9462_2p1_soc_preamble` are written during normal AR9003 split INI programming.

State and persistence behavior: The header stores immutable register matrices only. Runtime state is the `struct ath_hw` INI pointers set in `ar9003_hw.c` and the resulting hardware register state after `ar9003_hw_process_ini()` writes them. Because most symbols alias to 2.0, a 2.0 table change can persist into 2.1 hardware behavior without edits to this file.

Dependencies: Strongly depends on `ar9462_2p0_initvals.h` being included in the same translation unit before these aliases are used. It also depends on the AR9003 programming path for mixed/XLNA RX gain auxiliary arrays and PCIe PLL power-save arrays, even though those arrays physically live in the 2.0 header.

Integration points: This file is the revision-selection layer for AR9462 2.1. It plugs into the same MAC/baseband/radio/SoC, RX gain, TX gain, fast-clock, Japan FIR, system-to-antenna, and PCIe power-save integration points as 2.0 while overriding only the tables required by the 2.1 silicon revision.

Risks: The heavy aliasing makes dependency ordering and review clarity the main risks. A reader may assume a 2.1 symbol is locally defined when it actually expands to 2.0 data, and changes to `ar9462_2p0_initvals.h` can alter 2.1 behavior. The small number of local override tables must still preserve exact modal column layout; a mismatch in `ar9462_2p1_baseband_postamble` would affect all mode-specific PHY programming for this revision.

Test signals: Build validation should catch missing 2.0 aliases. Runtime validation should cover AR9462 2.1 probe/reset, both bands and HT widths, fast-clock channels, TX gain modes inherited from 2.0, RX gain modes 0 through 3 including mixed and XLNA auxiliary writes, PCIe PLL power-save D0/D3 paths, and comparison against AR9462 2.0 behavior to confirm that only intended revision deltas changed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9462_2p1_initvals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9485_initvals.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9485_initvals.h

Purpose: Provides AR9485 1.1-or-later initialization tables for ath9k. It covers pre/core/post baseband setup, MAC and radio core/postamble, SoC preamble, normal and no-XLNA RX gain tables, five TX gain profiles, and PCIe SerDes settings for clock-request/L1 power-save behavior.

Important APIs/types/functions: The header defines no functions or types. Important symbols include `ar9485_1_1`, `ar9485_1_1_mac_core`, `ar9485_1_1_baseband_core`, `ar9485_1_1_baseband_postamble`, `ar9485_1_1_radio_core`, `ar9485_1_1_radio_postamble`, `ar9485_1_1_soc_preamble`, `ar9485_common_rx_gain_1_1`, `ar9485Common_wo_xlna_rx_gain_1_1`, `ar9485Modes_high_power_tx_gain_1_1`, `ar9485Modes_green_ob_db_tx_gain_1_1`, `ar9485Modes_high_ob_db_tx_gain_1_1`, `ar9485Modes_low_ob_db_tx_gain_1_1`, `ar9485Modes_green_spur_ob_db_tx_gain_1_1`, `ar9485_1_1_pcie_phy_clkreq_disable_L1`, and `ar9485_1_1_pll_on_cdr_on_clkreq_disable_L1`. Macros alias the lowest-ob/db TX gain name to the low-ob/db table, the MAC postamble to the AR9331 1.1 MAC postamble, and the Japan FIR table to the AR9300 2.2 table.

Control flow: `ar9003_hw_init_mode_regs()` selects this header under `AR_SREV_9485_11_OR_LATER(ah)`. It installs a baseband preamble table (`ar9485_1_1`) in addition to the usual MAC, baseband, radio, SoC, RX gain, TX gain, and Japan FIR arrays. It selects no-XLNA RX gain and lowest/low-ob/db TX gain by default. TX gain apply modes can select low, high, high-power, green, or green-spur profiles. RX gain apply can switch between normal and no-XLNA tables. PCIe SerDes arrays are selected from either the PLL-on/CDR-on table or the phy-clock-request table depending on `ah->config.pll_pwrsave & AR_PCIE_PLL_PWRSAVE_CONTROL`.

State and persistence behavior: The file has no mutable state. It contributes static arrays to `struct ath_hw` INI pointers and PCIe SerDes slots, which then become device register writes during reset/channel programming and PCIe power-save setup. The baseband pre table means AR9485 uses the AR9003 split INI path slightly differently from chips that only fill baseband core/post slots.

Dependencies: Depends on AR9331 1.1 and AR9300 2.2 init symbols for aliases, plus ath9k's `INIT_INI_ARRAY`, `REG_WRITE_ARRAY`, and `ar9003_hw_prog_ini` machinery. Integration relies on AR9485 revision macros and PLL power-save flags in `ar9003_hw.c`.

Integration points: These tables are used for AR9485 1.1-or-newer devices during mode register initialization, channel programming, optional Japan 2484 handling, RX/TX gain profile selection, and PCIe SerDes power-save programming. The `ar9485_1_1_pcie_phy_clkreq_disable_L1` and `ar9485_1_1_pll_on_cdr_on_clkreq_disable_L1` arrays feed both awake and low-power SerDes slots depending on configuration.

Risks: AR9485 combines multiple board-policy gain profiles with PCIe power management settings, so changes can regress RF behavior or platform sleep stability independently. The low/lowest TX gain alias is intentional but can hide the fact that mode 0 and mode 2 may share data. The MAC postamble alias means AR9331 changes can affect AR9485. Incorrect modal values in the green or green-spur tables can create regulatory or spur-mask failures that may not appear in ordinary connectivity tests.

Test signals: Build coverage should catch missing alias dependencies. Runtime validation should include AR9485 probe/reset, 2 GHz and any supported 5 GHz/HT modal paths as applicable to the chip, TX gain modes 0, 1, 2, 3, 5, and 6, RX gain modes 0 and 1, PCIe PLL power-save enabled and disabled cases, suspend/resume or L1 clock-request behavior, Japan 2484 CCK programming through the shared FIR table, and RF measurements for green/green-spur power profiles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9485_initvals.h -->
