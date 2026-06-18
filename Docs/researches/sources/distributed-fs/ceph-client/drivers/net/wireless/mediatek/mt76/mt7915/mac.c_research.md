# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/mac.c

Purpose: Core MAC datapath, statistics, reset recovery, DFS radar, and TWT scheduling for MT7915-family devices.

Important APIs: `mt7915_mac_wtbl_update`, `mt7915_mac_wtbl_lmac_addr`, `mt7915_mac_write_txwi`, `mt7915_tx_prepare_skb`, `mt7915_wed_init_buf`, `mt7915_rx_check`, `mt7915_queue_rx_skb`, `mt7915_mac_cca_stats_reset`, `mt7915_mac_reset_counters`, `mt7915_mac_set_timing`, `mt7915_mac_enable_nf`, `mt7915_update_channel`, `mt7915_mac_reset_work`, `mt7915_mac_dump_work`, `mt7915_reset`, `mt7915_mac_update_stats`, `mt7915_mac_sta_rc_work`, `mt7915_mac_work`, `mt7915_dfs_init_radar_detector`, `mt7915_mac_add_twt_setup`, and `mt7915_mac_twt_teardown_flow`.

Control flow: RX dispatch separates txfree notifications, MCU events, RX vectors, TX status, firmware monitor logs, and normal frames. Normal RX parses RX descriptors, security flags, WCID, checksum, radiotap/rate vectors, A-MSDU state, header translation, PPE/WED metadata, and sequence/QoS fields before passing frames to mt76. TX preparation allocates tokens, writes connac TXWI, attaches firmware TXP buffers, and requests periodic TX status. Reset work handles full firmware crash recovery with coredump and restart, or partial DMA-stop recovery synchronized with MCU state bits. Periodic MAC work updates survey/stats, severe checks, MURU stats, and TX status. DFS configures region-specific radar patterns and RDD state. TWT validates and schedules individual agreements, then mirrors them to firmware.

State and persistence: maintains WCID airtime, ack RSSI EWMA, token IDR, MIB accumulators, noise filter, reset/recovery flags, coredump crash data, DFS state, TWT table/list masks, and station rate-control work lists.

Dependencies and integration: depends on mt76_connac2 TX/RX helpers, DMA/WED, MCU command layer, debugfs firmware log sink, coredump, mac80211 station/TWT/DFS APIs, and register definitions.

Risks: descriptor parsing is length-sensitive and must reject malformed SKBs before pointer overrun. Token release and WED offload accounting are concurrency-sensitive. Reset sequencing spans NAPI, workers, MCU waitqueues, DMA, and mac80211 queues. DFS radar constants are regulatory critical. TWT list scheduling must avoid overlapping agreements and stale table masks.

Test signals: RX with encrypted/plain/header-translated/A-MSDU frames, malformed descriptor fuzzing, TX token exhaustion/release, WED on/off, firmware monitor logs, full and partial SER recovery, MIB counter growth, DFS CAC/active/stop transitions per region, TWT accept/reject/teardown, and long-running watchdog behavior.
