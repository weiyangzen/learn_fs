# sources/distributed-fs/ceph-client/arch/arc/lib/strcmp-archs.S

Purpose: ARCv2 optimized `strcmp()`.

Important APIs/functions: exports `strcmp`.

Control flow: if either pointer is not halfword/word aligned, falls back to a byte loop. The aligned path loads words, detects NUL in the first string with a repeated-byte mask, compares whole words, and on mismatch or NUL isolates the relevant byte to return -1, 0, or 1 style ordering. Big-endian paths swizzle words before comparison.

State and persistence: no persistent state.

Dependencies and integration: selected for ARCv2. Depends on ARCv2 `ffs`, `swape`, branch hints, and endian conditionals.

Risks: return value need only indicate ordering, but must match C semantics. NUL detection and word mismatch interaction are subtle, especially on big endian and when one string terminates inside the compared word.

Test signals: equal strings, prefix cases, first difference at each byte position, unaligned pointers, strings containing high-bit bytes, and endian variants.
