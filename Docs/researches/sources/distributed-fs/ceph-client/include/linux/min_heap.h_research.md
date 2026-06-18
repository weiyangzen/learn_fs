# sources/distributed-fs/ceph-client/include/linux/min_heap.h

## Purpose
Generic typed min-heap API for kernel priority queues, with typed declarations, inline/out-of-line operations, comparator callbacks, optional custom swaps, and optimized default swaps.

## Important APIs/Types
`MIN_HEAP_PREALLOCATED`, `DEFINE_MIN_HEAP`, and `min_heap_char` define heap layout. `struct min_heap_callbacks` supplies `less` and optional `swp`. Macro APIs cover init, peek, full, sift down/up, heapify, pop, pop-push, push, and delete, with inline and external implementations. Internal helpers choose 64-bit, 32-bit, or byte swaps and compute parents using byte offsets.

## Control Flow
Push appends then sifts up. Pop replaces root with the last element then sifts down. Pop-push overwrites root then sifts down. Delete swaps target with last, decrements, then sifts up and down. Heapify uses bottom-up Floyd heapification.

## State And Persistence
Caller-owned heap state is `nr`, `size`, `data`, optional preallocated storage, and callback-private args. No internal locking is provided.

## Dependencies And Integration Points
Depends on bug warnings, string copying, types, alignment, and pointer arithmetic. Integrates with subsystems needing small generic priority queues.

## Risks
Empty pop, full push, invalid comparator ordering, unsafe custom swaps, alignment assumptions, zero-size heaps, and concurrent mutation without external locking.

## Test Signals
Randomized heap property tests, push/pop/delete/pop-push ordering, full/empty warnings, custom swap coverage, preallocated/external storage, odd element sizes, and 32/64-bit behavior.
