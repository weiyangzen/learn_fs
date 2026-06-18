# sources/distributed-fs/ceph-client/include/asm-generic/bitops/ffs.h

Purpose: Implements generic `ffs()` with libc-compatible one-based indexing for the first set bit in an `int`.

Important APIs, types, and functions: Defines `generic_ffs(int x)` and maps `ffs(x)` unless the architecture provides `__HAVE_ARCH_FFS`.

Control flow: Returns 0 for zero. Otherwise shifts through 16/8/4/2/1-bit chunks and increments a one-based result until the low set bit is located.

State and persistence: No state.

Dependencies and integration points: Used by generic bitops and integer helpers where compiler builtins or arch implementations are absent.

Risks and test signals: Risks are one-based semantics confusion and signed-int expectations. Test zero, powers of two, negative/high-bit inputs, and equivalence with compiler builtin `ffs`.
