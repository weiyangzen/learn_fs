# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/debugfs.c

Purpose: Debugfs, relay logging, diagnostics, and test controls for MT7915 PHYs and stations.

Important APIs: `mt7915_init_debugfs`, `mt7915_debugfs_rx_fw_monitor`, `mt7915_debugfs_rx_log`, and `mt7915_sta_add_debugfs`. File operations cover implicit TXBF, system error recovery, radar trigger, MURU stats/debug, firmware WM/WA/bin logging, firmware CPU utilization, hardware queues, TX stats, txpower SKU/path, TWT stats, RF register access, and per-station fixed rate/queues.

Control flow: init registers per-phy debugfs files, saving the main phy directory for relay logging. Firmware debug setters program MCU log routing and open/reset a relay channel for binary logs. SER debugfs writes can query recovery, enable and trigger L1/L2/L3 recovery, request full reset, or intentionally assert firmware. Read paths format register/MIB state through seq_file or simple buffers. Per-station debugfs can translate user rate tuples into MCU fixed-rate controls.

State and persistence: runtime knobs mutate `dev->ibf`, `dev->muru_debug`, `dev->fw.debug_*`, relay channel state, txpower tables, recovery counters, and per-station fixed-rate state. Most data is volatile hardware/firmware state exposed for diagnostics.

Dependencies and integration: depends on debugfs, relayfs, mac80211 debugfs, mt7915 MCU commands, MAC stats, EEPROM SKU lengths, DFS/RDD helpers, and register access.

Risks: debugfs write knobs are privileged but powerful: firmware crash, full reset, RF writes, txpower override, and fixed rates can disrupt operation or regulatory behavior. Formatting code must avoid buffer overflow; relay logging needs synchronization, handled by a static spinlock. Many reads assume hardware is responsive.

Test signals: debugfs file creation for main/ext PHY, enable/disable firmware logs, relay data capture, SER trigger paths, txpower read/write validation, MURU stats after enabling, radar trigger error paths, fixed-rate input parsing, and cleanup on device removal.
