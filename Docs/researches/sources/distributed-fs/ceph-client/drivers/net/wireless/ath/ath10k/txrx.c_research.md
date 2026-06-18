# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/txrx.c

Purpose: Implements shared ath10k TX completion unreference/status reporting and HTT peer map/unmap bookkeeping used by RX/TX data paths.

Important APIs and functions: Public functions are `ath10k_txrx_tx_unref()`, `ath10k_peer_find()`, `ath10k_peer_find_by_id()`, `ath10k_wait_for_peer_created()`, `ath10k_wait_for_peer_deleted()`, `ath10k_peer_map_event()`, and `ath10k_peer_unmap_event()`. `ath10k_report_offchan_tx()` handles off-channel TX completion signaling.

Control flow: TX completion validates `msdu_id`, finds the pending skb under `htt->tx_lock`, decrements per-TXQ firmware queue count, frees the msdu ID, decrements pending TX, registers airtime, unmaps DMA for non-high-latency devices, completes any matching off-channel TX wait, fills mac80211 TX status flags based on HTT completion state and no-ack flags, reports ACK signal when valid, emits a tracepoint, and hands ownership to `ieee80211_tx_status_ext()`. Peer map events validate peer ID, find or allocate a peer under `data_lock`, add it to `ar->peers`, set `ar->peer_map[peer_id]`, set the peer bitmap, and wake waiters. Peer unmap clears the peer ID mapping, frees the peer when no IDs remain, and wakes waiters.

State and persistence: Mutates `htt->pending_tx`, HTT pending counters, TXQ `num_fw_queued`, skb DMA mappings, mac80211 TX status, `ar->offchan_tx_skb`, `ar->peer_map`, `ar->peers`, peer ID bitmaps, and `peer_mapping_wq`. State is runtime-only but must remain consistent across firmware HTT events and mac80211 queues.

Dependencies and integration points: Depends on ath10k core/HTT/MAC/debug, mac80211 TX status and airtime APIs, Linux IDR, DMA mapping, RCU, wait queues, and tracepoints from `trace.h`.

Risks: Invalid or duplicate firmware completion IDs can desynchronize pending TX. The code assumes send ownership and DMA mapping differ for high-latency buses. Off-channel completion guards against stale timeouts with pointer matching. Peer mapping updates require `data_lock`; callers relying on peer existence use a three-second wait and must handle crash flush.

Test signals: HTT TX completion ACK/NOACK/DISCARD, invalid and duplicate msdu IDs, high-latency versus DMA-unmap buses, airtime registration with TXQs, off-channel TX timeout race, peer map/unmap for multiple IDs per peer, out-of-range peer IDs, and wait-for-peer created/deleted timeout and crash-flush exit.
