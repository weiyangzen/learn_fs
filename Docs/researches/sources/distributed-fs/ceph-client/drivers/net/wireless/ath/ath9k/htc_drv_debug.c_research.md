# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_drv_debug.c

Purpose: Provides ath9k_htc debugfs files and ethtool statistics for target interrupt/TX/RX stats, host TX/RX SKB counters, TX slot/queue state, debug mask control, spectral debug setup, and EEPROM debug exposure.

Important APIs and functions: Debugfs read handlers include `read_file_tgt_int_stats()`, `read_file_tgt_tx_stats()`, `read_file_tgt_rx_stats()`, `read_file_xmit()`, `read_file_skb_rx()`, `read_file_slot()`, `read_file_queue()`, and `read_file_debug()`, with `write_file_debug()` updating the common debug mask. Exported functions are `ath9k_htc_err_stat_rx()`, `ath9k_htc_get_et_strings()`, `ath9k_htc_get_et_sset_count()`, `ath9k_htc_get_et_stats()`, `ath9k_htc_init_debug()`, and `ath9k_htc_deinit_debug()`.

Control flow: Init creates a driver debugfs directory under the wiphy, initializes spectral debug, creates stats/control files, and registers common RX PHY error and EEPROM dump nodes. Target stats readers wake the device from HTC power save, send WMI stat commands, restore power state, and format big-endian firmware counters. Host stats readers sample local counters and queues, with TX slot reading protected by `tx_lock`. Ethtool callbacks copy static stat names and fill values from debug counters.

State and persistence: Debug counters live in `priv->debug`; debugfs dentries are runtime filesystem state; `common->debug_mask` persists only for the loaded driver instance. There is no durable persistence.

Dependencies and integration points: Depends on debugfs, ethtool stats ABI, WMI commands, HTC power-save helpers, common ath9k debug/stat helpers, spectral debug support, EEPROM dump helpers, and TX/RX stat macros used by USB/TX/RX code.

Risks: WMI target stats reads depend on firmware response behavior while power state is temporarily forced awake. Some queue readers sample lockless SKB queue lengths. Debugfs creation return values are not treated as fatal. Stat ordering must stay aligned between string names and `ath9k_htc_get_et_stats()`.

Test signals: Mount/read each debugfs node, write debug mask, collect ethtool stats and verify string/value count, query target stats during active traffic and power save, inspect TX slot bitmap under load, and deinit debugfs on disconnect.
