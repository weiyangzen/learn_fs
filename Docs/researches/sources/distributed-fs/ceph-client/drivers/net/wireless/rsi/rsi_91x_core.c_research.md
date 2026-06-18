# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_core.c

Purpose: RSI common TX queuing, WMM scheduling, station/vif lookup, and mac80211 transmit entry path.

Important APIs/functions: `rsi_core_xmit()` accepts mac80211 skbs, classifies management/control/data, prepares descriptors, starts BA sessions, applies queue watermarks, and wakes the TX thread. `rsi_core_qos_processor()` dequeues selected queues and sends packets to HAL/coex. Helpers implement weighted queue selection, TXOP-based burst counts, enqueue/dequeue, `rsi_find_sta()`, and `rsi_get_vif()`.

Control flow: beacon and management queues preempt data. Data queues use WMM weights/backoff: contending queues get `wme_params`, the minimum weight queue is selected, weights are reduced, and VO/VI may dequeue multiple packets based on TXOP duration. The processor checks hardware queue availability under `tx_lock`, wakes stopped mac80211 queues below low watermark, sends through coex or direct management/data routines, updates stats, and yields after about 300 ms of continuous work.

State and persistence: `common->tx_queue[]`, `tx_qinfo[]`, `min_weight`, `selected_qnum`, `pkt_cnt`, queue block flags, TX stats, station table, vif array, FSM state, WOW flags, and aggregation-start flags drive behavior.

Dependencies/integration: mac80211 TX metadata, RSI HAL descriptor routines, bus queue status callback, coexistence, station/vif private data, BA session API, and watermarks.

Risks: invalid vif/station lookup drops packets. Queue watermark handling must avoid deadlocking stopped mac80211 queues. `info->driver_data` shares storage with `control`, so the code copies key state before overwriting. WOW and FSM gating block TX.

Test signals: traffic across all ACs, management/EAPOL paths, AP unicast station lookup, BA session start, hardware queue full behavior, queue stop/wake watermarks, coex-enabled data path, and WOW TX blocking.
