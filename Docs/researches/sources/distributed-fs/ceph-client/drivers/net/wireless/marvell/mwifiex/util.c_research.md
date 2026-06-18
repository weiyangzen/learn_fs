# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/util.c

## Purpose
`util.c` provides shared mwifiex helpers for firmware init/shutdown, debug state collection/formatting, management-frame parsing and cfg80211 delivery, host-MLME disconnect indication, final Ethernet packet delivery, synchronous command completion wakeups, station-list management, TDLS command gating, peer HT capability setup, RX histograms, DMA-aligned RX SKB allocation, and firmware dump event triggering.

## Important APIs, Types, and Functions
Key APIs include `mwifiex_init_shutdown_fw`, `mwifiex_get_debug_info`, `mwifiex_debug_info_to_buffer`, `mwifiex_host_mlme_disconnect`, `mwifiex_process_mgmt_packet`, `mwifiex_recv_packet`, `mwifiex_complete_cmd`, `mwifiex_get_sta_entry`, `mwifiex_is_tdls_chan_switching`, `mwifiex_is_send_cmd_allowed`, `mwifiex_add_sta_entry`, `mwifiex_set_sta_ht_cap`, `mwifiex_del_sta_entry`, `mwifiex_del_all_sta_list`, histogram helpers, `mwifiex_alloc_dma_align_buf`, and `mwifiex_fw_dump_event`. The static `items[]` table maps debug output names to fields in `mwifiex_debug_info` or `mwifiex_adapter`.

## Control Flow and Integration
Debug collection copies adapter/private counters, queue state, BA tables, TDLS peers, power-save flags, command/event history, and transport counters into `mwifiex_debug_info`; formatting iterates the debug descriptor table and appends BA/reorder/TDLS table summaries. Management RX first validates registration and packet length, strips RXPD and firmware packet length, removes address4, handles TDLS discovery response and drops BACK action frames, optionally reports host-MLME auth/deauth/disassoc through cfg80211 under wiphy lock, logs uAP host-MLME events, and finally calls `cfg80211_rx_mgmt`.

`mwifiex_recv_packet` is the final data delivery helper: it updates RX counters, updates AP source station stats, fills netdev/protocol/checksum fields, adjusts `skb->truesize` for large USB/PCIe allocations, and calls `netif_rx`. Station-list helpers add/find/delete nodes under `sta_list_spinlock` where mutation is needed. TDLS gating helpers scan station nodes for `TDLS_CHAN_SWITCHING` or `TDLS_IN_OFF_CHAN` and block commands while peers are off base channel.

## State and Persistence Behavior
State touched includes debug info snapshots, `priv->auth_flag`, `priv->auth_alg`, station list nodes, peer HT flags/max-AMSDU, histogram atomics, packet statistics, AP peer statistics, and adapter command wait queue status. `mwifiex_complete_cmd` sets the command wait condition and wakes waiters; `mwifiex_alloc_dma_align_buf` returns SKBs whose data pointer is aligned for DMA.

## Dependencies and Risks
Dependencies include cfg80211 management APIs, 11n BA/reorder inspection, TDLS list helpers, WMM/debug fields, netdev RX, SKB allocation, and firmware command dispatch. Risks are debug buffer sizing because formatting uses repeated `sprintf`, management frame length/pointer assumptions during address4 removal, station-list traversal callers that rely on external locking, and histogram index ranges derived directly from firmware rate/SNR/NF values.

## Test Signals
Test debugfs/output formatting, command wait wakeups, management frame delivery for host MLME STA/uAP, BACK action drop, TDLS discovery RSSI update, netif RX packet counters, station add/delete/list cleanup, TDLS command blocking while off-channel, histogram reset/add bounds, DMA alignment, and firmware dump command dispatch.
