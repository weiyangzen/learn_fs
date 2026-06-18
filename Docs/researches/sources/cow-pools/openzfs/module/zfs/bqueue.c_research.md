# File Research: sources/cow-pools/openzfs/module/zfs/bqueue.c

## Scope

Implements a bounded blocking queue with batched enqueue/dequeue lists and capacity measured in caller-supplied item sizes.

## APIs And Behavior

- `bqueue_init()` initializes shared, enqueuing, and dequeuing lists, condition variables, lock, maximum capacity, node offset, and fill fraction.
- `bqueue_destroy()` asserts all lists/sizes are empty, destroys synchronization primitives, and tears down lists.
- `bqueue_enqueue()` appends to a private enqueuing list and flushes it to the shared list when the batched size reaches the fill threshold.
- `bqueue_enqueue_flush()` forces a flush and wakeup for final records or low-volume producers.
- `bqueue_dequeue()` consumes from a private dequeuing list; if empty, it waits for shared-list data, moves the whole shared list locally, wakes producers, and returns the head entry.

## State And Dependencies

`bqueue_t` contains three lists, size counters, max size/fill fraction, embedded-node offset, one mutex, and producer/consumer condition variables. Stored objects must contain a `bqueue_node_t` at the configured offset.

## Risks And Invariants

The API assumes at most one concurrent enqueuer and at most one concurrent dequeuer per queue, though the enqueuer and dequeuer may run concurrently with each other. Producers can remain below the fill threshold indefinitely unless `bqueue_enqueue_flush()` is used. Capacity waiting uses shared `bq_size`, while batched private list sizes are tracked separately.
