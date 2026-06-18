# sources/distributed-fs/ceph-client/arch/m68k/lib/memcpy.c

## Purpose

`memcpy.c` provides the m68k implementation of `memcpy()` for non-overlapping memory copies.

## Important APIs, Types, and Functions

It defines and exports `void *memcpy(void *to, const void *from, size_t n)`. The implementation uses m68k inline assembly and alignment-aware loops to copy bytes, words, or longwords efficiently.

## Control Flow

The function saves the original destination pointer for return, handles small or unaligned leading bytes as needed, copies larger aligned chunks using wider operations, then copies trailing bytes. It assumes the source and destination do not overlap, as required by `memcpy()`.

## State and Persistence Behavior

The only persistent effect is writing `n` bytes into the destination buffer. No global state is used.

## Dependencies and Integration Points

It satisfies generic kernel `memcpy()` calls and module references through `EXPORT_SYMBOL`. It is selected by `arch/m68k/lib/Makefile`.

## Risks and Edge Cases

Overlapping ranges are undefined and must use `memmove()`. Assembly constraints and alignment handling must be correct for all CPU variants selected by this library. Very small copies and odd addresses are common edge cases.

## Test Signals

Run memory selftests comparing byte-for-byte results for sizes 0 through large buffers, all source/destination alignments, and ensure overlapping tests are routed to `memmove()` rather than relying on `memcpy()`.
