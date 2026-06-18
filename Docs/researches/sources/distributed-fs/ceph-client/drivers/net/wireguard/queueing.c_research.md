# sources/distributed-fs/ceph-client/drivers/net/wireguard/queueing.c

Purpose: Implements WireGuard queue primitives used to run crypto in parallel while preserving per-peer packet order.

Important APIs and functions: `wg_packet_percpu_multicore_worker_alloc()` allocates and initializes a per-CPU `multicore_worker` array. `wg_packet_queue_init()` initializes a bounded `ptr_ring` and per-CPU workers for a crypt queue. `wg_packet_queue_free()` frees workers and cleans the ring. `wg_prev_queue_init()`, `wg_prev_queue_enqueue()`, and `wg_prev_queue_dequeue()` implement a multi-producer/single-consumer ordered queue using `skb->prev` as next pointer and a stub node.

Control flow: Device queues receive skbs/lists for parallel encryption/decryption. Per-peer queues receive the same items first so the serial consumer can wait until worker state changes from uncrypted to crypted/dead, preserving order even if crypto finishes out of order.

State and persistence: Mutates `crypt_queue.ring`, per-CPU worker pointers, `last_cpu`, and `prev_queue` head/tail/peek/count state. Queue contents are volatile skbs.

Dependencies and integration points: Used by device setup/teardown, send encryption worker, receive decryption worker, per-peer TX worker, and NAPI RX polling. Depends on ptr_ring, per-CPU workqueues, skb layout, atomics, and memory barriers.

Risks: The queue relies on `struct sk_buff` `next`/`prev` offsets and release/acquire ordering. `wg_packet_queue_free()` warns if non-purge cleanup sees pending entries. Failed global queue insertion after per-peer insertion returns `-EPIPE` and callers must mark peer queue entries dead.

Test signals: Queue capacity limits, multi-producer ordering, crypto completion out of order, queue free with and without purge, CPU hotplug/online selection behavior, and skb leak tests on `-EPIPE` paths.
