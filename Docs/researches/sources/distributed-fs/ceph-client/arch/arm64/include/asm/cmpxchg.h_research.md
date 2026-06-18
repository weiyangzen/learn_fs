## sources/distributed-fs/ceph-client/arch/arm64/include/asm/cmpxchg.h

Purpose: implements arm64 exchange, compare-exchange, 128-bit compare-exchange, and compare-wait primitives.

Important APIs/types/functions: exports `arch_xchg_relaxed/acquire/release/full`, `arch_cmpxchg*`, `arch_cmpxchg64*`, `arch_cmpxchg128`, `arch_cmpxchg128_local`, `system_has_cmpxchg128`, and `__cmpwait_relaxed`. Internal macro generators emit size-specific LL/SC and LSE paths.

Control flow: xchg uses alternative-patched LL/SC loops or LSE `swp` instructions. cmpxchg dispatches through `__lse_ll_sc_body`. cmpwait performs `sevl`, `wfe`, exclusive load, compares, and optionally waits again.

State and persistence: mutates caller memory atomically; no independent state.

Dependencies and integration: depends on barriers, LSE dispatch, build-bug checks, and generic atomic/locking users. Used by locks, atomics, refcounts, futexes, and wait loops.

Risks: size dispatch, acquire/release mapping, and LL/SC retry behavior are critical. Incorrect 128-bit support can corrupt paired-word atomics. Test signals are atomic selftests, qspinlock/refcount stress, LKMM litmus tests, and LSE/non-LSE hardware coverage.
