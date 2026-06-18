# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/data_tx.c

Purpose: Implements WFx mac80211 TX preparation, firmware TX policy caching, SKB queue insertion, TX confirmation processing, and flush/drop behavior.

Important APIs and functions: `wfx_tx()` is the mac80211 TX callback. Helpers include `wfx_tx_policy_init()`, `wfx_tx_policy_upload_work()`, `wfx_skb_tx_priv()`, `wfx_skb_txreq()`, `wfx_skb_wvif()`, `wfx_tx_confirm_cb()`, and `wfx_flush()`. Internal policy-cache functions build packed firmware retry-rate policies, find/reuse/free policy slots, upload missing policies, and stop/wake mac80211 queues when cache slots are exhausted.

Control flow and integration: TX chooses a vif, drops BA action frames handled by firmware, fixes retry rates into firmware-compatible descending policies, reserves tailroom for ICV/MIC, pushes HIF/TX headers into the SKB, assigns interface/packet ID/peer link/retry policy/queue/frame format flags, enqueues to normal/CAB/offchannel queue, and requests BH TX. Confirmations find the pending SKB by packet ID, fill mac80211 retry/status information from firmware ack counts/rate/status, trim reserved crypto tailroom, set ACK/noack/filtered flags, release retry-policy usage, and report status.

State and persistence: Uses per-vif `tx_policy_cache`, per-SKB `wfx_tx_priv` in `rate_driver_data`, `wdev->packet_id`, `wdev->tx_pending`, queue pending counters, and `after_dtim_tx_allowed`. Policy entries persist across frames until reset/interface removal.

Dependencies: Depends on mac80211 TX control/status APIs, HIF TX request/confirm ABI, queue helpers, station link IDs, key tailroom flags, BH scheduling, and MIB policy upload.

Risks and test signals: Risks include SKB headroom/alignment errors, retry-policy cache exhaustion deadlocks, packet ID lookup failures, stale vif IDs after interface removal, incorrect firmware/Linux queue inversion, offchannel interface ID misuse, and requeue/DTIM handling. Tests should cover data/mgmt TX, offchannel TX, CAB after DTIM, encrypted TKIP/CCMP tailroom, multi-rate retries, policy upload races, unknown packet IDs, failed TX statuses, flush with drop, and frozen-chip pending drop.

Test signals: Source read size: 594 lines, 17979 bytes.
