# sources/distributed-fs/ceph-client/include/linux/bit_spinlock.h

## Purpose
Implements compact spin locks backed by individual bits in an unsigned long, for cases where a full `spinlock_t` is too costly or unavailable.

## Important APIs, types, and functions
- `__bitlock(bitnum, addr)` creates a sparse/static-analysis lock token per bit/address pair.
- `bit_spin_lock()` disables preemption and acquires the bit lock.
- `bit_spin_trylock()` tries to acquire and returns success.
- `bit_spin_unlock()` releases with atomic clear semantics.
- `__bit_spin_unlock()` releases with non-atomic clear semantics for cases where the bit lock protects the rest of the word.
- `bit_spin_is_locked()` reports lock state with SMP/debug/preempt-count fallbacks.

## Control flow and state
Lock acquisition disables preemption, uses `test_and_set_bit_lock()` on SMP/debug builds, and busy-waits with a non-atomic `test_bit()` plus `cpu_relax()` to reduce bus traffic before retrying. Unlock clears the bit and re-enables preemption.

## State and persistence behavior
The lock state is one bit in caller-owned memory. No persistent state exists beyond that word. Preemption state is part of the lock contract and must be restored by unlock.

## Dependencies and integration points
Depends on preemption, atomic bit operations, bug checks, processor relax, sparse lock annotations, and debug spinlock config. Used by memory-management and low-level structures needing embedded bit locks.

## Risks
This is slower than normal spinlocks and should be used only when necessary. Non-atomic unlock is only safe when the lock bit protects the word being modified. Missing unlock leaves preemption disabled. Lock ordering is less visible than named spinlocks.

## Test signals
Use lockdep/sparse annotations, SMP contention tests, trylock failure paths, debug spinlock BUG checks, preempt-count balance checks, and non-atomic unlock users that modify protected flag words.
