# File Research: sources/cow-pools/bcachefs-tools/fs/util/fifo.h

Purpose: Header-only generic circular FIFO macros for typed queues with selectable index widths.

Key APIs and behavior:
- Defines `FIFO(type)`, `FIFO_U16_IDX`, `FIFO_U32_IDX`, `FIFO_U64_IDX`, and declaration helpers.
- `init_fifo()` allocates a power-of-two backing buffer with `kvmalloc`; `free_fifo()` releases it.
- Tracks absolute `front` and `back` counters and indexes storage with `idx & mask`.
- Supports push/pop at both ends, peek, pointer/index conversion, move, swap, grow, and forward/reverse iteration.

Integration:
- Depends on `util.h` for allocation, `roundup_pow_of_two`, `swap`, and `typecheck`.
- Used by higher-level utility code such as SIX-lock wait machinery.

Risks and invariants:
- `fifo_grow()` assumes old data can be duplicated into both halves to preserve absolute-index masking.
- Counters wrap according to the chosen index type, so small index variants require bounded occupancy/lifetime use.
