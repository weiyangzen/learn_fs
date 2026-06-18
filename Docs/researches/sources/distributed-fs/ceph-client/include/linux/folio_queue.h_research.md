# sources/distributed-fs/ceph-client/include/linux/folio_queue.h

## Purpose
This header defines a segmented queue of folios for running buffers and `ITER_FOLIOQ` users. It extends `folio_batch` with linked queue segments, per-slot order metadata, and two mark bitmaps.

## APIs, types, and control flow
`struct folio_queue` contains a `folio_batch`, `orders[]`, explicit `next`/`prev` links, two `unsigned long` mark fields, request/debug ids, and a compile-time check that one word can cover all slots. `folioq_init()` resets links, marks, ids, and batch state. Capacity/count/full helpers operate on the embedded batch. Mark helpers test/set/clear first and second bitmaps. `folioq_append()` and `folioq_append_mark()` append a folio, store its `folio_order()`, and optionally set the first mark. Accessors retrieve the folio, order, and size. `folioq_clear()` nulls a slot and clears marks without decreasing occupancy.

## State and dependencies
State is per segment, often chained by producer/consumer code that can add at tail and remove at head without list-head locking. It depends on folio APIs, `PAGE_SIZE`, bit operations, and `folio_batch`.

## Integration, risks, and tests
Netfs, buffered IO, and iterator code can use these queues. Risks are no bounds checks on slot access/append, occupancy not decreasing after clear, stale orders for cleared slots, and lockless link assumptions. Tests should cover segment init, append/full behavior, mark independence, clear semantics, multi-segment traversal, and invalid slot handling under debug instrumentation.
