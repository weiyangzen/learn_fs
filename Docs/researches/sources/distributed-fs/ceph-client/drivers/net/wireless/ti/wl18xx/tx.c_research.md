# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/tx.c

## Purpose
Handles WiLink 8 immediate TX completion status: maps firmware release descriptors to host skbs, fills mac80211 TX status, returns completed frames to the netstack worker, and updates per-link last-rate data.

## Important APIs, types, and functions
- `wl18xx_tx_immediate_complete()` consumes the firmware release ring from `wl18xx_fw_status_priv`.
- `wl18xx_tx_complete_packet()` validates a TX descriptor id, determines success, fills `ieee80211_tx_info`, handles dummy packets, strips private/TKIP header space, queues the skb for common netstack completion, and frees the TX id.
- `wl18xx_get_last_tx_rate()` converts firmware rate indexes into mac80211 legacy or MCS rate status flags, including SGI and HT40.
- `wl18xx_next_tx_idx()` wraps the firmware TX-status descriptor ring.

## Control flow
On each immediate completion callback, the function compares `priv->last_fw_rls_idx` with firmware `fw_release_idx`. If changed, it updates the last-rate cache for the reported HLID, validates the release index, then iterates ring entries from the previous index to the new one, completing each packet and incrementing `wl->tx_results_count`. The completion helper returns dummy packets internally; normal packets are pulled back to the original frame, annotated, queued on `wl->deferred_tx_queue`, and completed asynchronously by `netstack_work`.

## State and persistence behavior
Mutates `priv->last_fw_rls_idx`, `wl->links[hlid].fw_rate_idx`, `fw_rate_mbps`, `wl->stats.retry_count`, `wl->tx_results_count`, `wl->tx_frames[]`, the deferred completion queue, and TX id allocation state. No persistent storage.

## Dependencies and integration points
Depends on common wlcore TX descriptor definitions, mac80211 `ieee80211_tx_info`, SKB helpers, workqueues, and wl18xx firmware status private layout. Called through `wl18xx_ops.tx_immediate_compl`.

## Risks and test signals
Risks include invalid firmware release indexes, stale/null `tx_frames` entries, rate-index conversion errors for SGI/HT40/MIMO, TKIP header restoration bugs, and completion ring wraparound. Test heavy TX traffic, failures/no-ACK, dummy packets, TKIP encrypted traffic, HT20/HT40 MCS rates, ring wrap, and firmware recovery after invalid status.
