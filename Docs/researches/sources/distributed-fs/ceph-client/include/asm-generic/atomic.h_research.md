# sources/distributed-fs/ceph-client/include/asm-generic/atomic.h

Purpose: Implements generic 32-bit atomic integer operations for architectures that can build them from `cmpxchg` on SMP or interrupt disabling on UP.

Important APIs, types, and functions: Generates `generic_atomic_add/sub/and/or/xor`, return variants, and fetch variants, then maps them to `arch_atomic_*`. Defines `arch_atomic_read()` and `arch_atomic_set()` through `READ_ONCE`/`WRITE_ONCE`.

Control flow: On SMP, each operation loops on `arch_cmpxchg()` until the expected old value is replaced. On non-SMP, it disables local interrupts, updates `v->counter`, and restores interrupts.

State and persistence: Operates on caller-owned `atomic_t` counters. No global state.

Dependencies and integration points: Depends on `asm/cmpxchg.h`, `asm/barrier.h`, `linux/irqflags.h` for UP, and atomic wrapper layers in `linux/atomic.h`.

Risks and test signals: Risks include weak `cmpxchg` semantics on architectures, missing barriers for higher-level atomic APIs, IRQ latency on UP, and signed overflow expectations. Test atomic litmus tests, KCSAN/lockless users, SMP contention, UP interrupt nesting, and compare with architecture overrides.
