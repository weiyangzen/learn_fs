# File Research: sources/block-storage/kvdo/vdo/funnel-queue.c

## Purpose
Implements the non-inline portions of a multi-producer, single-consumer funnel queue.

## Main Behavior
- `make_funnel_queue()` allocates a cache-line-aligned queue and initializes a permanent stub entry so newest/oldest are never NULL.
- `funnel_queue_poll()` returns and removes the oldest real entry for the single consumer.
- `is_funnel_queue_empty()` reports whether an entry can currently be retrieved.
- `is_funnel_queue_idle()` distinguishes true idleness from producer transition states.

## Algorithm Notes
The queue uses an atomic exchange on the producer end and a stub node to maintain invariants. It is “almost” lock-free: a producer preempted after swapping `newest` but before writing `previous->next` can temporarily hide later entries from the consumer.

## Invariants
Only one consumer may poll. Callers own entry allocation and must embed `struct funnel_queue_entry` at a consistent offset.
