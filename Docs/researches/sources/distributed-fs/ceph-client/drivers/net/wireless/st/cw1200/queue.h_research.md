# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/queue.h

Purpose: Public queue structures and function prototypes for CW1200 TX queue management.

Important APIs and types: Defines `cw1200_queue_skb_dtor_t`, `struct cw1200_queue`, `struct cw1200_queue_stats`, and `struct cw1200_txpriv`. Declares queue lifecycle, put/get/requeue/remove, skb lookup, lock/unlock, timestamp, and stats-empty functions. Inline helpers extract queue ID and generation from packet IDs.

Control flow: TX code constructs `cw1200_txpriv`, enqueues skbs, WSM selects frames, and confirmations use packet IDs to remove or requeue items.

State and persistence: Structures hold in-memory queue lists, pools, link maps, counters, timers, and locks for the lifetime of the device.

Dependencies and integration: Shared by main initialization, TX/RX, BH, STA/AP power-save, and debugfs status output.

Risks: Consumers must respect the packet-ID encoding and queue locking rules. `cw1200_txpriv` fields such as link ID, TID, and offset are used by multiple paths, so incorrect population can break AP power-save or direct probe work.

Test signals: Compile all queue users after API changes; runtime TX, requeue, flush, AP station sleep/wake, and direct probe paths validate semantics.
