# sources/distributed-fs/ceph-client/net/mac802154/tx.c

Purpose: implements mac802154 transmit path, including FCS append, queue serialization, async/sync driver handoff, MLME synchronous transmission helpers, and monitor/subinterface start_xmit functions.

Important APIs and functions: `ieee802154_tx()` is the core transmit helper. `ieee802154_xmit_sync_worker()` handles drivers without async transmit. `ieee802154_sync_queue()`, `ieee802154_sync_and_hold_queue()`, `ieee802154_mlme_tx_locked()`, `ieee802154_mlme_tx()`, and `ieee802154_mlme_tx_one_locked()` provide management-frame synchronization. `ieee802154_subif_start_xmit()` encrypts through LLSEC then transmits.

Control flow and state: TX optionally appends CRC, holds all interface queues, increments `ongoing_txs`, and calls `drv_xmit_async()` or queues sync work. Completion paths in `util.c` release queue/ongoing counters. MLME helpers stop user traffic, wait for outstanding TX, and send control frames under RTNL.

Dependencies and integration: depends on driver ops, LLSEC, netdevice stats, CRC helpers, `util.c` queue primitives, and workqueue setup from `main.c`.

Risks and test signals: queue hold/release and `ongoing_txs` must stay balanced on all driver success/failure paths. Sync fallback uses `local->tx_skb` single storage, so serialization is required. Test async failure, sync failure, encrypted TX failure, tailroom expansion failure, and MLME sends while interface is down.
