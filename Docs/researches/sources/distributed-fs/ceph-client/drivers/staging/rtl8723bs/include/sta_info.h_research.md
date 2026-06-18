<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sta_info.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sta_info.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sta_info.h` defines station table state for associated peers, including ACLs, per-station transmit/receive state, security keys, QoS/HT state, timers, power-save queues, statistics, and station allocation APIs. The source was reviewed as a complete 330-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct rtw_wlan_acl_node`, `struct wlan_acl_pool`, `struct rssi_sta`, `struct stainfo_stats`, `struct sta_info`, `struct sta_priv`, packet counter macros, `_rtw_init_sta_priv`, `rtw_alloc_stainfo`, `rtw_free_stainfo`, `rtw_get_stainfo`, `rtw_init_bcmc_stainfo`, `rtw_get_bcmc_stainfo`, and `rtw_access_ctrl`.

## Control Flow

AP/client MLME paths allocate station entries on association or peer discovery, attach TX/RX/security/HT state, update counters during data flow, and free entries on disassociation or adapter teardown.

## State and Persistence Behavior

`sta_priv` owns the station pool, free queue, hash table, auth/asoc lists, sleep/wakeup queues, AID map, and ACL pool. Each `sta_info` owns per-peer keys, sequence/cache state, timers, and traffic stats.

## Dependencies and Integration Points

Connected to `rtw_xmit.h`, `rtw_recv.h`, `rtw_security.h`, `rtw_ht.h`, `rtw_mlme.h`, AP support, and rate adaptation. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Station lifetime races with RX/TX, timers, and AP events can cause use-after-free. Hash/AID/ACL bounds are fixed-size and must be respected.

## Test Signals

Multi-client AP association/disassociation, station lookup/free under traffic, BCMC station setup, ACL allow/deny, power-save queue handling, and timer cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sta_info.h -->
