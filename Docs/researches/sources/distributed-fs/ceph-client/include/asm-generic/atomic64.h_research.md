# sources/distributed-fs/ceph-client/include/asm-generic/atomic64.h

Purpose: Declares a generic spinlock-backed 64-bit atomic implementation for architectures without native 64-bit atomic instructions.

Important APIs, types, and functions: Defines aligned `atomic64_t`, `ATOMIC64_INIT`, declares `generic_atomic64_read/set`, add/sub/and/or/xor operations with return/fetch variants, `generic_atomic64_dec_if_positive()`, `generic_atomic64_cmpxchg()`, `generic_atomic64_xchg()`, and `generic_atomic64_fetch_add_unless()`, then maps them to `arch_atomic64_*`.

Control flow: Implementations are external, typically serializing operations through hashed spinlocks. The header only binds generic symbols to the arch atomic64 interface.

State and persistence: Operates on caller-owned 64-bit atomic counters; any lock table is implemented elsewhere.

Dependencies and integration points: Depends on Linux types and the generic atomic64 implementation object. Used by 32-bit or simple architectures to satisfy `atomic64_*` APIs.

Risks and test signals: Risks are alignment assumptions, lock contention, release/acquire semantics of mapped operations, and missing implementation linkage. Test atomic64 selftests, 32-bit SMP stress, cmpxchg/xchg correctness, add-unless races, and module link coverage.
