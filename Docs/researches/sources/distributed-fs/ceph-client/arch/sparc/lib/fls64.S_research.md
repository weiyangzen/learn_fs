# sources/distributed-fs/ceph-client/arch/sparc/lib/fls64.S

Purpose: SPARC64 find-last-set helper for 64-bit values.

Important APIs/functions: Exports `__fls`.

Control flow: Determines the highest set bit through staged tests/shifts across the 64-bit input and returns a zero-based index for nonzero values.

State and persistence: Pure register computation.

Dependencies/integration: Includes `linux/export.h` and `linux/linkage.h`.

Risks/test signals: High-half/low-half boundary and return indexing are critical. Test bit 0, bit 31, bit 32, bit 63, all-ones, and random values.
