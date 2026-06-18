# sources/distributed-fs/ceph-client/arch/arm64/lib/memcmp.S

Purpose: optimized ARM64 implementation of `memcmp`, returning ordering for the first differing byte in two bounded buffers.

Important APIs/types/functions: `__pi_memcmp`, weak alias `memcmp`, less-than-8 byte path, 16-byte loop, alignment optimization, endian-aware return normalization, and `EXPORT_SYMBOL_NOKASAN`.

Control flow: handles small lengths with word/byte paths, compares initial 8/16 bytes, optionally aligns `src1` for large ranges, loops over 16-byte pairs using conditional compare, then checks last overlapping bytes. On word difference it reverses data on little-endian so numeric compare reflects byte order and returns -1/0/1 or byte difference for tiny path.

State and persistence: reads caller buffers only. No persistent state.

Dependencies/integration: exported kernel memory routine; assumes ARMv8 unaligned access support.

Risks: overlapping tail loads must remain within the bounded range. Endian-specific comparison controls observable ordering. Misalignment optimization overlaps loads and needs correct length thresholds.

Test signals: randomized buffers and lengths, first difference at every position, equal buffers, lengths 0..128 and large sizes, unaligned pairs, big-endian coverage, and comparison against generic implementation.
