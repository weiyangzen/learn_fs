# sources/distributed-fs/ceph-client/net/mac802154/util.c

Purpose: provides mac802154 queue control, inter-frame-spacing timer completion, transmit completion/error callbacks exported to drivers, device stop, and the private `wpan_phy` identity token.

Important APIs and functions: `ieee802154_hold_queue()`, `ieee802154_release_queue()`, and `ieee802154_disable_queue()` stop/wake/disable all interface queues. `ieee802154_xmit_ifs_timer()` releases queues after SIFS/LIFS. `ieee802154_xmit_complete()`, `ieee802154_xmit_error()`, and `ieee802154_xmit_hw_error()` finish driver TX. `ieee802154_stop_device()` flushes work, cancels timer, and stops the driver.

Control flow and state: `hold_txs` is an atomic nesting counter protected by `queue_lock`; only the transition to/from zero stops or wakes netdev queues. Completion records `local->tx_result`, optionally delays release based on skb length and PHY SIFS/LIFS periods, consumes/frees skb, decrements `ongoing_txs`, and wakes synchronous waiters.

Dependencies and integration: used by `tx.c`, scan/MLME paths, and drivers through exported completion symbols. Requires RCU access to `local->interfaces` and hrtimer support.

Risks and test signals: incorrect completion use by drivers can leak queue holds or wake too early. IFS timing depends on symbol durations configured in `main.c`. Tests should check nested holds, IFS delayed release, error completion, and stop behavior with pending work/timer.
