<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/tx.c

Purpose: Provides carl9170 transmit preparation, queueing, firmware-memory accounting, USB submission scheduling, TX completion processing, A-MPDU aggregation, power-save filtering, BAR tracking, and beacon upload.

Important APIs/types/functions: Exports `carl9170_op_tx()`, `carl9170_tx_scheduler()`, `carl9170_tx_process_status()`, `carl9170_tx_status()`, `carl9170_tx_callback()`, `carl9170_tx_drop()`, `carl9170_tx_janitor()`, `carl9170_update_beacon()`, and skb kref helpers. Core internals include `carl9170_tx_prepare()`, `carl9170_tx_apply_rateset()`, `carl9170_tx_ampdu_queue()`, `carl9170_tx_ampdu()`, `carl9170_tx()`, `carl9170_alloc_dev_space()`, and `carl9170_release_dev_space()`.

Control flow: mac80211 calls `carl9170_op_tx()`, which prepends the firmware superframe, fills encryption, queue, VIF, rate, ERP, and A-MPDU metadata, accounts queue depth, and either enqueues an aggregate TID or direct pending frame. `carl9170_tx()` allocates a firmware memory cookie, moves the skb to the status queue, adds an extra skb reference for USB/status race handling, and submits via `carl9170_usb_tx()`. Firmware TXCOMP traps remove skbs by cookie and queue, fill rate retry counts, and report status to mac80211. USB callbacks drop the pending reference and reschedule if more work exists.

State and persistence: Maintains `tx_stats`, queue stop timestamps, `tx_total_queued`, `tx_total_pending`, firmware memory bitmap/free-block counters, per-TID BA windows and sequence bitmaps, BAR lists, current A-MPDU density/factor, pending beacon skb cache per vif, and delayed janitor state. State is volatile and reset on device restart.

Dependencies and integration points: Depends on mac80211 rate control/status APIs, USB TX callbacks, firmware status cookies, `wlan.h` descriptor layout, `hw.h` register writes for beacon upload, RCU-protected station/vif state, and power-save station blocking.

Risks and test signals: Risks include cookie double-free races, queue wake/stop imbalance, stuck TX requiring restart, strict sequence assumptions in A-MPDU queues, BAR status heuristics, and beacon memory overflow. Test signals are TX under queue pressure, aggregation setup/teardown, firmware TXCOMP correlation, filtered frames for sleeping stations, queue timeout recovery, and beacon generation in AP/IBSS/mesh modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/tx.c -->
