<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/atomic64.c -->
# sources/distributed-fs/ceph-client/lib/atomic64.c

## Purpose
Provides a generic 64-bit atomic operation implementation using hashed spinlocks for architectures without native 64-bit atomic instructions.

## APIs, Types, and Functions
Exports `generic_atomic64_read()`, `generic_atomic64_set()`, generated add/sub/and/or/xor operations, return variants, fetch variants, `generic_atomic64_dec_if_positive()`, `generic_atomic64_cmpxchg()`, `generic_atomic64_xchg()`, and `generic_atomic64_fetch_add_unless()`. Internal state is an array of 16 cacheline-aligned `arch_spinlock_t` locks.

## Control Flow, State, and Persistence
`lock_addr()` hashes an `atomic64_t *` address to a lock. Every operation disables local interrupts, locks the hashed spinlock, reads/modifies `v->counter`, unlocks, and restores interrupts. Return/fetch variants differ only in whether they return the updated or previous value. `dec_if_positive()` writes only if decrement stays non-negative; `cmpxchg()` and `fetch_add_unless()` conditionally modify based on old value. Persistent state is the static lock array; atomic values are caller-owned.

## Dependencies and Integration
Depends on architecture spinlocks, local IRQ save/restore, cacheline sizing, `atomic64_t`, and export support. Built under `CONFIG_GENERIC_ATOMIC64` and expected to satisfy generic atomic64 API calls.

## Risks and Test Signals
Risks include lock hash contention, deadlock if used where local IRQ disabling is insufficient, memory-ordering expectations for atomic API variants, and mismatches between generic wrappers and architecture-specific atomic semantics. Test signals include `atomic64_test.c`, LKMM-style atomic tests, SMP stress with multiple atomic64 variables sharing locks, interrupt-context use, and compare/exchange/add-unless edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/atomic64.c -->
