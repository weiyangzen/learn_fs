# sources/distributed-fs/ceph-client/include/linux/mutex_types.h

Purpose: defines the storage layout and semantic contract for `struct mutex`, separated from the higher-level API declarations in `mutex.h`.

Important APIs and types: non-RT `context_lock_struct(mutex)` contains `atomic_long_t owner`, `raw_spinlock_t wait_lock`, optional optimistic spin queue `osq`, guarded `first_waiter`, optional debug `magic`, and optional `lockdep_map`. PREEMPT_RT uses `struct rt_mutex_base rtmutex` plus optional lockdep metadata. The comments document strict mutex rules: one owner, owner-only unlock, no recursive locking, no copying or memset initialization, no held-lock exit/free/reinit, and no interrupt-context use.

Control flow: higher-level mutex APIs allocate, initialize, and mutate this state. Waiters serialize through `wait_lock`, optimistic spinning uses `osq` when configured, and RT builds delegate wait/ownership behavior to rtmutex internals.

State and persistence: all fields are volatile in-memory lock state. Debug and lockdep fields persist only for the lifetime of the mutex object and help detect misuse; there is no durable state.

Dependencies and integration points: depends on atomic, lockdep, osq, spinlock, type definitions, and `rtmutex.h` on PREEMPT_RT. It is included by lock users needing the concrete type but not necessarily the full API.

Risks and test signals: risks include ABI/layout assumptions outside the locking core, failing to respect RT versus non-RT layout, racing direct field access, and missing debug enforcement in non-debug builds. Test with lockdep/debug mutex configs, optimistic spinning configs, PREEMPT_RT, structure initialization paths, and misuse tests for recursive lock/unlock/free cases.
