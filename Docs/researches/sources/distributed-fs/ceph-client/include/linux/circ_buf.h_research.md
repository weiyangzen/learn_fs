# sources/distributed-fs/ceph-client/include/linux/circ_buf.h

## Purpose

`circ_buf.h` provides the kernel's simple power-of-two circular buffer struct and arithmetic macros.

## Important APIs, Types, and Functions

`struct circ_buf` contains `buf`, `head`, and `tail`. Macros are `CIRC_CNT()`, `CIRC_SPACE()`, `CIRC_CNT_TO_END()`, and `CIRC_SPACE_TO_END()`.

## Control Flow

Producers and consumers update head/tail externally, while macros compute used bytes, free bytes, and contiguous ranges before wraparound. One slot is intentionally left unused to distinguish full from empty.

## State and Persistence Behavior

State is only the caller-owned buffer pointer and head/tail indexes. There is no synchronization or persistence built in.

## Dependencies and Integration Points

It has no external dependencies. It is used by drivers and subsystems needing lightweight ring-buffer arithmetic.

## Risks and Edge Cases

`size` must be a power of two. Macros do not enforce memory barriers or locking; concurrent users must provide ordering. Full capacity is `size - 1`, not `size`. Head/tail expressions in `_TO_END` variants are carefully evaluated once; callers should preserve that property if wrapping.

## Test Signals

Test empty/full/one-less-than-full states, wraparound count/space, nonconcurrent producer/consumer behavior, and lockless users with required memory barriers.
