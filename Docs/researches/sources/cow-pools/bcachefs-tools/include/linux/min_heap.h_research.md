# File Research: sources/cow-pools/bcachefs-tools/include/linux/min_heap.h

This header implements typed min-heap helpers. `MIN_HEAP_PREALLOCATED()` defines heap structs with `nr`, `size`, `data`, and optional preallocated storage; `DEFINE_MIN_HEAP()` provides the common no-preallocation shape.

`struct min_heap_callbacks` supplies comparison and optional swap callbacks. The header contains inline heap operations for init, peek, full check, sift down/up, heapify, pop, pop-push, push, and delete. It also declares non-inline equivalents and type-preserving macros for callers.

Swap selection optimizes aligned element copies using 64-bit or 32-bit word swaps, falling back to byte swaps or a caller-provided swap function. Heap indexing is done in byte offsets, with a branchless parent calculation.
