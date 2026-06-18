# sources/distributed-fs/ceph-client/lib/lockref.c

Purpose: combined spinlock/reference-count helper operations with optional lockless cmpxchg fast paths.

Important APIs/types/functions: `lockref_get()`, `lockref_get_not_zero()`, `lockref_put_return()`, `lockref_put_or_lock()`, `lockref_mark_dead()`, `lockref_get_not_dead()`, and `CMPXCHG_LOOP`.

Control flow: when `USE_CMPXCHG_LOCKREF` is enabled, operations optimistically read the combined lock/count word, verify the embedded spinlock appears unlocked, adjust count, and try `try_cmpxchg64_relaxed()`, retrying up to 100 times. Fallback paths acquire `lockref->lock` and update `count`. `put_or_lock()` returns false with the lock held when count is too low for a simple decrement.

State/persistence: mutates `struct lockref` count and sometimes leaves the spinlock held for caller-side object destruction. `mark_dead()` sets a negative count under the lock.

Dependencies/integration: exported for VFS/object lifecycle users that need atomic refcounting with lock handoff. Depends on architecture spinlock layout and 64-bit cmpxchg support for fast path.

Risks: cmpxchg path assumes `sizeof(struct lockref)` packed word is 8 bytes and that lock value can be checked directly. Callers must obey semantics around dead/zero counts and lock ownership from `put_or_lock()`.

Test signals: no direct subset tests; concurrency stress, refcount lifecycle tests, and lockdep around fallback lock paths are expected signals.
