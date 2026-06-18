# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/debug.h

Purpose: Defines ath9k debugfs/statistics structures, reset reason enum, counter macros, debug API prototypes, and no-op stubs for feature-disabled builds.

Important APIs/types: `enum ath_reset_type` names reset causes. Counter macros `TX_STAT_INC`, `RX_STAT_INC`, `RESET_STAT_INC`, `ANT_STAT_INC`, and `ANT_LNA_INC` update stats when debugfs is enabled. `struct ath_interrupt_stats`, `ath_tx_stats`, `ath_rx_rate_stats`, `ath_airtime_stats`, `ath_antenna_stats`, `ath_stats`, and `ath9k_debug` define the persistent debug state. Function prototypes cover debug init/deinit, IRQ/TX/RX/antenna/sync stats, ethtool stats, and per-station debugfs.

Control flow: Runtime paths increment stats through macros and helper functions. Debugfs init exposes those stats; ethtool callbacks serialize a subset. Station statistics are separately gated by `CONFIG_ATH9K_STATION_STATISTICS`.

State/persistence: `struct ath9k_debug` is embedded in `ath_softc` and persists the debugfs dentry, selected register index, and stats for the device lifetime. All counters are `u32` except ethtool exports as `u64`.

Dependencies/integration: Includes `hw.h` and `dfs_debug.h`; used widely by TX, RX, reset, IRQ, antenna diversity, DFS, and station code.

Risks: Counter macros compile to no-ops without debugfs, so code must not depend on side effects. Reset enum ordering must match `debug.c` display arrays. Per-queue stats index by hardware queue number and assume mapped queues exist.

Test signals: Compile with debugfs and station statistics enabled/disabled, reset cause display coverage, ethtool stat count matches string table, and no side-effect dependencies on stat macros.
