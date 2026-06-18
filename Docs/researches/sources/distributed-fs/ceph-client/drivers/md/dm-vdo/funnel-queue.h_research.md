# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/funnel-queue.h

## Purpose
`funnel-queue.h` declares the VDO multi-producer, single-consumer queue and inlines the producer enqueue operation for low overhead.

## Important APIs, Types, And Functions
- `struct funnel_queue_entry` is the embedded link field required in every queued object.
- `struct funnel_queue` contains producer-owned `newest`, consumer-owned cache-line-separated `oldest`, and the `stub` sentinel.
- `vdo_funnel_queue_put()` initializes `entry->next`, atomically exchanges it into `queue->newest`, and links it from the previous newest entry.
- Non-inline APIs are `vdo_make_funnel_queue()`, `vdo_free_funnel_queue()`, `vdo_funnel_queue_poll()`, `vdo_is_funnel_queue_empty()`, and `vdo_is_funnel_queue_idle()`.

## Control Flow And Data Flow
Producers call `vdo_funnel_queue_put()` with the address of an embedded `funnel_queue_entry`. The full barrier behavior of `xchg()` orders all caller data initialization before publication. Consumers call `vdo_funnel_queue_poll()` and recover the containing object with `container_of()` or equivalent, assuming every queued type uses the same link offset for a given queue.

## State And Persistence Behavior
The queue has no persistence. Its concurrency state is encoded in two pointers and the stub node. Cache-line alignment separates producer and consumer hot fields to reduce false sharing.

## Dependencies And Integration Points
The header uses Linux atomic/cache primitives and is included by VDO workqueue and UDS request queue implementations. It intentionally exposes internals only to make `vdo_funnel_queue_put()` inline.

## Risks
- The API cannot enforce single-consumer use.
- All entries in a queue must have the embedded link at the same offset if callers use a shared cast pattern.
- Producers must not modify or free entries after enqueue until ownership returns through the consumer.
- The enqueue operation can temporarily leave the linked-list view incomplete; consumers must tolerate NULL polls.

## Test Signals
Tests should verify memory-order visibility of payload fields, correct behavior with queue stub reinsertion, and no ABA sensitivity when entries are freed after poll and later reallocated.
