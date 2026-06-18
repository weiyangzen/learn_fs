# sources/distributed-fs/ceph-client/kernel/locking/spinlock_debug.c

## Purpose
Implements DEBUG_SPINLOCK validation for raw spinlocks and, on non-PREEMPT_RT, raw rwlocks. It initializes debug metadata, checks magic/owner/CPU recursion, records owners, and emits emergency diagnostics on misuse.

## Important APIs, Types, and Functions
- Exports `__raw_spin_lock_init()` and, non-RT, `__rwlock_init()`.
- Spin debug helpers: `spin_dump()`, `spin_bug()`, `debug_spin_lock_before()`, `debug_spin_lock_after()`, and `debug_spin_unlock()`.
- Raw spin operations: `do_raw_spin_lock()`, `do_raw_spin_trylock()`, and `do_raw_spin_unlock()`.
- Non-RT rwlock operations: `do_raw_read_lock()`, `do_raw_read_trylock()`, `do_raw_read_unlock()`, `do_raw_write_lock()`, `do_raw_write_trylock()`, and `do_raw_write_unlock()`.

## Control Flow
Initialization sets lockdep maps when enabled, raw architecture lock state, magic value, owner sentinel, and owner CPU. Lock operations validate magic and recursion before acquiring the architecture lock, then record current task and CPU. Unlock validates lock state, owner task, and owner CPU, clears owner metadata, and releases the architecture lock. Trylock records ownership only on success and asserts UP trylock failures as impossible.

## State and Persistence
Debug fields live inside raw spinlock/rwlock structures: magic, owner, and owner CPU. No persistence beyond live kernel objects.

## Dependencies and Integration Points
Depends on architecture spin/rwlock primitives, debug locks, lockdep, NMI/delay support, PID/task info for diagnostics, MMIO write-barrier hooks for spinlocks, and exported debug lock initialization APIs.

## Risks
Diagnostics call `debug_locks_off()` to avoid repeated reports; after the first serious failure, later issues may be suppressed. Owner checks are meaningful only for exclusive spin/write locks, not read locks. PREEMPT_RT excludes raw rwlock debug implementation here.

## Test Signals
Enable DEBUG_SPINLOCK and intentionally exercise bad magic, recursion, wrong owner, wrong CPU, double unlock, and UP trylock behavior. Expected signals are emergency printk reports, stack dumps, and lockdep map initialization checks.
