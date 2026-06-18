# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/debugfs.c

## Purpose
Implements ath12k debugfs controls and diagnostics for SOC, pdev/radio, vif link, firmware stats, TPC power tables, extended RX stats, DP device stats, radar simulation, and firmware crash simulation.

## Important APIs, Types, And Functions
Exports `ath12k_debugfs_soc_create()`, `ath12k_debugfs_soc_destroy()`, `ath12k_debugfs_pdev_create()`, `ath12k_debugfs_register()`, `ath12k_debugfs_unregister()`, and `ath12k_debugfs_op_vif_add()`. Internal file operations cover `simulate_fw_crash`, `dfs_simulate_radar`, `tpc_stats`, `tpc_stats_type`, `ext_rx_stats`, `link_stats`, `device_dp_stats`, and firmware stats files for vdev/beacon/pdev. TPC helpers map preambles, modes, rate codes, and firmware arrays into printable per-chain power limits.

## Control Flow
SOC creation creates `/sys/kernel/debug/ath12k/<bus-dev>`. Pdev creation adds SOC-level crash simulation and DP stats. Radio registration creates `macN`, symlinks from mac80211 debugfs, optional radar simulation, TPC files, HTT stats, firmware stats, and extended RX stats. Read-open operations usually allocate a buffer, lock wiphy when needed, request firmware stats or TPC data over WMI, wait for completions, render text, and free data on release. Writes validate user input and send WMI commands or HTT filter updates.

## State And Persistence
Uses `ar->debug` for dentries, TPC type/request/completion/stats, RX filter, and extended RX stats enabled state. Firmware stats lists in `ar->fw_stats` are initialized for debugfs and reset after dumping. Link stats are copied under per-link spinlock. Debugfs dentries persist until unregister/destroy.

## Dependencies And Integration Points
Depends on mac80211 debugfs/wiphy locking, WMI commands/events, DP TX HTT RX filter setup, HTT debug stats registration, firmware stats dumping, core hardware state, pdev/radio capabilities, RCU pdev lookups, and Linux debugfs/file APIs.

## Risks
Debugfs operations can trigger firmware actions, including crash simulation, radar simulation, stats requests, and RX filter changes; permissions mitigate but do not remove operational risk. TPC formatting uses a fixed large buffer and complex firmware-provided arrays, so bounds and received TLV flags matter. Several reads require hardware state `ON`; races with recovery must be covered by wiphy/core state locking. Extended RX stats changes monitor filters and can affect datapath volume/performance.

## Test Signals
Mount debugfs and verify SOC/radio symlinks, firmware stats reads while interfaces are up/down, TPC timeout behavior, ext_rx_stats toggling, DP stats content, radar simulation on 5 GHz-capable radios, and firmware assert recovery through `simulate_fw_crash`. KASAN/lockdep help validate open/release and recovery races.
