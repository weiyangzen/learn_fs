# sources/distributed-fs/ceph/src/mds/SimpleLock.cc

Purpose: Implements the non-inline behavior for MDS `SimpleLock`, including lazy unstable state allocation, xlock ownership, wait/cap shift mappings, cache tracking, dumping, and printing.

Important APIs/functions: `more`, `try_clear_more`, `get_xlock`, `set_xlock_done`, `put_xlock`, `get_xlock_by`, `dump`, `get_wait_shift`, `get_cap_shift`, `get_cap_mask`, `add_cache`, `remove_cache`, `get_active_caches`, and `_print`.

Control flow: The lock allocates `unstable_bits_t` only when gather sets, wrlocks, xlocks, exclusive clients, or lock caches are needed. `get_xlock()` asserts valid states, pins the parent with `PIN_LOCK`, records the mutation/client owner, and increments xlock count. `set_xlock_done()` clears mutation ownership and moves non-local locks to `LOCK_XLOCKDONE`. `put_xlock()` decrements count, unpins the parent, clears owner fields at zero, and frees unstable bits if empty.

State and persistence behavior: The state machine state is stored on `SimpleLock`; unstable fields are in-memory. `dump()` omits fully sync/unlocked locks, reducing diagnostic noise. The encode/decode behavior is declared in the header and persists state plus gather set for replay/rejoin rather than lock holder refs.

Dependencies and integration points: Relies on `MDSCacheObject` pin/waiter APIs, `MutationImpl`, `locks.h` state constants, `MDLockCache`, and Ceph cap bit constants. Wait shifts map lock types into reserved high bits of `MDSCacheObject::waitmask_t`.

Risks: Incorrect state assertions in xlock paths indicate protocol violations. Wait-shift or cap-mask mistakes can wake wrong waiters or grant incorrect caps. Lazy unstable cleanup must not drop active cache items or lock holders. `get_active_caches()` filters invalidating caches, so invalidation state changes need care.

Test signals: Cover xlock lifecycle for local and non-local locks, `LOCK_XLOCKDONE` transition, cache add/remove, waiter shift uniqueness for every lock type, cap mask/shift mappings, and dencoder round trips for sync and non-sync states.
