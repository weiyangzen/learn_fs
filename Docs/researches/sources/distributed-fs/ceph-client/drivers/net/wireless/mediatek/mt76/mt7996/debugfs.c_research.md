# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/debugfs.c

## Purpose
This file implements MT7996 debugfs controls and diagnostics for firmware logging, SER recovery testing, radar emulation, queue state, TX/beamforming stats, TWT flows, RF register access, firmware relay logging, and per-station fixed-rate/queue debugfs.

## Important APIs, Types, And Functions
The main entry is `mt7996_init_debugfs()`. Other exported/visible hooks are `mt7996_debugfs_rx_fw_monitor()`, `mt7996_debugfs_rx_log()`, `mt7996_sta_add_debugfs()`, and `mt7996_link_sta_add_debugfs()`. Key controls include `implicit_txbf`, `sys_recovery`, `radar_trigger`, `fw_debug_wm`, `fw_debug_wa`, `fw_debug_bin`, `fw_util_wa`, `rf_regval`, and station `fixed_rate`.

## Control Flow
Initialization registers the mt76 debugfs directory and creates global files. `sys_recovery` parses `<band>,<val>` commands, queries or triggers firmware SER levels, full reset, or firmware assert. Firmware debug setters configure WM/WA logging and optional relay binary logging, with relay callbacks creating `fwlog_data`. Queue readers dump PLE/PSE pages, non-empty hardware queues, per-station AC queues across all phys, and software TX queues. TX stats refresh MIBs per PHY and print AMPDU, PER, beamforming, MU/SU, and AMSDU counters. Radar trigger validates DFS/channel/background state and sends RDD emulate commands. TWT stats walk an RCU list. RF reg access proxies through MCU. Per-station fixed rate parses a ten-field rate tuple, resolves link station WCID under mutex, and sends fixed-rate control.

## State And Persistence
The file mutates debug flags `fw_debug_wm`, `fw_debug_wa`, `fw_debug_bin`, relay channel state, `fw_debug_seq`, `dev->ibf`, recovery state for full reset, and fixed-rate firmware state. It reads queue registers, MIB stats, TWT list, RDD channel state, station link/WCID state, and firmware logs.

## Dependencies And Integration Points
It integrates debugfs, relayfs, mac80211 per-station debugfs, mt76 queue/debugfs helpers, MT7996 MCU commands, DFS/cfg80211 radar checks, recovery/reset, firmware log RX path, RCU station/link iteration, and optional `CONFIG_MAC80211_DEBUGFS`.

## Risks
Debugfs write handlers can trigger firmware crashes, SER, full reset, or fixed rates; they require privileged/debug use. Input parsing must reject malformed strings. Relay logging uses a spinlock and reserve/flush path that must be safe from RX context. Queue readers touch hardware while stations/links are RCU-protected. Fixed-rate control assumes link PHY and WCID are still valid.

## Test Signals
Debugfs file creation, SER query/trigger, firmware assert and coredump, relay log capture, queue dumps under traffic, TWT list output, radar emulation on DFS channels, RF register read/write, implicit TXBF toggle, and per-station fixed-rate programming validate this file.
