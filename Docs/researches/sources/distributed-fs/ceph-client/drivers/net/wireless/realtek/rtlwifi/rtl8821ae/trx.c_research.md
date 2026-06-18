# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/trx.c

## Purpose
Implements RTL8821AE PCI TX/RX descriptor handling and PHY-status translation. It converts hardware RX descriptors into `rtl_stats` and `ieee80211_rx_status`, computes RSSI/EVM/CFO metrics, fills TX descriptors from mac80211 TX control state, maps bandwidth/subcarrier settings for 20/40/80 MHz operation, and exposes descriptor get/set helpers to the shared PCI core.

## Important APIs, Types, And Functions
External functions are `rtl8821ae_rx_query_desc`, `rtl8821ae_tx_fill_desc`, `rtl8821ae_tx_fill_cmddesc`, `rtl8821ae_set_desc`, `rtl8821ae_get_desc`, `rtl8821ae_is_tx_desc_closed`, and `rtl8821ae_tx_polling`. Key internal helpers include `_rtl8821ae_map_hwqueue_to_fwqueue`, `odm_cfo`, `_rtl8821ae_evm_dbm_jaguar`, `query_rxphystatus`, `translate_rx_signal_stuff`, `rtl8821ae_insert_emcontent`, `rtl8821ae_get_rxdesc_is_ht`, `rtl8821ae_get_rxdesc_is_vht`, `rtl8821ae_get_rx_vht_nss`, `rtl8821ae_bw_mapping`, and `rtl8821ae_sc_mapping`.

## Control Flow
RX processing starts in `rtl8821ae_rx_query_desc`: descriptor macros extract length, driver-info size, shift, CRC/ICV, rate, aggregation, timestamp, bandwidth, MAC ID, HT/VHT/NSS, report type, wake-match flags, and decryption status. It fills mac80211 status fields and, when PHY status is present, calls `translate_rx_signal_stuff`, which determines BSSID/self/beacon matches and then calls `query_rxphystatus`. CCK packets use AGC report formulas that differ between RTL8812AE and RTL8821AE; OFDM/HT/VHT packets compute per-path RSSI, SNR, CFO, EVM, and signal strength. TX processing starts in `rtl8821ae_tx_fill_desc`: it computes the TCB descriptor, optionally prepends early-mode content, DMA maps the skb, clears the descriptor, writes rates, SGI/preamble, aggregation, RTS/CTS, bandwidth, subcarrier, packet size, AMPDU density, security type, queue selection, fallback limits, rate ID, MAC ID, sequence handling, multicast/broadcast flags, and TX report fields. Command descriptors are a simpler one-segment 1 Mbps beacon-queue path.

## State And Persistence
The file mutates live descriptor rings, DMA mappings, skb data when early mode is enabled, `rtlpriv->stats`, `rtlpriv->dm` counters/CFO state, antenna diversity keep fields, and link statistics. No durable persistence exists. Descriptor OWN bits and DMA addresses persist only until consumed by hardware.

## Dependencies And Integration Points
Integrates with mac80211 frame/status structures, rtlwifi PCI ring management, shared stats helpers (`rtl_query_rxpwrpercentage`, `rtl_signal_scale_mapping`, `rtl_process_phyinfo`, `rtl_evm_db_to_percentage`), dynamic management (`rtl8821ae_dm_set_tx_ant_by_tx_info`), firmware TX reports, LED control via the caller, and register polling through `REG_PCIE_CTRL_REG`. Bit layout accessors and packed descriptor structs come from `trx.h`.

## Risks And Edge Cases
DMA mapping errors cause an early return after possible early-mode `skb_push`, leaving callers to handle an skb that may have been modified. `rtl8821ae_tx_fill_desc` writes DMA addresses through 32-bit descriptor fields, so address width assumptions must match the PCI DMA setup. RX robust-management decryption logic deliberately clears `RX_FLAG_DECRYPTED` for protected management frames. The stats code later smooths `rx_mimo_sig_qual`, while this file fills `rx_mimo_signalquality`, so link-quality smoothing may miss EVM values for this chip unless another compatibility path copies them. RX descriptor parsing assumes enough skb data exists after `rx_drvinfo_size` and `rx_bufshift`. Incorrect primary channel offset state creates wrong 20/40/80 subcarrier descriptor values.

## Test Signals
Exercise RX for CCK, OFDM, HT, and VHT 1SS/2SS rates, including CRC/ICV failures, protected robust management frames, WoWLAN wake reports, TX report 2 packets, and PHY-status-present/absent cases. TX tests should cover AMPDU, multicast/broadcast, hardware and software sequence paths, WEP/TKIP/CCMP keys, RTS/CTS, 20/40/80 MHz bandwidth, early mode, DMA mapping failure injection, and descriptor OWN polling. Traffic tests should validate RSSI, SNR, EVM, CFO, and rate reporting in mac80211.
