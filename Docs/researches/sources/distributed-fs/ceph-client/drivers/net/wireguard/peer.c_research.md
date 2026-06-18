# sources/distributed-fs/ceph-client/drivers/net/wireguard/peer.c

Purpose: Implements WireGuard peer allocation, initialization, lookup reference helpers, removal, full teardown, and peer slab cache lifecycle.

Important APIs and functions: `wg_peer_create()` allocates a peer, initializes endpoint cache, Noise handshake, cookie state, timers, keypair lock, work items, per-peer TX/RX ordered queues, endpoint lock, staged packet queue, NAPI, allowedips list, pubkey hash entry, and peer counters. `wg_peer_get_maybe_zero()` safely references peers under RCU. `wg_peer_remove()` and `wg_peer_remove_all()` remove peers from configuration lookup structures and complete asynchronous teardown. `wg_peer_put()` releases krefs. `wg_peer_init()`/`wg_peer_uninit()` manage the peer kmem cache.

Control flow: Creation requires `device_update_lock`, checks `MAX_PEERS_PER_DEVICE`, initializes all peer subsystems, adds the peer to the device list and pubkey hashtable, and enables NAPI. Removal first calls `peer_make_dead()` to remove config-time reachability and set `is_dead`, then `synchronize_net()`, then `peer_remove_after_dead()` to clear keypairs, stop timers, flush crypto work twice, disable/delete NAPI, flush handshake send work, decrement peer count, and drop the owning reference. Final kref release removes handshake index, purges staged packets, and schedules RCU memory zero/free.

State and persistence: Mutates `wg->peer_list`, `wg->num_peers`, peer allowedips list, pubkey hash, index hash entries, NAPI state, keypairs, timers, staged packets, endpoint cache, and peer kref/RCU lifetime. No durable state exists.

Dependencies and integration points: Depends on device state, queueing, timers, peerlookup, Noise, cookie, allowedips, dst cache, NAPI, workqueues, RCU, and krefs. Netlink creates/removes peers; datapath holds peer references during TX/RX and handshake processing.

Risks: Removal ordering is delicate because packets can move from global crypto queues to per-peer serial/NAPI queues while references are in flight. The double workqueue flush and `synchronize_net()` are part of the lifetime proof. Any new peer context must honor `is_dead` or removal can race into freed state. Final zeroing wipes sensitive material but requires all references gone.

Test signals: Create up to limit, remove single/all peers under traffic, remove during handshake and data receive, NAPI disable/delete correctness, queued packet cleanup, staged packet drop accounting, RCU stall/leak detection, and peer cache init failure.
