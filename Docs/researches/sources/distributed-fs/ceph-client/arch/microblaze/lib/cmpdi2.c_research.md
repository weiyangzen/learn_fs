# sources/distributed-fs/ceph-client/arch/microblaze/lib/cmpdi2.c

Purpose: implements signed 64-bit comparison helper `__cmpdi2`.

Important APIs and state: exported `__cmpdi2(long long a, long long b)` returns libgcc-style 0 for less, 1 for equal, and 2 for greater.

Control flow: compares signed high words first, then unsigned low words if highs match.

State and persistence: pure arithmetic.

Dependencies and integration: compiler and modules use it for 64-bit signed comparisons when no native sequence is emitted.

Risks and test signals: return values are not normal C comparison signs. Test negative/positive crossings, equal values, and low-word ordering with equal high words.
