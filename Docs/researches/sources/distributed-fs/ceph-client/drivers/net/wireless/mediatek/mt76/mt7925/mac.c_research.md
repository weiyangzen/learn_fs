# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/mac.c

Purpose: MT7925 MAC datapath and recovery logic. It parses RX descriptors, builds TX descriptors, handles TX status/free events, tracks airtime and ACK signal, routes MCU/RX packets, performs SER/coredump reset work, and provides USB/SDIO TX helpers.

Important APIs/types/functions: `mt7925_mac_write_txwi()` builds TXWI for 802.3/802.11 frames; `mt7925_queue_rx_skb()` dispatches RX packets; `mt7925_rx_check()` prefilters DMA RX; `mt7925_mac_fill_rx()` decodes RX metadata/rate/security/AMSDU; `mt7925_mac_add_txs()` and `mt7925_mac_tx_free()` process TX status/free reports; `mt7925_mac_reset_work()` and `mt7925_coredump_work()` implement recovery; `mt7925_usb_sdio_tx_prepare_skb()` and completion/status helpers support non-MMIO buses.

Control flow: RX begins by classifying packet type from RXD. TX-free and TXS packets update token/status state and are consumed; MCU events go to `mt7925_mcu_rx_event()`; normal frames are validated, descriptor groups are walked, status/rate/security fields are filled, optional header translation reversal is done, radiotap HE/EHT metadata is decoded, and frames enter `mt76_rx()`. TXWI construction chooses queue and packet format from beacon/inband discovery/PSD/data path, fills WCID/OMAC/band/WMM, handles fixed-rate cases, keys, no-ack, BIP, injected sequence numbers, and basic/beacon/multicast rate tables.

State/persistence: updates WCID statistics, packet IDs, tx status queues, airtime counters, `wcid->rate`, RSSI/ACK EWMA, A-MPDU state bits, reset flags, coredump message queue, scan state on reset, PM suspended state, and IPv6 NS offload queue. Hardware state is touched through WTBL reads/writes and reset calls.

Dependencies/integration: integrates mt76 DMA/token queues, connac3 radiotap decoding, mac80211 TX/RX status, WTBL register layout, MT7925 MCU event and reset helpers, devcoredump, USB/SDIO shared framing, IPv6 offload, and regulatory fallback after reset.

Risks: descriptor parsing is length-sensitive and must reject malformed RXD groups. Header translation reversal for fragmented mesh frames is complex and can corrupt skb layout if offsets are wrong. Reset work retries device reset ten times and then reconnects interfaces; partial failures can leave firmware/mac80211 state mismatched. TX-free parsing relies on firmware event format version.

Test signals: RX for legacy/HT/VHT/HE/EHT rates, checksum offload, security error flags, AMSDU, header translation, TX status reporting, BA session start, token cleanup, USB/SDIO TX pad handling, firmware coredump collection, SER reset with active AP/STA interfaces, and IPv6 NS offload send failure purge.
