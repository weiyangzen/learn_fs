# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/dfs_debug.c

Purpose: Exposes DFS detector and pool statistics through debugfs and provides a debugfs trigger to simulate radar detection.

Important APIs/functions: `ath9k_dfs_init_debug()` creates `dfs_stats` and `dfs_simulate_radar`. `read_file_dfs()` formats hardware DFS support, detector availability, per-wiphy pulse stats, detector region, and global pool stats. `write_file_dfs()` resets per-device DFS stats only when a magic value is written. `write_file_simulate_radar()` calls `ieee80211_radar_detected()`.

Control flow: Debug init registers files under `sc->debug.debugfs_phy`. Reading stats pulls current pool stats from `sc->dfs_detector->get_stats()`. Writing `0x80000000` to `dfs_stats` clears `sc->debug.stats.dfs_stats`; other values are accepted but ignored. Writing any data to `dfs_simulate_radar` reports radar to mac80211.

State/persistence: Uses a file-static `dfs_pool_stats` snapshot and persistent `sc->debug.stats.dfs_stats`. Debugfs files hold `ath_softc` as private data.

Dependencies/integration: Depends on debugfs, DFS detector pool stats, mac80211 radar notification, `debug.h` stats, and build-time `CONFIG_ATH9K_DFS_DEBUGFS`.

Risks: Simulated radar is a powerful test hook that can trigger channel availability behavior. Stats reset uses a magic value to avoid accidental reset but has no locking. File-static pool stats are overwritten on reads.

Test signals: Debugfs presence, stats output with and without detector, magic reset behavior, simulated radar triggering cfg80211/mac80211 radar handling, and pool stat formatting.
