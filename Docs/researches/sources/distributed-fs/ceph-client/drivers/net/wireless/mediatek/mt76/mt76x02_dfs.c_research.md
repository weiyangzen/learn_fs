<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_dfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_dfs.c

Purpose: DFS radar detection implementation for MMIO mt76x02 devices. It configures region/bandwidth-specific hardware radar engines, collects hardware pulse reports and debug pulse events, runs a software pulse-sequence detector, and reports radar to mac80211.

Important APIs/types/functions: radar spec tables for ETSI/FCC/JP W53/W56, `mt76x02_dfs_init_detector()`, `mt76x02_dfs_init_params()`, `mt76x02_regd_notifier()`, `mt76x02_phy_dfs_adjust_agc()`, and the DFS tasklet.

Control flow: regulatory changes set the DFS domain under mutex, disable the tasklet, update EDCCA, program BBP DFS registers, enable GP timer interrupts, then re-enable. The tasklet skips scanning, periodically fetches event FIFO data into ring buffers, creates/extends PRI sequences, reports radar on sequence threshold, checks hardware engine status, validates pulse periods by region, and re-enables the GP timer IRQ.

State and persistence: `dev->dfs_pd` owns sequence lists, a pool, event ring buffers, stats, chirp counters, last timestamps, tasklet state, and software detector thresholds. Hardware DFS/IBI/AGC registers persist until channel/domain reset.

Dependencies/integration: mac80211 DFS state/`ieee80211_radar_detected()`, regulatory notifier, mt76 IRQ mask helpers, BBP register access, EDCCA initialization, and debugfs DFS stats.

Risks: false positives/negatives from region tables, timestamp wrap/reset, sequence pool accounting, tasklet/IRQ ordering, and scanning suppression. Test signals include region switch FCC/ETSI/JP, radar CAC channels, synthetic pulse patterns, debugfs stats increments, GP timer interrupt behavior, and no detection during scans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_dfs.c -->
