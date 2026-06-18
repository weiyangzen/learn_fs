# sources/distributed-fs/ceph-client/include/linux/ww_mutex.h

## Purpose
Defines the public wound/wait mutex API used by kernel subsystems that must acquire multiple same-class locks in arbitrary order without deadlocking. The header provides lock-class descriptors, acquisition contexts, initialization helpers, slowpath helpers, and declarations for the core lock, trylock, interruptible lock, and unlock routines.

## Important APIs, Types, and Functions
`struct ww_class` owns the monotonically increasing acquisition stamp and lockdep class keys for a family of related ww mutexes. `struct ww_mutex` embeds either a normal `mutex` or an `rt_mutex` under `CONFIG_PREEMPT_RT`, plus the active owner acquisition context. `struct ww_acquire_ctx` records the acquiring task, stamp, count of acquired locks, wound state, algorithm choice, lockdep maps, and optional debug injection counters. `DEFINE_WD_CLASS()` selects wait/die ordering; `DEFINE_WW_CLASS()` selects wound/wait ordering. Public calls are `ww_mutex_init()`, `ww_acquire_init()`, `ww_acquire_done()`, `ww_acquire_fini()`, `ww_mutex_lock()`, `ww_mutex_lock_interruptible()`, `ww_mutex_lock_slow()`, `ww_mutex_lock_slow_interruptible()`, `ww_mutex_trylock()`, `ww_mutex_unlock()`, `ww_mutex_destroy()`, and `ww_mutex_is_locked()`.

## Control Flow
Typical use starts by defining a class, initializing each `ww_mutex`, creating a stack `ww_acquire_ctx`, and attempting locks with the same context. `ww_mutex_lock()` returns `0` on success, `-EALREADY` for the same lock/context, or `-EDEADLK` when the caller must back off. On `-EDEADLK`, the caller releases all locks already acquired for the context, waits on the contended lock via the slowpath helper, then retries the remaining lock set. `ww_acquire_done()` optionally marks the transition from acquisition to protected-data use, and `ww_acquire_fini()` releases lockdep bookkeeping after all ww mutexes are unlocked.

## State and Persistence
The header owns no persistent storage outside embedded objects, but the class stamp persists across acquire contexts and establishes ordering. Each lock stores its current acquisition context while held. Each acquire context is task-owned and must remain valid until all locks acquired under it have been released and `ww_acquire_fini()` has run. Lockdep and debug fields persist only under matching debug configs.

## Dependencies and Integration Points
Depends on `linux/mutex.h`, `linux/rtmutex.h`, lockdep annotations, `current`, atomics, and debug mutex config. Integrates with DRM/GPU reservation locking, buffer-object management, memory-management code, and other subsystems that lock sets discovered at runtime.

## Risks
The main risk is caller protocol abuse: mixing single-lock acquisition with context-based acquisition in the same class, using different contexts for the same class, freeing a context too early, failing to back off on `-EDEADLK`, or calling slowpath helpers while still holding other ww mutexes. PREEMPT_RT changes the underlying primitive, so code must rely on ww APIs rather than mutex internals. Debug-only checks catch many ordering mistakes, but production builds still depend on disciplined call patterns.

## Test Signals
Signals include lockdep/PROVE_LOCKING warnings, `CONFIG_DEBUG_WW_MUTEX_SLOWPATH` deadlock injection, DRM reservation stress tests, PREEMPT_RT lock tests, interruptible wait signal tests, and KCSAN/KASAN findings around context lifetime and unlock ordering.
