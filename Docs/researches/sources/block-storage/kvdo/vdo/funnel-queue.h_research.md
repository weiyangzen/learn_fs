# File Research: sources/block-storage/kvdo/vdo/funnel-queue.h

## Purpose
Defines the funnel queue structures and inline producer enqueue operation.

## Main Contents
- `struct funnel_queue_entry`: intrusive next pointer embedded in queued objects.
- `struct funnel_queue`: cache-line-separated producer `newest`, consumer `oldest`, and stub entry.
- `funnel_queue_put()`: inline multi-producer enqueue using `xchg()` and `previous->next` publication.
- Poll/status allocation API declarations.

## Memory Ordering
`xchg()` provides a full barrier; producer stores must be visible before linking an entry. Consumer polling uses a read barrier before returning the dequeued entry.
