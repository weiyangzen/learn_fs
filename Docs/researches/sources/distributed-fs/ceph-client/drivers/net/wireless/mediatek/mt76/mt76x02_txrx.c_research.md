<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_txrx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_txrx.c

Purpose: shared TX/RX glue between mac80211/mt76 core and mt76x02 MAC descriptors. It chooses WCIDs for outgoing frames, dispatches MCU vs data RX, computes TX power adjustment, exposes TX status polling, and prepares MMIO TXWI metadata.

Important APIs/types/functions: `mt76x02_tx()`, `mt76x02_queue_rx_skb()`, `mt76x02_tx_get_max_txpwr_adj()`, `mt76x02_tx_get_txpwr_adj()`, `mt76x02_tx_set_txpwr_auto()`, `mt76x02_tx_status_data()`, and `mt76x02_tx_prepare_skb()`.

Control flow: TX selects station WCID, VIF group WCID, or global WCID, then calls mt76 core TX. RX sends MCU queue packets to `mt76_mcu_rx_event()` and data packets through RXWI parsing before mt76 RX. MMIO TX preparation writes TXWI, allocates pktid, encodes fallback rate in no-skb pktids, selects EDCA/MGMT qsel, sets WIV, and updates per-station packet length EWMA.

State and persistence: updates packet-id maps, station EWMA length, WCID drop state for PSD queue, TXWI contents, auto-protection TX power fields, and rate-power-derived adjustment.

Dependencies/integration: shared MAC code, mt76 TX/RX core, mac80211 rate flags, DMA bitfields, and USB/MMIO driver ops.

Risks: wrong WCID selection, pktid leak on errors, TX power adjustment encoding, and MCU RX queue misclassification. Test signals include station/group/global traffic, AMPDU with no skb status, encrypted WIV handling, MCU events, and TX power changes with TPC enabled/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_txrx.c -->
