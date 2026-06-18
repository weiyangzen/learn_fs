# sources/distributed-fs/ceph-client/arch/arm64/lib/memchr.S

Purpose: optimized ARM64 implementation of `memchr`, returning the first matching byte in a bounded memory range.

Important APIs/types/functions: `__pi_memchr`, weak alias `memchr`, byte replication constants, word-loop zero-byte-style match detection, endian fixup, and `EXPORT_SYMBOL_NOKASAN`.

Control flow: masks the search character to one byte, scans 8-byte words with a replicated character and parallel byte-match detection, then scans any trailing bytes. On a matching word, it reverses the syndrome on little-endian, counts leading zeros, and computes the matching address.

State and persistence: read-only scan of caller memory. No persistent state.

Dependencies/integration: used by kernel string/memory library callers and exported without KASAN instrumentation.

Risks: word loads require the full word to be inside the caller's valid range; the routine only loads complete 8-byte chunks derived from `n`. Endian syndrome math must locate the first matching byte, not just any match.

Test signals: all byte values, lengths 0..16, unaligned buffers, match at first/last/no byte, big-endian builds, and comparison with generic C `memchr`.
