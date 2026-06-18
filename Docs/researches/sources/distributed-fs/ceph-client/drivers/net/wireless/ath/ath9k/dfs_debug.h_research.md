# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/dfs_debug.h

Purpose: Defines DFS debug statistics and conditional debugfs/stat increment hooks.

Important APIs/types: `struct ath_dfs_stats` records pulse totals, non-DFS pulse reports, detected pulses, datalen/RSSI/BW discards, primary/extension/dual-channel PHY errors, processed pulses, and radar detections. `DFS_STAT_INC(sc, c)` increments stats when `CONFIG_ATH9K_DFS_DEBUGFS` is enabled; otherwise it compiles to a no-op. `ath9k_dfs_init_debug()` is declared or stubbed similarly.

Control flow: `dfs.c` increments counters through `DFS_STAT_INC()` throughout the radar filtering pipeline. `debug.c` calls `ath9k_dfs_init_debug()` during debugfs setup.

State/persistence: Stats are embedded in `sc->debug.stats.dfs_stats`. No direct allocation or synchronization is defined here.

Dependencies/integration: Includes `hw.h`, forward-declares `ath_softc`, and references `ath_dfs_pool_stats` from the shared DFS detector.

Risks: Counter no-ops in disabled builds mean DFS logic cannot rely on side effects. Unsynchronized `u32` counters can race or wrap. External declaration of global pool stats must match detector implementation.

Test signals: Compile with/without DFS debugfs, per-counter increments from radar path, debugfs initialization stubbing, and stats reset/read behavior through `dfs_debug.c`.
