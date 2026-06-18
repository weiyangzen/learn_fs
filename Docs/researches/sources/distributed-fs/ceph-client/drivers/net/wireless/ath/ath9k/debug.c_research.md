# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/debug.c

Purpose: Implements ath9k debugfs and ethtool statistics, hardware register diagnostics, mutable debug knobs, and debug statistic accounting.

Important APIs/functions: External/stat APIs include `ath9k_debug_sync_cause()`, `ath9k_debug_stat_ant()`, `ath_debug_stat_interrupt()`, `ath_debug_stat_tx()`, `ath_debug_stat_rx()`, `ath9k_get_et_strings()`, `ath9k_get_et_sset_count()`, `ath9k_get_et_stats()`, `ath9k_deinit_debug()`, and `ath9k_init_debug()`. Debugfs operations cover `debug`, `ani`, `bt_ant_diversity`, `antenna_diversity`, `dma`, `interrupt`, `xmit`, `queues`, `misc`, `reset`, `regidx`, `regval`, `regdump`, `dump_nfcal`, `btcoex`, `ack_to`, `wow`, `tpc`, and `nf_override`.

Control flow: Init creates the `ath9k` debugfs directory under the wiphy, initializes DFS/tx99/spectral/common debug files, and registers per-feature files. Read paths format current driver or hardware state, often waking hardware before register access and restoring power state after. Write paths parse user input and mutate driver state: debug mask, ANI enable, BT antenna diversity, user reset, selected register index/value, WOW, TPC, and NF override. Ettool stats copy fixed names and fill totals plus per-AC TX and RX counters.

State/persistence: Debug stats live in `sc->debug.stats` and include interrupt, TX, RX, DFS, antenna, and reset counters. Debugfs mutable state includes `common->debug_mask`, `common->disable_ani`, `common->bt_ant_diversity`, `sc->debug.regidx`, `sc->force_wow`, `ah->tpc_enabled`, and `ah->nf_override`; register writes persist in hardware.

Dependencies/integration: Uses debugfs, seq_file, vmalloc, mac80211 wiphy debugfs, ath power-save helpers, reset work, tx/queue structures, common debug and spectral/DFS init, btcoex/tx99/WOW feature code, calibration NF history, and ethtool stats callbacks.

Risks: Debugfs is operationally powerful: arbitrary register write, forced reset, NF override, and TPC/ANI toggles can destabilize live hardware. Most counters are unsynchronized `u32`. `regdump` skips hard-coded register holes and allocates based on revision. User reset must avoid shutdown invalid state. NF override validates only non-positive values down to `-120`.

Test signals: Debugfs file presence under feature matrices, read/write validation errors, power-state wake/restore around register access, ethtool string/count alignment, reset write queuing, NF override immediate load, counter increments from IRQ/TX/RX paths, and debugfs teardown closing spectral relay.
