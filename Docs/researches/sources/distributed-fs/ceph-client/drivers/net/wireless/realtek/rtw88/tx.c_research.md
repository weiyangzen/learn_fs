## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/tx.c

Purpose: common transmit preparation for rtw88. It translates mac80211 SKBs into hardware TX packet info/descriptors, manages TX reports, reserved/H2C packet allocation, mac80211 TXQ draining, aggregation decisions, statistics, and queue mapping.

Important APIs/functions: `rtw_tx_fill_tx_desc()` encodes `struct rtw_tx_pkt_info` into the hardware descriptor. `rtw_tx_pkt_info_update()` derives MAC ID, management/data rates, AMPDU parameters, RTS, BW, STBC/LDPC, security type, queue select, report request, size, and stats. `rtw_tx()` submits a single SKB to HCI ops. TXQ functions initialize/cleanup/drain mac80211 TXQs. `rtw_tx_report_enqueue/handle/purge_timer` bridge firmware CCX reports to mac80211 TX status. Reserved page helpers allocate SKBs for firmware pages and H2C.

Control flow: mac80211 TX calls update packet info, HCI `tx_write`, and HCI kick-off. TXQ work locks `txq_lock`, dequeues frames from mac80211, checks/requests BA aggregation, writes to HCI, then kicks HCI. TX reports store sequence numbers in skb driver data and are matched against C2H report payloads.

State and persistence: updates global/per-VIF TX stats, `rtwdev->tx_report` queue/timer/SN, station BA bitmaps, and transient descriptor fields. Persistent queue membership lives in `rtwdev->txqs` and HCI queues.

Dependencies and integration: depends on mac80211 TX info, firmware C2H definitions, power-save code, and HCI ops implemented by PCI/USB/SDIO.

Risks and test signals: descriptor bit-field correctness, TX status lifetime, queue mapping, forced-rate/debug paths, and AMPDU negotiation are key risks. Test with unicast/multicast, management frames, BA setup, encryption, TX status requests, queue cleanup, and all HCIs.
