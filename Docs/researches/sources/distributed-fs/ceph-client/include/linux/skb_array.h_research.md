# sources/distributed-fs/ceph-client/include/linux/skb_array.h

## Purpose

`skb_array.h` defines a type-safe `struct sk_buff` FIFO wrapper around `ptr_ring`. It provides fixed-size queue operations for network packet buffers, including context-specific locking variants, length peeking with VLAN tag accounting, resizing, unconsume, and cleanup.

## Important APIs, Types, And Functions

The core type is `struct skb_array`, containing `struct ptr_ring ring`. APIs include `__skb_array_full()`, `skb_array_full()`, `skb_array_produce()`, `skb_array_produce_irq()`, `skb_array_produce_bh()`, `skb_array_produce_any()`, `__skb_array_empty()`, `__skb_array_peek()`, `skb_array_empty()`, `skb_array_empty_bh()`, `skb_array_empty_irq()`, `skb_array_empty_any()`, `__skb_array_consume()`, `skb_array_consume()`, batched consume variants for normal/IRQ/BH/any contexts, `skb_array_peek_len*()`, `skb_array_init()`, `skb_array_unconsume()`, `skb_array_resize()`, `skb_array_resize_multiple_bh()`, and `skb_array_cleanup()`.

`__skb_array_len_with_tag()` computes packet length and adds `VLAN_HLEN` when an skb carries a hardware-accelerated VLAN tag. `__skb_array_destroy_skb()` frees leftover ring entries with `kfree_skb()`.

## Control Flow

Producers enqueue SKBs into the underlying ptr ring with the variant matching their locking context. Consumers dequeue one or a batch, optionally peek at the first skb length, and may unconsume a batch back into the ring. Resize operations preserve entries or free overflow through the skb destroy callback. Cleanup drains and frees queued SKBs.

## State And Persistence

Persistent state is the embedded ptr ring: queue array, producer/consumer indexes, locks, and stored skb pointers. SKB ownership transfers to the ring on successful produce and back to the consumer on consume; cleanup and resize own freeing of retained SKBs.

## Dependencies And Integration Points

Dependencies are `ptr_ring`, `skbuff`, VLAN definitions, allocation hook wrappers, and kernel-only networking headers. Integration points are networking drivers and virtio/vhost-style packet queues that need fixed-depth SKB FIFOs.

## Risks And Test Signals

Risks include using `__skb_array_empty()` or `__skb_array_full()` in loops without compiler barriers, wrong context variant leading to IRQ/BH locking bugs, SKB leaks on resize/unconsume, length undercounting when VLAN tags are present, and assumptions that `struct skb_array` can diverge from `struct ptr_ring` layout despite the offset build check. Test signals include enqueue/dequeue ordering, full/empty transitions, IRQ/BH producer-consumer tests, batch consume/unconsume, resize under load, cleanup leak checks, VLAN length peeking, and allocation failure paths.
