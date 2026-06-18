# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/trx.c

`trx.c` implements RTL8188EE transmit and receive descriptor handling. It maps mac80211 frames to firmware queues, fills PCI TX descriptors, decodes RX descriptors into `rtl_stats` and `ieee80211_rx_status`, translates PHY status to RSSI/EVM/signal quality, maintains antenna-diversity statistics, and exposes generic descriptor get/set callbacks.

Important functions include `rtl88ee_rx_query_desc()`, `_rtl88ee_query_rxphystatus()`, `_rtl88ee_translate_rx_signal_stuff()`, `_rtl88ee_smart_antenna()`, `rtl88ee_tx_fill_desc()`, `rtl88ee_tx_fill_cmddesc()`, `rtl88ee_set_desc()`, `rtl88ee_get_desc()`, `rtl88ee_is_tx_desc_closed()`, and `rtl88ee_tx_polling()`. RX flow parses descriptor fields, handles normal RX versus TX report packets, computes header offsets, validates BSSID/self/beacon status, and populates mac80211 status. TX flow derives rate-control metadata, optionally pushes early-mode bytes, DMA maps the skb, programs rate, AMPDU, RTS/CTS, bandwidth, security, queue, fallback, MAC ID, QoS, buffer address, and antenna fields.

State is updated in `rtlpriv->stats`, `rtlpriv->dm.fat_table`, PCI ring descriptors, DMA mappings, skb contents, and mac80211 RX status. Dependencies include `trx.h` bit helpers, `reg.h`, `def.h`, DMA APIs, mac80211 helpers, rtlwifi base/stats/PCI code, DM, LED, and PHY support.

Risks include descriptor bit/endian mistakes, DMA mapping failure handling, robust management frame decryption semantics, 20/40 MHz descriptor fields, and ownership-bit lifecycle. Test signals include RX status accuracy, FCS/decryption flags, hardware crypto, AMPDU throughput, beacon/management queues, descriptor closure, TX polling, and antenna diversity stats.
