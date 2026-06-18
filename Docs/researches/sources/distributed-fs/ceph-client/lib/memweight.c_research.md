# sources/distributed-fs/ceph-client/lib/memweight.c

Purpose: Counts set bits across an arbitrary byte range.

Important APIs/types/functions: Exports `memweight(const void *ptr, size_t bytes)`.

Control flow: Counts unaligned leading bytes with `hweight8`, processes aligned full words through `bitmap_weight`, then counts trailing bytes individually to preserve big-endian correctness for partial words.

State and persistence: Stateless.

Dependencies/integration: Uses bit/bitmap helpers and `BUG_ON` to guard excessive bitmap length.

Risks: Very large input can trip the `BUG_ON(longs >= INT_MAX / BITS_PER_LONG)` guard; caller must supply valid memory.

Test signals: No local tests; important cases are unaligned buffers, trailing bytes, endian behavior, and large-size guard.
