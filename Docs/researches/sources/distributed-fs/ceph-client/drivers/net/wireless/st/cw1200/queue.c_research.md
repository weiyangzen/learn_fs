# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/queue.c

Purpose: Implements bounded O(1)-style TX queues with packet IDs, per-link accounting, pending/queued separation, queue locking, and TTL garbage collection.

Important APIs and functions: Provides queue stats init/deinit, queue init/deinit/clear, `cw1200_queue_put`, `cw1200_queue_get`, `cw1200_queue_requeue`, `cw1200_queue_remove`, `cw1200_queue_get_skb`, lock/unlock wrappers, timestamp lookup, and stats empty checks. Private `cw1200_queue_item` stores skb, packet ID, timestamps, txpriv, and generation.

Control flow: `put` takes a free item, assigns a packet ID from queue generation, queue ID, item generation, and pool index, updates per-link stats, and may stop the mac80211 queue if near capacity. `get` selects the first queued item matching a link map, moves it to pending, stamps transmit time, and exposes WSM TX data. `remove` completes a pending item and calls the skb destructor. `requeue` moves a pending item back to queued with incremented item generation. GC expires stale queued frames based on TTL and wakes waiters when link maps empty.

State and persistence: Queue state is memory-resident: item pool, free/queued/pending lists, generation counters, counts, link-map caches, timer, and spinlocks. Stats aggregate queued counts across queues.

Dependencies and integration: Used by TX/RX WSM code, BH timeout detection, AP power-save link maps, flush logic, and mac80211 queue stop/wake APIs. Calls debug and PM stay-awake helpers.

Risks: Packet ID parsing indexes `queue->pool[item_id]` before checking `item_id >= capacity`, so invalid IDs could form out-of-bounds pointers before validation. Correct stats depend on every get/remove/requeue path being balanced. Unsafely clearing queues while TX confirms arrive can expose stale generation handling.

Test signals: Queue capacity/overfull behavior, TTL expiration, link-id-specific draining, requeue after firmware retry, stale packet ID rejection, flush waiters, and mac80211 stop/wake transitions under parallel TX.
