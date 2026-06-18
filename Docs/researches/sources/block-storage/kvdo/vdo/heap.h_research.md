# File Research: sources/block-storage/kvdo/vdo/heap.h

Generic heap interface for fixed-size array elements.

Key responsibilities:
- Defines `heap_comparator` and `heap_swapper` callbacks used to compare and exchange arbitrary element types.
- Defines `struct heap`, a 1-based heap view over caller-provided storage with capacity, element size, current count, comparator, and swapper.
- Declares setup and operations: `initialize_heap()`, `build_heap()`, `pop_max_heap_element()`, `sort_heap()`, and `sort_next_heap_element()`.
- Provides `is_heap_empty()` inline.

Important behavior:
- The header documents a max-heap invariant, though the comment says every child "must be at least as large as its children", which appears to intend "every parent".
- The heap does not own storage; callers provide the backing array and element callbacks.
- Sorting and pop behavior depend entirely on the comparator/swapper being O(1) and correct for the array element type.

Dependencies:
- Uses `type-defs.h` for `byte`, `bool`, and related base types.

Notable risks:
- The 1-based array convention is explicit; callers must allocate/pass storage compatible with that convention.
- No ownership, locking, or bounds semantics are visible in the header beyond capacity/count fields.
