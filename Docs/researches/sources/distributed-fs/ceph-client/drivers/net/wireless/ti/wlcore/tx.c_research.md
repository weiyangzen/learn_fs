# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/tx.c

## Purpose
`tx.c` implements the common wlcore transmit pipeline shared by TI WiLink wl12xx/wl18xx-family drivers. It bridges mac80211 skb submission to firmware transfer buffers, assigns firmware TX descriptor IDs, fills the packed `wl1271_tx_hw_descr` ABI, schedules packets across vifs/links/access categories, handles TX completion status from firmware, and provides reset/flush/queue-stop helpers used by suspend, recovery, interface teardown, and chipset-specific interrupt paths.

## Important APIs, Types, And Functions
- `wlcore_tx_work_locked()` drains driver TX queues into `wl->aggr_buf`, writes the aggregate to `REG_SLV_MEM_DATA`, optionally triggers older hardware end-of-transaction signaling, wakes watermark-stopped queues, and rearms RX streaming for active data links.
- `wl1271_tx_work()` is the workqueue wrapper that takes `wl->mutex`, resumes runtime PM, invokes the locked worker, and queues recovery on bus failure.
- `wlcore_tx_complete()` reads the firmware TX-result ring from `target_mem_map->tx_result`, acknowledges `tx_result_fw_counter`, and hands each result to `wl1271_tx_complete_packet()`.
- `wl1271_tx_complete_packet()` validates the descriptor ID, restores skb layout, updates mac80211 TX status, queues the skb on `deferred_tx_queue`, schedules `netstack_work`, and frees the descriptor ID.
- `wl1271_tx_flush()`, `wl12xx_tx_reset()`, `wl12xx_tx_reset_wlvif()`, and `wl1271_tx_reset_link_queues()` are cleanup paths that stop queues, force TX work, report failed skbs, and restore counters after timeout or recovery.
- `wlcore_stop_queue*()`, `wlcore_wake_queue*()`, and `wlcore_is_queue_stopped*()` maintain per-mac80211-queue stop reason bitmaps for watermark, firmware restart, flush, and spare-block throttling.
- Internal helpers include `wl1271_alloc_tx_id()`, `wl1271_free_tx_id()`, `wl12xx_tx_get_hlid()`, `wl1271_tx_allocate()`, `wl1271_tx_fill_hdr()`, `wl1271_prepare_tx_frame()`, `wl1271_skb_dequeue()`, and `wl1271_skb_queue_head()`.

## Control Flow
mac80211 enqueue happens in `main.c`: skb queue mapping is translated by `wl1271_tx_get_queue()`, `wl12xx_tx_get_hlid()` chooses a host link ID, the skb is appended to `wl->links[hlid].tx_queue[q]`, queue counters are incremented, high watermark may stop the mac80211 queue, and `tx_work` is queued unless firmware TX is busy. `wl1271_skb_dequeue()` chooses an AC with pending packets and the fewest firmware-allocated packets, then does round-robin selection across vifs and links while asking chip ops whether a link is high or low priority.

For each skb, `wl1271_prepare_tx_frame()` validates the HLID, determines TKIP/GEM extra space and WEP default-key updates, calls `wl1271_tx_allocate()` to reserve a descriptor ID and firmware memory blocks, and calls `wl1271_tx_fill_hdr()` to populate session, lifetime, rate policy, encryption, EAPOL, checksum, and data-length fields. The prepared skb bytes are copied into the aggregate buffer with alignment selected by `wlcore_calc_packet_alignment()`.

If the aggregate buffer fills, the skb is pushed back to the head, the partial aggregate is written to firmware, and the loop continues. If firmware blocks are exhausted, the skb is pushed back, `WL1271_FLAG_FW_TX_BUSY` is set, and the worker exits until completions/free-block accounting lets TX proceed. Bus write failures are the only errors propagated to the workqueue wrapper for recovery.

Completion flow is ring-counter based: firmware advances `tx_result_fw_counter`; the host acknowledges by writing the same counter back; each ring entry supplies descriptor ID, status, retry count, rate class, and timing data. Successful completions map firmware rate class to mac80211 rate index and set ACK status unless no-ACK was requested. Retry-exceeded completions update retry statistics. Dummy packets free their ID but are not reported to mac80211.

## State And Persistence Behavior
This file does not persist state outside kernel memory. Runtime state is kept in `struct wl1271`: `tx_frames_map`, `tx_frames[]`, `tx_frames_cnt`, `tx_queue_count[]`, `queue_stop_reasons[]`, `tx_blocks_available`, `tx_allocated_blocks`, `tx_allocated_pkts[]`, `tx_packets_count`, `tx_results_count`, `last_wlvif`, `dummy_packet`, `deferred_tx_queue`, and per-link `allocated_pkts`. Per-vif state in `struct wl12xx_vif` includes per-AC counters, `last_tx_hlid`, pending authentication ROC timing, default WEP key, rate policy indexes, and link maps.

Locking is split by responsibility: `wl->mutex` protects high-level device state and runtime PM transitions; `wl->wl_lock` protects queue counters and stop-reason bitmaps; `flush_mutex` serializes `wl1271_tx_flush()`. The code assumes callers hold `wl->mutex` for locked TX/reset paths and uses `assert_spin_locked()` in queue-state queries that require `wl_lock`.

## Dependencies And Integration Points
The file depends on mac80211/cfg80211 skb metadata, Linux skb queues, runtime PM, workqueues, timers, and bitmaps. It calls wlcore hardware abstraction helpers from `hw_ops.h` for block accounting, descriptor data length, checksum setup, pre-send padding, link priority, and spare blocks. It uses wlcore bus helpers (`wlcore_write_data`, `wlcore_write32`, `wlcore_read`), command helpers (`wl12xx_cmd_set_default_wep_key`, `wl1271_acx_set_inconnection_sta`), power-save helpers (`wl12xx_ps_link_start`), recovery helpers (`wl12xx_queue_recovery_work`), and main.c watchdog/RX-streaming work.

Chip integration differs by family. wl12xx uses `wlcore_tx_complete()` through its delayed completion hook, while wl18xx has a separate completion path but still uses common queueing/allocation helpers and common state fields. Firmware ABI integration is through `struct wl1271_tx_hw_descr` and `struct wl1271_tx_hw_res_if` from `tx.h`.

## Risks And Edge Cases
- Descriptor ID accounting is safety-critical. Lost completions or double frees can leave `WL1271_FLAG_FW_TX_BUSY` stuck or leak skbs in `tx_frames[]`.
- Queue counters are updated in enqueue, dequeue, push-back, reset, and dummy-packet paths. Any mismatch can break watermark throttling or trigger warnings.
- `wl1271_tx_complete()` warns on result-ring overflow but still processes `count` entries using a 16-entry masked offset, so large counter jumps risk duplicate/stale result processing after firmware or bus anomalies.
- skb layout mutation for TX descriptors and TKIP extra header space must be exactly reversed before mac80211 status; mistakes corrupt frame headers on completion or reset.
- `wl1271_prepare_tx_frame()` suppresses most non-bus errors from the workqueue caller by design; command failures may rely on lower-level recovery scheduling.
- Flush stops all queues and waits up to `WL1271_TX_FLUSH_TIMEOUT`; timeout falls back to link queue reset, but in-flight firmware frames are handled separately by full TX reset/recovery.
- AP pending-auth handling starts a remain-on-channel style timer when auth responses are transmitted; incorrect detection could keep ROC too short or too long.

## Test Signals
Useful signals include mac80211 TX status correctness, no queue-counter warnings under traffic, high/low watermark stop/wake transitions, descriptor count returning to zero after traffic and flush, recovery behavior when bus writes fail, TX watchdog recovery when firmware completions stop, AP-mode sleeping-station traffic, EAPOL/WEP/TKIP/GEM frames, dummy packet reuse, and suspend/remove paths that call `wl1271_tx_flush()`.
