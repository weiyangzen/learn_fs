# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/decl.h

## Purpose
`decl.h` is a shared mwifiex declaration header for generic constants, small enums, packet metadata structures, WMM structures, histogram/storage structs, DFS/radar structs, firmware-dump definitions, and channel-width/offset enums. It establishes common values used across cfg80211, firmware command/event handling, data path, debugfs, power management, TDLS, 11n/11ac, and SDIO aggregation code.

## Important APIs, types, and functions
The file has no functions; its API surface is macros, enums, and structs. Major constants include BSS/interface limits, DMA/RX/TX headroom and management-frame sizes, host-MLME auth flags, management frame masks, block-ack stream limits, AMPDU window defaults, RTS/fragment thresholds, WMM version fields, retry limits, skb flag bits, TDLS operation values, TDLS RSSI/failure thresholds, rate index values, max STA/uAP/P2P counts, SDIO aggregation constants, histogram bounds, firmware-dump markers, and channel-width/offset values.

Key enums are `mwifiex_bss_type`, `mwifiex_bss_role`, `mwifiex_tdls_status`, `mwifiex_tdls_error_code`, `mwifiex_data_frame_type`, `mwifiex_wmm_ac_e`, `rdwr_status`, `mwifiex_chan_width`, and `mwifiex_chan_offset`. Key structs include `mwifiex_fw_image`, `mwifiex_802_11_ssid`, `mwifiex_wait_queue`, `mwifiex_rxinfo`, `mwifiex_txinfo`, WMM IE structs, `mwifiex_arp_eth_header`, `mwifiex_chan_stats`, `mwifiex_histogram_data`, `mwifiex_iface_comb`, `mwifiex_radar_params`, `mwifiex_11h_intf_state`, and `memory_type_mapping`.

## Control flow
There is no executable control flow. Compile-time consumers use this header to agree on structure layouts, bit meanings, and numeric bounds. Macros such as `GET_BSS_ROLE()` influence runtime branches in other files by masking `priv->bss_role`.

## State and persistence behavior
The header defines layouts for state stored elsewhere. Examples include per-skb RX/TX control blocks (`mwifiex_rxinfo`, `mwifiex_txinfo`), histogram counters (`mwifiex_histogram_data`), interface-combination counters (`mwifiex_iface_comb`), channel stats used by survey reporting, DFS CAC/channel-switch parameters, and firmware-dump memory tracking. The actual state lifetime is owned by adapters, priv structures, skbs, or debug/firmware-dump paths.

## Dependencies and integration points
`decl.h` includes kernel wait queues, timers, IEEE 802.11 definitions, ARP user ABI, and cfg80211. Its constants are used by `cfg80211.c` for management frame formatting, host-MLME auth, TDLS, AP settings, RTS/fragment validation, channel stats, scan-gap allocation, and DFS. `debugfs.c` uses histogram bounds and data structures. `cmdevt.c` uses wait queues, command buffer sizing from related headers, BSS role/type values, and power/host-sleep state conventions. Because it is included broadly, changes can have wide compile and ABI-layout impact inside the driver.

## Risks and test signals
Risks are compatibility and bounds risks: changing packet header lengths or headroom values can break firmware packet framing; altering enum numeric values can break firmware protocol assumptions; shrinking histogram or rate limits can cause out-of-bounds users; changing `__packed` structures can alter wire format; and BSS role/type constants are embedded in command sequence/event demux paths. Test signals are broad compile coverage plus runtime tests for management-frame TX/auth, skb metadata handling, histogram updates/debugfs reads, TDLS transitions, DFS CAC, firmware dump, SDIO aggregation, and command/event BSS routing.
