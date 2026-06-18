# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/trx.c

## Purpose
This file implements RTL8192EE PCIe transmit and receive descriptor handling. It maps mac80211 packets into 8192EE TX descriptors and buffer descriptors, translates RX descriptors and PHY status into `rtl_stats` and `ieee80211_rx_status`, manages DMA pointer accounting, and exposes descriptor helpers to the shared rtlwifi PCI layer.

## Important APIs, Types, And Functions
RX processing centers on `rtl92ee_rx_query_desc()`, `_rtl92ee_translate_rx_signal_stuff()`, and `_rtl92ee_query_rxphystatus()`. These parse RX descriptor fields, detect C2H/TX report packets, set mac80211 RX metadata, handle hardware decryption flags, calculate CCK/OFDM RSSI/PWDB/EVM, update CFO tails and beacon/non-BE counters, and report wake pattern/magic/unicast matches.

TX processing centers on `rtl92ee_tx_fill_desc()`, `rtl92ee_pre_fill_tx_bd_desc()`, `_rtl92ee_map_hwqueue_to_fwqueue()`, `_rtl92ee_insert_emcontent()`, and `rtl92ee_tx_fill_cmddesc()`. These fill packet descriptors, optional early-mode headers, DMA mappings, PCIe buffer descriptors, aggregation fields, RTS/CTS fields, bandwidth/subcarrier bits, security type, rate fallback controls, rate ids, MAC ids, BMC flags, and H2C command descriptors.

Descriptor ring integration uses `rtl92ee_set_desc()`, `rtl92ee_get_desc()`, `rtl92ee_is_tx_desc_closed()`, `rtl92ee_get_available_desc()`, `rtl92ee_rx_desc_buff_remained_cnt()`, `rtl92ee_rx_check_dma_ok()`, and `get_desc_addr_fr_q_idx()`.

## Control Flow
On TX, the generic PCI layer passes a prepared skb and descriptor slot into `rtl92ee_tx_fill_desc()`. The function derives a firmware queue selector from frame type, asks the rtlwifi core for a `rtl_tcb_desc`, optionally prepends early-mode bytes, DMA-maps the skb, fills buffer descriptors for PCIe DMA, then fills the packet descriptor with segmentation, aggregation, sequence, rate, security, queue, and station fields. Ownership and write-pointer advancement are later handled through `rtl92ee_set_desc(HW_DESC_OWN)`.

On RX, the PCI layer calls `rtl92ee_rx_query_desc()` for a completed descriptor. It extracts length, driver-info size, shift, CRC/ICV, decryption state, rate, AMPDU, timestamp, MAC id, packet report type, and channel metadata. If PHY status is present, it locates `rx_fwinfo`, derives signal information, then calls `rtl_process_phyinfo()`. It also fills TX report 2 valid MAC-id bitmaps when the RX packet is actually a firmware report.

## State And Persistence
The file updates ring state in `rtlpci->tx_ring[].cur_tx_wp`, `cur_tx_rp`, and `rtlpci->rx_ring[].next_rx_rp`; updates PHY/DM state such as `dm.cfo_tail`, `dm.packet_count`, beacon query counts, and non-BE packet counts; and relies on skb control block metadata from the core. DMA mappings are embedded in descriptors and later retrieved by `rtl92ee_get_desc()`. Register write/read pointers are the hardware source of truth for descriptor availability and closure.

## Dependencies And Integration Points
It depends on rtlwifi PCI ring structures, mac80211 TX/RX status types, `rtl_get_tcb_desc()`, `rtl_set_tx_report()`, `rtlwifi_rate_mapping()`, PHY/statistics helpers, Realtek register definitions, descriptor bitfield helpers in `trx.h`, and PCI DMA APIs. It integrates with firmware C2H reporting, WoWLAN wake matches, CAM hardware crypto state, aggregation/rate adaptation, and the generic rtlwifi interrupt/RX/TX loops.

## Risks
DMA and descriptor ownership ordering are high risk. Failed `dma_map_single()` returns without fully completing descriptor state, so callers must not hand the slot to hardware. `rtl92ee_pre_fill_tx_bd_desc()` assumes PCIe buffer descriptor layout and 64-bit DMA policy match module settings. RX pointer accounting uses hardware read/write registers and a static `start_rx` flag, so stale register reads can suppress or miscount completions. Robust management frames intentionally clear `RX_FLAG_DECRYPTED` despite hardware saying decrypted; regressions here affect 802.11w. Early-mode skb push changes data pointer and length, which must remain consistent with DMA and descriptor packet sizes.

## Test Signals
Relevant tests include sustained TX/RX under all access categories, management/control/data frames, AMPDU aggregation, 20/40 MHz operation, multicast/broadcast traffic, hardware crypto with WEP/TKIP/CCMP and robust management frames, WoWLAN wake-pattern reporting, firmware TX report handling, descriptor ring wraparound, DMA mapping failure injection, and suspend/unload while queues are active. Debug signals include correct register write pointers, no DMA API warnings, sane RSSI/EVM values, and no stuck TX descriptors.
