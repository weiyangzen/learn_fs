# sources/distributed-fs/ceph-client/include/linux/wait_bit.h

## Purpose
`wait_bit.h` builds specialized wait primitives on top of waitqueues for sleeping on individual bits or arbitrary variable addresses. It is used for page flags, locks encoded as bits, reference counters, and address-keyed state changes.

## Important APIs, Types, and Functions
Core types are `struct wait_bit_key`, `struct wait_bit_queue_entry`, and `wait_bit_action_f`. APIs include `__wake_up_bit()`, `__wait_on_bit()`, `__wait_on_bit_lock()`, `wake_up_bit()`, out-of-line wait helpers, `bit_waitqueue()`, `wait_bit_init()`, `wake_bit_function()`, `DEFINE_WAIT_BIT`, and actions `bit_wait`, `bit_wait_io`, and `bit_wait_timeout`. Inline bit waits include `wait_on_bit()`, `wait_on_bit_io()`, `wait_on_bit_timeout()`, `wait_on_bit_action()`, `wait_on_bit_lock()`, `wait_on_bit_lock_io()`, and `wait_on_bit_lock_action()`. Variable-address waits include `init_wait_var_entry()`, `wake_up_var()`, `__var_waitqueue()`, `wait_var_event*()` variants, locked var waits, `wake_up_var_protected()`, `wake_up_var_locked()`, `clear_and_wake_up_bit()`, `test_and_clear_wake_up_bit()`, `atomic_dec_and_wake_up()`, and `store_release_wake_up()`.

## Control Flow
Bit waiters first test the bit with acquire or atomic test-and-set semantics. If the fast path fails, they enqueue on a hashed waitqueue keyed by `(word, bit)` and sleep with a selected action. Wakers clear or update state with release/ordered semantics and call `wake_up_bit()` or `wake_up_var()`. Variable waits hash an arbitrary address into a shared waitqueue and wake only entries with matching keys.

## State and Persistence
State is transient waitqueue entries and shared hashed waitqueue heads. The actual condition state remains in caller-owned bits or variables. Memory ordering is explicit: clear-and-wake uses release semantics plus a barrier; waits use acquire tests; `store_release_wake_up()` publishes data before waking.

## Dependencies and Integration Points
The header depends on `wait.h`, bitops, atomics, scheduler states, IO scheduling, lockdep, spinlocks, and mutexes. It integrates with page wait bits, buffer locks, inode and folio state, refcount zero waits, and any subsystem using address-keyed wakeups.

## Risks
Callers must wake exactly the bit or variable address being waited on. Missing release/acquire ordering can expose stale data after wait completion. `wait_on_bit_lock()` sets the bit before returning and must be paired with correct unlock/wake. Hashed waitqueues mean key matching is mandatory to avoid false wakeups. Locked variable waits require the wake under the same lock.

## Test Signals
Signals include page-bit wait tests, lock-bit contention, timeout and signal return paths, IO wait accounting, variable-address wakeups under lock, atomic decrement-to-zero wakeups, memory-order litmus tests, and stress runs with lockdep/KCSAN.
