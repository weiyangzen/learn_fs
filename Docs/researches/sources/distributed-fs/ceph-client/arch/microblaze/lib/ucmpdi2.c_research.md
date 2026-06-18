# sources/distributed-fs/ceph-client/arch/microblaze/lib/ucmpdi2.c

Purpose: implements unsigned 64-bit comparison helper `__ucmpdi2`.

Important APIs and state: exported `__ucmpdi2(unsigned long long a, unsigned long long b)` returns 0, 1, or 2 for less, equal, or greater.

Control flow: compares unsigned high words first, then unsigned low words.

State and persistence: pure arithmetic.

Dependencies and integration: used by compiler-generated unsigned 64-bit comparisons and modules.

Risks and test signals: return convention differs from normal compare. Test values around 2^32, top-bit-set highs, equal values, and endian variants.
