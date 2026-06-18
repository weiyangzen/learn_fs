# File Research: sources/cow-pools/openzfs/module/zfs/zrlock.c

Read coverage: complete file, 189 lines.

Purpose: Zero Reference Lock implementation, a lightweight lock/reference primitive for cases where many readers may hold references and a writer may only lock when the reference count is zero.

Semantics:
- Readers call `zrl_add_impl()` and `zrl_remove()`.
- A writer-like caller uses `zrl_tryenter()` only; it never waits for readers to drain.
- `ZRL_LOCKED` is `-1` and semantically means zero references but exclusively locked.
- `ZRL_DESTROYED` is `-2` for debug/sanity after destruction.
- Reader acquisition is reentrant because it increments a count and does not track per-thread ownership for correctness.

Functions:
- `zrl_init()` initializes mutex, condition variable, refcount, and debug owner/caller fields.
- `zrl_destroy()` asserts zero references, destroys synchronization primitives, and marks destroyed.
- `zrl_add_impl()` uses atomic CAS to increment the refcount while not locked; if locked, waits on the condition variable until unlocked.
- `zrl_remove()` decrements the refcount atomically and asserts non-negative count in debug builds.
- `zrl_tryenter()` atomically transitions refcount from zero to `ZRL_LOCKED`; returns failure if references exist.
- `zrl_exit()` releases exclusive locked state, clears debug owner, sets refcount to zero, and broadcasts waiters.
- `zrl_is_zero()` returns true for zero or locked states.
- `zrl_is_locked()` checks exclusive locked state.
- `zrl_owner()` is available in debug builds.

Concurrency notes:
- Fast reader acquisition is lock-free unless the ZRL is exclusively locked.
- Waiting readers use `zr_mtx` and `zr_cv`.
- There is no writer priority and no blocking writer acquisition, avoiding reader/writer priority policy complexity.

Exports:
- Kernel builds export `zrl_add_impl` and `zrl_remove`.
