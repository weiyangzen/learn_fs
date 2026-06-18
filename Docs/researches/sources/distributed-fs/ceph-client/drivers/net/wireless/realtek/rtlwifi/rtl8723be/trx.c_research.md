<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/trx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/trx.c

## Purpose
Implements RTL8723BE transmit and receive descriptor handling for the PCI rtlwifi path. It maps mac80211 frames into hardware TX descriptors, parses RX descriptors and PHY status into `rtl_stats` and `ieee80211_rx_status`, handles early-mode aggregation metadata, command descriptors, descriptor ownership helpers, and TX queue polling.

## Important APIs, Types, And Functions
- RX path: `rtl8723be_rx_query_desc`, `_rtl8723be_query_rxphystatus`, and `_rtl8723be_translate_rx_signal_stuff`.
- TX path: `rtl8723be_tx_fill_desc`, `_rtl8723be_map_hwqueue_to_fwqueue`, `_rtl8723be_insert_emcontent`, and `rtl8723be_tx_fill_cmddesc`.
- Descriptor helpers: `rtl8723be_set_desc`, `rtl8723be_get_desc`, `rtl8723be_is_tx_desc_closed`, and `rtl8723be_tx_polling`.
- Uses `struct rtl_stats`, `struct ieee80211_rx_status`, `struct rtl_tcb_desc`, `struct rx_fwinfo_8723be`, `struct phy_status_rpt`, PCI DMA mapping, mac80211 header helpers, and the inline descriptor bit helpers from `trx.h`.

## Control Flow
TX frames are classified into firmware queues, TCB metadata is filled, optional early-mode bytes are pushed into the skb, the skb is DMA mapped, the descriptor is cleared, and first-segment fields are populated with rate, SGI/preamble, AMPDU, sequence, RTS/CTS, bandwidth/subcarrier, security type, queue selection, fallback limits, rate control, RDG, report settings, segment flags, DMA address, MAC ID, and multicast/broadcast flags. Command descriptors use a simpler beacon queue, 1 Mbps fixed rate, one segment, own bit set, and DMA address. RX parsing reads descriptor fields, classifies normal RX versus C2H report, marks CRC/ICV/decryption/HT/40 MHz/mac time fields for mac80211, handles robust management frame decryption flags, maps hardware rate to rate index, parses PHY status when present, and records TX report 2 MAC ID bitmaps when applicable.

## State And Persistence
The file mutates descriptor memory shared with the PCI device, DMA mappings for outgoing skbs, per-packet `rtl_stats`, mac80211 RX status, dynamic-management counters such as CFO tails and packet count, beacon query debug counters, and TX report descriptor fields. Hardware observes descriptor ownership and buffer addresses until rings recycle them.

## Dependencies And Integration Points
Integrated through `rtl8723be_hal_ops.fill_tx_desc`, `fill_tx_cmddesc`, `query_rx_desc`, `set_desc`, `get_desc`, `is_tx_desc_closed`, and `tx_polling` in `sw.c`. Depends on mac80211 frame helpers, rtlwifi PCI rings, rate mapping, PHY signal conversion helpers, security helpers, `reg.h`, `def.h`, `fw.h`, `dm.h`, and descriptor layout definitions in `trx.h`.

## Risks And Edge Cases
DMA mapping errors return without a descriptor, so callers must avoid queue corruption. Descriptor bit offsets must match hardware exactly. The RX signal path has separate CCK and OFDM calculations with signed conversions and percentage clamping. Robust management frame handling deliberately clears `RX_FLAG_DECRYPTED` for IEEE 802.11w frames even when hardware reports decrypted. Early-mode `skb_push` changes buffer layout and must match descriptor offsets. `rtl8723be_get_desc` lacks an explicit return assignment for some names and warns on unsupported descriptors, so HAL callers must use only supported names.

## Test Signals
Signals include TX under all access categories, management/beacon/command TX, AMPDU aggregation, encrypted traffic including CCMP/TKIP/WEP and robust management frames, RX RSSI/EVM reporting for CCK and OFDM/HT rates, wake packet debug logs, TX report handling, descriptor ring progress, and no DMA mapping or ownership stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/trx.c -->
