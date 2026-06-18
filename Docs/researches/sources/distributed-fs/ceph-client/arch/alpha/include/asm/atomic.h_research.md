# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/atomic.h

This header implements Alpha `atomic_t` and `atomic64_t` operations using load-locked/store-conditional loops. It supplies read/set, add/sub, bitwise and/andnot/or/xor, fetch and return variants, add-unless, and `atomic64_dec_if_positive`.

The central macros are `ATOMIC_OP`, `ATOMIC_OP_RETURN`, `ATOMIC_FETCH_OP`, and 64-bit equivalents. They emit `ldl_l/stl_c` or `ldq_l/stq_c`, branch to a cold subsection on store-conditional failure, and retry. Because Alpha has very weak ordering, the relaxed fetch/return primitives end with `smp_mb()`, and acquire/post fences are intentionally empty to avoid redundant back-to-back fences in generic wrappers. `arch_atomic_fetch_add_unless` and 64-bit versions add explicit full barriers before and after the LL/SC loop.

State is the atomic counter field itself. Dependencies include `READ_ONCE`, `WRITE_ONCE`, `asm/barrier.h`, and `asm/cmpxchg.h`. Risks are memory-ordering regressions, incorrect inline-asm constraints, and changing generic atomic expectations without preserving Alpha dependency ordering. Tests should include atomic API build tests, LKMM-style litmus assumptions, SMP stress, and refcount/add-unless users.
