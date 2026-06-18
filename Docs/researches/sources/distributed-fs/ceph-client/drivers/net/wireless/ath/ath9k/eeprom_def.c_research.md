# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/eeprom_def.c

Purpose: Implements the default AR5416/AR9280-family EEPROM operations for dual-band devices with up to three chains, including 2 GHz and 5 GHz modal headers, ADDAC adjustment, PDADC calibration, regulatory TX power limiting, and board register setup.

Important APIs and functions: The exported ops table is `eep_def_ops`. Main callbacks are `ath9k_hw_def_fill_eeprom()`, `ath9k_hw_def_check_eeprom()`, `ath9k_hw_def_get_eeprom()`, `ath9k_hw_def_set_board_values()`, `ath9k_hw_def_set_addac()`, and `ath9k_hw_def_set_txpower()`. Calibration helpers include `ath9k_get_txgain_index()`, `ath9k_olc_get_pdadcs()`, `ath9k_hw_set_def_power_cal_table()`, `ath9k_hw_set_def_power_per_rate_table()`, `ath9k_change_gain_boundary_setting()`, and `ath9k_adjust_pdadc_values()`.

Control flow: Fill reads the default EEPROM image from offset `0x100`, with USB support through register multi-read. Check performs byte-swap conversion, checksum and version validation, AR9280 top2 fixup detection, and a USB AR9280 xpa bias workaround. Board setup chooses 2 GHz or 5 GHz modal data, writes antenna switch/IQ/gain/RF timing/CCA/analog bias registers, handles special chainmask offset mapping, and applies revision-gated DAC and CCK scale fields. TX power setup interpolates target powers for 2 GHz or 5 GHz, clamps by regulatory CTLs and chain scaling, writes PDADC tables, records max power, and programs rate power/TPC registers.

State and persistence: Persistent data is held in `ah->eeprom.def`. Runtime mutations include `ah->need_an_top2_fixup`, `ah->initPDADC`, regulatory max power, ADDAC ini table entries, PHY registers, and TPC state. Backing EEPROM is not modified.

Dependencies and integration points: Depends on common EEPROM helpers, AR9002 PHY registers, AR5416/AR9280 silicon revision macros, regulatory CTL definitions, chain masks, and common debugfs EEPROM dump helpers. It is the fallback ops table for pre-AR9300 devices not handled by 4K or AR9287 layouts.

Risks: This is the broadest layout and contains many revision gates; regressions can be band-, chain-, or silicon-specific. Open-loop control for AR9280 2.0 changes PDADC generation and CCK deltas. Chainmask `5` remapping changes register offsets. EEPROM minor-version gates protect fields that may be uninitialized on older boards.

Test signals: Boot AR5416/AR9160/AR9280 variants, test both 2 GHz and 5 GHz HT20/HT40 channels, chain masks 1/3/5/7, open-loop and closed-loop TX power, ADDAC xpa bias interpolation, endian swap/checksum failures, AR9280 USB workaround, and debugfs base/modal dumps.
