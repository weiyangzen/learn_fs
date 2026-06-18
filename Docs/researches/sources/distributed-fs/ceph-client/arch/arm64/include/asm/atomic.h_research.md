## sources/distributed-fs/ceph-client/arch/arm64/include/asm/atomic.h

### Purpose
Defines ARM64 architecture atomic integer and atomic64 operations by dispatching to LSE or LL/SC implementations.

### Important APIs, Types, And Functions
Macro generators create `arch_atomic_*` and `arch_atomic64_*` operations for add, sub, and, andnot, or, xor, fetch variants, return variants with relaxed/acquire/release/full ordering, and `arch_atomic64_dec_if_positive`. Also defines `arch_atomic_read`, `arch_atomic_set`, `ATOMIC64_INIT`, and aliases indicating generic atomic API support.

### Control Flow
Inline functions call `__lse_ll_sc_body()` for each operation, letting `asm/lse.h` select Large System Extensions atomics when available or LL/SC fallbacks otherwise. Reads/writes use `__READ_ONCE` and `__WRITE_ONCE`.

### State, Persistence, And Dependencies
State is caller-owned `atomic_t` or `atomic64_t` counters. No persistence beyond memory. Dependencies include compiler/types, memory barriers, cmpxchg, and LSE selection headers.

### Integration Points
Used by generic kernel atomic API on ARM64 across scheduler, locking, MM, networking, and filesystem code, indirectly supporting Ceph client correctness.

### Risks
Memory-order aliases must match generic expectations. LSE/LLSC dispatch must preserve semantics across heterogeneous CPUs. Atomic64 aliases to atomic read/set assume compatible counter layout.

### Test Signals
Run LKMM atomic litmus tests, locktorture/refcount tests, KCSAN stress, LSE-capable and LL/SC-only boot tests, and compile checks for all generated operation names.
