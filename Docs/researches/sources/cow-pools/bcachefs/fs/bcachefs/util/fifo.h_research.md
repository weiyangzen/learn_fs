# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/fifo.h

This header defines generic macro-based ring buffers/FIFOs with selectable index type.

Core types:
- `FIFO(type)`
- `FIFO_U16_IDX(type)`
- `FIFO_U32_IDX(type)`
- `FIFO_U64_IDX(type)`

Lifecycle:
- `init_fifo()` initializes indices, size, mask, and allocates power-of-two backing storage.
- `free_fifo()` frees backing storage.
- `fifo_swap()` swaps two FIFO objects.

Capacity/state:
- `fifo_used()`
- `fifo_free()`
- `fifo_empty()`
- `fifo_full()`

Element operations:
- `fifo_push_back_ref()`
- `fifo_push_front_ref()`
- `fifo_push_back()`
- `fifo_push_front()`
- `fifo_pop_front()`
- `fifo_pop_back()`
- aliases: `fifo_push`, `fifo_pop`, `fifo_peek`

Growth:
- `fifo_grow()` doubles backing storage.
- Growth preserves absolute front/back indices by copying old data into both halves of the new buffer.

Index helpers:
- Convert pointer to absolute or relative FIFO index.
- Access by relative FIFO index.

Iteration:
- forward entry iteration
- pointer iteration
- reverse pointer iteration

Important invariants:
- Backing size is rounded to a power of two and accessed by mask.
- Front/back are monotonic modulo the index type.
- Callers must handle allocation failure from `init_fifo()` and `fifo_grow()`.

Research notes:
- This is a generic low-level utility suitable for queues/deques where callers manage locking externally.
