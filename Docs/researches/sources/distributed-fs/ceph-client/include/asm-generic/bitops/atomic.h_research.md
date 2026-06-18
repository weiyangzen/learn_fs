# sources/distributed-fs/ceph-client/include/asm-generic/bitops/atomic.h

Purpose: Implements generic atomic bit set/clear/change/test operations on bitmaps using atomic-long fetch operations.

Important APIs, types, and functions: Defines `arch_set_bit()`, `arch_clear_bit()`, `arch_change_bit()`, `arch_test_and_set_bit()`, `arch_test_and_clear_bit()`, and `arch_test_and_change_bit()`, then includes instrumented atomic bitops.

Control flow: Computes the target word with `BIT_WORD(nr)`, mask with `BIT_MASK(nr)`, performs raw atomic OR/ANDNOT/XOR or fetch variants, and returns the previous bit state for test-and operations.

State and persistence: Mutates caller-owned volatile bitmap words atomically.

Dependencies and integration points: Depends on atomic-long operations, compiler annotations, barriers, and instrumented wrappers. Used by bit locks, flags, filesystems, and concurrent bitmap code.

Risks and test signals: Risks are missing ordering expectations, volatile/atomic cast assumptions, and incorrect bit numbering. Test atomic bitops under concurrency, KCSAN instrumentation, lock bit users, and little-endian bitmap call sites.
