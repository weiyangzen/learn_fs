## sources/distributed-fs/ceph-client/arch/arm64/include/asm/atomic_ll_sc.h

### Purpose
Implements ARM64 LL/SC fallback atomic, cmpxchg, and 128-bit cmpxchg primitives using exclusive load/store loops.

### Important APIs, Types, And Functions
Macro generators define `__ll_sc_atomic_*`, `__ll_sc_atomic_fetch_*`, `__ll_sc_atomic64_*`, and `__ll_sc_atomic64_fetch_*` for arithmetic/bitwise operations and memory-order variants. It also defines `__ll_sc_atomic64_dec_if_positive`, `__ll_sc__cmpxchg_case_*` for 8/16/32/64-bit relaxed/acquire/release/full cases, `union __u128_halves`, and `__ll_sc__cmpxchg128`/`__ll_sc__cmpxchg128_mb`.

### Control Flow
Each operation prefetches for store, loops on `ldxr`/`stxr` or acquire/release variants until the exclusive store succeeds, and emits `dmb ish` or memory clobbers for full ordering. Cmpxchg compares loaded old values before attempting store; 128-bit compare exchange uses `ldxp/stxp` over two 64-bit halves.

### State, Persistence, And Dependencies
State is caller memory protected by exclusive monitors. Dependencies include compiler constraint support, stringify, AArch64 exclusive instruction semantics, and barrier conventions.

### Integration Points
Included through the ARM64 LSE dispatch machinery when LSE atomics are unavailable or patched out.

### Risks
Constraint letters, sub-word casts, clobbers, and memory barriers are correctness-critical. LL/SC loops can livelock under heavy contention. 128-bit cmpxchg must preserve pair alignment and compare high/low halves correctly.

### Test Signals
Run atomic and cmpxchg LKMM tests on LL/SC-only hardware or with LSE disabled, stress contended atomics, test sub-word cmpxchg, run 128-bit cmpxchg users, and build with compilers with/without `K` constraint support.
