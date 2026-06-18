# sources/distributed-fs/ceph-client/kernel/locking/ww_rt_mutex.c

## Purpose
Provides the RT mutex backed implementation of the public `ww_mutex` operations. It compiles `rtmutex.c` with `WW_RT` policy hooks and exports trylock, blocking lock, interruptible lock, and unlock entry points.

## Important APIs, Types, And Functions
Exports `ww_mutex_trylock`, `ww_mutex_lock`, `ww_mutex_lock_interruptible`, and `ww_mutex_unlock`. The central helper is `__ww_rt_mutex_lock`, which wraps lockdep nesting, fastpath `rt_mutex_try_acquire`, and slowpath `rt_mutex_slowlock`.

## Control Flow
Trylock delegates to plain `rt_mutex_trylock` when no ww context is supplied. With a context, it resets `wounded` when the context holds no locks, attempts `__rt_mutex_trylock`, publishes the ww context with `ww_mutex_set_context_fastpath`, then records lockdep nesting. Blocking lock rejects recursive acquisition with `-EALREADY`, performs lockdep acquisition, uses the RT fastpath if possible, and otherwise enters the RT slowpath with the ww context and task state.

## State And Persistence
State is held in the embedded `struct rt_mutex`, the ww context pointer on `struct ww_mutex`, and lockdep maps. Unlock clears ww context accounting before releasing lockdep state and calling `__rt_mutex_unlock`.

## Dependencies And Integration Points
Depends on `rtmutex.c`, `ww_mutex.h`, lockdep, scheduler sleep rules, and exported module symbols. It is the PREEMPT_RT-compatible backend for users of the generic `linux/ww_mutex.h` API.

## Risks And Edge Cases
The main risks are preserving ww semantics while RT priority inheritance reorders waiters, resetting `wounded` only when no locks are held, and keeping lockdep nesting paired on all failure paths. Recursive same-context locking must return `-EALREADY` without corrupting lockdep state.

## Test Signals
Coverage should include RT builds, `test-ww_mutex`, lockdep-enabled kernels, interruptible wait interruption, trylock behavior with and without contexts, and deadlock recovery paths returning `-EDEADLK` from the RT slowpath.
