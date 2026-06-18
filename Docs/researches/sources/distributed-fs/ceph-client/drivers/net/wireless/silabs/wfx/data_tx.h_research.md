# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/data_tx.h

Purpose: Declares WFx TX private SKB state, firmware TX retry-policy cache structures, and TX/flush/status helper APIs.

Important APIs and types: `struct wfx_tx_policy` holds packed firmware rates, list link, upload flag, and usage count. `struct wfx_tx_policy_cache` owns 15 policy slots, a lock, and used/free lists. `struct wfx_tx_priv` stores ICV size, vif ID, and transmit timestamp in `ieee80211_tx_info.rate_driver_data`. Exports include policy init/upload work, mac80211 `wfx_tx()`/`wfx_flush()`, confirmation callback, and SKB accessors.

Control flow and integration: `data_tx.c` stores per-frame private state in `wfx_tx_priv`, queue code records transmit timestamps, and confirmation/flush code uses the accessors to recover HIF request and vif state.

State and persistence: The cache is persistent per vif; SKB private data is transient per frame.

Dependencies: Depends on Linux list/spinlock/workqueue, mac80211 TX structures, and HIF TX MIB constants for policy count/invalid ID.

Risks and test signals: Tests should assert `wfx_tx_priv` fits in `rate_driver_data`, policy slot accounting wakes queues correctly, and callers do not touch `tx_info->control` after it is repurposed.

Test signals: Source read size: 53 lines, 1360 bytes.
