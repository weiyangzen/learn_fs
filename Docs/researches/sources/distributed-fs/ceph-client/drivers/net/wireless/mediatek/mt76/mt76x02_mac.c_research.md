<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mac.c

Purpose: shared MAC-layer logic for mt76x02. It handles WCID/key programming, TXWI construction, TX status reconstruction, RXWI parsing, MAC address/BSSID programming, protection/RTS settings, EDCCA monitoring, channel survey accounting, and periodic MAC work.

Important APIs/types/functions: `mt76x02_mac_write_txwi()`, `mt76x02_mac_process_rx()`, `mt76x02_send_tx_status()`, `mt76x02_mac_load_tx_status()`, WCID/key helpers, `mt76x02_mac_setaddr()`, `mt76x02_mac_set_tx_protection()`, `mt76x02_edcca_init()`, and `mt76x02_mac_work()`.

Control flow: TX builds rate/flags/power/PN/BA metadata into TXWI, then bus-specific code adds DMA transport. TX status is fetched from hardware FIFO, matched to skb pktids when possible, aggregated for no-skb AMPDU reports, converted into mac80211 rates/airtime, and submitted. RX strips padding/PN, fills decrypt/AMPDU/rate/RSSI/status fields, trims frame length, and hands packets to mt76. Periodic work updates survey/aggr counters, checks MAC errors, runs EDCCA, and reschedules.

State and persistence: programs key tables, WCID tables, BSSID registers, MAC address, protection registers, EDCCA block state, airtime counters, aggregation stats, and per-station cached TX status/packet length.

Dependencies/integration: mac80211, mt76 TX status/airtime/WCID helpers, tracepoints, EEPROM-derived calibration, register definitions, and USB/MMIO TX paths.

Risks: PN/key offload correctness, skb pktid lifecycle, AMPDU status coalescing, RX padding/PN stripping, rate conversion, EDCCA TX blocking, and MAC reset triggers. Test signals include encrypted traffic, AP/client multi-VIF, AMPDU retries, monitor/rate reporting, fragmented CCMP RX, airtime accounting, EDCCA busy-channel behavior, and beacon hang recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mac.c -->
