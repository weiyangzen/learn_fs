# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/trx_common.c

Purpose: Implements shared RX descriptor parsing, PHY status interpretation, RSSI/EVM smoothing, and generic descriptor set/get helpers for RTL8192D.

Important APIs/functions: `rtl92d_rx_query_desc()` converts a hardware RX descriptor and optional PHY status into `rtl_stats` plus mac80211 `ieee80211_rx_status`. `rtl92d_set_desc()` sets TX/RX ownership, next descriptor address, RX buffer address/length/EOR. `rtl92d_get_desc()` reads descriptor ownership, buffer address, and packet length. Internal helpers decode CCK/OFDM PHY status, smooth UI RSSI/link quality, update PWDB, and classify BSSID/self/beacon packets.

Control flow: RX descriptor parsing extracts packet length, driver-info size, buffer shift, CRC/ICV, encryption, MCS/rate, AMPDU flags, timestamp, bandwidth and HT flags, then populates mac80211 rate/frequency/band/flags. If PHY status is present, it locates driver info in the skb, decodes CCK or OFDM power/quality, checks frame addresses against BSSID and local MAC, updates smoothed RSSI/PWDB/link-quality state for self or beacon packets, and sets `rx_status->signal`.

State and persistence: Updates `rtlpriv->stats` smoothing windows, RSSI percentages, SNR, EVM, signal strength/quality, `rtlpriv->dm.undec_sm_pwdb`, and per-packet `rtl_stats`. Descriptor writes hand ownership to hardware with memory barriers; no disk persistence.

Dependencies and integration: Depends on descriptor bit helpers from `trx_common.h`, rtlwifi base/stats helpers, mac80211 headers, `rtl_signal_scale_mapping()`, `rtlwifi_rate_mapping()`, and `rtl_efuse`/`rtl_mac` identity state. Bus-specific TX/RX paths call these through ops.

Risks: skb offsets rely on descriptor `rx_drvinfo_size` and `rx_bufshift` being valid. PHY CCK/OFDM formulas are hardware-specific. Address parsing assumes enough frame header bytes after descriptor stripping. Descriptor ownership uses `wmb()`; ordering bugs can cause DMA races. `rx_status->signal = recvsignalpower + 10` differs from raw dBm.

Test signals: RX under CCK/OFDM/HT, CRC/ICV failure handling, encrypted packet flagging, AMPDU first/subsequent packets, RSSI/link-quality stability, descriptor DMA ring recycling, and mac80211 rate/band reporting.
