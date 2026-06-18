# sources/distributed-fs/ceph-client/arch/m68k/lib/memmove.c

## Purpose

`memmove.c` provides the m68k implementation of `memmove()`, supporting overlapping memory ranges safely.

## Important APIs, Types, and Functions

It defines and exports `void *memmove(void *dest, const void *src, size_t n)`. The implementation chooses forward or backward copying based on relative source/destination addresses.

## Control Flow

If the destination is before the source or outside the overlapping forward hazard, the routine copies forward much like `memcpy()`. If the destination lies inside the source range at a higher address, it starts from the end and copies backward to prevent overwriting bytes that have not yet been read. Alignment and chunk loops optimize larger transfers.

## State and Persistence Behavior

The only persistent effect is updating the destination memory range. No global state is used.

## Dependencies and Integration Points

It satisfies generic kernel and module `memmove()` references through `EXPORT_SYMBOL`. Signal frame code and many core subsystems rely on correct overlap behavior.

## Risks and Edge Cases

The overlap decision must be exact for adjacent, identical, and partially overlapping ranges. Backward-copy alignment handling is more error-prone than forward copy. Zero-length copies must return immediately without touching memory.

## Test Signals

Test all small sizes, all alignments, exact same source/destination, destination before source, destination after source, adjacent ranges, and large aligned ranges against a reference memmove.
